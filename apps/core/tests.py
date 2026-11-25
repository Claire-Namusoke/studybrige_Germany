from datetime import timedelta
from smtplib import SMTPException
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.core.models import (
    BlogPost,
    ConsultationRequest,
    Enquiry,
    Package,
    Service,
    Testimonial,
)


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
        self.assertNotContains(response, "University Admission")
        self.assertNotContains(response, "Draft service")

    @override_settings(DEBUG=True)
    def test_homepage_uses_marked_demo_services_when_none_are_published(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "University Admission")
        self.assertContains(response, "Settling in Germany")
        self.assertContains(response, "DEMO CONTENT")

    @override_settings(DEBUG=True)
    def test_homepage_marks_sample_tracker_and_story_content_as_demo(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Sample progress only")
        self.assertContains(response, "Demo stories")
        self.assertContains(response, "Amanda K.")
        self.assertContains(response, "Chat preview")
        self.assertContains(
            response,
            '<details class="home-chat-preview" aria-label="Chat preview">',
            html=False,
        )
        self.assertNotContains(
            response,
            '<details class="home-chat-preview" aria-label="Chat preview" open>',
            html=False,
        )

    @override_settings(DEBUG=False)
    def test_homepage_never_exposes_demo_content_outside_development(self):
        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, "500+ Students Supported")
        self.assertNotContains(response, "DEMO CONTENT")
        self.assertNotContains(response, "Amanda K.")
        self.assertNotContains(response, "Sample progress only")
        self.assertNotContains(response, "Chat preview")
        self.assertNotContains(response, "SAMPLE COPY")
        self.assertNotContains(response, "Expert knowledge of the German education system")
        self.assertContains(response, "Start with a conversation.")

    def test_homepage_shows_only_consented_published_testimonials(self):
        Testimonial.objects.create(
            display_name="Approved student",
            quote="A real, approved experience.",
            is_published=True,
            consent_confirmed=True,
        )
        Testimonial.objects.create(
            display_name="Unpublished student",
            quote="This story is not public.",
        )

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Approved student")
        self.assertContains(response, "A real, approved experience.")
        self.assertNotContains(response, "Amanda K.")
        self.assertNotContains(response, "Unpublished student")

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


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="StudyBridge Germany <no-reply@example.test>",
    BUSINESS_NOTIFICATION_EMAIL="team@example.test",
)
class RequestFormTests(TestCase):
    def setUp(self):
        if hasattr(mail, "outbox"):
            mail.outbox.clear()

    def test_enquiry_is_saved_and_sends_customer_and_team_notifications(self):
        response = self.client.post(
            reverse("core:enquiry"),
            {
                "full_name": "Alex Student",
                "email": "alex@example.test",
                "phone": "",
                "country": "Canada",
                "service": "",
                "message": "I would like to learn about study options.",
                "privacy_consent": "on",
            },
            follow=True,
        )

        enquiry = Enquiry.objects.get(email="alex@example.test")
        self.assertEqual(enquiry.status, Enquiry.Status.NEW)
        self.assertTrue(enquiry.privacy_consent)
        self.assertIsNotNone(enquiry.privacy_consent_at)
        self.assertContains(response, f"Reference: {enquiry.reference}")
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(str(enquiry.reference), mail.outbox[0].body)
        self.assertIn(str(enquiry.reference), mail.outbox[1].body)
        self.assertNotIn(enquiry.message, mail.outbox[1].body)

    def test_enquiry_without_privacy_acknowledgement_is_not_saved(self):
        response = self.client.post(
            reverse("core:enquiry"),
            {
                "full_name": "Alex Student",
                "email": "alex@example.test",
                "country": "Canada",
                "message": "I would like to learn about study options.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Enquiry.objects.count(), 0)
        self.assertContains(response, "This field is required.")

    def test_consultation_request_is_pending_until_manually_confirmed(self):
        preferred_date = timezone.localdate() + timedelta(days=3)
        response = self.client.post(
            reverse("core:consultation"),
            {
                "full_name": "Alex Student",
                "email": "alex@example.test",
                "country": "Canada",
                "service": "",
                "preferred_date": preferred_date.isoformat(),
                "preferred_time": ConsultationRequest.PreferredTime.MORNING,
                "message": "I would like to discuss study planning.",
                "privacy_consent": "on",
            },
            follow=True,
        )

        consultation = ConsultationRequest.objects.get(email="alex@example.test")
        self.assertEqual(consultation.status, ConsultationRequest.Status.REQUESTED)
        self.assertIsNone(consultation.scheduled_at)
        self.assertIsNotNone(consultation.privacy_consent_at)
        self.assertContains(response, f"Reference: {consultation.reference}")
        self.assertIn("not a confirmed appointment", mail.outbox[0].body)

    def test_past_consultation_date_is_rejected(self):
        preferred_date = timezone.localdate() - timedelta(days=1)
        response = self.client.post(
            reverse("core:consultation"),
            {
                "full_name": "Alex Student",
                "email": "alex@example.test",
                "preferred_date": preferred_date.isoformat(),
                "preferred_time": ConsultationRequest.PreferredTime.MORNING,
                "privacy_consent": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConsultationRequest.objects.count(), 0)
        self.assertContains(response, "Choose today or a future date.")

    def test_database_rejects_confirmed_consultation_without_schedule(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ConsultationRequest.objects.create(
                    full_name="Alex Student",
                    email="alex@example.test",
                    preferred_date=timezone.localdate() + timedelta(days=1),
                    preferred_time=ConsultationRequest.PreferredTime.MORNING,
                    privacy_consent=True,
                    status=ConsultationRequest.Status.CONFIRMED,
                )

    @patch("apps.core.notifications.send_mail", side_effect=SMTPException("SMTP unavailable"))
    def test_email_failure_does_not_discard_saved_enquiry(self, _send_mail):
        with self.assertLogs("apps.core.notifications", level="ERROR"):
            response = self.client.post(
                reverse("core:enquiry"),
                {
                    "full_name": "Alex Student",
                    "email": "alex@example.test",
                    "message": "I would like to learn about study options.",
                    "privacy_consent": "on",
                },
                follow=True,
            )

        self.assertEqual(Enquiry.objects.count(), 1)
        self.assertContains(response, "could not send a confirmation email")
