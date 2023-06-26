from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from .models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


#page d'accueil
def index(request):
    return render(request, "appuser/index.html")

#page de connexion

def connection(request):
    if request.method == "POST":
        email = request.POST.get('email', None)  # Récupérer l'e-mail à partir des données POST
        password = request.POST.get('password', None)  # Récupérer le mot de passe à partir des données POST

        user = Users.objects.filter(email=email).first()  # Filtrer les utilisateurs avec l'e-mail fourni
        
        # Vérifier si l'utilisateur existe
        if user:
            auth_user = authenticate(username=user.nuser, password=password)  # Authentifier l'utilisateur avec le nom d'utilisateur et le mot de passe
            
            if auth_user:
                login(request, auth_user)  # Connecter l'utilisateur
                return redirect('dashboard')  # Redirection vers le tableau de bord
                
            else:
                print("Mot de passe incorrect", user.nuser)  # Afficher un message d'erreur si le mot de passe est incorrect
        
        else:
            print("User does not exist")  # Afficher un message d'erreur si l'utilisateur n'existe pas

    return render(request, 'appuser/connection.html')  # Rendre le template de connexion


class ModifierProfilIntegrationTest(TestCase):
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.profile = Users.objects.create(nuser='testuser', nom='Test User', email='test@example.com')

    def test_modifier_profil(self):
        # Se connecter en tant qu'utilisateur de test
        self.client.login(username='testuser', password='testpassword')

        # Effectuer une requête POST pour modifier le profil
        response = self.client.post(reverse('modifier_profil'), {'nom': 'Nouveau nom', 'email': 'nouveau@example.com', 'password': 'nouveaumotdepasse'})

        # Vérifier la redirection vers la page de modification du profil
        self.assertRedirects(response, reverse('modifier_profil'))

        # Recharger le profil depuis la base de données
        self.profile.refresh_from_db()

        # Vérifier que les modifications ont été enregistrées
        self.assertEqual(self.profile.nom, 'Nouveau nom')
        self.assertEqual(self.profile.email, 'nouveau@example.com')
        self.assertTrue(self.user.check_password('nouveaumotdepasse'))

    
# inscription d'un utilisateur
def inscription(request):
    message = ""  
    error = False
    
    if request.method == "POST":
        # Récupérer les données du formulaire
        name = request.POST.get('name', None)
        prenom = request.POST.get('surname', None)
        email = request.POST.get('email' , None)
        name_user = request.POST.get('username', None)
        password = request.POST.get('pass', None)
        
        # Vérifier si l'utilisateur existe déjà avec le même email ou nom d'utilisateur
        user = Users.objects.filter(Q(email = email) | Q(nuser = name_user)).first()
        if user:
            error = True
            message = f"Un utilisateur avec l'email {email} ou le nom d'utilisateur {name_user} existe déjà !"

        # Créer un nouvel utilisateur
        newUser = Users.objects.create(nom=name, pnom=prenom, nuser=name_user, email=email, password=password)
        newUser.save()

        if error == False:
            # Créer un objet User pour l'authentification Django
            user = User(
                username = name_user,
                email = email
            )
            user.save()
            user.password = password
            user.set_password(user.password)
            user.save()
        
        # Rediriger vers la page de connexion
        return redirect('connexion')

    # Préparer le contexte pour le rendu de la page d'inscription
    context = {
        "error": error,
        "message": message 
    }
    return render(request, "appuser/inscription.html", context)


@login_required
def dashboard(request):
    username = None
    
    # Vérifier si l'utilisateur est authentifié et récupérer le nom d'utilisateur
    if request.user.is_authenticated:
        username = request.user.get_username()

    if request.method == "POST":
        # Récupérer les données du formulaire soumis
        bookname = request.POST.get('book', None)
        auteur = request.POST.get('auteur', None)
        comment = request.POST.get('commentaire', None)
        
        # Créer un nouvel objet book avec les données du formulaire
        add = book.objects.create(Bookname=bookname, Autbook=auteur, commentaire=comment)
        add.save()
    
    # Récupérer tous les objets book existants
    form_list = book.objects.all()

    # Préparer le contexte pour le rendu de la page du tableau de bord
    context = {
        'username': username,
        'form_list': form_list
    } 

    return render(request, 'appuser/dashboard.html', context)


