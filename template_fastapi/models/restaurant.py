from pydantic import BaseModel


class Restaurant(BaseModel):
    id: str
    name: str
    description: str | None = None
    price: float
    latitude: float | None = None
    longitude: float | None = None
    tags: list[str] = []
