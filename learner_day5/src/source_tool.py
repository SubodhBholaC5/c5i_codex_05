import json
from pathlib import Path

class ReadOnlyOrderLookup:
    """The single allow-listed, read-only tool available to the draft feature."""
    name="lookup_order"
    def __init__(self, path=None):
        self.path=Path(path or Path(__file__).parents[1]/"data/source_records.json")
        self.db=json.loads(self.path.read_text())
        self.version=self.db["version"]
    def __call__(self, order_id: str):
        if not isinstance(order_id,str) or not order_id or len(order_id)>40:
            raise ValueError("Invalid order_id")
        return self.db["records"].get(order_id)
