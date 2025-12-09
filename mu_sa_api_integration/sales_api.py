import frappe
import requests
from frappe.utils.data import flt
from datetime import datetime

@frappe.whitelist()
def sync_sales(shop):
    """
    Minimal Salla -> ERPNext Sales Order sync:
    - Uses total.amount and divides by item quantity to set rate.
    - Parses Salla date.date and uses its date part as transaction_date/delivery_date.
    - Uses warehouse string "Stores - NGS" for each item line.
    - Creates Customer if missing. Skips Sales Order if already exists (Salla-<id>).
    """
    try:
        shop_doc = frappe.get_doc("Shop", shop)
        token = shop_doc.value_bear

        url = "https://api.salla.dev/admin/v2/orders"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        # fetch orders
        try:
            r = requests.get(url, headers=headers, timeout=60)
            r.raise_for_status()
            orders = r.json().get("data", [])
        except Exception as exc:
            frappe.throw(f"Salla API request failed: {exc}")

        if not orders:
            frappe.msgprint("No orders returned from Salla.")
            return

        for order in orders:
            try:
                order_id = order.get("id") or "unknown"
                # parse order total amount
                total_obj = order.get("total", {}) or {}
                total_amount = flt(total_obj.get("amount") or 0)

                # parse Salla date -> ERPNext date
                date_obj = order.get("date", {}) or {}
                date_str_raw = date_obj.get("date")  # e.g. "2025-11-13 10:40:59.000000"
                if date_str_raw:
                    try:
                        dt = datetime.strptime(date_str_raw, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        # try without microseconds as fallback
                        dt = datetime.strptime(date_str_raw, "%Y-%m-%d %H:%M:%S")
                    txn_date = dt.strftime("%Y-%m-%d")
                    txn_time = dt.strftime("%H:%M:%S")
                else:
                    txn_date = frappe.utils.nowdate()
                    txn_time = ""

                # customer
                cust = order.get("customer") or {}
                customer_name = cust.get("full_name") or f"Customer-{order_id}"
                mobile = str(cust.get("mobile") or "")
                email = cust.get("email") or ""

                if not frappe.db.exists("Customer", customer_name):
                    frappe.get_doc({
                        "doctype": "Customer",
                        "customer_name": customer_name,
                        "customer_group": "All Customer",
                        "territory": "All Territories",
                        "mobile_no": mobile,
                        "email_id": email
                    }).insert(ignore_permissions=True)
                    frappe.db.commit()

                # prepare items: compute rate = total_amount / total_quantity_proportionally per item
                items = order.get("items", []) or []
                # compute total quantity across items to allow proportional distribution (if multiple items)
                total_qty = sum([int(i.get("quantity") or 0) for i in items]) or 0

                # If sum qty is zero, fall back to per-item handling to avoid division by zero
                items_list = []
                if total_qty > 0:
                    # distribute total_amount proportionally by quantity
                    for i in items:
                        name = i.get("name") or f"Item-{order_id}"
                        qty = flt(i.get("quantity") or 1)
                        # proportional share: (qty / total_qty) * total_amount
                        share = (qty / total_qty) * total_amount if total_amount else 0
                        rate = share / max(1, qty)
                        items_list.append({
                            "item_code": name,
                            "item_name": name,
                            "qty": qty,
                            "rate": flt(rate, 2),
                            "amount": flt(rate * qty, 2),
                            "warehouse": "Stores - NGS"
                        })
                else:
                    # fallback: each item takes entire total / its own qty (useful when only single item present)
                    for i in items:
                        name = i.get("name") or f"Item-{order_id}"
                        qty = flt(i.get("quantity") or 1)
                        rate = (total_amount / max(1, qty)) if total_amount else 0
                        items_list.append({
                            "item_code": name,
                            "item_name": name,
                            "qty": qty,
                            "rate": flt(rate, 2),
                            "amount": flt(rate * qty, 2),
                            "warehouse": "Stores - NGS"
                        })

                if not items_list:
                    frappe.msgprint(f"No items for order {order_id}, skipping.")
                    continue

                # Sales Order docname we will use to avoid duplicates
                so_name = f"Salla-{order_id}"
                if frappe.db.exists("Sales Order", so_name):
                    frappe.msgprint(f"Sales Order {so_name} already exists. Skipping.")
                    continue

                so_doc = frappe.get_doc({
                    "doctype": "Sales Order",
                    "salla_product_id": order_id,
                    "customer": customer_name,
                    "customer_name": customer_name,
                    "transaction_date": txn_date,
                    "delivery_date": txn_date,      # using same date; ERPNext expects date format YYYY-MM-DD
                    "company": getattr(shop_doc, "company", frappe.defaults.get_defaults().company),
                    "items": items_list
                }).insert(ignore_permissions=True)

                frappe.db.commit()
                frappe.msgprint(f"Created Sales Order {so_doc.name} for Salla order {order_id} (time: {txn_time})")

            except Exception as order_exc:
                frappe.log_error(message=str(order_exc), title=f"Salla Order {order.get('id') or 'unknown'} sync failed")
                # continue to next order
                continue

    except Exception as e:
        frappe.log_error(message=str(e), title="Salla Sync Sales Failed")
        frappe.throw(f"Salla Sales Sync failed: {str(e)}")
