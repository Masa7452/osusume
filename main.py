import os
from google.cloud import bigquery
from google.cloud import aiplatform

# BigQuery クライアントの初期化
bq_client = bigquery.Client()

BQ_DATASET = os.getenv('BQ_DATASET')
BQ_TABLE_NAME = os.getenv('BQ_TABLE_NAME')
PROJECT_ID = os.getenv('PROJECT_ID')
LOCATION = os.getenv('LOCATION')

# Vertex AI の初期化
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# グローバル変数としてエンドポイント名を保持
ENDPOINT_NAME = None


def train_and_deploy_model():
    global ENDPOINT_NAME

    if ENDPOINT_NAME:
        print("モデルは既にデプロイされています。")
        return

    print("モデルのトレーニングとデプロイを開始します...")

    bq_uri = f"bq://{bq_client.project}.{BQ_DATASET}.{BQ_TABLE_NAME}"
    dataset = aiplatform.TabularDataset.create(
        display_name="osusume",
        bq_source=bq_uri
    )
    print('データセット作成完了')

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

    # モデルをデプロイ
    endpoint = model.deploy(
        machine_type="n1-standard-4",
        min_replica_count=1,
        max_replica_count=1
    )

    ENDPOINT_NAME = endpoint.resource_name
    print(f"モデルがデプロイされました。エンドポイント名: {ENDPOINT_NAME}")


def get_recommendations(user_id):
    global ENDPOINT_NAME

    if not ENDPOINT_NAME:
        print("エラー: モデルがデプロイされていません。")
        return []

    # BigQuery からユーザーの購買履歴を取得
    query = f"""
    SELECT DISTINCT product_id, category, price, season
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE_NAME}`
    WHERE user_id = '{user_id}' AND purchased = 1
    """
    query_job = bq_client.query(query)
    results = query_job.result()

    purchased_products = [row['product_id'] for row in results]

    # 全商品リストを取得
    query = f"""
    SELECT DISTINCT product_id, category, price, season
    FROM `{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE_NAME}`
    """
    query_job = bq_client.query(query)
    results = query_job.result()

    all_products = [(row['product_id'], row['category'], row['price'], row['season']) for row in results]

    # 未購入の商品を抽出
    unpurchased_products = [product for product in all_products if product[0] not in purchased_products]

    # モデルを使って推薦スコアを計算
    endpoint = aiplatform.Endpoint(ENDPOINT_NAME)

    predictions = endpoint.predict([
        {'user_id': user_id, 'product_id': product[0], 'category': product[1], 'price': product[2], 'season': product[3]}
        for product in unpurchased_products
    ])

    # スコアの高い順に商品をソート
    recommended_products = sorted(
        zip(unpurchased_products, predictions.predictions),
        key=lambda x: x[1][1],  # positive class probability
        reverse=True
    )

    return recommended_products[:5]  # 上位5つの商品を返す


def main():
    print("商品推薦システムを起動します...")
    train_and_deploy_model()

    print("ユーザーIDを入力してください（終了するには 'quit' と入力）:")
    while True:
        user_id = input().strip()

        if user_id.lower() == 'quit':
            print("アプリケーションを終了します。")
            break

        recommendations = get_recommendations(user_id)

        if recommendations:
            print(f"\nユーザー {user_id} へのおすすめ商品:")
            for product, score in recommendations:
                print(f"商品ID: {product[0]}, カテゴリー: {product[1]}, 価格: {product[2]}, 季節: {product[3]}, スコア: {score[1]:.2f}")
        else:
            print(f"ユーザー {user_id} への推薦商品はありません。")

        print("\n次のユーザーIDを入力してください（終了するには 'quit' と入力）:")


if __name__ == "__main__":
    main()
