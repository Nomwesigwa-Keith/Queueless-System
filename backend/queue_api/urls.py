from django.urls import path
from .views import AdminBusinessStatusView, BusinessDirectoryView, BusinessListView, BusinessPauseView, BusinessRegisterView, BusinessStaffView, BusinessView, BusinessStatsView, EmailVerifyView, LoginView, MeView, PasswordChangeView, PasswordResetConfirmView, PasswordResetRequestView, RegisterView, TicketCancelView, TicketDetailView, TicketListCreateView, TicketStatusView

urlpatterns = [
    path("auth/me/", MeView.as_view()),
    path("auth/register/", RegisterView.as_view()),
    path("auth/verify-email/", EmailVerifyView.as_view()),
    path("auth/business-register/", BusinessRegisterView.as_view()),
    path("auth/password/change/", PasswordChangeView.as_view()),
    path("auth/password/reset/", PasswordResetRequestView.as_view()),
    path("auth/password/reset/confirm/", PasswordResetConfirmView.as_view()),
    path("directory/businesses/", BusinessDirectoryView.as_view()),
    path("tickets/", TicketListCreateView.as_view()),
    path("tickets/<int:pk>/", TicketDetailView.as_view()),
    path("tickets/<int:pk>/status/", TicketStatusView.as_view()),
    path("tickets/<int:pk>/cancel/", TicketCancelView.as_view()),
    path("business/", BusinessView.as_view()),
    path("business/pause/", BusinessPauseView.as_view()),
    path("business/staff/", BusinessStaffView.as_view()),
    path("business/stats/", BusinessStatsView.as_view()),
    path("admin/businesses/", BusinessListView.as_view()),
    path("admin/businesses/<int:pk>/status/", AdminBusinessStatusView.as_view()),
]
