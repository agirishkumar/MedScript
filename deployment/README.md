### Deployment to GKE

### 1. Accessing the Cluster

- Set up and configure gcloud CLI, kubectl
```bash
# verify kubectl is installed
kubectl version --client
```

- To authenticate and communicate with GKE clusters, kubectl requires the authenticate plugin - 
gke-gcloud-auth-plugin

```bash
  gcloud components install gke-gcloud-auth-plugin

  # verify the plugin is installed
  gke-gcloud-auth-plugin --version
```

- To get credentials for the cluster and interact with it using kubectl, run: 

```bash
gcloud container clusters get-credentials [CLUSTER-NAME] --region [ZONE]

gcloud container clusters get-credentials medscript-cluster-1 --region us-central1-c
```

Configure kubectl to set it to the cluster

```bash
kubectl config current-context
```


### 2. Service account and Kubernetes secrets
The service account needs to have the following permissions:
- Cloud SQL Client role
- Artifact Registry Reader 

- Create a namespace 
```bash
kubectl create namespace medscript
```

- Create Kubernetes secrets

```bash
  kubectl create secret generic gke-fastapi-secrets -n medscript \
  --from-literal=database=medscript \
  --from-literal=username=DB_USER \
  --from-literal=password=DB_PASS \
  --from-literal=jwt_secret_key=KEY \
  --from-literal=jwt_refresh_secret_key=KEY
```

```bash
kubectl create secret generic gke-airflow-secrets -n medscript \
  --from-literal=slack_webhook_url=URL
```


### 3. Build and push the docker images
- Build the docker image 

From the Medscript folder:

```bash
cd Medscript

docker build -f app/Dockerfile --platform linux/amd64 --no-cache -t medscript-backend-app:v1 .

docker build -f data_pipeline/Dockerfile -t airflow-dag-img:v1 --no-cache --platform linux/amd64 .
```


- Tag the image
```bash
docker tag medscript-backend-app:v1 gcr.io/medscript-437117/fast-api-backend:latest

docker tag data-pipeline-img:v1 gcr.io/medscript-437117/data-pipeline-img:v1     

```

 - To authenticate and push the docker image to GCR:
```bash
gcloud auth activate-service-account --key-file=/path/to/service-account-key.json
```

  - Configure docker to use the service account

```bash
gcloud auth configure-docker
```

- Push the image to GCR
```bash
docker push gcr.io/medscript-437117/fast-api-app:latest
docker push gcr.io/medscript-437117/data-pipeline-img:v1 
docker tag airflow-img:latest gcr.io/medscript-437117/airflow-dag-img:v1    
                   
```

### Deploy the FAST API application on GKE

```bash
cd deployment
kubectl apply -f backend/app-deployment.yaml
kubectl apply -f backend/app-service.yaml
```

### Deploy the data pipeline on GKE 

- Get the External IP of the backend service

```bash
kubectl get service backend-service -n medscript
```

- Update the BASE_API_URL in `deployment/data_pipeline/values.yaml`

```bash
env: 
  - name: BASE_API_URL
  - value: <EXTERNAL IP>
```

- If the airflow image is updated, update the repository in `deployment/data_pipeline/values.yaml`

```bash
images:
  airflow:
    repository: gcr.io/medscript-437117/airflow-dags
    tag: latest
```

- Install [Helm](https://helm.sh/docs/intro/install/) - it's a package manager that bundles Kubernetes applications into charts.

- Deploy with helm

```bash
helm upgrade --install airflow apache-airflow/airflow -n medscript  \
   --values data_pipeline/values.yaml \
  --debug
```