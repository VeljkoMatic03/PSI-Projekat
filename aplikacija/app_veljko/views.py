from django.shortcuts import render
from shared_app.models import MyUser, Verification, Tutor

# Create your views here.

def adminpanel(request):
    return render(request, 'dashboard-admin.html')

def verifyTutor(request):
    if request.method == 'POST':
        tutorid = request.POST.get('tutor_id')
        tutor = Tutor.objects.get(iduser=tutorid)
        if request.POST.get('action') == 'verify':
            tutor.isverified = 1
            tutor.save()
        elif request.POST.get('action') == 'reject':
            tutor.isverified = 0
            tutor.save()
        verificationInstance = Verification.objects.get(iduser=tutor)
        verificationInstance.delete()
    verifications = Verification.objects.all()
    tutors = []
    for verification in verifications:
        tutors.append(verification.iduser)
    return render(request, 'admin-verify-tutor.html', {'tutors': tutors})

def removeUser(request):
    user = None
    msgnf = None
    msg_user_deleted = None
    if request.method == 'POST':
        if "search" in request.POST:
            username = request.POST.get("username")
            try:
                user = MyUser.objects.get(username=username)
                if user.isbanned == 1 or user.isactive == 0:
                    user = None
                    msgnf = 'Nema korisnika sa tim korisnickim imenom'
            except MyUser.DoesNotExist:
                user = None
                msgnf = 'Nema korisnika sa tim korisnickim imenom'
        if "remove" in request.POST:
            id = request.POST.get("user_id")
            user = MyUser.objects.get(iduser=id)
            if user.isactive == 1 and user.isbanned == 0:
                user.isbanned = 1
                user.isactive = 0
                user.save()
            user = None
            msg_user_deleted = 'Uspesno obrisan korisnik'
    else:
        user = None
        msgnf = None
    return render(request, 'admin-remove-user.html', {'user': user, 'msgnf': msgnf, 'msg_user_deleted': msg_user_deleted})