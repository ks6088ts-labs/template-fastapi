import uuid

from azure.cosmos import CosmosClient
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from template_fastapi.models.restaurant import Restaurant
from template_fastapi.settings.azure_cosmosdb import get_azure_cosmosdb_settings
from template_fastapi.settings.azure_openai import get_azure_openai_settings

# 設定の取得
azure_cosmosdb_settings = get_azure_cosmosdb_settings()
azure_openai_settings = get_azure_openai_settings()


class RestaurantRepository:
    """レストランデータを管理するリポジトリクラス"""

    def __init__(self):
        self._container = None

    @property
    def container(self):
        """コンテナを遅延初期化するプロパティ"""
        if self._container is None:
            self._container = self._setup_cosmos_client()
        return self._container

    def _setup_cosmos_client(self):
        """Azure Cosmos DBに接続するクライアントを設定する"""
        client = CosmosClient.from_connection_string(azure_cosmosdb_settings.azure_cosmosdb_connection_string)
        db = client.get_database_client(azure_cosmosdb_settings.azure_cosmosdb_database_name)
        container = db.get_container_client(azure_cosmosdb_settings.azure_cosmosdb_container_name)
        return container

    def _get_embeddings(self, text: str) -> list[float]:
        """Azure OpenAIを使用してテキストのベクトル埋め込みを生成する"""
        embedding_model = AzureOpenAIEmbeddings(
            azure_endpoint=azure_openai_settings.azure_openai_endpoint,
            api_key=azure_openai_settings.azure_openai_api_key,
            azure_deployment=azure_openai_settings.azure_openai_model_embedding,
            api_version=azure_openai_settings.azure_openai_api_version,
        )

        document = Document(page_content=text)
        embedding = embedding_model.embed_documents([document.page_content])[0]
        return embedding

    def _cosmos_item_to_restaurant(self, item: dict) -> Restaurant:
        """CosmosDBのアイテムをRestaurantモデルに変換する"""
        # 位置情報の取り出し
        latitude = None
        longitude = None
        if "location" in item and "coordinates" in item["location"]:
            longitude, latitude = item["location"]["coordinates"]

        return Restaurant(
            id=item.get("id"),
            name=item.get("name"),
            description=item.get("description"),
            price=float(item.get("price", 0)),
            latitude=latitude,
            longitude=longitude,
            tags=item.get("tags", []),
        )

    def list_restaurants(self, limit: int = 10, offset: int = 0) -> list[Restaurant]:
        """レストラン一覧を取得する（ページネーション対応）"""
        query = f"SELECT * FROM c OFFSET {offset} LIMIT {limit}"
        items = list(self.container.query_items(query=query, enable_cross_partition_query=True))
        return [self._cosmos_item_to_restaurant(item) for item in items]

    def get_restaurant(self, restaurant_id: str) -> Restaurant:
        """指定されたIDのレストラン情報を取得する"""
        item = self.container.read_item(item=restaurant_id, partition_key=restaurant_id)
        return self._cosmos_item_to_restaurant(item)

    def create_restaurant(self, restaurant: Restaurant) -> Restaurant:
        """新しいレストランを作成する"""
        # IDが指定されていない場合は自動生成
        if not restaurant.id:
            restaurant.id = str(uuid.uuid4())

        # ベクトル埋め込みの生成
        description = restaurant.description or restaurant.name
        vector_embedding = self._get_embeddings(description)

        # 位置情報の構築
        location = None
        if restaurant.latitude is not None and restaurant.longitude is not None:
            location = {"type": "Point", "coordinates": [restaurant.longitude, restaurant.latitude]}

        # CosmosDBに保存するアイテムの作成
        item = {
            "id": restaurant.id,
            "name": restaurant.name,
            "description": restaurant.description,
            "price": restaurant.price,
            "tags": restaurant.tags,
            "vector": vector_embedding,
        }

        if location:
            item["location"] = location

        # CosmosDBに保存
        created_item = self.container.create_item(body=item)
        return self._cosmos_item_to_restaurant(created_item)

    def update_restaurant(self, restaurant_id: str, restaurant: Restaurant) -> Restaurant:
        """既存のレストラン情報を更新する"""
        # 既存のアイテムを取得
        existing_item = self.container.read_item(item=restaurant_id, partition_key=restaurant_id)

        # 説明文が変更された場合、新しいベクトル埋め込みを生成
        description = restaurant.description or restaurant.name
        if description != (existing_item.get("description") or existing_item.get("name")):
            vector_embedding = self._get_embeddings(description)
        else:
            vector_embedding = existing_item.get("vector")

        # 位置情報の構築
        location = None
        if restaurant.latitude is not None and restaurant.longitude is not None:
            location = {"type": "Point", "coordinates": [restaurant.longitude, restaurant.latitude]}

        # 更新するアイテムの作成
        updated_item = {
            "id": restaurant_id,
            "name": restaurant.name,
            "description": restaurant.description,
            "price": restaurant.price,
            "tags": restaurant.tags,
            "vector": vector_embedding,
        }

        if location:
            updated_item["location"] = location

        # CosmosDBのアイテムを更新
        result = self.container.replace_item(item=restaurant_id, body=updated_item)
        return self._cosmos_item_to_restaurant(result)

    def delete_restaurant(self, restaurant_id: str) -> None:
        """指定されたIDのレストランを削除する"""
        self.container.delete_item(item=restaurant_id, partition_key=restaurant_id)

    def search_restaurants(self, query: str, k: int = 3, offset: int = 0) -> list[Restaurant]:
        """キーワードによるレストランのベクトル検索を実行する（ページネーション対応）"""
        # クエリテキストのベクトル埋め込みを生成
        query_embedding = self._get_embeddings(query)

        # ベクトル検索クエリの実行（オフセットとリミットを適用）
        query_text = f"""
        SELECT *
        FROM c
        ORDER BY VectorDistance(c.vector, @queryVector)
        OFFSET {offset} LIMIT {k}
        """

        parameters = [{"name": "@queryVector", "value": query_embedding}]
        items = list(
            self.container.query_items(query=query_text, parameters=parameters, enable_cross_partition_query=True)
        )
        return [self._cosmos_item_to_restaurant(item) for item in items]

    def find_nearby_restaurants(
        self, latitude: float, longitude: float, distance_km: float = 5.0, limit: int = 10, offset: int = 0
    ) -> list[Restaurant]:
        """指定した位置の近くにあるレストランを検索する（ページネーション対応）"""
        # 地理空間クエリの実行（メートル単位で距離を指定）
        distance_meters = distance_km * 1000
        query_text = f"""
        SELECT *
        FROM c
        WHERE ST_DISTANCE(c.location, {{
            "type": "Point",
            "coordinates": [{longitude}, {latitude}]
        }}) < {distance_meters}
        OFFSET {offset} LIMIT {limit}
        """

        items = list(self.container.query_items(query=query_text, enable_cross_partition_query=True))
        return [self._cosmos_item_to_restaurant(item) for item in items]
