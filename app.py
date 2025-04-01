from flask import Flask, jsonify, redirect, render_template,request,session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os

app=Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/"

client = MongoClient(app.config['MONGO_URI'])
db = client.get_database('CarSellingProduct')

app.static_folder='static'

app.secret_key='1234'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def Home():
    if(session.get('user')):
       print('user',session.get('user'))
       return render_template('index.html',username=session.get('user'))
    return render_template('index.html',username="")

@app.route("/contactus")
def Contactus():
    return render_template('contactus.html',username="")

@app.route("/sellcar", methods=['GET', 'POST'])
def Sellcar():
    if request.method == 'POST':
        car_model = request.form['car_model']
        car_year = request.form['car_year']
        car_condition = request.form['car_condition']
        car_price = request.form['car_price']
        
        if 'car_image' not in request.files:
            return 'No image part', 400
        car_image = request.files['car_image']
        
        if car_image and allowed_file(car_image.filename):
            filename = secure_filename(car_image.filename)
            car_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            car_data = {
                'car_model': car_model,
                'car_year': car_year,
                'car_condition': car_condition,
                'car_price': car_price,
                'car_image': os.path.join(app.config['UPLOAD_FOLDER'], filename)
            }
            db.cars.insert_one(car_data)  
            
            return redirect('/success')  
    return render_template('carsell.html', username=session.get('user'))


@app.route('/success')
def success():
    return '<h1>Your car has been listed for sale successfully!</h1>'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/fetchcars")
def get_cars():
    cars = list(db.cars.find({}, {"_id": 0}))  
    return jsonify(cars)

if __name__ == "__main__":
    app.run(debug=True)