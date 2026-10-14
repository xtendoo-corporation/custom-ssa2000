from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _ssa_get_pickings(self):
        """Albaranes de salida validados que originaron esta línea de factura."""
        self.ensure_one()
        return self.sale_line_ids.move_ids.picking_id.filtered(
            lambda p: p.state == "done" and p.picking_type_code == "outgoing"
        ).sorted("date_done")
