
STUDENT PERFORMANCE ANALYSIS SYSTEM USING DATA SCIENCE

SUBMITTED BY: MOHAMMED HARIS RAHIM | BSCS-2Y-023A24P-1
SHEHROZ MALIK | BSCS-2Y-023R24P-20

SUPERVISED BY: FIZA ISHTIAQ


PROJECT OVERVIEW
This project is a web-based predictive analytics application designed to assist educational institutions in 
evaluating student academic trajectories. By leveraging the Random Forest machine learning algorithm, the system 
ingests historical and current academic metrics (such as attendance, assignment scores, & previous GPA) to 
forecast future student performance on a 4.0 GPA scale. The application features a robust MySQL relational 
database for secure user management, an intuitive Streamlit web interface for educators, & automated data 
preprocessing capabilities. Ultimately, the system enables proactive academic intervention by accurately 
identifying and classifying at-risk students before final assessments.


TOOLS, TECHNOLOGIES & SOFTWARE USED
- Programming Language: Python 3.9+
- Web Framework: Streamlit (for rapid, interactive dashboard deployment)
- Machine Learning Engine: Scikit-Learn (Random Forest Regressor)
- Relational Database: MySQL (managed via MySQL Workbench)
- Data Manipulation & Analysis: Pandas, NumPy
- Data Visualization: Matplotlib, Seaborn
- Model Serialization: Joblib
- Database Connectivity: mysql-connector-python


SYSTEM REQUIREMENTS & PREREQUISITES
- Operating System: Windows 10/11, macOS, or Linux.
- Python Environment: Python 3.9 or higher installed and added to system PATH.
- Database Server: MySQL Server and MySQL Workbench installed and running.
- Hardware: Minimum 4GB RAM (8GB recommended), 500MB free disk space.
- Network: Localhost environment (no external internet required post-install).


STEP-BY-STEP INSTALLATION & CONFIGURATION
1. Copy the entire 'Student_Performance_FYP' directory from this USB drive to a local directory on your machine 
   (e.g., C:\Projects\Student_Performance_FYP).
2. Open the Command Prompt (Windows) or Terminal (macOS/Linux).
3. Navigate to the project directory using the 'cd' command:   cd path\to\Student_Performance_FYP
4. Create a Python virtual environment to isolate project dependencies:   python -m venv venv
5. Activate the virtual environment:
   - Windows: venv\Scripts\activate
   - Linux: source venv/bin/activate
   (Note: Your terminal prompt should now be prefixed with '(venv)').


DATABASE SETUP & CONFIGURATION (MySQL Workbench)
The system utilizes a normalized MySQL database to manage credentials securely.
1. Launch MySQL Workbench/XAMPP & connect to your local MySQL server.
2. Navigate to File > Open SQL Script and select the 'Performance_Analysis_DB.sql' file located in this project 
directory.
3. Click the Execute button to run the script. This will:
   - Create the 'performance_analysis_db' database.
   - Generate the Admin, Teacher, Student, Academic_Record, and Prediction tables with all specified Primary & 
     Foreign Key constraints.
   - Insert a default administrative, teacher & student account for immediate testing. 
4. CREDENTIAL VERIFICATION: Open 'app.py' in a text editor and locate the get_db_connection() function 
   (approx. line 30). Ensure the 'user' & 'password' parameters match your local MySQL credentials. 
   (Default is user="root", password="root"). Modify these if your local setup utilizes different credentials.


STEP-BY-STEP INSTRUCTIONS FOR RUNNING THE PROJECT
1. Ensure that your MySQL Server is running in the background.
2. Ensure your Python virtual environment is activated in the terminal.
3. CRUCIAL VERIFICATION: Verify that the following machine learning artifacts are present in the project 
   directory. Without these, the predictive features will not function:
   - random_forest_model.joblib (The trained AI model)
   - model_features.joblib (The expected feature array)
4. Launch the Streamlit web application by executing:   streamlit run app.py
5. Your default web browser will automatically open the application at:   http://localhost:8501
6. Authenticate using the default credentials provisioned by the SQL script:
   - Role: Admin | Username: admin | Password: admin123
   - Role: Teacher | Username: teacher | Password: admin123
   - Role: Student | Username: student | Password: admin123
7. Navigate to 'Upload & Process Data' and upload the provided 'FYPDS1.csv' or 'FYPDS2.csv' to test the batch 
   processing capabilities.
8. Explore the 'Single Student Prediction', 'Batch Results', and 'Analytics & Insights' modules to evaluate 
   the system's predictive accuracy.

