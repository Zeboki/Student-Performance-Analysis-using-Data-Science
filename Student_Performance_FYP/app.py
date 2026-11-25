import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import mysql.connector
import hashlib
import os
import time
from sklearn.preprocessing import LabelEncoder


st.set_page_config(page_title="Student Performance Analyzer", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1998rhgwars1998",  # Update if SQL password is different
        database="performance_analysis_db"
    )

def execute_query(query, params=None, fetch=False):
    """Universal helper to execute SQL queries safely with proper connection handling."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
            
        return result
        
    except mysql.connector.Error as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return e
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login(username, password, role):
    """Verifies credentials based on the selected role using the updated schema."""
    # Demo accounts
    if role == "Admin" and username == "admin" and password == "admin123":
        return {"id": 1, "username": "admin", "role": "Admin"}
    if role == "Teacher" and username == "teacher" and password == "admin123":
        return {"id": 1, "username": "teacher", "role": "Teacher", "teacher_id": 1}
    if role == "Student" and username == "student" and password == "admin123":
        return {"id": 1, "username": "student", "role": "Student", "student_id": 1}

    try:
        hashed_pw = hash_password(password)
        if role == "Teacher":
            query = "SELECT * FROM Teacher WHERE Teacher_Name=%s AND Teacher_PW=%s"
        elif role == "Student":
            query = "SELECT * FROM Student WHERE Student_Name=%s AND Student_PW=%s"
        else:
            return None
            
        user = execute_query(query, (username, hashed_pw), fetch=True)
        if user and not isinstance(user, Exception):
            user = user[0]
            user['role'] = role
            if role == 'Teacher':
                user['username'] = user.get('Teacher_Name')
                user['teacher_id'] = user.get('Teacher_ID')
            elif role == 'Student':
                user['username'] = user.get('Student_Name')
                user['student_id'] = user.get('Student_ID')
            return user
        return None
    except Exception:
        return None

@st.cache_resource
def load_model():
    model_path = 'random_forest_model.joblib'
    features_path = 'model_features.joblib'
    if not os.path.exists(model_path) or not os.path.exists(features_path):
        return None, None, 0.0
    try:
        model = joblib.load(model_path)
        features = joblib.load(features_path)
        file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
        return model, features, file_size_mb
    except Exception:
        return None, None, 0.0

def get_risk_level(gpa_score):
    if gpa_score < 2.0: return "🔴 High Risk"
    elif gpa_score < 3.0: return "🟡 Medium Risk"
    else: return "🟢 Low Risk"


# SESSION STATE INITIALIZATION
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'student_id' not in st.session_state:
    st.session_state.student_id = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'original_data' not in st.session_state:
    st.session_state.original_data = None


# LANDING PAGE & LOGIN
if not st.session_state.logged_in:
    st.title("🎓 Student Performance Analysis System")
    st.markdown("### Secure Portal Login")
    
    selected_role = st.selectbox("Select your login role:", ["Teacher", "Admin", "Student"])
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            user = check_login(username, password, selected_role)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user['username']
                st.session_state.role = user['role']
                st.session_state.user_id = user.get('id') or user.get('teacher_id') or user.get('student_id')
                if 'student_id' in user:
                    st.session_state.student_id = user['student_id']
                st.rerun()
            else:
                st.error(f"Invalid credentials for {selected_role}.")

# MAIN DASHBOARD ROUTING
else:
    st.sidebar.title(f"🏫 {st.session_state.role} Portal")
    st.sidebar.write(f"Welcome, **{st.session_state.username}**")
    st.sidebar.success("Status: System Online & Connected to MySQL")
    
    model, expected_features, model_size_mb = load_model()

    st.sidebar.markdown("---")
    

# ADMIN DASHBOARD
    if st.session_state.role == "Admin":
        menu = st.sidebar.radio("Navigation", ["📊 System Overview", "👥 User Management", "🚪 Logout"])
        
        # SYSTEM OVERVIEW
        if menu == "📊 System Overview":
            st.header("📊 System Overview")
            st.write("High-level statistics of the educational institution and AI usage.")
            
            try:
                total_students = execute_query("SELECT COUNT(*) as count FROM Student", fetch=True)[0]['count']
                total_teachers = execute_query("SELECT COUNT(*) as count FROM Teacher", fetch=True)[0]['count']
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Students", total_students)
                c2.metric("Total Teachers", total_teachers)

            except Exception as e:
                st.error(f"Database error fetching metrics: {e}")
                
            st.subheader("👥 Current User Roster")
            tab_roster_teachers, tab_roster_students = st.tabs(["Teachers", "Students"])
            
            with tab_roster_teachers:
                teachers = execute_query("SELECT Teacher_ID, Teacher_Name FROM Teacher", fetch=True)
                if not isinstance(teachers, Exception):
                    st.dataframe(pd.DataFrame(teachers), use_container_width=True, height=250)
                else:
                    st.error(f"DB Error: {teachers}")
                    
            with tab_roster_students:
                students = execute_query("SELECT Student_ID, Student_Name FROM Student", fetch=True)
                if not isinstance(students, Exception):
                    st.dataframe(pd.DataFrame(students), use_container_width=True, height=250)
                else:
                    st.error(f"DB Error: {students}")


        # USER MANAGEMENT 
        elif menu == "👥 User Management":
            st.header("👥 User Management")
            st.write("Create, update, or delete Teacher and Student accounts.")
            
            tab_teachers, tab_students = st.tabs(["👨‍🏫 Manage Teachers", "🎓 Manage Students"])
            
            # TEACHERS CRUD
            with tab_teachers:
                teachers = execute_query("SELECT Teacher_ID, Teacher_Name FROM Teacher", fetch=True)
                action = st.radio("Select Action", ["Add New Teacher", "Edit Existing Teacher", "Delete Teacher"], horizontal=True, key="t_action")
                
                if action == "Add New Teacher":
                    with st.form("add_t_form"):
                        u = st.text_input("Teacher Name (Username)")
                        p = st.text_input("Password", type="password")
                        if st.form_submit_button("Add Teacher"):
                            if not u or not p: st.error("Name and Password are required.")
                            else:
                                res = execute_query("INSERT INTO Teacher (Admin_ID, Teacher_Name, Teacher_PW) VALUES (1, %s, %s)", (u, hash_password(p)))
                                if isinstance(res, Exception):
                                    st.error("Error: Name already exists!" if "Duplicate" in str(res) else f"Error: {res}")
                                else:
                                    st.success(f"Teacher '{u}' added successfully!")
                                    st.rerun()
                                    
                elif action == "Edit Existing Teacher":
                    if not teachers: st.warning("No teachers available to edit.")
                    else:
                        t_map = {f"{t['Teacher_Name']} (ID: {t['Teacher_ID']})": t['Teacher_ID'] for t in teachers}
                        selected = st.selectbox("Select Teacher", list(t_map.keys()), key="edit_t_sel")
                        sel_id = t_map[selected]
                        details = execute_query("SELECT * FROM Teacher WHERE Teacher_ID = %s", (sel_id,), fetch=True)[0]
                        
                        with st.form("edit_t_form"):
                            u = st.text_input("Teacher Name", value=details['Teacher_Name'])
                            p = st.text_input("Password (leave blank to keep current)", type="password")
                            if st.form_submit_button("Update Teacher"):
                                if not p:
                                    res = execute_query("UPDATE Teacher SET Teacher_Name=%s WHERE Teacher_ID=%s", (u, sel_id))
                                else:
                                    res = execute_query("UPDATE Teacher SET Teacher_Name=%s, Teacher_PW=%s WHERE Teacher_ID=%s", (u, hash_password(p), sel_id))
                                
                                if isinstance(res, Exception):
                                    st.error("Error: Name already exists!" if "Duplicate" in str(res) else f"Error: {res}")
                                else:
                                    st.success("Teacher updated successfully!")
                                    st.rerun()
                                    
                elif action == "Delete Teacher":
                    if not teachers: st.warning("No teachers available to delete.")
                    else:
                        t_map = {f"{t['Teacher_Name']} (ID: {t['Teacher_ID']})": t['Teacher_ID'] for t in teachers}
                        selected = st.selectbox("Select Teacher to Delete", list(t_map.keys()), key="del_t_sel")
                        sel_id = t_map[selected]
                        if st.button("⚠️ Confirm Delete", type="primary"):
                            res = execute_query("DELETE FROM Teacher WHERE Teacher_ID = %s", (sel_id,))
                            if isinstance(res, Exception): st.error(f"Error: {res}")
                            else:
                                st.success("Teacher deleted successfully!")
                                st.rerun()

            # STUDENTS CRUD
            with tab_students:
                students = execute_query("SELECT Student_ID, Student_Name FROM Student", fetch=True)
                action = st.radio("Select Action", ["Add New Student", "Edit Existing Student", "Delete Student"], horizontal=True, key="s_action")
                
                if action == "Add New Student":
                    with st.form("add_s_form"):
                        u = st.text_input("Student Name (Username)")
                        p = st.text_input("Password", type="password")
                        if st.form_submit_button("Add Student"):
                            if not u or not p: st.error("Name and Password are required.")
                            else:
                                res = execute_query("INSERT INTO Student (Admin_ID, Student_Name, Student_PW) VALUES (1, %s, %s)", (u, hash_password(p)))
                                if isinstance(res, Exception):
                                    st.error("Error: Duplicate entry!" if "Duplicate" in str(res) else f"Error: {res}")
                                else:
                                    st.success(f"Student '{u}' added successfully!")
                                    st.rerun()
                                    
                elif action == "Edit Existing Student":
                    if not students: st.warning("No students available to edit.")
                    else:
                        s_map = {f"{s['Student_Name']} (ID: {s['Student_ID']})": s['Student_ID'] for s in students}
                        selected = st.selectbox("Select Student", list(s_map.keys()), key="edit_s_sel")
                        sel_id = s_map[selected]
                        details = execute_query("SELECT * FROM Student WHERE Student_ID = %s", (sel_id,), fetch=True)[0]
                        
                        with st.form("edit_s_form"):
                            u = st.text_input("Student Name", value=details['Student_Name'] or "")
                            p = st.text_input("Password (leave blank to keep current)", type="password")
                            if st.form_submit_button("Update Student"):
                                if not p:
                                    res = execute_query("UPDATE Student SET Student_Name=%s WHERE Student_ID=%s", (u, sel_id))
                                else:
                                    res = execute_query("UPDATE Student SET Student_Name=%s, Student_PW=%s WHERE Student_ID=%s", (u, hash_password(p), sel_id))
                                
                                if isinstance(res, Exception):
                                    st.error("Error: Duplicate entry!" if "Duplicate" in str(res) else f"Error: {res}")
                                else:
                                    st.success("Student updated successfully!")
                                    st.rerun()
                                    
                elif action == "Delete Student":
                    if not students: st.warning("No students available to delete.")
                    else:
                        s_map = {f"{s['Student_Name']} (ID: {s['Student_ID']})": s['Student_ID'] for s in students}
                        selected = st.selectbox("Select Student to Delete", list(s_map.keys()), key="del_s_sel")
                        sel_id = s_map[selected]
                        if st.button("⚠️ Confirm Delete", type="primary"):
                            res = execute_query("DELETE FROM Student WHERE Student_ID = %s", (sel_id,))
                            if isinstance(res, Exception): st.error(f"Error: {res}")
                            else:
                                st.success("Student deleted successfully!")
                                st.rerun()


    # STUDENT DASHBOARD
    elif st.session_state.role == "Student":
        menu = st.sidebar.radio("Navigation", ["🎯 My Academic Profile", "🚪 Logout"])
        
        if menu == "🎯 My Academic Profile":
            st.header("🎯 My Academic Profile")
            st.write(f"Welcome, Student ID: **{st.session_state.get('student_id', 'N/A')}**. Enter your current metrics to predict your upcoming GPA.")
            if model is None: st.error("⚠️ AI Model offline.")
            else:
                col1, col2, col3 = st.columns(3)
                with col1: att = st.slider("My Attendance Status (%)", 0.0, 100.0, 75.0)
                with col2: assign = st.slider("My Assignment Scores (out of 12)", 0.0, 12.0, 8.0, 0.5)
                with col3: prev_gpa = st.slider("My Previous GPA (out of 4.0)", 0.0, 4.0, 2.8, 0.1)
                if st.button("🔮 Calculate My Predicted GPA", use_container_width=True, type="primary"):
                    with st.spinner("Consulting AI Model..."):
                        time.sleep(1) 
                        input_data = {'Attendance_Status': [att], 'Assignment_Scores': [assign], 'Previous_GPA': [prev_gpa]}
                        input_df = pd.DataFrame(input_data)
                        for col in expected_features:
                            if col not in input_df.columns: input_df[col] = 0
                        input_df = input_df[expected_features]
                        predicted_gpa = round(min(max(model.predict(input_df)[0], 0.0), 4.0), 2)
                        st.markdown("### 🎯 My Prediction")
                        st.metric("My Predicted GPA", f"{predicted_gpa:.2f} / 4.0")
                        if predicted_gpa < 2.0: st.error("⚠️ **Alert:** You are currently at high risk. Please consult your academic advisor immediately.")
                        elif predicted_gpa < 3.0: st.warning("⚠️ **Note:** You are performing below average. Consider attending extra tutoring sessions.")
                        else: st.success("✅ **Status:** Excellent! You are on track for academic success.")



    # TEACHER DASHBOARD
    else:
        menu = st.sidebar.radio("Navigation", [
            "📤 Upload & Process Data", "🎯 Single Student Prediction", 
            "📊 Batch Results", "📈 Analytics & Insights", "🚪 Logout"
        ])

        if menu == "📤 Upload & Process Data":
            st.header("📤 Upload Student Dataset")
            st.write("Upload a CSV file. The system will automatically clean the data and prepare it for the AI model.")
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                try:
                    df_original = pd.read_csv(uploaded_file)
                    df_original = df_original.loc[:, ~df_original.columns.str.contains('^Unnamed', case=False, na=False)]
                    for col in df_original.columns:
                        if df_original[col].dtype == 'object':
                            df_original[col] = df_original[col].astype(str).str.replace('%', '', regex=False)
                            df_original[col] = pd.to_numeric(df_original[col], errors='coerce')
                    df_original = df_original.fillna(df_original.median(numeric_only=True))
                    st.session_state.original_data = df_original
                    st.session_state.processed_data = df_original
                    st.success("✅ Data processed and cleaned successfully!")
                    st.dataframe(df_original.head(50), use_container_width=True, height=400)
                except Exception as e:
                    st.error(f"Error processing file: {e}")


        elif menu == "🎯 Single Student Prediction":
            st.header("🎯 Single Student Prediction")

            if model is None:
                st.error("⚠️ Model files not found.")
            else:
                tab_search, tab_add = st.tabs(["🔍 Search Existing Student", "➕ Add New Student Record"])
                
                with tab_search:
                    if st.session_state.processed_data is None:
                        st.warning("Please upload a student dataset first from 'Upload & Process Data' to search for existing students.")
                    else:
                        df_clean = st.session_state.processed_data.copy()
                        if "Student_ID" not in df_clean.columns:
                            st.error("Student_ID column not found in the uploaded dataset.")
                        else:
                            st.write("Search for a student by Student ID to retrieve their academic metrics and predict their GPA.")
                            with st.form("student_search_form"):
                                student_id_input = st.text_input("🔍 Search Student ID", placeholder="Enter Student ID").strip()
                                search_clicked = st.form_submit_button("Search Student", use_container_width=True)
                                
                            if search_clicked:
                                if not student_id_input:
                                    st.session_state.pop("selected_student_record", None)
                                    st.error("Please enter a Student ID.")
                                else:
                                    id_values = df_clean["Student_ID"].astype("string").str.strip()
                                    matches = df_clean[id_values == student_id_input]
                                    if matches.empty:
                                        st.session_state.pop("selected_student_record", None)
                                        st.error(f"No student found with ID {student_id_input} in the uploaded dataset.")
                                    elif len(matches) > 1:
                                        st.session_state.pop("selected_student_record", None)
                                        st.error("Multiple records found for this Student ID.")
                                    else:
                                        st.session_state["selected_student_record"] = matches.iloc[0].to_dict()
                                        
                            student_record = st.session_state.get("selected_student_record")
                            if student_record is not None:
                                st.markdown("---")
                                st.subheader("👤 Student Details")
                                st.write(f"**Student ID:** {student_record['Student_ID']}")
                                display_fields = ["Attendance_Status", "Assignment_Scores", "Previous_GPA"]
                                available_fields = [col for col in display_fields if col in student_record]
                                if available_fields:
                                    detail_cols = st.columns(len(available_fields))
                                    for i, col in enumerate(available_fields):
                                        value = student_record[col]
                                        detail_cols[i].metric(col.replace("_", " "), "N/A" if pd.isna(value) else str(value))
                                        
                                try:
                                    with st.spinner("Processing via Random Forest Model..."):
                                        time.sleep(0.5)
                                        input_df = pd.DataFrame([student_record])
                                        missing_features = [col for col in expected_features if col not in input_df.columns]
                                        if missing_features:
                                            st.error("Missing required model features: " + ", ".join(missing_features))
                                        else:
                                            input_df = input_df[expected_features].copy()
                                            for col in input_df.columns:
                                                if input_df[col].dtype == "object" or pd.api.types.is_string_dtype(input_df[col]):
                                                    input_df[col] = input_df[col].astype("string").str.replace("%", "", regex=False)
                                                    input_df[col] = pd.to_numeric(input_df[col], errors="coerce")
                                            if input_df.isna().any().any():
                                                bad_cols = input_df.columns[input_df.isna().any()].tolist()
                                                st.error("Some model features are missing or non-numeric: " + ", ".join(bad_cols))
                                            else:
                                                predicted_gpa = round(min(max(float(model.predict(input_df)[0]), 0.0), 4.0), 2)
                                                risk = get_risk_level(predicted_gpa)
                                                st.markdown("### 🎯 Prediction Results")
                                                m1, m2 = st.columns(2)
                                                m1.metric("Predicted GPA", f"{predicted_gpa:.2f} / 4.0")
                                                m2.metric("Risk Level", risk)
                                                if predicted_gpa < 2.0: st.error("⚠️ High risk of academic failure.")
                                                elif predicted_gpa < 3.0: st.warning("⚠️ The student may benefit from additional academic support.")
                                                else: st.success("✅ The student is performing well.")
                                except Exception as e:
                                    st.error(f"Prediction failed: {e}")


                # ADD NEW STUDENT RECORD
                with tab_add:
                    st.write("Enter the details of a new student record. Predict their GPA first, then save the record and prediction to the database.")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_student_id = st.number_input("Student ID", min_value=1, step=1, value=1001, key="new_sid")
                        new_att = st.number_input("Attendance Status (%)", min_value=0.0, max_value=100.0, value=75.0, step=0.1, key="new_att")
                    with col2:
                        new_assign = st.number_input("Assignment Scores (out of 12)", min_value=0.0, max_value=12.0, value=8.0, step=0.5, key="new_assign")
                        new_prev_gpa = st.number_input("Previous GPA (out of 4.0)", min_value=0.0, max_value=4.0, value=2.8, step=0.1, key="new_gpa")
                        
                    if st.button("Predict Performance", use_container_width=True, type="primary"):
                        with st.spinner("Consulting Random Forest Model..."):
                            input_data = {
                                'Attendance_Status': [new_att],
                                'Assignment_Scores': [new_assign],
                                'Previous_GPA': [new_prev_gpa]
                            }
                            input_df = pd.DataFrame(input_data)
                            for col in expected_features:
                                if col not in input_df.columns:
                                    input_df[col] = 0
                            input_df = input_df[expected_features]
                            
                            predicted_gpa = round(min(max(float(model.predict(input_df)[0]), 0.0), 4.0), 2)
                            risk = get_risk_level(predicted_gpa)
                            
                            # Store prediction in session state
                            st.session_state['pending_new_record'] = {
                                'student_id': new_student_id,
                                'att': new_att,
                                'assign': new_assign,
                                'prev_gpa': new_prev_gpa,
                                'predicted_gpa': predicted_gpa,
                                'risk': risk
                            }
                            
                    if 'pending_new_record' in st.session_state:
                        pred = st.session_state['pending_new_record']
                        
                        st.markdown("---")
                        st.markdown("### 🎯 Prediction Results")
                        m1, m2 = st.columns(2)
                        m1.metric("Predicted GPA", f"{pred['predicted_gpa']:.2f} / 4.0")
                        m2.metric("Risk Level", pred['risk'])
                        
                        if pred['predicted_gpa'] < 2.0:
                            st.error("⚠️ High risk of academic failure. Consider academic support and intervention.")
                        elif pred['predicted_gpa'] < 3.0:
                            st.warning("⚠️ The student may benefit from additional academic support.")
                        else:
                            st.success("✅ The student is performing well.")
                            
                        # Save Button
                        if st.button("💾 Save Record & Prediction", use_container_width=True):
                            with st.spinner("Saving & updating records..."):
                                
                                
                                admin_res = execute_query("SELECT Admin_ID FROM Admin LIMIT 1", fetch=True)
                                if isinstance(admin_res, Exception) or not admin_res:
                                    st.error("❌ No Admin found in the database. Please ensure the database is initialized.")
                                else:
                                    valid_admin_id = admin_res[0]['Admin_ID']
                                    
                                    student_check = execute_query("SELECT Student_ID FROM Student WHERE Student_ID = %s", (pred['student_id'],), fetch=True)
                                    
                                    if isinstance(student_check, Exception):
                                        st.error(f"❌ Database error checking student: {student_check}")
                                    elif not student_check:
                                        res_create = execute_query(
                                            "INSERT INTO Student (Admin_ID, Student_ID, Student_Name, Student_PW) VALUES (%s, %s, %s, %s)", 
                                            (valid_admin_id, pred['student_id'], f"Student_{pred['student_id']}", hash_password("default123"))
                                        )
                                        if isinstance(res_create, Exception):
                                            st.error(f"❌ Failed to create student profile: {res_create}")
                                            st.stop() 
                                    
                                    res_record = execute_query(
                                        "INSERT INTO Academic_Record (student_id, attendance_status, assignment_scores, previous_gpa) VALUES (%s, %s, %s, %s)",
                                        (pred['student_id'], pred['att'], pred['assign'], pred['prev_gpa'])
                                    )
                                    
                                    if isinstance(res_record, Exception):
                                        st.error(f"❌ Failed to save academic record: {res_record}")
                                    else:
                                        record_id_res = execute_query(
                                            "SELECT record_id FROM Academic_Record WHERE student_id = %s ORDER BY record_id DESC LIMIT 1", 
                                            (pred['student_id'],), 
                                            fetch=True
                                        )
                                        
                                        if not isinstance(record_id_res, Exception) and record_id_res:
                                            record_id = record_id_res[0]['record_id']
                                            teacher_id = st.session_state.get('user_id') or 1
                                            
                                            res_pred = execute_query(
                                                "INSERT INTO Prediction (teacher_id, record_id, predicted_score, risk_level) VALUES (%s, %s, %s, %s)",
                                                (teacher_id, record_id, pred['predicted_gpa'], pred['risk'])
                                            )
                                            
                                            if isinstance(res_pred, Exception):
                                                st.error(f"❌ Failed to save prediction: {res_pred}")
                                            else:
                                                new_row_data = {
                                                    'Student_ID': pred['student_id'],
                                                    'Attendance_Status': pred['att'],
                                                    'Assignment_Scores': pred['assign'],
                                                    'Previous_GPA': pred['prev_gpa']
                                                }
                                                
                                                if st.session_state.processed_data is not None:
                                                    new_row_df = pd.DataFrame([new_row_data])
                                                    st.session_state.processed_data = pd.concat([st.session_state.processed_data, new_row_df], ignore_index=True)
                                                    
                                                if st.session_state.original_data is not None:
                                                    new_row_df_orig = pd.DataFrame([new_row_data])
                                                    st.session_state.original_data = pd.concat([st.session_state.original_data, new_row_df_orig], ignore_index=True)

                                                st.success("✅ Record and prediction saved!")
                                                st.session_state.pop('pending_new_record', None)
                                                

                                                st.success("✅ Record and prediction saved.")
                                                
                                                st.rerun()                                                


        elif menu == "📊 Batch Results":
            st.header("📊 Batch Prediction Results")
            if model is None: st.error("⚠️ Model files not found!")
            elif st.session_state.processed_data is None: st.warning("Please upload a dataset first.")
            else:
                df_clean = st.session_state.processed_data
                input_features = [col for col in expected_features if col in df_clean.columns]
                X_predict = df_clean[input_features]
                predictions = model.predict(X_predict)
                results_df = df_clean.copy()
                results_df['Predicted_GPA_AI'] = np.round(predictions, 2)
                results_df['Risk_Level'] = results_df['Predicted_GPA_AI'].apply(get_risk_level)
                high_risk = len(results_df[results_df['Risk_Level'].str.contains('High')])
                med_risk = len(results_df[results_df['Risk_Level'].str.contains('Medium')])
                avg_gpa = results_df['Predicted_GPA_AI'].mean()
                c1, c2, c3 = st.columns(3)
                c1.metric("Average Predicted GPA", f"{avg_gpa:.2f} / 4.0")
                c2.metric("High Risk Students", f"🔴 {high_risk}")
                c3.metric("Medium Risk Students", f"🟡 {med_risk}")
                st.dataframe(results_df, use_container_width=True, height=500)
                csv = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Download Full Report (CSV)", data=csv, file_name='batch_predictions.csv', mime='text/csv')

        elif menu == "📈 Analytics & Insights":
            st.header("📈 Analytics & Insights")
            if model is None: st.error("⚠️ Model files not found!")
            elif st.session_state.processed_data is None: st.warning("Please upload data first.")
            else:
                df_clean = st.session_state.processed_data
                ignore_cols = ['Record_ID', 'Student_ID']
                tab1, tab2, tab3 = st.tabs(["📊 Feature Importance", "🔥 Correlation Heatmap", "🥧 Risk Distribution"])
                
                with tab1:
                    importances = model.feature_importances_
                    feature_df = pd.DataFrame({'Feature': expected_features, 'Importance': importances})
                    feature_df = feature_df[~feature_df['Feature'].isin(ignore_cols)].sort_values(by='Importance', ascending=True)
                    
                    fig1, ax1 = plt.subplots(figsize=(6, 4)) 
                    ax1.barh(feature_df['Feature'], feature_df['Importance'], color='skyblue')
                    ax1.set_title('Random Forest Feature Importance')
                    ax1.set_xlabel('Importance Weight')
                    fig1.tight_layout() 
                    st.pyplot(fig1, use_container_width=True)
                    
                with tab2:
                    numeric_df = df_clean.select_dtypes(include=[np.number]).drop(columns=ignore_cols, errors='ignore')
                    if 'Predicted_GPA' in numeric_df.columns: numeric_df = numeric_df.drop(columns=['Predicted_GPA'])
                    
                    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
                    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax2, vmin=-1, vmax=1)
                    ax2.set_title('Feature Correlation Matrix')
                    st.pyplot(fig2, use_container_width=True)
                    
                with tab3:
                    input_features = [col for col in expected_features if col in df_clean.columns]
                    temp_preds = model.predict(df_clean[input_features])
                    temp_df = df_clean.copy()
                    temp_df['Risk_Level'] = pd.Series(temp_preds).apply(get_risk_level)
                    risk_counts = temp_df['Risk_Level'].value_counts()
                    clean_labels = [label.split(' ')[1] if ' ' in label else label for label in risk_counts.index]
                    col_left, col_mid, col_right = st.columns([1, 2, 1])
                    with col_mid:
                        fig3, ax3 = plt.subplots(figsize=(5, 5)) 
                        ax3.pie(risk_counts, labels=clean_labels, autopct='%1.1f%%', colors=['#99ff99', '#ffcc99', '#ff9999'], startangle=90)
                        ax3.set_title('Class Risk Distribution')
                        st.pyplot(fig3) 
                    
    # LOGOUT HANDLER
    if 'menu' in locals() and menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = ""
        st.session_state.user_id = None
        st.session_state.student_id = None
        st.session_state.processed_data = None
        st.session_state.original_data = None
        st.rerun()