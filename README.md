# CS 166 Climbing Final Project
## Aidan Brown
## To Run...

    - First, run the database_setup.py file to initailize the DB. 
    - Then run app.py to see the Climbing site
    - Sign in (with existing username or pw) or create a new user
    - Only certain users have upper access (2 & 3), check the database_setup
      to see which users do
    - All new users only have access to access 1
    - Passwords must be at least 7 chars long, 22 max, and include an upper, lower, num, and special char
    - Leave password blank to access automatic password generator    
    - Hashing/Salting takes place on backend, in app.py

## Database:
    - This uses SQLite, which is simpler and easier to use than actual MYSQL
    - It's more limited, but for this project seemed like a better choice
    - The only table is the "users" table, with a username, hashed pw, and access level