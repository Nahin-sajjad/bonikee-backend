from django.urls import reverse

from rest_framework import status

from apps.share.test.base import BaseTestCase


class EmployeeTestCase(BaseTestCase):

    def test_list_employee(self):
        url = reverse("employee-list")

        for i in range(0, 6):
            self.get_or_create_employee(1)

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_employee(self):
        url = reverse('employee-list')
        department_id = self.get_or_create_department(1).pk
        designation_id = self.get_or_create_designation(1).pk
        data = {
        'values': ['{"id": "","name": "Computer Science", "dept": 1, "desig" : 1,"doj":"2023-07-01", "emp_wage_type":1, "hr_per_day":"5","salary":"5000", "addr": "adasdasd", "nid" : "3242432423423", "phone":"01846445294", "status":"1" }'],
    "photo": self.generate_photo(),
    "id": ""
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_employee(self):
        employee = self.get_or_create_employee(1)
        url = reverse("employee-detail", kwargs={"pk": employee.id})
        department_id = self.get_or_create_department(1).pk
        designation_id = self.get_or_create_designation(1).pk

        data = {
        'values': ['{"id": 1,"name": "Computer Apartment", "dept": 1, "desig" : 1,"doj":"2023-07-01", "emp_wage_type":1, "hr_per_day":"5","salary":"5000", "addr": "adasdasdfsdfsdfs", "nid" : "3242432423423", "phone":"01846445294", "status":"1" }'],
    "photo": self.generate_photo(),
    "id": "1"
        }
        response = self.client.put(url, data)

        self.assertEqual(response.data["name"], "Computer Apartment")
        self.assertEqual(response.data["addr"], "adasdasdfsdfsdfs")

    def test_delete_employee(self):
        employee = self.get_or_create_employee(1)
        url = reverse("employee-detail", kwargs={"pk": employee.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
