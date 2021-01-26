import mimetypes
import os.path
import re
from email.mime.base import MIMEBase

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from rwanda.administration.utils import param_currency, param_base_price
from rwanda.purchase.models import ServicePurchase, ServicePurchaseUpdateRequest, Litigation
from rwanda.service.models import Service
from rwanda.settings import BASE_DIR
from rwanda.user.models import User

base_files = [
    "static/emails/images/favicon.png",
    "static/emails/images/facebook2x.png",
    "static/emails/images/twitter2x.png",
    "static/emails/images/instagram2x.png",
    "static/emails/images/youtube2x.png",
]


class EmailMultiRelated(EmailMultiAlternatives):
    """
    A version of EmailMessage that makes it easy to send multipart/related
    messages. For example, including text and HTML versions with inline images.

    @see https://djangosnippets.org/snippets/2215/
    """
    related_subtype = 'related'

    def __init__(self, *args, **kwargs):
        # self.related_ids = []
        self.related_attachments = []
        super(EmailMultiRelated, self).__init__(*args, **kwargs)

    def attach_related(self, filename=None, content=None, mimetype=None):
        """
        Attaches a file with the given filename and content. The filename can
        be omitted and the mimetype is guessed, if not provided.

        If the first parameter is a MIMEBase subclass it is inserted directly
        into the resulting message attachments.
        """
        if isinstance(filename, MIMEBase):
            assert content == mimetype is None
            self.related_attachments.append(filename)
        else:
            assert content is not None
            self.related_attachments.append((filename, content, mimetype))

    def attach_related_file(self, path, mimetype=None):
        """Attaches a file from the filesystem."""
        filename = os.path.basename(path)
        content = open(path, 'rb').read()
        self.attach_related(filename, content, mimetype)

    def _create_message(self, msg):
        return self._create_attachments(self._create_related_attachments(self._create_alternatives(msg)))

    def _create_alternatives(self, msg):
        for i, (content, mimetype) in enumerate(self.alternatives):
            if mimetype == 'text/html':
                for related_attachment in self.related_attachments:
                    if isinstance(related_attachment, MIMEBase):
                        content_id = related_attachment.get('Content-ID')
                        content = re.sub(r'(?<!cid:)%s' % re.escape(content_id), 'cid:%s' % content_id, content)
                    else:
                        filename, _, _ = related_attachment
                        content = re.sub(r'(?<!cid:)%s' % re.escape(filename), 'cid:%s' % filename, content)
                self.alternatives[i] = (content, mimetype)

        return super(EmailMultiRelated, self)._create_alternatives(msg)

    def _create_related_attachments(self, msg):
        encoding = self.encoding or settings.DEFAULT_CHARSET
        if self.related_attachments:
            body_msg = msg
            msg = SafeMIMEMultipart(_subtype=self.related_subtype, encoding=encoding)
            if self.body:
                msg.attach(body_msg)
            for related_attachment in self.related_attachments:
                if isinstance(related_attachment, MIMEBase):
                    msg.attach(related_attachment)
                else:
                    msg.attach(self._create_related_attachment(*related_attachment))
        return msg

    def _create_related_attachment(self, filename, content, mimetype=None):
        """
        Convert the filename, content, mimetype triple into a MIME attachment
        object. Adjust headers to use Content-ID where applicable.
        Taken from http://code.djangoproject.com/ticket/4771
        """
        attachment = super(EmailMultiRelated, self)._create_attachment(filename, content, mimetype)
        if filename:
            mimetype = attachment['Content-Type']
            del (attachment['Content-Type'])
            del (attachment['Content-Disposition'])
            attachment.add_header('Content-Disposition', 'inline', filename=filename)
            attachment.add_header('Content-Type', mimetype, name=filename)
            attachment.add_header('Content-ID', '<%s>' % filename)
        return attachment


def attach_related_file(msg, files):
    for file in files:
        file = os.path.join(BASE_DIR, file)
        mimetypes.MimeTypes().guess_type(file)
        msg.attach_related_file(file, mimetypes.MimeTypes().guess_type(file)[0])


def send_mail(subject, template, data, email, files=None):
    if files is None:
        files = base_files

    body = render_to_string(template, data).strip()
    msg = EmailMultiRelated(subject, body, to=[email])
    attach_related_file(msg, files)
    msg.content_subtype = "html"
    msg.send()


