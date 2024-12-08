### Deployment Service

### Frontend Deployment Pipeline Overview
Workflow: .github/workflows/deploy-to-cloud-run.yml
The CI/CD pipeline automates the deployment of the Streamlit application to Google Cloud Platform (GCP). Here's an overview of the steps:

1. **Trigger on Push**:
   - The pipeline is triggered when changes are pushed to the `UI/` directory in the `dev` or `main` branches.

2. **Authenticate with Google Cloud**:
   - The pipeline uses a service account key stored in GitHub Secrets to authenticate with GCP.

3. **Build and Push Docker Image**:
   - The pipeline builds a Docker image for the Streamlit application using the `Dockerfile` in the `UI/` directory.
   - The Docker image is tagged and pushed to **Google Artifact Registry** under the repository `us-docker.pkg.dev/project_id/gcr.io/medscript-app`.

4. **Deploy to Cloud Run**:
   - The Docker image is deployed to **Cloud Run**, which provides a managed, scalable environment to host the Streamlit app.
   - The application is exposed to the internet and configured to allow unauthenticated access.
   <img width="1280" alt="image" src="https://github.com/user-attachments/assets/1a788151-2e13-48bb-a0c9-8f1248df92f0">

This pipeline ensures that any updates to the `UI/` directory in the specified branches are automatically deployed to the production environment.

### Slack Alert Notification Integration

We’ve integrated Slack alert notifications into the deployment pipeline to keep developers informed about deployment failures. If a deployment fails, an alert is sent to a specified Slack channel with details including the branch, commit and author. Slack notifications are triggered through a webhook and provide real-time information about the deployment status. Screenshot of sample notification is below:
<img width="1280" alt="Screenshot 2024-12-03 at 6 37 47 PM" src="https://github.com/user-attachments/assets/ca66cb1f-8871-4695-89b6-52db59ccdbe9">
