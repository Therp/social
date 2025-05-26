# Copyright 2016-2026 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models, tools


class MailTemplate(models.Model):
    _inherit = "mail.template"

    body_type = fields.Selection(
        [("qweb", "QWeb"), ("qweb_view", "QWeb View")],
        "Body templating engine",
        default="qweb",
        required=True,
    )
    body_view_id = fields.Many2one("ir.ui.view", domain=[("type", "=", "qweb")])
    body_view_arch = fields.Text(
        compute="_compute_body_view_arch",
        inverse="_inverse_body_view_arch",
        readonly=False,
    )
    edit_language = fields.Selection(
        selection="_get_edit_language_selection",
        default="en_US",
        help="Set the language to edit template",
    )

    def _get_edit_language_selection(self):
        """Selection for language to edit template."""
        active_languages = self.env["res.lang"].search(
            [("active", "=", True), ("code", "!=", "en_US")]
        )
        selection = [("en_US", "English (US)")] + [
            (lang.code, lang.name) for lang in active_languages
        ]
        return selection

    @api.depends("edit_language", "body_view_id.arch")
    def _compute_body_view_arch(self):
        for this in self:
            this.body_view_arch = this.body_view_id.with_context(
                lang=this.edit_language
            ).arch

    def _inverse_body_view_arch(self):
        for this in self:
            this.body_view_id.with_context(
                lang=this.edit_language
            ).arch = this.body_view_arch

    def generate_email(self, res_ids, fields):
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False
        result = super().generate_email(res_ids, fields=fields)
        if self.body_type != "qweb_view" or (fields and "body_html" not in fields):
            return result if multi_mode else result[res_ids[0]]
        for lang, (_template, template_res_ids) in self._classify_per_lang(
            res_ids
        ).items():
            self_with_lang = self.with_context(lang=lang)
            IrQweb = self_with_lang.env["ir.qweb"]
            for res_id in template_res_ids:
                record = self_with_lang.env[self_with_lang.model].browse(res_id)
                result_res_id = result[res_id]
                body_html = IrQweb._render(
                    self_with_lang.body_view_id.id,
                    {"object": record, "email_template": self_with_lang},
                )
                body_html = tools.ustr(body_html)
                rendered_post_temp = self_with_lang._render_template_postprocess(
                    {res_id: body_html}
                )
                result_res_id["body_html"] = rendered_post_temp[res_id]
                result_res_id["body"] = tools.html_sanitize(result_res_id["body_html"])
        return result if multi_mode else result[res_ids[0]]

    def copy_data(self, default=None):
        """Copy template view together with template.

        Users copy an email template usually to give it new contents. They
        consider the content they see (the body_view_arch) as an integral
        part of the email template.
        """
        self.ensure_one()
        if not default or "body_view_id" not in default:
            # There is no specific body_view_id already set in default.
            if self.body_view_id:
                # There is a body_view_id that can be copied.
                body_default = dict(
                    name=_("%s (copy)", self.body_view_id.name or ""),
                )
                new_view = self.body_view_id.copy(default=body_default)
                default = dict(
                    default or {},
                    body_view_id=new_view.id,
                )
        return super().copy_data(default=default)
