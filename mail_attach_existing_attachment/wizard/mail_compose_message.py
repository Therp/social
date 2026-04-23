# Copyright 2015 ACSONE SA/NV
# Copyright 2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if (
            res.get("res_id")
            and res.get("model")
            and res.get("composition_mode", "") != "mass_mail"
            and not res.get("can_attach_attachment")
        ):
            res["can_attach_attachment"] = True  # pragma: no cover
        return res

    can_attach_attachment = fields.Boolean()
    object_attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="mail_compose_message_ir_attachments_object_rel",
        column1="wizard_id",
        column2="attachment_id",
        string="Object Attachments",
    )
    model_attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        string="Model Attachments",
    )

    def get_mail_values(self, res_ids):
        res = super().get_mail_values(res_ids)
        if self.model and len(res_ids) == 1:
            attachment_ids = set(res[res_ids[0]].get("attachment_ids", []))
            attachment_ids.update(self.object_attachment_ids.ids)
            attachment_ids.update(self.model_attachment_ids.ids)
            if attachment_ids:
                res[res_ids[0]]["attachment_ids"] = list(attachment_ids)
        return res
