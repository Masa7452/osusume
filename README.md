# Osusume (Product Recommendation Engine)

## Overview

This project implements a product recommendation engine using Google Cloud's Vertex AI and BigQuery. The system analyzes user product interactions history to provide personalized product recommendations.

## Prerequisites

Before running this application, ensure you have:

1. A Google Cloud Platform account with billing enabled
2. The following APIs enabled in your GCP project:
   - BigQuery API
   - Vertex AI API
3. Docker installed on your local machine
4. Python 3.9 or higher installed (for local development)

## Important: Cost Considerations

**Please note that using Vertex AI and BigQuery incurs costs.** The model training and deployment process, as well as running predictions, will result in charges to your Google Cloud account. 

For detailed pricing information, please refer to the following documentation:
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)

Ensure you understand the costs involved before running this application, especially for large datasets or frequent model training.

## Setup

### BigQuery Setup

1. Create a new dataset in BigQuery:
   ```
   bq mk --dataset your_project_id:osusume_dataset
   ```

2. Create a table in the dataset:
   ```
   bq mk --table your_project_id:osusume_dataset.product_interactions user_id:STRING,product_id:STRING,category:STRING,price:FLOAT,season:STRING,purchased:BOOLEAN
   ```

3. Load the CSV data into the table:
   ```
   bq load --source_format=CSV your_project_id:osusume_dataset.product_interactions path/to/your/product_interactions.csv
   ```

### Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```
PROJECT_ID=your_project_id
LOCATION=us-central1  # or your preferred region
BQ_DATASET=osusume_dataset
BQ_TABLE_NAME=product_interactions
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
   - Input example: `12345` (assuming this is a valid user ID in your dataset)

3. The application will output recommended products for the user. 
   - Output example:
     ```
     Recommendations for user 12345:
     1. Product ID: P789, Category: Electronics, Price: $599.99, Season: Summer, Score: 0.85
     2. Product ID: P456, Category: Clothing, Price: $79.99, Season: Fall, Score: 0.72
     3. Product ID: P234, Category: Home, Price: $149.99, Season: Winter, Score: 0.68
     4. Product ID: P567, Category: Sports, Price: $89.99, Season: Spring, Score: 0.61
     5. Product ID: P890, Category: Books, Price: $24.99, Season: Summer, Score: 0.57
     ```

4. You can continue to enter different user IDs to get recommendations for other users.

5. Type 'quit' to exit the application.

6. To stop the container, press Ctrl+C or run:
   ```
   docker-compose down
   ```

## How It Works

1. The script first trains and deploys a machine learning model using Vertex AI AutoML Tables. This process may take some time, especially on the first run.
2. When you enter a user ID, the application retrieves the user's product interaction history from BigQuery.
3. The model then predicts the likelihood of the user purchasing other products they haven't interacted with yet.
4. The application returns the top 5 recommended products, sorted by the prediction score.

## Project Structure

- `main.py`: The main Python script containing the recommendation engine logic.
- `Dockerfile`: Defines the Docker image for the application.
- `docker-compose.yml`: Defines the services and configuration for running the application.
- `requirements.txt`: Lists the Python dependencies for the project.
- `.env`: Contains environment variables (do not commit this file to version control).
- `secret.json`: Google Cloud service account key (do not commit this file to version control).

## Notes

- The first run may take considerable time (potentially hours) as it needs to train and deploy the model. Subsequent runs will be faster as they use the existing model.
- Ensure you have sufficient quota in your GCP project for Vertex AI and BigQuery operations.
- The model is trained only once per session. For production use, consider implementing a more robust model management system.

## Customization

You can modify the `column_specs` in the `train_and_deploy_model` function in `main.py` to adjust how each column is treated in the model training process. Refer to the [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs/tabular-data/classification-regression/create-dataset#column-specs) for more information on column specifications.

## Cleanup

Remember to delete your Vertex AI endpoint and BigQuery resources when you're done to avoid unnecessary charges. You can do this through the Google Cloud Console or using the `gcloud` command-line tool.

## Troubleshooting

If you encounter any issues, check the following:
1. Ensure all required APIs are enabled in your Google Cloud project.
2. Verify that your `secret.json` file has the necessary permissions.
3. Check your Google Cloud project's quotas and limits.

For more detailed troubleshooting, refer to the [Vertex AI troubleshooting guide](https://cloud.google.com/vertex-ai/docs/general/troubleshooting).

