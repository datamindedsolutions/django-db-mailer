# -*- coding: utf-8 -*-

from dbmail.models import (
    MailTemplate, MailBcc, MailFromEmail,
    MailFile, MailFromEmailCredential,
)
from .base import BaseTestCase


class TemplateTestCase(BaseTestCase):

    def test_retrieve_named_template(self):
        """ create template and check queries """
        self._create_template()
        self._retrieve_named_template_and_check_num_queries(3)

    def test_retrieve_named_template_cached(self):
        """ check num of queries for cached template """
        self.test_retrieve_named_template()
        self._retrieve_named_template_and_check_num_queries(0)

    def test_retrieve_named_template_with_cache_invalidation(self):
        """ invalidate cached template """
        self.test_retrieve_named_template_cached()

        template = MailTemplate.get_template("welcome")
        self.assertEquals(template.subject, "Welcome")

        template.subject = "Hello"
        template.save()

        self._retrieve_named_template_and_check_num_queries(3)
        self.assertEquals(template.subject, "Hello")

    def test_retrieve_named_template_with_cache_invalidation_cache(self):
        """ check num of queries for cached template after invalidation """
        self.test_retrieve_named_template_with_cache_invalidation()
        template = self._retrieve_named_template_and_check_num_queries(0)
        self.assertEquals(template.subject, "Hello")

    ###########################################################################
    def test_retrieve_bcc(self):
        """ create template and check bcc """
        self._create_template()

        template = self._retrieve_named_template_and_check_num_queries(3)
        self.assertEquals(template.bcc_list, [])

    def test_retrieve_bcc_cached(self):
        """ create template and bcc cache """
        self.test_retrieve_bcc()
        self._retrieve_named_template_and_check_num_queries(0)

    def test_retrieve_bcc_cached_invalidation(self):
        """ invalidate cached bcc and add new bcc email """
        self.test_retrieve_bcc_cached()

        bcc = MailBcc.objects.create(email="root@local.host")
        template = MailTemplate.get_template("welcome")
        template.bcc_email.add(bcc)
        template.save()

        with self.assertNumQueries(3):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(template.bcc_list, ["root@local.host"])

    def test_retrieve_bcc_cached_invalidation_cache(self):
        """ check cached bcc with email """
        self.test_retrieve_bcc_cached_invalidation()

        with self.assertNumQueries(0):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(template.bcc_list, ["root@local.host"])

    def test_retrieve_bcc_delete(self):
        """ invalidate cached template when object was removed """
        self.test_retrieve_bcc_cached_invalidation_cache()

        for bcc in MailBcc.objects.all():
            bcc.delete()

        with self.assertNumQueries(3):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(template.bcc_list, [])

        self._retrieve_named_template_and_check_num_queries(0)

    ###########################################################################
    def test_retrieve_from(self):
        """ create template and check default email from """
        self._create_template()

        template = self._retrieve_named_template_and_check_num_queries(3)
        self.assertEquals(template.from_email, None)

    def test_retrieve_from_cached(self):
        """ create template and check email from cache """
        self.test_retrieve_from()
        self._retrieve_named_template_and_check_num_queries(0)

    def test_retrieve_from_cached_invalidation(self):
        """ invalidate cached from and add new email from """
        self.test_retrieve_from_cached()

        mail_from = MailFromEmail.objects.create(
            name="root", email="r@loc.hs", pk=1)
        template = MailTemplate.get_template("welcome")
        template.from_email = mail_from
        template.save()

        with self.assertNumQueries(3):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(
                template.from_email.get_mail_from, "root <r@loc.hs>")

    def test_retrieve_from_cached_invalidation_cache(self):
        """ check cached from with email """
        self.test_retrieve_from_cached_invalidation()

        with self.assertNumQueries(0):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(
                template.from_email.get_mail_from, "root <r@loc.hs>")

    def test_retrieve_from_delete(self):
        """ invalidate cached template when object was removed """
        self.test_retrieve_from_cached_invalidation_cache()

        mail_from = MailFromEmail.objects.get(pk=1)
        mail_from.delete()

        with self.assertNumQueries(3):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(template.from_email, None)

        self._retrieve_named_template_and_check_num_queries(0)

    ###########################################################################
    def test_retrieve_file(self):
        self._create_template()

        template = self._retrieve_named_template_and_check_num_queries(3)
        self.assertEquals(template.files_list, [])

    def test_retrieve_file_cached(self):
        self.test_retrieve_file()
        self._retrieve_named_template_and_check_num_queries(0)

    def test_retrieve_file_cached_invalidation(self):
        self.test_retrieve_file_cached()

        attachment = MailFile.objects.create(
            template_id=1, name="report.xls", filename="", pk=1)
        attachment.save()

        with self.assertNumQueries(3):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(template.files_list, [attachment])

    def test_retrieve_file_cached_invalidation_cache(self):
        self.test_retrieve_file_cached_invalidation()

        with self.assertNumQueries(0):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(len(template.files_list), 1)

    def test_retrieve_file_delete(self):
        self.test_retrieve_file_cached_invalidation_cache()

        attachment = MailFile.objects.get(pk=1)
        attachment.delete()

        with self.assertNumQueries(3):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(template.files_list, [])

        self._retrieve_named_template_and_check_num_queries(0)

    ###########################################################################
    def test_retrieve_auth(self):
        self._create_template()

        template = self._retrieve_named_template_and_check_num_queries(3)
        self.assertEquals(template.auth_credentials, None)

    def test_retrieve_auth_cached(self):
        self.test_retrieve_auth()
        self._retrieve_named_template_and_check_num_queries(0)

    def test_retrieve_auth_cached_invalidation(self):
        self.test_retrieve_auth_cached()

        credentials = MailFromEmailCredential.objects.create(
            host="localhost", port=25, id=1)
        credentials.save()

        mail_from = MailFromEmail.objects.create(
            name="root", email="r@loc.hs", credential=credentials)

        template = MailTemplate.get_template("welcome")
        template.from_email = mail_from
        template.save()

        with self.assertNumQueries(4):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(len(template.auth_credentials), 6)
            self.assertEquals(template.auth_credentials['port'], 25)

    def test_retrieve_auth_cached_invalidation_cache(self):
        self.test_retrieve_auth_cached_invalidation()

        with self.assertNumQueries(0):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(len(template.auth_credentials), 6)
            self.assertEquals(template.auth_credentials['port'], 25)

    def test_retrieve_auth_cached_invalidation_parent(self):
        self.test_retrieve_auth_cached_invalidation_cache()

        credentials = MailFromEmailCredential.objects.get(pk=1)
        credentials.port = 587
        credentials.save()

        with self.assertNumQueries(4):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(len(template.auth_credentials), 6)
            self.assertEquals(template.auth_credentials['port'], 587)

    def test_retrieve_auth_cached_invalidation_parent_cached(self):
        self.test_retrieve_auth_cached_invalidation_parent()

        with self.assertNumQueries(0):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(len(template.auth_credentials), 6)
            self.assertEquals(template.auth_credentials['port'], 587)

    def test_retrieve_auth_cached_delete(self):
        self.test_retrieve_auth_cached_invalidation_parent_cached()

        credentials = MailFromEmailCredential.objects.get(pk=1)
        credentials.delete()

        with self.assertNumQueries(3):
            template = MailTemplate.get_template("welcome")
            self.assertEquals(template.auth_credentials, None)
            self.assertEquals(template.from_email, None)


