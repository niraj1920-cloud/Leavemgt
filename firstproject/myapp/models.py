from django.db import models
from django.contrib.auth.models import User

# Create your models here.
"""
class Book(models.Model):
    title=models.CharField(max_length=200)
    pub_date=models.DateTimeField('date published')
"""
# class


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="0")
    fname = models.CharField(max_length=50, null=True)
    lname = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    DOB = models.DateField(max_length=50, null=True)
    phone_number = models.CharField(max_length=10, default="0000000000")
    doj = models.DateField(max_length=10, null=True)
    department = models.CharField(max_length=50, null=True)
    designation = models.CharField(max_length=50, default="Employee")
    address = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.fname + " " + self.lname
        # return str(self.fname + self.lname + self.email + str(self.age))


# class Employee(models.Model):
#     emp_id = models.IntegerField(max_length=10)
#     fname = models.CharField(max_length=50)
#     lname = models.CharField(max_length=100)
#     email = models.EmailField(max_length=100)
#     DOB = models.CharField(max_length=50)
#     phone_number = models.CharField(max_length=10)
#     doj = models.CharField(max_length=10)
#     department = models.CharField(max_length=50)
#     designation = models.CharField(max_length=50)
#     address = models.CharField(max_length=100)

#     def __str__(self):
#         return self.fname


class LeaveForm(models.Model):
    employee = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50)
    reason = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default="applied")

    def __str__(self):
        return (
            self.employee.member.fname
            + " "
            + self.employee.member.lname
            + " ///  "
            + self.start_date
            + " to "
            + self.end_date
            + " ///  "
            + self.start_date
        )
