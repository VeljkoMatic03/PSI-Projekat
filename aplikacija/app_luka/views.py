import base64,json
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import render, redirect

from shared_app.models import Notice, Student, Tutor, Request, Collaboration, Tag, MyUser, Applied, Admin, Rating


# Create your views here.
@login_required
def create_ad(request):
    """
    Prikazuje stranicu za kreiranje :model:`shared_app.Notice`. |
    Template:
    :template:`create-ad.html`
    """
    if request.method=="POST":
        naziv_oglasa=request.POST.get('naziv_oglasa')
        predmet=request.POST.get('predmet')
        tip_pomoci=request.POST.get('tip_pomoci')
        opis=request.POST.get('opis')
        tagovi=request.POST.get('tagovi')
        attachment_file = request.FILES.get('attachment')

        attachment_data = None
        if attachment_file:
            encoded_content = base64.b64encode(attachment_file.read()).decode('utf-8')
            attachment_data = json.dumps({
                "filename": attachment_file.name,
                "content_type": attachment_file.content_type,
                "data": encoded_content
            })
        student=Student.objects.get(iduser__username=request.user.username)

        myNotice=Notice.objects.create(type=tip_pomoci, description=opis, idpublisher=student, title=naziv_oglasa, subject=predmet,attachment=attachment_data)

        tags=tagovi.split(',')
        for tag in tags:
            if (len(tag)==0):
                continue
            postoji=Tag.objects.filter(value=tag)
            if (len(postoji)==0):
                Tag.objects.create(value=tag)
            myTag=Tag.objects.filter(value=tag)[0]
            Applied.objects.create(idtag=myTag,idnotice=myNotice)

        return redirect('dashboard-student')
    return render(request,'create-ad.html')
@login_required
def dashboard_student(request):
    """
    Prikazuje dashboard za :model:`shared_app.Student`. |
    Template:
    :template:`dashboard-student.html`
    """
    return render(request,'dashboard-student.html')

@login_required
def search_ads(request):
    """
    Prikazuje stranicu za pretrazivanje :model:`shared_app.Notice`. |
    Template:
    :template:`search-ads.html`
    """
    oglasi=Notice.objects.all()
    finalOglasi=[]
    for oglas in oglasi:
        if len(Collaboration.objects.filter(idnotice=oglas))==0:
            finalOglasi.append(oglas)
            continue
        kolaboracija=Collaboration.objects.filter(idnotice=oglas)[0]
        if kolaboracija.dateend==None:
            finalOglasi.append(oglas)
    myType=None

    if Student.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Student'
    elif Tutor.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Tutor'
    elif Admin.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Admin'

    if request.method!="POST": return render(request,'search-ads.html',{'myType':myType,'oglasi':finalOglasi})

    nazivOglasa = request.POST.get("search", "").strip()
    tipOglasa = request.POST.getlist("tip")

    tags_input = request.POST.get("tag", "").strip()
    tags=[t.strip() for t in tags_input.split(",") if t.strip()]

    minRating = request.POST.get("min_rating", None)

    print(nazivOglasa)
    print(tags)
    print(tipOglasa)
    print(minRating)


    filteredOglasi = finalOglasi
    if len(nazivOglasa)>0:
        filteredOglasi = [o for o in filteredOglasi if nazivOglasa.lower() in (o.title or "").lower()]
    if len(tipOglasa)>0:
        filteredOglasi = [o for o in filteredOglasi if o.type in tipOglasa]
    if len(tags)>0:
        filteredOglasi = [
            o for o in filteredOglasi
            if o.applied_set.filter(idtag__value__in=tags).exists()
        ]
    if minRating:
        minRating = float(minRating)
        filteredOglasi = [
            o for o in filteredOglasi
            if (
                    Rating.objects.filter(idrateduser=o.idpublisher.iduser).aggregate(avg=Avg("value"))["avg"] is None
                    or
                    Rating.objects.filter(idrateduser=o.idpublisher.iduser).aggregate(avg=Avg("value"))["avg"] >= minRating
            )
        ]

    print(filteredOglasi)

    return render(request,'search-ads.html',{'myType':myType,'oglasi':filteredOglasi})

