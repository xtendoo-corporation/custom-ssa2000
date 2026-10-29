import re

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _ssa_refund_reason(self):
        """Motivo del abono sin el prefijo que añade Odoo ("Reversión de: INV/..., motivo")."""
        self.ensure_one()
        ref = self.ref or ""
        return re.sub(r"^(Reversión de|Reversal of):\s*[^,]*,\s*", "", ref)
