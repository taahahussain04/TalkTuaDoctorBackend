import os
from livekit import api
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from livekit.api import LiveKitAPI, ListRoomsRequest
import uuid
import json
import traceback
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('talktuadoctor-firebase-adminsdk.json') 
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

async def generate_room_name():
    name = "room-" + str(uuid.uuid4())[:8]
    rooms = await get_rooms()
    while name in rooms:
        name = "room-" + str(uuid.uuid4())[:8]
    return name

async def get_rooms():
    api = LiveKitAPI()
    rooms = await api.room.list_rooms(ListRoomsRequest())
    await api.aclose()
    return [room.name for room in rooms.rooms]

@app.route("/getToken")
async def get_token():
    name = request.args.get("name", "my name")
    room = request.args.get("room", None)
    
    if not room:
        room = await generate_room_name()
        
    token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")) \
        .with_identity(name)\
        .with_name(name)\
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room
        ))
    
    return token.to_jwt()

@app.route('/login', methods=['POST'])
def login():
    print("=== Login Request ===")
    print(f"Request Method: {request.method}")
    print(f"Request Headers: {dict(request.headers)}")
    print(f"Request Body: {request.get_data(as_text=True)}")
    
    try:
        print("Parsing request data...")
        user_data = request.json
        if not user_data:
            print("No JSON data received")
            return jsonify({'error': 'No data received'}), 400
            
        print(f"User data received: {json.dumps(user_data, indent=2)}")
        
        if not user_data.get('uid') or not user_data.get('email'):
            print("Error: Invalid user data - missing uid or email")
            return jsonify({'error': 'Invalid user data - missing uid or email'}), 400
        
        # Add debug logging for Firestore operations
        print(f"Attempting to access Firestore - db object type: {type(db)}")
        
        # Use email as document ID instead of UID
        user_ref = db.collection('users').document(user_data['email'])
        print(f"Created document reference for email: {user_data['email']}")
        
        user_doc = user_ref.get()
        print(f"Retrieved document snapshot - exists: {user_doc.exists}")
        
        if not user_doc.exists:
            print(f"Creating new user document with data:")
            user_data_to_save = {
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'email': user_data['email'],
                'photo_url': user_data.get('photo_url', ''),
                'uid': user_data['uid'],
                'created_at': firestore.SERVER_TIMESTAMP
            }
            # Print the data without the SERVER_TIMESTAMP
            print({k: v for k, v in user_data_to_save.items() if k != 'created_at'})
            
            try:
                user_ref.set(user_data_to_save)
                print("Document creation successful")
            except Exception as e:
                print(f"Document creation failed with error: {str(e)}")
                raise
                
            return jsonify({'message': 'User created successfully'}), 201
        
        print(f"User already exists - Email: {user_data['email']}")
        return jsonify({'message': 'User already exists'}), 200
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({'error': f'An error occurred during login: {str(e)}'}), 500


if __name__ == "__main__":
    app.run(port=8000, debug=True)