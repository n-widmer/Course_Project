import os
import re

from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL

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
        if 'email' in request.form and 'password' in request.form and 'name' in request.form and 'phone_number' in request.form:
            email = request.form['email']
            password = request.form['password']
            phone_number = request.form['phone_number']
            name = request.form['name']
            print("we are here")
            cursor = mysql.connection.cursor()
            query = "INSERT INTO Users (email, password, phone_number, name) VALUES (%s, %s, %s, %s);"
            cursor.execute(query, (email, password, phone_number, name,))
            mysql.connection.commit()
            message = "You Have Successfully Registered"
            cursor.close()
        return render_template("index.html", message=message, email=email)
    else:
        message = "Please fill out the form correctly"
        return render_template("register.html", message=message)

@app.route("/login", methods=['GET', 'POST'])
def login_user():
    message = ""
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = mysql.connection.cursor()
            query = "SELECT * FROM Users WHERE email = %s AND password = %s;"
            cursor.execute(query, (email, password,))
            account = cursor.fetchone()
            if account:
                message = "Login Successful"
                return render_template("index.html", message=message, email=email)
            else:
                message = "Invalid email or password"
                return render_template("login.html", message=message)
    return render_template("login.html")


@app.route("/logout", methods=['GET', 'POST'])
def logout_user():
    session.clear()
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)