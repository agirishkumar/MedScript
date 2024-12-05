#!/bin/bash

# Check if gcloud CLI is installed
if ! command -v gcloud &> /dev/null
then
    echo "gcloud CLI not found. Please install it and try again."
    exit 1
fi

# Get the current active project
PROJECT=$(gcloud config get-value project 2>/dev/null)

if [ -z "$PROJECT" ]; then
  echo "No active GCP project is set. Use 'gcloud config set project PROJECT_ID' to set one."
  exit 1
fi

echo "Active GCP Project: $PROJECT"

# List active resources in the project
# Function to check active resources and handle errors
function list_resources {
  RESOURCE_TYPE=$1
  echo -e "\nListing $RESOURCE_TYPE:"
  gcloud $RESOURCE_TYPE list --project="$PROJECT" --format="table" || echo "Failed to list $RESOURCE_TYPE. Ensure you have the required permissions."
}

# List resources (examples include compute instances, storage buckets, and databases)
list_resources "compute instances"
list_resources "storage buckets"
list_resources "sql instances"
list_resources "container clusters"
list_resources "functions"
list_resources "pubsub topics"
list_resources "bigtable instances"
list_resources "dataproc clusters"

# Add additional resource types as needed

# Final message
echo -e "\nResource listing completed for project: $PROJECT"
