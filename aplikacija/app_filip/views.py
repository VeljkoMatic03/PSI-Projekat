from datetime import datetime

from django.contrib.auth import login, authenticate

from shared_app.models import MyUser, Student, Tutor, Admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def homepage(request):
    """
        Sluzi kao pocetna stranica.

        Nudi linkove ka :template:`login.html` i :template:`register.html` za nastavak koriscenja sajta.



    """
    return render(request, 'index.html')

def register_user(request):
    """
        Funkcionalnost sluzi da registruje novog korisnika kao studenta ili tutora.

        Korisnik popuni formu na :template:`register.html` i pošalje podatke.

        Kreira se novi :model:`shared_app.MyUser` objekat,kao i odgovarajući :model:`shared_app.Student` ili :model:`shared_app.Tutor` profil,
        nakon čega se korisnik preusmerava na početnu stranicu.
    """
    msgError = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        ime = request.POST['ime']
        prezime = request.POST['prezime']
        datum = request.POST['datum']
        role = request.POST['role']

        datum = datetime.strptime(datum, "%Y-%m-%d").date()

        userExisting = MyUser.objects.filter(username=username).exists()
        if userExisting:
            msgError = 'Postoji korisnik'
            return render(request, 'register.html', {'msg': msgError})

        emailExisting = User.objects.filter(email=email).exists()
        if emailExisting:
            msgError = 'Email vec upotrebljen'
            return render(request, 'register.html', {'msg': msgError})

        user = User.objects.create_user(username=username, password=password, email=email)
        myuser = MyUser.objects.create(
            username=username,
            password=user.password,
            email=email,
            isbanned=0,
            isactive=1
        )
        if role == 'student':
            Student.objects.create(
                iduser=myuser,
                name=ime,
                surname=prezime,
                dateofbirth=datum
            )
        elif role == 'tutor':
            Tutor.objects.create(
                iduser=myuser,
                name=ime,
                surname=prezime,
                dateofbirth=datum,
                isverified=0
            )
        return redirect('homepage')
    return render(request, 'register.html', {'msg': msgError})

def login_user(request):
    """
        Prijavljuje postojećeg korisnika i preusmerava ga na odgovarajuću kontrolnu tablu.

        Ova funkcija proverava da li je korisnik već prijavljen. Ako jeste,
        preusmerava ga na osnovu njegove uloge (student, tutor, admin).

        Ako nije prijavljen i zahtev je POST, pokušava da autentifikuje
        korisnika sa prosleđenim korisničkim imenom i lozinkom.

        **Redirectovi:**

        * :template:`dashboard-student.html` ako je korisnik student.
        * :template:`dashboard-tutor.html` ako je korisnik tutor.
        * :template:`adminpanel.html` ako je korisnik admin.
        """
    errorMsg = None
    if request.user.is_authenticated:
        if Student.objects.filter(iduser__username=request.user.username).exists():
            return redirect('dashboard-student')
        if Tutor.objects.filter(iduser__username=request.user.username).exists():
            return redirect('dashboard-tutor')
        if Admin.objects.filter(iduser__username=request.user.username).exists():
            return redirect('adminpanel')
        userAdmin = request.user
        myUserAdmin = MyUser(username=userAdmin.username, email=userAdmin.email,
                             password=userAdmin.password, isactive=1, isbanned=0)
        myUserAdmin.save()
        admin = Admin(iduser=myUserAdmin)
        admin.save()
        return redirect('adminpanel')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            errorMsg = 'Netacna sifra ili nepostojeci korisnik'
            return render(request, 'login.html', {'error': errorMsg})
        login(request, user)
        if Student.objects.filter(iduser__username=request.user.username).exists():
            return redirect('dashboard-student')
        if Tutor.objects.filter(iduser__username=request.user.username).exists():
            return redirect('dashboard-tutor')
        if Admin.objects.filter(iduser__username=request.user.username).exists():
            return redirect('adminpanel')
        userAdmin = request.user
        myUserAdmin = MyUser(username=userAdmin.username, email=userAdmin.email,
                             password=userAdmin.password, isactive=1, isbanned=0)
        myUserAdmin.save()
        admin = Admin(iduser=myUserAdmin)
        admin.save()
        return redirect('adminpanel')
    return render(request, 'login.html', {'error': errorMsg})
def reset_password(request):
    """
        Prikazuje stranicu za pokretanje procesa resetovanja lozinke.

        Ova funkcija je deo ugrađenog Django sistema za resetovanje lozinke,
        koji se oslanja na slanje tokena na email korisnika.

        1.  Korisnik unosi svoju email adresu na formi koju prikazuje ovaj view.

        2.  Nakon slanja forme, Django generiše token i šalje email sa linkom za resetovanje na unetu adresu.

        3.  Korisnik otvara link iz email-a, koji ga vodi na stranicu gde može da unese novu lozinku.

        4.  Nakon potvrde, lozinka se ažurira u sistemu.

            **Redirectovi:**

            * :template:`reset-password.html` je pocetni template.

            * :template:`password_reset_form` je template gde korisnik unosi svoju email adresu.

            * :template:`password_reset_done` je template koji obavestava korisnika da mu je poslat mail na odredjenu adresu.

            * :template:`password_reset_confirm` je template za stranicu na kojoj korisnik bira novu lozinku kada klikne na link u mailu.

            * :template:`password_reset_complete` je template za poslednju stranicu koja potvrdjuje korisniku da je uspesno promenio lozinku.

    """
    errorMsg = None
    return render(request, 'reset-password.html', {'error': errorMsg})
