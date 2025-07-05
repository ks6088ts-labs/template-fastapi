from template_fastapi.models.item import Item

# In-memory database for items
items_db: dict[int, Item] = {}

# Sample data initialization
sample_items = [
    Item(id=1, name="Hammer", description="A tool for hammering nails", price=9.99, tags=["tool", "hardware"]),
    Item(id=2, name="Screwdriver", description="A tool for driving screws", price=7.99, tags=["tool", "hardware"]),
    Item(id=3, name="Wrench", description="A tool for tightening bolts", price=12.99, tags=["tool", "hardware"]),
    Item(id=4, name="Saw", description="A tool for cutting wood", price=19.99, tags=["tool", "hardware", "cutting"]),
    Item(id=5, name="Drill", description="A tool for drilling holes", price=49.99, tags=["tool", "hardware", "power"]),
]

# Initialize database with sample data
for item in sample_items:
    items_db[item.id] = item
