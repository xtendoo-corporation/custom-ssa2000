from odoo import fields, models


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

    def _ssa_set_default_registry_code(self):
        """Registro de productores y distribuidores de la compañía principal, si no está informado."""
        company = self.env.ref("base.main_company", raise_if_not_found=False)
        if company and not company.ssa_registry_code:
            company.ssa_registry_code = "ESP41000642"
