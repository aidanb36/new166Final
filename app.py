"""
* aidan brown
* cs 166/eddy
* final project, cimbing flask app
"""

#imports
from flask import Flask, render_template, request, url_for, flash, redirect
from base64 import b64encode
from random import choice
import hashlib
import sqlite3
import os

#globals
MAX_PASSWORD_LENGTH = 22
MIN_PASSWORD_LENGTH = 7
SALT_LENGTH = 40
DEBUG = True

app = Flask(__name__, static_folder='instance/static')
app.config.from_object('configuration')

#home page
@app.route("/", methods=['GET', 'POST'])
def home():
    """ Home page """
    return render_template('home.html',
                           title="Home Page",
                           heading="Home Page"
                           )

#login page
@app.route("/login/<int:attempts>", methods=['GET', 'POST'])
def login(attempts):
    """ Log the user in """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            stored_data = query_db()
            attempts += 1
            print(attempts)

            if attempts >= 3:
                flash("Too many login attempts!", 'alert-danger')
                return render_template('login.html',
                                       title="Secure Login",
                                       heading="Secure Login",
                                       attempts=attempts)
            elif not sign(stored_data, username, password):
                flash("Invalid name or password", 'alert-danger')
                print(attempts)
                return redirect(url_for('login', attempts=attempts))

            elif sign(stored_data, username, password):
                print("Logged in!")
                for user in stored_data:
                    if user[0] == username:
                        access_level = user[2]
                return redirect(url_for('success', access_level=access_level))

        except KeyError:
            pass
        flash("Invalid username or password!", 'alert-danger')
    return render_template('login.html',
                           title="Secure Login",
                           heading="Secure Login")

#successful login
@app.route("/success/<int:access_level>", methods=['GET', 'POST'])
def success(access_level):
    flash("Welcome! You have logged in!", 'alert-success')
    if access_level == 1:
        return render_template('customer1.html',
                               title="Home",
                               heading="Home")
    elif access_level == 2:
        return render_template('customer2.html',
                               title="Home",
                               heading="Home")
    elif access_level == 3:
        return render_template('customer3.html',
                               title="Home",
                               heading="Home")
    else:
        return render_template('customer1.html',
                               title="Home",
                               heading="Home")

#create new user
@app.route("/new-user", methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            success = add_user(username, password)

            if not success:
                flash("A user with that username is already registered! Try again!", 'alert-danger')
            else:
                flash("Success!", 'alert-success')
                return redirect(url_for('success', access_level=1))

        except KeyError:
            pass

    return render_template('user.html',
                           heading="Register User")


#valid password?
def val(password):
    valid = False
    upper = False
    lower = False
    num = False
    spec = False

    for i in password:
        if not valid:
            if i.isupper():
                upper = True
            elif i.islower():
                lower = True
            elif i.isdigit():
                num = True
            else:
                spec = True

            if upper and lower and spec and num and len(password) >= MIN_PASSWORD_LENGTH and len(password) <= MAX_PASSWORD_LENGTH:
                valid = True

    return valid

#add new user
def add_user(name="", password="", access_level=1):
    usernames = []
    users = query_db()
    for user in users:
        usernames.append(user[0])

    while name == "" or name in usernames:
        name = input("Choose username: ")
        if name in usernames:
            print("Username taken")

    usernames.append(name)

    if password == "":
        choose_default = ""
        while choose_default != "0" and choose_default != "1":
            choose_default = input("Enter 1 to choose your own password or 0 to use the default generator")

            if choose_default == "0":
                password = passw()

    valid = val(password)
    while not valid:
        if password == "":
            password = input("Create password with upper-case letter, lower-case letter, special "
                             "character, and a number. Minimum password length = 7, max length = 22: ")

        valid = val(password)

        if not valid:
            if len(password) < MIN_PASSWORD_LENGTH:
                print("too short\n")
            elif len(password) > MAX_PASSWORD_LENGTH:
                print("too long\n")

            password = ""

    if DEBUG:
        print("\n\nAdding", name + "...")
    hashed_password = hash_pw(password)

    new_user = [(name, hashed_password, access_level)]
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.executemany("INSERT INTO users VALUES (?, ?, ?)", new_user)
        conn.commit()
    except sqlite3.IntegrityError:
        print("Error. Tried to add duplicate record!")
        return False
    else:
        print("Success")
        return True
    finally:
        if c is not None:
            c.close()
        if conn is not None:
            conn.close()

#sign in existing user
def sign(users, username = "", password = ""):
    verified = False
    for user in users:
        # figure out if user exists (salt)
        if username == user[0]:
            salt = user[1][:56]
            hashable = salt + password  # concatenate salt and plain_text
            hashable = hashable.encode('utf-8')  # convert to bytes
            hashed_password = hashlib.sha1(hashable).hexdigest()  # hash w/ SHA-1 and hexdigest
            hashed_password = salt + hashed_password
            if hashed_password == user[1]:
                verified = True
                print("Good")

    return verified

#initialize database table (user)
def create_db():
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE users
                    (
                    name text,
                    password text,
                    access_level text
                    )''')
        conn.commit()
        return True
    except BaseException:
        print("FAILED create_db")
        return False
    finally:
        if c is not None:
            c.close()
        if conn is not None:
            conn.close()

#query from users table
def query_db():
    users = []
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        for row in c.execute("SELECT * FROM users"):
            users.append(row)
    except sqlite3.DatabaseError:
        print("Error. Could not retrieve data.")
    finally:
        if c is not None:
            c.close()
        if conn is not None:
            conn.close()
        return users

#password creation (if necesarry)
def passw(length=MAX_PASSWORD_LENGTH):
    secure = ""
    while len(secure) < length:
        character = choice("agjaejaeaeqlwpigyaervznxmASFJQWOFIEHQBEL1234567890<>?=+-!@#$%^&*")
        secure += character
    return secure

#hash pw, from labs
def hash_pw(plain_text, salt='') -> str:
    if salt == '':
        salt_bytes = os.urandom(SALT_LENGTH)
        salt = b64encode(salt_bytes).decode('utf-8')

    hashable = salt + plain_text  # concatenate salt and plain_text
    if DEBUG:
        print("salt: ", salt)
        print("hashable: ", hashable)
    hashable = hashable.encode('utf-8')  # convert to bytes
    this_hash = hashlib.sha1(hashable).hexdigest()  # hash w/ SHA-1 and hexdigest
    return salt + this_hash  # prepend hash and return
if __name__ == '__main__':
    app.run(debug=app.debug, host='localhost', port=5200)
