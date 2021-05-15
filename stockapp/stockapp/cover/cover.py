from django.shortcuts import render

def index(request):
    title = '封面'
    return render(request, 'cover/index.html', locals())