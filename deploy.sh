#!/bin/bash

# Exit on any error
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print step information
print_step() {
    echo -e "\n${BLUE}Step: $1${NC}"
    echo "----------------------------------------"
}

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
        exit 1
    fi
}

# Function to prompt for input with a default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    read -p "$prompt [$default]: " value
    echo "${value:-$default}"
}

# Function to confirm before proceeding
confirm() {
    read -p "Do you want to proceed? (y/n): " answer
    if [[ "$answer" != "y" ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
}

# Function to wait for cluster to be ready
wait_for_cluster() {
    local cluster=$1
    local zone=$2
    print_step "Waiting for cluster to be ready..."
    
    while true; do
        STATUS=$(gcloud container clusters list --filter="name=$cluster AND location=$zone" --format="value(status)" 2>/dev/null || echo "ERROR")
        if [ "$STATUS" = "RUNNING" ]; then
            echo -e "${GREEN}Cluster is ready!${NC}"
            break
        elif [ "$STATUS" = "ERROR" ]; then
            echo -e "${RED}Error getting cluster status${NC}"
            exit 1
        else
            echo -e "${YELLOW}Cluster status: $STATUS - waiting...${NC}"
            sleep 30
        fi
    done
}

# Function to wait for image to be available in GCR
wait_for_image() {
    local project=$1
    local image=$2
    local tag=$3
    print_step "Verifying image availability in Container Registry..."
    
    while true; do
        if gcloud container images describe gcr.io/$project/$image:$tag >/dev/null 2>&1; then
            echo -e "${GREEN}Image is available in Container Registry!${NC}"
            break
        else
            echo -e "${YELLOW}Waiting for image to be available...${NC}"
            sleep 10
        fi
    done
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    local namespace=$1
    print_step "Waiting for deployment to be ready..."
    
    kubectl -n $namespace rollout status deployment/backend-deployment --timeout=300s
    check_status
}

# Function to verify pods are running
verify_pods() {
    local namespace=$1
    print_step "Verifying pod status..."
    
    while true; do
        PODS_READY=$(kubectl get pods -n $namespace -l app=backend -o jsonpath='{.items[*].status.containerStatuses[*].ready}' | grep -o "true" | wc -l)
        PODS_TOTAL=$(kubectl get pods -n $namespace -l app=backend --no-headers | wc -l)
        
        if [ "$PODS_READY" -eq "$PODS_TOTAL" ] && [ "$PODS_TOTAL" -gt 0 ]; then
            echo -e "${GREEN}All pods are running and ready!${NC}"
            break
        else
            echo -e "${YELLOW}Pods ready: $PODS_READY/$PODS_TOTAL - waiting...${NC}"
            sleep 10
        fi
    done
}

echo -e "${BLUE}Welcome to the GKE Deployment Script${NC}"
echo "Please provide the following information (press Enter to use default values):"
echo "----------------------------------------"

# Interactive configuration
PROJECT_ID=$(prompt_with_default "Enter your Google Cloud Project ID" "medscript-437117")
CLUSTER_NAME=$(prompt_with_default "Enter the cluster name" "project-cluster-1")
ZONE=$(prompt_with_default "Enter the zone" "us-central1-a")
NAMESPACE=$(prompt_with_default "Enter the namespace" "medscript")
IMAGE_NAME=$(prompt_with_default "Enter the image name" "fast-api-backend")
IMAGE_TAG=$(prompt_with_default "Enter the image tag" "latest")
DOCKERFILE_PATH=$(prompt_with_default "Enter the path to your Dockerfile" "app/Dockerfile")
MACHINE_TYPE=$(prompt_with_default "Enter the machine type" "e2-standard-2")
MIN_NODES=$(prompt_with_default "Enter minimum number of nodes" "0")
MAX_NODES=$(prompt_with_default "Enter maximum number of nodes" "3")
SERVICE_ACCOUNT=$(prompt_with_default "Enter the service account email" "github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com")

# Display configuration summary
echo -e "\n${BLUE}Configuration Summary:${NC}"
echo "----------------------------------------"
echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Zone: $ZONE"
echo "Namespace: $NAMESPACE"
echo "Image Name: $IMAGE_NAME"
echo "Image Tag: $IMAGE_TAG"
echo "Dockerfile Path: $DOCKERFILE_PATH"
echo "Machine Type: $MACHINE_TYPE"
echo "Node Range: $MIN_NODES to $MAX_NODES"
echo "Service Account: $SERVICE_ACCOUNT"
echo "----------------------------------------"

confirm

print_step "1. Authenticating with Google Cloud"
gcloud auth login
gcloud config set project $PROJECT_ID
check_status

print_step "2. Building Docker image"
docker build -f $DOCKERFILE_PATH --platform linux/amd64 --no-cache -t $IMAGE_NAME:$IMAGE_TAG .
check_status

print_step "3. Tagging Docker image"
docker tag $IMAGE_NAME:$IMAGE_TAG gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG
check_status

print_step "4. Configuring Docker authentication"
gcloud auth configure-docker
check_status

print_step "5. Pushing image to Container Registry"
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG
check_status

# Verify image is available in GCR
wait_for_image $PROJECT_ID $IMAGE_NAME $IMAGE_TAG

print_step "6. Creating GKE cluster"
gcloud beta container --project $PROJECT_ID clusters create $CLUSTER_NAME \
    --zone $ZONE \
    --tier "standard" \
    --no-enable-basic-auth \
    --cluster-version "1.30.5-gke.1699000" \
    --release-channel "regular" \
    --machine-type $MACHINE_TYPE \
    --image-type "COS_CONTAINERD" \
    --disk-type "pd-balanced" \
    --disk-size "100" \
    --metadata disable-legacy-endpoints=true \
    --service-account $SERVICE_ACCOUNT \
    --num-nodes "3" \
    --logging=SYSTEM,WORKLOAD \
    --monitoring=SYSTEM,STORAGE,POD,DEPLOYMENT,STATEFULSET,DAEMONSET,HPA,CADVISOR,KUBELET \
    --enable-ip-alias \
    --network "projects/$PROJECT_ID/global/networks/default" \
    --subnetwork "projects/$PROJECT_ID/regions/us-central1/subnetworks/default" \
    --no-enable-intra-node-visibility \
    --default-max-pods-per-node "110" \
    --enable-autoscaling \
    --min-nodes $MIN_NODES \
    --max-nodes $MAX_NODES \
    --location-policy "BALANCED" \
    --enable-ip-access \
    --security-posture=standard \
    --workload-vulnerability-scanning=disabled \
    --no-enable-master-authorized-networks \
    --no-enable-google-cloud-access \
    --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
    --enable-autoupgrade \
    --enable-autorepair \
    --max-surge-upgrade 1 \
    --max-unavailable-upgrade 0 \
    --binauthz-evaluation-mode=DISABLED \
    --enable-autoprovisioning \
    --min-cpu 4 \
    --max-cpu 8 \
    --min-memory 16 \
    --max-memory 32 \
    --enable-autoprovisioning-autorepair \
    --enable-autoprovisioning-autoupgrade \
    --autoprovisioning-max-surge-upgrade 1 \
    --autoprovisioning-max-unavailable-upgrade 0 \
    --autoscaling-profile optimize-utilization \
    --enable-managed-prometheus \
    --enable-vertical-pod-autoscaling \
    --enable-shielded-nodes \
    --node-locations $ZONE

# Wait for cluster to be ready
wait_for_cluster $CLUSTER_NAME $ZONE

print_step "7. Getting cluster credentials"
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE
check_status

print_step "8. Creating namespace"
kubectl create namespace $NAMESPACE 2>/dev/null || true
check_status

print_step "9. Creating Kubernetes service account"
kubectl apply -f deployment/service-account.yaml
check_status

print_step "10. Deploying application"
# Update the image in the deployment file
sed -i "s|image: gcr.io/.*/.*|image: gcr.io/$PROJECT_ID/$IMAGE_NAME:$IMAGE_TAG|g" deployment/backend/app-deployment.yaml

# Apply the configurations
kubectl apply -f deployment/backend/app-deployment.yaml
kubectl apply -f deployment/backend/app-service.yaml
check_status

# Wait for deployment to be ready
wait_for_deployment $NAMESPACE

# Verify pods are running
verify_pods $NAMESPACE

echo -e "\n${GREEN}Deployment completed successfully!${NC}"
echo -e "\nUseful commands to check your deployment:"
echo "----------------------------------------"
echo "Check pods status:        kubectl get pods -n $NAMESPACE"
echo "Check services:           kubectl get services -n $NAMESPACE"
echo "View pod logs:            kubectl logs -n $NAMESPACE <pod-name>"
echo "Describe deployment:      kubectl describe deployment -n $NAMESPACE"