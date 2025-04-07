from flask import Flask, jsonify, redirect, render_template,request,session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from flask import session

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
                if exist['password'] != data['password']: 
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
                    'password':data['password']  
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
            
            return jsonify({'success': True, 'message': 'Car Created successfully'}) 
    if(session.get('user')):
       return render_template('carsell.html',username=session.get('user'))
    return redirect('/login')    



@app.route('/success')
def success():
    return '<h1>Your car has been listed for sale successfully!</h1>'

@app.route('/editcar')
def EditCar():
    id=request.args.get('id')
    print('req',id)
    return render_template('carsell.html',id=id)

from bson.objectid import ObjectId

@app.route('/updatecar', methods=['PUT'])
def UpdateCar():
    if request.method == 'PUT':
        car_id = request.form.get('car_id')  
            
        car_model = request.form['car_model']
        car_year = request.form['car_year']
        car_condition = request.form['car_condition']
        car_price = request.form['car_price']

        car_data = {
            'car_model': car_model,
            'car_year': car_year,
            'car_condition': car_condition,
            'car_price': car_price
        }
    
        if 'car_image' in request.files:
            car_image = request.files['car_image']
            if car_image and allowed_file(car_image.filename):
                filename = secure_filename(car_image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                car_image.save(filepath)
                car_data['car_image'] = filepath 
        
        result = db.cars.update_one({"_id": ObjectId(car_id)}, {"$set": car_data})
        
        if result.modified_count > 0:
             return jsonify({'success': True, 'message': 'Car updated successfully'})
        else:
              return jsonify({'success': False, 'message': 'No changes made or car not found'})
        
@app.route('/deletecar', methods=['GET'])
def DeleteCar():
        car_id = request.args.get('id')  
        print('id',car_id)
        if not car_id:
            return jsonify({'success': False, 'message': 'Car ID not present'})
   
        result = db.cars.delete_one({"_id": ObjectId(car_id)})
        return render_template('usedcars.html')
        
            
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/fetchcars")
def FetchCars():
    cars = list(db.cars.find({}))  
    for car in cars:
        car["_id"] = str(car["_id"]) 
    return jsonify(cars)

@app.route("/usedcars")
def UsedCars():
    if(session.get('user')):
       return render_template('usedcars.html',username=session.get('user'))
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
            results = list(db.cars.find(query))
        else:
            results = []

        print(results)
        return render_template('searchpage.html', results=results,username=session.get('user'))
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)