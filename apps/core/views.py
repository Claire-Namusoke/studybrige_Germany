from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from apps.core.models import BlogPost, FAQ, Package, Service, Testimonial


def _published_blog_posts():
    return BlogPost.objects.filter(
        status=BlogPost.Status.PUBLISHED,
        published_at__lte=timezone.now(),
    )


def home(request):
    return render(
        request,
        "core/home.html",
        {
            "services": Service.objects.filter(is_published=True)[:3],
            "recent_posts": _published_blog_posts()[:3],
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
