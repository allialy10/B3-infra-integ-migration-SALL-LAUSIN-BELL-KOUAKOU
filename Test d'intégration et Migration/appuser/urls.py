from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('connexion', views.connection, name= 'connexion'),
    path('inscription', views.inscription, name= 'inscription'),
    path('dashboard', views.dashboard, name= 'dashboard'),
    path('modifier_profil', views.modifier_profil, name= 'modify'),
    path('deconnexion', views.log_out, name= 'log_out'),
    path('delete/<int:row_id>/', views.delete_row, name='delete_row')
]