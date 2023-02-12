from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# from django.contrib.auth.models import Employee
# from path.to.models import Employee
from .models import Member
from .models import LeaveForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .countLeaves import leave_days

# from django.contrib.auth import User
from django.http import HttpResponse

# Create your views here.
def home(request):
    all_members = Member.objects.all
    return render(request, "mhome.html", {"all": all_members})


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # utype=request.POST['user-type']
        # des = Employee.objects.get(designation="Manager")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.member.designation == "Manager":
                return redirect("mhome")
            else:
                return redirect("ehome")
        else:
            messages.success(request, ("There was an Error Loggin In, Try Again..."))
            return redirect("login")
    else:
        return render(request, "login.html", {})


# @login_required(login_url="login")
def navigation(request):
    if request.user.is_authenticated:
        print("yes bro")
    else:
        print("NO")
    return render(request, "ehome.html", {})


def leave(request):
    if request.method == "POST":
        # name = request.POST.get("name")
        # email = request.POST.get("email")
        # emp_id = request.POST.get("emp_id")
        # emp_id = request.user.id
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")
        # employee = Employee.objects.get(emp_id=int(emp_id))
        days = leave_days(start_date, end_date)
        leaveform = LeaveForm(
            employee=request.user,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            days=days,
        )
        leaveform.save()
        messages.success(request, "Leave Details submitted successfully!")
    # username = request.user.username
    profile = request.user.member.fname
    # profile = Employee.objects.get(fname=username.capitalize())
    print(profile)
    return render(request, "leave.html", {"profile": profile})


def logoutPage(request):
    logout(request)
    return render(request, "logout.html", {})


def leave_history(request):
    leaves = LeaveForm.objects.filter(employee=request.user)
    return render(request, "leave_history.html", {"leaves": leaves})


def profile(request):
    # username = request.user.username
    # print(username.capitalize())
    # profile = Employee.objects.get(fname=username.capitalize())
    # profile = request.user.member
    return render(request, "profile.html",)


def manager_dash(request):
    # username = request.user.username
    # currUser = Employee.objects.get(fname=username.capitalize())
    if request.user.member.designation != "Manager":
        return HttpResponse("You are not a manager. Please go back")

    return render(request, "manager_dash.html", {})


def manager_leaveapproval(request):
    leave_data = LeaveForm.objects.all()

    return render(request, "manager_leaveapproval.html", {"leave_data": leave_data})


def manageraddemp(request):
    return render(request, "manageraddemp.html", {})


def teams(request):
    return render(request, "teams_page.html", {})


def ehome(request):
    approvedLeaves = len(LeaveForm.objects.filter(employee = request.user, status = "Approved"))
    rejectedLeaves = len(LeaveForm.objects.filter(employee = request.user, status = "Rejected"))
    context ={'approvedLeaves':approvedLeaves,'rejectedLeaves':rejectedLeaves}
    print("teraaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", context)
    return render(request, "ehome.html", context)


def mhome(request):
    return render(request, "mhome.html", {})


def approve(request, leaveID):
    lf = LeaveForm.objects.get(id=leaveID)
    emp = Member.objects.get(user=lf.employee)
    emp.leave_balance -= lf.days
    emp.save()
    print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",emp)
    print(lf)
    lf.status = "Approved"
    lf.save()
    return redirect("manager_leaveapproval")


def reject(request, leaveID):
    lf = LeaveForm.objects.get(id=leaveID)
    print(lf)
    lf.status = "Rejected"
    lf.save()
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", lf.status)
    return redirect("manager_leaveapproval")
