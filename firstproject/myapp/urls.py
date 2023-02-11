from django.urls import path
from . import views

urlpatterns= [
    path('home/', views.home,name="home"),
    path('login', views.login_user, name="login"),
    path('nav', views.navigation, name="nav"),
    path('leave', views.leave, name="leave"),
    path('logout', views.logoutPage, name="logout"),
    path('leave_history', views.leave_history, name="leave_history"),
    path('profile', views.profile, name="profile"),
    path('manager_dash', views.manager_dash, name="manager_dash"),
    path('manager_leaveapproval', views.manager_leaveapproval, name="manager_leaveapproval"),
    path('manageraddemp', views.manageraddemp, name="manageraddemp"),

]