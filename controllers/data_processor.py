from datetime import datetime
from pathlib import Path
from flask import jsonify
from flask import Blueprint

from db.models import Item, Product, Promo, Transaction, Venue, Store

from flask import jsonify, g
import json

data_processor = Blueprint("data_processor", __name__)


@data_processor.route("/start", methods=["GET"])
def start_data_processor():
    """
    Starts the processing of the datafile in the input folder
    """

    # Define the input path
    input_path = Path(__file__).parent.parent / "input"

    # Look for JSON files matching the pattern Venue1-5_YYYYMMDD_YYYYMMDD.json
    json_files = list(input_path.glob("Venue*_*.json"))

    if not json_files:
        return (
            jsonify({"data": [], "error": "No JSON files found in input folder"}),
            404,
        )

    # Read the first matching JSON file using polars
    json_file = json_files[0]

    try:
        # Read and flatten the nested JSON
        with open(json_file, "r") as f:
            raw_data = json.load(f)

        # Extract Values
        # Use sets to track seen IDs for deduplication
        seen_venues = set()
        seen_stores = set()
        seen_transactions = set()
        seen_products = set()
        seen_items = set()

        venues = []
        stores = []
        transactions = []
        items = []
        products = []
        promos = []

        for venue in raw_data:
            venue_id = venue.get("VenueID")
            if venue_id not in seen_venues:
                venues.append(
                    {"VenueID": venue_id, "VenueName": venue.get("VenueName")}
                )
                seen_venues.add(venue_id)

            for store in venue.get("Stores", []):
                store_id = store.get("StoreID")
                if store_id not in seen_stores:
                    stores.append(
                        {
                            "StoreID": store_id,
                            "StoreName": store.get("StoreName"),
                            "VenueID": venue_id,
                        }
                    )
                    seen_stores.add(store_id)

                for transaction in store.get("Transactions", []):
                    trans_id = transaction.get("TransactionID")
                    if trans_id not in seen_transactions:
                        transactions.append(
                            {
                                "TransactionID": trans_id,
                                "TransactionType": transaction.get("TransactionType"),
                                "DateTimeUTC": datetime.strptime(
                                    transaction.get("DateTimeUTC"),
                                    "%d/%m/%Y %I:%M:%S %p",
                                ),
                                "OperatorNumber": transaction.get("OperatorNumber"),
                                "OperatorName": transaction.get("OperatorName"),
                                "TillID": transaction.get("TillID"),
                                "TillName": transaction.get("TillName"),
                                "ServiceCharge": transaction.get("ServiceCharge", 0.0),
                                "NettTotal": transaction.get("NettTotal"),
                                "NettSales": transaction.get("NettSales"),
                                "GrossSales": transaction.get("GrossSales"),
                                "OrderDiscount": transaction.get("OrderDiscount", 0.0),
                                "TotalDiscount": transaction.get("TotalDiscount", 0.0),
                                "Taxable": transaction.get("Taxable"),
                                "NonTaxable": transaction.get("NonTaxable"),
                                "TaxAmount": transaction.get("TaxAmount"),
                                "Payments": transaction.get("Payments"),
                                "Account": transaction.get("Account"),
                                "StoreID": store_id,
                            }
                        )
                        seen_transactions.add(trans_id)

                    for item in transaction.get("Items", []):
                        product_data = item.get("Product")
                        if product_data:
                            prod_id = product_data.get("ProductID")
                            if prod_id not in seen_products:
                                products.append(
                                    {
                                        "ProductID": prod_id,
                                        "ProductName": product_data.get("ProductName"),
                                        "CategoryID": product_data.get("CategoryID"),
                                        "Category": product_data.get("Category"),
                                        "CategoryGroupID": product_data.get(
                                            "CategoryGroupID"
                                        ),
                                        "CategoryGroup": product_data.get(
                                            "CategoryGroup"
                                        ),
                                        "Active": product_data.get("Active", True),
                                        "Price": product_data.get("Price"),
                                        "ProductCost": product_data.get("ProductCost"),
                                        "Size": product_data.get("Size"),
                                        "SizeVolume": product_data.get("SizeVolume"),
                                        "SizeUnit": product_data.get("SizeUnit"),
                                        "Barcode": product_data.get("Barcode"),
                                        "Base": product_data.get("Base"),
                                        "BaseVolume": product_data.get("BaseVolume"),
                                        "BaseUnit": product_data.get("BaseUnit"),
                                    }
                                )
                                seen_products.add(prod_id)

                        line_id = item.get("LineID")
                        item_key = (line_id, trans_id)
                        if item_key not in seen_items:
                            items.append(
                                {
                                    "LineID": line_id,
                                    "TransactionID": trans_id,
                                    "ProductID": item.get("ProductID"),
                                    "Quantity": item.get("Quantity"),
                                    "NettPrice": item.get("NettPrice"),
                                    "GrossPrice": item.get("GrossPrice"),
                                    "ItemDiscount": item.get("ItemDiscount", 0.0),
                                    "IsCondiment": item.get("IsCondiment", False),
                                    "NettTotal": item.get("NettTotal"),
                                }
                            )
                            seen_items.add(item_key)

                        # Promos don't need deduplication (auto-increment PK)
                        for promo in item.get("Promos", []):
                            promos.append(
                                {
                                    "LineID": line_id,
                                    "TransactionID": trans_id,
                                    "PromoID": promo.get("PromoID"),
                                    "PromoName": promo.get("PromoName"),
                                    "TotaliserName": promo.get("TotaliserName"),
                                    "Amount": promo.get("Amount"),
                                    "TotaliserID": promo.get("TotaliserID"),
                                }
                            )

        # Use bulk_insert_mappings for much better performance
        session = g.session
        try:
            if venues:
                session.bulk_insert_mappings(Venue, venues, render_nulls=True)
            if stores:
                session.bulk_insert_mappings(Store, stores, render_nulls=True)
            if transactions:
                session.bulk_insert_mappings(
                    Transaction, transactions, render_nulls=True
                )
            if products:
                session.bulk_insert_mappings(Product, products, render_nulls=True)
            if items:
                session.bulk_insert_mappings(Item, items, render_nulls=True)
            if promos:
                session.bulk_insert_mappings(Promo, promos, render_nulls=True)

            session.commit()
        except Exception as e:
            session.rollback()
            session.close()
            g.logger.exception(f"Error during db insert: {str(e)}")
            return jsonify({"error": f"Error during db insert: {str(e)}"}), 500
        finally:
            session.close()

        # Log basic information about the loaded data
        g.logger.debug(f"Successfully loaded {json_file.name}")

        return (
            jsonify(
                {
                    "message": f"Successfully loaded {json_file.name}",
                }
            ),
            200,
        )

    except Exception as e:
        g.logger.exception(f"Error reading JSON file: {str(e)}")
        return jsonify({"error": f"Error reading JSON file: {str(e)}"}), 500
