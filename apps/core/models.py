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
