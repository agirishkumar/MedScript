import streamlit as st
import pages.patient_form as patient_form

# Set page configuration
st.set_page_config(
    page_title="Medscript-AI",
    page_icon="🤖",
    layout="wide",  # "wide" layout uses full screen, without sidebar
    initial_sidebar_state="collapsed",  # Ensures the sidebar is collapsed by default, but we will hide it completely
)

st.markdown(
    """
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #0d1117;
            color: #ffffff;
            margin: 0;
            padding: 0;
        }

        .header {
            text-align: center;
            padding: 50px 0;
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

        .cta-button {
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

        .offer-card {
            background-color: #202c38;
            padding: 30px;
            border-radius: 10px;
            width: 300px;
            text-align: center;
        }

        .offer-card h3 {
            color: #f4f4f4;
            font-size: 1.5rem;
        }

        .offer-card p {
            color: #b0b3b8;
            font-size: 1.2rem;
        }

        .offer-card a {
            color: #f4f4f4;
            text-decoration: none;
            font-size: 1.2rem;
            margin-top: 15px;
            display: block;
        }
    </style>
    """,
    unsafe_allow_html=True
)

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
