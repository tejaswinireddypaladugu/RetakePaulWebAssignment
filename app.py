from flask import Flask, jsonify, redirect, render_template,request,session
from pymongo import MongoClient

app=Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://tejaswinireddy989:tejaswini%40123@cluster0.8chifhn.mongodb.net/"

client = MongoClient(app.config['MONGO_URI'])
db = client.get_database('CarSellingProduct')

app.static_folder='static'

app.secret_key='1234'

@app.route("/")
def home():
    if(session.get('user')):
       print('user',session.get('user'))
       return render_template('index.html',username=session.get('user'))
    return render_template('index.html',username="")

if __name__ == "__main__":
    app.run(debug=True)