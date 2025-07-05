from django.core.mail import EmailMultiAlternatives

from django.template.loader import render_to_string    # help to sent email

from django.conf import settings


def send_email(subject,recipient,template,context):

    mail = EmailMultiAlternatives(subject=subject,from_email=settings.EMAIL_HOST_USER,to=[recipient])
                                 #subject of email ,sender name,to-multiple user list

    content = render_to_string(template,context)

    mail.attach_alternative(content,'text/html')

    mail.send()    