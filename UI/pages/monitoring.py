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
tableau_html = """
    <div style="margin: 20px 500px">
        <div class='tableauPlaceholder' id='viz1733455825368' style='position: relative; size: 150%'>
            <noscript>
                <a href='#'><img alt='Dashboard 1' src='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Ta&#47;Tableau_Medscript&#47;Dashboard1&#47;1_rss.png' style='border: none' /></a>
            </noscript>
            <object class='tableauViz'  style='display:none;'>
                <param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' /> 
                <param name='embed_code_version' value='3' /> 
                <param name='site_root' value='' />
                <param name='name' value='Tableau_Medscript&#47;Dashboard1' />
                <param name='tabs' value='no' />
                <param name='toolbar' value='yes' />
                <param name='static_image' value='https:&#47;&#47;public.tableau.com&#47;static&#47;images&#47;Ta&#47;Tableau_Medscript&#47;Dashboard1&#47;1.png' />
                <param name='animate_transition' value='yes' />
                <param name='display_static_image' value='yes' />
                <param name='display_spinner' value='yes' />
                <param name='display_overlay' value='yes' />
                <param name='display_count' value='yes' />
                <param name='language' value='en-US' />
                <param name='filter' value='publish=yes' />
            </object>
        </div>
    
        <script type='text/javascript'>
            var divElement = document.getElementById('viz1733455825368');
            var vizElement = divElement.getElementsByTagName('object')[0];
            if ( divElement.offsetWidth > 800 ) { vizElement.style.width='1250px';vizElement.style.height='727px';} 
            else if ( divElement.offsetWidth > 500 ) { vizElement.style.width='1250px';vizElement.style.height='727px';} 
            else { vizElement.style.width='150%';vizElement.style.height='1577px';} 
            var scriptElement = document.createElement('script');
            scriptElement.src = 'https://public.tableau.com/javascripts/api/viz_v1.js';
            vizElement.parentNode.insertBefore(scriptElement, vizElement);
        </script>
    </div>
"""  # Replace with your Tableau public dashboard link
st.components.v1.html(tableau_html,height=1200)

# Footer or additional monitoring information
st.write("For detailed logs or additional insights, please check the system logs or the admin panel.")
