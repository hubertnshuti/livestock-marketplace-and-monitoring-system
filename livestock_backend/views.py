from django.shortcuts import render

# def landing(request):
#     return render(request, "landing.html")

def home(request):
    return render(request, 'home.html')

def for_farmers(request):
    return render(request, 'for_farmers.html')

def for_buyers(request):
    return render(request, 'for_buyers.html')

def add_livestock(request):
    return render(request, 'add_livestock.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
