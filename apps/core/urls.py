from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.service_list, name="service_list"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("packages/", views.package_list, name="package_list"),
    path("faqs/", views.faq_list, name="faq_list"),
    path("stories/", views.testimonial_list, name="testimonial_list"),
    path("resources/", views.blog_list, name="blog_list"),
    path("resources/<slug:slug>/", views.blog_detail, name="blog_detail"),
]
