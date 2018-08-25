#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Parametres
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Propertygrid
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Vignettes_documents
import wx.propgrid as wxpg
import copy
import GestionDB
from PIL import Image
import cStringIO

LISTE_MODELES = [
    # Arc-en-ciel
    {"label": _(u"Arc-en-ciel"), "fichier": "Modele_arcenciel.png", "description": _(u"Format paysage / Mensuel"), "donnees" :
        {'case_fond_alpha': 100, 'case_macaron_hauteur': 12, 'titre_fond_couleur': wx.Colour(0, 128, 192, 255), 'type': u'mensuel', 'case_macaron_largeur': 12, 'pied_hauteur': 15, 'titre_bord_couleur': wx.Colour(0, 128, 192, 255), 'page_fond_image': u'Menus/Arcenciel.jpg',
        'entete_mix_couleurs': True, 'pied_texte_couleur': wx.Colour(255, 255, 255, 255), 'case_macaron_mix_couleurs': True, 'case_macaron_type': u'rond', 'case_macaron_taille_police': 11, 'pied_taille_police': 8}
     },

    # Cuisine
    {"label": _(u"Cuisine"), "fichier": "Modele_cuisine.png", "description": _(u"Format paysage / Hebdomadaire"), "donnees":
        {'pied_fond_alpha': 40, 'case_fond_alpha': 80, 'entete_bord_couleur': wx.Colour(128, 128, 255, 255), 'titre_fond_couleur': wx.Colour(0, 128, 255, 255),
         'case_separateur_image': u'aucune', 'titre_bord_couleur': wx.Colour(0, 128, 255, 255), 'page_fond_image': u'Menus/Table_bois.jpg',
         'entete_fond_couleur': wx.Colour(128, 128, 255, 255), 'case_macaron_afficher': False, 'case_taille_police': 12}
     },

    # Noir métallique
    {"label": _(u"Noir métallique"), "fichier": "Modele_noirmetallique.png", "description": _(u"Format paysage / Mensuel"), "donnees":
        {'case_macaron_type': u'rond', 'case_macaron_largeur': 12, 'case_macaron_hauteur': 12, 'page_fond_image': u'Interface/Noir/Fond.jpg', 'pied_hauteur': 20,
         'type': u'mensuel', 'case_macaron_taille_police': 10}
     },

    # Noir métallique
    {"label": _(u"Ballons multicolores"), "fichier": "Modele_ballons.png", "description": _(u"Format paysage / Mensuel"), "donnees":
        {'pied_fond_alpha': 0, 'case_fond_alpha': 80, 'pied_bord_alpha': 0, 'entete_mix_couleurs': True, 'pied_hauteur': 12, 'page_fond_image': u'Menus/Ballons.jpg',
         'case_bord_couleur': wx.Colour(64, 0, 128, 255), 'pied_taille_police': 8, 'case_macaron_mix_couleurs': True, 'case_rotation_aleatoire': True, 'type': u'mensuel'}
     },

    # Tableau de craie
    {"label": _(u"Tableau de craie"), "fichier": "Modele_tableaucraie.png", "description": _(u"Format portrait / Journalier"), "donnees":
        {'case_separateur_type': u'image', 'case_fond_alpha': 0, 'pied_afficher': False, 'entete_afficher': False, 'page_marge_haut': 180, 'page_marge_bas': 100, 'page_format': u'portrait',
         'titre_afficher': False, 'case_bord_alpha': 0, 'page_fond_image': u'Menus/Tableau_craie.jpg','case_texte_couleur': wx.Colour(255, 255, 255, 255),
         'page_marge_droite': 100, 'page_marge_gauche': 100, 'type': u'quotidien', 'case_macaron_afficher': False, 'case_taille_police': 25}
     },

    # Girly
    {"label": _(u"Girly"), "fichier": "Modele_girly.png", "description": _(u"Format paysage / Hebdomadaire"), "donnees":
        {'case_separateur_type': u'ligne', 'titre_fond_couleur': wx.Colour(255, 128, 192, 255), 'entete_mix_couleurs': True,
         'case_titre_hauteur': 30, 'entete_afficher': False, 'page_fond_image': u'Menus/Abstrait.jpg', 'case_titre_taille_police': 11,
         'pied_texte_couleur': wx.Colour(255, 255, 255, 255), 'case_titre_afficher': True, 'case_titre_mix_couleurs': True, 'case_macaron_afficher': False,
         'case_taille_police': 14}
     },

    # Raclette
    {"label": _(u"Raclette"), "fichier": "Modele_hivernal.png", "description": _(u"Format paysage / Hebdomadaire"), "donnees":
        {'pied_fond_alpha': 0, 'case_separateur_type': u'image', 'case_fond_alpha': 80, 'entete_afficher': False, 'titre_fond_couleur': wx.Colour(255, 255, 255, 255),
         'case_titre_afficher': True, 'case_titre_fond_couleur': wx.Colour(128, 64, 0, 255), 'case_titre_hauteur': 25, 'pied_bord_alpha': 0,
         'page_fond_image': u'Badgeage/Theme_sommets.jpg', 'case_texte_couleur': wx.Colour(128, 64, 0, 255), 'case_titre_taille_police': 12, 'titre_hauteur': 70,
         'titre_texte_couleur': wx.Colour(128, 64, 0, 255), 'titre_bord_couleur': wx.Colour(255, 255, 255, 255), 'case_macaron_afficher': False, 'case_taille_police': 14}
     },

    # Cadeau de Noël
    {"label": _(u"Cadeau de Noël"), "fichier": "Modele_cadeaunoel.png", "description": _(u"Format paysage / Hebdomadaire"), "donnees":
        {'case_separateur_type': u'image', 'case_macaron_bord_couleur': wx.Colour(255, 0, 0, 255), 'case_fond_alpha': 70, 'entete_bord_couleur': wx.Colour(0, 128, 0, 255),
         'titre_fond_couleur': wx.Colour(0, 128, 0, 255), 'pied_hauteur': 20, 'pied_taille_police': 9, 'case_separateur_image': u'Ligne_branche.png',
         'titre_bord_couleur': wx.Colour(0, 128, 0, 255), 'page_fond_image': u'Badgeage/Theme_noel.jpg', 'pied_texte_couleur': wx.Colour(255, 255, 255, 255),
         'entete_fond_couleur': wx.Colour(0, 128, 0, 255), 'case_macaron_fond_couleur': wx.Colour(255, 0, 0, 255), 'case_taille_police': 15}
     },

    # Fond marin
    {"label": _(u"Fond marin"), "fichier": "Modele_fondmarin.png", "description": _(u"Format paysage / Mensuel"), "donnees":
        {'pied_hauteur': 20, 'type': u'mensuel'}
     },

    # Ardoise
    {"label": _(u"Ardoise"), "fichier": "Modele_ardoise.png", "description": _(u"Format portrait / Mensuel"), "donnees":
        {'pied_fond_alpha': 0, 'case_fond_alpha': 0, 'entete_afficher': False, 'titre_fond_couleur': wx.Colour(255, 255, 255, 255), 'type': u'mensuel', 'pied_hauteur': 20, 'page_format': u'portrait',
         'titre_bord_couleur': wx.Colour(255, 255, 255, 255), 'pied_bord_alpha': 0, 'page_fond_image': u'Badgeage/Theme_bleu.jpg', 'case_texte_couleur': wx.Colour(255, 255, 255, 255),
         'pied_texte_couleur': wx.Colour(255, 255, 255, 255), 'case_radius': 0, 'case_titre_afficher': True, 'titre_texte_couleur': wx.Colour(0, 0, 0, 255), 'case_rotation_aleatoire': True,
         'case_titre_mix_couleurs': True, 'case_macaron_afficher': False, 'pied_taille_police': 8}
     },

    # Olive
    {"label": _(u"Olive"), "fichier": "Modele_olive.png", "description": _(u"Format paysage / Mensuel"), "donnees":
        {'pied_fond_alpha': 0, 'entete_afficher': False, 'titre_fond_couleur': wx.Colour(128, 128, 0, 255), 'case_titre_afficher': True, 'case_titre_fond_couleur': wx.Colour(128, 128, 0, 255),
         'titre_bord_couleur': wx.Colour(128, 128, 0, 255), 'pied_bord_alpha': 0, 'page_fond_image': u'Badgeage/Theme_defaut.png', 'pied_texte_couleur': wx.Colour(255, 255, 255, 255),
         'pied_hauteur': 14, 'type': u'mensuel', 'case_macaron_afficher': False, 'pied_taille_police': 8}
     },

    # Plage d'été
    {"label": _(u"Plage d'été"), "fichier": "Modele_plageete.png", "description": _(u"Format paysage / Hebdomadaire"), "donnees":
        {'pied_fond_alpha': 0, 'case_separateur_type': u'image', 'entete_bord_couleur': wx.Colour(228, 190, 142, 255), 'titre_fond_couleur': wx.Colour(228, 190, 142, 255),
         'case_titre_fond_couleur': wx.Colour(228, 190, 142, 255), 'pied_taille_police': 8, 'case_separateur_image': u'Ligne_bijou.png', 'pied_bord_alpha': 0,
         'page_fond_image': u'Badgeage/Theme_ocean.jpg', 'pied_texte_couleur': wx.Colour(255, 255, 255, 255), 'entete_fond_couleur': wx.Colour(228, 190, 142, 255),
         'pied_hauteur': 20, 'titre_texte_couleur': wx.Colour(37, 176, 242, 255), 'titre_bord_couleur': wx.Colour(228, 190, 142, 255), 'case_macaron_afficher': False, 'case_taille_police': 15}
     },

    # Bulles de couleur
    {"label": _(u"Bulles de couleur"), "fichier": "Modele_bullescouleur.png", "description": _(u"Format paysage / Mensuel"), "donnees":
        {'pied_fond_alpha': 0, 'entete_afficher': False, 'titre_fond_couleur': wx.Colour(128, 128, 255, 255), 'type': u'mensuel', 'pied_hauteur': 20, 'titre_bord_couleur': wx.Colour(128, 128, 255, 255),
         'pied_bord_alpha': 0, 'page_fond_image': u'Badgeage/Theme_vert.jpg', 'pied_texte_couleur': wx.Colour(255, 255, 255, 255), 'case_radius': 30, 'case_titre_afficher': True,
         'case_rotation_aleatoire': True, 'case_titre_mix_couleurs': True, 'case_macaron_afficher': False, 'pied_taille_police': 8}
     },

    # Noir et blanc
    {"label": _(u"Noir et blanc"), "fichier": "Modele_noiretblanc.png", "description": _(u"Format portrait / Journalier"), "donnees":
        {'pied_fond_alpha': 40, 'case_separateur_type': u'image', 'case_fond_alpha': 0, 'entete_afficher': False, 'titre_fond_couleur': wx.Colour(255, 255, 255, 255),
         'page_format': u'portrait', 'case_bord_alpha': 0, 'case_separateur_image': u'Ligne_ronds.png', 'titre_bord_couleur': wx.Colour(255, 255, 255, 255),
         'page_fond_image': u'Interface/Noir/Fond.jpg', 'case_texte_couleur': wx.Colour(255, 255, 255, 255), 'titre_hauteur': 80, 'titre_taille_police': 35,
         'titre_texte_couleur': wx.Colour(0, 0, 0, 255), 'type': u'quotidien', 'case_macaron_afficher': False, 'case_taille_police': 30}
     },

    # Montagnes blanches
    {"label": _(u"Montagnes blanches"), "fichier": "Modele_montagneshiver.png", "description": _(u"Format paysage / Hebdomadaire"), "donnees":
        {'case_titre_texte_couleur': wx.Colour(0, 128, 255, 255), 'case_fond_alpha': 20, 'pied_afficher': False, 'entete_afficher': False, 'titre_fond_couleur': wx.Colour(255, 255, 255, 255),
         'case_titre_fond_couleur': wx.Colour(255, 255, 255, 255), 'page_marge_bas': 250, 'case_separateur_image': u'Ligne_moderne.png', 'case_titre_hauteur': 30,
         'titre_bord_couleur': wx.Colour(255, 255, 255, 255), 'page_fond_image': u'Badgeage/Theme_hiver.jpg', 'case_texte_couleur': wx.Colour(255, 255, 255, 255), 'case_titre_taille_police': 11,
         'pied_texte_couleur': wx.Colour(192, 192, 192, 255), 'case_titre_afficher': True, 'titre_texte_couleur': wx.Colour(0, 128, 255, 255), 'case_macaron_afficher': False}
     },


]



