#!/bin/bash

# Exit on any error
set -e

echo "Checking GCP configuration..."

# Get current project
current_project=$(gcloud config get-value project)
if [ -z "$current_project" ]; then
    echo "Error: No project is currently set"
    exit 1
fi

echo "Current project: $current_project"
echo "Gathering resource information..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if gcloud is installed
if ! command_exists gcloud; then
    echo "Error: gcloud CLI is not installed"
    exit 1
fi

echo -e "\n=== Compute Engine Instances ==="
gcloud compute instances list --format="table(name,zone,status,machineType.machine_type())"

echo -e "\n=== Cloud SQL Instances ==="
gcloud sql instances list --format="table(name,databaseVersion,region,state)"

echo -e "\n=== App Engine Services ==="
gcloud app services list 2>/dev/null || echo "No App Engine services found"

echo -e "\n=== Kubernetes Engine Clusters ==="
gcloud container clusters list --format="table(name,zone,status)" 2>/dev/null || echo "No GKE clusters found"

echo -e "\n=== Cloud Run Services ==="
gcloud run services list --format="table(name,region,status)" 2>/dev/null || echo "No Cloud Run services found"

echo -e "\n=== Active Cloud Functions ==="
gcloud functions list --format="table(name,status,runtime)" 2>/dev/null || echo "No Cloud Functions found"

echo -e "\n=== Load Balancers ==="
gcloud compute forwarding-rules list --format="table(name,IPAddress,target)" 2>/dev/null || echo "No load balancers found"