###################################################### Imports #########################################################################################################
from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

###################################################### database and configuration #########################################################################################################
load_dotenv()
app = Flask(__name__)
CORS(app)
db_username = os.getenv('db_username')
db_password = os.getenv('db_password')
host_address = os.getenv('host_address')
port= os.getenv('port')
db_name = os.getenv('db_name')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_username}:{db_password}@{host_address}:{port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Configure the session
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize the session
Session(app)

###################################################### Database declaration and creation ########################################################################################################
# Create the engine to connect to the MySQL server (without specifying the database)
engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@{host_address}:{port}')

# Create the database
database_name = os.getenv('db_name')

def create_database(engine, database_name):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database_name}"))

create_database(engine, database_name)

# Now connect to the newly created database
engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@{host_address}:{port}/{database_name}')

###################################################### Table declaration and creation #########################################################################################################
# Define the base class
Base = declarative_base()

# Define the User class
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    username=db.Column(db.String(100), unique=True, nullable=False)
    email=db.Column(db.String(100), unique=True, nullable=False)
    password=db.Column(db.String(100), nullable=False)
    mobile=db.Column(db.BigInteger)
    
# Define the Bakery class
class Bakery(db.Model):
    __tablename__ = 'bakery'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    price=db.Column(db.String(100))
    imageUrl=db.Column(db.String(100))
    quantity=db.Column(db.String(100))
    
# Define the Ingredients class
class Ingredients(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    quantity=db.Column(db.String(100))
    purpose=db.Column(db.String(100))
    orderItem=db.Column(db.Boolean)
    
# Define the Employees class
class Employees(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    
# Define the Contactus class
class Contactus(db.Model):
    __tablename__ = 'contactus'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))
    phone=db.Column(db.BigInteger)
    message=db.Column(db.String(100))
    
# Define the Comment model
class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    replies = db.relationship('Reply', backref='comment', lazy=True, cascade="all, delete-orphan")

# Define the Reply model
class Reply(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    
# Set up the database engine
engine = create_engine(f'mysql+pymysql://{db_username}:{db_password}@{host_address}:{port}/{db_name}')

# Create the table in the database
Base.metadata.create_all(engine)

# Create the database and the table
# with app.app_context():
#     db.create_all()

###################################################### code starts for api creation #########################################################################################################
@app.route('/')
def root():
    return 'Welcome to the API!'

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    mobile = data.get('mobile')
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    
    if not name or not mobile or not email or not password or not username:
        return jsonify({"error": "Missing required fields"}), 400
    
    new_user = User(name=name, mobile=mobile, email=email, password=password,username=username)
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "User with this mobile or email already exists"}), 409
    
    return jsonify({"message": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')  # Can be mobile or email
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Find the user by username or email
    # user = User.query.filter(User.username == username).first()
    user = User.query.filter(User.email == email).first()
    
    if user and (user.password == password):
        # Store user info in session
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return jsonify({"message": "Logout successful"}), 200

# Define the route for the POST request to add all bakery
@app.route('/bakery', methods=['POST'])
def add_bakery():
    data = request.get_json()
    for bakery in data:
        new_bakery = Bakery(
            name=bakery['name'],
            price=bakery['price'],
            imageUrl=bakery['imageUrl'],
            quantity=bakery['quantity']
        )
        db.session.add(new_bakery)
    db.session.commit()
    return jsonify({"message": "Bakery added successfully!"}), 201

# Define the route for the GET request to fetch all bakery
@app.route('/bakery', methods=['GET'])
def get_cakes():
    bakerys = Bakery.query.all()
    results = [
        {
            "id": bakery.id,
            "name": bakery.name,
            "price": bakery.price,
            "imageUrl": bakery.imageUrl,
            "quantity": bakery.quantity
        } for bakery in bakerys]

    return jsonify(results), 200


# Define the route for the POST request to add all ingredients
@app.route('/ingredients', methods=['POST'])
def add_ingredients():
    data = request.get_json()
    for ingredients in data:
        new_ingredients = Ingredients(
            name=ingredients['name'],
            purpose=ingredients['purpose'],
            orderItem=ingredients['orderItem'],
            quantity=ingredients['quantity']
        )
        db.session.add(new_ingredients)
    db.session.commit()
    return jsonify({"message": "ingredients added successfully!"}), 201

# Define the route for the GET request to fetch all ingredients
@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    ingredients = Ingredients.query.all()
    results = [
        {
            "id": ingredient.id,
            "name": ingredient.name,
            "purpose": ingredient.purpose,
            "orderItem": ingredient.orderItem,
            "quantity": ingredient.quantity
        } for ingredient in ingredients]

    return jsonify(results), 200

# Define the route for the POST request to add all Employees 
@app.route('/employees', methods=['POST'])
def add_employees():
    data = request.get_json()
    for employees in data:
        new_employees = Employees(
            name=employees['name'],
        )
        db.session.add(new_employees)
    db.session.commit()
    return jsonify({"message": "Employees added successfully!"}), 201

# Define the route for the GET request to fetch all Employees 
@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employees.query.all()
    results = [
        {
            "id": employee.id,
            "name": employee.name
        } for employee in employees]

    return jsonify(results), 200


# Define the route for the POST request to add all Contact Us 
@app.route('/contactus', methods=['POST'])
def add_contactus():
    data = request.get_json()
    
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    message = data.get('message')

    
    new_contact = Contactus(name=name, phone=phone, email=email, message=message)
    
    try:
        db.session.add(new_contact)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error while saving contact"}), 409
    
    return jsonify({"message": "Contact created successfully"}), 201

# Define the route for the GET request to fetch all Contact Us 
@app.route('/contactus', methods=['GET'])
def get_contactus():
    contactus = Contactus.query.all()
    results = [
        {
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phone,
            "message": contact.message
        } for contact in contactus]

    return jsonify(results), 200


# Define the route for the POST request to add comments and replies
@app.route('/comments', methods=['POST'])
def add_comments():
    data = request.get_json()
    new_reply = Reply(
        comment_id=data['id'],
        name=data['name'],
        text=data['text']
    )
    db.session.add(new_reply)
    db.session.commit()
    return jsonify({"message": "Replies added successfully!"}), 201

# Define the route for the GET request to fetch comments and replies
@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comments.query.all()
    results = []
    for comment in comments:
        replies = Reply.query.filter_by(comment_id=comment.id).all()
        replies_list = [
            {
                "id": reply.id,
                "name": reply.name,
                "text": reply.text
            } for reply in replies]
        
        results.append({
            "id": comment.id,
            "name": comment.name,
            "text": comment.text,
            "replies": replies_list
        })

    return jsonify(results), 200


####################################################### main driver function#########################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
