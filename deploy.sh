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

# Function to validate input
validate_input() {
    local image_type=$1
    local dockerfile_path=$2
    
    # Validate image type
    if [[ ! "$image_type" =~ ^(backend|data_pipeline)$ ]]; then
        echo -e "${RED}Error: Image type must be either 'backend' or 'data_pipeline'${NC}"
        exit 1
    fi

    # Validate Dockerfile exists
    if [ ! -f "$dockerfile_path" ]; then
        echo -e "${RED}Error: Dockerfile not found at $dockerfile_path${NC}"
        exit 1
    fi

    # Validate deployment files exist
    local deployment_path="deployment/${image_type}"
    if [ ! -d "$deployment_path" ]; then
        echo -e "${RED}Error: Deployment directory not found at $deployment_path${NC}"
        exit 1
    fi
}

# Function to check if image exists in GCR
check_image_exists() {
    local project=$1
    local image=$2
    local tag=$3
    
    if gcloud container images describe gcr.io/$project/$image:$tag >/dev/null 2>&1; then
        return 0  # Image exists
    else
        return 1  # Image doesn't exist
    fi
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

# Function to check if cluster exists
check_cluster_exists() {
    local cluster=$1
    local zone=$2
    
    if gcloud container clusters describe $cluster --zone $zone >/dev/null 2>&1; then
        return 0  # Cluster exists
    else
        return 1  # Cluster doesn't exist
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

# Function to get deployment files
get_deployment_files() {
    local image_type=$1
    if [ "$image_type" == "backend" ]; then
        echo "deployment/backend/app-deployment.yaml deployment/backend/app-service.yaml"
    else
        echo "deployment/data_pipeline/deployment.yaml"
    fi
}

# Function to wait for deployment to be ready
wait_for_deployment() {
    local namespace=$1
    local image_type=$2
    print_step "Waiting for deployment to be ready..."
    
    local deployment_name="${image_type}-deployment"
    kubectl -n $namespace rollout status deployment/$deployment_name --timeout=300s
    check_status
}

# Function to verify pods are running
verify_pods() {
    local namespace=$1
    local image_type=$2
    print_step "Verifying pod status..."
    
    while true; do
        PODS_READY=$(kubectl get pods -n $namespace -l app=$image_type -o jsonpath='{.items[*].status.containerStatuses[*].ready}' | grep -o "true" | wc -l)
        PODS_TOTAL=$(kubectl get pods -n $namespace -l app=$image_type --no-headers | wc -l)
        
        if [ "$PODS_READY" -eq "$PODS_TOTAL" ] && [ "$PODS_TOTAL" -gt 0 ]; then
            echo -e "${GREEN}All pods are running and ready!${NC}"
            break
        else
            echo -e "${YELLOW}Pods ready: $PODS_READY/$PODS_TOTAL - waiting...${NC}"
            sleep 10
        fi
    done
}

# Function to create Kubernetes secrets
create_kubernetes_secrets() {
    local namespace=$1
    print_step "Creating Kubernetes Secrets"
    
    # Check if .env.kube exists
    if [ ! -f .env.kube ]; then
        echo -e "${RED}Error: .env.kube file not found${NC}"
        exit 1
    fi

    # Source the .env file
    set -a
    source .env.kube
    set +a

    # Create FastAPI secrets
    echo "Creating FastAPI secrets..."
    kubectl create secret generic gke-fastapi-secrets -n $namespace \
        --from-literal=database=$FASTAPI_DB_NAME \
        --from-literal=username=$FASTAPI_DB_USER \
        --from-literal=password=$FASTAPI_DB_PASS \
        --from-literal=jwt_secret_key=$FASTAPI_JWT_SECRET \
        --from-literal=jwt_refresh_secret_key=$FASTAPI_JWT_REFRESH_SECRET \
        --dry-run=client -o yaml | kubectl apply -f -
    check_status

    # Generate Airflow webserver secret if not exists
    if [ -z "$AIRFLOW_WEBSERVER_SECRET" ]; then
        AIRFLOW_WEBSERVER_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
    fi

    # Create Airflow secrets
    echo "Creating Airflow secrets..."
    kubectl create secret generic gke-airflow-secrets -n $namespace \
        --from-literal=slack_webhook_url=$AIRFLOW_SLACK_WEBHOOK \
        --from-literal=webserver-secret-key=$AIRFLOW_WEBSERVER_SECRET \
        --dry-run=client -o yaml | kubectl apply -f -
    check_status

    # If git SSH key file exists, add it to the secret
    if [ -f ./airflow-gke ]; then
        kubectl create secret generic gke-airflow-secrets -n $namespace \
            --from-file=gitSshKey=./airflow-gke \
            --dry-run=client -o yaml | kubectl apply -f -
        check_status
    fi

    echo -e "${GREEN}✓ Kubernetes secrets created successfully${NC}"
}

# Function to deploy component
deploy_component() {
    local image_type=$1
    local dockerfile_path=$2
    local project_id=$3
    local namespace=$4
    local image_tag=$5

    echo -e "\n${BLUE}Deploying ${image_type}...${NC}"
    echo "----------------------------------------"

    # Validate input
    validate_input $image_type $dockerfile_path

    # Build and push image if needed
    if check_image_exists $project_id $image_type $image_tag; then
        echo -e "${GREEN}Image gcr.io/$project_id/$image_type:$image_tag already exists. Skipping build steps.${NC}"
    else
        print_step "Building $image_type image"
        docker build -f $dockerfile_path --platform linux/amd64 --no-cache -t $image_type:$image_tag .
        check_status

        print_step "Tagging $image_type image"
        docker tag $image_type:$image_tag gcr.io/$project_id/$image_type:$image_tag
        check_status

        print_step "Pushing $image_type image"
        docker push gcr.io/$project_id/$image_type:$image_tag
        check_status

        wait_for_image $project_id $image_type $image_tag
    fi

    # Get deployment files
    local deployment_files=$(get_deployment_files $image_type)

    # Update and apply deployment files
    for file in $deployment_files; do
        echo "Updating image in $file"
        sed -i "s|image: gcr.io/.*/.*|image: gcr.io/$project_id/$image_type:$image_tag|g" $file
        kubectl apply -f $file -n $namespace
        check_status
    done

    # Wait for deployment and verify pods
    wait_for_deployment $namespace $image_type
    verify_pods $namespace $image_type
}

# Script starts here
echo -e "${BLUE}Welcome to the GKE Deployment Script${NC}"
echo "Please provide the following information (press Enter to use default values):"
echo "----------------------------------------"

# Basic configuration
PROJECT_ID=$(prompt_with_default "Enter your Google Cloud Project ID" "medscript-437117")
CLUSTER_NAME=$(prompt_with_default "Enter the cluster name" "project-cluster-1")
ZONE=$(prompt_with_default "Enter the zone" "us-central1-a")
NAMESPACE=$(prompt_with_default "Enter the namespace" "medscript")
MACHINE_TYPE=$(prompt_with_default "Enter the machine type" "e2-standard-2")
MIN_NODES=$(prompt_with_default "Enter minimum number of nodes" "0")
MAX_NODES=$(prompt_with_default "Enter maximum number of nodes" "3")
SERVICE_ACCOUNT=$(prompt_with_default "Enter the service account email" "github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com")

# Component selection
echo -e "\nSelect components to deploy:"
echo "1) Backend API"
echo "2) Data Pipeline"
echo "3) Both"
read -p "Enter choice [1]: " deployment_choice

case "${deployment_choice:-1}" in
    1)
        COMPONENTS=("backend")
        ;;
    2)
        COMPONENTS=("data_pipeline")
        ;;
    3)
        COMPONENTS=("backend" "data_pipeline")
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

