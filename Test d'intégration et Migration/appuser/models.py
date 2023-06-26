from django.db import models

class Users(models.Model):
    nom = models.CharField(max_length=20, unique=False)
    pnom = models.CharField(max_length= 60, unique= False)
    nuser = models.CharField(max_length=15, unique= True)
    email= models.EmailField(max_length= 30, unique= True)
    password = models.CharField(max_length=30, unique= False)

class book(models.Model):
    Bookname = models.CharField(max_length=20, unique= True)
    Autbook = models.CharField (max_length=20 , unique= False)
    commentaire = models.TextField( max_length=300 , unique= False, default='')