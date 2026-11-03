import re

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    ssa_withholding_base = fields.Selection(
        [("base", "Base imponible"), ("base_iva", "Base imponible + IVA")],
        string="Retención sobre",
        copy=True,
        help="Base sobre la que se calcula la retención (IRPF) de la autofactura. "
        "Al elegirla se pone el impuesto correspondiente en todas las líneas.",
    )

    @api.onchange("ssa_withholding_base")
    def _onchange_ssa_withholding_base(self):
        if not self.ssa_withholding_base:
            return
        domain = [("type_tax_use", "=", "purchase"), ("company_id", "=", self.company_id.id)]
        tax_base = self.env["account.tax"].search(domain + [("name", "=", "2% WHI")], limit=1)
        tax_base_iva = self.env["account.tax"].search(domain + [("name", "=", "2% WHI s/ base + IVA")], limit=1)
        target = tax_base if self.ssa_withholding_base == "base" else tax_base_iva
        if not target:
            return
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type == "product"):
            others = line.tax_ids.filtered(lambda t: t._origin.id not in (tax_base | tax_base_iva).ids)
            line.tax_ids = others | target

    def _ssa_refund_reason(self):
        """Motivo del abono sin el prefijo que añade Odoo ("Reversión de: INV/..., motivo")."""
        self.ensure_one()
        ref = self.ref or ""
        return re.sub(r"^(Reversión de|Reversal of):\s*[^,]*,\s*", "", ref)
