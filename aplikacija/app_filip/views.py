from datetime import datetime

from django.contrib.auth import login, authenticate

from shared_app.models import MyUser, Student, Tutor, Admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


def homepage(request):
    return render(request, 'index.html')

def register_user(request):
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
