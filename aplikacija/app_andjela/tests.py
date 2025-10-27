from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from shared_app.models import MyUser, Student, Tutor, Admin


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

