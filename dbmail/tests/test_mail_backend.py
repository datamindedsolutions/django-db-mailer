# -*- coding: utf-8 -*-

from django.core import mail

from dbmail.backends.mail import Sender
from dbmail.defaults import BACKEND

from .base import BaseTestCase


class MailSenderBackendTestCase(BaseTestCase):

    def setUp(self):
        self._create_localized_template()
        self.sender = Sender("welcome", "user1@example.com", backend=BACKEND["mail"])

    def test_get_template(self):
        # tests it without lang
        template = self.sender._get_template()
        self.assertEquals(template.subject, "Welcome")
        self.assertEquals(template.message, "Welcome to our site. We are glad to see you.")
        # tests it passing lang
        template = self.sender._get_template(lang="es")
        self.assertEquals(template.subject, "Bienvenido")
        self.assertEquals(template.message, "Bienvenido a nuestro sitio. Nos alegra verte.")
        # tests lang not available
        template = self.sender._get_template(lang="fr")
        self.assertEquals(template.subject, "Welcome")
        self.assertEquals(template.message, "Welcome to our site. We are glad to see you.")

    def test_send(self):
        # test send email without passing lang
        self.assertEquals(self.sender.send(), "OK")
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, "Welcome")
        self.assertEquals(mail.outbox[0].body, "Welcome to our site. We are glad to see you.")
        # test send email passing lang to the sender
        localized_sender = Sender("welcome", "user1@example.com", lang="es", backend=BACKEND["mail"])
        self.assertEquals(localized_sender.send(), "OK")
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[1].subject, "Bienvenido")
        self.assertEquals(mail.outbox[1].body, "Bienvenido a nuestro sitio. Nos alegra verte.")
        # test send email passing lang not available sends default version
        localized_sender = Sender("welcome", "user1@example.com", lang="fr", backend=BACKEND["mail"])
        self.assertEquals(localized_sender.send(), "OK")
        self.assertEquals(len(mail.outbox), 3)
        self.assertEquals(mail.outbox[2].subject, "Welcome")
        self.assertEquals(mail.outbox[2].body, "Welcome to our site. We are glad to see you.")
