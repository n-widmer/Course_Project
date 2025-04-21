import os
import re

from flask import Flask, render_template, request, session, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.secret_key = os.getenv('SECRET_KEY')

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register_user():
    message = ""
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form and 'username' in request.form:
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
            cursor = mysql.connection.cursor()
            query = f"INSERT INTO Users (email, username, password) VALUES ('{email}', '{username}', '{hashed_password}');"
            cursor.execute(query)
            #cursor.execute(query, (email, username, password,))
            mysql.connection.commit()
            cursor.close()
            message = "You Have Successfully Registered"

        return render_template("index.html", message=message, username=username)
    else:
        message = "Please fill out the form correctly"
        return render_template("register.html", message=message)

@app.route("/login", methods=['GET', 'POST'])
def login_user():
    message = ""
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connection.cursor()
            query = f"SELECT * FROM Users WHERE username = '{username}' AND password = '{password}';"
            cursor.execute(query)
            #query = "SELECT * FROM Users WHERE email = %s AND password = %s;"
            #cursor.execute(query, (email, password,))
            account = cursor.fetchone()
            if account:
                message = "Login Successful"
                return render_template("index.html", message=message, username=username)
            else:
                message = "Invalid email or password"
                return render_template("login.html", message=message)
    return render_template("login.html")


@app.route("/logout", methods=['GET', 'POST'])
def logout_user():
    session.clear()
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)