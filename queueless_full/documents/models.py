import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    fee = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def emoji(self):
        n = self.name.lower()
        if "clearance" in n:
            return "🛡️"
        if "indigency" in n:
            return "🤝"
        if "residency" in n:
            return "🏠"
        if "business" in n:
            return "🏪"
        if "id" in n.split():
            return "🪪"
        return "📄"

    def __str__(self):
        return self.name


class PickupSlot(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["date", "start_time"]

    def clean(self):
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be later than start time.")

    def slots_left(self):
        return self.capacity - self.requests.exclude(status="rejected").count()

    def __str__(self):
        return f"{self.date} {self.start_time:%I:%M %p}-{self.end_time:%I:%M %p}"


class DocumentRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("ready", "Ready for pickup"),
        ("released", "Released"),
        ("rejected", "Rejected"),
    ]

    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    purpose = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    pickup_slot = models.ForeignKey(
        PickupSlot, null=True, blank=True, on_delete=models.SET_NULL, related_name="requests"
    )
    document_file = models.FileField(
        upload_to="issued/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(["pdf"])],
    )
    reference_code = models.CharField(max_length=12, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def step(self):
        return {"pending": 1, "approved": 2, "ready": 3, "released": 4}.get(self.status, 0)

    def status_help(self):
        if self.status == "pending":
            return "We received your request. Staff will check it soon."
        if self.status == "approved":
            return "Your request was approved. A pickup time will be set soon."
        if self.status == "ready":
            if self.document_file:
                return "Your document is ready. You can download it now."
            return "Your document is ready. Bring a valid ID and your reference code."
        if self.status == "released":
            return "This document was given to you. Thank you!"
        return "Your request was not approved. Please visit the barangay hall."

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_code} - {self.document_type}"
