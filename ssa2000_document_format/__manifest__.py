{
    "name": "SSA2000 - Document Format",
    "version": "19.0.1.0.0",
    "category": "Extra Tools",
    "summary": "Formato de albarán y factura para Sevillana de Servicios Agrícolas 2000",
    "author": "Xtendoo",
    "website": "https://xtendoo.es",
    "license": "AGPL-3",
    "depends": ["sale_stock", "account"],
    "data": [
        "views/res_company_views.xml",
        "views/stock_picking_views.xml",
        "reports/stock_picking_report_templates.xml",
        "reports/invoice_report_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
}