@login_required
def view_ad(request,id):
    """
    Prikazuje stranicu za detaljan prikaz :model:`shared_app.Notice` na osnovu id-a koji se prosledjuje view-u.|
    Template:
    :template:`view-ad.html`
    """
    oglas=Notice.objects.get(pk=id)
    student=Student.objects.get(iduser__username=oglas.idpublisher.iduser.username)
    jeTutor=None
    poslaoZahtev=None
    korisnik=MyUser.objects.filter(username=request.user.username)[0]

    tutor=None
    gotovaSaradnja=None

    saradnja=Collaboration.objects.filter(idnotice=id)

    if len(saradnja)>0 and saradnja[0].dateend!=None:
        gotovaSaradnja="DA"

    jaPomogao=None

    if len(Tutor.objects.filter(iduser=korisnik.iduser))>0:
        jeTutor="DA"
        tutor = Tutor.objects.filter(iduser=korisnik.iduser)[0]
        if len(Collaboration.objects.filter(idnotice=id,idtutor=tutor))>0:
            jaPomogao="DA"

    if len(Request.objects.filter(idnotice=id,isaccepted='P',idtutor=tutor))>0:
        poslaoZahtev="DA"

    myType=None
    if Student.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Student'
    elif Tutor.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Tutor'
    elif Admin.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Admin'

    zahteviNeprihvaceni=Request.objects.filter(idnotice=id, isaccepted='P')
    aktivneKolaboracije=Collaboration.objects.filter(idnotice=id,dateend__isnull=True)

    tutoriNeprihvaceni=[]
    tutoriPrihvaceni=[]

    for zahtev in zahteviNeprihvaceni:
        tutoriNeprihvaceni.append(zahtev.idtutor)

    for zahtev in aktivneKolaboracije:
        tutoriPrihvaceni.append(zahtev.idtutor)

    return render(request,'view-ad.html',{'myType':myType,'oglas':oglas,'studentIme':student.name, 'studentPrezime':student.surname, 'usernameVlasnika':student.iduser.username, 'jeTutor':jeTutor, 'tutoriPrihvaceni':tutoriPrihvaceni,'tutoriNeprihvaceni':tutoriNeprihvaceni, 'poslaoZahtev' : poslaoZahtev, 'gotovaSaradnja':gotovaSaradnja, 'jaPomogao':jaPomogao})
@login_required()
def prekini_saradnju(request,id):
    """
    Funckionalnost koja se koristi za prekidanje saradnje izmedju :model:`shared_app.Student` i :model:`shared_app.Tutor` na osnovu id-a oglasa
    """
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        print(f"Prekini saradnju tutor_id={tutor_id}, oglas_id={id}")

        collab = Collaboration.objects.filter(idnotice_id=id,idtutor_id=tutor_id,dateend__isnull=True)[0]
        print(collab)
        collab.dateend = date.today()
        Collaboration.save(collab)

        oglas=Notice.objects.get(pk=id)
        Notice.save(oglas)
        #Request.objects.filter(idnotice_id=id,idtutor_id=tutor_id,isaccepted='A').update(isaccepted='R')
        #Mozemo da stavimo da bude rejected u requests ali mi to nema smisla pa cu ostaviti u komentaru

    return redirect('view_ad', id=id)

@login_required()
def prihvati_zahtev(request, id):
    """
    Funckionalnost koja se koristi za pocetak saradnje izmedju :model:`shared_app.Student` i :model:`shared_app.Tutor` na osnovu id-a oglasa
    """
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

@login_required()
def odbij_zahtev(request,id):
    """
    Funckionalnost koja se koristi za odbijanje zahteva za saradnju izmedju :model:`shared_app.Student` i :model:`shared_app.Tutor` na osnovu id-a oglasa
    """
    if request.method == "POST":
        tutor_id = request.POST.get("tutor_id")
        print(f"Odbij zahtev tutor_id={tutor_id}, oglas_id={id}")

        zahtev = Request.objects.filter(idtutor_id=tutor_id,idnotice_id=id,isaccepted='P')[0]
        zahtev.isaccepted = 'R'
        zahtev.save()
    return redirect('view_ad',id=id)

@login_required()
def posalji_zahtev(request, id):
    """
    Funckionalnost koja se koristi za slanje zahteva za saradnju izmedju :model:`shared_app.Student` i :model:`shared_app.Tutor` na osnovu id-a oglasa
    """
    if request.method == "POST":
        tutor_username = request.POST.get("tutor_username")

        korisnik = MyUser.objects.filter(username=tutor_username)[0]
        tutor=Tutor.objects.get(iduser=korisnik.iduser)

        notice = Notice.objects.get(idnotice=id)
        Request.objects.create(idnotice=notice,idtutor=tutor,isaccepted='P')

    return redirect('search_ads')

@login_required()
def download_attachment(request, id):
    """
    Funckionalnost koja se koristi za preuzimanje priloga za odredjen :model:`shared_app.Notice` ukoliko taj oglas ima priloge.
    """
    notice = Notice.objects.get(idnotice=id)
    if not notice.attachment:
        return HttpResponse("Nema priloga za ovaj oglas.", status=404)

    try:
        attachment_info = json.loads(notice.attachment)
        file_data = base64.b64decode(attachment_info["data"])
        file_name = attachment_info.get("filename", "attachment.bin")
        file_type = attachment_info.get("content_type", "application/octet-stream")
    except Exception:
        return HttpResponse("Invalid attachment format.", status=400)

    response = HttpResponse(file_data, content_type=file_type)
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response