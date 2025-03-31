import yaml
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from importlib.resources import files

def lod2dol(list_of_dicts: List[Dict]):
    # Collect all unique keys
    all_keys = set().union(*(d.keys() for d in list_of_dicts))
    
    # Initialize the output dictionary
    dict_of_lists = {key: [] for key in all_keys}
    
    # Fill in the values
    for d in list_of_dicts:
        for key in all_keys:
            dict_of_lists[key].append(d.get(key, None))
    
    return dict_of_lists

def check_dates_in_range(temporal: str, start_dt: Optional[datetime.date], 
                         end_dt: Optional[datetime.date]) -> int:
    """Check if a date is within a range"""
    out_of_range = 0
    if not ',' in temporal:
        raise ValueError("Temporal range must be comma-separated: start,end")

    time_range = temporal.split(",")
    time_start_dt = datetime.strptime(time_range[0], "%Y-%m-%d").date()
    time_end_dt = datetime.strptime(time_range[1], "%Y-%m-%d").date()

    if start_dt:
        if time_start_dt < start_dt:
            out_of_range += 1

    if end_dt:
        if time_end_dt > end_dt:
            out_of_range += 2

    return out_of_range

def select_product_within(products: List[Dict], time: str) -> Optional[Dict]:
    """select a product from a list based on temporal range"""
    if not temporal:
        return products[0]

    for product in products:
        if product.get("temporal") == temporal:
            return product

    return None

class ProductCatalog:
    def __init__(self, yaml_path: Optional[str]=None):
        if yaml_path:
            path = Path(yaml_path)
        else:
            # Load products.yaml as a resource from the api package
            path = files("qkun.cmr") / "products.yaml"

        if not path.is_file():
            raise FileNotFoundError(f"'products.yaml' not found at: {path}")

        with open(path, 'r') as f:
            self.catalog = yaml.safe_load(f)

    def get_concept_id(self, mission: str, instrument: str, 
                       product_name: str, temporal: Optional[str]=None) -> Optional[str]:
        """Return concept-id for given mission, instrument, and product"""
        products = self._get_products(mission, instrument, product_name)

        if not temporal:
            return products[0].get("concept-id") if products else None

        for product in products:
            start_date = product.get("start-date")
            end_date = product.get("end-date")
            err = check_dates_in_range(temporal, start_date, end_date)
            if err == 0:
                return product.get("concept-id")

        if products:
            out = "Temporal range is not within any product\n"
            out += "Valid temporal ranges:"
            for product in products:
                out += f"\n- {product.get('start-date')} to {product.get('end-date')}"
            warnings.warn(out)

        return None

    def get_products_metadata(self, mission: str, instrument: str,
                              product_name: str) -> List[Dict]:
        """Return full metadata dict for a product, or None if not found"""
        return lod2dol(self._get_products(mission, instrument, product_name))

    def _get_products(self, mission: str, instrument: str, product_name: str) -> List[Dict]:
        mission_data = self.catalog.get(mission.lower())
        if not mission_data:
            return []

        instrument_data = mission_data.get(instrument)
        if not instrument_data:
            return []

        products = []
        for product in instrument_data:
            if product.get("name") == product_name:
                products.append(product)

        return products
