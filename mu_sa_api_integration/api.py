import frappe
import requests
from frappe.utils.file_manager import save_file

@frappe.whitelist()
def sync_products(shop, page=1, per_page=20):
    """
    Sync products from Salla API to ERPNext (skip variants/attributes).
    """
    shop_doc = frappe.get_doc("Shop", shop)
    headers = {
        "Authorization": f"Bearer {shop_doc.value_bear}",
        "Accept": "application/json"
    }

    url = f"https://api.salla.dev/admin/v2/products?page={page}&limit={per_page}"
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    products = response.json().get("data", [])

    created, updated = 0, 0

    for p in products:
        # --- ITEM CODE ---
        item_code = p.get("sku") or f"ITEM-{p.get('id')}"
        if frappe.db.exists("Item", item_code):
            doc = frappe.get_doc("Item", item_code)
            updated += 1
        else:
            doc = frappe.get_doc({"doctype": "Item", "item_code": item_code})
            created += 1

        # --- ITEM GROUP ---
        group_name = p.get("categories")[0]["name"] if p.get("categories") else "All Item Groups"
        if not frappe.db.exists("Item Group", group_name):
            frappe.get_doc({"doctype": "Item Group", "item_group_name": group_name}).insert(ignore_permissions=True)
        doc.item_group = group_name

        # --- BASIC FIELDS ---
        doc.item_name = p.get("name") or item_code
        doc.description = p.get("description") or ""
        doc.stock_uom = "Nos"
        doc.disabled = 0 if p.get("is_available") else 1
        doc.standard_rate = p.get("price", {}).get("amount") or 0
        doc.barcode = p.get("barcode") or ""
        doc.variant_of = None
        doc.has_variants = 0
        doc.image= p.get("thumbnail") or 0
        doc.valuation_rate = p.get("price", {}).get("amount") or 0
        doc.stock_uom =  p.get("weight_type") or ""
        doc.weight_uom = p.get("weight_type") or ""
        doc.weight_per_unit = p.get("weight") or ""

        # --- MAIN IMAGE ---
        main_image_url = p.get("main_image") or p.get("thumbnail")
        frappe.msgprint(frappe.as_json(main_image_url))
        if main_image_url:
            try:
                file_doc = save_file(
                    filename=main_image_url.split("/")[-1],
                    content=requests.get(main_image_url, timeout=60).content,
                    attached_to_doctype="Item",
                    attached_to_name=item_code,
                    is_private=0
                )
                doc.image_url = file_doc.file_url
            except:
                doc.image_url = main_image_url

        # --- SAVE ITEM ---
        doc.save(ignore_permissions=True)

    frappe.db.commit()

    return {
        "products_fetched": len(products),
        "created": created,
        "updated": updated
    }
