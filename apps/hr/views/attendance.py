from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import GroupPermission

from apps.hr.models.attendance import Attendance
from apps.hr.serializers.attendance import AttendanceSerializer

from apps.share.views import get_tenant_user

from datetime import datetime


class AttendanceView(generics.ListCreateAPIView):
    queryset = Attendance
    serializer_class = AttendanceSerializer
    permission_classes = (
        IsAuthenticated,
        GroupPermission,
    )

    def get_queryset(self, *args):
        date = self.request.GET.get("date")
        user_tenant = get_tenant_user(self)
        if user_tenant is not None:
            tenant = user_tenant.tenant
            if date:
                selected_date = datetime.strptime(date, "%Y-%m-%d")
                attendance = tenant.attendance_base_models.filter(
                    date__date=selected_date
                )

            else:
                attendance = tenant.attendance_base_models.all().order_by("-created_at")
            return attendance
        else:
            print("Tenant id not found")

    def create(self, request, *args, **kwargs):
        tenant = get_tenant_user(self).tenant
        employee_lines = request.data["employee_lines"]
        date = datetime.fromisoformat(request.data["date"][:-1])
        week = request.data["week"]
        created_attendances = []
        if tenant is not None:
            for line in employee_lines:
                if line["attend_status"] != None:
                    # Check if there is an existing record for the employee and date
                    attendance = Attendance.objects.filter(
                        employee=line["employee"],
                        date__date=date,
                    ).first()

                    print(attendance)
                    # print(attendance.date)

                    if attendance:
                        # If an attendance record exists, update it with the new data
                        serializer = AttendanceSerializer(attendance, data=line)
                    else:
                        # If no attendance record exists, create a new one
                        line["date"] = date
                        line["week"] = week
                        serializer = AttendanceSerializer(data=line)

                    if serializer.is_valid():
                        serializer.save(tenant=tenant)
                        created_attendances.append(serializer.data)
                    else:
                        print(serializer.errors)

            return Response(created_attendances, status=status.HTTP_201_CREATED)

        else:
            print("Tenant not found.")
            return Response(
                {"error": "Tenant not found."}, status=status.HTTP_404_NOT_FOUND
            )
