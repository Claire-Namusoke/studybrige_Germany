from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.core.models import BlogPost, Package, Service, Testimonial


class PublicContentTests(TestCase):
    def test_content_index_pages_render_with_empty_content(self):
        page_names = (
            "core:service_list",
            "core:package_list",
            "core:faq_list",
            "core:testimonial_list",
            "core:blog_list",
        )

        for page_name in page_names:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)

    def test_homepage_shows_only_published_services(self):
        Service.objects.create(
            title="Study planning",
            slug="study-planning",
            summary="Plan your study journey.",
            description="Guidance for your study plans.",
            is_published=True,
        )
        Service.objects.create(
            title="Draft service",
            slug="draft-service",
            summary="Not public yet.",
            description="Draft copy.",
        )

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "StudyBridge Germany")
        self.assertContains(response, "Study planning")
        self.assertNotContains(response, "Draft service")

    def test_published_service_has_a_public_detail_page(self):
        service = Service.objects.create(
            title="Study planning",
            slug="study-planning",
            summary="Plan your study journey.",
            description="Guidance for your study plans.",
            is_published=True,
        )

        response = self.client.get(
            reverse("core:service_detail", kwargs={"slug": service.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guidance for your study plans.")

    def test_draft_service_is_not_public(self):
        service = Service.objects.create(
            title="Draft service",
            slug="draft-service",
            summary="Not public yet.",
            description="Draft copy.",
        )

        response = self.client.get(
            reverse("core:service_detail", kwargs={"slug": service.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_only_published_packages_are_listed(self):
        Package.objects.create(
            title="Published package",
            slug="published-package",
            summary="Available package.",
            is_published=True,
        )
        Package.objects.create(
            title="Draft package",
            slug="draft-package",
            summary="Not available yet.",
        )

        response = self.client.get(reverse("core:package_list"))

        self.assertContains(response, "Published package")
        self.assertNotContains(response, "Draft package")

    def test_testimonial_cannot_be_published_without_consent(self):
        testimonial = Testimonial(
            display_name="A student",
            quote="A sample quote.",
            is_published=True,
        )

        with self.assertRaises(ValidationError):
            testimonial.full_clean()

    def test_database_rejects_testimonial_publication_without_consent(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Testimonial.objects.create(
                    display_name="A student",
                    quote="A sample quote.",
                    is_published=True,
                    consent_confirmed=False,
                )

    def test_only_consented_published_testimonials_are_public(self):
        Testimonial.objects.create(
            display_name="Published student",
            quote="A shared experience.",
            is_published=True,
            consent_confirmed=True,
        )
        Testimonial.objects.create(
            display_name="Unpublished student",
            quote="Not approved for publication.",
        )

        response = self.client.get(reverse("core:testimonial_list"))

        self.assertContains(response, "Published student")
        self.assertNotContains(response, "Unpublished student")

    def test_draft_blog_post_is_not_public(self):
        BlogPost.objects.create(
            title="Draft article",
            slug="draft-article",
            excerpt="Not ready.",
            body="Draft copy.",
        )

        response = self.client.get(reverse("core:blog_list"))

        self.assertNotContains(response, "Draft article")

    def test_published_blog_post_gets_a_publication_time(self):
        post = BlogPost.objects.create(
            title="Preparing your study plan",
            slug="preparing-your-study-plan",
            excerpt="A short overview.",
            body="The full article.",
            status=BlogPost.Status.PUBLISHED,
        )

        self.assertIsNotNone(post.published_at)
        self.assertContains(self.client.get(reverse("core:blog_list")), post.title)
