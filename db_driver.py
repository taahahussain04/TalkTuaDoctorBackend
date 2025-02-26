# firebase_setup.py
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('talktuadoctor-firebase-adminsdk.json')  # Path to your downloaded JSON key
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def add_patient(patient_data):
    try:
        # Create or update the document in the "patients" collection using patientId as the document ID.
        db.collection('patients').document(patient_data['patientId']).set(patient_data)
        print(f"Patient {patient_data['patientId']} added successfully!")
    except Exception as e:
        print("Error adding patient:", e)

def get_patient(patient_id):
   
    try:
        doc_ref = db.collection('patients').document(patient_id)
        doc = doc_ref.get()
        if doc.exists:
            print(f"Patient {patient_id} found:")
            return doc.to_dict()
        else:
            print(f"No patient found with ID: {patient_id}")
            return None
    except Exception as e:
        print("Error retrieving patient:", e)
        return None

def collect_patient_info(patientId, firstName, lastName, phoneNumber, dateOfBirth, knownSymptoms, currentMedications=None):
    patient_data = {
        "patientId": patientId,
        "firstName": firstName,
        "lastName": lastName,
        "phoneNumber": phoneNumber,
        "dateOfBirth": dateOfBirth,
        "knownSymptoms": knownSymptoms.split(",") if isinstance(knownSymptoms, str) else knownSymptoms,
        "currentMedications": currentMedications if currentMedications else None
    }
    db.collection('patients').document(patientId).set(patient_data)
    return patient_data

def find_patient_by_name_dob(firstName, lastName, dateOfBirth):
    """
    Finds a patient by first name, last name, and date of birth.
    """
    query = db.collection('patients').where('firstName', '==', firstName).where('lastName', '==', lastName).where('dateOfBirth', '==', dateOfBirth)
    results = query.get()

def add_appointment(patient_id, appointment_data):
    try:
        # Get the patient document reference
        patient_ref = db.collection('patients').document(patient_id)
        
        # Get the current appointments array or create a new one
        patient_doc = patient_ref.get()
        if patient_doc.exists:
            current_data = patient_doc.to_dict()
            appointments = current_data.get('appointments', [])
            
            # Add the new appointment
            appointments.append(appointment_data)
            
            # Update the patient document with the new appointments array
            patient_ref.update({'appointments': appointments})
            
            print(f"Appointment added successfully for patient {patient_id}")
            return True
        else:
            print(f"No patient found with ID: {patient_id}")
            return False
            
    except Exception as e:
        print("Error adding appointment:", e)
        return False