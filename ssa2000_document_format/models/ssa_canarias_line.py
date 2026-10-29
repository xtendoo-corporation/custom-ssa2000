from odoo import fields, models


class SsaCanariasLine(models.Model):
    _name = "ssa.canarias.line"
    _description = "Línea de envío a Canarias"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    picking_id = fields.Many2one("stock.picking", required=True, ondelete="cascade", index=True)
    move_id = fields.Many2one("stock.move", string="Movimiento", ondelete="set null")
    product_id = fields.Many2one("product.product", string="Producto", required=True)
    units = fields.Float(string="Nº de unidades / bultos", digits=(16, 2))
    net_kg = fields.Float(string="Kg netos", digits=(16, 0))
    container = fields.Char(string="Nº de contenedor")
    seal = fields.Char(string="Nº de precinto")
    lot = fields.Char(string="Lote")
    destination = fields.Char(string="Destino")
