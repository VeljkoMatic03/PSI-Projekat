from django.shortcuts import render, redirect

from shared_app.models import Cv, Tutor, MyUser


# Create your views here.

def dashboard_tutor(request):
    return render(request, 'dashboard-tutor.html')

def create_cv(request):
    if request.method == 'POST':
        user =  MyUser.objects.filter(username=request.user)
        print("                     ", user.first().iduser)
        tutor = Tutor.objects.filter(iduser=user.first().iduser)
        cv = Cv.objects.filter(idtutor=user.first().iduser)

        if cv:
            msg = "Vec ste kreirali CV"
            return render(request, 'create-cv.html', {'msg': msg})

        ime = request.POST['ime']
        prezime = request.POST['prezime']
        slika = request.POST['slika']
        oMeni = request.POST['oMeni']
        edukacija = request.POST['edukacija']
        projekti = request.POST['projekti']
        iskustvo = request.POST['iskustvo']

        Cv.objects.create(
            name=ime,
            surname=prezime,
            picture=slika,
            aboutme=oMeni,
            education=edukacija,
            projects=projekti,
            experience=iskustvo,
            idtutor=tutor.first()
        )

        return redirect('dashboard-tutor')

    return render(request, 'create-cv.html')

def edit_cv(request):
    return render(request, 'edit-cv.html')

def download_cv(request):
    return render(request, 'dashboard-tutor.html', {'msg': "nemate cv"})
