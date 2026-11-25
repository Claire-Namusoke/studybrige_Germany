from django.conf import settings
from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.core.forms import ConsultationRequestForm, EnquiryForm
from apps.core.models import BlogPost, FAQ, Package, Service, Testimonial
from apps.core.notifications import send_submission_notifications


def _published_blog_posts():
    return BlogPost.objects.filter(
        status=BlogPost.Status.PUBLISHED,
        published_at__lte=timezone.now(),
    )


def home(request):
    show_demo_content = settings.DEBUG
    services = list(Service.objects.filter(is_published=True)[:6])
    if not services and show_demo_content:
        services = [
            {
                "title": "University Admission",
                "summary": "Get guidance on German universities.",
                "is_demo": True,
            },
            {
                "title": "Blocked Account",
                "summary": "Secure your blocked account with ease.",
                "is_demo": True,
            },
            {
                "title": "Health Insurance",
                "summary": "Find the right health insurance plan.",
                "is_demo": True,
            },
            {
                "title": "Accommodation",
                "summary": "Discover safe and affordable housing.",
                "is_demo": True,
            },
            {
                "title": "Arrival Support",
                "summary": "Get help before and after your arrival.",
                "is_demo": True,
            },
            {
                "title": "Settling in Germany",
                "summary": "Enjoy a smooth transition into your new life.",
                "is_demo": True,
            },
        ]

    return render(
        request,
        "core/home.html",
        {
            "services": services,
            "testimonials": Testimonial.objects.filter(
                is_published=True,
                consent_confirmed=True,
            )[:3],
            "show_demo_content": show_demo_content,
        },
    )


def service_list(request):
    return render(
        request,
        "core/service_list.html",
        {"services": Service.objects.filter(is_published=True)},
    )


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_published=True)
    return render(
        request,
        "core/service_detail.html",
        {
            "service": service,
            "related_faqs": service.faqs.filter(is_published=True),
        },
    )


def package_list(request):
    published_services = Service.objects.filter(is_published=True)
    return render(
        request,
        "core/package_list.html",
        {
            "packages": Package.objects.filter(is_published=True).prefetch_related(
                Prefetch(
                    "services",
                    queryset=published_services,
                    to_attr="published_services",
                )
            )
        },
    )


def faq_list(request):
    return render(
        request,
        "core/faq_list.html",
        {"faqs": FAQ.objects.filter(is_published=True).select_related("service")},
    )


def testimonial_list(request):
    return render(
        request,
        "core/testimonial_list.html",
        {"testimonials": Testimonial.objects.filter(is_published=True)},
    )


def blog_list(request):
    return render(request, "core/blog_list.html", {"posts": _published_blog_posts()})


def blog_detail(request, slug):
    post = get_object_or_404(
        _published_blog_posts(),
        slug=slug,
    )
    return render(request, "core/blog_detail.html", {"post": post})


def _show_submission_result(request, submission, *, request_type):
    confirmation_sent, admin_sent = send_submission_notifications(
        submission,
        request_type=request_type,
    )

    if settings.EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
        messages.success(
            request,
            f"Your {request_type} request has been saved. Reference: {submission.reference}.",
        )
        messages.info(
            request,
            "Development mode: confirmation email output is written to the server console, not sent externally.",
        )
    elif confirmation_sent:
        messages.success(
            request,
            f"Your {request_type} request has been saved and a confirmation email was sent. "
            f"Reference: {submission.reference}.",
        )
    else:
        messages.warning(
            request,
            f"Your {request_type} request was saved, but we could not send a confirmation email. "
            f"Keep this reference: {submission.reference}.",
        )

    if not settings.BUSINESS_NOTIFICATION_EMAIL:
        messages.warning(
            request,
            "The team notification address is not configured; the request is available in Django Admin.",
        )
    elif not admin_sent:
        messages.warning(
            request,
            "The team notification email could not be sent; the request is available in Django Admin.",
        )


def enquiry_create(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            _show_submission_result(request, enquiry, request_type="enquiry")
            return redirect("core:enquiry")
    else:
        form = EnquiryForm()

    return render(request, "core/enquiry_form.html", {"form": form})


def consultation_create(request):
    if request.method == "POST":
        form = ConsultationRequestForm(request.POST)
        if form.is_valid():
            consultation = form.save()
            _show_submission_result(
                request,
                consultation,
                request_type="consultation",
            )
            return redirect("core:consultation")
    else:
        form = ConsultationRequestForm()

    return render(request, "core/consultation_form.html", {"form": form})
