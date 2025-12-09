import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_custom_fields():
    custom_fields = {
        "Sales Order": [
            {
                "fieldname": "salla_product_id",
                "fieldtype": "Data",
                "label": "Salla ID",
                "insert_after": "customer",
                "reqd": 0,
                "unique": 1
            }
        ],
        "Customer": [
            {
                "fieldname": "salla_customer_id",
                "fieldtype": "Data",
                "label": "Salla Customer ID",
                "insert_after": "customer_name",
                "reqd": 0,
                "unique": 1
            }
        ]
    }

    # ❗ FIX: remove ignore_validate
    create_custom_fields(custom_fields)
