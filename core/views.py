from django.shortcuts import render

# Create your views here.
def no_permission(request):
    return render(request, 'no_permission.html')

def home(request):
    print("Home view called") 
    return render(request, 'home.html')