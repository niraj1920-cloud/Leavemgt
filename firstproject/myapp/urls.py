from django.urls import path
from . import views

urlpatterns = [
    path("mhome", views.mhome, name="mhome"),
    path("login", views.login_user, name="login"),
    path("ehome", views.navigation, name="ehome"),
    path("leave", views.leave, name="leave"),
    path("logout", views.logoutPage, name="logout"),
    path("leave_history", views.leave_history, name="leave_history"),
    path("profile", views.profile, name="profile"),
    path("manager_dash", views.manager_dash, name="manager_dash"),
    path(
        "manager_leaveapproval",
        views.manager_leaveapproval,
        name="manager_leaveapproval",
    ),
    path("manageraddemp", views.manageraddemp, name="manageraddemp"),
    path("teams", views.teams, name="teams"),
    path("mhome", views.mhome, name="mhome"),
    path("approve/<leaveID>", views.approve, name="approve"),
    path("reject/<leaveID>", views.reject, name="reject"),
]
