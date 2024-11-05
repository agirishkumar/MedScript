import time
# import paramiko
from googleapiclient import discovery
from google.oauth2 import service_account
from constants import PROJECT_ID, SERVICE_ACCOUNT_FILEPATH#, set_vectorstore_ip
import access_vectorstore_instance as avi

# GCP configuration
# PROJECT_ID = "your-project-id"
ZONE = "us-central1-a"
INSTANCE_NAME = "instance-20241101-155133"
# SERVICE_ACCOUNT_FILE = ""  # Path to service account JSON file

# # Qdrant Docker command
# QDRANT_DOCKER_COMMAND = "sudo docker run -d --name qdrant -p 6333:6333 -v ~/qdrant_storage:/qdrant/storage qdrant/qdrant"

# Function to start the VM instance
def start_instance(compute, project, zone, instance_name):
    print(f"Starting instance {instance_name}...")
    request = compute.instances().start(project=project, zone=zone, instance=instance_name)
    response = request.execute()
    return response

# Function to check if the VM instance is running
def is_instance_running(compute, project, zone, instance_name):
    instance = compute.instances().get(project=project, zone=zone, instance=instance_name).execute()
    return instance['status'] == 'RUNNING'

# # Function to execute a command via SSH
# def run_ssh_command(ip_address, username, command):
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     ssh.connect(ip_address, username=username, key_filename="path/to/your-ssh-key")  # Replace with your SSH key path
#     stdin, stdout, stderr = ssh.exec_command(command)
#     print(stdout.read().decode())
#     print(stderr.read().decode())
#     ssh.close()

def main():
    # Authenticate with Google Cloud
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILEPATH)
    compute = discovery.build('compute', 'v1', credentials=credentials)

    # Step 1: Start the VM instance
    start_instance(compute, PROJECT_ID, ZONE, INSTANCE_NAME)

    # Step 2: Wait for the instance to start
    print("Waiting for the instance to start...")
    while not is_instance_running(compute, PROJECT_ID, ZONE, INSTANCE_NAME):
        print("Instance is still starting...")
        time.sleep(10)  # Wait 10 seconds before checking again

    print("Instance is running.")

    # Step 3: Get the external IP address of the instance
    instance = compute.instances().get(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME).execute()
    ip_address = instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
    print(f"Instance IP: {ip_address}")

    avi.set_vectorstore_ip(ip_address)

    print("IP: ", avi.get_vectorstore_ip())
    # # Step 4: Run Qdrant Docker container on the VM via SSH
    # run_ssh_command(ip_address, "your-username", QDRANT_DOCKER_COMMAND)  # Replace "your-username" with the VM username

    # print("Qdrant Docker container started on the VM.")

if __name__ == "__main__":
    main()