IMAGE_TAG=$(prompt_with_default "Enter the image tag" "latest")

# Display configuration summary
echo -e "\n${BLUE}Configuration Summary:${NC}"
echo "----------------------------------------"
echo "Project ID: $PROJECT_ID"
echo "Cluster Name: $CLUSTER_NAME"
echo "Zone: $ZONE"
echo "Namespace: $NAMESPACE"
echo "Machine Type: $MACHINE_TYPE"
echo "Node Range: $MIN_NODES to $MAX_NODES"
echo "Service Account: $SERVICE_ACCOUNT"
echo "Components to deploy: ${COMPONENTS[*]}"
echo "Image Tag: $IMAGE_TAG"
echo "----------------------------------------"

confirm

print_step "1. Authenticating with Google Cloud"
gcloud auth login
gcloud config set project $PROJECT_ID
check_status

# Configure Docker authentication once
print_step "2. Configuring Docker authentication"
gcloud auth configure-docker
check_status

# Create or use existing cluster
if check_cluster_exists $CLUSTER_NAME $ZONE; then
    echo -e "${GREEN}Cluster $CLUSTER_NAME already exists in zone $ZONE. Skipping cluster creation.${NC}"
else
    print_step "3. Creating GKE cluster"
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

    wait_for_cluster $CLUSTER_NAME $ZONE
fi

print_step "4. Getting cluster credentials"
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE
check_status

print_step "5. Creating namespace"
kubectl create namespace $NAMESPACE 2>/dev/null || true
check_status

print_step "6. Creating Kubernetes secrets"
create_kubernetes_secrets $NAMESPACE

# Deploy each component
for component in "${COMPONENTS[@]}"; do
    case $component in
        "backend")
            deploy_component "backend" "app/Dockerfile" $PROJECT_ID $NAMESPACE $IMAGE_TAG
            ;;
        "data_pipeline")
            deploy_component "data_pipeline" "data_pipeline/Dockerfile" $PROJECT_ID $NAMESPACE $IMAGE_TAG
            ;;
    esac
done

echo -e "\n${GREEN}All components deployed successfully!${NC}"
echo -e "\nUseful commands to check your deployments:"
echo "----------------------------------------"
echo "Check pods status:        kubectl get pods -n $NAMESPACE"
echo "Check services:           kubectl get services -n $NAMESPACE"
echo "View pod logs:            kubectl logs -n $NAMESPACE <pod-name>"
echo "Describe deployment:      kubectl describe deployment -n $NAMESPACE"