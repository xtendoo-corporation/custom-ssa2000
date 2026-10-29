import re

from odoo import api, fields, models
from odoo.tools import format_date


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ssa_weight_mode = fields.Selection(
        [
            ("net", "Toneladas netas / unidades"),
            ("gross_tare", "Toneladas brutas, tara y netas"),
        ],
        string="Cantidades del albarán",
        default="gross_tare",
        required=True,
        copy=True,
        help="Neto: se imprime una sola columna 'Tn. netas / unidades'. "
        "Bruto y tara: se imprimen también las columnas Tn. bruto y Tn. tara.",
    )
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

    ssa_is_canarias = fields.Boolean(
        string="Destino Canarias",
        compute="_compute_ssa_is_canarias",
        store=True,
        readonly=False,
        help="Se marca solo si el destinatario está en Las Palmas o Santa Cruz de Tenerife; se puede cambiar a mano.",
    )
    ssa_canarias_line_ids = fields.One2many("ssa.canarias.line", "picking_id", string="Datos de envío a Canarias")
    ssa_invoice_number = fields.Char(
        string="Nº de factura",
        compute="_compute_ssa_invoice",
        store=True,
        readonly=False,
    )
    ssa_invoice_date = fields.Date(
        string="Fecha de factura",
        compute="_compute_ssa_invoice",
        store=True,
        readonly=False,
    )

    @api.depends("partner_id.state_id")
    def _compute_ssa_is_canarias(self):
        for picking in self:
            picking.ssa_is_canarias = picking.partner_id.state_id.code in ("GC", "TF")

    @api.depends("sale_id.invoice_ids.name", "sale_id.invoice_ids.state", "sale_id.invoice_ids.invoice_date")
    def _compute_ssa_invoice(self):
        for picking in self:
            invoice = picking.sale_id.invoice_ids.filtered(
                lambda m: m.state == "posted" and m.move_type == "out_invoice"
            )[:1]
            if invoice:
                picking.ssa_invoice_number = invoice.name
                picking.ssa_invoice_date = invoice.invoice_date
            else:
                picking.ssa_invoice_number = picking.ssa_invoice_number
                picking.ssa_invoice_date = picking.ssa_invoice_date

    def _ssa_canarias_reference(self):
        """Nº de referencia del Anexo IV: la parte final numérica del número de factura (26.385 -> 385)."""
        self.ensure_one()
        groups = re.findall(r"\d+", self.ssa_invoice_number or "")
        return str(int(groups[-1])) if groups else ""

    def _ssa_canarias_date_text(self):
        self.ensure_one()
        date = self.date_done or self.scheduled_date or fields.Datetime.now()
        return format_date(self.env, date, lang_code="es_ES", date_format="d 'de' MMMM 'de' y")

    def _ssa_prepare_canarias_lines(self):
        """Crea una línea por movimiento que aún no la tenga, con los datos del albarán."""
        self.ensure_one()
        existing = self.ssa_canarias_line_ids.move_id
        vals = []
        for move in self.move_ids.filtered(lambda m: m.quantity or m.product_uom_qty):
            if move in existing:
                continue
            vals.append(
                {
                    "picking_id": self.id,
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "units": move.ssa_units,
                    "net_kg": move.ssa_net_weight * 1000.0,
                    "lot": self.ssa_origin_lot,
                }
            )
        if vals:
            self.env["ssa.canarias.line"].create(vals)

    def _ssa_canarias_rows(self):
        """Filas de datos para las plantillas del pack de Canarias."""
        self.ensure_one()
        rows = []
        for line in self.ssa_canarias_line_ids:
            move = line.move_id
            tons = line.net_kg / 1000.0
            price = move.ssa_price_unit if move else 0.0
            rows.append(
                {
                    "line": line,
                    "product": line.product_id,
                    "tons": tons,
                    "gross": move.ssa_gross_weight if move else 0.0,
                    "tare": move.ssa_tare_weight if move else 0.0,
                    "price": price,
                    "amount": tons * price,
                }
            )
        return rows

    def action_ssa_open_canarias(self):
        self.ensure_one()
        self._ssa_prepare_canarias_lines()
        view = self.env.ref("ssa2000_document_format.view_picking_canarias_form_ssa2000")
        return {
            "type": "ir.actions.act_window",
            "name": "Datos de envío a Canarias",
            "res_model": "stock.picking",
            "res_id": self.id,
            "view_mode": "form",
            "views": [(view.id, "form")],
            "target": "new",
        }

    def action_ssa_print_canarias(self):
        self.ensure_one()
        return self.env.ref("ssa2000_document_format.action_report_canarias_ssa2000").report_action(self)