class LocalizedTemplateTestCase(BaseTestCase):

    def test_retrieve_localized_template(self):
        """ create template + localized template, and checks queries """
        self._create_localized_template()

        with self.assertNumQueries(4):
            template = MailTemplate.get_template("welcome", lang="es")
            self.assertEquals(template.subject, "Bienvenido")
            self.assertEquals(template.message, "Bienvenido a nuestro sitio. Nos alegra verte.")

    def test_retrieve_localized_template_from_cache(self):
        """ create template + localized template, and checks queries """
        self._create_localized_template()

        with self.assertNumQueries(4):
            template = MailTemplate.get_template("welcome", lang="es")
            self.assertEquals(template.subject, "Bienvenido")
            self.assertEquals(template.message, "Bienvenido a nuestro sitio. Nos alegra verte.")

        # ensures 0 queries are made after caching the localized template
        with self.assertNumQueries(0):
            template = MailTemplate.get_template("welcome", lang="es")
            self.assertEquals(template.subject, "Bienvenido")
            self.assertEquals(template.message, "Bienvenido a nuestro sitio. Nos alegra verte.")

    def test_template_does_not_exists(self):
        """ checks that fails gracefully when localized content does not exists """
        self._create_template()
        self.assertIsNotNone(MailTemplate.get_template("welcome"))
        # this should log an error and return the default template
        template = MailTemplate.get_template("welcome", lang="es")
        self.assertEquals(template.subject, "Welcome")
        self.assertEquals(template.message, "Welcome to our site. We are glad to see you.")
