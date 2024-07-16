This module was written to surpress all notification messages from Odoo.

In the maze of code that provides email functionality, it is very
difficult, if not impossible, to configure Odoo to not send all
kinds of unwanted mail notifications to customers or users, and to
limit email actually to email that we conciously decide to sent.

This module will try to prevent all these notifications, by not
sending them out, but still logging the attempt to sent them.

A possible extention would be to whitelist certain notifications,
based on the message subtype, the sender or the desired recipient.
