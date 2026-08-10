from database import initialize_database
from inventry import InventoryManager


def display_product(product):

    if not product:
        print("Product not found.")
        return

    print("\n-----------------------------")
    print(f"ID       : {product['id']}")
    print(f"Name     : {product['name']}")
    print(f"Category : {product['category']}")
    print(f"Price    : ₹{product['price']:.2f}")
    print(f"Quantity : {product['quantity']}")
    print(f"Supplier : {product['supplier']}")
    print("-----------------------------")


def display_products(products):

    if not products:
        print("No products found.")
        return

    print("\n" + "-" * 90)
    print(
        f"{'ID':<5}"
        f"{'Name':<25}"
        f"{'Category':<18}"
        f"{'Price':<12}"
        f"{'Qty':<8}"
    )
    print("-" * 90)

    for product in products:
        print(
            f"{product['id']:<5}"
            f"{product['name'][:23]:<25}"
            f"{product['category'][:16]:<18}"
            f"₹{product['price']:<11.2f}"
            f"{product['quantity']:<8}"
        )

    print("-" * 90)


def add_product(manager):

    name = input("Product name: ")
    category = input("Category: ")
    price = float(input("Price: "))
    quantity = int(input("Quantity: "))
    supplier = input("Supplier: ")

    product_id = manager.add_product(
        name,
        category,
        price,
        quantity,
        supplier
    )

    print(f"Product added successfully. ID = {product_id}")


def view_product(manager):

    product_id = int(input("Product ID: "))

    product = manager.get_product(product_id)

    display_product(product)


def view_products(manager):

    page = int(input("Page number: "))

    products = manager.get_products(
        page=page,
        page_size=10
    )

    display_products(products)


def search_products(manager):

    keyword = input("Search keyword: ")

    products = manager.search_products(keyword)

    display_products(products)


def update_product(manager):

    product_id = int(input("Product ID: "))

    product = manager.get_product(product_id)

    if not product:
        print("Product not found.")
        return

    print("Enter new details:")

    name = input("Name: ")
    category = input("Category: ")
    price = float(input("Price: "))
    quantity = int(input("Quantity: "))
    supplier = input("Supplier: ")

    success = manager.update_product(
        product_id,
        name,
        category,
        price,
        quantity,
        supplier
    )

    if success:
        print("Product updated successfully.")
    else:
        print("Update failed.")


def delete_product(manager):

    product_id = int(input("Product ID: "))

    success = manager.delete_product(product_id)

    if success:
        print("Product deleted successfully.")
    else:
        print("Product not found.")


def update_stock(manager):

    product_id = int(input("Product ID: "))
    change = int(
        input("Stock change (+add / -remove): ")
    )

    success = manager.update_stock(
        product_id,
        change
    )

    if success:
        print("Stock updated successfully.")
    else:
        print(
            "Stock update failed. "
            "Check product ID or available stock."
        )


def show_low_stock(manager):

    threshold = int(
        input("Low-stock threshold: ")
    )

    products = manager.low_stock_products(
        threshold
    )

    display_products(products)


def show_inventory_value(manager):

    value = manager.inventory_value()

    print(
        f"\nTotal inventory value: ₹{value:,.2f}"
    )


def main():

    initialize_database()

    manager = InventoryManager()

    while True:

        print("""
=========================================
      INVENTORY MANAGEMENT SYSTEM
=========================================

1. Add Product
2. View Product
3. View Products
4. Search Products
5. Update Product
6. Delete Product
7. Update Stock
8. Low Stock Products
9. Total Inventory Value
0. Exit
""")

        choice = input("Enter your choice: ")

        try:

            if choice == "1":
                add_product(manager)

            elif choice == "2":
                view_product(manager)

            elif choice == "3":
                view_products(manager)

            elif choice == "4":
                search_products(manager)

            elif choice == "5":
                update_product(manager)

            elif choice == "6":
                delete_product(manager)

            elif choice == "7":
                update_stock(manager)

            elif choice == "8":
                show_low_stock(manager)

            elif choice == "9":
                show_inventory_value(manager)

            elif choice == "0":
                print("Thank you!")
                break

            else:
                print("Invalid choice.")

        except ValueError as error:
            print(f"Input error: {error}")

        except Exception as error:
            print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()