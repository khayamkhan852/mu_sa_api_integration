frappe.listview_settings['Item'] = {
    onload(listview) {
        listview.page.add_inner_button(__('Sync Salla Products'), () => {

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
                        method: "mu_sa_api_integration.api.sync_products",  // 👉 your python method
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
