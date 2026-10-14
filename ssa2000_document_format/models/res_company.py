from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ssa_registry_code = fields.Char(
        string="Registro Junta de Andalucía",
        help="Código de registro que se imprime en el encabezado de albaranes y facturas.",
    )
