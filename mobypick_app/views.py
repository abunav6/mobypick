from django.shortcuts import render, redirect
from mobypick_proj.settings import COGNITO_CLIENT_ID,COGNITO_CLIENT_SECRET,REDIRECT_URL, COGNITO_DOMAIN, BASE_URL, COGNITO_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY, DYNAMO_TABLE
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
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)

        # Specify your DynamoDB table
        table = dynamodb.Table(DYNAMO_TABLE)

        # Replace these values with your actual data

        want_to_read = []
        finished_reading = []
        language_pref = 'en'
        genre_pref = ''

        # Construct item to be added to DynamoDB
        item = {
            'userID': userID,
            'email': email,
            'wantToRead': want_to_read,
            'finishedReading': finished_reading,
            'languagePref': language_pref,
            'genrePref': genre_pref
        }

        response = table.put_item(Item=item)

        print("PutItem succeeded:", response)

    
    return render(request, 'loading.html')

def show_recommendations(request):
    return render(request, 'show_recommendations.html')
