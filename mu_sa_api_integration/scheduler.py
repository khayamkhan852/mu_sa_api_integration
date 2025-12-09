import frappe

def sync_all_data_for_all_shops():
    shops = frappe.get_all("Shop", pluck="name")

    if not shops:
        frappe.logger().error("No shops found for scheduled sync")
        return

    for shop in shops:
        frappe.logger().info(f"Starting full sync for shop: {shop}")

        try:
            frappe.enqueue(
                "mu_sa_api_integration.customer_api.sync_customers",
                shop=shop, queue="long", timeout=600
            )

            frappe.enqueue(
                "mu_sa_api_integration.api.sync_products",
                shop=shop, queue="long", timeout=900
            )

            # frappe.enqueue(
            #     "mu_sa_api_integration.mu_sa_api_integration.tax_api.sync_taxes",
            #     shop=shop, queue="long", timeout=400
            # )

            frappe.enqueue(
                "mu_sa_api_integration.sales_api.sync_sales",
                shop=shop, queue="long", timeout=900
            )

            frappe.logger().info(f"Full sync enqueued for shop: {shop}")

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Shop Sync Failed: {shop}")
            frappe.logger().error(f"Error syncing shop {shop}: {str(e)}")
