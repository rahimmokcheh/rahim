from django.test import TestCase
from Superviseur.models import *

# Create your tests here.
class TestSuperviseur (TestCase):
    # Setup exécutée avant chaque meth de test (des configurations)
    def setUp(self):
        self.superviseur1 = Superviseur.objects.create(
            name_superviseur="anwar",
            pseudo="anwarsf",
            gender="F",
            email="anwarsf@gmail.com",
            phone_number=52701121,
            description_superviseur="description"
        )
    # tester la création du supervideur
    def test_superviseur_creation(self):
        self.assertEqual(self.superviseur1.pseudo, "anwarsf")
        self.assertEqual(self.superviseur1.email, "anwarsf@gmail.com")
        self.assertEqual(self.superviseur1.gender, "F")
        self.assertEqual(self.superviseur1.phone_number, 52701121)
        self.assertEqual(str(self.superviseur1), self.superviseur1.pseudo)

    #tester le choix d'un genre invalide(n'est pas définie dans le modèle)
    # def test_gender_choices(self):
    #     with self.assertRaises(ValueError):
    #         superviseur_invalid_gender = Superviseur(
    #             name_superviseur="superviseur",
    #             pseudo="sup",
    #             gender="F",  # Invalide
    #             email="superviseur@gmail.com",
    #             phone_number = 23569874
    #         )
    #         superviseur_invalid_gender.full_clean()  # This will raise the ValueError
    # # tester l'unicité de l'email
    def test_email_unique(self):
        with self.assertRaises(Exception):
            superviseur_duplicate_email = Superviseur(
                name_superviseur="mohamed",
                pseudo="med",
                gender="M",
                email="med@gmail.com"  # Duplicate email
            )
            superviseur_duplicate_email.full_clean()  # This will raise an exception
    # tester l'unicité du pseudo
    def test_pseudo_unique(self):
        with self.assertRaises(Exception):
            superviseur_duplicate_pseudo = Superviseur(
                name_superviseur="anwar",
                pseudo="anwarsf",  # Duplicate pseudo
                gender="F",
                email="anwarsf@gmail.com"
            )
            superviseur_duplicate_pseudo.full_clean()  # This will raise an exception
    #  Vérifier que les champs optionnels peuvent être laissés vides et que le modèle fonctionne toujours correctement
    def test_optional_fields(self):
        superviseur_optional = Superviseur.objects.create(
            pseudo="anwarsf",
            email="anwarsf@gmail.com"
        )
        self.assertIsNone(superviseur_optional.name_superviseur) #vérifier que ces champs sont none
        self.assertIsNone(superviseur_optional.gender)
        self.assertIsNone(superviseur_optional.phone_number)
        self.assertIsNone(superviseur_optional.profile_picture.name, "")
        self.assertIsNone(superviseur_optional.description_superviseur)
    
# class TestClient(TestCase):
#     def setUp(self):
#        self.

# def test_client_creation():
#     Client = Client.objects.create(
#         name_client = 
#     )
