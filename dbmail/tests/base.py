# -*- coding: utf-8 -*-

from django.test import TestCase

from dbmail.models import (
    MailTemplate, MailTemplateLocalizedContent,
)


class BaseTestCase(TestCase):

    def _create_template(self):
        return MailTemplate.objects.create(
            name="Site welcome template",
            subject="Welcome",
            message="Welcome to our site. We are glad to see you.",
            slug="welcome",
            is_html=False,
            id=1,
        )

    def _create_localized_template(self):
        template = self._create_template()
        return MailTemplateLocalizedContent.objects.create(
            template=template,
            lang="es",
            subject="Bienvenido",
            message="Bienvenido a nuestro sitio. Nos alegra verte.",
        )

    def _retrieve_named_template_and_check_num_queries(self, num):
        with self.assertNumQueries(num):
            template = MailTemplate.get_template("welcome")
            self.assertEqual(template.pk, 1)
            return template
