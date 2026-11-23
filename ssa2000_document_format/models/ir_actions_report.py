import io

from odoo import models
from odoo.tools.pdf import merge_pdf


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        collected = super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids=res_ids)
        report = self._get_report(report_ref)
        if report.model != "account.move" or report.report_name.startswith("ssa2000_document_format."):
            return collected
        annexes_report = self.env.ref("ssa2000_document_format.action_report_canarias_annexes_ssa2000")
        for move in self.env["account.move"].browse(list(collected)):
            values = collected[move.id]
            # Si el PDF viene de un adjunto guardado ya lleva los anexos
            if not values.get("stream") or (values.get("attachment") and report.attachment_use):
                continue
            picking = move._ssa_canarias_picking()
            if not picking:
                continue
            # Las páginas de Canarias van con su propio formato (márgenes de 12 mm), no con el de la factura
            annexes_pdf, _fmt = annexes_report.with_context(report_pdf_no_attachment=True)._render_qweb_pdf(
                annexes_report, picking.ids
            )
            values["stream"] = io.BytesIO(merge_pdf([values["stream"].getvalue(), annexes_pdf]))
        return collected
