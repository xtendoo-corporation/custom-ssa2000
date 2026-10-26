from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    ssa_gross_weight = fields.Float(string="Tn. bruto", digits=(16, 3))
    ssa_tare_weight = fields.Float(string="Tn. tara", digits=(16, 3))
    ssa_units = fields.Float(
        string="Unidades",
        digits=(16, 2),
        help="Número de unidades (informativo); la cantidad facturada la marca el pedido.",
    )
    ssa_net_weight = fields.Float(
        string="Tn. neto",
        digits=(16, 3),
        compute="_compute_ssa_net_weight",
        help="Bruto - tara cuando hay pesaje; en caso contrario, la cantidad del movimiento.",
    )
    ssa_price_unit = fields.Float(
        string="Precio",
        digits="Product Price",
        compute="_compute_ssa_amounts",
    )
    ssa_price_subtotal = fields.Monetary(
        string="Importe",
        currency_field="ssa_currency_id",
        compute="_compute_ssa_amounts",
    )
    ssa_currency_id = fields.Many2one(
        "res.currency", compute="_compute_ssa_amounts"
    )

    @api.onchange("ssa_gross_weight", "ssa_tare_weight")
    def _onchange_ssa_weights(self):
        for move in self:
            if move.ssa_gross_weight or move.ssa_tare_weight:
                move.quantity = max(move.ssa_gross_weight - move.ssa_tare_weight, 0.0)

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get("ssa_no_sync") and (
            {"ssa_gross_weight", "ssa_tare_weight"} & vals.keys()
        ):
            for move in self:
                if move.ssa_gross_weight or move.ssa_tare_weight:
                    net = max(move.ssa_gross_weight - move.ssa_tare_weight, 0.0)
                    if move.quantity != net:
                        move.with_context(ssa_no_sync=True).quantity = net
        return res

    @api.depends("ssa_gross_weight", "ssa_tare_weight", "quantity")
    def _compute_ssa_net_weight(self):
        for move in self:
            if move.ssa_gross_weight or move.ssa_tare_weight:
                move.ssa_net_weight = move.ssa_gross_weight - move.ssa_tare_weight
            else:
                move.ssa_net_weight = move.quantity

    @api.depends(
        "sale_line_id.price_unit",
        "sale_line_id.discount",
        "sale_line_id.currency_id",
        "quantity",
        "ssa_gross_weight",
        "ssa_tare_weight",
    )
    def _compute_ssa_amounts(self):
        for move in self:
            line = move.sale_line_id
            move.ssa_currency_id = line.currency_id or move.company_id.currency_id
            move.ssa_price_unit = line.price_unit if line else 0.0
            if line:
                qty = move.ssa_net_weight if (
                    move.ssa_gross_weight or move.ssa_tare_weight
                ) else move.quantity
                move.ssa_price_subtotal = (
                    line.price_unit * qty * (1 - (line.discount or 0.0) / 100.0)
                )
            else:
                move.ssa_price_subtotal = 0.0
