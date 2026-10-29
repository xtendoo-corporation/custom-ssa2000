from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    ssa_stat_code = fields.Char(
        string="Partida estadística / arancelaria",
        help="Se imprime en la factura y en las declaraciones de Canarias.",
    )
    ssa_goods_description = fields.Char(
        string="Descripción de la mercancía",
        help="Texto de la mercancía en la factura de Canarias (p. ej. Materias vegetales alimentación animal).",
    )
    ssa_botanical_name = fields.Char(string="Nombre botánico")
    ssa_package_form = fields.Char(string="Forma / tipo de bulto", help="Por ejemplo: Alpaca.")
