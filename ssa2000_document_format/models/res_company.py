from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ssa_registry_code = fields.Char(
        string="Registro Junta de Andalucía",
        help="Código de registro que se imprime en el encabezado de albaranes y facturas.",
    )
    ssa_delivery_footer = fields.Html(
        string="Pie de albarán",
        help="Pie que se imprime en los albaranes en lugar del pie general de la compañía.",
    )

    ssa_signer_name = fields.Char(string="Firmante (nombre y apellidos)")
    ssa_signer_vat = fields.Char(string="Firmante (DNI)")
    ssa_signer_position = fields.Char(string="Firmante (cargo)")

    @api.model
    def _ssa_set_default_registry_code(self):
        """Registro de productores y distribuidores de la compañía principal, si no está informado."""
        company = self.env.ref("base.main_company", raise_if_not_found=False)
        if company and not company.ssa_registry_code:
            company.ssa_registry_code = "ESP41000642"
        if company and not company.ssa_signer_name:
            company.write(
                {
                    "ssa_signer_name": "Nicolás Montero Pradas",
                    "ssa_signer_vat": "28482065S",
                    "ssa_signer_position": "Administrador Único",
                }
            )
