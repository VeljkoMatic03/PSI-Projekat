from datetime import date

from django.shortcuts import render, redirect

from shared_app.models import Notice, Student, Tutor, Request, Collaboration, Tag, MyUser


# Create your views here.
def create_ad(request):
    if request.method=="POST":
        naziv_oglasa=request.POST.get('naziv_oglasa')
        predmet=request.POST.get('predmet')
        tip_pomoci=request.POST.get('tip_pomoci')
        opis=request.POST.get('opis')
        tagovi=request.POST.get('tagovi')
        student=Student.objects.get(pk=request.user.id)
        Notice.objects.create(type=tip_pomoci, description=opis, idpublisher=student, title=naziv_oglasa, subject=predmet)
        tags=tagovi.split(',')
        for tag in tags:
            if (len(tag)==0):
                continue
            postoji=Tag.objects.filter(value=tag)
            if (len(postoji)==0):
                Tag.objects.create(value=tag)
        return redirect('dashboard-student')
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
    poslaoZahtev=None
    korisnik=MyUser.objects.filter(username=request.user.username)[0]

    tutor=Tutor.objects.filter(iduser=korisnik.iduser)[0]

    if len(Tutor.objects.filter(iduser=korisnik.iduser))>0:
        jeTutor="DA"

    if len(Request.objects.filter(idnotice=id,isaccepted='P',idtutor=tutor))>0:
        poslaoZahtev="DA"

    zahteviNeprihvaceni=Request.objects.filter(idnotice=id, isaccepted='P')
    aktivneKolaboracije=Collaboration.objects.filter(idnotice=id,dateend__isnull=True)

    tutoriNeprihvaceni=[]
    tutoriPrihvaceni=[]

    for zahtev in zahteviNeprihvaceni:
        tutoriNeprihvaceni.append(zahtev.idtutor)

    for zahtev in aktivneKolaboracije:
        tutoriPrihvaceni.append(zahtev.idtutor)

    return render(request,'view-ad.html',{'oglas':oglas,'studentIme':student.name, 'studentPrezime':student.surname, 'idVlasnika':student.iduser.iduser, 'jeTutor':jeTutor, 'tutoriPrihvaceni':tutoriPrihvaceni,'tutoriNeprihvaceni':tutoriNeprihvaceni, 'poslaoZahtev' : poslaoZahtev})
def prekini_saradnju(request,id):
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        print(f"Prekini saradnju tutor_id={tutor_id}, oglas_id={id}")

        collab = Collaboration.objects.filter(idnotice_id=id,idtutor_id=tutor_id,dateend__isnull=True)[0]
        print(collab)
        collab.dateend = date.today()
        Collaboration.save(collab)

        oglas=Notice.objects.get(pk=id)
        oglas.idtutor=None
        Notice.save(oglas)
        #Request.objects.filter(idnotice_id=id,idtutor_id=tutor_id,isaccepted='A').update(isaccepted='R')
        #Mozemo da stavimo da bude rejected u requests ali mi to nema smisla pa cu ostaviti u komentaru

    return redirect('view_ad', id=id)

def prihvati_zahtev(request, id):
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        print(f"Prihvati zahtev tutor_id={tutor_id}, oglas_id={id}")
        tutor=Tutor.objects.filter(iduser_id=tutor_id)[0]
        zahtev = Request.objects.filter(idtutor_id=tutor_id,idnotice_id=id,isaccepted='P')[0]
        zahtev.isaccepted = 'A'
        zahtev.save()

        oglas = zahtev.idnotice
        oglas.idtutor=tutor
        Notice.save(oglas)
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

def posalji_zahtev(request, id):
    if request.method == "POST":
        tutor_username = request.POST.get("tutor_username")

        korisnik = MyUser.objects.filter(username=tutor_username)[0]
        tutor=Tutor.objects.get(iduser=korisnik.iduser)

        notice = Notice.objects.get(idnotice=id)
        Request.objects.create(idnotice=notice,idtutor=tutor,isaccepted='P')

    return redirect('search_ads')