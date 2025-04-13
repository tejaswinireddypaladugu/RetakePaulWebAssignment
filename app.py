from flask import Flask, jsonify, redirect, render_template,request,session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from flask import session
from werkzeug.security import generate_password_hash,check_password_hash
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
       return render_template('index.html',username=session.get('user'))
    return redirect('/login')

@app.route("/contactus")
def Contactus():
    if(session.get('user')):
       return render_template('contactus.html',username=session.get('user'))
    return redirect('/login')


@app.route("/login",methods=['GET','POST'])
def Login():
    if(request.method=='POST'):
        try:
                data = request.get_json()
                exist=db.users.find_one({'email':data['email']})
                if not exist:
                    return jsonify({'success': False, 'message': 'Email not registered'})
                if not check_password_hash(exist['password'], data['password']):
                    return jsonify({'success': False, 'message': 'Password not match'}) 
                session['user'] = exist['email']
                return jsonify({'success': True, 'message': 'Login success'}) 
        except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
    return render_template('login.html')

@app.route("/register",methods=['GET','POST'])
async def Register():
    if(request.method=='POST'):
        try:
                data = request.get_json()
                userData = {
                    'name': data['name'],
                    'email': data['email'],
                    'password':generate_password_hash(data['password'])  
                }
                exist=db.users.find_one({'email':data['email']})
                if exist:
                    return jsonify({'success': False, 'message': 'User already registered'}) 
                db.users.insert_one(userData)
                return jsonify({'success': True, 'message': 'User added successfully'}) 
        except Exception as e:
                return jsonify({'success': False, 'message': str(e)})
    return render_template('register.html')

@app.route("/sellcar", methods=['GET', 'POST'])
def Sellcar():
    if request.method == 'POST':
        carModel = request.form['car_model']
        carYear = request.form['car_year']
        carCondition = request.form['car_condition']
        carPrice = request.form['car_price']
        
        if 'car_image' not in request.files:
            return 'No image part', 400
        car_image = request.files['car_image']
        
        if car_image and allowed_file(car_image.filename):
            filename = secure_filename(car_image.filename)
            car_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            car_data = {
                'car_model': carModel,
                'car_year': carYear,
                'car_condition': carCondition,
                'car_price': carPrice,
                'car_image': os.path.join(app.config['UPLOAD_FOLDER'], filename)
            }
            db.cars.insert_one(car_data)  
            
            return jsonify({'success': True, 'message': 'Car Created successfully'}) 
    if(session.get('user')):
       return render_template('carsell.html',username=session.get('user'))
    return redirect('/login')    



@app.route('/editcar')
def EditCar():
    id=request.args.get('id')
    print('req',id)
    return render_template('carsell.html',id=id)

from bson.objectid import ObjectId

@app.route('/updatecar', methods=['PUT'])
def UpdateCar():
    if request.method == 'PUT':
        carID = request.form.get('car_id')  
            
        carModel = request.form['car_model']
        carYear = request.form['car_year']
        carCondition = request.form['car_condition']
        carPrice = request.form['car_price']

        carData = {
            'car_model': carModel,
            'car_year': carYear,
            'car_condition': carCondition,
            'car_price': carPrice
        }
    
        if 'car_image' in request.files:
            carImage = request.files['car_image']
            if carImage and allowed_file(carImage.filename):
                filename = secure_filename(carImage.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                carImage.save(filepath)
                carData['car_image'] = filepath 
        
        result = db.cars.update_one({"_id": ObjectId(carID)}, {"$set": carData})
        
        if result.modified_count > 0:
             return jsonify({'success': True, 'message': 'Car updated successfully'})
        else:
              return jsonify({'success': False, 'message': 'No changes made or car not found'})
        
@app.route('/deletecar', methods=['GET'])
def DeleteCar():
        carId = request.args.get('id')  
        if not carId:
            return jsonify({'success': False, 'message': 'Car ID not present'})
   
        db.cars.delete_one({"_id": ObjectId(carId)})
        return render_template('usedcars.html')
        
            
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/fetchcars")
def FetchCars():
    cars = list(db.cars.find({}).sort("car_price",1))  
    for car in cars:
        car["_id"] = str(car["_id"]) 
    return jsonify(cars)

@app.route("/usedcars")
def UsedCars():
    if(session.get('user')):
       return render_template('usedcars.html',username=session.get('user'))
    return redirect('/login')

@app.route("/services")
def Services():
    if(session.get('user')):
       return render_template('services.html',username=session.get('user'))
    return redirect('/login')



@app.route("/search", methods=["GET"])
async def SearchPage():
    if(session.get('user')):
        value = request.args.get('value')
        
        if value:
            query = {
                "$or": [
                    {"car_model": {"$regex": value, "$options": "i"}},  
                    {"car_year": {"$regex": value, "$options": "i"}},
                    {"car_condition": {"$regex": value, "$options": "i"}},
                    {"car_price": {"$regex": value, "$options": "i"}}, 
                ]
            }
            results = list(db.cars.find(query).sort("car_price",1))
        else:
            results = []

        print(results)
        return render_template('searchpage.html', results=results,username=session.get('user'))
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)