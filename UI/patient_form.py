import streamlit as st

st.title("Welcome to MedScript")
# Streamlit application

st.markdown("<h1 style='font-size: 29px;'>Patient Information Submission Form</h1>", unsafe_allow_html=True)

st.markdown("""
Please fill out the form below with your details. Fields marked with an asterisk (*) are required.
""")

# Streamlit form
with st.form(key='patient_form'):
    # Basic Information
    st.header("Basic Information")
    gender = st.selectbox("Gender*", ["Select", "Male", "Female", "Other"])
    age = st.number_input("Age*", min_value=0, max_value=120, step=1)
    height = st.number_input("Height (cm)*", min_value=0.0, step=0.1, format="%.1f")
    weight = st.number_input("Weight (kg)*", min_value=0.0, step=0.1, format="%.1f")
    blood_type = st.selectbox("Blood Type*", ["Select", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])

    # Medical Details
    st.header("Medical Details")
    symptoms = st.text_area("Detailed Symptoms*", placeholder="Describe your symptoms in detail...")
    severity = st.slider("Severity*", min_value=1, max_value=10, step=1, help="Rate the severity of your symptoms on a scale of 1 to 10.")
    existing_conditions = st.text_area("Existing Medical Conditions", placeholder="List any pre-existing medical conditions...")
    allergies = st.text_area("Allergies", placeholder="List any allergies...")
    current_medications = st.text_area("Current Medications", placeholder="List any current medications...")

    # Previous Visits
    previous_visits = st.number_input("Number of Previous Visits*", min_value=0, step=1)

    # Form Submission
    submitted = st.form_submit_button("Submit")
    
    # Confirmation on submission
    if submitted:
        if gender == "Select" or blood_type == "Select":
            st.error("Please fill out all required fields correctly.")
        else:
            st.success("Form submitted successfully!")
            st.write("Here are the details you submitted:")
            st.json({
                "Gender": gender,
                "Age": age,
                "Height (cm)": height,
                "Weight (kg)": weight,
                "Blood Type": blood_type,
                "Symptoms": symptoms,
                "Severity": severity,
                "Existing Medical Conditions": existing_conditions,
                "Allergies": allergies,
                "Current Medications": current_medications,
                "Number of Previous Visits": previous_visits,
            })


st.markdown("---")
st.header("Diagnostic Report")

# Button to view diagnostic report
if st.button("View Diagnostic Report"):
    st.write("Diagnostic report is not yet available. Please contact your healthcare provider.")

st.subheader("Diagnosis")
primary_diagnosis = st.text_area("Primary Diagnosis", placeholder="Enter the primary diagnosis...", height=150)
differential_diagnosis = st.text_area("Differential Diagnosis", placeholder="Enter the differential diagnosis...", height=150)