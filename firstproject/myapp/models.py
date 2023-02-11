from django.db import models

# Create your models here.
'''
class Book(models.Model):
    title=models.CharField(max_length=200)
    pub_date=models.DateTimeField('date published')
'''
class Member(models.Model):
    fname=models.CharField(max_length=50)
    lname=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    psswd=models.CharField(max_length=50)
    age=models.IntegerField()

    def __str__(self):
        return self.fname + ' ' + self.lname
        #return str(self.fname + self.lname + self.email + str(self.age))

class Employee(models.Model):
    emp_id=models.IntegerField(max_length=10)
    fname=models.CharField(max_length=50)
    lname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    DOB = models.CharField(max_length=50)
    phone_number=models.CharField(max_length=10)
    doj=models.CharField(max_length=10)
    department=models.CharField(max_length=50)
    designation=models.CharField(max_length=50)
    address=models.CharField(max_length=100)

    def __str__(self):
        return self.fname

class LeaveForm(models.Model):
    employee = models.ForeignKey(Employee,default=1, on_delete=models.CASCADE)
    start_date=models.CharField(max_length=50)
    end_date=models.CharField(max_length=50)
    reason=models.CharField(max_length=100)

    def __str__(self):
        return self.employee.fname + " " + self.employee.lname + " ///  " + self.start_date + " to " + self.end_date
