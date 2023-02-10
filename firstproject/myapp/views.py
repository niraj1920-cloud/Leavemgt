from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
#from django.contrib.auth.models import Employee
#from path.to.models import Employee
from .models import Member, Employee
from .models import LeaveForm
from django.contrib import messages
from django.http import HttpResponse

# Create your views here.
def home(request):
    all_members=Member.objects.all
    return render(request, 'hi.html', {'all':all_members})

def login_user(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        utype=request.POST['user-type']
        #print(username,password)
        user = authenticate(request, username=username,password=password)
        #user = authenticate(request, username=Fname, password=Password)
        if user is not None:
            if utype == "employee":
                return render(request, 'nav.html')
            else:
                return render(request, 'manager_dash.html')
            login(request, user)
            return redirect('nav')
        else:
            messages.success(request, ("There was an Error Loggin In, Try Again..."))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def navigation(request):
    return render(request, 'nav.html', {})

def leave(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        start_date=request.POST.get('start_date')
        end_date=request.POST.get('end_date')
        reason=request.POST.get('reason')
        leaveform=LeaveForm(name=name,email=email,start_date=start_date,end_date=end_date,reason=reason)
        leaveform.save()
        messages.success(request,"Leave Details submitted successfully!")
    return render(request, 'leave.html', {})

def logout(request):
    return render(request, 'logout.html', {})

def leave_history(request):
    return render(request, 'leave_history.html', {})

def profile(request):
    username = request.user.username
    print(username.capitalize())
    profile = Employee.objects.get(fname=username.capitalize())
    return render(request, 'profile.html', {'profile': profile})

def manager_dash(request):
    return render(request, 'manager_dash.html', {})

def manager_leaveapproval(request):
    return render(request, 'manager_leaveapproval.html', {})

def manageraddemp(request):
    return render(request, 'manageraddemp.html', {})
