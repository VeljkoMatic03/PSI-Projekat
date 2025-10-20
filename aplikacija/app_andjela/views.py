from django.shortcuts import render

# Create your views here.

def dashboard_tutor(request):
    return render(request, 'dashboard-tutor.html')
