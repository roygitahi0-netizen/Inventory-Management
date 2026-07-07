import sys

import requests

SERVER_URL = "http://127.0.0.1:5000"


def print_items(items):
    if not items:
        print("No items found.")
        return

    print("ID   Name                     Qty   Price     Category       Barcode")
    print("-" * 75)

    for item in items:
        item_id = item["id"]
        item_name = item["name"]
        item_qty = item["quantity"]
        item_price = item["price"]
        item_category = item.get("category")
        item_barcode = item.get("barcode")

        if item_category is None:
            item_category = ""
        if item_barcode is None:
            item_barcode = ""

        if len(item_name) > 24:
            item_name = item_name[:24]

        print(f"{item_id:<4} {item_name:<24} {item_qty:<5} {item_price:<9} {item_category:<14} {item_barcode}")


def view_items():
    response = requests.get(SERVER_URL + "/api/inventory", timeout=10)

    if response.status_code == 200:
        items = response.json()
        print_items(items)
    else:
        print("Error: " + str(response.status_code))
        print(response.text)


def add_item():
    print("Enter the item details below:")

    name = input("Name: ").strip()
    barcode = input("Barcode (optional): ").strip()
    category = input("Category (optional): ").strip()
    brand = input("Brand (optional): ").strip()
    quantity = input("Quantity [0]: ").strip()
    price = input("Price [0.0]: ").strip()

    if barcode == "":
        barcode = None
    if category == "":
        category = None
    if brand == "":
        brand = None
    if quantity == "":
        quantity = 0
    else:
        quantity = int(quantity)
    if price == "":
        price = 0.0
    else:
        price = float(price)

    payload = {
        "name": name,
        "barcode": barcode,
        "category": category,
        "brand": brand,
        "quantity": quantity,
        "price": price
    }

    response = requests.post(SERVER_URL + "/api/inventory", json=payload, timeout=10)

    if response.status_code == 201:
        print("Item created successfully!")
        print_items([response.json()])
    else:
        print("Error: " + str(response.status_code))
        print(response.text)


def edit_item():
    item_id = input("Enter the ID of the item to edit: ").strip()
    print("Leave a field blank to keep it the same.")

    fields = {}

    name = input("New name: ").strip()
    if name != "":
        fields["name"] = name

    barcode = input("New barcode: ").strip()
    if barcode != "":
        fields["barcode"] = barcode

    category = input("New category: ").strip()
    if category != "":
        fields["category"] = category

    brand = input("New brand: ").strip()
    if brand != "":
        fields["brand"] = brand

    quantity = input("New quantity: ").strip()
    if quantity != "":
        fields["quantity"] = int(quantity)

    price = input("New price: ").strip()
    if price != "":
        fields["price"] = float(price)

    response = requests.patch(SERVER_URL + "/api/inventory/" + item_id, json=fields, timeout=10)

    if response.status_code == 200:
        print("Item updated!")
        print_items([response.json()])
    else:
        print("Error: " + str(response.status_code))
        print(response.text)


def delete_item():
    item_id = input("Enter the ID of the item to delete: ").strip()

    response = requests.delete(SERVER_URL + "/api/inventory/" + item_id, timeout=10)

    if response.status_code == 200:
        message = response.json().get("message", "Deleted.")
        print(message)
    else:
        print("Error: " + str(response.status_code))
        print(response.text)


def search_external():
    query = input("Search OpenFoodFacts for: ").strip()

    response = requests.get(SERVER_URL + "/api/external/search", params={"q": query}, timeout=10)

    if response.status_code != 200:
        print("Error: " + str(response.status_code))
        print(response.text)
        return

    products = response.json()

    if not products:
        print("No products found.")
        return

    count = 1
    for product in products:
        product_name = product["name"]
        product_barcode = product.get("barcode")
        product_brand = product.get("brand")
        print(str(count) + ". " + product_name + "  (barcode: " + str(product_barcode) + ", brand: " + str(product_brand) + ")")
        count = count + 1


def import_barcode(barcode=None):
    if barcode is None:
        barcode = input("Enter barcode to look up: ").strip()

    quantity = input("Starting quantity [0]: ").strip()
    price = input("Price [0.0]: ").strip()

    if quantity == "":
        quantity = 0
    else:
        quantity = int(quantity)

    if price == "":
        price = 0.0
    else:
        price = float(price)

    payload = {
        "barcode": barcode,
        "quantity": quantity,
        "price": price
    }

    response = requests.post(SERVER_URL + "/api/inventory/import/barcode", json=payload, timeout=10)

    if response.status_code == 201:
        print("Product imported and added to inventory!")
        print_items([response.json()])
    else:
        print("Error: " + str(response.status_code))
        print(response.text)


def show_menu():
    print("")
    print("==== Inventory Management CLI ====")
    print("1. View all items")
    print("2. Add item manually")
    print("3. Edit item")
    print("4. Delete item")
    print("5. Search OpenFoodFacts by name")
    print("6. Import item from OpenFoodFacts by barcode")
    print("0. Exit")
    print("")


def run():
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            view_items()
        elif choice == "2":
            add_item()
        elif choice == "3":
            edit_item()
        elif choice == "4":
            delete_item()
        elif choice == "5":
            search_external()
        elif choice == "6":
            import_barcode()
        else:
            print("That option is not valid, please try again.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--list":
            view_items()
        elif arg == "--add":
            add_item()
        elif arg == "--import-barcode":
            if len(sys.argv) > 2:
                import_barcode(sys.argv[2])
            else:
                print("Please provide a barcode after --import-barcode")
    else:
        try:
            run()
        except KeyboardInterrupt:
            sys.exit(0)