from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from shared_app.models import MyUser, Student, Tutor, Admin
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time


class LoginUserTests(TestCase):
    """
    Unit testovi za funkciju login_user koja omogućava prijavu
    studenta, tutora i admina, kao i test neuspešne prijave
    i ponovne prijave već autentifikovanog korisnika.
    """

    def setUp(self):
        self.client = Client()

        self.user_student = User.objects.create_user(username="student1", password="123")
        self.user_tutor = User.objects.create_user(username="tutor1", password="123")
        self.user_admin = User.objects.create_user(username="admin1", password="123")

        my_student = MyUser.objects.create(username="student1", email="s1@mail.com", password="123", isactive=1, isbanned=0)
        my_tutor = MyUser.objects.create(username="tutor1", email="t1@mail.com", password="123", isactive=1, isbanned=0)
        my_admin = MyUser.objects.create(username="admin1", email="a1@mail.com", password="123", isactive=1, isbanned=0)

        Student.objects.create(iduser=my_student, name="Marko", surname="Marković")
        Tutor.objects.create(iduser=my_tutor, name="Jovan", surname="Jović", isverified=0)
        Admin.objects.create(iduser=my_admin)

        self.url = reverse("login")

    def test_login_student_success(self):
        """Test uspešne prijave studenta"""
        response = self.client.post(self.url, {"username": "student1", "password": "123"})
        self.assertRedirects(response, reverse("dashboard-student"))

    def test_login_tutor_success(self):
        """Test uspešne prijave tutora"""
        response = self.client.post(self.url, {"username": "tutor1", "password": "123"})
        self.assertRedirects(response, reverse("dashboard-tutor"))

    def test_login_admin_success(self):
        """Test uspešne prijave admina"""
        response = self.client.post(self.url, {"username": "admin1", "password": "123"})
        self.assertRedirects(response, reverse("adminpanel"))

    def test_login_invalid_user(self):
        """Test neuspešne prijave (nepostojeći korisnik ili pogrešna lozinka)"""
        response = self.client.post(self.url, {"username": "nesto", "password": "nesto"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Netacna sifra ili nepostojeci korisnik")

    def test_already_authenticated_student_redirect(self):
        """Test da već prijavljeni student bude automatski preusmeren"""
        self.client.login(username="student1", password="123")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard-student"))
        

class RegisterUserTests(TestCase):
    """
    Testira registraciju korisnika: student ili tutor.
    Pokriva uspešne i neuspešne scenarije.
    """

    def setUp(self):
        """Kreira klijent i postojećeg korisnika za test username zauzet"""
        self.client = Client()
        self.existing_user = MyUser.objects.create(
            username="postojeci",
            password="123",
            email="postojeci@mail.com",
            isactive=1,
            isbanned=0
        )

    def test_student_registration_success(self):
        """Uspešna registracija studenta"""
        response = self.client.post(reverse('register'), {
            'username': 'student1',
            'password': '123',
            'email': 'student1@mail.com',
            'ime': 'Marko',
            'prezime': 'Markovic',
            'datum': '2000-01-01',
            'role': 'student'
        })
        self.assertRedirects(response, reverse('homepage'))
        self.assertTrue(Student.objects.filter(iduser__username='student1').exists())

    def test_tutor_registration_success(self):
        """Uspešna registracija tutora"""
        response = self.client.post(reverse('register'), {
            'username': 'tutor1',
            'password': '123',
            'email': 'tutor1@mail.com',
            'ime': 'Jovan',
            'prezime': 'Jovanovic',
            'datum': '1995-05-05',
            'role': 'tutor'
        })
        self.assertRedirects(response, reverse('homepage'))
        self.assertTrue(Tutor.objects.filter(iduser__username='tutor1').exists())

    def test_registration_fail_username_taken(self):
        """Neuspešna registracija zbog zauzetog username-a"""
        response = self.client.post(reverse('register'), {
            'username': 'postojeci',
            'password': '123',
            'email': 'novi@mail.com',
            'ime': 'Pera',
            'prezime': 'Peric',
            'datum': '2001-02-02',
            'role': 'student'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Postoji korisnik')


##########################################################################

class LoginSeleniumTests(StaticLiveServerTestCase):
    """
    Selenium testovi za login funkcionalnost
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        # Kreiramo korisnike u bazi
        self.user_student = User.objects.create_user(username='student1', password='123', email='s1@mail.com')
        self.user_tutor = User.objects.create_user(username='tutor1', password='123', email='t1@mail.com')
        self.user_admin = User.objects.create_superuser(username='admin1', password='adminpass', email='a1@mail.com')

        self.my_student = MyUser.objects.create(username='student1', email='s1@mail.com', password='123', isactive=1, isbanned=0)
        self.my_tutor = MyUser.objects.create(username='tutor1', email='t1@mail.com', password='123', isactive=1, isbanned=0)

        Student.objects.create(iduser=self.my_student, name='Pera', surname='Peric', dateofbirth='2000-01-01')
        Tutor.objects.create(iduser=self.my_tutor, name='Mika', surname='Mikic', dateofbirth='1995-01-01', isverified=1)

    def test_student_login_success(self):
        """Uspesna prijava studenta"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")
        self.driver.find_element(By.NAME, "username").send_keys("student1")
        self.driver.find_element(By.NAME, "password").send_keys("123")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(5)

        body = self.driver.page_source
        self.assertNotIn("Prijavi se", body)

    def test_tutor_login_success(self):
        """Uspesna prijava tutora"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")
        self.driver.find_element(By.NAME, "username").send_keys("tutor1")
        self.driver.find_element(By.NAME, "password").send_keys("123")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(5)

        body = self.driver.page_source
        self.assertNotIn("Prijavi se", body)

    def test_admin_login_success(self):
        """Uspesna prijava admina"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")
        self.driver.find_element(By.NAME, "username").send_keys("admin1")
        self.driver.find_element(By.NAME, "password").send_keys("adminpass")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(5)

        body = self.driver.page_source
        self.assertNotIn("Prijavi se", body)

    def test_invalid_login_failure(self):
        """Neuspesna prijava sa pogresnim podacima"""
        self.driver.get(f"{self.live_server_url}{reverse('login')}")
        self.driver.find_element(By.NAME, "username").send_keys("nesto")
        self.driver.find_element(By.NAME, "password").send_keys("nesto")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(5)

        body = self.driver.page_source
        self.assertIn("Prijavi se", body)
        
        
class RegistrationSeleniumTests(StaticLiveServerTestCase):
    """
    Selenium testovi za formu registracije korisnika (student/tutor).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        return

    def fill_registration_form(self, ime, prezime, email, datum, username, password, role):
        """Pomoćna metoda za popunjavanje forme"""
        driver = self.driver
        driver.get(f"{self.live_server_url}/register/")
        print("              ", role)
        driver.find_element(By.NAME, "ime").send_keys(ime)
        driver.find_element(By.NAME, "prezime").send_keys(prezime)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "datum").send_keys(datum)
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, f"input[name='role'][value='{role}']").click()
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)

    def test_successful_student_registration(self):
        """Test uspešne registracije studenta"""
        self.fill_registration_form(
            ime="Marko",
            prezime="Markovic",
            email="marko@mail.com",
            datum="2000-05-10",
            username="student1",
            password="123",
            role="student"
        )
        self.assertEqual(MyUser.objects.filter(username="student1").exists(), True)
        self.assertEqual(Student.objects.filter(iduser__username="student1").exists(), True)


    def test_successful_tutor_registration(self):
        """Test uspešne registracije tutora"""
        self.fill_registration_form(
            ime="Ana",
            prezime="Anic",
            email="ana@mail.com",
            datum="2000-05-10",
            username="tutor1",
            password="123",
            role="tutor"
        )
        self.assertEqual(MyUser.objects.filter(username="tutor1").exists(), True)
        self.assertEqual(Tutor.objects.filter(iduser__username="tutor1").exists(), True)

    def test_username_already_taken(self):
        """Test neuspešne registracije – korisničko ime zauzeto."""
        user=MyUser.objects.create(username="tutor1", email="isto@mail.com", password="123", isactive=1, isbanned=0)
        Student.objects.create(iduser=user, name="isto", surname="ime", dateofbirth="2003-01-01")

        self.fill_registration_form(
            ime="Ana",
            prezime="Anic",
            email="ana@mail.com",
            datum="2000-05-10",
            username="tutor1",
            password="123",
            role="tutor"
        )

        body = self.driver.page_source
        self.assertIn("Postoji korisnik", body)
      

    def test_missing_required_field(self):
        """Test neuspešne registracije – obavezno polje (ime) nije popunjeno"""
        driver = self.driver
        driver.get(f"{self.live_server_url}/register/")
        driver.find_element(By.NAME, "prezime").send_keys("Nemanja")
        driver.find_element(By.NAME, "email").send_keys("n@mail.com")
        driver.find_element(By.NAME, "datum").send_keys("2001-11-02")
        driver.find_element(By.NAME, "username").send_keys("bezimena")
        driver.find_element(By.NAME, "password").send_keys("123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)

        invalid_inputs = driver.find_elements(By.CSS_SELECTOR, "input:invalid")
        self.assertTrue(any(inp.get_attribute("name") == "ime" for inp in invalid_inputs))
