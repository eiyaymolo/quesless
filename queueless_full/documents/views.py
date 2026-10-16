from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import ProtectedError, Q
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .forms import (
    RegisterForm, RequestForm, StaffUpdateForm, DocumentTypeForm, PickupSlotForm,
)
from .models import DocumentRequest, DocumentType, PickupSlot


def barangay_required(view):
    return user_passes_test(
        lambda u: u.is_active and u.is_staff, login_url="barangay_login"
    )(view)


def owner_required(view):
    return user_passes_test(
        lambda u: u.is_active and u.is_superuser, login_url="barangay_login"
    )(view)


# ---------- residents ----------
def home(request):
    if request.user.is_authenticated:
        return redirect("my_requests")
    return render(request, "documents/home.html")


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("my_requests")
    return render(request, "documents/register.html", {"form": form})


@login_required
def request_create(request):
    form = RequestForm(request.POST or None)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.resident = request.user
        doc.save()
        messages.success(
            request,
            f"Request sent! Your reference code is {doc.reference_code}.",
            extra_tags="celebrate",
        )
        return redirect("my_requests")
    return render(request, "documents/request_form.html", {"form": form})


@login_required
def my_requests(request):
    items = DocumentRequest.objects.filter(resident=request.user)
    return render(request, "documents/my_requests.html", {"items": items})


@login_required
def download_document(request, pk):
    doc = get_object_or_404(DocumentRequest, pk=pk)
    if doc.resident != request.user and not request.user.is_staff:
        raise Http404()
    if not doc.document_file:
        raise Http404()
    return FileResponse(
        doc.document_file.open("rb"),
        as_attachment=True,
        filename=f"{doc.reference_code}.pdf",
    )


# ---------- barangay portal ----------
@barangay_required
def barangay_dashboard(request):
    items = DocumentRequest.objects.all()
    context = {
        "total": items.count(),
        "pending": items.filter(status="pending").count(),
        "ready": items.filter(status="ready").count(),
        "latest": items.filter(status="pending").select_related("resident", "document_type")[:5],
    }
    return render(request, "barangay/dashboard.html", context)


@barangay_required
def barangay_requests(request):
    items = DocumentRequest.objects.select_related("resident", "document_type", "pickup_slot")
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    if status:
        items = items.filter(status=status)
    if q:
        items = items.filter(
            Q(reference_code__icontains=q)
            | Q(resident__username__icontains=q)
            | Q(resident__first_name__icontains=q)
            | Q(resident__last_name__icontains=q)
        )
    context = {
        "items": items,
        "status": status,
        "q": q,
        "statuses": DocumentRequest.STATUS_CHOICES,
    }
    return render(request, "barangay/requests.html", context)


@barangay_required
def barangay_update(request, pk):
    doc = get_object_or_404(DocumentRequest, pk=pk)
    form = StaffUpdateForm(request.POST or None, request.FILES or None, instance=doc)
    if form.is_valid():
        form.save()
        messages.success(request, f"Request {doc.reference_code} was updated.")
        return redirect("barangay_requests")
    return render(request, "barangay/update.html", {"form": form, "doc": doc})


@barangay_required
@require_POST
def barangay_release(request, pk):
    doc = get_object_or_404(DocumentRequest, pk=pk)
    doc.status = "released"
    doc.save(update_fields=["status"])
    messages.success(request, f"{doc.reference_code} marked as picked up.")
    return redirect("barangay_requests")


@barangay_required
def doctype_list(request):
    return render(request, "barangay/doctypes.html", {"items": DocumentType.objects.all()})


@barangay_required
def doctype_edit(request, pk=None):
    obj = get_object_or_404(DocumentType, pk=pk) if pk else None
    form = DocumentTypeForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Document saved.")
        return redirect("doctype_list")
    title = "Edit document" if obj else "Add a document"
    return render(request, "barangay/form.html", {"form": form, "title": title, "back": "doctype_list"})


@barangay_required
def doctype_delete(request, pk):
    obj = get_object_or_404(DocumentType, pk=pk)
    if request.method == "POST":
        try:
            obj.delete()
            messages.success(request, "Document deleted.")
        except ProtectedError:
            messages.error(request, "This document already has requests, so it can't be deleted.")
        return redirect("doctype_list")
    return render(request, "barangay/confirm_delete.html", {"obj": obj, "back": "doctype_list"})


@barangay_required
def slot_list(request):
    return render(request, "barangay/slots.html", {"items": PickupSlot.objects.all()})


@barangay_required
def slot_edit(request, pk=None):
    obj = get_object_or_404(PickupSlot, pk=pk) if pk else None
    form = PickupSlotForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Pickup time saved.")
        return redirect("slot_list")
    title = "Edit pickup time" if obj else "Add a pickup time"
    return render(request, "barangay/form.html", {"form": form, "title": title, "back": "slot_list"})


@barangay_required
def slot_delete(request, pk):
    obj = get_object_or_404(PickupSlot, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Pickup time deleted.")
        return redirect("slot_list")
    return render(request, "barangay/confirm_delete.html", {"obj": obj, "back": "slot_list"})


@owner_required
def staff_accounts(request):
    if request.method == "POST":
        u = get_object_or_404(User, pk=request.POST.get("user"))
        if not u.is_superuser:
            u.is_staff = not u.is_staff
            u.save(update_fields=["is_staff"])
            state = "is now barangay staff" if u.is_staff else "is no longer staff"
            messages.success(request, f"{u.get_full_name() or u.username} {state}.")
        return redirect("staff_accounts")
    q = request.GET.get("q", "").strip()
    users = User.objects.filter(is_superuser=False)
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    return render(request, "barangay/staff_accounts.html", {"users": users.order_by("-is_staff", "username"), "q": q})
