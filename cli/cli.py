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
        item_name = item["name"][:24] if len(item["name"]) > 24 else item["name"]
        item_qty = item["quantity"]
        item_price = item["price"]
        item_category = item.get("category") or ""
        item_barcode = item.get("barcode") or ""
        print(f"{item_id:<4} {item_name:<24} {item_qty:<5} {item_price:<9} {item_category:<14} {item_barcode}")


def view_items():
    response = requests.get(f"{SERVER_URL}/api/inventory", timeout=10)
    if response.status_code == 200:
        print_items(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def add_item():
    print("Enter the item details below:")
    payload = {
        "name": input("Name: ").strip(),
        "barcode": input("Barcode (optional): ").strip() or None,
        "category": input("Category (optional): ").strip() or None,
        "brand": input("Brand (optional): ").strip() or None,
        "quantity": int(input("Quantity [0]: ").strip() or 0),
        "price": float(input("Price [0.0]: ").strip() or 0.0),
    }

    response = requests.post(f"{SERVER_URL}/api/inventory", json=payload, timeout=10)
    if response.status_code == 201:
        print("Item created successfully!")
        print_items([response.json()])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def edit_item():
    item_id = input("Enter the ID of the item to edit: ").strip()
    fields = {}
    for key, prompt in [("name", "New name: "), ("barcode", "New barcode: "), ("category", "New category: "), ("brand", "New brand: "), ("quantity", "New quantity: "), ("price", "New price: ")]:
        value = input(prompt).strip()
        if value:
            fields[key] = int(value) if key in {"quantity"} else float(value) if key == "price" else value
    response = requests.patch(f"{SERVER_URL}/api/inventory/{item_id}", json=fields, timeout=10)
    if response.status_code == 200:
        print("Item updated!")
        print_items([response.json()])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def delete_item():
    item_id = input("Enter the ID of the item to delete: ").strip()
    response = requests.delete(f"{SERVER_URL}/api/inventory/{item_id}", timeout=10)
    if response.status_code == 200:
        print(response.json().get("message", "Deleted."))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def search_external():
    query = input("Search OpenFoodFacts for: ").strip()
    response = requests.get(f"{SERVER_URL}/api/external/search", params={"q": query}, timeout=10)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    products = response.json()
    if not products:
        print("No products found.")
        return
    for idx, product in enumerate(products, 1):
        print(f"{idx}. {product['name']} (barcode: {product.get('barcode')}, brand: {product.get('brand')})")


def import_barcode(barcode=None):
    if barcode is None:
        barcode = input("Enter barcode to look up: ").strip()
    payload = {
        "barcode": barcode,
        "quantity": int(input("Starting quantity [0]: ").strip() or 0),
        "price": float(input("Price [0.0]: ").strip() or 0.0),
    }
    response = requests.post(f"{SERVER_URL}/api/inventory/import/barcode", json=payload, timeout=10)
    if response.status_code == 201:
        print("Product imported and added to inventory!")
        print_items([response.json()])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


def show_menu():
    print("\n==== Inventory Management CLI ====")
    for label, value in [("1. View all items", None), ("2. Add item manually", None), ("3. Edit item", None), ("4. Delete item", None), ("5. Search OpenFoodFacts by name", None), ("6. Import item from OpenFoodFacts by barcode", None), ("0. Exit", None)]:
        print(label)
    print()


def run():
    while True:
        show_menu()
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        actions = {"1": view_items, "2": add_item, "3": edit_item, "4": delete_item, "5": search_external, "6": import_barcode}
        action = actions.get(choice)
        if action:
            action()
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
