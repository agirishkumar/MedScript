import streamlit as st
import pages.patient_form as patient_form
# from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Medscript-AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

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

# Hero Section
st.markdown("""
    <div class="header">
        <h1>Medscript-AI</h1>
        <p>Revolutionizing Healthcare with AI-Driven Diagnosis</p>
        <button class="cta-button">Create a Free Account</button>
    </div>
""", unsafe_allow_html=True)

# st.title("Revolutionizing Healthcare with AI-Driven Diagnosis")
# st.subheader("Simplify treatment decisions and save valuable time with MedScript AI.")
# st.markdown("### 🚀 **Empowering doctors with AI-generated diagnosis reports.**")
# st.markdown("---")

# Overview Section
st.header("What is MedScript AI?")
st.write(
    """
    **MedScript AI** is an innovative healthcare application that combines cutting-edge artificial intelligence 
    with medical expertise. It takes in patient details, their current symptoms, and previous diagnoses to 
    generate comprehensive diagnosis reports. These reports help doctors make quick and informed treatment decisions.
    """
)
# st.image(logo, caption="MedScript AI Logo", use_column_width=True)

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

st.page_link("pages/patient_form.py", label="Patient Form", icon="1️⃣")


# # Sidebar Navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.selectbox("Select a Page:", ["Home", "Patient Form"])



# # Home Page
# if page == "Home":
#     # Add a header section with a background
#     st.markdown(
#         """
#         <style>
#         .header {
#             background-color: #7CB9E8   ;
#             padding: 100px;
#             text-align: center;
#             border-radius: 10px;
#         }
#         .header h1 {
#             color: white;
#             font-size: 6rem;
#         }
#         .header p {
#             color: white;
#             font-size: 2rem;
#         }
#         </style>
#         <div class="header">
#             <h1>MEDSCRIPT-AI</h1>
#             <p>Where Medicine Meets AI</p>
#         </div>
#         """,
#         unsafe_allow_html=True,
#     )

#     # # Main content
#     # col1, col2, col3 = st.columns([1, 2, 1])
#     # with col2:
#     #     st.image("https://via.placeholder.com/400", caption="Streamlit - Your Web Framework", use_column_width=True)

#     st.markdown(
#         """
#         <h2 style="text-align: center;">Features of the Webpage.</h2>
#         - 🎨 **Visually Engaging UI**: Designed to capture attention with smooth layouts and vivid colors.
#         - ⚡ **Fast Loading**: Streamlit's optimized rendering makes this page highly responsive.
#         - 🌐 **Interactive Elements**: Easily add widgets, inputs, and charts to enhance user experience.

#         ## Build Your Next Project
#         - 🚀 Quickly develop dashboards
#         - 🛠️ Integrate with powerful machine learning models
#         - 📊 Visualize your data interactively
#         """,
#         unsafe_allow_html=True,
#     )

# # Patient Form Page
# elif page == "Patient Form" or home == "Patient Form":
#     patient_form.render()

# # Footer
# st.markdown(
#     """
#     <style>
#     .footer {
#         text-align: center;
#         padding: 10px;
#         background-color: #333;
#         color: white;
#         border-radius: 10px;
#     }
#     .footer p {
#         margin: 0;
#         font-size: 1rem;
#     }
#     </style>
#     <div class="footer">
#         <p>© 2024 Streamlit Webpage | Designed by Python</p>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )
