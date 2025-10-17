from django.shortcuts import render

from shared_app.models import Student


# Create your views here.
def create_ad(request):
    if request.method=="POST":
        naziv_oglasa=request.POST.get('naziv_oglasa')
        predmet=request.POST.get('predmet')
        tip_pomoci=request.POST.get('tip_pomoci')
        opis=request.POST.get('opis')
        print(naziv_oglasa)
        print(predmet)
        print(tip_pomoci)
        print(opis)
    return render(request,'create-ad.html')
def dashboard_student(request):
    return render(request,'dashboard-student.html')