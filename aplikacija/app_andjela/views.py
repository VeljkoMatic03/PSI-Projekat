from django.shortcuts import render

# Create your views here.

def dashboard_tutor(request):
    return render(request, 'dashboard-tutor.html')

def create_cv(request):
    return render(request, 'create-cv.html')

def edit_cv(request):
    return render(request, 'edit-cv.html')

def download_cv(request):
    return render(request, 'dashboard-tutor.html', {'msg': "nemate cv"})