VALEURS_DEFAUT = {
    # Données
    "type" : "hebdomadaire",
    "jours_semaine" : [0, 1, 2, 3, 4],
    "pied_texte": u"Menus susceptibles de modifications",
    "categories_menus" : [0,],

    # Page
    "page_fond_image": "Interface/Bleu/Fond.jpg",
    "page_format": "paysage",
    "page_marge_gauche": 20,
    "page_marge_droite": 20,
    "page_marge_haut": 20,
    "page_marge_bas": 20,
    "page_espace_horizontal": 10,
    "page_espace_vertical": 10,
    "page_grille": False,

    # Entete
    "entete_afficher": True,
    "entete_fond_couleur": wx.Colour(254, 178, 0),
    "entete_fond_alpha": 1*100,
    "entete_bord_couleur": wx.Colour(254, 178, 0),
    "entete_bord_alpha": 1*100,
    "entete_texte_couleur": wx.WHITE,
    "entete_texte_alpha": 1*100,
    "entete_hauteur": 25,
    "entete_nom_police": "Helvetica-Bold", # Pas intégré dans le propertyGrid !
    "entete_taille_police": 15,
    "entete_radius": 5,
    "entete_mix_couleurs": False,

    # Case
    "case_hauteur": 0, # Pas intégré dans le propertyGrid !
    "case_radius": 5,
    "case_rotation_aleatoire": False,
    "case_bord_couleur": wx.WHITE,
    "case_bord_alpha": 0.6*100,
    "case_bord_alpha_vide": 0.2*100, # Pas intégré dans le propertyGrid !
    "case_fond_couleur": wx.WHITE,
    "case_fond_alpha": 0.6*100,
    "case_fond_alpha_vide": 0.2*100, # Pas intégré dans le propertyGrid !
    "case_repartition_verticale": True,
    "case_nom_police": "Helvetica", # Pas intégré dans le propertyGrid !
    "case_taille_police": 10,
    "case_texte_couleur": wx.BLACK,
    "case_marge_haut": 15,
    "case_espace_vertical": 5,
    "case_separateur_type": "aucun",
    "case_separateur_image": "Ligne_retro.png",

    # Case titre
    "case_titre_afficher": False,
    "case_titre_hauteur": 15,
    "case_titre_fond_couleur": wx.Colour(254, 178, 0),
    "case_titre_texte_couleur": wx.WHITE,
    "case_titre_mix_couleurs" : False,
    "case_titre_nom_police": "Helvetica-Bold", # Pas intégré dans le propertyGrid !
    "case_titre_taille_police": 8,

    # Macaron
    "case_macaron_afficher": True,
    "case_macaron_type": "carre",
    "case_macaron_radius": 5,
    "case_macaron_largeur": 25,
    "case_macaron_hauteur": 20,
    "case_macaron_bord_couleur": wx.Colour(254, 178, 0),
    "case_macaron_bord_alpha": 1*100,
    "case_macaron_fond_couleur": wx.Colour(254, 178, 0),
    "case_macaron_fond_alpha": 1*100,
    "case_macaron_nom_police": "Helvetica-Bold", # Pas intégré dans le propertyGrid !
    "case_macaron_taille_police": 13,
    "case_macaron_texte_couleur": wx.WHITE,
    "case_macaron_mix_couleurs" : False,

    # Titre de page
    "titre_afficher": True,
    "titre_hauteur": 50,
    "titre_bord_couleur": wx.Colour(254, 178, 0),
    "titre_fond_couleur": wx.Colour(254, 178, 0),
    "titre_nom_police": "Helvetica-Bold", # Pas intégré dans le propertyGrid !
    "titre_taille_police": 25,
    "titre_texte_couleur": wx.WHITE,
    "titre_texte" : u"",

    # Pied de page
    "pied_afficher": True,
    "pied_hauteur": 50,
    "pied_radius": 5,
    "pied_bord_couleur": wx.WHITE,
    "pied_bord_alpha": 0.2*100,
    "pied_fond_couleur": wx.WHITE,
    "pied_fond_alpha": 0.05*100,
    "pied_nom_police": "Helvetica", # Pas intégré dans le propertyGrid !
    "pied_taille_police": 10,
    "pied_texte_couleur": wx.BLACK,

}



