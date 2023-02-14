from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .otp import generateOTP
from django.contrib.auth.models import User
from .email import sendMail
from threading import Thread
from .models import Member
from .models import LeaveForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .countLeaves import leave_days
from django.http import HttpResponse


# Decorator for checking manager
def is_manager(user):
    # print("is manager: ", user.member.designation)
    return user.member.designation == "Manager"


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
    # print(profile)
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
    return render(
        request,
        "profile.html",
    )


@user_passes_test(is_manager, login_url="ehome")
def manager_dash(request):
    # username = request.user.username
    # currUser = Employee.objects.get(fname=username.capitalize())
    if request.user.member.designation != "Manager":
        return HttpResponse("You are not a manager. Please go back")

    return render(request, "manager_dash.html", {})


@user_passes_test(is_manager, login_url="ehome")
def manager_leaveapproval(request):
    leave_data = LeaveForm.objects.all()

    return render(request, "manager_leaveapproval.html", {"leave_data": leave_data})


@user_passes_test(is_manager, login_url="ehome")
def manageraddemp(request):
    if request.method == "POST":
        employee = request.POST.get("employee")
        team = request.POST.get("team")
        # print("EEEEEEEEEEEEEEEEEEEEEEE", employee, team)

        currEmp = Member.objects.get(user=employee)
        currEmp.team = team
        currEmp.save()
        # print("FFFFFFFFFFFFFFFFFF", currEmp)

    employees = Member.objects.filter(designation="Employee")
    return render(request, "manageraddemp.html", {"employees": employees})


@user_passes_test(is_manager, login_url="ehome")
def teams(request):
    team1_employees = Member.objects.filter(team="Marketing", designation="Employee")
    team2_employees = Member.objects.filter(team="Development", designation="Employee")
    team3_employees = Member.objects.filter(team="Design", designation="Employee")
    team4_employees = Member.objects.filter(team="bench", designation="Employee")
    context = {
        "team1_employees": team1_employees,
        "team2_employees": team2_employees,
        "team3_employees": team3_employees,
        "others_employees": team4_employees,
    }
    return render(request, "teams_page.html", context)


def ehome(request):
    approvedLeaves = len(
        LeaveForm.objects.filter(employee=request.user, status="Approved")
    )
    rejectedLeaves = len(
        LeaveForm.objects.filter(employee=request.user, status="Rejected")
    )
    context = {"approvedLeaves": approvedLeaves, "rejectedLeaves": rejectedLeaves}
    # print("teraaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", context)
    return render(request, "ehome.html", context)


@user_passes_test(is_manager, login_url="ehome")
def mhome(request):
    return render(request, "mhome.html", {})


@user_passes_test(is_manager, login_url="ehome")
def approve(request, leaveID):
    lf = LeaveForm.objects.get(id=leaveID)
    emp = Member.objects.get(user=lf.employee)
    emp.leave_balance -= lf.days
    emp.save()
    # print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", emp)
    # print(lf)
    lf.status = "Approved"
    lf.save()
    try:
        thread = Thread(
            target=sendMail,
            args=(
                emp.email,
                "Leave Approved",
                f"Your leave from {lf.start_date} to {lf.end_date} has been approved",
            ),
        )
        thread.start()
    except Exception as e:
        print(e)
    return redirect("manager_leaveapproval")


@user_passes_test(is_manager, login_url="ehome")
def reject(request, leaveID):
    lf = LeaveForm.objects.get(id=leaveID)
    emp = Member.objects.get(user=lf.employee)
    lf.status = "Rejected"
    lf.save()
    try:
        thread = Thread(
            target=sendMail,
            args=(
                emp.email,
                "Leave Rejected",
                f"Your leave from {lf.start_date} to {lf.end_date} has been rejected",
            ),
        )
        thread.start()
    except Exception as e:
        print(e)
    return redirect("manager_leaveapproval")


def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        otp = generateOTP()

        # Save these values in the session for reset_password() to use
        request.session["currentUser"] = username
        request.session["otp"] = otp

        # Threaded as sending emails sometimes takes time
        try:
            toEmail = Member.objects.get(user__username=username).email
            thread = Thread(
                target=sendMail,
                args=(toEmail, "Request for password Reset", f"Your OTP is {otp}"),
            )
            thread.start()
        except Exception as e:
            print(e)

        return redirect(reset_password)

    return render(request, "forgot_password.html")


def reset_password(request):
    if request.method == "POST":
        enteredOTP = request.POST.get("otp")
        newPassword = request.POST.get("password")

        try:
            userToChange = User.objects.get(username=request.session.get("currentUser"))
        except Exception as e:
            print(e)

        otp = request.session.get("otp")

        if otp == enteredOTP:
            userToChange.set_password(newPassword)
            return HttpResponse("Password Changed Successfully")

        else:
            return HttpResponse("Wrong OTP Entered or user does not exist")

    return render(request, "reset_password.html")


@user_passes_test(is_manager, login_url="ehome")
def add_employee(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        date_of_birth = request.POST.get("date_of_birth")
        phone_number = request.POST.get("phone_number")
        date_of_joining = request.POST.get("date_of_joining")
        department = request.POST.get("department")
        designation = request.POST.get("designation")
        address = request.POST.get("address")
        leave_balance = request.POST.get("leave_balance")

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        if not user:
            raise Exception("something went wrong with the DB!")
        try:
            Member.objects.create(
                user=user,
                fname=str(fname).capitalize(),
                lname=str(lname).capitalize(),
                email=email,
                DOB=date_of_birth,
                phone_number=phone_number,
                doj=date_of_joining,
                department=department,
                designation=designation,
                address=address,
                leave_balance=leave_balance,
            )
        except Exception as e:
            print(e)
    return render(request, "add_employee.html")
