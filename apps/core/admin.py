from django.contrib import admin

from apps.core.models import BlogPost, FAQ, Package, Service, Testimonial


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "display_order", "is_published", "updated_at")
    list_editable = ("display_order", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "description")
    ordering = ("display_order", "title")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "currency", "display_order", "is_published")
    list_editable = ("display_order", "is_published")
    list_filter = ("is_published", "currency")
    filter_horizontal = ("services",)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "services__title")
    ordering = ("display_order", "title")
    readonly_fields = ("created_at", "updated_at")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "service", "display_order", "is_published")
    list_editable = ("display_order", "is_published")
    list_filter = ("is_published", "service")
    search_fields = ("question", "answer", "service__title")
    ordering = ("display_order", "question")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("display_name", "consent_confirmed", "is_published", "display_order")
    list_filter = ("consent_confirmed", "is_published")
    search_fields = ("display_name", "quote", "context")
    ordering = ("display_order", "-created_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("display_name", "quote", "context")}),
        ("Publication", {"fields": ("consent_confirmed", "is_published", "display_order")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "updated_at")
    list_filter = ("status", "published_at")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "excerpt", "body", "author")
    ordering = ("-published_at", "-created_at")
    readonly_fields = ("created_at", "updated_at")
