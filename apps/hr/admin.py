from django.contrib import admin
from .models.designation import Designation
from .models.advance import Advance
from .models.attendance import Attendance
from .models.department import Department
from .models.employee import Employee
from .models.salary import Salary

# Register your models here.
admin.site.register(Designation)
admin.site.register(Advance)
admin.site.register(Attendance)
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Salary)
