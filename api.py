from livekit.agents import llm
import enum
from typing import Annotated
import logging

from db_driver import db, add_patient

logger = logging.getLogger("patient-data")
logger.setLevel(logging.INFO)

# Define an enum for patient details keys.
class PatientDetails(enum.Enum):
    PATIENT_ID = "patientId"
    FIRST_NAME = "firstName"
    LAST_NAME = "lastName"
    PHONE_NUMBER = "phoneNumber"
    DATE_OF_BIRTH = "dateOfBirth"
    KNOWN_SYMPTOMS = "knownSymptoms"
    CURRENT_MEDICATIONS = "currentMedications"

class AssistantFunc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self._patient_details = {
            PatientDetails.PATIENT_ID: "",
            PatientDetails.FIRST_NAME: "",
            PatientDetails.LAST_NAME: "",
            PatientDetails.PHONE_NUMBER: "",
            PatientDetails.DATE_OF_BIRTH: "",
            PatientDetails.KNOWN_SYMPTOMS: "",
            PatientDetails.CURRENT_MEDICATIONS: ""
        }
    
    def get_patient_str(self):
        """Generate a formatted string of the patient details."""
        patient_str = ""
        for key, value in self._patient_details.items():
            patient_str += f"{key.value}: {value}\n"
        return patient_str
    
    @llm.ai_callable(description="Lookup a patient by their Patient ID")
    def lookup_patient(self, patient_id: Annotated[str, llm.TypeInfo(description="The ID of the patient to lookup")]):
        logger.info("Lookup patient - ID: %s", patient_id)
        
        result = db.get_patient(patient_id)
        if result is None:
            return "Patient not found"
        
        self._patient_details = {
            PatientDetails.PATIENT_ID: result.get("patientId", ""),
            PatientDetails.FIRST_NAME: result.get("firstName", ""),
            PatientDetails.LAST_NAME: result.get("lastName", ""),
            PatientDetails.PHONE_NUMBER: result.get("phoneNumber", ""),
            PatientDetails.DATE_OF_BIRTH: result.get("dateOfBirth", ""),
            PatientDetails.KNOWN_SYMPTOMS: ", ".join(result.get("knownSymptoms", [])) if result.get("knownSymptoms") else "",
            PatientDetails.CURRENT_MEDICATIONS: result.get("currentMedications", "")
        }
        
        return f"The patient details are:\n{self.get_patient_str()}"
    
    @llm.ai_callable(description="Get the details of the current patient")
    def get_patient_details(self):
        logger.info("Retrieve current patient details")
        return f"The patient details are:\n{self.get_patient_str()}"
    
    @llm.ai_callable(description="Create a new patient profile")
    def create_patient(
        self, 
        patient_id: Annotated[str, llm.TypeInfo(description="The unique Patient ID")],
        first_name: Annotated[str, llm.TypeInfo(description="The first name of the patient")],
        last_name: Annotated[str, llm.TypeInfo(description="The last name of the patient")],
        phone_number: Annotated[str, llm.TypeInfo(description="The phone number of the patient")],
        date_of_birth: Annotated[str, llm.TypeInfo(description="The date of birth of the patient (YYYY-MM-DD)")],
        known_symptoms: Annotated[str, llm.TypeInfo(description="Known symptoms (comma-separated)")],
        current_medications: Annotated[str, llm.TypeInfo(description="Current medications (optional)")]=None
    ):
        logger.info("Create patient - ID: %s, Name: %s %s", patient_id, first_name, last_name)
        # Convert the comma-separated symptoms string into a list.
        symptoms_list = [symptom.strip() for symptom in known_symptoms.split(",")] if known_symptoms else []
        
        patient_data = {
            "patientId": patient_id,
            "firstName": first_name,
            "lastName": last_name,
            "phoneNumber": phone_number,
            "dateOfBirth": date_of_birth,
            "knownSymptoms": symptoms_list,
            "currentMedications": current_medications
        }
        
        # Add the patient to the database.
        add_patient(patient_data)
        
        self._patient_details = {
            PatientDetails.PATIENT_ID: patient_data.get("patientId", ""),
            PatientDetails.FIRST_NAME: patient_data.get("firstName", ""),
            PatientDetails.LAST_NAME: patient_data.get("lastName", ""),
            PatientDetails.PHONE_NUMBER: patient_data.get("phoneNumber", ""),
            PatientDetails.DATE_OF_BIRTH: patient_data.get("dateOfBirth", ""),
            PatientDetails.KNOWN_SYMPTOMS: ", ".join(patient_data.get("knownSymptoms", [])),
            PatientDetails.CURRENT_MEDICATIONS: patient_data.get("currentMedications", "")
        }
        
        return "Patient profile created successfully!"
    
    @llm.ai_callable(description="Find a patient by name and date of birth")
    def find_patient_by_name_dob(
        self,
        first_name: Annotated[str, llm.TypeInfo(description="The first name of the patient")],
        last_name: Annotated[str, llm.TypeInfo(description="The last name of the patient")],
        date_of_birth: Annotated[str, llm.TypeInfo(description="The date of birth of the patient (YYYY-MM-DD)")],
    ):
        logger.info("Find patient - Name: %s %s, DOB: %s", first_name, last_name, date_of_birth)
        # Assume there is a corresponding function in the db module to find a patient by name and DOB.
        result = db.find_patient_by_name_dob(first_name, last_name, date_of_birth)
        if result is None:
            return "Patient not found"
        
        self._patient_details = {
            PatientDetails.PATIENT_ID: result.get("patientId", ""),
            PatientDetails.FIRST_NAME: result.get("firstName", ""),
            PatientDetails.LAST_NAME: result.get("lastName", ""),
            PatientDetails.PHONE_NUMBER: result.get("phoneNumber", ""),
            PatientDetails.DATE_OF_BIRTH: result.get("dateOfBirth", ""),
            PatientDetails.KNOWN_SYMPTOMS: ", ".join(result.get("knownSymptoms", [])) if result.get("knownSymptoms") else "",
            PatientDetails.CURRENT_MEDICATIONS: result.get("currentMedications", "")
        }
        
        return f"Patient found:\n{self.get_patient_str()}"
    
    def has_patient(self):
        """Check if the current profile has a valid Patient ID."""
        return self._patient_details[PatientDetails.PATIENT_ID] != ""