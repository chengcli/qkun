import yaml
from pathlib import Path
from typing import Optional, Dict

class ProductCatalog:
    def __init__(self, yaml_path: Optional[str] = None):
        if yaml_path:
            path = Path(yaml_path)
        else:
            # Default: relative to this file's grandparent
            path = Path(__file__).resolve().parent.parent / "products.yaml"

        if not path.is_file():
            raise FileNotFoundError(f"'products.yaml' not found at: {path}")

        with open(path, 'r') as f:
            self.catalog = yaml.safe_load(f)

    def get_concept_id(self, mission: str, instrument: str, product_name: str) -> Optional[str]:
        """Return concept-id for given mission, instrument, and product"""
        product = self._get_product(mission, instrument, product_name)
        return product.get("concept-id") if product else None

    def get_product_metadata(self, mission: str, instrument: str, product_name: str) -> Optional[Dict]:
        """Return full metadata dict for a product, or None if not found"""
        return self._get_product(mission, instrument, product_name)

    def _get_product(self, mission: str, instrument: str, product_name: str) -> Optional[Dict]:
        mission_data = self.catalog.get(mission.lower())
        if not mission_data:
            return None

        instrument_data = mission_data.get(instrument)
        if not instrument_data:
            return None

        for product in instrument_data:
            if product.get("name") == product_name:
                return product

        return None

if __name__ == "__main__":
    catalog = ProductCatalog("products.yaml")

    cid = catalog.get_concept_id("pace", "OCI", "L1B")
    print("Concept ID:", cid)

    meta = catalog.get_product_metadata("pace", "OCI", "L1B")
    print("Formats:", meta["formats"])
    print("Description:\n", meta["description"])
