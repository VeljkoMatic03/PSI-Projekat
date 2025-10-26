import base64
from io import BytesIO

import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from shared_app.models import Cv, Tutor, MyUser, Student


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

def generate_cv(cv):
    name = cv.name
    surname = cv.surname
    aboutme = cv.aboutme
    education = cv.education
    projects = cv.projects
    experience = cv.experience
    picture = cv.picture

    img_reader = None
    if picture:
        if isinstance(picture, bytes):
            picture = picture.decode('utf-8')
        img_data = base64.b64decode(picture)
        img_reader = ImageReader(BytesIO(img_data))

    # Priprema PDF fajla
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=\"cv.pdf\"'

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Dizajn ---
    margin_left = 60
    start_y = height - 80

    # Boje
    title_color = colors.HexColor("#003366")
    label_color = colors.HexColor("#005599")
    text_color = colors.black

    # Naslov
    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(title_color)
    pdf.drawString(margin_left, start_y, "Curriculum Vitae")

    # Linija ispod naslova
    pdf.setStrokeColor(title_color)
    pdf.setLineWidth(2)
    pdf.line(margin_left, start_y - 10, width - margin_left, start_y - 10)

    y = start_y - 70

    # Sekcije
    sections = [
        ("Ime:", name),
        ("Prezime:", surname),
        ("O meni:", aboutme),
        ("Edukacija:", education),
        ("Projekti:", projects),
        ("Iskustvo:", experience),
    ]

    pdf.setFont("Helvetica", 12)
    for label, value in sections:
        # Labela
        pdf.setFont("Helvetica-Bold", 13)
        pdf.setFillColor(label_color)
        pdf.drawString(margin_left, y, label)

        # Sadržaj (uvođenje)
        pdf.setFont("Helvetica", 12)
        pdf.setFillColor(text_color)

        # Prelom teksta ako je duži
        text_obj = pdf.beginText(margin_left + 100, y)
        text_obj.setFont("Helvetica", 12)
        text_obj.setFillColor(text_color)
        max_width = width - margin_left - 120
        words = value.split(' ')
        line = ''
        count = 0
        for word in words:
            test_line = line + word + ' '
            if pdf.stringWidth(test_line, "Helvetica", 12) < max_width:
                line = test_line
            else:
                text_obj.textLine(line.strip())
                line = word + ' '
                count = count + 1
        text_obj.textLine(line.strip())
        pdf.drawText(text_obj)

        # Smanji Y za sledeću sekciju
        y -= 60
        if count > 1:
            y -= (count - 1) * 15
        if y < 100:
            pdf.showPage()
            y = height - 100

    # Slika ako postoji
    if img_reader:
        pdf.drawImage(img_reader, width - 180, height - 220, width=100, height=100, mask='auto')

    # Footer
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.setFillColor(colors.grey)
    pdf.drawRightString(width - margin_left, 40, "StudyBuddy")

    # Završetak
    pdf.showPage()
    pdf.save()

    pdf_data = buffer.getvalue()
    buffer.close()
    response.write(pdf_data)
    return response


def download_cv(request):
    user = MyUser.objects.filter(username=request.user)
    tutor = Tutor.objects.filter(iduser=user.first().iduser)
    cvs = Cv.objects.filter(idtutor=user.first().iduser)
    cv = cvs.first()

    if cvs is None or cv is None:
        return render(request, 'dashboard-tutor.html', {'msg': "nemate cv"})

    response = generate_cv(cv)
    return response

def download_tutors_cv(request, username):
    user = MyUser.objects.filter(username=username)
    tutor = Tutor.objects.filter(iduser=user.first().iduser)
    cvs = Cv.objects.filter(idtutor=user.first().iduser)
    cv = cvs.first()

    if cvs is None or cv is None:
        return redirect('profile', username=username)

    response = generate_cv(cv)
    return response
def wiki_search(request):
    query = request.GET.get("query", "")
    results = []
    searched = False

    if query:
        searched = query
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
        }
        headers = {
            "User-Agent": "StudyBuddyApp/1.0 (localhost development)"
        }

        response = requests.get(url, params=params, headers=headers)

        print(response.url)
        print(response.status_code)
        print(response.text[:500])

        if response.status_code == 200:
            data = response.json()
            results = data["query"]["search"]

    if Student.objects.filter(iduser__username=request.user.username).exists():
        return render(request, "dashboard-student.html", {"results": results, "searched": searched})
    elif Tutor.objects.filter(iduser__username=request.user.username).exists():
        return render(request, "dashboard-tutor.html", {"results": results, "searched": searched})
