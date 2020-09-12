from flask import Flask, url_for, request, session, redirect, render_template, jsonify
from flask_pymongo import PyMongo
from functools import wraps
import json
from bson import json_util
from flask_bcrypt import Bcrypt
import dns
import os
from MongoDB import data
import model

app = Flask(__name__,template_folder="scr/components/layouts")
app.secret_key = os.getenv("secret_key")

@app.route('/', methods = ['POST', 'GET'])
def index():
    return render_template("index.html")

def checkLoggedIn():
    def check(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if 'username' in session:
                return func(*args, **kwargs)
            else:
                return jsonify({"error":"please login before accessing this page"})
        return inner
    return check               

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return jsonify({'status': 'logged in' })
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username' : request.form['username']})
        if login_user:
            pw_hash = bcrypt.check_password_hash(login_user['password'],request.form['password'])
            if pw_hash:
                session['username'] = request.form['username']
                return jsonify({ 'status' : 'login Successful'})
            else:
                return jsonify({'status': 'incorrect password'})
        return jsonify({'status': 'username does not exist' })
    return jsonify({'status' : 'load login page' })

@app.route('/signUp', methods=['POST', 'GET'])
def signup():
    session.pop('username', None)
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username':request.form['username']})
        if existing_user is None:
            hashpass = bcrypt.generate_password_hash(request.form['password'])
            users.insert({
                    'username' : request.form['username'],
                    'password' : hashpass}
                    )
            session['username'] = request.form['username']
            return jsonify({'status' : 'registration successful'})
        return jsonify({'status' : 'username already exists'})
    return jsonify({ 'status': 'load registration page' })

@app.route('/submit', methods = ["POST", "GET"])
@checkLoggedIn()
def submit():
    if 'username' in session:
        if request.method == "POST":
            text = request.form['text']
            author = session['username']
            url = request.form['url']
            name = request.form['name']
            mongo.db.comments.insert({'author': author, 'name':name, 'url': url, 'text': text })
            return jsonify({'status': 'your comment has been recorded'})
        return jsonify({ 'status': 'load comment submission page' })
    return jsonify({'status': 'you must be logged in to view this page'})

@app.route('/comments', methods = ["GET"])
def comment():
    comments = mongo.db.comments
    return jsonify(comments)

@app.route('/logout',methods=['GET'])
@checkLoggedIn()
def logout():
    session.pop('username')
    return jsonify({'status':'logout'})

if __name__ == '__main__':
    app.run(debug=True)