def send_verification_mail(user: User):
    send_mail(_('Activate your account'),
              "mails/very_account.html",
              {
                  "activate_url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/activate/' + str(user.id),
                  "user": user
              },
              user.email,
              base_files + ["static/emails/images/Thanks.png"]
              )


def on_service_accepted_or_rejected(service: Service):
    data = {"currency": param_currency(),
            "base_price": param_base_price(),
            "service": service,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/services/' + str(service.id)}

    send_mail(_("Service accepted") if service.accepted else _("Service rejected"),
              "mails/services/accepted.html" if service.accepted else "mails/services/rejected.html",
              data,
              service.account.user.email)


def on_service_purchase_initiated(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(service_purchase.id)}

    send_mail(_("Purchase"),
              "mails/services/purchases/initiated.html",
              data,
              service_purchase.buyer.user.email)

    data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)
    send_mail(_("New order"),
              "mails/services/orders/initiated.html",
              data,
              service_purchase.seller.user.email)


def on_service_purchase_accepted_or_refused(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(service_purchase.id)}

    send_mail(_("Purchase accepted") if service_purchase.accepted else _("Purchase refused"),
              "mails/services/purchases/accepted_or_refused.html",
              data,
              service_purchase.buyer.user.email)


def on_service_purchase_delivered(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(service_purchase.id)}

    send_mail(_("Purchase delivered"),
              "mails/services/purchases/delivered.html",
              data,
              service_purchase.buyer.user.email)


def on_service_purchase_approved(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)}

    send_mail(_("Order approved"),
              "mails/services/purchases/approved.html",
              data,
              service_purchase.seller.user.email)


def on_service_purchase_canceled(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)}

    send_mail(_("Order canceled"),
              "mails/services/purchases/canceled.html",
              data,
              service_purchase.seller.user.email)


def send_service_purchase_deadline_reminder(service_purchase: ServicePurchase):
    data = {"currency": param_currency(),
            "purchase": service_purchase,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(service_purchase.id)}

    send_mail(_("Deadline reminder"),
              "mails/services/purchases/deadline_reminder.html",
              data,
              service_purchase.seller.user.email)


def on_service_purchase_update_request_initiated(service_purchase_update_request: ServicePurchaseUpdateRequest):
    data = {"currency": param_currency(),
            "update_request": service_purchase_update_request,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
                service_purchase_update_request.service_purchase.id)}

    send_mail(_("Update requested"),
              "mails/services/update_requests/initiated.html",
              data,
              service_purchase_update_request.service_purchase.seller.user.email)


def on_service_purchase_update_request_accepted_or_refused(
        service_purchase_update_request: ServicePurchaseUpdateRequest):
    data = {"currency": param_currency(),
            "update_request": service_purchase_update_request,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
                service_purchase_update_request.service_purchase.id)}

    send_mail(_("Update request accepted") if service_purchase_update_request.accepted else _("Update request refused"),
              "mails/services/update_requests/accepted_or_refused.html",
              data,
              service_purchase_update_request.service_purchase.buyer.user.email)


def on_service_purchase_update_request_delivered(service_purchase_update_request: ServicePurchaseUpdateRequest):
    data = {"currency": param_currency(),
            "update_request": service_purchase_update_request,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(
                service_purchase_update_request.service_purchase.id)}

    send_mail(_("Update delivered"),
              "mails/services/update_requests/delivered.html",
              data,
              service_purchase_update_request.service_purchase.buyer.user.email)


def on_litigation_opened(litigation: Litigation):
    data = {"currency": param_currency(),
            "litigation": litigation,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(litigation.service_purchase.id)}

    send_mail(_("Litigation opened"),
              "mails/services/disputes/opened.html",
              data,
              litigation.service_purchase.buyer.user.email)

    data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(litigation.service_purchase.id)
    send_mail(_("Litigation opened"),
              "mails/services/disputes/opened.html",
              data,
              litigation.service_purchase.seller.user.email)


def on_litigation_handled(litigation: Litigation):
    data = {"currency": param_currency(),
            "litigation": litigation,
            "url": settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/purchases/' + str(litigation.service_purchase.id)}

    send_mail(litigation.decision_display,
              "mails/services/disputes/handled.html",
              data,
              litigation.service_purchase.buyer.user.email)

    data["url"] = settings.FRONTEND_ACCOUNT_BASE_URL + '/#/account/orders/' + str(litigation.service_purchase.id)
    send_mail(litigation.decision_display,
              "mails/services/disputes/handled.html",
              data,
              litigation.service_purchase.seller.user.email)
