import base64

from django.shortcuts import render, redirect

from shared_app.models import Cv, Tutor, MyUser


# Create your views here.

def dashboard_tutor(request):
    return render(request, 'dashboard-tutor.html')

def create_cv(request):
    if request.method == 'POST':
        user = MyUser.objects.filter(username=request.user)
        tutor = Tutor.objects.filter(iduser=user.first().iduser)
        cv = Cv.objects.filter(idtutor=user.first().iduser)

        if cv:
            msg = "Vec ste kreirali CV"
            return render(request, 'create-cv.html', {'msg': msg})

        ime = request.POST['ime']
        prezime = request.POST['prezime']
        slika = request.FILES.get('slika')
        oMeni = request.POST['oMeni']
        edukacija = request.POST['edukacija']
        projekti = request.POST['projekti']
        iskustvo = request.POST['iskustvo']
        if slika:
            slika_data = base64.b64encode(slika.read()).decode('utf-8')
        else:
            slika_data = None

        Cv.objects.create(
            name=ime,
            surname=prezime,
            picture=slika_data,
            aboutme=oMeni,
            education=edukacija,
            projects=projekti,
            experience=iskustvo,
            idtutor=tutor.first()
        )

        return redirect('dashboard-tutor')

    return render(request, 'create-cv.html')

def edit_cv(request):
    user = MyUser.objects.filter(username=request.user)
    tutor = Tutor.objects.filter(iduser=user.first().iduser)
    cv = Cv.objects.filter(idtutor=user.first().iduser)

    context = {
        'name': "",
        'surname': "",
        'picture': None,
        'aboutme': "",
        'education': "",
        'projects': "",
        'experience': "",
        'msg': None
    }

    if cv:
        context['name'] = cv.first().name
        context['surname'] = cv.first().surname
        context['aboutme'] = cv.first().aboutme
        context['education'] = cv.first().education
        context['projects'] = cv.first().projects
        context['experience'] = cv.first().experience

        if isinstance(cv.first().picture, bytes):
            context['slika'] = cv.first().picture.decode('utf-8')  # pretvori bytes u string
        else:
            context['slika'] = cv.first().picture

    if request.method == 'POST':
        if cv is None:
            msg = "Nemate kreiran CV"
            context['msg'] = msg
            return render(request, 'create-cv.html', context)

        ime = request.POST['novoIme']
        prezime = request.POST['novoPrezime']
        slika = request.FILES.get('novaSlika')
        oMeni = request.POST['novoOMeni']
        edukacija = request.POST['novaEdukacija']
        projekti = request.POST['noviProjekti']
        iskustvo = request.POST['novoIskustvo']
        promeniSliku = request.POST.get('promeniSliku')

        noviCV = cv.first()
        noviCV.name = ime
        noviCV.surname = prezime
        noviCV.aboutme = oMeni
        noviCV.education = edukacija
        noviCV.projects = projekti
        noviCV.experience = iskustvo
        if slika:
            noviCV.picture = base64.b64encode(slika.read()).decode('utf-8')
            noviCV.save(update_fields=['name', 'surname', 'aboutme', 'education', 'projects', 'experience', 'picture'])
        elif promeniSliku:
            noviCV.picture = None
            noviCV.save(update_fields=['name', 'surname', 'aboutme', 'education', 'projects', 'experience', 'picture'])
        else:
            noviCV.save(update_fields=['name', 'surname', 'aboutme', 'education', 'projects', 'experience'])

        return render(request, 'dashboard-tutor.html')

    return render(request, 'edit-cv.html', context)

def download_cv(request):
    return render(request, 'dashboard-tutor.html', {'msg': "nemate cv"})
