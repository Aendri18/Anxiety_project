import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# API URL - Update with your FastAPI URL
API_URL = "http://localhost:8000"

# Set page configuration
st.set_page_config(
    page_title="Anxiety Assessment App - Doctor Portal",
    page_icon="👨‍⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Functions for API calls
def get_all_patients():
    response = requests.get(f"{API_URL}/patients/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return []


def get_patient(patient_id):
    response = requests.get(f"{API_URL}/patients/{patient_id}")
    if response.status_code == 200:
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


def get_questionnaire(questionnaire_id):
    response = requests.get(f"{API_URL}/questionnaires/{questionnaire_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None


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
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'doctor_id' not in st.session_state:
    st.session_state.doctor_id = "doctor123"  # In a real app, this would come from authentication
if 'doctor_name' not in st.session_state:
    st.session_state.doctor_name = "Dr. Sarah Johnson"  # Example doctor name
if 'selected_patient_id' not in st.session_state:
    st.session_state.selected_patient_id = None
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
if 'questionnaire' not in st.session_state:
    st.session_state.questionnaire = None


# Navigation functions
def go_to_dashboard():
    st.session_state.page = 'dashboard'
    st.session_state.selected_patient_id = None


def go_to_patient_details(patient_id):
    st.session_state.selected_patient_id = patient_id
    st.session_state.page = 'patient_details'


def logout():
    st.session_state.doctor_id = None
    st.session_state.doctor_name = None
    st.session_state.page = 'login'


# Sidebar navigation
def show_sidebar():
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.doctor_name}")
        st.markdown("---")

        if st.button("📊 Dashboard", key="sidebar_dashboard", use_container_width=True):
            go_to_dashboard()

        # Fetch all patients for the dropdown
        patients = get_all_patients()
        patient_options = {p["id"]: f"{p['name']} ({p['email']})" for p in patients}

        if patient_options:
            st.markdown("### Quick Access")
            selected_patient = st.selectbox(
                "Select a patient",
                options=list(patient_options.keys()),
                format_func=lambda x: patient_options[x],
                key="patient_selector"
            )

            if st.button("View Patient", key="view_patient_button", use_container_width=True):
                go_to_patient_details(selected_patient)

        st.markdown("---")
        if st.button("Logout", key="sidebar_logout", use_container_width=True):
            logout()


# Dashboard Page
def show_dashboard():
    st.markdown("<h1 class='main-header'>Doctor Dashboard</h1>", unsafe_allow_html=True)

    # Get all patients
    patients = get_all_patients()

    # Create dataframe for all patients' assessments
    all_assessments = []
    for patient in patients:
        patient_assessments = get_patient_assessments(patient["id"]).get("assessments", [])
        for assessment in patient_assessments:
            assessment["patient_name"] = patient["name"]
        all_assessments.extend(patient_assessments)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Patient Overview")

        # Calculate statistics
        total_patients = len(patients)
        patients_with_assessments = len(set(a["patient_id"] for a in all_assessments))
        total_assessments = len(all_assessments)

        # Display metrics
        st.metric("Total Patients", total_patients)
        st.metric("Patients with Assessments", patients_with_assessments)
        st.metric("Total Assessments", total_assessments)

        # Severity distribution
        if all_assessments:
            level_counts = pd.DataFrame(all_assessments).groupby("level").size().reset_index()
            level_counts.columns = ["Anxiety Level", "Count"]

            fig = px.pie(
                level_counts,
                values="Count",
                names="Anxiety Level",
                title="Anxiety Level Distribution",
                color="Anxiety Level",
                color_discrete_map={
                    "Minimal Anxiety": "#00cc96",
                    "Mild Anxiety": "#ffa15a",
                    "Moderate Anxiety": "#ef553b",
                    "Severe Anxiety": "#ab63fa"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Patients List")

        # Filter options
        search_name = st.text_input("Search by name or email:")

        # Apply filters
        filtered_patients = patients
        if search_name:
            filtered_patients = [
                p for p in filtered_patients if
                search_name.lower() in p["name"].lower() or
                search_name.lower() in p["email"].lower()
            ]

        # Display patients in a table
        if not filtered_patients:
            st.info("No patients match your search criteria.")
        else:
            # Create a dataframe for display
            df = pd.DataFrame(filtered_patients)

            # Add a column for last assessment date and score
            df["last_assessment"] = None
            df["last_score"] = None
            df["anxiety_level"] = None

            for i, patient in df.iterrows():
                patient_assessments = get_patient_assessments(patient["id"]).get("assessments", [])
                if patient_assessments:
                    # Convert timestamps to datetime for proper sorting
                    for assessment in patient_assessments:
                        assessment["timestamp"] = pd.to_datetime(assessment["timestamp"])

                    # Sort by timestamp and get the latest
                    latest = sorted(patient_assessments, key=lambda x: x["timestamp"], reverse=True)[0]
                    df.at[i, "last_assessment"] = latest["timestamp"].strftime("%Y-%m-%d")
                    df.at[i, "last_score"] = latest["score"]
                    df.at[i, "anxiety_level"] = latest["level"]

            # Select columns for display
            display_df = df[["name", "email", "age", "gender", "last_assessment", "last_score", "anxiety_level"]]
            display_df.columns = ["Name", "Email", "Age", "Gender", "Last Assessment", "Score", "Anxiety Level"]

            # Apply color coding based on anxiety level
            def highlight_anxiety(val):
                if val == "Minimal Anxiety":
                    return "background-color: #d0f0c0"
                elif val == "Mild Anxiety":
                    return "background-color: #fffacd"
                elif val == "Moderate Anxiety":
                    return "background-color: #ffcccb"
                elif val == "Severe Anxiety":
                    return "background-color: #e6e6fa"
                return ""

            styled_df = display_df.style.applymap(highlight_anxiety, subset=["Anxiety Level"])

            st.dataframe(styled_df, use_container_width=True)

            # Button to view patient details
            selected_indices = st.multiselect(
                "Select patient to view details:",
                options=list(range(len(filtered_patients))),
                format_func=lambda i: filtered_patients[i]["name"]
            )

            if selected_indices and st.button("View Patient Details", use_container_width=True):
                go_to_patient_details(filtered_patients[selected_indices[0]]["id"])

        st.markdown("</div>", unsafe_allow_html=True)


# Patient Details Page
def show_patient_details():
    if not st.session_state.selected_patient_id:
        st.error("No patient selected.")
        return

    # Get patient information
    patient = get_patient(st.session_state.selected_patient_id)
    if not patient:
        st.error("Patient not found.")
        return

    # Get patient assessments
    assessment_data = get_patient_assessments(st.session_state.selected_patient_id)
    assessments = assessment_data.get("assessments", [])

    # Load questionnaire for reference
    if not st.session_state.questionnaire:
        st.session_state.questionnaire = get_questionnaire("bai")
    questionnaire = st.session_state.questionnaire

    st.markdown(f"<h1 class='main-header'>Patient: {patient['name']}</h1>", unsafe_allow_html=True)

    if st.button("← Back to Dashboard", use_container_width=False):
        go_to_dashboard()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Patient Information")

        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Email:** {patient['email']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Gender:** {patient['gender']}")

        st.markdown("</div>", unsafe_allow_html=True)

        if assessments:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Assessment Summary")

            # Get the latest assessment
            df_assessments = pd.DataFrame(assessments)
            df_assessments['timestamp'] = pd.to_datetime(df_assessments['timestamp'])
            latest_assessment = df_assessments.sort_values('timestamp', ascending=False).iloc[0]

            # Display latest score
            score = latest_assessment['score']
            level = latest_assessment['level']

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

            # Calculate statistics
            total_assessments = len(assessments)
            avg_score = df_assessments['score'].mean()
            max_score = df_assessments['score'].max()
            min_score = df_assessments['score'].min()

            st.metric("Total Assessments", total_assessments)
            st.metric("Average Score", f"{avg_score:.1f}")
            st.metric("Score Range", f"{min_score} - {max_score}")

            # Show trend (improving, worsening, stable)
            if len(assessments) > 1:
                sorted_assessments = df_assessments.sort_values('timestamp')
                first_score = sorted_assessments.iloc[0]['score']
                last_score = sorted_assessments.iloc[-1]['score']

                if last_score < first_score:
                    st.success("Trend: Improving ↓")
                elif last_score > first_score:
                    st.warning("Trend: Worsening ↑")
                else:
                    st.info("Trend: Stable →")

            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if not assessments:
            st.info("This patient has not taken any assessments yet.")
        else:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Assessment History")

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
                yaxis=dict(range=[0, 63]),  # Updated for BAI's 0-63 range
                hovermode="x unified"
            )
            # Add horizontal threshold lines for BAI scoring
            fig.add_hline(y=21, line_dash="dot", line_color="green", annotation_text="Minimal")
            fig.add_hline(y=26, line_dash="dot", line_color="orange", annotation_text="Mild")
            fig.add_hline(y=34, line_dash="dot", line_color="red", annotation_text="Moderate")
            # Above 34 is Severe

            st.plotly_chart(fig, use_container_width=True)

            # Show response patterns if there are multiple assessments
            if len(assessments) > 0 and questionnaire:
                st.subheader("Response Patterns")

                # Create a dataframe for question responses across all assessments
                question_responses = []

                for assessment in assessments:
                    answers = assessment.get("answers", {})
                    timestamp = pd.to_datetime(assessment["timestamp"])

                    for question_id, answer_value in answers.items():
                        question_text = next(
                            (q["text"] for q in questionnaire["questions"] if q["id"] == int(question_id)), "Unknown")
                        question_responses.append({
                            "timestamp": timestamp,
                            "question_id": question_id,
                            "question_text": question_text,
                            "answer_value": answer_value
                        })

                if question_responses:
                    # Convert to dataframe
                    df_responses = pd.DataFrame(question_responses)

                    # Create a heatmap of responses over time
                    pivot_df = df_responses.pivot_table(
                        index="question_text",
                        columns="timestamp",
                        values="answer_value",
                        aggfunc='mean'
                    )

                    # Create a heatmap
                    fig = go.Figure(data=go.Heatmap(
                        z=pivot_df.values,
                        x=pivot_df.columns.strftime('%Y-%m-%d'),
                        y=pivot_df.index,
                        colorscale='YlOrRd',
                        colorbar=dict(title='Score'),
                        hoverongaps=False
                    ))

                    fig.update_layout(
                        title='Response Patterns Over Time',
                        xaxis_title='Date',
                        yaxis_title='Question',
                        height=600  # Increased height for 21 questions instead of 7
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Show average scores per question
                    st.subheader("Average Scores by Question")
                    avg_scores = df_responses.groupby("question_text")["answer_value"].mean().sort_values(
                        ascending=False)

                    fig = px.bar(
                        x=avg_scores.index,
                        y=avg_scores.values,
                        labels={'x': 'Question', 'y': 'Average Score'},
                        title='Questions Ranked by Average Score'
                    )
                    fig.update_layout(xaxis_tickangle=-45, height=600)  # Increased height for more questions

                    st.plotly_chart(fig, use_container_width=True)

            # Show assessment details table
            st.subheader("Assessment Details")

            # Format the dataframe for display
            display_df = df[['timestamp', 'score', 'level']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            display_df.columns = ['Date', 'Score', 'Anxiety Level']
            display_df = display_df.sort_values('Date', ascending=False)

            st.dataframe(display_df, use_container_width=True)

            # Add export buttons
            export_col1, export_col2 = st.columns(2)
            with export_col1:
                if st.button("Export to Excel", use_container_width=True):
                    st.download_button(
                        label="Download Excel",
                        data=df.to_excel().encode('utf-8'),
                        file_name=f"{patient['name']}_anxiety_data.xlsx",
                        mime="application/vnd.ms-excel",
                        use_container_width=True
                    )

            with export_col2:
                if st.button("Export for Tableau", use_container_width=True):
                    st.download_button(
                        label="Download CSV",
                        data=df.to_csv().encode('utf-8'),
                        file_name=f"{patient['name']}_anxiety_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

            st.markdown("</div>", unsafe_allow_html=True)


# Login Page
def show_login_page():
    st.markdown("<h1 class='main-header'>Anxiety Assessment App</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-header'>Doctor Portal</h2>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Login")

    col1, col2 = st.columns(2)

    with col1:
        email = st.text_input("Email", value="doctor@example.com")

    with col2:
        password = st.text_input("Password", type="password", value="password")

    if st.button("Login", use_container_width=True):
        # In a real app, you would authenticate against a database
        # For this demo, we'll just set session state to a default doctor
        st.session_state.doctor_id = "doctor123"
        st.session_state.doctor_name = "Dr. Sarah Johnson"
        st.session_state.page = 'dashboard'
        st.experimental_rerun()

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

    if st.session_state.doctor_id:
        show_sidebar()

        if st.session_state.page == 'dashboard':
            show_dashboard()
        elif st.session_state.page == 'patient_details':
            show_patient_details()
    else:
        show_login_page()


if __name__ == "__main__":
    main()