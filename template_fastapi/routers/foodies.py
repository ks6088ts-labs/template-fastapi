from fastapi import APIRouter, HTTPException, Query

from template_fastapi.models.restaurant import Restaurant
from template_fastapi.repositories.restaurants import RestaurantRepository

router = APIRouter()
restaurant_repo = RestaurantRepository()


@router.get(
    "/foodies/restaurants/",
    response_model=list[Restaurant],
    tags=["foodies"],
    operation_id="list_foodies_restaurants",
)
async def list_foodies_restaurants(
    limit: int = Query(10, description="取得する最大件数"),
    offset: int = Query(0, description="スキップする件数（ページネーション用）"),
) -> list[Restaurant]:
    """
    レストラン一覧を取得する（ページネーション対応）
    """
    try:
        return restaurant_repo.list_restaurants(limit, offset)
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
        return restaurant_repo.get_restaurant(restaurant_id)
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
        return restaurant_repo.create_restaurant(restaurant)
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
        try:
            return restaurant_repo.update_restaurant(restaurant_id, restaurant)
        except Exception as e:
            if "Resource with specified id does not exist" in str(e):
                raise HTTPException(status_code=404, detail=f"ID {restaurant_id} のレストランが見つかりません")
            raise
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
        restaurant_repo.delete_restaurant(restaurant_id)
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
        return restaurant_repo.search_restaurants(query, k)
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
        return restaurant_repo.find_nearby_restaurants(latitude, longitude, distance_km, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"位置検索に失敗しました: {str(e)}")
