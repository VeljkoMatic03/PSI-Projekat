from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import time
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from webdriver_manager.chrome import ChromeDriverManager

from shared_app.models import Admin, MyUser, Student, Tutor, Verification, Notice, Collaboration, Rating
from django.contrib.auth.hashers import make_password
#Luka Zdravic

class AdminUserTutorFuncionalitiesTests(TestCase):
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

        self.tutorVerify.refresh_from_db()
        self.assertEqual(self.tutorVerify.isverified, 1)

        self.assertFalse(Verification.objects.filter(iduser=self.tutorVerify).exists())

    def test_admin_remove_nonexistent_user(self):
        response = self.client.post("/admin_panel/remove/", {
            "username": "nonexistent_user",
            "search": "Search"
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nema korisnika sa tim korisnickim imenom")

    def test_admin_remove_admin_user(self):
        response = self.client.post("/admin_panel/remove/", {
            "username": "admin",
            "search": "Search"
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin se ne moze ukloniti")

    def test_admin_reject_tutor(self):
        response = self.client.post("/admin_panel/verify/", {
            "tutor_id": self.tutorVerify.iduser.iduser,
            "action": "reject"
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.tutorVerify.refresh_from_db()
        self.assertEqual(self.tutorVerify.isverified, 0)

        self.assertFalse(Verification.objects.filter(iduser=self.tutorVerify).exists())

    def test_student_rates_tutor(self):
        self.client.force_login(self.user_toDelete)
        notice = Notice.objects.create(
            title="Test Oglas",
            subject="Matematika",
            type="Help",
            description="Opis",
            idpublisher=self.toDelete
        )
        collab = Collaboration.objects.create(
            idnotice=notice,
            idstudent=self.toDelete,
            idtutor=self.tutorVerify,
            datebegin="2025-10-01",
            dateend="2025-10-10"
        )

        url = reverse('rate', args=[notice.idnotice])
        response = self.client.post(url, {
            "rating": "5",
            "comment": "Super tutor"
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        rating = Rating.objects.get(idcollaboration=collab, idratinguser=self.target_user)
        self.assertEqual(rating.value, 5)
        self.assertEqual(rating.comment, "Super tutor")

User = get_user_model()
EDGE_DRIVER_PATH = r"C:\Users\lukaz\Downloads\edgedriver_win64\msedgedriver.exe"

class AdminPanelTests(StaticLiveServerTestCase):
    def setUp(self) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        self.driver.implicitly_wait(5)

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

    def tearDown(self) -> None:
        self.driver.quit()

    def test_admin_remove_user(self):
        driver = self.driver
        driver.get(f"{self.live_server_url}/login/")

        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        time.sleep(2)
        self.assertIn("/admin_panel", driver.current_url)

        driver.get(f"{self.live_server_url}/admin_panel/remove/")
        driver.find_element(By.NAME, "username").send_keys("target_user")
        driver.find_element(By.NAME, "search").click()

        time.sleep(1)
        driver.find_element(By.NAME, "remove").click()
        time.sleep(2)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.isactive, 0)
        self.assertEqual(self.target_user.isbanned, 1)

    def test_admin_verify_tutor(self):
        driver = self.driver
        driver.get(f"{self.live_server_url}/login/")

        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        time.sleep(2)
        self.assertIn("/admin_panel", driver.current_url)

        driver.get(f"{self.live_server_url}/admin_panel/verify/")
        driver.find_element(By.CSS_SELECTOR, "button[value='verify']").click()

        time.sleep(2)
        self.tutorVerify.refresh_from_db()
        self.assertEqual(self.tutorVerify.isverified, 1)
        self.assertFalse(Verification.objects.filter(iduser=self.tutorVerify).exists())