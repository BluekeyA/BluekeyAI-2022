from django.urls import path
# from django.http import HttpResponse
from . import views

urlpatterns = [
    # path('full/', views.full_name),
    # path('first/', views.first),
    # path('test_login/', views.test_post),
    # path('test_post_2/', views.test_post_2),
    path('reset_email/', views.reset_email),
    path('reset_otp/<str:email_pass>', views.reset_otp),
    path('reset_password/<str:email_pass>', views.reset_password)
]