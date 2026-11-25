from django import forms
from django.utils import timezone

from apps.core.models import ConsultationRequest, Enquiry, Service


class PublicRequestFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"


class EnquiryForm(PublicRequestFormMixin, forms.ModelForm):
    privacy_consent = forms.BooleanField(
        label="I agree that StudyBridge Germany may use these details to respond to my enquiry.",
        required=True,
    )

    class Meta:
        model = Enquiry
        fields = (
            "full_name",
            "email",
            "phone",
            "country",
            "service",
            "message",
            "privacy_consent",
        )
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_published=True)
        self.fields["service"].required = False


class ConsultationRequestForm(PublicRequestFormMixin, forms.ModelForm):
    privacy_consent = forms.BooleanField(
        label="I agree that StudyBridge Germany may use these details to respond to my consultation request.",
        required=True,
    )

    class Meta:
        model = ConsultationRequest
        fields = (
            "full_name",
            "email",
            "phone",
            "country",
            "service",
            "preferred_date",
            "preferred_time",
            "message",
            "privacy_consent",
        )
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_published=True)
        self.fields["service"].required = False
        self.fields["preferred_date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data["preferred_date"]
        if preferred_date < timezone.localdate():
            raise forms.ValidationError("Choose today or a future date.")
        return preferred_date
