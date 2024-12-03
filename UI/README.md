## Pipeline Overview

The CI/CD pipeline automates the deployment of the Streamlit application to Google Cloud Platform (GCP). Here's an overview of the steps:

1. **Trigger on Push**:
   - The pipeline is triggered when changes are pushed to the `UI/` directory in the `feature/UI-deploy`, `dev`, or `main` branches.

2. **Authenticate with Google Cloud**:
   - The pipeline uses a service account key stored in GitHub Secrets to authenticate with GCP.

3. **Build and Push Docker Image**:
   - The pipeline builds a Docker image for the Streamlit application using the `Dockerfile` in the `UI/` directory.
   - The Docker image is tagged and pushed to **Google Artifact Registry** under the repository `us-docker.pkg.dev/medscript-437117/gcr.io/streamlit-app`.

4. **Deploy to Cloud Run**:
   - The Docker image is deployed to **Cloud Run**, which provides a managed, scalable environment to host the Streamlit app.
   - The application is exposed to the internet and configured to allow unauthenticated access.

This pipeline ensures that any updates to the `UI/` directory in the specified branches are automatically deployed to the production environment.
