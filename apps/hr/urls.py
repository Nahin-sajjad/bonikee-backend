from django.urls import path
from apps.hr.views.employee import EmployeeView, EmployeeDetailView
from apps.hr.views.attendance import AttendanceView
from apps.hr.views.salary import SalaryView, SalaryDetailView
from apps.hr.views.filtered_salary_list import FilterSalaryListView
from apps.hr.views.designation import DesignationView, DesignationDetailView
from apps.hr.views.department import DepartmentView, DepartmentDetailView
from apps.hr.views.advance import AdvanceView, AdvanceDetailView

urlpatterns = [
    path("employee/", EmployeeView.as_view(), name="employee-list"),
    path("employee/<int:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),

    path("attendance/", AttendanceView.as_view(), name="attendance-list"),

    path('filter-salary/', FilterSalaryListView.as_view(),
         name='filter-salary-list'),

    path('salary/', SalaryView.as_view(), name='salary-list'),
    path('salary/<int:pk>/', SalaryDetailView.as_view(), name='salary-detail'),


    path('designation/', DesignationView.as_view(), name='designation-list'),
    path('designation/<int:pk>/', DesignationDetailView.as_view(),
         name='designation-detail'),

    path('department/', DepartmentView.as_view(), name='department-list'),
    path('department/<int:pk>/', DepartmentDetailView.as_view(),
         name='department-detail'),
    
    path('advance/', AdvanceView.as_view(), name='advance-list'),
    path('advance/<int:pk>/', AdvanceDetailView.as_view(), name='advance-detail'),

]
