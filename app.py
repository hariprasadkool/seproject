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
    email=db.Column(db.String(100), unique=True, nullable=False)
    password=db.Column(db.String(100), nullable=False)
    mobile=db.Column(db.BigInteger)
    
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
    
    if not name or not mobile or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    new_user = User(name=name, mobile=mobile, email=email, password=password)
    
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
    
    email = data.get('email')  # Can be mobile or email
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Find the user by mobile or email
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


####################################################### main driver function#########################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
