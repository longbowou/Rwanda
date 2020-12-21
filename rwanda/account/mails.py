from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


def send_verification_mail(user):
    subject = _('Verify Your Email Account')
    activate_url = 'https://mdtaf.com/#/activate/' + str(user.id)
    body = render_to_string("emails/very_account.html",
                            {
                                "activate_url": activate_url,
                                "user": user
                            }).strip()
    msg = EmailMultiAlternatives(subject, body, to=[user.email])
    msg.content_subtype = "html"
    msg.send()
