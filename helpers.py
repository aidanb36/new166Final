# This file just has the functions I'll need for the project. They were getting in my way

import hashlib
from random import choice
import sqlite3
import os
from base64 import b64encode

MAX_PASSWORD_LENGTH = 22
MIN_PASSWORD_LENGTH = 7
SALT_LENGTH = 40
DEBUG = True


def passw(length=MAX_PASSWORD_LENGTH):
    """ "strong password generator" feature """
    secure = ""
    while len(secure) < length:
        character = choice("agjaejaeaeqlwpigyaervznxmASFJQWOFIEHQBEL1234567890<>?=+-!@#$%^&*")
        secure += character
    return secure


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


def add_user(name="", password="", access_level=1):
    """ Function to add a user to the CSV file """
    # Make a list of usernames to compare against
    usernames = []
    users = []
    users = query_db()
    for user in users:
        usernames.append(user[0])

    while name == "" or name in usernames:
        name = input("Choose a username: ")
        if name in usernames:
            print("Sorry! That name is taken. Choose a different one!")

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
                print("Password is too short! Please choose a longer password\n")
            elif len(password) > MAX_PASSWORD_LENGTH:
                print("Password is too long! Go easy on yourself!\n")

            password = ""

    if DEBUG:
        print("\n\nAdding", name + "...")
        print("----------------------------------------------------")
    hashed_password = hash_pw(password)

    # New user is all set to be added to the file
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

def sign_in(users, username = "", password = ""):
    verified = False
    for user in users:
        # Determine if this user is in the users file
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

def show_menu():
    """ Simply show the menu """
    print("1: Accounting")
    print("2: Receiving")
    print("3: Location of the last unicorn")
    print("4: Grocery list")
    print("5: Log out")
    choice = input("Input the number of the option you want to see: ")
    return choice

def create_db():
    """ Create table 'users' in 'user' database """
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

def query_db():
    """ Display all records in the users table """
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