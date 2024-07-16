# Copyright 2024 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    """Override message send to not send motifications."""

    _inherit = "mail.mail"

    def send(self, auto_commit=False, raise_exception=False):
        """Intercept notification messages and send the remaining ones if any."""
        notification_mails = self.filtered(
            lambda r: r.is_notification
            or r.mail_message_id.message_type in ("notification", "user_notification")
        )
        for mail in notification_mails:
            mail._send_into_blackhole()
        true_mails = self - notification_mails
        if true_mails:
            return super(MailMail, true_mails).send(
                auto_commit=auto_commit, raise_exception=raise_exception
            )
        return None

    def _send_into_blackhole(self):
        """Just log the attempt to send the notification."""
        self.ensure_one()
        _logger.debug(
            "Not sending message with subject %(subject)s", {"subject": self.subject}
        )
        if self.auto_delete:
            self.sudo().unlink()
        else:
            self.write({"state": "sent"})
