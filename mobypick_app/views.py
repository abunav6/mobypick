from django.shortcuts import render, redirect
from mobypick_proj.settings import COGNITO_CLIENT_ID,COGNITO_CLIENT_SECRET,REDIRECT_URL, COGNITO_DOMAIN, BASE_URL, COGNITO_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY, DYNAMO_TABLE, REQUEST_REDIRECT_URL
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
    code = request.GET.get('code')
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
        "redirect_uri": REQUEST_REDIRECT_URL
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
    
    isNewUser = request.COOKIES.get('isNewUser')
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_TABLE)

    if isNewUser=="true":
        print("adding new user")
        want_to_read = []
        finished_reading = []
        language_pref = ''
        genre_pref = ''

        item = {
            'userID': userID,
            'email': email,
            'wantToRead': want_to_read,
            'finishedReading': finished_reading,
            'languagePref': language_pref,
            'genrePref': genre_pref
        }

        response = table.put_item(Item=item)

        print("PutItem :", response)

    else:
        response = table.scan(
            FilterExpression='userID = :user_id',
            ExpressionAttributeValues={':user_id': userID}
        )
        if 'Items' in response and len(response['Items'])>0:
            item = response['Items'][0]
            genre_pref = item.get('genrePref', '')
            language_pref = item.get('languagePref', '')

    user = { 
        'id': userID,
        'email': email,
        'language_preference': language_pref,
        'genre_pref':genre_pref
    }
    print(user)
    return render(request, 'loading.html', {'user': user})

def show_recommendations(request, context):
    return render(request, 'show_recommendations.html', context)


def profile(request):
    return render(request, 'profile.html')

def update_profile(request):
    updated_lang = request.POST['language_preference']
    updated_genre = request.POST['genre_preference']
    userID = request.COOKIES.get('userID')

    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_TABLE)

    response = table.update_item(
        Key={'userID': userID},
            UpdateExpression='SET languagePref = :lang, genrePref = :genre',
            ExpressionAttributeValues={':lang': updated_lang, ':genre': updated_genre},
            ReturnValues='UPDATED_NEW'
    )
    if 'Attributes' in response:
        #  TODO: add an alert to show that the update was successful
        print("updated")
    else:
        #  TODO: add an alert to show that the update failed
        print("failed")
    return render(request, 'profile.html')


def getLatestRecommendations(request):
    userID = request.COOKIES.get('userID')
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_TABLE)
    response = table.scan(
            FilterExpression='userID = :user_id',
            ExpressionAttributeValues={':user_id': userID}
    )
    if 'Items' in response and len(response['Items'])>0:
        item = response['Items'][0]
        genre_pref = item.get('genrePref', '')
        language_pref = item.get('languagePref', '')
        return show_recommendations(request, {'genre_pref':genre_pref,'language_preference':language_pref })
    

def put_books(request):
    userID = request.COOKIES.get('userID')
    wantoread = request.COOKIES.get('selectedBooks')
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_TABLE)

    response = table.update_item(
        Key={'userID': userID},
            UpdateExpression='SET wantToRead = :wantoread',
            ExpressionAttributeValues={':wantoread': wantoread},
            ReturnValues='UPDATED_NEW'
    )
    if 'Attributes' in response:
        #  TODO: add an alert to show that the update was successful
        print("updated")
    else:
        #  TODO: add an alert to show that the update failed
        print("failed")
    return render(request, "profile.html")