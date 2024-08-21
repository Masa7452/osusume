import os
from google.cloud import bigquery
from google.cloud import aiplatform

bq_client = bigquery.Client()

BQ_DATASET = os.getenv('BQ_DATASET')
BQ_TABLE_NAME = os.getenv('BQ_TABLE_NAME')
MODEL_ENDPOINT_NAME = os.getenv('MODEL_ENDPOINT_NAME')
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION')

aiplatform.init(project=PROJECT_ID, location=LOCATION)

ENDPOINT = None


def get_existing_endpoint():
    """Search for and return an existing endpoint"""
    endpoints = aiplatform.Endpoint.list()
    for endpoint in endpoints:
        if endpoint.display_name == MODEL_ENDPOINT_NAME:
            print(f"Existing endpoint found: {endpoint.resource_name}")
            return endpoint
    return None


def create_dataset():
    """Create a BigQuery dataset"""
    bq_uri = f"bq://{bq_client.project}.{BQ_DATASET}.{BQ_TABLE_NAME}"
    dataset = aiplatform.TabularDataset.create(
        display_name="osusume",
        bq_source=bq_uri
    )
    print('Dataset creation completed')
    return dataset


def train_model(dataset):
    """Train the model"""
    job = aiplatform.AutoMLTabularTrainingJob(
        display_name="osusume_model",
        optimization_prediction_type="classification",
        optimization_objective="maximize-au-roc",
        column_specs={
            "user_id": "categorical",
            "product_id": "categorical",
            "category": "categorical",
            "price": "numeric",
            "season": "categorical",
            "purchased": "categorical"
        },
    )

    model = job.run(
        dataset=dataset,
        target_column="purchased",
        budget_milli_node_hours=1000,
    )
    return model


def deploy_model(model):
    """Deploy the model"""
    endpoint = model.deploy(
        machine_type="n1-standard-4",
        min_replica_count=1,
        max_replica_count=1,
        display_name="osusume_endpoint"
    )
    print(f"New model deployed. Endpoint name: {endpoint.resource_name}")
    return endpoint


def get_or_create_endpoint():
    """Get an existing endpoint or create a new one"""
    global ENDPOINT

    if ENDPOINT:
        print("Using existing endpoint.")
        return ENDPOINT

    ENDPOINT = get_existing_endpoint()
    if ENDPOINT:
        return ENDPOINT

    print("No existing endpoint found. Training and deploying a new model.")
    dataset = create_dataset()
    model = train_model(dataset)
    ENDPOINT = deploy_model(model)

    return ENDPOINT


def get_recommendations(user_id):
    """Get product recommendations for a user"""
    global ENDPOINT

    if not ENDPOINT:
        print("Error: Endpoint is not set.")
        return []

    query = f"""
    SELECT DISTINCT product_id, category, price, season
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE_NAME}`
    WHERE user_id = {user_id} AND purchased = 1
    """
    query_job = bq_client.query(query)
    results = query_job.result()

    purchased_products = [row['product_id'] for row in results]

    query = f"""
    SELECT DISTINCT product_id, category, price, season
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE_NAME}`
    """
    query_job = bq_client.query(query)
    results = query_job.result()

    all_products = [(row['product_id'], row['category'], row['price'], row['season']) for row in results]

    unpurchased_products = [product for product in all_products if product[0] not in purchased_products]

    predictions = ENDPOINT.predict([
        {'user_id': user_id, 'product_id': product[0], 'category': product[1], 'price': product[2], 'season': product[3]}
        for product in unpurchased_products
    ])

    print('未購入商品')
    print(unpurchased_products)
    print('予測結果')
    print(predictions)
    print('========')
    print(predictions.predictions)

    recommended_products = sorted(
        zip(unpurchased_products, predictions.predictions),
        key=lambda x: x[1][1],
        reverse=True
    )

    return recommended_products[:5]  # Return top 5 products


def main():
    print("Starting the product recommendation system...")

    get_or_create_endpoint()

    print("Enter a user ID (or 'quit' to exit):")
    while True:
        user_id = input().strip()

        if user_id.lower() == 'quit':
            print("Exiting the application.")
            break

        recommendations = get_recommendations(user_id)

        if recommendations:
            print(f"\nRecommended products for user {user_id}:")
            for product, score in recommendations:
                print(f"Product ID: {product[0]}, Category: {product[1]}, Price: {product[2]}, Season: {product[3]}, Score: {score[1]:.2f}")
        else:
            print(f"No recommendations for user {user_id}.")

        print("\nEnter the next user ID (or 'quit' to exit):")


if __name__ == "__main__":
    main()
