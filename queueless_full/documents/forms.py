from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import DocumentRequest, DocumentType, PickupSlot


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "username": "Choose a username",
            "email": "Email address",
        }
        help_texts = {"username": "Letters and numbers only, no spaces."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["password1"].help_text = "At least 8 characters."
        self.fields["password2"].label = "Type your password again"
        self.fields["password2"].help_text = ""


class DocumentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.emoji()} {obj.name}"


class RequestForm(forms.ModelForm):
    document_type = DocumentChoiceField(
        queryset=DocumentType.objects.all(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Which document do you need?",
    )


    class Meta:
        model = DocumentRequest
        fields = ["document_type", "purpose"]
        labels = {
            "document_type": "Which document do you need?",
            "purpose": "Why do you need it?",
        }
        help_texts = {"purpose": "Example: Job application, school, ID."}


class StaffUpdateForm(forms.ModelForm):
    class Meta:
        model = DocumentRequest
        fields = ["status", "pickup_slot", "document_file"]
        labels = {
            "status": "Request status",
            "pickup_slot": "Pickup date and time (optional)",
            "document_file": "Finished document (PDF, optional)",
        }
        help_texts = {
            "document_file": "Upload a PDF if the resident can download it online."
        }

    def clean_pickup_slot(self):
        slot = self.cleaned_data.get("pickup_slot")
        if slot and slot != self.instance.pickup_slot and slot.slots_left() <= 0:
            raise forms.ValidationError("That pickup slot is already full.")
        return slot


class BarangayLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError(
                "This login is for barangay staff only. Residents, please use the resident login.",
                code="not_staff",
            )


class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ["name", "description", "fee"]
        labels = {
            "name": "Document name",
            "description": "Short description (optional)",
            "fee": "Fee in pesos (0 if free)",
        }
        widgets = {"description": forms.TextInput()}


class PickupSlotForm(forms.ModelForm):
    class Meta:
        model = PickupSlot
        fields = ["date", "start_time", "end_time", "capacity"]
        labels = {
            "date": "Date",
            "start_time": "Starts at",
            "end_time": "Ends at",
            "capacity": "How many people can pick up in this time?",
        }
        widgets = {
            "date": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "start_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "end_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
        }
