from django.shortcuts import render, redirect
from mobypick_proj.settings import COGNITO_CLIENT_ID,COGNITO_CLIENT_SECRET,REDIRECT_URL, COGNITO_DOMAIN, BASE_URL, COGNITO_REGION
import requests, base64
import boto3

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
    # TODO: push the user details into the new dynamoDB table
    code = request.GET.get('code')
    isNewUser = request.COOKIES.get('isNewUser')
    print(isNewUser)
    if isNewUser:
    
        message = bytes(f"{COGNITO_CLIENT_ID}:{COGNITO_CLIENT_SECRET}",'utf-8')
        secret_hash = base64.b64encode(message).decode()

        url = url = f"{COGNITO_DOMAIN}/oauth2/token"  
        headers = {
            "Authorization": f"Basic {secret_hash}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "code": f'{code}',
            "grant_type": "authorization_code",
            "scope":"email+openid+phone+aws.cognito.signin.user.admin",
            "redirect_uri": "https://localhost:8000/loading",
        } 

        response = requests.post(url, headers=headers, data=data)    
        data = response.json()

        url = f"{COGNITO_DOMAIN}/oauth2/userInfo"
        headers = {
            "Content-Type": "application/x-amz-json-1.1",
            "Authorization": f"Bearer {data['access_token']}",
        }

        response = requests.get(url, headers=headers)

        userInfo = response.json()
        email = userInfo['email']
        userID = userInfo['username']
        # TODO: push the userID and email to the DynamoDB table, push access token to cookies, and then redirect to loading page
    
    return render(request, 'loading.html')

def show_recommendations(request):
    return render(request, 'show_recommendations.html')
