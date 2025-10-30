from django.urls import path
from . import views


urlpatterns = [
    path('', views.start_page, name='start_page'),
    path('diet-profile/', views.diet_profile, name='diet_profile'),
    path('check_food/', views.check_food, name='check_food'),
    # path('diet-plan/', views.diet_plan, name='diet_plan'),
    path('check_food/', views.check_food, name='check_food'),
    path('diet-form/', views.diet_form, name='diet_form'),

]