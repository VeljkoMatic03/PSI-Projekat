from django.shortcuts import render, redirect
from shared_app.models import MyUser, Verification, Tutor, Admin, Student, Rating, Notice, Collaboration
from django.contrib.auth.models import User
from django.contrib.auth import logout

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
                isAdmin = Admin.objects.filter(iduser__username=user.username).exists()
                if user.isbanned == 1 or user.isactive == 0:
                    user = None
                    msgnf = 'Nema korisnika sa tim korisnickim imenom'
                if isAdmin:
                    user = None
                    msgnf = 'Admin se ne moze ukloniti'
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
            authUser = User.objects.get(username=user.username)
            authUser.delete()
            user = None
            msg_user_deleted = 'Uspesno obrisan korisnik'
    else:
        user = None
        msgnf = None
    return render(request, 'admin-remove-user.html', {'user': user, 'msgnf': msgnf, 'msg_user_deleted': msg_user_deleted})

def logout_user(request):
    logout(request)
    return redirect('homepage')

def public_profile(request):
    username = request.GET.get("username")
    user = None
    type = None
    myProfile = True
    if username:
        user = User.objects.filter(username=username)
        if not user.exists():
            return render(request, 'index.html')
        user = MyUser.objects.get(username=username)
        if Student.objects.filter(iduser=user).exists():
            type = 'Student'
            user = Student.objects.filter(iduser=user).first()
        elif Tutor.objects.filter(iduser=user).exists():
            type = 'Tutor'
            user = Tutor.objects.filter(iduser=user).first()
        elif Admin.objects.filter(iduser=user).exists():
            return render(request, 'index.html')
        if user.iduser.username == request.user.username:
            myProfile = True
        else:
            myProfile = False
    else:
        user = request.user
        if Student.objects.filter(iduser__username=user.username).exists():
            type='Student'
            user = Student.objects.filter(iduser__username=user.username).first()
        elif Tutor.objects.filter(iduser__username=user.username).exists():
            type='Tutor'
            user = Tutor.objects.filter(iduser__username=user.username).first()
        myProfile=True

    avgRating = 0
    isRated = False
    countRating = 0
    listOfRatings = Rating.objects.filter(idrateduser__username=user.iduser.username)
    if not listOfRatings.exists():
        isRated=False
    else:
        sumRating = 0
        countRating = 0
        for rating in listOfRatings:
            sumRating += rating.value
            countRating += 1
        avgRating = sumRating / countRating
        isRated = True

    listOfNotices = []
    if type == 'Student':
        listOfNoticesQ = Notice.objects.filter(idpublisher__iduser=user.iduser)
        if not listOfNoticesQ.exists():
            listOfNotices = None
        else:
            for notice in listOfNoticesQ:
                listOfNotices.append(notice)
    elif type == 'Tutor':
        listOfNoticesQ = Notice.objects.filter(idtutor__iduser=user.iduser)
        if not listOfNoticesQ.exists():
            listOfNotices = None
        else:
            for notice in listOfNoticesQ:
                listOfNotices.append(notice)
    comments = []
    for rating in Rating.objects.all():
        if rating.idrateduser.username == user.iduser.username:
            comments.append(rating)
    myType = None
    if Student.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Student'
    elif Tutor.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Tutor'
    elif Admin.objects.filter(iduser__username=request.user.username).exists():
        myType = 'Admin'
    return render(request, 'public-profile.html', {'user': user,
                                                   'type': type,
                                                   'myProfile': myProfile,
                                                   'isRated': isRated,
                                                   'avgRating': avgRating,
                                                   'countRating': countRating,
                                                   'notices': listOfNotices,
                                                   'myType': myType,
                                                   'comments': comments})
def home(request, tip):
    if tip == 'Student':
        return redirect('dashboard-student')
    if tip == 'Tutor':
        return redirect('dashboard-tutor')
    if tip == 'Admin':
        return redirect('adminpanel')
    return redirect('homepage')

def rate(request, id):
    user = MyUser.objects.get(username=request.user.username)
    tip = None
    if Student.objects.filter(iduser=user).exists():
        tip = 'Student'
    elif Tutor.objects.filter(iduser=user).exists():
        tip = 'Tutor'
    elif Admin.objects.filter(iduser=user).exists():
        tip = 'Admin'
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        rating = int(rating)
        notice = Notice.objects.get(idnotice=id)
        collaboration = Collaboration.objects.get(idnotice=notice)
        otherUser = None
        if collaboration.idstudent.iduser.username == request.user.username:
            otherUser = collaboration.idtutor.iduser
        else:
            otherUser = collaboration.idstudent.iduser
        newRating = Rating.objects.create(
            value=rating,
            comment=comment,
            idratinguser=MyUser.objects.get(username=request.user.username),
            idrateduser=otherUser,
            idcollaboration=collaboration
        )
        return redirect('home', tip)

    notice = Notice.objects.filter(idnotice=id)
    if not notice.exists():
        return redirect('home', tip)
    msgNotFinished = False
    tutor = None
    if notice.first().idtutor != None:
        tutor = notice.first().idtutor.iduser
    student = notice.first().idpublisher.iduser
    collaboration = Collaboration.objects.filter(idnotice=notice.first())
    if not collaboration.exists():
        msgNotFinished = True
    else:
        if collaboration.first().dateend == None:
            msgNotFinished = True
    msgNotAllowed = True
    if request.user.username == student.username:
        msgNotAllowed = False
    if tutor != None and request.user.username == tutor.username:
        msgNotAllowed = False
    msgRated = False
    ratings = Rating.objects.filter(idcollaboration=collaboration.first())
    for rating in ratings:
        if rating.idratinguser.username == request.user.username:
            msgRated = True
    return render(request, 'rate.html', {'notice': notice.first(), 'student': student,
                                         'tutor': tutor, 'notFinished': msgNotFinished,
                                         'myType': tip, 'notAllowed': msgNotAllowed,
                                         'rated': msgRated})