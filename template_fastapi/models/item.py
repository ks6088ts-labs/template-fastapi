from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    tags: list[str] = []
