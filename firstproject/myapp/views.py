from datetime import datetime
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
            if(not hasattr(request.user,'member')):
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


# @login_required(login_url="login")
def navigation(request):
    if request.user.is_authenticated:
        print("yes bro")
    else:
        print("NO")
    return render(request, "ehome.html", {})


def leave(request):
    profile = request.user.member.fname
    if request.method == "POST":
        stDate = request.POST.get("start_date")
        endDate = request.POST.get("end_date")
        reason = request.POST.get("reason")
        temp=LeaveForm.objects.filter(employee=request.user.member.user).values()
        start_date=datetime.strptime(stDate, '%Y-%m-%d').date()
        end_date=datetime.strptime(endDate, '%Y-%m-%d').date()   
        days = leave_days(stDate, endDate)
        leaveform = LeaveForm(
                       employee=request.user,
                       start_date=start_date,
                       end_date=end_date,
                       reason=reason,
                       days=days,
                    )            
        if(temp.__len__()==0):
                Member.objects.filter(user=request.user.member.user).update(leave_balance=request.user.member.leave_balance-days)
                leaveform.save()
                messages.success(request, "Leave Details submitted successfully!")
        else:
            for ele in temp:
                if(ele['end_date'] > start_date and ele['start_date']<end_date and start_date<end_date):
                    msg="Leave dates correspond to previously applied leave:"
                    messages.error(request,msg)
                    for key,value in ele.items():
                        if(key=='start_date' or key=='end_date' or key=='reason' or key=='status'):
                            messages.error(request,"\n"+str(key)+":"+str(value))
                    break
            else:
                Member.objects.filter(user=request.user.member.user).update(leave_balance=request.user.member.leave_balance-days)
                leaveform.save()
                messages.success(request, "Leave Details submitted successfully!")
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
    if request.method=="POST":
        number=request.POST['number']
        emailId=request.POST['emailId']
        empId=request.POST['empId']
        Member.objects.filter(id=empId).update(email=emailId,phone_number=number)
    return render(request,"profile.html")



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
    if request.method == "POST":
        employee = request.POST.get("employee")
        team = request.POST.get("team")
        # print("EEEEEEEEEEEEEEEEEEEEEEE", employee, team)

        currEmp = Member.objects.get(user = employee)
        currEmp.team = team
        currEmp.save()
        # print("FFFFFFFFFFFFFFFFFF", currEmp)


    employees = Member.objects.filter(designation = "Employee")
    return render(request, "manageraddemp.html", {"employees": employees})


def teams(request):
    team1_employees = Member.objects.filter(team="Marketing", designation = "Employee")
    team2_employees = Member.objects.filter(team="Development", designation = "Employee")
    team3_employees = Member.objects.filter(team="Design", designation = "Employee")
    team4_employees = Member.objects.filter(team="bench", designation = "Employee")
    context = {"team1_employees":team1_employees,
               "team2_employees":team2_employees,
               "team3_employees":team3_employees,
               "others_employees":team4_employees,}
    return render(request, "teams_page.html", context)


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
