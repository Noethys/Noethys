#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
from Ctrl import CTRL_Profil
import FonctionsPerso
import sys
import operator
from Ctrl import CTRL_Photo
from Ctrl import CTRL_Bandeau
import GestionDB
from Utils import UTILS_Organisateur
from Utils import UTILS_Fichiers
from Utils import UTILS_Texte
from Utils import UTILS_Divers
from Utils import UTILS_Dates
from Data import DATA_Civilites as Civilites
from Ctrl import CTRL_Propertygrid
from Ctrl import CTRL_Selection_inscrits_presents
from Ol import OL_Impression_infos_medicales_colonnes
import wx.propgrid as wxpg
import copy

DICT_CIVILITES = Civilites.GetDictCivilites()


def GetSQLdates(listePeriodes=[]):
    texteSQL = ""
    for date_debut, date_fin in listePeriodes :
        texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
    if len(texteSQL) > 0 :
        texteSQL = "(" + texteSQL[:-4] + ")"
    else:
        texteSQL = "date=0"
    return texteSQL




class CTRL_profil_perso(CTRL_Profil.CTRL):
    def __init__(self, parent, categorie="", dlg=None):
        CTRL_Profil.CTRL.__init__(self, parent, categorie=categorie)
        self.dlg = dlg

    def Envoyer_parametres(self, dictParametres={}):
        """ Envoi des paramètres du profil sélectionné à la fenêtre """
        self.dlg.SetParametres(dictParametres)

    def Recevoir_parametres(self):
        """ Récupération des paramètres pour la sauvegarde du profil """
        dictParametres = self.dlg.GetParametres()
        self.Enregistrer(dictParametres)




