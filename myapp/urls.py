from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('violations/', views.vehicles, name='violations'),
   # path('im/', views.upload_image1, name = 'im'),
    #path('result1/', views.result, name='result1'),
    path('extract_text/', views.extract_text, name='extract_text'),
    path('result2/', views.result2, name='result2'),
   # path('result/', views.result, name='result'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('info/', views.violation_info, name='info'),
    path('generate-pdf/<int:pk>', views.pdf, name = 'generate-pdf'),
    
    
    
    path('upload/', views.upload_image, name='upload_image'),
    #path('images/', views.image_list, name='images'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
