from helpers import *
# from config import display
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__, static_folder='instance/static')

app.config.from_object('config')


@app.route("/", methods=['GET', 'POST'])
def home():
    """ Home page """
    return render_template('home.html',
                           title="Home Page",
                           heading="Home Page"
                           )


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
            elif not sign_in(stored_data, username, password):
                flash("Invalid name or password", 'alert-danger')
                print(attempts)
                return redirect(url_for('login', attempts=attempts))

            elif sign_in(stored_data, username, password):
                print("Logged in!")
                for user in stored_data:
                    if user[0] == username:
                        access_level = user[2]
                return redirect(url_for('login_success', access_level=access_level))

        except KeyError:
            pass
        flash("Invalid username or password!", 'alert-danger')
    return render_template('login.html',
                           title="Secure Login",
                           heading="Secure Login")


@app.route("/login_success/<int:access_level>", methods=['GET', 'POST'])
def login_success(access_level):
    flash("Welcome! You have logged in!", 'alert-success')
    # Different home pages for people with different access levels
    if access_level == 1:
        return render_template('customer_home_1.html',
                               title="Customer Home",
                               heading="Customer Home")
    elif access_level == 2:
        return render_template('customer_home_2.html',
                               title="Customer Home",
                               heading="Customer Home")
    elif access_level == 3:
        return render_template('customer_home_3.html',
                               title="Customer Home",
                               heading="Customer Home")
    else:
        # Give the lowest access level if somehow they have invalid access level
        return render_template('customer_home_1.html',
                               title="Customer Home",
                               heading="Customer Home")


@app.route("/new-user", methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        # User-entered values
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            success = add_user(username, password)

            if not success:
                flash("A user with that username is already registered! Try again!", 'alert-danger')
            else:
                flash("Success!", 'alert-success')
                return redirect(url_for('login_success', access_level=1))

        except KeyError:
            pass

    return render_template('new_user.html',
                           title="Register New User",
                           heading="Register New User")

if __name__ == '__main__':
    app.run(debug=app.debug, host='localhost', port=5200)
