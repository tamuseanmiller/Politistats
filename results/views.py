from django.shortcuts import render
from django.http import HttpResponse

def results(request):
    if request.method == "POST":
        print("wewewewewewewe")
    return render(request, 'results.html', {})