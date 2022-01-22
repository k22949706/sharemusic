import imp
from app import *
from member import UserRegister
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_username = request.form['username']
        register_email = request.form['email']
        register_password = request.form['password']
        new_member = UserRegister(username=register_username, email=register_email, password=register_password)
        db.session.add(new_member)
        db.session.commit()
        return render_template("index.html")
    else:
        return render_template("register.html")