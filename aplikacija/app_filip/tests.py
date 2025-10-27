#Filip Pantic
import time
from django.test import LiveServerTestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth.models import User
from shared_app.models import MyUser, Student, Tutor, Notice, Tag, Applied
from django.test import TestCase, Client

class SearchAdsTest(LiveServerTestCase):
    """
    Selenium testovi za pretragu i filtriranje oglasa.
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

        user = MyUser.objects.create(
            username='teststudent', password='123', email='test@student.com', isbanned=0, isactive=1
        )
        publisher = Student.objects.create(
            iduser=user, name='Marko', surname='Markovic'
        )

        tag_psi = Tag.objects.create(value='psi')

        Notice.objects.create(
            idpublisher=publisher, title='Potrebna pomoć za Python projekat',
            subject='Programiranje 1', type='Pomoc pri ucenju'
        )
        Notice.objects.create(
            idpublisher=publisher, title='Pisanje seminarskog rada',
            subject='Sociologija', type='Pomoc pri izradi projekta'
        )
        notice_combined = Notice.objects.create(
            idpublisher=publisher, title='Izrada Web Aplikacije',
            subject='Web Dizajn', type='Pomoc pri izradi projekta'
        )
        Applied.objects.create(idnotice=notice_combined, idtag=tag_psi)

    def test_search_by_keyword_with_results(self):
        driver = self.driver
        driver.get(f"{self.live_server_url}{reverse('search_ads')}")
        driver.find_element(By.ID, "search").send_keys("Python")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait = WebDriverWait(driver, 10)
        expected_title_selector = (By.CSS_SELECTOR, ".item h5")

        wait.until(EC.text_to_be_present_in_element(expected_title_selector, "Python"))

        results = driver.find_elements(By.CLASS_NAME, "item")
        self.assertEqual(len(results), 1, "Pronađeno je više od jednog rezultata za 'Python'.")

    def test_search_no_results(self):
        driver = self.driver
        driver.get(f"{self.live_server_url}{reverse('search_ads')}")
        driver.find_element(By.ID, "search").send_keys("NEPOSTOJECIREZULTAT12345")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Čekamo da se pojavi poruka
        message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Nema oglasa koji odgovaraju filterima')]"))
        )
        self.assertTrue(message.is_displayed())


    def test_combined_search_and_filter(self):
        driver = self.driver
        driver.get(f"{self.live_server_url}{reverse('search_ads')}")
        driver.find_element(By.ID, "search").send_keys("Web")
        driver.find_element(By.ID, "tag").send_keys("psi")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "item")))

        results = driver.find_elements(By.CLASS_NAME, "item")
        self.assertEqual(len(results), 1)
        self.assertIn("Web", results[0].find_element(By.TAG_NAME, "h5").text)


class SearchAdsUnitTests(TestCase):
    """
    Unit testovi za funkcionalnost pretrage i filtriranja oglasa.
    """

    def setUp(self):
        self.client = Client()
        self.url = reverse("search_ads")

        user = MyUser.objects.create(
            username='teststudent', password='123', email='test@student.com', isbanned=0, isactive=1
        )
        publisher = Student.objects.create(
            iduser=user, name='Marko', surname='Markovic'
        )
        self.tag_psi = Tag.objects.create(value='psi')
        self.notice_python = Notice.objects.create(
            idpublisher=publisher, title='Potrebna pomoć za Python projekat',
            subject='Programiranje 1', type='Pomoc pri ucenju'
        )
        self.notice_web = Notice.objects.create(
            idpublisher=publisher, title='Izrada Web Aplikacije',
            subject='Web Dizajn', type='Pomoc pri izradi'  # <-- Koristimo kratku vrednost
        )
        self.notice_seminar = Notice.objects.create(
            idpublisher=publisher, title='Pisanje seminarskog rada',
            subject='Sociologija', type='Pomoc pri izradi'  # <-- Koristimo kratku vrednost
        )
        Applied.objects.create(idnotice=self.notice_web, idtag=self.tag_psi)

    def test_page_loads_with_all_ads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['oglasi']), 3)

    def test_search_by_keyword_success(self):
        response = self.client.post(self.url, {'search': 'Python'})
        self.assertEqual(response.status_code, 200)

        oglasi = response.context['oglasi']
        self.assertEqual(len(oglasi), 1)
        self.assertEqual(oglasi[0], self.notice_python)

    def test_search_no_results(self):
        response = self.client.post(self.url, {'search': 'nepostojeci_termin_123'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['oglasi']), 0)
        self.assertContains(response, "Nema oglasa koji odgovaraju filterima")

    def test_filter_by_type_success(self):
        response = self.client.post(self.url, {'tip': 'Pomoc pri izradi'})
        self.assertEqual(response.status_code, 200)

        oglasi = response.context['oglasi']
        self.assertEqual(len(oglasi), 2)
        self.assertNotIn(self.notice_python, oglasi)
        self.assertIn(self.notice_web, oglasi)
        self.assertIn(self.notice_seminar, oglasi)

    def test_combined_search_and_filter_success(self):
        response = self.client.post(self.url, {'search': 'Web', 'tag': 'psi'})
        self.assertEqual(response.status_code, 200)
        oglasi = response.context['oglasi']
        self.assertEqual(len(oglasi), 1)
        self.assertEqual(oglasi[0], self.notice_web)