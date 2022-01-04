from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import json


class Item(BaseModel):
    name: str
    description: Optional[str] = None


app = FastAPI()

SUPPORTED_PRODUCTS = {
    "chilled": ["milk", "yougurt", "cheese", "insulin"],
    "hazard": ["bleach", "stain removal", "insulin"],
    "other": ["bread", "pasta", "salt", "bamba", "apple"]
}

MAX_SHELVE_ITEM_HOLD = 10


def create_store(matrix_size):
    """
    This function creates the storage of the market.
    :param matrix_size: The size of the market store
    :return: Json file that shows the market shelves status
    """
    matrix = []
    start_quantity = 0

    for i in range(matrix_size):
        matrix.append([])
        for n in range(matrix_size):
            if n == matrix_size - 1 and i >= matrix_size - 3:
                matrix[i].append({"productType": '', "quantity": start_quantity, "shelveType": ['chilled', 'hazard'],
                                  "shelveMaxSize": 10})
            elif n >= matrix_size - 3 and i >= matrix_size - 3:
                matrix[i].append(
                    {"productType": '', "quantity": start_quantity, "shelveType": ['chilled'], "shelveMaxSize": 10})
            elif n == matrix_size - 1:
                matrix[i].append(
                    {"productType": '', "quantity": start_quantity, "shelveType": ['hazard'], "shelveMaxSize": 10})
            else:
                matrix[i].append(
                    {"productType": '', "quantity": start_quantity, "shelveType": ['other'], "shelveMaxSize": 10})

    store = {"shelves": matrix}
    with open('Store.json', 'w') as f:
        json.dump(store, f, indent=4)


def check_product_type(product_id):
    """
    This function check in what category given product appear.
    :param product_id: Product name.
    :return: Array of product categories.
    """
    product_types = []

    for product_type in SUPPORTED_PRODUCTS:
        if product_id in SUPPORTED_PRODUCTS[product_type]:
            product_types.append(product_type)

    return product_types


def check_shelve(product_id, product_type, quantity):
    """
    This function check if there is a free shalve to store the prodact. If there is than it stores it in the store and
    return the place of the product.
    :param product_id: Product name.
    :param product_type: Product type.
    :param quantity: The quantity if the product.
    :return: If the prodact was stored and if it is than the place of the product in the store.
    """
    with open('Store.json') as f:
        store = json.load(f)

    shelves = store['shelves']
    quantity = int(quantity)

    for shelve in shelves:
        for cell in shelve:
            if cell['quantity'] < 10:
                if cell['productType'] == "" or cell['productType'] == product_id:
                    if (cell['productType'] == product_id and cell['quantity'] + quantity <= 10) or (
                    set(product_type).issubset(cell['shelveType'])):
                        cell['productType'] = product_id
                        cell['quantity'] = cell['quantity'] + quantity

                        with open('Store.json', 'w') as f:
                            json.dump(store, f, indent=4)

                        return {"foundCell": True, "cell": "{0},{1}".format(shelves.index(shelve), shelve.index(cell))}

    return {"foundCell": False}


@app.post("/allocateCell")
async def root(request: Request):
    data = await request.json()
    if "productId" not in data and "quantity" not in data:
        raise HTTPException(status_code=404, detail="Item not found")

    product_id = data["productId"]
    quantity = data["quantity"]

    product_type = check_product_type(product_id)

    if not product_type:
        return {"foundCell": False}
    insert_status = check_shelve(product_id, product_type, quantity)

    return insert_status