class CTRL_Options(CTRL_Propertygrid.CTRL):
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)

    def Remplissage(self):

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Données")))

        # Afficher uniquement les individus avec infos
        propriete = wxpg.BoolProperty(label=_(u"Afficher uniquement individus avec infos"), name="individus_avec_infos", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher uniquement les individus avec infos"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Page")))

        # Orientation page
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Orientation de la page"), name="orientation", liste_choix=[("automatique", _(u"Automatique")), ("portrait", _(u"Portrait")), ("paysage", _(u"Paysage"))], valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'orientation de la page"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Lignes")))

        # Tri
        liste_choix = [("nom", _(u"Nom")), ("prenom", _(u"Prénom")), ("age", _(u"Âge"))]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Tri"), name="tri", liste_choix=liste_choix, valeur="nom")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez le tri"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Ordre
        liste_choix = [("croissant", _(u"Croissant")), ("decroissant", _(u"Décroissant"))]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Ordre"), name="ordre", liste_choix=liste_choix, valeur="croissant")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez l'ordre"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Afficher lignes vierges
        propriete = wxpg.IntProperty(label=_(u"Lignes vierges"), name="nbre_lignes_vierges", value=3)
        propriete.SetEditor("SpinCtrl")
        propriete.SetHelpString(_(u"Nombre de lignes vierges à afficher en fin de liste"))
        propriete.SetAttribute("obligatoire", True)
        propriete.SetAttribute("Min", 0)
        self.Append(propriete)

        # Insérer saut de page après groupe
        propriete = wxpg.BoolProperty(label=_(u"Insérer saut de page après groupe"), name="saut_page_groupe", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour insérer un saut de page après chaque groupe"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Couleur du fond d'entête de colonne
        propriete = wxpg.ColourProperty(label=_(u"Couleur ligne des entêtes"), name="couleur_fond_entetes", value=wx.Colour(208, 208, 208) )
        propriete.SetHelpString(_(u"Sélectionnez la couleur de fond de la ligne des entêtes"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Insérer texte d'introduction
        propriete = wxpg.BoolProperty(label=_(u"Insérer un texte d'introduction"), name="afficher_introduction", value=False)
        propriete.SetHelpString(_(u"Cochez cette case pour insérer un texte d'introduction"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonne Photo")))

        # Afficher les photos
        liste_choix = [("non", _(u"Non")), ("petite", _(u"Petite taille")), ("moyenne", _(u"Moyenne taille")), ("grande", _(u"Grande taille"))]
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Afficher les photos"), name="afficher_photos", liste_choix=liste_choix, valeur="non")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Afficher les photos individuelles"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonne Individu")))

        # Largeur colonne nom
        liste_choix = [("automatique", _(u"Automatique")),]
        for x in range(5, 305, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Largeur de la colonne"), name="largeur_colonne_nom", liste_choix=liste_choix, valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la largeur de la colonne Nom de l'individu (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Catégorie
        self.Append(wxpg.PropertyCategory(_(u"Colonne Âge")))

        # Afficher l'âge des individus
        propriete = wxpg.BoolProperty(label=_(u"Afficher la colonne"), name="afficher_age", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher de la colonne de l'âge des individus"))
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Largeur colonne âge
        liste_choix = [("automatique", _(u"Automatique")),]
        for x in range(5, 305, 5):
            liste_choix.append((str(x), "%d pixels" % x))
        propriete = CTRL_Propertygrid.Propriete_choix(label=_(u"Largeur de la colonne"), name="largeur_colonne_age", liste_choix=liste_choix, valeur="automatique")
        propriete.SetEditor("EditeurChoix")
        propriete.SetHelpString(_(u"Sélectionnez la largeur de la colonne Âge de l'individu (en pixels)"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

    def Validation(self):
        """ Validation des données saisies """
        # Vérifie que les données obligatoires ont été saisies
        for nom, valeur in self.GetPropertyValues().items():
            propriete = self.GetPropertyByName(nom)
            if self.GetPropertyAttribute(propriete, "obligatoire") == True:
                if valeur == "" or valeur == None:
                    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement renseigner le paramètre '%s' !") % self.GetPropertyLabel(nom), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        return True

    def Importation(self):
        """ Importation des valeurs dans le contrôle """
        return False

    def GetParametres(self):
        return copy.deepcopy(self.GetPropertyValues())

    def SetParametres(self, dictParametres={}):
        # Réinitialisation
        if dictParametres == None :
            self.Reinitialisation(afficher_dlg=False)
            return

        # Envoi des paramètres au Ctrl
        for nom, valeur in dictParametres.items():
            try :
                propriete = self.GetPropertyByName(nom)
                propriete.SetValue(valeur)
            except :
                pass




class Page_Generalites(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="informations_medicales", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_parametres = CTRL_Selection_inscrits_presents.CTRL(self)

        # Layout
        sizer_base = wx.BoxSizer()
        sizer_base.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_base)
        self.Layout()
        self.sizer_base = sizer_base

    def GetParametres(self):
        return self.ctrl_parametres.GetParametres()

    def SetParametres(self, dictParametres={}):
        if "mode" in dictParametres:
            self.ctrl_parametres.SetModePresents(dictParametres["mode"] == "presents")


class Page_Colonnes(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_colonnes = OL_Impression_infos_medicales_colonnes.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_colonnes.SetMinSize((150, 100))
        self.ctrl_colonnes.MAJ()

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_monter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_descendre = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Monter, self.bouton_monter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_colonnes.Descendre, self.bouton_descendre)

        # Propriétés
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une colonne")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier la colonne sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer la colonne sélectionnée dans la liste")))
        self.bouton_monter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour monter la colonne sélectionnée dans la liste")))
        self.bouton_descendre.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour descendre la colonne sélectionnée dans la liste")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_colonnes, 1, wx.EXPAND, 0)

        grid_sizer_droit = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_monter, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_descendre, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def GetParametres(self):
        return {"colonnes" : self.ctrl_colonnes.GetParametres()}

    def SetParametres(self, dictParametres={}):
        if "colonnes" in dictParametres:
            self.ctrl_colonnes.SetParametres(dictParametres["colonnes"])


class Page_Options(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.ctrl_options = CTRL_Options(self)
        self.ctrl_options.SetMinSize((100, 50))

        self.bouton_reinit = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Actualiser.png"), wx.BITMAP_TYPE_ANY))

        # Binds
        self.Bind(wx.EVT_BUTTON, self.Reinitialisation, self.bouton_reinit)

        # Propriétés
        self.bouton_reinit.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour réinitialiser les options")))

        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)

        grid_sizer_base.Add(self.ctrl_options, 1, wx.EXPAND, 0)

        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_reinit, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        sizer_base.Add(grid_sizer_base, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer_base)
        self.Layout()

    def Reinitialisation(self, event=None):
        self.ctrl_options.Reinitialisation()

    def GetParametres(self):
        return self.ctrl_options.GetParametres()

    def SetParametres(self, dictParametres={}):
        self.ctrl_options.SetParametres(dictParametres)




# ----------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Parametres(wx.Notebook):
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=-1, style=wx.BK_DEFAULT | wx.NB_MULTILINE)
        self.dictPages = {}

        self.listePages = [
            {"code": "generalites", "ctrl": Page_Generalites(self), "label": _(u"Paramètres"), "image": "Calendrier.png"},
            {"code": "colonnes", "ctrl": Page_Colonnes(self), "label": _(u"Colonnes"), "image": "Tableau_colonne.png"},
            {"code": "options", "ctrl": Page_Options(self), "label": _(u"Options"), "image": "Options.png"},
        ]

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        self.dictImages = {}
        for dictPage in self.listePages:
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/%s" % dictPage["image"]), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Création des pages
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages:
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = dictPage["ctrl"]
            index += 1

    def GetPageAvecCode(self, codePage=""):
        return self.dictPages[codePage]

    def AffichePage(self, codePage=""):
        index = 0
        for dictPage in self.listePages:
            if dictPage["code"] == codePage:
                self.SetSelection(index)
            index += 1

    def GetParametres(self):
        dictParametres = {}
        for dictPage in self.listePages:
            dictParametres.update(dictPage["ctrl"].GetParametres())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        for dictPage in self.listePages:
            dictPage["ctrl"].SetParametres(dictParametres)


# ----------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Impression_infos_medicales", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici imprimer une liste au format PDF des informations médicales des individus présents sur la période de votre choix. Pour une liste standard, sélectionnez simplement une période puis cliquez sur 'Aperçu'.")
        titre = _(u"Impression de la liste des informations médicales")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")

        # Profil de configuration
        self.staticbox_profil_staticbox = wx.StaticBox(self, -1, _(u"Profil de configuration"))
        self.ctrl_profil = CTRL_profil_perso(self, categorie="impression_infos_medicales", dlg=self)

        # Notebook
        self.ctrl_notebook = CTRL_Parametres(self)

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init Contrôles
        self.ctrl_profil.SetOnDefaut()
        self.bouton_ok.SetFocus()


    def __set_properties(self):
        self.SetTitle(_(u"Impression de la liste des informations médicales"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((650, 650))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Profil
        staticbox_profil = wx.StaticBoxSizer(self.staticbox_profil_staticbox, wx.VERTICAL)
        staticbox_profil.Add(self.ctrl_profil, 1, wx.EXPAND | wx.ALL, 5)
        grid_sizer_base.Add(staticbox_profil, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        grid_sizer_base.Add(self.ctrl_notebook, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedesinformationsmdicales")

    def GetAge(self, date_naiss=None):
        if date_naiss == None : return None
        datedujour = datetime.date.today()
        age = (datedujour.year - date_naiss.year) - int((datedujour.month, datedujour.day) < (date_naiss.month, date_naiss.day))
        return age

    def GetPage(self, code=""):
        """ Retourne le ctrl page du notebook selon le code page """
        return self.ctrl_notebook.GetPageAvecCode(code)

    def GetParametres(self):
        """ Récupération des paramètres """
        return self.ctrl_notebook.GetParametres()

    def SetParametres(self, dictParametres={}):
        """ Importation des paramètres """
        if dictParametres != None :
            self.ctrl_notebook.SetParametres(dictParametres)

    def OnBoutonOk(self, event):
        dictParametres = self.ctrl_notebook.GetParametres()

        # Récupération et vérification des données
        listeActivites = dictParametres["liste_activites"]
        if len(listeActivites) == 0 :
            self.ctrl_notebook.AffichePage("generalites")
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Récupération et vérification des données
        listeGroupes = dictParametres["liste_groupes"]
        if len(dictParametres["liste_groupes"]) == 0 :
            self.ctrl_notebook.AffichePage("generalites")
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un groupe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Vérification qu'il y a des colonnes
        if not dictParametres["colonnes"]:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement créer au moins une colonne !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Recherche les catégories utilisées
        liste_categories_utilisees = []
        for nom_categorie, categories in dictParametres["colonnes"]:
            for IDcategorie in UTILS_Texte.ConvertStrToListe(categories):
                if IDcategorie not in liste_categories_utilisees :
                    liste_categories_utilisees.append(IDcategorie)

        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        
        self.taille_page = A4
        if dictParametres["orientation"] == "portrait" :
            self.hauteur_page = self.taille_page[1]
            self.largeur_page = self.taille_page[0]
        else:
            self.hauteur_page = self.taille_page[0]
            self.largeur_page = self.taille_page[1]
        
        # Création des conditions pour les requêtes SQL
        conditionsPeriodes = GetSQLdates(dictParametres["liste_periodes"])
        
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        if len(listeGroupes) == 0 : conditionGroupes = "()"
        elif len(listeGroupes) == 1 : conditionGroupes = "(%d)" % listeGroupes[0]
        else : conditionGroupes = str(tuple(listeGroupes))
                
        # Récupération des noms des groupes
        dictGroupes = dictParametres["dict_groupes"]
        dictActivites = dictParametres["dict_activites"]

        DB = GestionDB.DB()

        texte_introduction = []

        # ------------ MODE PRESENTS ---------------------------------

        if dictParametres["mode"] == "presents" :

            # Récupération de la liste des groupes ouverts sur cette période
            req = """SELECT IDouverture, IDactivite, IDunite, IDgroupe
            FROM ouvertures 
            WHERE ouvertures.IDactivite IN %s AND %s
            AND IDgroupe IN %s
            ; """ % (conditionActivites, conditionsPeriodes, conditionGroupes)
            DB.ExecuterReq(req)
            listeOuvertures = DB.ResultatReq()
            dictOuvertures = {}
            for IDouverture, IDactivite, IDunite, IDgroupe in listeOuvertures :
                if (IDactivite in dictOuvertures) == False :
                    dictOuvertures[IDactivite] = []
                if IDgroupe not in dictOuvertures[IDactivite] :
                    dictOuvertures[IDactivite].append(IDgroupe)

            # Récupération des individus grâce à leurs consommations
            req = """SELECT individus.IDindividu, IDactivite, IDgroupe,
            IDcivilite, nom, prenom, date_naiss
            FROM consommations 
            LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
            WHERE consommations.etat IN ("reservation", "present")
            AND IDactivite IN %s AND %s
            GROUP BY individus.IDindividu, IDactivite, IDgroupe
            ORDER BY nom, prenom
            ;""" % (conditionActivites, conditionsPeriodes)
            DB.ExecuterReq(req)
            listeIndividus = DB.ResultatReq()

            # Création du texte d'introduction
            liste_dates = []
            for date_debut, date_fin in dictParametres["liste_periodes"]:
                liste_dates.append(date_debut)
                liste_dates.append(date_fin)
            texte_introduction.append(u"Individus présents sur la période du %s au %s" % (UTILS_Dates.DateDDEnFr(min(liste_dates)), UTILS_Dates.DateDDEnFr(max(liste_dates))))


        # ------------ MODE INSCRITS ---------------------------------

        if dictParametres["mode"] == "inscrits" :

            dictOuvertures = {}
            for IDgroupe, dictGroupe in dictGroupes.items() :
                IDactivite = dictGroupe["IDactivite"]
                if (IDactivite in dictOuvertures) == False :
                    dictOuvertures[IDactivite] = []
                if IDgroupe not in dictOuvertures[IDactivite] :
                    dictOuvertures[IDactivite].append(IDgroupe)

            # Récupération des individus grâce à leurs consommations
            req = """SELECT individus.IDindividu, IDactivite, IDgroupe,
            IDcivilite, nom, prenom, date_naiss
            FROM individus 
            LEFT JOIN inscriptions ON inscriptions.IDindividu = individus.IDindividu
            WHERE inscriptions.statut='ok' AND IDactivite IN %s
            GROUP BY individus.IDindividu, IDactivite, IDgroupe
            ORDER BY nom, prenom
            ;""" % conditionActivites
            DB.ExecuterReq(req)
            listeIndividus = DB.ResultatReq()


        # Analyse des individus
        dictIndividus = {}
        listeIDindividus = []
        for IDindividu, IDactivite, IDgroupe, IDcivilite, nom, prenom, date_naiss in listeIndividus:
            if date_naiss != None: date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
            age = self.GetAge(date_naiss)

            # Mémorisation de l'individu
            dictIndividus[IDindividu] = {
                "IDcivilite": IDcivilite, "nom": nom, "prenom": prenom,
                "age": age, "date_naiss": date_naiss, "IDgroupe": IDgroupe, "IDactivite": IDactivite,
            }

            # Mémorisation du IDindividu
            if IDindividu not in listeIDindividus:
                listeIDindividus.append(IDindividu)


        # Dict Informations médicales
        req = """SELECT IDprobleme, IDindividu, IDtype, intitule, date_debut, date_fin, description, traitement_medical,
        description_traitement, date_debut_traitement, date_fin_traitement, eviction, date_debut_eviction, date_fin_eviction
        FROM problemes_sante 
        WHERE diffusion_listing_enfants=1
        ;"""
        DB.ExecuterReq(req)
        listeInformations = DB.ResultatReq()
        DB.Close()
        dictInfosMedicales = {}
        for IDprobleme, IDindividu, IDtype, intitule, date_debut, date_fin, description, traitement_medical, description_traitement, date_debut_traitement, date_fin_traitement, eviction, date_debut_eviction, date_fin_eviction in listeInformations :
            if (IDindividu in dictInfosMedicales) == False :
                dictInfosMedicales[IDindividu] = []
            dictTemp = {
                "IDprobleme" : IDprobleme, "IDcategorie" : IDtype, "intitule" : intitule, "date_debut" : date_debut,
                "date_fin" : date_fin, "description" : description, "traitement_medical" : traitement_medical, "description_traitement" : description_traitement, 
                "date_debut_traitement" : date_debut_traitement, "date_fin_traitement" : date_fin_traitement, "eviction" : eviction, 
                "date_debut_eviction" : date_debut_eviction, "date_fin_eviction" : date_fin_eviction, 
                }
            dictInfosMedicales[IDindividu].append(dictTemp)
        
        # Récupération des photos individuelles
        dictPhotos = {}
        taillePhoto = 128
        if dictParametres["afficher_photos"] == "petite" : tailleImageFinal = 16
        if dictParametres["afficher_photos"] == "moyenne" : tailleImageFinal = 32
        if dictParametres["afficher_photos"] == "grande" : tailleImageFinal = 64
        if dictParametres["afficher_photos"] != "non" :
            for IDindividu in listeIDindividus :
                IDcivilite = dictIndividus[IDindividu]["IDcivilite"]
                nomFichier = Chemins.GetStaticPath("Images/128x128/%s" % DICT_CIVILITES[IDcivilite]["nomImage"])
                IDphoto, bmp = CTRL_Photo.GetPhoto(IDindividu=IDindividu, nomFichier=nomFichier, taillePhoto=(taillePhoto, taillePhoto), qualite=100)
                
                # Création de la photo dans le répertoire Temp
                nomFichier = UTILS_Fichiers.GetRepTemp(fichier="photoTmp%d.jpg" % IDindividu)
                bmp.SaveFile(nomFichier, type=wx.BITMAP_TYPE_JPEG)
                img = Image(nomFichier, width=tailleImageFinal, height=tailleImageFinal)
                dictPhotos[IDindividu] = img
            
        # ---------------- Création du PDF -------------------
        
        # Initialisation du PDF
        nomDoc = FonctionsPerso.GenerationNomDoc("LISTE_INFORMATIONS_MEDICALES", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=(self.largeur_page, self.hauteur_page), topMargin=30, bottomMargin=30)
        story = []
        
        largeurContenu = self.largeur_page - 75
        
        # Création du titre du document
        def Header():
            dataTableau = []
            largeursColonnes = ( (largeurContenu-100, 100) )
            dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
            dataTableau.append( (_(u"Informations médicales"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
            style = TableStyle([
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                    ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                    ('ALIGN', (0,0), (0,0), 'LEFT'), 
                    ('FONT',(0,0),(0,0), "Helvetica-Bold", 16), 
                    ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                    ('FONT',(1,0),(1,0), "Helvetica", 6), 
                    ])
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(style)
            story.append(tableau)
            story.append(Spacer(0,20))       
        
        # Insère un header
        Header() 

        # Texte d'introduction
        para_style_introduction = ParagraphStyle(name="normal", fontName="Helvetica", fontSize=7, leading=7, spaceBefore=0, spaceAfter=0, alignment=1)
        if texte_introduction and dictParametres["afficher_introduction"]:
            story.append(Paragraph("".join([u"<para>%s</para>" % texte for texte in texte_introduction]), para_style_introduction))
            story.append(Spacer(0, 15))

        # Activités
        for IDactivite in listeActivites :

            # Groupes
            if IDactivite in dictOuvertures :
                nbreGroupes = len(dictOuvertures[IDactivite])
                indexGroupe = 1
                for IDgroupe in dictOuvertures[IDactivite] :
                    nomGroupe = dictGroupes[IDgroupe]["nom"]
                    if isinstance(dictActivites[IDactivite], dict):
                        nomActivite = dictActivites[IDactivite]["nom"]
                    else:
                        nomActivite = dictActivites[IDactivite]

                    # Initialisation du tableau
                    dataTableau = []
                    largeursColonnes = []
                    labelsColonnes = []
                                        
                    # Recherche des entêtes de colonnes :
                    if dictParametres["afficher_photos"] != "non" :
                        labelsColonnes.append(_(u"Photo"))
                        largeursColonnes.append(tailleImageFinal+6)
                        
                    labelsColonnes.append(_(u"Nom - prénom"))
                    if dictParametres["largeur_colonne_nom"] == "automatique" :
                        largeursColonnes.append(120)
                    else :
                        largeursColonnes.append(int(dictParametres["largeur_colonne_nom"]))

                    if dictParametres["afficher_age"] == True :
                        labelsColonnes.append(_(u"Âge"))
                        if dictParametres["largeur_colonne_age"] == "automatique":
                            largeursColonnes.append(20)
                        else:
                            largeursColonnes.append(int(dictParametres["largeur_colonne_age"]))

                    # Calcule la largeur restante
                    largeurRestante = largeurContenu - sum(largeursColonnes)

                    # Calcul des largeurs de colonnes
                    largeurColonnes = largeurRestante * 1.0 / len(dictParametres["colonnes"])
                    for nom_categorie, categories in dictParametres["colonnes"]:
                        labelsColonnes.append(nom_categorie)
                        largeursColonnes.append(largeurColonnes)

                    # Création de l'entete de groupe
                    ligne = [u"%s - %s" % (nomActivite, nomGroupe),]
                    for x in range(0, len(labelsColonnes)-1):
                        ligne.append("")
                    dataTableau.append(ligne)
        
                    # Création des entêtes
                    ligne = []
                    for label in labelsColonnes :
                        ligne.append(label)
                    dataTableau.append(ligne)
                    
                    # --------- Création des lignes -----------
                            
                    # Création d'une liste temporaire pour le tri
                    listeIndividus = []
                    if IDactivite in dictOuvertures :
                        if IDgroupe in dictOuvertures[IDactivite] :
                            for IDindividu in listeIDindividus :
                                dictIndividu = dictIndividus[IDindividu]
                                if dictIndividu["IDgroupe"] == IDgroupe :
                                    valeursTri = (IDindividu, dictIndividu["nom"], dictIndividu["prenom"], dictIndividu["age"])
                                    
                                    # + Sélection uniquement des individus avec infos
                                    if dictParametres["individus_avec_infos"] == False or (dictParametres["individus_avec_infos"] == True and IDindividu in dictInfosMedicales ) :
                                        listeIndividus.append(valeursTri)
                    
                    if dictParametres["tri"] == "nom" : paramTri = 1 # Nom
                    if dictParametres["tri"] == "prenom" : paramTri = 2 # Prénom
                    if dictParametres["tri"] == "age" : paramTri = 3 # Age
                    if dictParametres["ordre"] == "croissant" :
                        ordreDecroissant = False
                    else:
                        ordreDecroissant = True
                    listeIndividus = sorted(listeIndividus, key=operator.itemgetter(paramTri), reverse=ordreDecroissant)
                    
                    # Récupération des lignes individus
                    for IDindividu, nom, prenom, age in listeIndividus :
                        dictIndividu = dictIndividus[IDindividu]
                        
                        ligne = []
                        
                        # Photo
                        if dictParametres["afficher_photos"] != "non" and IDindividu in dictPhotos :
                            img = dictPhotos[IDindividu]
                            ligne.append(img)
                        
                        # Nom
                        ligne.append(u"%s %s" % (nom, prenom))
                        
                        # Age
                        if dictParametres["afficher_age"] == True :
                            if age != None :
                                ligne.append(age)
                            else:
                                ligne.append("")
                        
                        # Informations médicales
                        paraStyle = ParagraphStyle(name="infos",
                                    fontName="Helvetica",
                                    fontSize=7,
                                    leading=8,
                                    spaceAfter=2,
                                    )

                        # Création des colonnes
                        has_infos = False
                        for nom_categorie, categories in dictParametres["colonnes"]:
                            liste_categories = UTILS_Texte.ConvertStrToListe(categories)

                            case = []
                            # Recherche s'il y a une info médicale dans cette case
                            if IDindividu in dictInfosMedicales:
                                for infoMedicale in dictInfosMedicales[IDindividu] :
                                    IDcategorie = infoMedicale["IDcategorie"]

                                    if IDcategorie in liste_categories or (0 in liste_categories and IDcategorie not in liste_categories_utilisees) :

                                        intitule = infoMedicale["intitule"]
                                        description = infoMedicale["description"]
                                        traitement = infoMedicale["traitement_medical"]
                                        description_traitement = infoMedicale["description_traitement"]
                                        date_debut_traitement = infoMedicale["date_debut_traitement"]
                                        date_fin_traitement = infoMedicale["date_fin_traitement"]

                                        # Intitulé et description
                                        if description != None and description != "":
                                            texteInfos = u"<b>%s</b> : %s" % (intitule, description)
                                        else:
                                            texteInfos = u"%s" % intitule
                                        if len(texteInfos) > 0 and texteInfos[-1] != ".": texteInfos += u"."
                                        # Traitement médical
                                        if traitement == 1 and description_traitement != None and description_traitement != "":
                                            texteDatesTraitement = u""
                                            if date_debut_traitement != None and date_fin_traitement != None:
                                                texteDatesTraitement = _(u" du %s au %s") % (UTILS_Dates.DateEngFr(date_debut_traitement), UTILS_Dates.DateEngFr(date_fin_traitement))
                                            if date_debut_traitement != None and date_fin_traitement == None:
                                                texteDatesTraitement = _(u" à partir du %s") % UTILS_Dates.DateEngFr(date_debut_traitement)
                                            if date_debut_traitement == None and date_fin_traitement != None:
                                                texteDatesTraitement = _(u" jusqu'au %s") % UTILS_Dates.DateEngFr(date_fin_traitement)
                                            texteInfos += _(u"Traitement%s : %s.") % (texteDatesTraitement, description_traitement)

                                        # Création du paragraphe
                                        case.append(Paragraph(texteInfos, paraStyle))
                                        has_infos = True

                            # Ajoute la case à la ligne
                            ligne.append(case)

                        # Ajout de la ligne individuelle dans le tableau
                        if dictParametres["individus_avec_infos"] == False or (dictParametres["individus_avec_infos"] == True and has_infos == True):
                            dataTableau.append(ligne)
                    
                    # Création des lignes vierges
                    for x in range(0, dictParametres["nbre_lignes_vierges"]):
                        ligne = []
                        for col in labelsColonnes :
                            ligne.append("")
                        dataTableau.append(ligne)
                                                
                    # Style du tableau
                    couleur_fond_entetes = UTILS_Divers.ConvertCouleurWXpourPDF(dictParametres["couleur_fond_entetes"])
                    
                    style = TableStyle([
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), # Centre verticalement toutes les cases
                            
                            ('FONT',(0,0),(-1,-1), "Helvetica", 7), # Donne la police de caract. + taille de police 
                            ('GRID', (0,0), (-1,-1), 0.25, colors.black), # Crée la bordure noire pour tout le tableau
                            ('ALIGN', (0,1), (-2,-1), 'CENTRE'), # Centre les cases
                            
                            ('ALIGN', (0,1), (-1,1), 'CENTRE'), # Ligne de labels colonne alignée au centre
                            ('FONT',(0,1),(-1,1), "Helvetica", 6), # Donne la police de caract. + taille de police des labels
                            
                            ('SPAN',(0,0),(-1,0)), # Fusionne les lignes du haut pour faire le titre du groupe
                            ('FONT',(0,0),(0,0), "Helvetica-Bold", 10), # Donne la police de caract. + taille de police du titre de groupe
                            ('BACKGROUND', (0,0), (-1,0), couleur_fond_entetes), # Donne la couleur de fond du titre de groupe
                            
                            ])
                        
                       
                    # Création du tableau
                    tableau = Table(dataTableau, largeursColonnes)
                    tableau.setStyle(style)
                    story.append(tableau)
                    story.append(Spacer(0,20))
                    
                    # Saut de page après un groupe
                    if dictParametres["saut_page_groupe"] == True :
                        story.append(PageBreak())
                        # Insère un header
                        if indexGroupe < nbreGroupes :
                            Header() 
                    
                    indexGroupe += 1
            
        # Enregistrement du PDF
        doc.build(story)
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)
        





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
