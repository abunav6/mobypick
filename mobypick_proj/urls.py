"""
URL configuration for mobypick_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mobypick_app.views import landing_page, select_books, cognito_login, loading, show_recommendations, cognito_logout, cognito_signup, profile, update_profile,getLatestRecommendations, put_books, fetch_books, update_book, dislike_reco, chat

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='landing_page'),
    path('cognito_login/', cognito_login, name='cognito_login'),
    path('cognito_logout/', cognito_logout, name='cognito_logout'),
    path('select_books/', select_books, name='select_books'),
    path('cognito_signup/', cognito_signup, name='cognito_signup'),
    path('loading/', loading, name='loading'),
    path('show_recommendations/', show_recommendations, name='show_recommendations'),
    path('profile/', profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
    path('getLatestRecommendations/', getLatestRecommendations, name='getLatestRecommendations'),
    path('put_books/', put_books, name='put_books'),
    path('fetch_books/<str:book_type>/', fetch_books, name='fetch_books'),
    path('update_book/<str:book_type>/<str:book_id>', update_book, name='update_book'),
    path('dislike_reco/<str:book_id>/', dislike_reco, name='dislike_reco'),
    path('chat/', chat, name='chat'),
]
