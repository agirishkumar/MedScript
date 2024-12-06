# UI/pages/monitoring.py

import streamlit as st

# Set the page configuration
st.set_page_config(
    page_title="MedScript AI Monitoring",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
            width: 65%;
            margin: 0 auto;
            padding: 20px;
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

        button[kind="secondary"]{
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

# Add a title and description
st.markdown("""
    <div class="header">
        <h1>MedScript AI Monitoring Dashboard</h1>
        <p>Welcome to the MedScript AI Monitoring Page. 
            Here, you can track the performance of your models, monitor data pipelines, and review system statistics.
            Below, you will find a live Tableau Public Dashboard embedded for detailed insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
# st.title("MedScript AI Monitoring Dashboard")
# st.write("""
# Welcome to the MedScript AI Monitoring Page. 
# Here, you can track the performance of your models, monitor data pipelines, and review system statistics.
# Below, you will find a live Tableau Public Dashboard embedded for detailed insights.
# """)

# Embed the Tableau Public Dashboard
tableau_url = "https://public.tableau.com/app/profile/mallika.gaikwad/viz/Tableau_Medscript/Dashboard1?publish=yes"  # Replace with your Tableau public dashboard link
st.components.v1.html(
    f"""
    <iframe src="{tableau_url}" width="100%" height="800" frameborder="0"></iframe>
    """,
    height=850,
)

# Footer or additional monitoring information
st.write("For detailed logs or additional insights, please check the system logs or the admin panel.")
