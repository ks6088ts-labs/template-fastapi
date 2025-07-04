import uuid

from azure.cosmos import CosmosClient
from fastapi import APIRouter, HTTPException, Query
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from template_fastapi.models.restaurant import Restaurant
from template_fastapi.settings.azure_cosmosdb import get_azure_cosmosdb_settings
from template_fastapi.settings.azure_openai import get_azure_openai_settings

router = APIRouter()
azure_cosmosdb_settings = get_azure_cosmosdb_settings()
azure_openai_settings = get_azure_openai_settings()


def setup_cosmos_client():
    """Azure Cosmos DBに接続するクライアントを設定する"""
    client = CosmosClient.from_connection_string(azure_cosmosdb_settings.azure_cosmosdb_connection_string)
    db = client.get_database_client(azure_cosmosdb_settings.azure_cosmosdb_database_name)
    container = db.get_container_client(azure_cosmosdb_settings.azure_cosmosdb_container_name)
    return container


def get_embeddings(text: str) -> list[float]:
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


def cosmos_item_to_restaurant(item: dict) -> Restaurant:
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


@router.get(
    "/foodies/restaurants/",
    response_model=list[Restaurant],
    tags=["foodies"],
    operation_id="list_foodies_restaurants",
)
async def list_foodies_restaurants(limit: int = Query(10, description="取得する最大件数")) -> list[Restaurant]:
    """
    レストラン一覧を取得する
    """
    try:
        container = setup_cosmos_client()
        query = f"SELECT TOP {limit} * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        return [cosmos_item_to_restaurant(item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データの取得に失敗しました: {str(e)}")


@router.get(
    "/foodies/restaurants/{restaurant_id}",
    response_model=Restaurant,
    tags=["foodies"],
    operation_id="get_foodies_restaurant",
)
async def get_foodies_restaurant(restaurant_id: str) -> Restaurant:
    """
    指定されたIDのレストラン情報を取得する
    """
    try:
        container = setup_cosmos_client()
        item = container.read_item(item=restaurant_id, partition_key=restaurant_id)
        return cosmos_item_to_restaurant(item)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"ID {restaurant_id} のレストランが見つかりません: {str(e)}")


@router.post(
    "/foodies/restaurants/",
    response_model=Restaurant,
    tags=["foodies"],
    operation_id="create_foodies_restaurant",
)
async def create_foodies_restaurant(restaurant: Restaurant) -> Restaurant:
    """
    新しいレストランを作成する
    """
    try:
        container = setup_cosmos_client()

        # IDが指定されていない場合は自動生成
        if not restaurant.id:
            restaurant.id = str(uuid.uuid4())

        # ベクトル埋め込みの生成
        description = restaurant.description or restaurant.name
        vector_embedding = get_embeddings(description)

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
        created_item = container.create_item(body=item)

        return cosmos_item_to_restaurant(created_item)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レストランの作成に失敗しました: {str(e)}")


@router.put(
    "/foodies/restaurants/{restaurant_id}",
    response_model=Restaurant,
    tags=["foodies"],
    operation_id="update_foodies_restaurant",
)
async def update_foodies_restaurant(restaurant_id: str, restaurant: Restaurant) -> Restaurant:
    """
    既存のレストラン情報を更新する
    """
    try:
        container = setup_cosmos_client()

        # 既存のアイテムを取得
        try:
            existing_item = container.read_item(item=restaurant_id, partition_key=restaurant_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"ID {restaurant_id} のレストランが見つかりません")

        # 説明文が変更された場合、新しいベクトル埋め込みを生成
        description = restaurant.description or restaurant.name
        if description != (existing_item.get("description") or existing_item.get("name")):
            vector_embedding = get_embeddings(description)
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
        result = container.replace_item(item=restaurant_id, body=updated_item)

        return cosmos_item_to_restaurant(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レストランの更新に失敗しました: {str(e)}")


@router.delete(
    "/foodies/restaurants/{restaurant_id}",
    tags=["foodies"],
    operation_id="delete_foodies_restaurant",
)
async def delete_foodies_restaurant(restaurant_id: str) -> dict:
    """
    指定されたIDのレストランを削除する
    """
    try:
        container = setup_cosmos_client()
        container.delete_item(item=restaurant_id, partition_key=restaurant_id)
        return {"message": f"ID {restaurant_id} のレストランを削除しました"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"ID {restaurant_id} のレストランの削除に失敗しました: {str(e)}")


@router.get(
    "/foodies/restaurants/search/",
    response_model=list[Restaurant],
    tags=["foodies"],
    operation_id="search_foodies_restaurants",
)
async def search_foodies_restaurants(
    query: str, k: int = Query(3, description="取得する上位結果の数")
) -> list[Restaurant]:
    """
    キーワードによるレストランのベクトル検索を実行する
    """
    try:
        # クエリテキストのベクトル埋め込みを生成
        query_embedding = get_embeddings(query)

        # CosmosDBに接続
        container = setup_cosmos_client()

        # ベクトル検索クエリの実行
        query_text = f"""
        SELECT TOP {k} *
        FROM c
        ORDER BY VectorDistance(c.vector, @queryVector)
        """

        parameters = [{"name": "@queryVector", "value": query_embedding}]

        items = list(container.query_items(query=query_text, parameters=parameters, enable_cross_partition_query=True))

        return [cosmos_item_to_restaurant(item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索に失敗しました: {str(e)}")


@router.get(
    "/foodies/restaurants/near/",
    response_model=list[Restaurant],
    tags=["foodies"],
    operation_id="find_nearby_restaurants",
)
async def find_nearby_restaurants(
    latitude: float = Query(..., description="緯度"),
    longitude: float = Query(..., description="経度"),
    distance_km: float = Query(5.0, description="検索半径（キロメートル）"),
    limit: int = Query(10, description="取得する最大件数"),
) -> list[Restaurant]:
    """
    指定した位置の近くにあるレストランを検索する
    """
    try:
        container = setup_cosmos_client()

        # 地理空間クエリの実行（メートル単位で距離を指定）
        distance_meters = distance_km * 1000
        query_text = f"""
        SELECT TOP {limit} *
        FROM c
        WHERE ST_DISTANCE(c.location, {{
            "type": "Point",
            "coordinates": [{longitude}, {latitude}]
        }}) < {distance_meters}
        """

        items = list(container.query_items(query=query_text, enable_cross_partition_query=True))

        return [cosmos_item_to_restaurant(item) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"位置検索に失敗しました: {str(e)}")
