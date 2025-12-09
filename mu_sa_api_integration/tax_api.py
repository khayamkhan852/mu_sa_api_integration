import frappe
import requests
import json

@frappe.whitelist()
def sync_taxes(shop):
    shop_doc = frappe.get_doc("Shop", shop)

    key_auth = shop_doc.key_auth
    value_bear = shop_doc.value_bear

    url = "https://api.salla.dev/admin/v2/taxes"

    headers = {
        "Authorization": f"Bearer {value_bear}",
        "Accept": "application/json",
    }

    # ----- DEBUG OUTPUT -----
    debug_info = {
        "URL": url,
        "Headers Sent": headers,
        "Shop Used": shop_doc.name
    }
    frappe.msgprint(f"<b>Request Debug:</b><br><pre>{json.dumps(debug_info, indent=4)}</pre>")

    # ----- API CALL -----
    try:
        response = requests.get(url, headers=headers)
    except Exception as e:
        frappe.throw(f"Request Error: {str(e)}")

    # ----- STATUS CODE -----
    frappe.msgprint(f"<b>Status Code:</b> {response.status_code}")

    # ----- ERROR -----
    if response.status_code != 200:
        frappe.throw(f"<b>API Error:</b><br><pre>{response.text}</pre>")

    # ----- SUCCESS: CLEAN JSON VIEW -----
    json_response = response.json()

    frappe.msgprint(f"""
        <b>API Response:</b>
        <br>
        <pre>{json.dumps(json_response, indent=4, ensure_ascii=False)}</pre>
    """)

    return json_response
