from django.contrib.auth.models import User
from django.test import TestCase, Client
from shared_app.models import Admin, MyUser, Student, Tutor, Verification
from django.contrib.auth.hashers import make_password

class AdminVerifyRemoveTests(TestCase):
    def setUp(self):
        self.user_admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )

        self.my_user_admin = MyUser.objects.create(
            username="admin",
            email="admin@example.com",
            password=make_password("admin123"),
            isactive=1,
            isbanned=0
        )

        self.user_toDelete = User.objects.create_user(
            username="target_user",
            email="target@example.com",
            password="password123"
        )

        self.target_user = MyUser.objects.create(
            username="target_user",
            email="target@example.com",
            password=make_password("password123"),
            isactive=1,
            isbanned=0
        )

        self.user_tutor = User.objects.create_user(
            username="target_tutor",
            email="target_tutor@example.com",
            password="password123"
        )

        self.target_tutor = MyUser.objects.create(
            username="target_tutor",
            email="target_tutor@example.com",
            password=make_password("password123"),
            isactive=1,
            isbanned=0
        )

        self.admin = Admin.objects.create(iduser=self.my_user_admin)
        self.toDelete=Student.objects.create(iduser=self.target_user)
        self.tutorVerify=Tutor.objects.create(iduser=self.target_tutor,name="TutorTest",surname="Test",dateofbirth="2025-10-14",isverified=0)
        Verification.objects.create(iduser=self.tutorVerify)

        self.client = Client()

    def test_admin_remove_user(self):
        response = self.client.post("/login/", {
            "username": "admin",
            "password": "admin123"
        }, follow=True)

        self.assertIn("/admin_panel", response.redirect_chain[-1][0])

        response = self.client.post("/admin_panel/remove/", {
            "username": "target_user",
            "search": "Search"
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "target_user")

        response = self.client.post("/admin_panel/remove/", {
            "user_id": self.target_user.iduser,
            "remove": "Remove"
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.isactive, 0)
        self.assertEqual(self.target_user.isbanned, 1)

    def test_admin_verify_tutor(self):
        response = self.client.post("/login/", {
            "username": "admin",
            "password": "admin123"
        }, follow=True)
        self.assertIn("/admin_panel", response.redirect_chain[-1][0])

        response = self.client.post("/admin_panel/verify/", {
            "tutor_id": self.tutorVerify.iduser.iduser,
            "action": "verify"
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        # Proveri da je tutor verifikovan
        self.tutorVerify.refresh_from_db()
        self.assertEqual(self.tutorVerify.isverified, 1)

        # Proveri da je verification obrisan
        self.assertFalse(Verification.objects.filter(iduser=self.tutorVerify).exists())
