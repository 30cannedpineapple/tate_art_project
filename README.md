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