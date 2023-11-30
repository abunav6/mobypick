from django.shortcuts import render, redirect
from mobypick_app.hidden import client_id

import boto3

class Book:
    def __init__(self, poster, author, title):
        self.poster = poster
        self.author = author
        self.title = title

def landing_page(request):
    return render(request, 'landing_page.html')

def select_books(request):
    genre_choices = ['fiction', 'mystery_thriller_crime', 'romance', 'non_fiction', 'history_biography', 'fantasy_paranormal', 'children', 'young_adult', 'comics_graphic', 'poetry']
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('book_data_1')
    top_books = {}

    for genre in genre_choices:
        response = table.scan(
            FilterExpression="contains(#genres, :genre)",
            ExpressionAttributeNames={
                "#genres": "genres",
            },
            ExpressionAttributeValues={
                ":genre": genre,
            }
        )


        items = response['Items']
        filtered_items = [item for item in items if 'ratings_count' in item and int(item['ratings_count']) >= 50000]

        sorted_items = sorted(filtered_items, key=lambda x: x['avg_rating'], reverse=True)
        top_books[genre] = sorted_items[:10]


    items = []
    for genre in top_books:
        print(f"\n\n\n{genre}")
        for book in top_books[genre]:
            print(book['title'])
            # items.append(Book(poster=book['image_url'],author=book['author_id'],title=book['title']))
    
    return render(request, 'select_books.html', {'items': items, 'genre_choices': ["/".join([a.capitalize() for a in k.split("_")]) for k in genre_choices]})

def cognito_login(request):
    # uri = "https%3A%2F%2Fmobypick.us-east-1.elasticbeanstalk.com%2Fselect_books"
    uri = "https%3A%2F%2Flocalhost%3A8000%2Fselect_books"
    return redirect(f"https://mobypick.auth.us-east-1.amazoncognito.com/login?client_id={client_id}&response_type=code&scope=email+openid+phone&redirect_uri={uri}")    
