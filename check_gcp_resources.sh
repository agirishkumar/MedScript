#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "\n${GREEN}=== $1 ===${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to handle command execution with error checking
execute_command() {
    local command="$1"
    local error_message="$2"
    
    if ! eval "$command" 2>/dev/null; then
        echo -e "${YELLOW}$error_message${NC}"
    fi
}

# Function to list gcr.io container images with versions
list_gcr_images() {
    local project_id="$1"
    local gcr_path="gcr.io/${project_id}"
    
    print_header "Container Registry Images (gcr.io)"
    echo -e "${BLUE}Registry path: ${gcr_path}${NC}"
    
    # Get all image names from gcr.io
    local images=$(gcloud container images list --repository="gcr.io/${project_id}" --format="value(name)")
    
    if [ -z "$images" ]; then
        echo -e "${YELLOW}No images found in gcr.io/${project_id}${NC}"
        return
    fi
    
    # For each image repository
    for image in $images; do
        echo -e "\n${BLUE}📦 Image: ${image}${NC}"
        
        # Print version table header
        printf "%-15s %-30s %-15s %-20s %-20s\n" "Name" "Description" "Tags" "Created" "Updated"
        echo "--------------------------------------------------------------------------------"
        
        # List all tags and details for the image
        gcloud container images list-tags "$image" \
            --format="table[no-heading](
                digest.slice(7:19).join(''),
                description.yesno(no='-'),
                tags.list(),
                timestamp.date('%Y-%m-%d %H:%M:%S'),
                timestamp.date('%Y-%m-%d %H:%M:%S')
            )" \
            --sort-by=~timestamp
            
        echo "--------------------------------------------------------------------------------"
    done
}

echo -e "${GREEN}Checking GCP configuration...${NC}"

# Check if gcloud is installed
if ! command_exists gcloud; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    exit 1
fi

# Get current project
current_project=$(gcloud config get-value project)
if [ -z "$current_project" ]; then
    echo -e "${RED}Error: No project is currently set${NC}"
    exit 1
fi

echo -e "Current project: ${GREEN}$current_project${NC}"
echo "Gathering resource information..."

# Check Compute Engine Instances
print_header "Compute Engine Instances"
execute_command "gcloud compute instances list --format='table(
    name,
    zone,
    status,
    machineType.machine_type(),
    networkInterfaces[0].networkIP:label=INTERNAL_IP,
    networkInterfaces[0].accessConfigs[0].natIP:label=EXTERNAL_IP
)'" "No Compute Engine instances found"

# Check Cloud SQL Instances
print_header "Cloud SQL Instances"
execute_command "gcloud sql instances list --format='table(
    name,
    databaseVersion,
    region,
    state,
    settings.tier
)'" "No Cloud SQL instances found"

# Check App Engine Services
print_header "App Engine Services"
execute_command "gcloud app services list" "No App Engine services found"

# Check GKE Clusters
print_header "Kubernetes Engine Clusters"
execute_command "gcloud container clusters list --format='table(
    name,
    zone,
    status,
    currentNodeCount,
    currentMasterVersion:label=MASTER_VERSION
)'" "No GKE clusters found"

# Check Cloud Run Services
print_header "Cloud Run Services"
execute_command "gcloud run services list --format='table(
    name,
    region,
    status.conditions[0].status,
    status.url
)'" "No Cloud Run services found"

# Check Cloud Functions
print_header "Active Cloud Functions"
execute_command "gcloud functions list --format='table(
    name,
    status,
    runtime,
    entryPoint
)'" "No Cloud Functions found"

# Check Load Balancers
print_header "Load Balancers"
execute_command "gcloud compute forwarding-rules list --format='table(
    name,
    IPAddress,
    target,
    loadBalancingScheme
)'" "No load balancers found"

# Check GCR Images with versions
list_gcr_images "$current_project"

# Add Resource Usage Summary
print_header "Resource Usage Summary"
echo "Active instances: $(gcloud compute instances list --filter="status=RUNNING" --format="value(name)" | wc -l)"
echo "Total SQL instances: $(gcloud sql instances list --format="value(name)" | wc -l)"
echo "Active Cloud Run services: $(gcloud run services list --format="value(name)" | wc -l)"