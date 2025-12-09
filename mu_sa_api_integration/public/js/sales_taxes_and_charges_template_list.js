frappe.listview_settings['Sales Taxes and Charges Template'] = {
    onload(listview) {
        listview.page.add_inner_button(__('Sync Salla Taxes'), () => {

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
                        method: "salla.tax_api.sync_taxes",  // 👉 your python method
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
