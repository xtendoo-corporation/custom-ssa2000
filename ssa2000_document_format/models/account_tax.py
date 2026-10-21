from odoo import models


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _ssa_create_irpf_base_iva_tax(self):
        """Crea, copiando el "2% WHI" de cada compañía, la retención del 2% sobre base + IVA 12%.

        El IVA agrario es del 12%, así que 2% de (base + 12% de base) equivale a un -2,24% de la base.
        Es idempotente: si el impuesto ya existe no hace nada.
        """
        name = "2% WHI s/ base + IVA"
        for company in self.env["res.company"].search([]):
            taxes = self.with_company(company).with_context(active_test=False)
            if taxes.search([("name", "=", name), ("company_id", "=", company.id)]):
                continue
            source = taxes.search(
                [
                    ("name", "=", "2% WHI"),
                    ("type_tax_use", "=", "purchase"),
                    ("company_id", "=", company.id),
                ],
                limit=1,
            )
            if source:
                source.copy({"name": name, "amount": -2.24})
