from datetime import datetime
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
from .utils import check_date_overlap

# Decorator for checking manager
def is_manager(user):
    # print("is manager: ", user.member.designation)
    return user.member.designation == "Manager"


# Create your views here.
@login_required(login_url="login")
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
            if not hasattr(request.user, "member"):
                messages.error(request, ("Oops!! Member doesn't exist..."))
                return redirect("login")
            elif request.user.member.designation == "Manager":
                return redirect("mhome")
            else:
                print(request.user.member)
                return redirect("ehome")
        else:
            messages.error(request, ("Oops!! User doesn't exist..."))
            return redirect("login")
    else:
        return render(request, "login.html", {})


@login_required(login_url="login")
def navigation(request):
    if request.user.is_authenticated:
        print("yes bro")
    else:
        print("NO")
    return render(request, "ehome.html", {})


@login_required(login_url="login")
def leave(request):
    profile = request.user.member.fname
    if request.method == "POST":
        stDate = request.POST.get("start_date")
        endDate = request.POST.get("end_date")
        reason = request.POST.get("reason")
        previousLeaves = LeaveForm.objects.filter(
            employee=request.user.member.user
        ).values()
        start_date = datetime.strptime(stDate, "%Y-%m-%d").date()
        end_date = datetime.strptime(endDate, "%Y-%m-%d").date()
        days = leave_days(stDate, endDate)
        leaveform = LeaveForm(
            employee=request.user,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            days=days,
        )

        if start_date > end_date:
            msg = "End date can't be less than start date"
            messages.error(request, msg)
        elif previousLeaves.__len__() == 0:
            leaveform.save()
            # Send mail to all managers
            managers = Member.objects.filter(designation="Manager")
            for manager in managers:
                try:
                    thread = Thread(
                        target=sendMail,
                        args=(
                            manager.email,
                            "Leave Approval",
                            f"{request.user.member.fname} {request.user.member.lname} has requested a leave<br />Duration : {start_date} to {end_date} ({days} days)<br >Reason :{reason}",
                        ),
                    )
                    thread.start()
                except Exception as e:
                    print(e)

            # Send mail to employee
            try:
                thread = Thread(
                    target=sendMail,
                    args=(
                        request.user.email,
                        "Leave Applied",
                        f"You have applied for a leave from {start_date} to {end_date}",
                    ),
                )
                thread.start()
            except Exception as e:
                print(e)
            messages.success(request, "Leave Details submitted successfully!")
        else:
            for previousLeave in previousLeaves:
                if (
                    previousLeave["end_date"] > start_date
                    and previousLeave["start_date"] < end_date
                    and start_date < end_date
                ):
                    msg = "Leave dates correspond to previously applied leave:"
                    messages.error(request, msg)
                    for key, value in previousLeave.items():
                        if (
                            key == "start_date"
                            or key == "end_date"
                            or key == "reason"
                            or key == "status"
                        ):
                            messages.error(request, "\n" + str(key) + ":" + str(value))
                    break
            else:
                leaveform.save()
                managers = Member.objects.filter(designation="Manager")
                # Send mail to all managers
                for manager in managers:
                    try:
                        thread = Thread(
                            target=sendMail,
                            args=(
                                manager.email,
                                "Leave Approval",
                                f"{request.user.member.fname} {request.user.member.lname} has requested a leave<br />Duration : {start_date} to {end_date} ({days} days)<br >Reason :{reason}",
                            ),
                        )
                        thread.start()
                    except Exception as e:
                        print(e)

                # Send mail to employee
                try:
                    thread = Thread(
                        target=sendMail,
                        args=(
                            request.user.email,
                            "Leave Applied",
                            f"You have applied for a leave from {start_date} to {end_date}",
                        ),
                    )
                    thread.start()
                except Exception as e:
                    print(e)
                messages.success(request, "Leave Details submitted successfully!")
    return render(request, "leave.html", {"profile": profile})


@login_required(login_url="login")
def logoutPage(request):
    logout(request)
    return render(request, "logout.html", {})


