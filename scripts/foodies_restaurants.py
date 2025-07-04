#!/usr/bin/env python
# filepath: /Users/ks6088ts/src/github.com/ks6088ts-labs/template-fastapi/scripts/foodies_restaurant.py

import csv

import typer
from azure.cosmos import CosmosClient, PartitionKey
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings
from rich.console import Console

from template_fastapi.settings.azure_cosmosdb import get_azure_cosmosdb_settings
from template_fastapi.settings.azure_openai import get_azure_openai_settings

app = typer.Typer()
console = Console()


def read_csv_data(file_path: str) -> list[dict]:
    """CSVファイルからレストランデータを読み込む"""
    restaurants = []
    with open(file_path, encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # タグをリストに変換
            tags = row["tags"].strip('"').split(",")
            restaurant = {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "price": int(row["price"]),
                "location": {
                    "type": "Point",
                    "coordinates": [float(row["longitude"]), float(row["latitude"])],
                },
                "tags": tags,
            }
            restaurants.append(restaurant)
    return restaurants


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Azure OpenAIを使用してテキストのベクトル埋め込みを生成する"""
    settings = get_azure_openai_settings()
    embedding_model = AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        azure_deployment=settings.azure_openai_model_embedding,
        api_version=settings.azure_openai_api_version,
    )

    documents = [Document(page_content=text) for text in texts]
    embeddings = embedding_model.embed_documents([doc.page_content for doc in documents])
    return embeddings


def setup_cosmos_db():
    """Azure Cosmos DBのセットアップと接続"""
    settings = get_azure_cosmosdb_settings()
    client = CosmosClient.from_connection_string(settings.azure_cosmosdb_connection_string)

    # データベースが存在しなければ作成
    db = client.create_database_if_not_exists(id=settings.azure_cosmosdb_database_name)

    # コンテナが存在しなければ作成（ベクトル検索用インデックスポリシー付き）
    indexing_policy = {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        "excludedPaths": [{"path": "/vector/*"}],
        "vectorIndexes": [
            {
                "path": "/vector",
                "type": "cosine",
                "numDimensions": 1536,  # OpenAI Embedding modelのデフォルトサイズ
                "vectorSearchConfiguration": "vectorConfig",
            }
        ],
    }

    container = db.create_container_if_not_exists(
        id=settings.azure_cosmosdb_container_name,
        partition_key=PartitionKey(path="/id"),
        indexing_policy=indexing_policy,
    )

    return container


@app.command()
def import_data(
    csv_file: str = typer.Option(..., "--csv-file", "-f", help="CSVファイルのパス"),
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="一度に処理するバッチサイズ"),
):
    """CSVからデータをCosmosDBにインポートしてベクトル検索を設定する"""
    console.print(f"[bold green]CSVファイル[/bold green]: {csv_file}からデータを読み込みます")

    # CSVデータの読み込み
    restaurants = read_csv_data(csv_file)
    console.print(f"[bold blue]{len(restaurants)}件[/bold blue]のレストランデータを読み込みました")

    # 説明文を抽出してベクトル埋め込みを生成
    descriptions = [restaurant["description"] for restaurant in restaurants]
    console.print("[bold yellow]説明文のベクトル埋め込みを生成しています...[/bold yellow]")
    embeddings = get_embeddings(descriptions)

    # Cosmos DBのセットアップ
    container = setup_cosmos_db()
    console.print(f"[bold green]Cosmos DBのコンテナ[/bold green]: {container.id}に接続しました")

    # データの登録
    console.print("[bold yellow]レストランデータをCosmosDBに登録しています...[/bold yellow]")
    for i, restaurant in enumerate(restaurants):
        # ベクトルデータを追加
        restaurant["vector"] = embeddings[i]

        # UpsertによりCosmosDBに登録
        container.upsert_item(body=restaurant)

        console.print(f"ID: {restaurant['id']} - {restaurant['name']}を登録しました")

    console.print("[bold green]すべてのデータが正常に登録されました！[/bold green]")


@app.command()
def search(
    query: str = typer.Option(..., "--query", "-q", help="検索クエリ"),
    k: int = typer.Option(3, "--top-k", "-k", help="取得する上位結果の数"),
):
    """説明文のベクトル検索を実行する"""
    console.print(f"[bold green]クエリ[/bold green]: '{query}'で検索します")

    # クエリテキストのベクトル埋め込みを生成
    query_embedding = get_embeddings([query])[0]

    # Cosmos DBに接続
    container = setup_cosmos_db()

    # ベクトル検索クエリの実行
    query_text = f"""
    SELECT TOP {k} r.id, r.name, r.description, r.price, r.tags
    FROM restaurants r
    ORDER BY VectorDistance(r.vector, @queryVector)
    """

    parameters = [{"name": "@queryVector", "value": query_embedding}]

    items = list(container.query_items(query=query_text, parameters=parameters, enable_cross_partition_query=True))

    # 結果の表示
    console.print(f"\n[bold blue]{len(items)}件[/bold blue]の検索結果:")
    for i, item in enumerate(items):
        console.print(f"\n[bold]{i + 1}. {item['name']}[/bold]")
        console.print(f"   説明: {item['description']}")
        console.print(f"   価格: ¥{item['price']}")
        console.print(f"   タグ: {', '.join(item['tags'])}")

    return items


if __name__ == "__main__":
    app()
