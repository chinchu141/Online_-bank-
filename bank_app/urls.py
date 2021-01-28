from django.urls import path,include
from . import views

urlpatterns=[
    
    path('home/', views.home, name='home'),
    
    path('login/', views.login, name='login'),
    
    path('more_info/', views.more_info, name='more_info'),
    path('registration/', views.registration, name='registration'),
    path('user_view/', views.user_view, name='user_view'),
    path('dashboard1/', views.dashboard1, name='dash1'),
    path('dashboard/', views.dashboard, name='dash'),
    path('t_1/', views.t, name='t'),
    path('contact/', views.contact, name='contact'),
    path('bill_pay/', views.bill_pay, name='bill'),
    path('book_gas/', views.book_gas, name='gas'),
    path('update/', views.update, name='update'),
    path('admin/', views.admin, name='admin'),
    path('admin_user/', views.admin_user, name='user_view'),
    path('history_tran/', views.history_tran, name='history_tran'),
    path('transaction/', views.transaction, name='transaction'),
    
]