# Osusume (Product Recommendation Engine)

## Overview

This project implements a product recommendation engine using Google Cloud's Vertex AI and BigQuery. The system analyzes user purchase history to provide personalized product recommendations.

## Prerequisites

Before running this application, ensure you have:

1. A Google Cloud Platform account with billing enabled
2. The following APIs enabled in your GCP project:
   - BigQuery API
   - Vertex AI API
3. Docker installed on your local machine
4. Python 3.9 or higher installed (for local development)

## Setup

### BigQuery Setup

1. Create a new dataset in BigQuery:
   ```
   bq mk --dataset your_project_id:osusume_dataset
   ```

2. Create a table in the dataset:
   ```
   bq mk --table your_project_id:osusume_dataset.purchase_history user_id:STRING,product_id:STRING,category:STRING,price:FLOAT,season:STRING,purchased:BOOLEAN
   ```

3. Load the CSV data into the table:
   ```
   bq load --source_format=CSV your_project_id:osusume_dataset.purchase_history path/to/your/product_interactions.csv
   ```

### Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```
PROJECT_ID=your_project_id
LOCATION=us-central1  # or your preferred region
BQ_DATASET=osusume_dataset
BQ_TABLE_NAME=purchase_history
```

### Google Cloud Authentication

1. Create a service account key file and download it as `secret.json`.
2. Place `secret.json` in the root directory of the project.

### Docker Setup

1. Ensure Docker is installed and running on your machine.
2. Build the Docker image:
   ```
   docker-compose build
   ```

## Running the Application

1. Start the application using Docker Compose:
   ```
   docker-compose up
   ```

2. When prompted, enter a user ID to get product recommendations.

3. Type 'quit' to exit the application.

4. To stop the container, press Ctrl+C or run:
   ```
   docker-compose down
   ```

## How It Works

1. The script first trains and deploys a machine learning model using Vertex AI AutoML Tables.
2. It then uses this model to predict product recommendations for a given user.
3. The recommendations are based on the user's purchase history and the likelihood of purchasing other products.

## Project Structure

- `main.py`: The main Python script containing the recommendation engine logic.
- `Dockerfile`: Defines the Docker image for the application.
- `docker-compose.yml`: Defines the services and configuration for running the application.
- `requirements.txt`: Lists the Python dependencies for the project.
- `.env`: Contains environment variables (do not commit this file to version control).
- `secret.json`: Google Cloud service account key (do not commit this file to version control).

## Notes

- The first run may take some time as it needs to train and deploy the model.
- Ensure you have sufficient quota in your GCP project for Vertex AI and BigQuery operations.
- The model is trained only once per session. For production use, consider implementing a more robust model management system.

## Customization

You can modify the `column_specs` in the `train_and_deploy_model` function in `main.py` to adjust how each column is treated in the model training process.

## Cleanup

Remember to delete your Vertex AI endpoint and BigQuery resources when you're done to avoid unnecessary charges.
