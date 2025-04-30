import streamlit as st
import subprocess
import sys
import os
import threading
import time


def setup_environment():
    """Install required packages if they're not already installed"""
    required_packages = [
        "streamlit",
        "fastapi",
        "uvicorn",
        "pandas",
        "plotly",
        "requests",
        "openpyxl",
    ]

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")


def start_backend():
    """Start the FastAPI backend server"""
    print("Starting FastAPI backend server...")
    # Run the FastAPI backend in a separate process
    os.environ["PYTHONUNBUFFERED"] = "1"  # Ensure output is not buffered
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Log the backend output
    while True:
        line = backend_process.stdout.readline()
        if not line:
            break
        print(f"[Backend] {line.strip()}")

    backend_process.wait()
    print("Backend server stopped")


def main():
    """Main application launcher"""
    st.title("Anxiety Assessment Application")
    st.write("Welcome to the Anxiety Assessment Application")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Launch Patient Interface", use_container_width=True):
            # Launch the patient interface in a new browser tab
            command = f"{sys.executable} -m streamlit run patient_app.py"
            subprocess.Popen(command, shell=True)
            st.success("Patient interface launched! Check your browser for a new tab.")

    with col2:
        if st.button("Launch Doctor Interface", use_container_width=True):
            # Launch the doctor interface in a new browser tab
            command = f"{sys.executable} -m streamlit run doctor_app.py"
            subprocess.Popen(command, shell=True)
            st.success("Doctor interface launched! Check your browser for a new tab.")

    st.divider()

    # Backend server status
    st.subheader("Backend Server Status")
    if st.button("Start Backend Server"):
        st.session_state.backend_running = True
        st.info("Starting backend server... This may take a moment.")

        # Start the backend server in a separate thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()

        # Give the server a moment to start
        time.sleep(2)
        st.success("Backend server started successfully!")
        st.markdown("API available at: http://localhost:8000")
        st.markdown("API documentation available at: http://localhost:8000/docs")

    # Display environment info
    st.divider()
    st.subheader("Environment Information")
    st.code(f"Python version: {sys.version}")
    st.code(f"Working directory: {os.getcwd()}")


if __name__ == "__main__":
    # Initialize session state
    if 'backend_running' not in st.session_state:
        st.session_state.backend_running = False

    # Setup environment first
    setup_environment()

    # Run the main application
    main()