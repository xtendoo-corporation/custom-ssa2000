from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ssa_origin_supplier_id = fields.Many2one(
        "res.partner",
        string="Proveedor origen mercancía",
        copy=False,
    )
    ssa_origin_farm = fields.Char(string="Desde la finca", copy=False)
    ssa_carrier_name = fields.Char(string="Transportista", copy=False)
    ssa_vehicle_plate = fields.Char(string="Matrícula", copy=False)
    ssa_trip_number = fields.Char(string="Núm. viaje", copy=False)
    ssa_origin_lot = fields.Char(string="Lote de origen", copy=False)

    def _ssa_has_origin_info(self):
        self.ensure_one()
        return any(
            (
                self.ssa_origin_supplier_id,
                self.ssa_origin_farm,
                self.ssa_carrier_name,
                self.ssa_vehicle_plate,
                self.ssa_trip_number,
                self.ssa_origin_lot,
            )
        )
