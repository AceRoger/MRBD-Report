from django.shortcuts import render

# Create your views here.
def records_landing_page(request):
    return render(request, 'scheduleapp/approval.html')