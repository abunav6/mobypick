from django.shortcuts import render, redirect
from mobypick_proj.settings import COGNITO_CLIENT_ID,COGNITO_CLIENT_SECRET,REDIRECT_URL, COGNITO_DOMAIN, BASE_URL

def landing_page(request):
    return render(request, 'landing_page.html')

def select_books(request):    
    import json
    items = json.load(open("top10.json", "r"))
    return render(request, 'select_books.html', {'items':items})

def cognito_login(request):
    return redirect(f"{COGNITO_DOMAIN}/login?client_id={COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+phone&redirect_uri={REDIRECT_URL}")    

def cognito_logout(request):
    return redirect(f"{COGNITO_DOMAIN}/logout?client_id={COGNITO_CLIENT_ID}&logout_uri={BASE_URL}")

def cognito_signup(request):
    return redirect(f"{COGNITO_DOMAIN}/signup?client_id={COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+phone&redirect_uri={REDIRECT_URL}")    


def loading(request):
    code = request.GET.get('code')
    # CODE TO GET USER INFO
    # import requests, base64
    # message = bytes(f"{COGNITO_CLIENT_ID}:{COGNITO_CLIENT_SECRET}",'utf-8')
    # secret_hash = base64.b64encode(message).decode()
    # url = "https://mobypick.auth.us-east-1.amazoncognito.com/oauth2/token"

    # headers = {
    #     "Authorization": f"Basic {secret_hash}",
    #     "Content-Type": "application/x-www-form-urlencoded",
    # }

    # data = {
    #     "code": code,
    #     "grant_type": "authorization_code",
    #     "redirect_uri": "https://localhost:8000/loading",
    # }   
    # response = requests.post(url, headers=headers, data=data)    
    # data = response.json()
    # print(data)
    return render(request, 'loading.html')

def show_recommendations(request):
    return render(request, 'show_recommendations.html')
