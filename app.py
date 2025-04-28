import os
import re

from flask import Flask, render_template, request, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import base64
from hashlib import sha256
from binascii import unhexlify




app = Flask(__name__)

app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # to ensure out 'account' always returns a dictionary
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.secret_key = os.getenv('SECRET_KEY')
key_hex = os.getenv('AESKEY')
key = unhexlify(key_hex)



mysql = MySQL(app)

@app.route("/")
def index():

    print(key)
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register_user():
    message = ""
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form and 'username' in request.form and 'phone' in request.form:
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            phone = request.form['phone']
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
            cursor = mysql.connection.cursor()

            encrypted_phone = encrypt_phone(phone, key)

            query = f"INSERT INTO users (username, email, password, phone) VALUES ('{username}', '{email}', '{hashed_password}', '{encrypted_phone}');"
            cursor.execute(query)

            #cursor.execute(query, (email, username, password,))
            mysql.connection.commit()
            cursor.close()
            message = "You Have Successfully Registered"

            return render_template("index.html", message=message, email=email, username=username)
        else:
            message = "Please fill out the form correctly"
            return render_template("register.html", message=message)
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login_user():
    message = ""
    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            #password = request.form['password']
            cursor = mysql.connection.cursor()
            query = f"SELECT * FROM Users WHERE username = '{username}';"
            cursor.execute(query)
            #query = "SELECT * FROM Users WHERE email = %s AND password = %s;"
            #cursor.execute(query, (email, password,))
            account = cursor.fetchone()
            #if account:
                #stored_password = account['password']
                #email = account['email']
                #if check_password_hash(stored_password, password):
                    #message = "Login Successful"
                    #return render_template("index.html", message=message, email=email, username=username)
                #else:
                    #print("check password hash fails")
                    #message = "Invalid email or password"
            #else:
            message = "Login Successful!"
            return render_template("index.html", message=message, username=username)
        else:
            message = "Incorrect email or password... Try Again"
            return render_template("login.html")
    return render_template("login.html")


@app.route("/logout", methods=['GET', 'POST'])
def logout_user():
    session.clear()
    return render_template("index.html")





def encrypt_phone(phone, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(phone.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + ':' + ct

"""def decrypt_phone(encrypted_phone, key):
    iv, ct = encrypted_phone.split(':')
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')"""

if __name__ == '__main__':
    app.run(debug=True)


    