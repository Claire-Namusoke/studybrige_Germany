from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_homepage_renders_primary_sections(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "StudyBridge Germany")
        self.assertContains(response, 'id="services"')
        self.assertContains(response, 'id="approach"')
