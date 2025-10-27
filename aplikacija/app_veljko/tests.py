#Veljko Matic
# Create your tests here.
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import date

from shared_app.models import Tutor, Cv, MyUser

User = get_user_model()

class TutorTest(StaticLiveServerTestCase):
    def setUp(self) -> None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        self.driver.implicitly_wait(5)

        self.user = User.objects.create_user(
            username="tutor_test",
            email="tutor@gmail.com",
            password="testpass123"
        )

        self.myUser = MyUser.objects.create(
            username=self.user.username,
            email=self.user.email,
            password=self.user.password,
            isbanned=0,
            isactive=1
        )

        Tutor.objects.create(iduser=self.myUser, name="Test", surname="Tutor", isverified=0, dateofbirth=date(2025, 10, 26))

    def tearDown(self) -> None:
        self.driver.quit()

    def test_tutor_create_cv(self):
        driver = self.driver
        driver.get(f"{self.live_server_url}/login")

        driver.find_element(By.NAME, "username").send_keys("tutor_test")
        driver.find_element(By.NAME, "password").send_keys("testpass123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        time.sleep(3)
        self.assertIn("/dashboard_tutor", driver.current_url)

        driver.get(f"{self.live_server_url}/create_cv/")
        time.sleep(1)

        driver.find_element(By.NAME, "ime").send_keys("Test")
        driver.find_element(By.NAME, "prezime").send_keys("Tutor")
        driver.find_element(By.NAME, "oMeni").send_keys("Ovo je test")
        driver.find_element(By.NAME, "edukacija").send_keys("ETF")
        driver.find_element(By.NAME, "projekti").send_keys("StudyBuddy")
        driver.find_element(By.NAME, "iskustvo").send_keys("Bez prakse")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)

        try:
            submit_btn.click()
        except:
            driver.execute_script("arguments[0].click();", submit_btn)

        time.sleep(3)
        self.assertIn('/dashboard_tutor', driver.current_url)
        print("Uspesan test")

class CVTest(TestCase):

    def setUp(self) -> None:

        self.user = User.objects.create_user(
            username="tutor_test",
            email="tutor@gmail.com",
            password="testpass123"
        )

        self.myUser = MyUser.objects.create(
            username=self.user.username,
            email=self.user.email,
            password=self.user.password,
            isbanned=0,
            isactive=1
        )

        self.tutor = Tutor.objects.create(iduser=self.myUser, name="Test", surname="Tutor", isverified=0,
                             dateofbirth=date(2025, 10, 26))

        self.cv = Cv.objects.create(idtutor=self.tutor, name = "Test", surname="Tutor", education="ETF", aboutme="Opis",
                                    projects="PSI projekat", experience="Nemam")

        self.client = Client()
        self.client.login(username = "tutor_test", password = "testpass123")

    def test_download_cv(self):
        response = self.client.get(reverse("download_cv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b"%PDF-"), "Response nije validan PDF fajl")

    def test_cv_belongs_to_tutor(self):
        user = MyUser.objects.create(username="test", email="test@test.com", password="123", isactive=1, isbanned=0)
        tutor = Tutor.objects.create(iduser=user, name="T", surname="S", isverified=False, dateofbirth=date(2025, 10, 26))
        cv = Cv.objects.create(idtutor=tutor, name="Test", surname="Tutor", education="ETF")

        self.assertEqual(cv.idtutor, tutor)
        self.assertEqual(cv.idtutor.name, "T")

    def test_redirect_to_dashboard(self):
        data = {
            "novoIme": "Test",
            "novoPrezime": "Tutor",
            "novoOMeni": "Opis",
            "novaEdukacija": "ETF",
            "noviProjekti": "Test projekat",
            "novoIskustvo": "Bez prakse"
        }
        response = self.client.post(reverse("edit_cv"), data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "dashboard-tutor.html")
