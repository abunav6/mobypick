from django.shortcuts import render, redirect
from mobypick_app.hidden import client_id

def landing_page(request):
    return render(request, 'landing_page.html')

def select_books(request):    
    import json
    items = json.load(open("top10.json", "r"))
    return render(request, 'select_books.html', {'items':items})

def cognito_login(request):
    uri = "https%3A%2F%2Fmobypick.us-east-1.elasticbeanstalk.com%2Fselect_books"
    # uri = "https%3A%2F%2Flocalhost%3A8000%2Fselect_books"
    return redirect(f"https://mobypick.auth.us-east-1.amazoncognito.com/login?client_id={client_id}&response_type=code&scope=email+openid+phone&redirect_uri={uri}")    
