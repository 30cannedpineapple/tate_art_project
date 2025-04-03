# Tate Art Project
Musuems collect thousands of artwork pieces of variance forms, artists, and periods. For this project, I try to analyze the artwork data from Tate Gallery and create a dashboard for insights on the artworks and artists. For the project, artwork and artist data are ingested from Tate Github into GCP bucket by Airflow and then transformed into BigQuery datasets by dbt. Based on the BigQuery datasets, a dashboard is created in Looker Studio.

## About Tate
[Tate Gallery](https://www.tate.org.uk/) is a collection of 4 art galleries in the United Kingdom. It includes Tate Britain, Tate Modern, Tate Liverpool, and Tate St ives. It houses collections of British art and international modern and contemporary art.

## Dataset
[Artwork and Artist data csv files](https://github.com/tategallery/collection/tree/master) from the Tate GitHub repository. It includes around 70,000 artworks and 4,000 artists data.

## Technology
- Infrastructure as Code: Terraform
- Workflor Management: Airflow
- Data Lake: Google Cloud Storage
- Data Warehouse: Google BigQuery
- Data Transformation: dbt
- Dashboard: Looker Studio

## Architecture
![Architecture](/images/architecture.png)

# Reproduce the repo

## Local setup
Install the following:
- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Cloud setup
In GCP, create a service principal with the following permissions:
* Compute Admin
* BigQuery Admin
* Storage Admin

Download the authentication json file and save it as `~/.google/credentials/google_credentials.json`.

## Initializing Infrastructure (Terraform)
Update the `variable.tf` file under `Terraform` folder to your setup variables including credentials and project (your GCP Project ID). Region, location, bucket name, and dataset name can be kept the same. 

Set up the cloud infrastructure using Terraform
```shell
cd terraform
terraform init
terraform plan
terraform apply

cd ..
```

## Data Ingestion
Update the `docker-compose.yaml` file under `Airflow` folder. GCP_PROJECT_ID and GCP_GCS_BUCKET should be updated.

Set up airflow to perform data ingestion
```shell
cd airflow

docker compose build
docker compose up airflow-init
docker compose up -d
```

* After the Airflow set up is complete (could take a while), go to Airflow Web UI `localhost:8080` log in with creadentials: Username airflow and Password airflow. 
* Select data_ingestion_gcs_dag. Then click on the play button on the top right and select "Trigger DAG".
![](/images/airflow.png)
* This dag will download the artwork and artist csv files from GitHub, clean up the data with Python, and then upload into Google Cloud Storage bucket.
* After the dag finishes running, turn off Airflow.
```shell
docker compose down
cd ..
```

## Data Transformation
Update the `docker-compose.yaml` file under `dbt` folder. Paths under Volumes need to be updated.

* Go to dbt folder and run the dbt project
```shell
cd dbt
docker compose up -d
docker compose run dbt-bq-dtc deps
docker compose run dbt-bq-dtc build --vars '{"is_test_run": false}'
docker compose down
cd ..
```
* The transformed data will be saved as a BigQuery table `artist_artwork_table` under `tate_data_all` dataset.

## Dashboard
The Dashboard is built in Looker Studio based on the BigQuery table. 
[Dashboard Link](https://lookerstudio.google.com/reporting/fcc8c293-9338-4b47-983d-f301bb264b37)
![Dashboard Screenshot](/images/dashboard.png)
The views show:
* The most popular medium of the artworks is Graphite on paper.
* More than 3,000 artworks were collected by the museum when they had been created for 37 years.
* Tate has collected more than 33,000 artworks by [J. M. W. Turner](https://en.wikipedia.org/wiki/J._M._W._Turner), the largest number by any artist in its collection.
