import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import json
import uuid

# API URL - Update with your FastAPI URL
API_URL = "https://anxiety-project-2j9z.onrender.com"


# Set page configuration
st.set_page_config(
    page_title="Anxiety Assessment App - Patient Portal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Functions for API calls
def get_questionnaire(questionnaire_id):
    response = requests.get(f"{API_URL}/questionnaires/{questionnaire_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None


def submit_assessment(patient_id, questionnaire_id, answers):
    data = {
        "patient_id": patient_id,
        "questionnaire_id": questionnaire_id,
        "answers": answers,
        "timestamp": datetime.now().isoformat()
    }

    response = requests.post(f"{API_URL}/assessments/", json=data)
    if response.status_code == 201:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None


def get_patient_assessments(patient_id):
    response = requests.get(f"{API_URL}/assessments/patient/{patient_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return {"assessments": []}


def get_latest_assessment(patient_id):
    response = requests.get(f"{API_URL}/patient/{patient_id}/latest-assessment")
    if response.status_code == 200:
        return response.json()
    else:
        return None


def register_patient(name, email, age, gender):
    data = {
        "id": str(uuid.uuid4()),  # Generate UUID here
        "name": name,
        "email": email,
        "age": age,
        "gender": gender
    }

    response = requests.post(f"{API_URL}/patients/", json=data)
    if response.status_code == 201:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

def get_all_doctors():
    response = requests.get(f"{API_URL}/doctors/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return []


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4F8BF9;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4F8BF9;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .assessment-score {
        font-size: 3rem;
        text-align: center;
        font-weight: bold;
    }
    .assessment-level {
        font-size: 1.5rem;
        text-align: center;
        font-weight: bold;
    }
    .level-minimal {
        color: #00cc96;
    }
    .level-mild {
        color: #ffa15a;
    }
    .level-moderate {
        color: #ef553b;
    }
    .level-severe {
        color: #ab63fa;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'patient_id' not in st.session_state:
    st.session_state.patient_id = None
if 'patient_name' not in st.session_state:
    st.session_state.patient_name = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'assessment_completed' not in st.session_state:
    st.session_state.assessment_completed = False
if 'questionnaire' not in st.session_state:
    st.session_state.questionnaire = None
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0


# Navigation functions
def go_to_dashboard():
    st.session_state.page = 'dashboard'
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.assessment_completed = False


def go_to_assessment():
    st.session_state.page = 'assessment'
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.assessment_completed = False
    if not st.session_state.questionnaire:
        st.session_state.questionnaire = get_questionnaire("bai")


def go_to_doctors():
    st.session_state.page = 'doctors'


def logout():
    st.session_state.patient_id = None
    st.session_state.patient_name = None
    st.session_state.page = 'login'


# Sidebar navigation
def show_sidebar():
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.patient_name}")
        st.markdown("---")

        if st.button("📊 Dashboard", use_container_width=True):
            go_to_dashboard()

        if st.button("📝 Take Assessment", use_container_width=True):
            go_to_assessment()

        if st.button("👨‍⚕️ Find Doctors", use_container_width=True):
            go_to_doctors()

        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            logout()


# Login/Registration Page
def show_login_page():
    st.markdown("<h1 class='main-header'>Anxiety Assessment App</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Patient Portal</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        if st.button("Login", use_container_width=True):

            if email:
                # Find patient by email
                patients = requests.get(f"{API_URL}/patients/").json()
                patient = next((p for p in patients if p["email"] == email), None)

                if patient:
                    st.session_state.patient_id = patient["id"]
                    st.session_state.patient_name = patient["name"]
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Patient not found. Please register first.")
            else:
                st.error("Please enter your email")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Register")
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="register_email")
        age = st.number_input("Age", min_value=18, max_value=100, value=25)
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])

        if st.button("Register", use_container_width=True):
            if name and email and age:
                result = register_patient(name, email, age, gender)
                if result:
                    st.success("Registration successful!")
                    st.session_state.patient_id = result["id"]
                    st.session_state.patient_name = name
                    st.session_state.page = 'dashboard'
                    time.sleep(1)  # Give user time to see the success message
                    st.rerun()
            else:
                st.error("Please fill in all required fields")
        st.markdown("</div>", unsafe_allow_html=True)


# Dashboard Page
def show_dashboard():
    st.markdown("<h1 class='main-header'>Patient Dashboard</h1>", unsafe_allow_html=True)

    # Get the patient's assessment history
    assessment_data = get_patient_assessments(st.session_state.patient_id)
    assessments = assessment_data.get("assessments", [])

    # Get the latest assessment
    latest_assessment = get_latest_assessment(st.session_state.patient_id)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Quick Actions")

        if st.button("Take New Assessment", key="dashboard_take_assessment", use_container_width=True):
            go_to_assessment()

        if st.button("Find Doctors", key="dashboard_find_doctors", use_container_width=True):
            go_to_doctors()
        st.markdown("</div>", unsafe_allow_html=True)

        # Show latest assessment result if available
        if latest_assessment:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Latest Assessment")
            score = latest_assessment.get("score", 0)
            level = latest_assessment.get("level", "Unknown")

            level_class = ""
            if level == "Minimal Anxiety":
                level_class = "level-minimal"
            elif level == "Mild Anxiety":
                level_class = "level-mild"
            elif level == "Moderate Anxiety":
                level_class = "level-moderate"
            elif level == "Severe Anxiety":
                level_class = "level-severe"

            st.markdown(f"<div class='assessment-score'>{score}/63</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='assessment-level {level_class}'>{level}</div>", unsafe_allow_html=True)

            timestamp_raw = latest_assessment.get("timestamp") if latest_assessment else None

            if timestamp_raw:
                timestamp = datetime.fromisoformat(timestamp_raw.replace("Z", "+00:00")).strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp = "Unknown"

            if level in ["Moderate Anxiety", "Severe Anxiety"]:
                st.warning("Consider consulting with a mental health professional.")
                if st.button("Find Help Now", use_container_width=True):
                    go_to_doctors()
            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Assessment History")

        if not assessments:
            st.info("You haven't taken any assessments yet.")
            if st.button("Take Your First Assessment", use_container_width=True):
                go_to_assessment()
        else:
            # Create dataframe for visualizations
            df = pd.DataFrame(assessments)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')

            # Line chart of scores over time
            fig = px.line(
                df,
                x='timestamp',
                y='score',
                title='Anxiety Scores Over Time',
                labels={'timestamp': 'Date', 'score': 'Anxiety Score'},
                markers=True
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Score",
                yaxis=dict(range=[0, 63]),  # Updated to match BAI max score of 63
                hovermode="x unified"
            )
            # Add horizontal threshold lines based on BAI scoring
            fig.add_hline(y=21, line_dash="dot", line_color="orange", annotation_text="Mild")
            fig.add_hline(y=26, line_dash="dot", line_color="red", annotation_text="Moderate")
            fig.add_hline(y=34, line_dash="dot", line_color="purple", annotation_text="Severe")

            st.plotly_chart(fig, use_container_width=True)

            # Show assessment history table
            st.subheader("Past Assessments")

            # Format the dataframe for display
            display_df = df[['timestamp', 'score', 'level']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            display_df.columns = ['Date', 'Score', 'Anxiety Level']
            display_df = display_df.sort_values('Date', ascending=False)

            st.dataframe(display_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# Assessment Page
def show_assessment():
    if not st.session_state.questionnaire:
        st.session_state.questionnaire = get_questionnaire("bai")

    questionnaire = st.session_state.questionnaire

    if not questionnaire:
        st.error("Failed to load the questionnaire. Please try again later.")
        return

    st.markdown(f"<h1 class='main-header'>{questionnaire['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p>{questionnaire['description']}</p>", unsafe_allow_html=True)

    if st.session_state.assessment_completed:
        st.success("Assessment completed! Your responses have been recorded.")

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("View Dashboard", use_container_width=True):
                go_to_dashboard()

        with col2:
            if st.button("Take Again", use_container_width=True):
                st.session_state.answers = {}
                st.session_state.current_question = 0
                st.session_state.assessment_completed = False
                st.rerun()

        return

    # Display progress bar
    questions = questionnaire["questions"]
    progress = min(1.0, (len(st.session_state.answers) / len(questions)))
    st.progress(progress)

    # If we have all answers, submit the assessment
    if len(st.session_state.answers) == len(questions):
        result = submit_assessment(
            st.session_state.patient_id,
            questionnaire["id"],
            st.session_state.answers
        )

        if result:
            st.session_state.assessment_completed = True
            st.rerun()
        return

    # Display current question
    current_question = questions[st.session_state.current_question]

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader(f"Question {current_question['id']} of {len(questions)}")
    st.markdown(f"**{current_question['text']}**")

    # Create radio buttons for the options
    option_keys = [f"{opt['value']} - {opt['text']}" for opt in current_question['options']]
    selected_option = st.radio("Select your response:", option_keys, key=f"q_{current_question['id']}")

    # Extract the selected value from the option text
    selected_value = int(selected_option.split(" - ")[0])

    col1, col2 = st.columns([1, 1])

    with col2:
        if st.button("Next", use_container_width=True):
            # Save the answer
            st.session_state.answers[current_question['id']] = selected_value

            # Move to the next question
            if st.session_state.current_question < len(questions) - 1:
                st.session_state.current_question += 1

            st.rerun()

    with col1:
        if st.session_state.current_question > 0:
            if st.button("Previous", use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# Doctors Page
def show_doctors():
    st.markdown("<h1 class='main-header'>Find Mental Health Professionals</h1>", unsafe_allow_html=True)

    # Get the latest assessment to show recommendations
    latest_assessment = get_latest_assessment(st.session_state.patient_id)

    # Get all doctors
    doctors = get_all_doctors()

    col1, col2 = st.columns([1, 2])

    with col1:
        if latest_assessment:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Your Assessment Status")

            score = latest_assessment.get("score", 0)
            level = latest_assessment.get("level", "Unknown")

            level_class = ""
            if level == "Minimal Anxiety":
                level_class = "level-minimal"
            elif level == "Mild Anxiety":
                level_class = "level-mild"
            elif level == "Moderate Anxiety":
                level_class = "level-moderate"
            elif level == "Severe Anxiety":
                level_class = "level-severe"

            st.markdown(f"<div class='assessment-score'>{score}/63</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='assessment-level {level_class}'>{level}</div>", unsafe_allow_html=True)

            if level == "Minimal Anxiety":
                st.info(
                    "Based on your assessment, you're experiencing minimal anxiety. Regular mental wellness check-ups are still beneficial.")
            elif level == "Mild Anxiety":
                st.info(
                    "Based on your assessment, you're experiencing mild anxiety. Consider talking to a mental health professional about strategies to manage your anxiety.")
            elif level == "Moderate Anxiety":
                st.warning(
                    "Based on your assessment, you're experiencing moderate anxiety. It's recommended to consult with a mental health professional soon.")
            else:  # Severe
                st.error(
                    "Based on your assessment, you're experiencing severe anxiety. Please consider reaching out to a mental health professional as soon as possible.")

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.info("You haven't taken any assessments yet. Take an assessment to get personalized recommendations.")

            if st.button("Take an Assessment Now", use_container_width=True):
                go_to_assessment()
            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Available Mental Health Professionals")

        # Search and filter
        search_name = st.text_input("Search by name:")
        specialization_filter = st.multiselect(
            "Filter by specialization:",
            options=list(set(d["specialization"] for d in doctors)),
            default=[]
        )

        # Apply filters
        filtered_doctors = doctors
        if search_name:
            filtered_doctors = [d for d in filtered_doctors if search_name.lower() in d["name"].lower()]

        if specialization_filter:
            filtered_doctors = [d for d in filtered_doctors if d["specialization"] in specialization_filter]

        if not filtered_doctors:
            st.info("No doctors match your search criteria.")
        else:
            for doctor in filtered_doctors:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(doctor["name"])
                        st.write(f"**Specialization:** {doctor['specialization']}")
                        st.write(f"**Email:** {doctor['email']}")
                        st.write(f"**Phone:** {doctor['phone']}")
                    with col2:
                        st.button("Contact", key=f"contact_{doctor['id']}")
                    st.divider()

        st.markdown("</div>", unsafe_allow_html=True)


# Main app logic
def main():
    try:
        # Check API connection
        requests.get(f"{API_URL}/")
    except:
        st.error("Cannot connect to the API. Please make sure the FastAPI backend is running.")
        st.warning(f"Attempting to connect to: {API_URL}")
        return

    if st.session_state.patient_id:
        show_sidebar()

        if st.session_state.page == 'dashboard':
            show_dashboard()
        elif st.session_state.page == 'assessment':
            show_assessment()
        elif st.session_state.page == 'doctors':
            show_doctors()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
