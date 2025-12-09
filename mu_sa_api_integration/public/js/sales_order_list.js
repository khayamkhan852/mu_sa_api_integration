frappe.listview_settings['Sales Order'] = {
    onload(listview) {
        listview.page.add_inner_button(__('Sync Salla Sales'), () => {

            let d = new frappe.ui.Dialog({
                title: "Select Shop",
                fields: [
                    {
                        label: 'Shop',
                        fieldname: 'shop',
                        fieldtype: 'Link',
                        options: 'Shop',   // 👉 your Shop doctype
                        reqd: 1
                    }
                ],
                primary_action_label: "Sync Now",
                primary_action(values) {
                    d.hide();

                    // Call whitelisted backend method
                    frappe.call({
                        method: "mu_sa_api_integration.sales_api.sync_sales",  // 👉 your python method
                        args: {
                            shop: values.shop
                        },
                        callback: function (r) {
                            if (!r.exc) {
                                frappe.msgprint("Sync Complete!");
                                listview.refresh();
                            }
                        }
                    });
                }
            });

            d.show();
        });
    }
}
