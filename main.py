from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import os
import uuid

app = FastAPI(title="Anxiety Assessment API")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define data models
class QuestionOption(BaseModel):
    value: int
    text: str


class Question(BaseModel):
    id: int
    text: str
    options: List[QuestionOption]


class Questionnaire(BaseModel):
    id: str
    title: str
    description: str
    questions: List[Question]


class AnswerSubmission(BaseModel):
    patient_id: str
    questionnaire_id: str
    answers: Dict[int, int]  # Question ID to selected option value
    timestamp: Optional[datetime] = None


class Patient(BaseModel):
    id: str
    name: str
    email: str
    age: int
    gender: str


class Doctor(BaseModel):
    id: str
    name: str
    specialization: str
    email: str
    phone: str


# Check if the Excel files exist, if not create them
def init_database():
    if not os.path.exists('data'):
        os.makedirs('data')

    # Initialize patients database
    if not os.path.exists('data/patients.xlsx'):
        df = pd.DataFrame(columns=['id', 'name', 'email', 'age', 'gender'])
        df.to_excel('data/patients.xlsx', index=False)

    # Initialize doctors database
    if not os.path.exists('data/doctors.xlsx'):
        df = pd.DataFrame(columns=['id', 'name', 'specialization', 'email', 'phone'])
        df.to_excel('data/doctors.xlsx', index=False)

        # Add some sample doctors
        sample_doctors = [
            {"id": str(uuid.uuid4()), "name": "Dr. Sarah Johnson", "specialization": "Psychiatry",
             "email": "sjohnson@example.com", "phone": "555-1234"},
            {"id": str(uuid.uuid4()), "name": "Dr. Michael Chen", "specialization": "Clinical Psychology",
             "email": "mchen@example.com", "phone": "555-5678"},
            {"id": str(uuid.uuid4()), "name": "Dr. Emily Williams", "specialization": "Therapy",
             "email": "ewilliams@example.com", "phone": "555-9012"}
        ]
        doctors_df = pd.DataFrame(sample_doctors)
        doctors_df.to_excel('data/doctors.xlsx', index=False)

    # Initialize assessments database
    if not os.path.exists('data/assessments.xlsx'):
        df = pd.DataFrame(columns=['id', 'patient_id', 'questionnaire_id', 'score', 'level', 'timestamp'])
        df.to_excel('data/assessments.xlsx', index=False)

    # Initialize assessment details database
    if not os.path.exists('data/assessment_details.xlsx'):
        df = pd.DataFrame(columns=['assessment_id', 'question_id', 'answer_value'])
        df.to_excel('data/assessment_details.xlsx', index=False)


# Initialize database files
init_database()

# Anxiety assessment questionnaire
anxiety_questionnaire = Questionnaire(
    id="bai",
    title="Beck Anxiety Inventory (BAI)",
    description="Below is a list of common symptoms of anxiety. Please carefully read each item in the list. Indicate how much you have been bothered by that symptom during the past month, including today.",
    questions=[
        Question(
            id=1,
            text="Numbness or tingling",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Several days"),
                QuestionOption(value=2, text="More than half the days"),
                QuestionOption(value=3, text="Nearly every day")
            ]
        ),
        Question(
            id=2,
            text="Feeling hot",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Several days"),
                QuestionOption(value=2, text="More than half the days"),
                QuestionOption(value=3, text="Nearly every day")
            ]
        ),
        Question(
            id=3,
            text="Wobbliness in legs",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Several days"),
                QuestionOption(value=2, text="More than half the days"),
                QuestionOption(value=3, text="Nearly every day")
            ]
        ),
        Question(
            id=4,
            text="Unable to relax",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Several days"),
                QuestionOption(value=2, text="More than half the days"),
                QuestionOption(value=3, text="Nearly every day")
            ]
        ),
        Question(
            id=5,
            text="Fear of worst happening",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Several days"),
                QuestionOption(value=2, text="More than half the days"),
                QuestionOption(value=3, text="Nearly every day")
            ]
        ),
        Question(
            id=6,
            text="Dizzy or lightheaded",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Several days"),
                QuestionOption(value=2, text="More than half the days"),
                QuestionOption(value=3, text="Nearly every day")
            ]
        ),
        Question(
            id=7,
            text="Heart pounding / racing",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Several days"),
                QuestionOption(value=2, text="More than half the days"),
                QuestionOption(value=3, text="Nearly every day")
            ]
        ),
        Question(
            id=8,
            text="Unsteady",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=9,
            text="Terrified or afraid",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=10,
            text="Nervous",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=11,
            text="Feeling of choking",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=12,
            text="Hands trembling",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=13,
            text="Shaky / unsteady",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=14,
            text="Fear of losing control",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=15,
            text="Difficulty in breathing",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=16,
            text="Fear of dying",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=17,
            text="Scared",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=18,
            text="Indigestion",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=19,
            text="Faint / lightheaded",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=20,
            text="Face flushed",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        ),
        Question(
            id=21,
            text="Hot / cold sweats",
            options=[
                QuestionOption(value=0, text="Not at all"),
                QuestionOption(value=1, text="Mildly, but it didn't bother me much"),
                QuestionOption(value=2, text="Moderately – it wasn't pleasant at times"),
                QuestionOption(value=3, text="Severely – it bothered me a lot")
            ]
        )
    ]
)


# Function to calculate anxiety score and level
def calculate_anxiety_level(score):
    if score >= 0 and score <= 21:
        return "Minimal Anxiety"
    elif score >= 22 and score <= 26:
        return "Mild Anxiety"
    elif score >= 27 and score <= 34:
        return "Moderate Anxiety"
    else:
        return "Severe Anxiety"


# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the Anxiety Assessment API"}


@app.get("/questionnaires/{questionnaire_id}", response_model=Questionnaire)
def get_questionnaire(questionnaire_id: str):
    if questionnaire_id == anxiety_questionnaire.id:
        return anxiety_questionnaire
    raise HTTPException(status_code=404, detail="Questionnaire not found")


@app.get("/questionnaires", response_model=List[Questionnaire])
def get_questionnaires():
    return [anxiety_questionnaire]


@app.post("/patients/", status_code=status.HTTP_201_CREATED)
def create_patient(patient: Patient):
    try:
        df = pd.read_excel('data/patients.xlsx')

        # Check if email already exists
        if patient.email in df['email'].values:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Add new patient
        patient_dict = patient.dict()
        if not patient_dict.get('id'):
            patient_dict['id'] = str(uuid.uuid4())

        df = pd.concat([df, pd.DataFrame([patient_dict])], ignore_index=True)
        df.to_excel('data/patients.xlsx', index=False)

        return {"id": patient_dict['id'], "message": "Patient created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    try:
        df = pd.read_excel('data/patients.xlsx')
        patient = df[df['id'] == patient_id]

        if patient.empty:
            raise HTTPException(status_code=404, detail="Patient not found")

        return patient.iloc[0].to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patients/")
def get_all_patients():
    try:
        df = pd.read_excel('data/patients.xlsx')
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/doctors/")
def get_all_doctors():
    try:
        df = pd.read_excel('data/doctors.xlsx')
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assessments/", status_code=status.HTTP_201_CREATED)
def submit_assessment(submission: AnswerSubmission):
    try:
        # Validate patient exists
        patients_df = pd.read_excel('data/patients.xlsx')
        if submission.patient_id not in patients_df['id'].values:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Calculate score
        score = sum(submission.answers.values())
        level = calculate_anxiety_level(score)

        # Set timestamp if not provided
        if not submission.timestamp:
            submission.timestamp = datetime.now()

        # Generate assessment ID
        assessment_id = str(uuid.uuid4())

        # Save assessment summary
        assessments_df = pd.read_excel('data/assessments.xlsx')
        new_assessment = {
            'id': assessment_id,
            'patient_id': submission.patient_id,
            'questionnaire_id': submission.questionnaire_id,
            'score': score,
            'level': level,
            'timestamp': submission.timestamp
        }

        assessments_df = pd.concat([assessments_df, pd.DataFrame([new_assessment])], ignore_index=True)
        assessments_df.to_excel('data/assessments.xlsx', index=False)

        # Save assessment details
        details_df = pd.read_excel('data/assessment_details.xlsx')

        new_details = []
        for question_id, answer_value in submission.answers.items():
            new_details.append({
                'assessment_id': assessment_id,
                'question_id': question_id,
                'answer_value': answer_value
            })

        details_df = pd.concat([details_df, pd.DataFrame(new_details)], ignore_index=True)
        details_df.to_excel('data/assessment_details.xlsx', index=False)

        return {
            "assessment_id": assessment_id,
            "score": score,
            "level": level,
            "message": "Assessment submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/assessments/patient/{patient_id}")
def get_patient_assessments(patient_id: str):
    try:
        # Validate patient exists
        patients_df = pd.read_excel('data/patients.xlsx')
        if patient_id not in patients_df['id'].values:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Get patient assessments
        assessments_df = pd.read_excel('data/assessments.xlsx')
        patient_assessments = assessments_df[assessments_df['patient_id'] == patient_id]

        if patient_assessments.empty:
            return {"message": "No assessments found for this patient", "assessments": []}

        # Convert timestamps to string to ensure JSON serialization
        patient_assessments['timestamp'] = patient_assessments['timestamp'].astype(str)

        assessments_list = patient_assessments.to_dict(orient='records')

        # Add detailed answers to each assessment
        details_df = pd.read_excel('data/assessment_details.xlsx')

        for assessment in assessments_list:
            assessment_details = details_df[details_df['assessment_id'] == assessment['id']]
            assessment['answers'] = {}

            for _, detail in assessment_details.iterrows():
                assessment['answers'][int(detail['question_id'])] = int(detail['answer_value'])

        return {"assessments": assessments_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patient/{patient_id}/latest-assessment")
def get_latest_assessment(patient_id: str):
    try:
        assessments_df = pd.read_excel('data/assessments.xlsx')
        patient_assessments = assessments_df[assessments_df['patient_id'] == patient_id]

        if patient_assessments.empty:
            return {"message": "No assessments found for this patient"}

        # Sort by timestamp and get the latest
        patient_assessments['timestamp'] = pd.to_datetime(patient_assessments['timestamp'])
        latest_assessment = patient_assessments.sort_values('timestamp', ascending=False).iloc[0]

        # Get detailed answers
        details_df = pd.read_excel('data/assessment_details.xlsx')
        assessment_details = details_df[details_df['assessment_id'] == latest_assessment['id']]

        answers = {}
        for _, detail in assessment_details.iterrows():
            answers[int(detail['question_id'])] = int(detail['answer_value'])

        result = latest_assessment.to_dict()
        result['timestamp'] = str(result['timestamp'])
        result['answers'] = answers

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    try:
        df = pd.read_excel('data/doctors.xlsx')
        doctor = df[df['id'] == doctor_id]

        if doctor.empty:
            raise HTTPException(status_code=404, detail="Doctor not found")

        return doctor.iloc[0].to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the application with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)