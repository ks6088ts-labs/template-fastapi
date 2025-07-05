#!/usr/bin/env python
# filepath: /Users/ks6088ts/src/github.com/ks6088ts-labs/template-fastapi/scripts/foodies_restaurants.py

import csv

import typer
from rich.console import Console

from template_fastapi.models.restaurant import Restaurant
from template_fastapi.repositories.restaurants import RestaurantRepository

app = typer.Typer()
console = Console()
restaurant_repo = RestaurantRepository()


def read_csv_data(file_path: str) -> list[Restaurant]:
    """CSVファイルからレストランデータを読み込む"""
    restaurants = []
    with open(file_path, encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            # タグをリストに変換
            tags = row["tags"].strip('"').split(",") if row["tags"] else []
            restaurant = Restaurant(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                price=float(row["price"]),
                latitude=float(row["latitude"]) if row["latitude"] else None,
                longitude=float(row["longitude"]) if row["longitude"] else None,
                tags=tags,
            )
            restaurants.append(restaurant)
    return restaurants


@app.command()
def import_data(
    csv_file: str = typer.Option(..., "--csv-file", "-f", help="CSVファイルのパス"),
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="一度に処理するバッチサイズ"),
):
    """CSVからデータをデータベースにインポートしてベクトル検索を設定する"""
    console.print(f"[bold green]CSVファイル[/bold green]: {csv_file}からデータを読み込みます")

    # CSVデータの読み込み
    restaurants = read_csv_data(csv_file)
    console.print(f"[bold blue]{len(restaurants)}件[/bold blue]のレストランデータを読み込みました")

    # データの登録
    console.print("[bold yellow]レストランデータをデータベースに登録しています...[/bold yellow]")

    # バッチサイズごとに処理
    for i in range(0, len(restaurants), batch_size):
        batch = restaurants[i : i + batch_size]
        for restaurant in batch:
            created_restaurant = restaurant_repo.create_restaurant(restaurant)
            console.print(f"ID: {created_restaurant.id} - {created_restaurant.name}を登録しました")

        console.print(f"[bold blue]{min(i + batch_size, len(restaurants))}/{len(restaurants)}件[/bold blue]処理完了")

    console.print("[bold green]すべてのデータが正常に登録されました！[/bold green]")


@app.command()
def search(
    query: str = typer.Option(..., "--query", "-q", help="検索クエリ"),
    k: int = typer.Option(3, "--top-k", "-k", help="取得する上位結果の数"),
):
    """説明文のベクトル検索を実行する"""
    console.print(f"[bold green]クエリ[/bold green]: '{query}'で検索します")

    # レポジトリを使用してベクトル検索を実行
    results = restaurant_repo.search_restaurants(query=query, k=k)

    # 結果の表示
    console.print(f"\n[bold blue]{len(results)}件[/bold blue]の検索結果:")
    for i, restaurant in enumerate(results):
        console.print(f"\n[bold]{i + 1}. {restaurant.name}[/bold]")
        console.print(f"   説明: {restaurant.description or '説明なし'}")
        console.print(f"   価格: ¥{restaurant.price}")
        console.print(f"   タグ: {', '.join(restaurant.tags)}")
        if restaurant.latitude and restaurant.longitude:
            console.print(f"   位置: 緯度 {restaurant.latitude}, 経度 {restaurant.longitude}")

    return results


@app.command()
def find_nearby(
    latitude: float = typer.Option(..., "--latitude", "-lat", help="緯度"),
    longitude: float = typer.Option(..., "--longitude", "-lon", help="経度"),
    distance_km: float = typer.Option(5.0, "--distance", "-d", help="検索半径（キロメートル）"),
    limit: int = typer.Option(10, "--limit", "-l", help="取得する最大件数"),
):
    """位置情報に基づいて近くのレストランを検索する"""
    console.print(f"[bold green]位置[/bold green]: 緯度 {latitude}, 経度 {longitude}の{distance_km}km圏内を検索します")

    # レポジトリを使用して位置検索を実行
    results = restaurant_repo.find_nearby_restaurants(
        latitude=latitude, longitude=longitude, distance_km=distance_km, limit=limit
    )

    # 結果の表示
    console.print(f"\n[bold blue]{len(results)}件[/bold blue]の検索結果:")
    for i, restaurant in enumerate(results):
        console.print(f"\n[bold]{i + 1}. {restaurant.name}[/bold]")
        console.print(f"   説明: {restaurant.description or '説明なし'}")
        console.print(f"   価格: ¥{restaurant.price}")
        console.print(f"   タグ: {', '.join(restaurant.tags)}")
        if restaurant.latitude and restaurant.longitude:
            console.print(f"   位置: 緯度 {restaurant.latitude}, 経度 {restaurant.longitude}")

    return results


@app.command()
def get_restaurant(
    restaurant_id: str = typer.Option(..., "--id", "-i", help="レストランID"),
):
    """指定されたIDのレストラン情報を取得する"""
    console.print(f"[bold green]レストランID[/bold green]: {restaurant_id}の情報を取得します")

    try:
        # レポジトリを使用してレストラン情報を取得
        restaurant = restaurant_repo.get_restaurant(restaurant_id)

        # 結果の表示
        console.print("\n[bold blue]レストラン情報[/bold blue]:")
        console.print(f"ID: {restaurant.id}")
        console.print(f"名前: {restaurant.name}")
        console.print(f"説明: {restaurant.description or '説明なし'}")
        console.print(f"価格: ¥{restaurant.price}")
        console.print(f"タグ: {', '.join(restaurant.tags)}")
        if restaurant.latitude and restaurant.longitude:
            console.print(f"位置: 緯度 {restaurant.latitude}, 経度 {restaurant.longitude}")

        return restaurant
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")
        return None


@app.command()
def delete_restaurant(
    restaurant_id: str = typer.Option(..., "--id", "-i", help="削除するレストランID"),
    force: bool = typer.Option(False, "--force", "-f", help="確認なしで削除する"),
):
    """指定されたIDのレストランを削除する"""
    console.print(f"[bold green]レストランID[/bold green]: {restaurant_id}を削除します")

    try:
        # 削除前に確認
        if not force:
            restaurant = restaurant_repo.get_restaurant(restaurant_id)
            console.print("以下のレストランを削除しようとしています：")
            console.print(f"ID: {restaurant.id}")
            console.print(f"名前: {restaurant.name}")

            if not typer.confirm("削除してもよろしいですか？"):
                console.print("[yellow]削除をキャンセルしました[/yellow]")
                return

        # レポジトリを使用してレストランを削除
        restaurant_repo.delete_restaurant(restaurant_id)
        console.print(f"[bold green]レストランID: {restaurant_id}を正常に削除しました[/bold green]")
    except Exception as e:
        console.print(f"[bold red]エラー[/bold red]: {str(e)}")


if __name__ == "__main__":
    app()
