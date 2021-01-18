# -*- coding: utf-8 -*-
from mock import patch

from django.core import mail

from dbmail.backends.mail import Sender
from dbmail.defaults import BACKEND

from .base import BaseTestCase


class MailSenderBackendTestCase(BaseTestCase):

    def setUp(self):
        self._create_localized_template()
        self.sender = Sender("welcome", "user1@example.com", backend=BACKEND["mail"])

    @patch('dbmail.models.logger')
    def test_get_template(self, mock_logger):
        # tests it without lang
        template = self.sender._get_template()
        self.assertEquals(template.subject, "Welcome")
        self.assertEquals(template.message, "Welcome to our site. We are glad to see you.")
        assert mock_logger.error.call_count == 0, 'Error was logged for no language {}'.format(
            mock_logger.error.__dict__)

        # tests it passing 'en', which are stored in MailTemplate
        template = self.sender._get_template(lang='en')
        self.assertEquals(template.subject, "Welcome")
        self.assertEquals(template.message, "Welcome to our site. We are glad to see you.")
        assert mock_logger.error.call_count == 0, 'Error was logged for "en" language {}'.format(
            mock_logger.error.__dict__)

        # tests it passing lang
        template = self.sender._get_template(lang="es")
        self.assertEquals(template.subject, "Bienvenido")
        self.assertEquals(template.message, "Bienvenido a nuestro sitio. Nos alegra verte.")
        assert mock_logger.error.call_count == 0, 'Error was logged for "es" language {}'.format(
            mock_logger.error.__dict__)

        # tests lang not available
        template = self.sender._get_template(lang="fr")
        self.assertEquals(template.subject, "Welcome")
        self.assertEquals(template.message, "Welcome to our site. We are glad to see you.")
        assert mock_logger.error.call_count == 1, 'Error was NOT logged for "fr" language {}'.format(
            mock_logger.error.__dict__)
        mock_logger.error.assert_called_with('Localized template not found for lang={}, slug={}'.format('fr', 'welcome'))

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
        # test send email with custom base_template and without lang
        self._create_localized_template_with_base()
        sender = Sender("welcome_with_base", "user1@example.com", backend=BACKEND["mail"])
        self.assertEquals(sender.send(), "OK")
        self.assertEquals(len(mail.outbox), 4)
        self.assertEquals(mail.outbox[3].subject, "Welcome")
        self.assertEquals(mail.outbox[3].body, "Base Template: Welcome to our site. We are glad to see you.")
        # test send email with custom base_template and custom lang
        localized_sender = Sender("welcome_with_base", "user1@example.com", lang="es", backend=BACKEND["mail"])
        self.assertEquals(localized_sender.send(), "OK")
        self.assertEquals(len(mail.outbox), 5)
        self.assertEquals(mail.outbox[4].subject, "Bienvenido")
        self.assertEquals(mail.outbox[4].body, "Base Template: Bienvenido a nuestro sitio. Nos alegra verte.")

    def test_get_message_with_base(self):
        base_template = self._create_base_template()
        message = self.sender._get_message_with_base(base_template)
        self.assertEquals(message, "Test Base Template")

    def test_get_message_base(self):
        # tests without passing base_template
        message = self.sender._get_message()
        self.assertEquals(message, "Welcome to our site. We are glad to see you.")
        # tests passing base_template
        base_template = self._create_base_template()
        message = self.sender._get_message(base_template=base_template)
        self.assertEquals(message, "Test Base Template")
        # test calling when the template already has a base template
        self._create_template_with_base()
        sender_with_base = Sender("welcome_with_base", "user1@example.com", lang="en", backend=BACKEND["mail"])
        message = sender_with_base._get_message()
        self.assertEquals(message, "Welcome to our site. We are glad to see you.")
        # test calling it with a base_template when the template already has a base
        message = sender_with_base._get_message(base_template=base_template)
        self.assertEquals(message, "Test Base Template")
