import frappe
import requests
import json

@frappe.whitelist()
def sync_customers(shop):
    """
    Fetch customers from Salla API and insert/update them in ERPNext Customer DocType.
    Automatically creates missing Customer Group or Territory if not found.
    """
    shop_doc = frappe.get_doc("Shop", shop)
    value_bear = shop_doc.value_bear

    url = "https://api.salla.dev/admin/v2/customers"
    headers = {
        "Authorization": f"Bearer {value_bear}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        frappe.throw(f"API Request Failed: {str(e)}")

    data = response.json().get("data", [])

    if not data:
        frappe.msgprint("No customers found in Salla API.")
        return []

    inserted = 0
    updated = 0

    # Ensure default Customer Group exists
    customer_group = frappe.get_value("Customer Group", "All Customer")
    if not customer_group:
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "All Customer",
            "is_group": 0
        }).insert(ignore_permissions=True)
        customer_group = "All Customer"

    # Ensure default Territory exists
    territory = frappe.get_value("Territory", "All Territories")
    if not territory:
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "All Territories",
            "is_group": 0
        }).insert(ignore_permissions=True)
        territory = "All Territories"

    for cust in data:
        customer_name = cust.get("full_name") or f"{cust.get('first_name', '')} {cust.get('last_name', '')}".strip()
        email = cust.get("email")
        mobile = cust.get("mobile")
        country = cust.get("country") or ""
        salla_id = cust.get("id")
        # frappe.msgprint(frappe.as_json(salla_id))

        # Check if customer exists by email
        existing = frappe.get_all(
            "Customer",
            filters={"email_id": email},
            fields=["name"]
        )
        mobile = str(cust.get("mobile")) if cust.get("mobile") else ""

        if existing:
            # Update existing customer
            customer_doc = frappe.get_doc("Customer", existing[0].name)
            customer_doc.customer_name = customer_name

            customer_doc.mobile_no = mobile
            customer_doc.country = country
            customer_doc.customer_group = customer_group
            customer_doc.territory = territory
            customer_doc.salla_customer_id = salla_id  # custom field
            customer_doc.save(ignore_permissions=True)
            updated += 1
        else:
            # Create new customer
            customer_doc = frappe.get_doc({
                "doctype": "Customer",
                "salla_customer_id": salla_id,
                "customer_name": customer_name,
                "customer_type": "Individual",
                "customer_group": customer_group,
                "territory": territory,
                "email_id": email,
                "mobile_no": mobile,
                "country": country,
                "salla_id": salla_id
            })
            customer_doc.insert(ignore_permissions=True)
            inserted += 1

    frappe.msgprint(f"Customers inserted: {inserted}, updated: {updated}")
    return {"inserted": inserted, "updated": updated}
