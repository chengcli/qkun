
if __name__ == "__main__":
    catalog = ProductCatalog("products.yaml")

    cid = catalog.get_concept_id("pace", "OCI", "L1B")
    print("Concept ID:", cid)

    meta = catalog.get_product_metadata("pace", "OCI", "L1B")
    print("Formats:", meta["formats"])
    print("Description:\n", meta["description"])