#test
class AppuserIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_inscription(self):
        # Création d'un utilisateur fictif pour le test
        user_data = {
            'name': 'John',
            'surname': 'Doe',
            'email': 'john.doe@example.com',
            'username': 'johndoe',
            'pass': 'password123'
        }

        # Envoi d'une requête POST à l'URL d'inscription
        response = self.client.post(reverse('inscription'), data=user_data)

        # Vérification de la redirection après l'inscription
        self.assertRedirects(response, reverse('connexion'))

        # Vérification de la création de l'utilisateur dans la base de données
        user_exists = Users.objects.filter(email=user_data['email'], nuser=user_data['username']).exists()
        self.assertTrue(user_exists)

        # Vérification de la création de l'utilisateur dans le système d'authentification Django
        django_user = User.objects.get(username=user_data['username'])
        self.assertEqual(django_user.email, user_data['email'])

    def test_dashboard(self):
        # Création d'un utilisateur fictif pour le test
        user = User.objects.create_user(username='johndoe', email='john.doe@example.com', password='password123')
        self.client.login(username='johndoe', password='password123')

        # Envoi d'une requête POST à l'URL du tableau de bord
        book_data = {
            'book': 'Book Title',
            'auteur': 'Author',
            'commentaire': 'Some comment'
        }
        response = self.client.post(reverse('dashboard'), data=book_data)

        # Vérification de la redirection après l'ajout du formulaire
        self.assertRedirects(response, reverse('dashboard'))

        # Vérification de la création du formulaire dans la base de données
        form_exists = book.objects.filter(Bookname=book_data['book'], Autbook=book_data['auteur'], commentaire=book_data['commentaire']).exists()
        self.assertTrue(form_exists)

        # Vérification de l'affichage du tableau de bord
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, book_data['book'])
        self.assertContains(response, book_data['auteur'])
        self.assertContains(response, book_data['commentaire'])

@login_required
def modifier_profil(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.get_username()

    user = Users.objects.filter(Q(nuser = username)).first()
    if request.method == 'POST':
        name = request.POST.get('nom', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        # Mettre à jour le nom et l'e-mail de l'utilisateur
        if name:
            user.nom = name
            user.save()
        user1 = User(
                email = email    
            )
        if email:
            user1.save()


        # Mettre à jour le mot de passe de l'utilisateur si un nouveau mot de passe est fourni
        if password:
            user.password = password
            user1.set_password(user.password)
            user.save()

    context = {
        'user': user,
        'username': username
    }
    return render(request, 'appuser/modify.html', context)

# Test

class ModifierProfilIntegrationTest(TestCase):
    def setUp(self):
        # Créer un utilisateur de test
        self.user = User.objects.create_user(username='testuser', password='testpassword')
    
    def test_modifier_profil(self):
        # Se connecter en tant qu'utilisateur de test
        self.client.login(username='testuser', password='testpassword')

        # Envoyer une requête POST pour modifier le profil
        data = {
            'nom': 'Nouveau Nom',
            'email': 'nouveau@email.com',
            'password': 'nouveaumotdepasse'
        }
        response = self.client.post(reverse('modifier_profil'), data)
        
        # Vérifier que la réponse est une redirection vers la page de modification réussie
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('modification_reussie'))
        
        # Récupérer l'utilisateur mis à jour depuis la base de données
        user = User.objects.get(username='testuser')
        
        # Vérifier que les informations du profil ont été mises à jour correctement
        self.assertEqual(user.first_name, 'Nouveau Nom')
        self.assertEqual(user.email, data['email'])
        
        # Vérifier que le mot de passe a été mis à jour correctement
        self.assertTrue(user.check_password(data['password']))

    def test_modifier_profil_non_connecte(self):
        # Se déconnecter de l'utilisateur
        self.client.logout()
        
        # Envoyer une requête GET pour accéder à la page de modification du profil
        response = self.client.get(reverse('modifier_profil'))
        
        # Vérifier que la réponse est une redirection vers la page de connexion
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('connexion'))



def log_out(request):
    logout(request)
    return redirect('connexion')

def delete_row(request, row_id):
    if request.method == 'POST':
        row = get_object_or_404(book, id=row_id)  # Assurez-vous d'utiliser le bon nom de modèle
        row.delete()
        return redirect('dashboard')