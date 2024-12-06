# monitor.py
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from google.cloud import monitoring_v3
from google.cloud import container_v1
from google.cloud import compute_v1
from google.cloud.sql.connector import Connector
import os

def get_gcp_metrics(project_id):
    """Get GCP resource metrics"""
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    
    metrics = {}
    
    # Get Cloud Run metrics
    cloudrun_filter = 'metric.type = "run.googleapis.com/container/cpu/utilization"'
    metrics['cloudrun'] = client.list_time_series(
        request={
            "name": project_name,
            "filter": cloudrun_filter,
            "interval": {"minutes": 30}  # Last 30 minutes
        }
    )
    
    # Get GKE cluster metrics
    gke_filter = 'metric.type = "kubernetes.io/container/cpu/core_usage_time"'
    metrics['gke'] = client.list_time_series(
        request={
            "name": project_name,
            "filter": gke_filter,
            "interval": {"minutes": 30}
        }
    )
    
    return metrics

def get_qdrant_status(instance_ip):
    """Check Qdrant instance status"""
    try:
        response = requests.get(f"http://{instance_ip}:6333/health")
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_db_metrics(connection_name, db_user, db_pass, db_name):
    """Get PostgreSQL database metrics"""
    try:
        connector = Connector()
        conn = connector.connect(
            instance_connection_string=connection_name,
            driver="pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        
        cursor = conn.cursor()
        
        # Get database size
        cursor.execute("SELECT pg_database_size(current_database());")
        db_size = cursor.fetchone()[0]
        
        # Get connection count
        cursor.execute("SELECT count(*) FROM pg_stat_activity;")
        connections = cursor.fetchone()[0]
        
        # Get table statistics
        cursor.execute("""
            SELECT schemaname, relname, n_live_tup 
            FROM pg_stat_user_tables 
            ORDER BY n_live_tup DESC;
        """)
        table_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'db_size': db_size,
            'connections': connections, 
            'table_stats': table_stats
        }
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def create_usage_chart(data, title):
    """Create a line chart for resource usage"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['time'], y=data['value'], mode='lines'))
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Usage")
    return fig

def main():
    st.title("MedScript Infrastructure Monitor")
    
    # Load GCP credentials from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    instance_ip = os.getenv("QDRANT_INSTANCE_IP")
    db_connection = os.getenv("CLOUD_SQL_CONNECTION")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")
    
    # Cloud Run Section
    st.header("Cloud Run (UI Application)")
    metrics = get_gcp_metrics(project_id)
    if 'cloudrun' in metrics:
        cloudrun_data = {
            'time': [point.points[0].interval.end_time for point in metrics['cloudrun']],
            'value': [point.points[0].value.double_value for point in metrics['cloudrun']]
        }
        st.plotly_chart(create_usage_chart(cloudrun_data, "Cloud Run CPU Usage"))
    
    # GKE (Airflow) Section
    st.header("GKE Cluster (Airflow)")
    if 'gke' in metrics:
        gke_data = {
            'time': [point.points[0].interval.end_time for point in metrics['gke']],
            'value': [point.points[0].value.double_value for point in metrics['gke']]
        }
        st.plotly_chart(create_usage_chart(gke_data, "GKE CPU Usage"))
        
        # Airflow webserver status
        try:
            response = requests.get("http://airflow-public-ip:8080/health")
            if response.status_code == 200:
                st.success("Airflow is healthy")
            else:
                st.error("Airflow is not responding")
        except:
            st.warning("Unable to connect to Airflow webserver")
    
    # Qdrant Section
    st.header("Qdrant Vector Database")
    qdrant_status = get_qdrant_status(instance_ip)
    if qdrant_status:
        st.success("Qdrant is healthy")
        st.json(qdrant_status)
    else:
        st.error("Unable to connect to Qdrant")
    
    # PostgreSQL Section
    st.header("Cloud SQL (PostgreSQL)")
    db_metrics = get_db_metrics(db_connection, db_user, db_pass, db_name)
    if db_metrics:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Database Size (MB)", f"{db_metrics['db_size'] / (1024*1024):.2f}")
        with col2:
            st.metric("Active Connections", db_metrics['connections'])
        
        # Table statistics
        st.subheader("Table Statistics")
        df = pd.DataFrame(db_metrics['table_stats'], 
                         columns=['Schema', 'Table', 'Row Count'])
        st.dataframe(df)
    
    # Auto-refresh
    if st.button("Refresh Metrics"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()