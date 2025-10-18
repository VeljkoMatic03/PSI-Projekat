from django.shortcuts import render

from shared_app.models import Notice, Student, Tutor, Request


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
    print(Tutor.objects.filter(iduser_id=request.user.id))
    if len(Tutor.objects.filter(iduser_id=request.user.id))>0:
        jeTutor="DA"
    prijavljeniTutori=Request.objects.filter(idnotice=id, isaccepted=0)
    print(prijavljeniTutori)
    trenutneSaradnje=Request.objects.filter(idnotice=id, isaccepted=1)
    print(trenutneSaradnje)
    return render(request,'view-ad.html',{'oglas':oglas,'studentIme':student.name, 'studentPrezime':student.surname, 'idVlasnika':student.iduser.iduser, 'jeTutor':jeTutor})