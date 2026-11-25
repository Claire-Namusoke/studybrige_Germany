import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Service(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    summary = models.CharField(max_length=320)
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "title")

    def __str__(self):
        return self.title


class Package(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    summary = models.CharField(max_length=320)
    services = models.ManyToManyField(Service, related_name="packages", blank=True)
    price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(max_length=3, default="EUR")
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "title")

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=240)
    answer = models.TextField()
    service = models.ForeignKey(
        Service,
        related_name="faqs",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "question")
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    display_name = models.CharField(max_length=120)
    quote = models.TextField()
    context = models.CharField(max_length=180, blank=True)
    consent_confirmed = models.BooleanField(
        default=False,
        help_text="Confirm the student has agreed to publication before publishing.",
    )
    is_published = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("display_order", "-created_at")
        constraints = [
            models.CheckConstraint(
                condition=Q(is_published=False) | Q(consent_confirmed=True),
                name="testimonial_publication_requires_consent",
            ),
        ]

    def clean(self):
        super().clean()
        if self.is_published and not self.consent_confirmed:
            raise ValidationError(
                {"is_published": "Confirm the student's consent before publishing."}
            )

    def __str__(self):
        return self.display_name


class BlogPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    excerpt = models.CharField(max_length=400)
    body = models.TextField()
    author = models.CharField(max_length=120, default="StudyBridge Germany")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-published_at", "-created_at")

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Enquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        RESPONDED = "responded", "Responded"
        CLOSED = "closed", "Closed"

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=100, blank=True)
    service = models.ForeignKey(
        Service,
        related_name="enquiries",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    message = models.TextField(max_length=4000)
    privacy_consent = models.BooleanField(default=False)
    privacy_consent_at = models.DateTimeField(null=True, blank=True, editable=False)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=Q(privacy_consent=True),
                name="enquiry_requires_privacy_acknowledgement",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.privacy_consent and self.privacy_consent_at is None:
            self.privacy_consent_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.full_name}"


class ConsultationRequest(models.Model):
    class PreferredTime(models.TextChoices):
        MORNING = "morning", "Morning"
        AFTERNOON = "afternoon", "Afternoon"
        EVENING = "evening", "Evening"

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        CONFIRMED = "confirmed", "Confirmed"
        DECLINED = "declined", "Declined"
        COMPLETED = "completed", "Completed"

    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    country = models.CharField(max_length=100, blank=True)
    service = models.ForeignKey(
        Service,
        related_name="consultation_requests",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    preferred_date = models.DateField()
    preferred_time = models.CharField(max_length=16, choices=PreferredTime.choices)
    message = models.TextField(max_length=2000, blank=True)
    privacy_consent = models.BooleanField(default=False)
    privacy_consent_at = models.DateTimeField(null=True, blank=True, editable=False)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("preferred_date", "created_at")
        constraints = [
            models.CheckConstraint(
                condition=Q(privacy_consent=True),
                name="consultation_requires_privacy_acknowledgement",
            ),
            models.CheckConstraint(
                condition=~Q(status="confirmed") | Q(scheduled_at__isnull=False),
                name="consultation_confirmation_requires_schedule",
            ),
        ]

    def clean(self):
        super().clean()
        if self.preferred_date and self.preferred_date < timezone.localdate():
            raise ValidationError(
                {"preferred_date": "Choose today or a future date."}
            )
        if self.status == self.Status.CONFIRMED and not self.scheduled_at:
            raise ValidationError(
                {"scheduled_at": "Set the confirmed appointment time before confirming."}
            )

    def save(self, *args, **kwargs):
        if self.privacy_consent and self.privacy_consent_at is None:
            self.privacy_consent_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.full_name}"
