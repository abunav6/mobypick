from django.shortcuts import render, redirect
from mobypick_app.hidden import client_id

def landing_page(request):
    return render(request, 'landing_page.html')

def select_books(request):    
    import json
    items = json.load(open("top10.json", "r"))
    return render(request, 'select_books.html', {'items':items})

def cognito_login(request):
    uri = "https%3A%2F%2Fmobypick.us-east-1.elasticbeanstalk.com%2Fshow_recommendations"
    # uri = "https%3A%2F%2Flocalhost%3A8000%2Fshow_recommendations"
    return redirect(f"https://mobypick.auth.us-east-1.amazoncognito.com/login?client_id={client_id}&response_type=code&scope=email+openid+phone&redirect_uri={uri}")    

def loading(request):
    return render(request, 'loading.html')

def show_recommendations(request):
    recommendations = [
        {"title": "Macbeth", "author": "William Shakespeare", "poster_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1459795224i/8852.jpg"},
        {"title": "Othello", "author": "William Shakespeare", "poster_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1459795105i/12996.jpg"},
        {"title": "Hamlet", "author": "William Shakespeare", "poster_url": "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1351051208i/1420.jpg"},
        # Add more books as needed
    ]

    context = {"recommendations": recommendations}
    return render(request, 'show_recommendations.html', context)
