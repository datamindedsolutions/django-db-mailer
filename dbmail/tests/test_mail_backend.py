# -*- coding: utf-8 -*-


from dbmail.backends.mail import Sender
from dbmail.defaults import BACKEND

from .base import BaseTestCase


class MailSenderBackendTestCase(BaseTestCase):

    def setUp(self):
        self._create_localized_template()
        self.sender = Sender("welcome", "user1@example.com", backend=BACKEND['mail'])

    def test_get_template(self):
        # tests it without lang
        template = self.sender._get_template()
        self.assertEquals(template.subject, "Welcome")
        self.assertEquals(template.message, "Welcome to our site. We are glad to see you.")
        # tests it passing lang
        template = self.sender._get_template(lang="es")
        self.assertEquals(template.subject, "Bienvenido")
        self.assertEquals(template.message, "Bienvenido a nuestro sitio. Nos alegra verte.")
