# UI/home.py

import streamlit as st
import pages.patient_form as patient_form
<<<<<<< HEAD
from PIL import Image
import base64
=======
>>>>>>> 2138f6a9a877100f42001d4731693e4f4edd8ea4

# Set page configuration
st.set_page_config(
    page_title="Medscript-AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
<<<<<<< HEAD
# Change the background color
st.markdown(
    """
    <style>
        /* Set the background color */
        .stApp {
            background-color: #f4f4f4; /* Light grey */
        }

        /* Optional: Customize the text color */
        div, h1, h2, h3, h4, h5, h6, p {
            color: #333333; /* Dark grey */
        }

        .main > div {
            padding-left: 0rem;    
        }

=======

st.markdown(
    """
    <style>
>>>>>>> 2138f6a9a877100f42001d4731693e4f4edd8ea4
        body {
            font-family: Arial, sans-serif;
            background-color: #0d1117;
            color: #ffffff;
            margin: 0;
            padding: 0;
            height: 100vh;
            background-image: url('https://your-image-url.com');
            background-size: cover;
            background-position: center;
        }

        /* Container for centering the text */
        .container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            width: 65%;
            margin: 0 auto;
            padding: 20px;
        }

        h2 {
            clear: left;
        }

        .header {
            text-align: center;
            padding: 100px 0;
            background-color: #161b22;
        }

        .header h1 {
            font-size: 3rem;
            color: #f5a623;
        }


        .header p {
            font-size: 1.2rem;
            margin-top: 10px;
            color: #b0b3b8;
        }

        .patient-form-button {
            background-color: #f5a623;
            color: #161b22;
            border: none;
            padding: 15px 30px;
            font-size: 1.2rem;
            cursor: pointer;
            border-radius: 5px;
            margin-top: 20px;
        }

        .offers {
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 50px;
            background-color: #161b22;
        }
        
        .features-grid-container {
            display: grid;
            gap: 20px;
            grid-template-columns: auto auto auto;
            min-height: 0;
            padding: 10px;
        }

        .features-grid-item {
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid #ddd;
            padding: 20px;
            text-align: center;
            min-height: 0;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)

<<<<<<< HEAD
# Hero Section
st.markdown("""
    <div class="header">
        <h1>Medscript-AI</h1>
        <p>Revolutionizing Healthcare with AI-Driven Diagnosis</p>
    </div>
""", unsafe_allow_html=True)

# Overview Section
st.markdown("""
    <div class="container">
        <h1>What is MedScript AI?</h1>
        <p>
            <strong>MedScript AI</strong> is an innovative healthcare application that combines cutting-edge artificial intelligence
            with medical expertise. It takes in patient details, their current symptoms, and previous diagnoses to
            generate comprehensive diagnosis reports. These reports help doctors make quick and informed treatment decisions.
        </p>
    </div>
""", unsafe_allow_html=True)

# st.image(logo, caption="MedScript AI Logo", use_column_width=True)

# Key Features Section

# Convert Microchip image to base64
with open("UI/images/microchip.png", "rb") as f:
    contents = f.read()
    microchip_img = base64.b64encode(contents).decode("utf-8")

# Convert medical checkup image to base 64
with open("UI/images/medical-checkup.png", "rb") as f:
    contents = f.read()
    medical_report_img = base64.b64encode(contents).decode("utf-8")

# Convert decision making image to base 64
with open("UI/images/decision-making.png", "rb") as f:
    contents = f.read()
    decision_making_img = base64.b64encode(contents).decode("utf-8")

st.markdown(f"""
    <div class="container">
        <h1>Key Features</h1>
        <div class ="features-grid-container">
            <div class = "features-grid-item">
                <img src="data:image/png;base64,{microchip_img}" alt="microchip img" ,width="60px", height="60px">
                <br/>
                <strong>AI-powered Diagnosis</strong>
                <p>Generates diagnosis reports based on patient details and symptoms.</p>
            </div>
            <div class = "features-grid-item">
                <img src="data:image/png;base64,{medical_report_img}" alt="medical report img", width="56px", height="50px">
                <br/>
                <strong>Comprehensive Reports</strong>
                <p>Provides detailed reports to help doctors make informed decisions.</p>
            </div>
            <div class = "features-grid-item">
                <img src="data:image/png;base64,{decision_making_img}" alt="decision making img", width="60px", height="60px">
                <br/>
                <strong>Quick Treatment Decisions</strong>
                <p>Enables faster decision-making for doctors with AI-driven insights.</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)


# st.markdown("---")

# Benefits Section
st.markdown(f"""
    <div class= "container" style="text-align: left;">
        <h1>Why Choose MedScript AI?</h1>
            <h2>Faster diagnosis</h2>
                <p>MedScript AI accelerates the diagnostic process by automating tasks such as analyzing patient symptoms, past medical records, and diagnostic data. It uses advanced AI models to generate comprehensive and precise diagnostic reports in real time.</p>
            <h2>Improved patient outcomes</h2>
                <p>By delivering accurate diagnostic reports and recommending potential treatment plans swiftly, MedScript AI ensures that patients receive timely interventions, which is crucial for managing acute and chronic conditions.</p>
            <h2>Simplified streamlined healthcare workflows</h2>
                <p>MedScript AI integrates seamlessly into existing healthcare systems, reducing the administrative burden on medical staff and enhancing coordination between departments. Tasks such as generating discharge summaries, prescription writing, and report sharing are automated.</p>
    </div>  
""", unsafe_allow_html=True)

# Technology Section
st.markdown(f"""
    <div class = "container">
        <h1>Why MedScript AI Stands Out</h1>
        <h2>Leveraging Retrieval-Augmented Generation (RAG)</h2>
        <p>
            MedScript AI uses <strong>Retrieval-Augmented Generation (RAG)</strong>, an advanced AI technique that combines 
            information retrieval and generative models to create accurate, context-aware, and reliable outputs. By dynamically 
            fetching relevant information from trusted sources, RAG ensures that MedScript AI generates detailed and highly 
            contextualized reports.
        </p>
        <h3>How RAG Enhances MedScript AI:</h3>
        <ul>
            <li><strong>Improved Contextual Understanding:</strong> Dynamically pulls specific, relevant data points to ground outputs in accurate, up-to-date medical knowledge.</li>
            <li><strong>Enhanced Accuracy and Relevance:</strong> Incorporates real-time retrieved information, aligning insights with current medical standards and practices.</li>
            <li><strong>Dynamic Adaptability:</strong> Adapts to different scenarios by retrieving and synthesizing tailored data for specific input queries or cases.</li>
        </ul>
        
        <h2>Training on Robust Datasets like MIMIC-IV</h2>
        <p>
            MedScript AI is trained on the <strong>MIMIC-IV (Medical Information Mart for Intensive Care)</strong> dataset, 
            a comprehensive, de-identified dataset of patient records. This dataset enables the model to understand a 
            wide spectrum of medical conditions and scenarios, making it highly reliable and credible.
        </p>
        <h3>Why MIMIC-IV is a Game-Changer:</h3>
        <ul>
            <li><strong>Rich Clinical Context:</strong> Provides diverse and detailed real-world medical scenarios, helping MedScript AI generalize across routine and complex cases.</li>
            <li><strong>Reliability and Credibility:</strong> Trained on a rigorously curated dataset, ensuring the AI model produces trustworthy outputs.</li>
            <li><strong>Advanced Research Potential:</strong> Incorporates cutting-edge medical research insights for informed clinical decision support.</li>
        </ul>
        
        <h2>Why This Matters</h2>
        <p>
            By combining RAG’s dynamic retrieval capabilities with robust training on datasets like MIMIC-IV, MedScript AI delivers:
        </p>
        <ul>
            <li><strong>Precision in reports:</strong> Providing actionable insights for critical decisions.</li>
            <li><strong>Personalization for patient-specific contexts:</strong> Ensuring tailored care for every patient.</li>
            <li><strong>Scalability for diverse healthcare environments:</strong> Supporting clinics, hospitals, and beyond.</li>
        </ul>
        <p>
            This synergy of advanced techniques and data makes MedScript AI a pioneering tool in modern healthcare.
        </p>
    </div>
""", unsafe_allow_html=True)

# st.header("How MedScript AI Works")
# st.write(
#     """
#     MedScript AI uses **Retrieval-Augmented Generation (RAG)** to provide additional context to its models, 
#     ensuring accuracy and relevance in the generated reports. Our AI is trained on robust datasets like 
#     MIMIC-IV making it highly reliable and credible.
#     """
# )
=======
# Initialize session state
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "home"

def navigate_to(page_name):
    st.session_state["current_page"] = page_name
    st.experimental_rerun()

# Render page based on session state
if st.session_state["current_page"] == "home":
    st.markdown("""
        <div class="header">
            <h1>MedScript-AI</h1>
            <p>Revolutionizing Healthcare with AI-Driven Diagnosis</p>
        </div>
    """, unsafe_allow_html=True)

    st.header("What is MedScript AI?")
    st.write(
        """
        **MedScript AI** is an innovative healthcare application that combines cutting-edge artificial intelligence 
        with medical expertise. It takes in patient details, their current symptoms, and previous diagnoses to 
        generate comprehensive diagnosis reports. These reports help doctors make quick and informed treatment decisions.
        """
    )

    # Key Features Section
    st.header("Key Features")
    features = {
        "📝 Patient Data Collection": "Easily capture and store patient symptoms and diagnoses.",
        "💡 AI Diagnosis Reports": "Generate accurate, concise reports to aid in decision-making.",
        "⏱️ Streamlined Workflow": "Save time and focus on delivering quality care."
    }
    for feature, description in features.items():
        st.subheader(feature)
        st.write(description)

    st.markdown("---")

    # Benefits Section
    st.header("Why Choose MedScript AI?")
    benefits = [
        "Faster diagnosis process for doctors.",
        "Improved patient outcomes with timely treatments.",
        "Simplified and streamlined healthcare workflows."
    ]
    for benefit in benefits:
        st.markdown(f"- {benefit}")

    st.markdown("---")
>>>>>>> 2138f6a9a877100f42001d4731693e4f4edd8ea4

    # Technology Section
    st.header("How MedScript AI Works")
    st.write(
        """
        MedScript AI uses **Retrieval-Augmented Generation (RAG)** to provide additional context to its models,
        ensuring accuracy and relevance in the generated reports. Our AI is trained on robust datasets like
        MIMIC-III, ChestX-ray14, PTB-XL, and PubMed Central Open Access Subset, making it highly reliable and credible.
        """
    )

    steps = [
        "1️⃣ **Input patient details and symptoms.**",
        "2️⃣ **AI analyzes data and retrieves relevant context.**",
        "3️⃣ **Generates a diagnosis report for doctor review.**"
    ]
    st.write("### Workflow")
    for step in steps:
        st.markdown(step)

    st.markdown("---")

elif st.session_state["current_page"] == "patient_form":
    patient_form.render()
