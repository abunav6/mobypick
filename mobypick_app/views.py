from django.shortcuts import render, redirect
from mobypick_app.hidden import client_id

class Book:
    def __init__(self, poster, author, title):
        self.poster = poster
        self.author = author
        self.title = title

def landing_page(request):
    return render(request, 'landing_page.html')

def select_books(request):
    # TODO: from the below 10 genres, get 10 books each, prompt user to select at most 10 books that appeals to them the most among these 100
    genre_choices = ['fiction', 'mystery_thriller_crime', 'romance', 'non_fiction', 'history_biography', 'fantasy_paranormal', 'children', 'young_adult', 'comics_graphic', 'poetry']


    items = [{'image':'https://m.media-amazon.com/images/I/511x4eT16mL._SY466_.jpg', 'author': 'Shakespeare','name':'OTHELLO'},
             {'image':'https://images-worker.bonanzastatic.com/afu/images/069e/8d8f/be88_6591207841/51vvyfgws_2bl._sl1500_.jpg', 'author': 'Herman Melville','name':'MOBY DICK'}]
    return render(request, 'select_books.html', {'items': items})

def cognito_login(request):
    uri = "https%3A%2F%2Fmobypick.us-east-1.elasticbeanstalk.com%2Fselect_books"
    return redirect(f"https://mobypick.auth.us-east-1.amazoncognito.com/login?client_id={client_id}&response_type=code&scope=email+openid+phone&redirect_uri={uri}")

