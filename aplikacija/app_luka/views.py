from datetime import date

from django.shortcuts import render, redirect

from shared_app.models import Notice, Student, Tutor, Request, Collaboration


# Create your views here.
def create_ad(request):
    if request.method=="POST":
        naziv_oglasa=request.POST.get('naziv_oglasa')
        predmet=request.POST.get('predmet')
        tip_pomoci=request.POST.get('tip_pomoci')
        opis=request.POST.get('opis')
        tagovi=request.POST.get('tagovi')
        #Notice.objects.create(type=tip_pomoci, description=opis, idpublisher=request.user.id)
        print(naziv_oglasa)
        print(predmet)
        print(tip_pomoci)
        print(opis)
        print(tagovi)
    return render(request,'create-ad.html')
def dashboard_student(request):
    return render(request,'dashboard-student.html')

def search_ads(request):
    oglasi=Notice.objects.all()
    return render(request,'search-ads.html',{'oglasi':oglasi})

def view_ad(request,id):
    oglas=Notice.objects.get(pk=id)
    student=Student.objects.get(pk=oglas.idpublisher.iduser)
    jeTutor=None
    if len(Tutor.objects.filter(iduser_id=request.user.id))>0:
        jeTutor="DA"
    zahteviNeprihvaceni=Request.objects.filter(idnotice=id, isaccepted='P')
    aktivneKolaboracije=Collaboration.objects.filter(idnotice=id,dateend__isnull=True)

    tutoriNeprihvaceni=[]
    tutoriPrihvaceni=[]

    for zahtev in zahteviNeprihvaceni:
        tutoriNeprihvaceni.append(zahtev.idtutor)

    for zahtev in aktivneKolaboracije:
        tutoriPrihvaceni.append(zahtev.idtutor)

    return render(request,'view-ad.html',{'oglas':oglas,'studentIme':student.name, 'studentPrezime':student.surname, 'idVlasnika':student.iduser.iduser, 'jeTutor':jeTutor, 'tutoriPrihvaceni':tutoriPrihvaceni,'tutoriNeprihvaceni':tutoriNeprihvaceni})
def prekini_saradnju(request,id):
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        print(f"Prekini saradnju tutor_id={tutor_id}, oglas_id={id}")

        collab = Collaboration.objects.filter(idnotice_id=id,idtutor_id=tutor_id,dateend__isnull=True)[0]
        print(collab)
        collab.dateend = date.today()
        Collaboration.save(collab)

        #Request.objects.filter(idnotice_id=id,idtutor_id=tutor_id,isaccepted='A').update(isaccepted='R')
        #Mozemo da stavimo da bude rejected u requests ali mi to nema smisla pa cu ostaviti u komentaru

    return redirect('view_ad', id=id)

def prihvati_zahtev(request, id):
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        print(f"Prihvati zahtev tutor_id={tutor_id}, oglas_id={id}")

        zahtev = Request.objects.filter(idtutor_id=tutor_id,idnotice_id=id,isaccepted='P')[0]
        zahtev.isaccepted = 'A'
        zahtev.save()

        oglas = zahtev.idnotice
        student = oglas.idpublisher
        tutor = zahtev.idtutor

        Collaboration.objects.create(idnotice=oglas,idstudent=student,idtutor=tutor,datebegin=date.today())

    return redirect('view_ad', id=id)

def odbij_zahtev(request,id):
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        print(f"Odbij zahtev tutor_id={tutor_id}, oglas_id={id}")

        zahtev = Request.objects.filter(idtutor_id=tutor_id,idnotice_id=id,isaccepted='P')[0]
        zahtev.isaccepted = 'R'
        zahtev.save()
    return redirect('view_ad',id=id)