class CTRL_Parametres(CTRL_Propertygrid.CTRL) :
    def __init__(self, parent, categorie=""):
        self.categorie = categorie
        CTRL_Propertygrid.CTRL.__init__(self, parent)

    
    def Remplissage(self):
        # Rubrique Données
        self.Append(wxpg.PropertyCategory(_(u"Données")))

        # Orientation page
        nom = "type"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Type d'affichage"), name=nom, liste_choix=[("mensuel", _(u"Mensuel")), ("hebdomadaire", _(u"Hebdomadaire")), ("quotidien", _(u"Journalier"))], valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez le type d'affichage de la page"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Jours de la semaine
        nom = "jours_semaine"
        liste_jours = [(0, _(u"Lundi")), (1, _(u"Mardi")), (2, _(u"Mercredi")), (3, _(u"Jeudi")), (4, _(u"Vendredi")), (5, _(u"Samedi")), (6, _(u"Dimanche"))]
        propriete = CTRL_Propertygrid.Propriete_multichoix(label=_(u"Jours de la semaine"), name=nom, liste_choix=liste_jours, liste_selections=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez les jours de la semaine à inclure. Cliquez sur le bouton à droite du champ de saisie pour accéder à la fenêtre de sélection."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Choix des catégories
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM menus_categories 
        ORDER BY ordre;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        liste_choix = [(0, _(u"Toutes")),]
        for IDcategorie, nom in listeDonnees:
            liste_choix.append((IDcategorie, nom))

        nom = "categories_menus"
        propriete = CTRL_Propertygrid.Propriete_multichoix(label=_(u"Catégories à afficher"), name=nom, liste_choix=liste_choix, liste_selections=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez les catégories de menus à afficher."))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Texte de titre de page
        nom = "titre_texte"
        propriete = wxpg.LongStringProperty(label=_(u"Texte de titre de page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte de titre de page"))
        self.Append(propriete)

        # Texte de pied de page
        nom = "pied_texte"
        propriete = wxpg.LongStringProperty(label=_(u"Texte de pied de page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez un texte de pied de page"))
        self.Append(propriete)

        # Rubrique page
        self.Append(wxpg.PropertyCategory(_(u"Page")))

        # Orientation page
        nom = "page_format"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Orientation de la page"), name=nom, liste_choix=[("portrait", _(u"Portrait")), ("paysage", _(u"Paysage"))], valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'orientation de la page"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # Image de fond de page
        nom = "page_fond_image"
        liste_images = [("aucune", _(u"Aucune")),
                        ("Menus/Table_bois.jpg", _(u"Cuisine")),
                        ("Menus/Abstrait.jpg", _(u"Abstrait")),
                        ("Menus/Arcenciel.jpg", _(u"Arc-en-ciel")),
                        ("Menus/Ballons.jpg", _(u"Ballons")),
                        ("Interface/Bleu/Fond.jpg", _(u"Fond marin")),
                        ("Menus/Tableau_craie.jpg", _(u"Tableau de craie")),
                        ("Interface/Noir/Fond.jpg", _(u"Noir métallique")),
                        ("Badgeage/Theme_vert.jpg", _(u"Vert pomme")),
                        ("Badgeage/Theme_sommets.jpg", _(u"Sommets enneigés")),
                        ("Badgeage/Theme_ocean.jpg", _(u"Plage d'été")),
                        ("Badgeage/Theme_noel.jpg", _(u"Cadeau de Noël")),
                        ("Badgeage/Theme_hiver.jpg", _(u"Hiver blanc")),
                        ("Badgeage/Theme_bleu.jpg", _(u"Bleu sombre")),
                        ("Badgeage/Theme_defaut.png", _(u"Marron chic")),
                        ]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Image de fond"), name=nom, liste_choix=liste_images, valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez une image de fond"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Marges et espaces
        temp = [
            ("page_marge_gauche", _(u"Marge gauche")),
            ("page_marge_droite", _(u"Marge droite")),
            ("page_marge_haut", _(u"Marge haut")),
            ("page_marge_bas", _(u"Marge bas")),
            ("page_espace_horizontal", _(u"Espace horizontal")),
            ("page_espace_vertical", _(u"Espace vertical")),
        ]
        for nom, label in temp:
            propriete = wxpg.IntProperty(label=label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)
            self.SetPropertyEditor(nom, "SpinCtrl")

        # Afficher grille
        nom = "page_grille"
        propriete = wxpg.BoolProperty(label=_(u"Afficher la grille"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"L'affichage de la grille peut faciliter votre travail de mise en page"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # Rubrique Titre de page
        self.Append(wxpg.PropertyCategory(_(u"Titre de page")))

        # Afficher titre
        nom = "titre_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher le titre de page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Afficher les macarons"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Hauteur
        nom = "titre_hauteur"
        propriete = wxpg.IntProperty(label=_(u"Hauteur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Fond et bord
        temp = [
            ("titre_fond", _(u"fond")),
            ("titre_bord", _(u"bord")),
        ]
        for code, label in temp:
            # Couleur
            nom = "%s_couleur" % code
            propriete = wxpg.ColourProperty(label=_(u"Couleur du %s") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Sélectionnez une couleur"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)

        # Couleur de texte
        nom = "titre_texte_couleur"
        propriete = wxpg.ColourProperty(label=_(u"Couleur du texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Taille de texte
        nom = "titre_taille_police"
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une taille de texte"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")


        # Rubrique Entete
        self.Append(wxpg.PropertyCategory(_(u"Entêtes")))

        # Afficher entêtes
        nom = "entete_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher les entêtes des dates"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Les entêtes affichent les dates"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Fond, bord et texte
        temp = [
            ("entete_fond", _(u"fond")),
            ("entete_bord", _(u"bord")),
            ("entete_texte", _(u"texte")),
        ]
        for code, label in temp:

            # Couleur
            nom = "%s_couleur" % code
            propriete = wxpg.ColourProperty(label=_(u"Couleur du %s") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Sélectionnez une couleur"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)

            # Transparence
            nom = "%s_alpha" % code
            propriete = wxpg.IntProperty(label=_(u"Opacité du %s (en %%)") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)
            self.SetPropertyEditor(nom, "SpinCtrl")
            propriete.SetAttribute("Min", 0)
            propriete.SetAttribute("Max", 100)

        # Afficher entêtes
        nom = "entete_mix_couleurs"
        propriete = wxpg.BoolProperty(label=_(u"Fond mix de couleurs"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Afficher un fond avec un mix de couleurs"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Hauteur de l'entete
        nom = "entete_hauteur"
        propriete = wxpg.IntProperty(label=_(u"Hauteur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Valeur de l'arrondi
        nom = "entete_radius"
        propriete = wxpg.IntProperty(label=_(u"Valeur de l'arrondi"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Taille de texte
        nom = "entete_taille_police"
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une taille de texte"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")


        # Rubrique Case titre
        self.Append(wxpg.PropertyCategory(_(u"Titre de case")))

        # Afficher titre de case
        nom = "case_titre_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher les titres de cases"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Afficher les titres de cases"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Hauteur
        nom = "case_titre_hauteur"
        propriete = wxpg.IntProperty(label=_(u"Hauteur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Couleur de fond
        nom = "case_titre_fond_couleur"
        propriete = wxpg.ColourProperty(label=_(u"Couleur du fond"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur de texte
        nom = "case_titre_texte_couleur"
        propriete = wxpg.ColourProperty(label=_(u"Couleur du texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Afficher entêtes
        nom = "case_titre_mix_couleurs"
        propriete = wxpg.BoolProperty(label=_(u"Fond mix de couleurs"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Afficher un fond avec un mix de couleurs"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Taille de texte
        nom = "case_titre_taille_police"
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une taille de texte"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")


        # Rubrique Macaron
        self.Append(wxpg.PropertyCategory(_(u"Macaron")))

        # Afficher macaron
        nom = "case_macaron_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher les macarons"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Afficher les macarons"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Type de macaron
        nom = "case_macaron_type"
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Type de macaron"), name=nom, liste_choix=[("carre", _(u"Carré")), ("rond", _(u"Rond"))], valeur=VALEURS_DEFAUT[nom])
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez le type de macaron"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Valeur de l'arrondi
        nom = "case_macaron_radius"
        propriete = wxpg.IntProperty(label=_(u"Valeur de l'arrondi"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Largeur
        nom = "case_macaron_largeur"
        propriete = wxpg.IntProperty(label=_(u"Largeur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Hauteur
        nom = "case_macaron_hauteur"
        propriete = wxpg.IntProperty(label=_(u"Hauteur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Fond et bord
        temp = [
            ("case_macaron_fond", _(u"fond")),
            ("case_macaron_bord", _(u"bord")),
        ]
        for code, label in temp:

            # Couleur
            nom = "%s_couleur" % code
            propriete = wxpg.ColourProperty(label=_(u"Couleur du %s") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Sélectionnez une couleur"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)

            # Transparence
            nom = "%s_alpha" % code
            propriete = wxpg.IntProperty(label=_(u"Opacité du %s (en %%)") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)
            self.SetPropertyEditor(nom, "SpinCtrl")
            propriete.SetAttribute("Min", 0)
            propriete.SetAttribute("Max", 100)

        # Afficher entêtes
        nom = "case_macaron_mix_couleurs"
        propriete = wxpg.BoolProperty(label=_(u"Fond mix de couleurs"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Afficher un fond avec un mix de couleurs"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Couleur de texte
        nom = "case_macaron_texte_couleur"
        propriete = wxpg.ColourProperty(label=_(u"Couleur du texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Taille de texte
        nom = "case_macaron_taille_police"
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une taille de texte"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")



        # Rubrique Case
        self.Append(wxpg.PropertyCategory(_(u"Case")))

        # Hauteur de la case
        nom = "case_hauteur"
        propriete = wxpg.IntProperty(label=_(u"Hauteur (0=automatique)"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique en pixels"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Valeur de l'arrondi
        nom = "case_radius"
        propriete = wxpg.IntProperty(label=_(u"Valeur de l'arrondi"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Rotation
        nom = "case_rotation_aleatoire"
        propriete = wxpg.BoolProperty(label=_(u"Rotation aléatoire"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Chaque case subit une légère rotation aléatoire"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Fond et bord
        temp = [
            ("case_fond", _(u"fond")),
            ("case_bord", _(u"bord")),
        ]
        for code, label in temp:

            # Couleur
            nom = "%s_couleur" % code
            propriete = wxpg.ColourProperty(label=_(u"Couleur du %s") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Sélectionnez une couleur"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)

            # Transparence
            nom = "%s_alpha" % code
            propriete = wxpg.IntProperty(label=_(u"Opacité du %s (en %%)") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)
            self.SetPropertyEditor(nom, "SpinCtrl")
            propriete.SetAttribute("Min", 0)
            propriete.SetAttribute("Max", 100)

        # Répartition verticale des texte
        nom = "case_repartition_verticale"
        propriete = wxpg.BoolProperty(label=_(u"Répartition verticale des textes"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Les lignes de texte sont répartis verticalement"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Taille de texte
        nom = "case_taille_police"
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une taille de texte"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Couleur de texte
        nom = "case_texte_couleur"
        propriete = wxpg.ColourProperty(label=_(u"Couleur du texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Marge haut
        nom = "case_marge_haut"
        propriete = wxpg.IntProperty(label=_(u"Marge supérieure"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Espace verticale
        nom = "case_espace_vertical"
        propriete = wxpg.IntProperty(label=_(u"Espace vertical"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Type de séparateur de ligne
        nom = "case_separateur_type"
        liste_choix = [("aucun", _(u"Aucun")), ("image", _(u"Image")), ("ligne", _(u"Ligne"))]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Séparateur de ligne"), name=nom, liste_choix=liste_choix, valeur=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez un type de séparateur de ligne"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Image du séparateur
        nom = "case_separateur_image"
        liste_choix = [("aucune", _(u"Aucune")),
                       ("Ligne_retro.png", _(u"Rétro")),
                       ("Ligne_bijou.png", _(u"Bijou")),
                       ("Ligne_branche.png", _(u"Branche")),
                       ("Ligne_fleurs.png", _(u"Fleurs")),
                       ("Ligne_moderne.png", _(u"Moderne")),
                       ("Ligne_ronds.png", _(u"Ronds")),
                       ]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Image du séparateur"), name=nom, liste_choix=liste_choix, valeur=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une image pour le séparateur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)



        # Rubrique Pied de page
        self.Append(wxpg.PropertyCategory(_(u"Pied de page")))

        # Afficher pied
        nom = "pied_afficher"
        propriete = wxpg.BoolProperty(label=_(u"Afficher le pied de page"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Afficher les macarons"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Hauteur
        nom = "pied_hauteur"
        propriete = wxpg.IntProperty(label=_(u"Hauteur"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Fond et bord
        temp = [
            ("pied_fond", _(u"fond")),
            ("pied_bord", _(u"bord")),
        ]
        for code, label in temp:

            # Couleur
            nom = "%s_couleur" % code
            propriete = wxpg.ColourProperty(label=_(u"Couleur du %s") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Sélectionnez une couleur"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)

            # Transparence
            nom = "%s_alpha" % code
            propriete = wxpg.IntProperty(label=_(u"Opacité du %s (en %%)") % label, name=nom, value=VALEURS_DEFAUT[nom])
            propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
            propriete.SetAttribute("obligatoire", True)
            self.Append(propriete)
            self.SetPropertyEditor(nom, "SpinCtrl")
            propriete.SetAttribute("Min", 0)
            propriete.SetAttribute("Max", 100)

        # Valeur de l'arrondi
        nom = "pied_radius"
        propriete = wxpg.IntProperty(label=_(u"Valeur de l'arrondi"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une valeur numérique"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")

        # Couleur de texte
        nom = "pied_texte_couleur"
        propriete = wxpg.ColourProperty(label=_(u"Couleur du texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Taille de texte
        nom = "pied_taille_police"
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name=nom, value=VALEURS_DEFAUT[nom])
        propriete.SetHelpString(_(u"Saisissez une taille de texte"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor(nom, "SpinCtrl")



    def Validation(self):
        """ Validation des données saisies """
        for nom, valeur in self.GetPropertyValues().iteritems() :
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True :
                if valeur == "" or valeur == None :
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % nom, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
        return True
        
    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        # Récupération des noms et valeurs par défaut du contrôle
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        # Recherche les paramètres mémorisés
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie=self.categorie, dictParametres=dictValeurs)
        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.iteritems() :
            propriete = self.GetPropertyByName(nom)
            ancienneValeur = propriete.GetValue() 
            propriete.SetValue(valeur)
    
    def Sauvegarde(self, forcer=False):
        """ Mémorisation des valeurs du contrôle """
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie=self.categorie, dictParametres=dictValeurs)
        
    def GetValeurs(self) :
        return self.GetPropertyValues()

    def SetValeurs(self, dictDonnees={}):
        for nom, valeur in dictDonnees.iteritems() :
            propriete = self.GetPropertyByName(nom)
            if propriete != None :
                propriete.SetValue(valeur)


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Track_modele(CTRL_Vignettes_documents.Track):
    def __init__(self, parent, buffer=None, type=None, label=None, description="", donnees={}):
        CTRL_Vignettes_documents.Track.__init__(self, parent, buffer=buffer, type=type, label=label)
        self.description = description
        self.donnees = donnees

    def GetInfobulle(self):
        texte = _(u"%s\n%s\n\nDouble-cliquez pour appliquer ce modèle") % (self.label.upper(), self.description)
        return texte




class CTRL_Modeles(CTRL_Vignettes_documents.CTRL):
    def __init__(self, parent):
        CTRL_Vignettes_documents.CTRL.__init__(self, parent, type_donnee=None, tailleVignette=256,style=wx.BORDER_SUNKEN, afficheLabels=True)
        self.parent = parent
        self.ImportationModeles()
        self.SetMinSize((330, -1))
        self.SetPopupMenu(None)

    def OnDoubleClick(self, event):
        index = self.GetSelection()
        dictDonnees = self.GetItem(index).track.donnees
        self.parent.SetModele(dictDonnees)

    def ChargeImage(self, fichier):
        """Read a file into PIL Image object. Return the image and file size"""
        buf = cStringIO.StringIO()
        f = open(fichier, "rb")
        while 1:
            rdbuf = f.read(8192)
            if not rdbuf: break
            buf.write(rdbuf)
        f.close()
        buf.seek(0)
        image = Image.open(buf).convert("RGB")
        return image, len(buf.getvalue())

    def ImportationModeles(self):
        for dictModele in LISTE_MODELES:
            cheminFichier = Chemins.GetStaticPath("Images/Menus/%s" % dictModele["fichier"])
            imgPIL, poidsImg = self.ChargeImage(cheminFichier)
            blob = self.GetBufferImage(imgPIL)

            # Conserve l'image en mémoire
            track = Track_modele(self, buffer=blob, type=dictModele["fichier"][-3:], label=dictModele["label"],
                                 description=dictModele["description"], donnees=dictModele["donnees"])
            self.listePages.append(track)

        # MAJ de l'affichage
        self.MAJ()


    # ----------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, periode=(None, None)):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période à afficher"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de période")))

        # Paramètres généraux
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options d'impression"))
        self.ctrl_parametres = CTRL_Parametres(self, categorie="impression_menu")
        self.ctrl_parametres.Importation()
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)
        self.ctrl_parametres.SetMinSize((50, 50)) 

        # Modèles
        self.box_modeles_staticbox = wx.StaticBox(self, -1, _(u"Modèles prédéfinis"))
        self.ctrl_modeles = CTRL_Modeles(self)

        self.__do_layout()

        # Init
        self.ctrl_date_debut.SetDate(periode[0])
        self.ctrl_date_fin.SetDate(periode[1])
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        grid_sizer_gauche = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)

        # Période de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=5, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_gauche.Add(staticbox_periode, 1, wx.RIGHT|wx.EXPAND, 0)

        # Paramètres généraux
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_parametres.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_reinitialisation, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_sauvegarde, 0, 0, 0)

        grid_sizer_parametres.Add(grid_sizer_boutons, 0, 0, 0)
        grid_sizer_parametres.AddGrowableRow(0)
        grid_sizer_parametres.AddGrowableCol(0)
        box_options.Add(grid_sizer_parametres, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_gauche.Add(box_options, 1, wx.EXPAND, 0)

        grid_sizer_gauche.AddGrowableRow(1)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)

        # Modèles
        box_modeles = wx.StaticBoxSizer(self.box_modeles_staticbox, wx.VERTICAL)
        box_modeles.Add(self.ctrl_modeles, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(box_modeles, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
            
    def MemoriserParametres(self):
        self.ctrl_parametres.Sauvegarde() 
            
    def GetOptions(self):
        dictOptions = copy.copy(VALEURS_DEFAUT)
        
        # Récupération des paramètres
        if self.ctrl_parametres.Validation() == False :
            return False
        for nom, valeur in self.ctrl_parametres.GetValeurs().iteritems()  :
            dictOptions[nom] = valeur

        # Récupération de la période
        date_debut = self.ctrl_date_debut.GetDate()
        if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None:
            dlg = wx.MessageDialog(self, _(u"La date de début de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        dictOptions["date_debut"] = date_debut

        date_fin = self.ctrl_date_fin.GetDate()
        if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None:
            dlg = wx.MessageDialog(self, _(u"La date de fin de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        dictOptions["date_fin"] = date_fin

        return dictOptions

    def SetModele(self, dictDonnees={}):
        self.ctrl_parametres.SetValeurs(VALEURS_DEFAUT)
        self.ctrl_parametres.SetValeurs(dictDonnees)




# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, periode=(None, None), IDrestaurateur=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        if IDrestaurateur == None :
            IDrestaurateur = 0
        self.IDrestaurateur = IDrestaurateur

        # Bandeau
        titre = _(u"Options d'impression")
        intro = _(u"Vous pouvez ici modifier les paramètres d'impression du document. Double-cliquez sur un modèle prédéfini, ajustez éventuellement les paramètres souhaités puis cliquez sur le bouton 'Mémoriser les paramètres' (Image disquette) pour mémoriser votre modèle pour les impressions suivantes.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")

        # Paramètres
        self.ctrl_parametres = CTRL(self, periode=periode)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        self.bouton_ok.SetFocus() 

    def __set_properties(self):
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((870, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_base.Add(self.ctrl_parametres, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        # Envoie les modification  dans le clipboard
        texte = unicode(self.GetProfilOptions())
        clipdata = wx.TextDataObject()
        clipdata.SetText(texte)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        # Aide
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def GetProfilOptions(self):
        dictModifications = {}
        dictDonnees = self.ctrl_parametres.GetOptions()
        for code, valeur in VALEURS_DEFAUT.iteritems() :
            if dictDonnees.has_key(code):
                if dictDonnees[code] != valeur :
                    dictModifications[code] = dictDonnees[code]
        return dictModifications

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)        
        
    def GetOptions(self):
        return self.ctrl_parametres.GetOptions() 

    def OnBoutonOk(self, event):
        # Récupération des options
        dictDonnees = self.ctrl_parametres.GetOptions()
        if dictDonnees == False :
            return

        # Complète le dictOptions
        dictDonnees["IDrestaurateur"] = self.IDrestaurateur

        # Affiche le PDF
        from Utils import UTILS_Impression_menu
        UTILS_Impression_menu.Impression(dictDonnees=dictDonnees)

        # Ferme la DLG
        #self.EndModal(wx.ID_OK)



if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
