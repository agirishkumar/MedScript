## Steps for setting up GCP on ubuntu terminal:

- Add the Cloud SDK distribution URI as a package source
`echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list`

- Import the Google Cloud public key
`curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -`

- Update and install the Cloud SDK
`sudo apt-get update && sudo apt-get install google-cloud-sdk`

- initialize the SDK:
`gcloud init`

login with google account, select the project

- verify the configuration:
`gcloud config list`


## clone repo from github:
- `gh repo clone agirishkumar/MedScript`
- create and activate virtual envionment 'MedEnv'.
`python3 -m venv MedEnv`
`source MedEnv/bin/activate`

## install fastapi, uvicorn, sqlalchemy

`pip3 install 'fastapi[standard]' 'uvicorn[standard]' sqlalchemy`

## To run and check the app
`python3 -m uvicorn app.main:app --reload`

- check the urls `http://127.0.0.1:8000`, `http://127.0.0.1:8000/api/v1/health`,

## Install and start the Cloud SQL Proxy in terminal
- `wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy`
- `chmod +x cloud_sql_proxy`
- `./cloud_sql_proxy -instances=medscript-437117:us-east4:medscript-db-1=tcp:5432` # change the port number if 5432 is already in use (5433).
- Connect to the database using psql: `psql -h localhost -p 5433 -U <username> -d medcript` and enter the password.

postgres=> CREATE DATABASE medscript;
CREATE DATABASE
postgres=> \list
postgres=> GRANT ALL PRIVILEGES ON DATABASE medscript TO "dev-girish";
GRANT