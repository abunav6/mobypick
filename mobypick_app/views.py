from django.shortcuts import render, redirect
from django.http import JsonResponse
from mobypick_proj.settings import COGNITO_CLIENT_ID,COGNITO_CLIENT_SECRET,REDIRECT_URL, COGNITO_DOMAIN, BASE_URL, COGNITO_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY, DYNAMO_USER_TABLE, REQUEST_REDIRECT_URL,PERSONALIZE_EVENT_TRACKER, RDS_HOST, RDS_USER, RDS_PWD, RDS_DB
import requests, base64
import boto3
import uuid
from datetime import datetime
import pymysql

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
    table = dynamodb.Table(DYNAMO_USER_TABLE)

    if isNewUser=="true":
        want_to_read = ''
        finished_reading = ''
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

def show_recommendations(request, context=None):
    return render(request, 'show_recommendations.html', context)


def profile(request):
    return render(request, 'profile.html')

def update_profile(request):
    updated_lang = request.POST['language_preference']
    updated_genre = request.POST['genre_preference']
    userID = request.COOKIES.get('userID')

    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_USER_TABLE)

    response = table.update_item(
        Key={'userID': userID},
            UpdateExpression='SET languagePref = :lang, genrePref = :genre',
            ExpressionAttributeValues={':lang': updated_lang, ':genre': updated_genre},
            ReturnValues='UPDATED_NEW'
    )
    if 'Attributes' in response:
        print("updated")
    else:
        print("failed")
    return render(request, 'profile.html')


def getLatestRecommendations(request):
    userID = request.COOKIES.get('userID')
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_USER_TABLE)
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
    table = dynamodb.Table(DYNAMO_USER_TABLE)
    print(wantoread)
    response = table.update_item(
        Key={'userID': userID},
            UpdateExpression='SET wantToRead = :wantoread',
            ExpressionAttributeValues={':wantoread': wantoread},
            ReturnValues='UPDATED_NEW'
    )
    if 'Attributes' in response:
        
        print("updated")
    else:
        
        print("failed")
    return render(request, "profile.html")


def fetch_books(request, book_type):
    print("need to fetch books")    
    userID = request.COOKIES.get('userID')
    print(userID)
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_USER_TABLE)
    response = table.scan(
            FilterExpression='userID = :user_id',
            ExpressionAttributeValues={':user_id': userID}
    )
    
    if 'Items' in response and len(response['Items'])>0:
        user = response['Items'][0]
        if book_type=="w":
            books = user['wantToRead']

        else:
            books = user['finishedReading']
        
        items = []
        if books:
            try:
                conn = pymysql.connect(host=RDS_HOST, user=RDS_USER, passwd=RDS_PWD, db=RDS_DB, connect_timeout=5)
            except pymysql.MySQLError as e:
                return JsonResponse({'error': e})
        
            if books.startswith(","):
                books = books[1:]

            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM Book WHERE ITEM_ID IN ({});".format(books))
                data = list(cur)
                item_count=0
                for row in data:
                    item_count += 1
                    items.append({
                        'id': row.get("ITEM_ID"),
                        'title': row.get("title"),
                        'author': row.get("name"),
                        'url': row.get("url"),
                        'image_url' : row.get("image_url")
                    })

        print(items)
        return JsonResponse({'books': items})

def update_book(request, book_type, book_id):
    userID = request.COOKIES.get('userID')
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_USER_TABLE)
    response = table.scan(
            FilterExpression='userID = :user_id',
            ExpressionAttributeValues={':user_id': userID}
    )
    print(response)
    if 'Items' in response and len(response['Items'])>0:
        user = response['Items'][0]
        if book_type=="w":
            field = 'wantToRead'
        else:
            field = 'finishedReading'
        
        string = user[field]
        string += f",{book_id}"
        print(string)
        
        response = table.update_item(
            Key={'userID': userID},
            UpdateExpression=f'SET {field} = :newvalue',
            ExpressionAttributeValues={':newvalue': string},
            ReturnValues='UPDATED_NEW'
        )
        print(response)
        if 'Attributes' in response:
            personalize_events = boto3.client(service_name='personalize-events')
            # telling Personalize that this event needs to be tracked for the user
            response = personalize_events.put_events(
                trackingId = PERSONALIZE_EVENT_TRACKER,
                userId= userID,
                sessionId = str(uuid.uuid4()),
                eventList = [{
                    'sentAt': datetime.now(),
                    'eventType': 'read',
                    'itemId': book_id
                    }]
            )
            print(response)

            return JsonResponse({"status" : "updated"})
        else:
            
            return JsonResponse({"status": "failed"})


def dislike_reco(request, book_id):
    userID = request.COOKIES.get('userID')
    personalize_events = boto3.client(service_name='personalize-events')
            # telling Personalize that this event needs to be tracked for the user
    response = personalize_events.put_events(
        trackingId = PERSONALIZE_EVENT_TRACKER,
        userId= userID,
        sessionId = str(uuid.uuid4()),
        eventList = [{
            'sentAt': datetime.now(),
            'eventType': 'read',
            'itemId': book_id
            }]
    )
    
    print(response)
    return JsonResponse({"status" : "Got it! We will not recommend books like this anymore!"})



def chat(request):
    return render(request, "chat.html")


def move_to_read(request, book_id):
    userID = request.COOKIES.get('userID')
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=COGNITO_REGION)
    table = dynamodb.Table(DYNAMO_USER_TABLE)
    response = table.scan(
            FilterExpression='userID = :user_id',
            ExpressionAttributeValues={':user_id': userID}
    )
    print(response)
    if 'Items' in response and len(response['Items'])>0:
        user = response['Items'][0]
        wtr = user['wantToRead']
        fr = user['finishedReading']
        print(wtr, fr)
        wtr = wtr.replace(f",{book_id}","")
        print(wtr)
        fr+=f",{book_id}"
        print(fr)
        response = table.update_item(
            Key={'userID': userID},
            UpdateExpression=f'SET wantToRead = :wtr, finishedReading = :fr',
            ExpressionAttributeValues={':wtr': wtr, ':fr' : fr},
            ReturnValues='UPDATED_NEW'
        )
        print(response)
        if 'Attributes' in response:
            personalize_events = boto3.client(service_name='personalize-events')
            response = personalize_events.put_events(
                trackingId = PERSONALIZE_EVENT_TRACKER,
                userId= userID,
                sessionId = str(uuid.uuid4()),
                eventList = [{
                    'sentAt': datetime.now(),
                    'eventType': 'read',
                    'itemId': book_id
                    }]
            )
            print(response)

            return JsonResponse({"status" : "updated"})
        else:
            
            return JsonResponse({"status": "failed"}) 

        
    
    return JsonResponse({"status": "ongoing"})