@login_required(login_url="login")
def leave_history(request):
    leaves = LeaveForm.objects.filter(employee=request.user)
    return render(request, "leave_history.html", {"leaves": leaves})


@login_required(login_url="login")
def profile(request):
    # username = request.user.username
    # print(username.capitalize())
    # profile = Employee.objects.get(fname=username.capitalize())
    # profile = request.user.member
    if request.method == "POST":
        number = request.POST["number"]
        emailId = request.POST["emailId"]
        empId = request.POST["empId"]
        Member.objects.filter(id=empId).update(email=emailId, phone_number=number)
    return render(request, "profile.html")


@login_required(login_url="login")
@user_passes_test(is_manager, login_url="ehome")
def manager_dash(request):
    # username = request.user.username
    # currUser = Employee.objects.get(fname=username.capitalize())
    if request.user.member.designation != "Manager":
        return HttpResponse("You are not a manager. Please go back")

    return render(request, "manager_dash.html", {})


@login_required(login_url="login")
@user_passes_test(is_manager, login_url="ehome")
def manager_leaveapproval(request):
    leave_data = LeaveForm.objects.all()

    return render(request, "manager_leaveapproval.html", {"leave_data": leave_data})


@login_required(login_url="login")
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


@login_required(login_url="login")
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


@login_required(login_url="login")
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


@login_required(login_url="login")
@user_passes_test(is_manager, login_url="ehome")
def mhome(request):
    return render(request, "mhome.html", {})


@login_required(login_url="login")
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


@login_required(login_url="login")
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


# def forgot_password(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         otp = generateOTP()

#         # Save these values in the session for reset_password() to use
#         request.session["currentUser"] = username
#         request.session["otp"] = otp

#         # Threaded as sending emails sometimes takes time
#         try:
#             toEmail = Member.objects.get(user__username=username).email
#             thread = Thread(
#                 target=sendMail,
#                 args=(toEmail, "Request for password Reset", f"Your OTP is {otp}"),
#             )
#             thread.start()
#         except Exception as e:
#             print(e)

#         return redirect(reset_password)

#     return render(request, "forgot_password.html")


# def reset_password(request):
#     if request.method == "POST":
#         enteredOTP = request.POST.get("otp")
#         newPassword = request.POST.get("password")

#         try:
#             userToChange = User.objects.get(username=request.session.get("currentUser"))
#         except Exception as e:
#             print(e)

#         otp = request.session.get("otp")

#         if otp == enteredOTP:
#             userToChange.set_password(newPassword)
#             return HttpResponse("Password Changed Successfully")

#         else:
#             return HttpResponse("Wrong OTP Entered or user does not exist")

#     return render(request, "reset_password.html")


@login_required(login_url="login")
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
            try:
                thread = Thread(
                    target=sendMail,
                    args=(
                        email,
                        "Successfully registered to 127.0.0.1",
                        f"You have been registered to the employee portal.<br />Visit 127.0.0.1 to login.<br />Username: {username}<br />Password: {password}<br />Please change your password at the earliest and login to view further details.",
                    ),
                )
                thread.start()
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)
    return render(request, "add_employee.html")


def roster(request, leaveID):
    leave = LeaveForm.objects.get(id=leaveID)
    employee = leave.employee
    team = employee.member.team

    leavesInSameTeam = LeaveForm.objects.filter(
        employee__member__team=team,
        status="Approved",
        employee__member__designation="Employee",
    ).exclude(employee=employee)

    leaveOnSameDate = []
    for leaveInSameTeam in leavesInSameTeam:
        if check_date_overlap(
            leave.start_date,
            leave.end_date,
            leaveInSameTeam.start_date,
            leaveInSameTeam.end_date,
        ):
            leaveOnSameDate.append(leaveInSameTeam)
        print()

    context = {"leaves": leaveOnSameDate, "employee": employee}
    return render(request, "roster.html", context)


# Password reset
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",
                        "site_name": "Website",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email,
                            "admin@example.com",
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name="password/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )
