from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home' ),
    path('upload/', views.upload_file, name='upload_file'),
    path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('delete/',views.deleteall_record,name='deleteall_record'),
    path('view-all-data/', views.view_all_data, name='view_all_data'),
]
