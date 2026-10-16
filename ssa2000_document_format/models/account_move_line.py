from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _ssa_get_pickings(self):
        """Albaranes de salida validados que originaron esta línea de factura."""
        self.ensure_one()
        return self.sale_line_ids.move_ids.picking_id.filtered(
            lambda p: p.state == "done" and p.picking_type_code == "outgoing"
        ).sorted("date_done")

    def _ssa_get_weights(self):
        """Pesajes (bruto, tara, neto) y lotes de los movimientos de entrega de la línea."""
        self.ensure_one()
        moves = self._ssa_get_pickings().move_ids.filtered(
            lambda m: m.sale_line_id in self.sale_line_ids and m.state == "done"
        )
        gross = sum(moves.mapped("ssa_gross_weight"))
        tare = sum(moves.mapped("ssa_tare_weight"))
        lots = moves.move_line_ids.lot_id.mapped("name")
        origin_lots = [p.ssa_origin_lot for p in moves.picking_id if p.ssa_origin_lot]
        return {
            "has_weights": bool(gross or tare),
            "gross": gross,
            "tare": tare,
            "net": gross - tare,
            "lots": list(dict.fromkeys(lots + origin_lots)),
        }
