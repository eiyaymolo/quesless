from django.contrib import admin
from .models import DocumentType, PickupSlot, DocumentRequest

admin.site.site_header = "QueueLess Admin"
admin.site.site_title = "QueueLess"
admin.site.index_title = "Barangay setup: documents, pickup times and requests"


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "fee", "description")
    search_fields = ("name",)


@admin.register(PickupSlot)
class PickupSlotAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "end_time", "capacity", "slots_left_display")
    list_filter = ("date",)

    @admin.display(description="Slots left")
    def slots_left_display(self, obj):
        return obj.slots_left()


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "resident", "document_type", "status", "pickup_slot", "created_at")
    list_filter = ("status", "document_type")
    search_fields = ("reference_code", "resident__username", "resident__first_name", "resident__last_name")
    list_editable = ("status",)
    actions = ["mark_ready", "mark_released"]

    @admin.action(description="Mark selected as Ready for pickup")
    def mark_ready(self, request, queryset):
        n = queryset.update(status="ready")
        self.message_user(request, f"{n} request(s) marked as ready.")

    @admin.action(description="Mark selected as Released (picked up)")
    def mark_released(self, request, queryset):
        n = queryset.update(status="released")
        self.message_user(request, f"{n} request(s) marked as released.")
