from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import BarangayLoginForm

urlpatterns = [
    # residents
    path("", views.home, name="home"),
    path("requests/", views.my_requests, name="my_requests"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("request/new/", views.request_create, name="request_create"),
    path("download/<int:pk>/", views.download_document, name="download_document"),
    # barangay portal (staff and admin together)
    path("barangay/login/", auth_views.LoginView.as_view(
        template_name="barangay/login.html",
        authentication_form=BarangayLoginForm,
        next_page="/barangay/",
    ), name="barangay_login"),
    path("barangay/logout/", auth_views.LogoutView.as_view(next_page="/barangay/login/"), name="barangay_logout"),
    path("barangay/", views.barangay_dashboard, name="barangay_dashboard"),
    path("barangay/requests/", views.barangay_requests, name="barangay_requests"),
    path("barangay/requests/<int:pk>/", views.barangay_update, name="barangay_update"),
    path("barangay/requests/<int:pk>/release/", views.barangay_release, name="barangay_release"),
    path("barangay/documents/", views.doctype_list, name="doctype_list"),
    path("barangay/documents/new/", views.doctype_edit, name="doctype_new"),
    path("barangay/documents/<int:pk>/", views.doctype_edit, name="doctype_edit"),
    path("barangay/documents/<int:pk>/delete/", views.doctype_delete, name="doctype_delete"),
    path("barangay/pickup-times/", views.slot_list, name="slot_list"),
    path("barangay/pickup-times/new/", views.slot_edit, name="slot_new"),
    path("barangay/pickup-times/<int:pk>/", views.slot_edit, name="slot_edit"),
    path("barangay/pickup-times/<int:pk>/delete/", views.slot_delete, name="slot_delete"),
    path("barangay/staff/", views.staff_accounts, name="staff_accounts"),
]
