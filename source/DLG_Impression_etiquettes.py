#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
from wx.lib.floatcanvas import FloatCanvas
import numpy
import wx.lib.agw.hyperlink as Hyperlink
import wx.lib.agw.pybusyinfo as PBI

import DLG_Noedoc
import CTRL_Bandeau
import CTRL_Choix_modele
import UTILS_Config
import OL_Etiquettes

try: import psyco; psyco.full()
except: pass

# Couleurs
COULEUR_ZONE_TRAVAIL = (100, 200, 0)
COULEUR_FOND_PAGE = (255, 255, 255)
EPAISSEUR_OMBRE = 2
COULEUR_OMBRE_PAGE = (0, 0, 0)
COULEUR_BORD_ETIQUETTE = (255, 0, 0)
COULEUR_FOND_ETIQUETTE = (200, 200, 200)

    
# ------------------------------------------------------------------------------------------------------------

LISTE_CATEGORIES = [
    ("individu", u"Individus"),
    ("famille", u"Familles"),
    ]


class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(-1, -1)) 
        self.parent = parent
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        listeItems = []
        index = 0
        for code, label in LISTE_CATEGORIES :
            listeItems.append(label)
            index += 1
        return listeItems

    def SetCategorie(self, categorie=""):
        index = 0
        for code, label in LISTE_CATEGORIES :
            if code == categorie :
                 self.SetSelection(index)
            index += 1

    def GetCategorie(self):
        index = self.GetSelection()
        return LISTE_CATEGORIES[index][0]

# -----------------------------------------------------------------------------------------------------
    
class CTRL_Apercu(wx.Panel):
    def __init__(self, parent,
                IDmodele=None, 
                taille_page=(210, 297),
                margeHaut=10,
                margeGauche=10,
                margeBas = 10,
                margeDroite=10,
                espaceVertical=5,
                espaceHorizontal=5,
                ):
        wx.Panel.__init__(self, parent, id=-1, style=wx.SUNKEN_BORDER|wx.TAB_TRAVERSAL)        
        self.parent = parent
        self.taille_page = taille_page
        self.largeurPage = taille_page[0]
        self.hauteurPage = taille_page[1]
        self.margeHaut = margeHaut
        self.margeGauche = margeGauche
        self.margeBas = margeBas
        self.margeDroite = margeDroite
        self.espaceVertical = espaceVertical
        self.espaceHorizontal = espaceHorizontal
        
        # FloatCanvas
        self.canvas = FloatCanvas.FloatCanvas(self, Debug=0, BackgroundColor=COULEUR_ZONE_TRAVAIL)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.canvas, 0, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        
        # Init Modèle
        self.SetModele(IDmodele)
    
    def SetModele(self, IDmodele=None):
        # Initialisation du modèle de document
        if IDmodele == None :
            self.largeurEtiquette = 0
            self.hauteurEtiquette = 0
            return
        modeleDoc = DLG_Noedoc.ModeleDoc(IDmodele=IDmodele)
        self.largeurEtiquette = modeleDoc.dictInfosModele["largeur"]
        self.hauteurEtiquette = modeleDoc.dictInfosModele["hauteur"]
        
    def SetTaillePage(self, taille_page=(210, 297)):
        self.taille_page = taille_page
        self.largeurPage = taille_page[0]
        self.hauteurPage = taille_page[1]
        
    def SetMargeHaut(self, valeur=0):
        self.margeHaut = valeur

    def SetMargeGauche(self, valeur=0):
        self.margeGauche = valeur
        
    def SetMargeBas(self, valeur=0):
        self.margeBas = valeur
        
    def SetMargeDroite(self, valeur=0):
        self.margeDroite = valeur
        
    def SetEspaceVertical(self, valeur=0):
        self.espaceVertical = valeur
        
    def SetEspaceHorizontal(self, valeur=0):
        self.espaceHorizontal = valeur

    def MAJ(self):
        self.canvas.ClearAll()
        self.Init_page() 
        self.Dessine_etiquettes() 
        self.canvas.ZoomToBB()        

    def Init_page(self):
        """ Dessine le fond de page """
        # Ombre de la page
        ombre1 = FloatCanvas.Rectangle( (self.taille_page[0]-1, -EPAISSEUR_OMBRE), (EPAISSEUR_OMBRE+1, self.taille_page[1]), LineWidth=0, LineColor=COULEUR_OMBRE_PAGE, FillColor=COULEUR_OMBRE_PAGE, InForeground=False)
        ombre2 = FloatCanvas.Rectangle( (EPAISSEUR_OMBRE, -EPAISSEUR_OMBRE), (self.taille_page[0]-1, EPAISSEUR_OMBRE+1), LineWidth=0, LineColor=COULEUR_OMBRE_PAGE, FillColor=COULEUR_OMBRE_PAGE, InForeground=False)
        # Fond de page
        rect = FloatCanvas.Rectangle( (0, 0), self.taille_page, LineWidth=1, FillColor=COULEUR_FOND_PAGE, InForeground=False)
        self.page = self.canvas.AddGroup([ombre1, ombre2, rect], InForeground=False)

    def Dessine_etiquettes(self):
        # Calcul du nbre de colonnes et de lignes
        if self.largeurEtiquette < 1 or self.hauteurEtiquette < 1 :
            nbreColonnes = 0
            nbreLignes = 0
        else:
            nbreColonnes = (self.largeurPage - self.margeGauche - self.margeDroite + self.espaceHorizontal) / (self.largeurEtiquette + self.espaceHorizontal)
            nbreLignes = (self.hauteurPage - self.margeHaut - self.margeBas + self.espaceVertical) / (self.hauteurEtiquette + self.espaceVertical)
        # Dessin des étiquettes
        numColonne = 0
        numLigne = 0
        y = self.hauteurPage - self.margeHaut- self.hauteurEtiquette
        for numLigne in range(0, nbreLignes) :
            x = self.margeGauche
            for numColonne in range(0, nbreColonnes) :
                rect = FloatCanvas.Rectangle(numpy.array([x, y]), numpy.array([self.largeurEtiquette, self.hauteurEtiquette]), LineWidth=0.25, LineColor=COULEUR_BORD_ETIQUETTE, FillColor=COULEUR_FOND_ETIQUETTE, InForeground=True)
                self.canvas.AddObject(rect)
                x += (self.largeurEtiquette + self.espaceHorizontal)
            y -= (self.hauteurEtiquette + self.espaceVertical)


# ----------------------------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent
        
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
        
    def OnLeftLink(self, event):
        if self.URL == "filtrer" : self.parent.ctrl_donnees.Filtrer()
        if self.URL == "tout" : self.parent.ctrl_donnees.CocheTout()
        if self.URL == "rien" : self.parent.ctrl_donnees.CocheRien()
        self.UpdateLink()
        
        
# ---------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="individu", IDindividu=None, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.categorie = categorie

        # DLG Attente
        dlgAttente = PBI.PyBusyInfo(u"Veuillez patienter durant l'initialisation de l'éditeur...", parent=None, title=u"Patientez", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 

        # Si on vient d'une fiche famille ou d'une fiche individuelle
        if IDindividu != None : self.categorie="individu"
        if IDfamille != None : self.categorie="famille"
        
        # Bandeau
        titre = u"Edition d'étiquettes et de badges"
        intro = u"Vous pouvez ici imprimer rapidement des planches d'étiquettes ou de badges au format PDF. Commencez par sélectionner la catégorie de données et un modèle, puis définissez le gabarit de la page avant de cocher les données à afficher."
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Etiquette.png")
        
        # Modèle
        self.box_modele_staticbox = wx.StaticBox(self, -1, u"Modèle")
        self.label_categorie = wx.StaticText(self, -1, u"Catégorie :")
        self.ctrl_categorie = CTRL_Categorie(self)
        self.label_modele = wx.StaticText(self, -1, u"Modèle :")
        self.ctrl_modele = CTRL_Choix_modele.CTRL_Choice(self, categorie=self.categorie)
        self.bouton_modele = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        # Gabarit
        self.box_gabarit_staticbox = wx.StaticBox(self, -1, u"Gabarit (en mm)")
        self.label_largeur_page = wx.StaticText(self, -1, u"Largeur page :")
        self.ctrl_largeur_page = wx.SpinCtrl(self, -1, u"", min=1, max=1000)
        self.label_marge_haut = wx.StaticText(self, -1, u"Marge haut :")
        self.ctrl_marge_haut = wx.SpinCtrl(self, -1, u"", min=0, max=1000)
        self.label_hauteur_page = wx.StaticText(self, -1, u"Hauteur page :")
        self.ctrl_hauteur_page = wx.SpinCtrl(self, -1, u"", min=1, max=1000)
        self.label_marge_bas = wx.StaticText(self, -1, u"Marge bas :")
        self.ctrl_marge_bas = wx.SpinCtrl(self, -1, u"", min=0, max=1000)
        self.label_espace_vertic = wx.StaticText(self, -1, u"Espace vertic. :")
        self.ctrl_espace_vertic = wx.SpinCtrl(self, -1, u"", min=0, max=1000)
        self.label_marge_gauche = wx.StaticText(self, -1, u"Marge gauche :")
        self.ctrl_marge_gauche = wx.SpinCtrl(self, -1, u"", min=0, max=1000)
        self.label_espace_horiz = wx.StaticText(self, -1, u"Espace horiz. :")
        self.ctrl_espace_horiz = wx.SpinCtrl(self, -1, u"", min=0, max=1000)
        self.label_marge_droite = wx.StaticText(self, -1, u"Marge droite :")
        self.ctrl_marge_droite = wx.SpinCtrl(self, -1, u"", min=0, max=1000)
        
        # Aperçu
        self.box_apercu_staticbox = wx.StaticBox(self, -1, u"Aperçu du gabarit")
        self.ctrl_apercu = CTRL_Apercu(self)

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, u"Options")
        self.check_contour = wx.CheckBox(self, -1, u"Contour des étiquettes")
        self.check_reperes = wx.CheckBox(self, -1, u"Repères de découpe")
        
        # Données
        self.box_donnees_staticbox = wx.StaticBox(self, -1, u"Données")
        self.ctrl_donnees = OL_Etiquettes.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_donnees.SetMinSize((10, 10))
        self.hyper_filtrer = Hyperlien(self, label=u"Filtrer", infobulle=u"Cliquez ici pour filtrer la liste", URL="filtrer")
        self.label_separation1 = wx.StaticText(self, -1, u"|")
        self.hyper_select = Hyperlien(self, label=u"Tout sélectionner", infobulle=u"Cliquez ici pour tout sélectionner", URL="tout")
        self.label_separation2 = wx.StaticText(self, -1, u"|")
        self.hyper_deselect = Hyperlien(self, label=u"Tout désélectionner", infobulle=u"Cliquez ici pour tout désélectionner", URL="rien")
        
        if IDindividu != None or IDfamille != None : 
            self.hyper_filtrer.Enable(False)
            self.label_separation1.Enable(False)
            self.hyper_select.Enable(False)
            self.label_separation2.Enable(False)
            self.hyper_deselect.Enable(False)

        # Mémorisation des paramètres
        self.ctrl_memoriser = wx.CheckBox(self, -1, u"Mémoriser les paramètres")
        font = self.GetFont() 
        font.SetPointSize(7)
        self.ctrl_memoriser.SetFont(font)
        self.ctrl_memoriser.SetValue(True) 
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Apercu_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixCategorie, self.ctrl_categorie)
        self.Bind(wx.EVT_CHOICE, self.OnChoixModele, self.ctrl_modele)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModele, self.bouton_modele)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixTaille, self.ctrl_largeur_page)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixMargeH, self.ctrl_marge_haut)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixTaille, self.ctrl_hauteur_page)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixMargeB, self.ctrl_marge_bas)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixEspaceV, self.ctrl_espace_vertic)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixMargeG, self.ctrl_marge_gauche)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixEspaceH, self.ctrl_espace_horiz)
        self.Bind(wx.EVT_SPINCTRL, self.OnChoixMargeD, self.ctrl_marge_droite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        largeurPage = UTILS_Config.GetParametre("impression_etiquettes_largeurpage", defaut=210)
        hauteurPage = UTILS_Config.GetParametre("impression_etiquettes_hauteurpage", defaut=297)
        margeHaut = UTILS_Config.GetParametre("impression_etiquettes_margehaut", defaut=10)
        margeBas = UTILS_Config.GetParametre("impression_etiquettes_margebas", defaut=10)
        margeGauche = UTILS_Config.GetParametre("impression_etiquettes_margegauche", defaut=10)
        margeDroite = UTILS_Config.GetParametre("impression_etiquettes_margedroite", defaut=10)
        espaceV = UTILS_Config.GetParametre("impression_etiquettes_espacev", defaut=5)
        espaceH = UTILS_Config.GetParametre("impression_etiquettes_espaceh", defaut=5)
        contour = UTILS_Config.GetParametre("impression_etiquettes_contour", defaut=True)
        reperes = UTILS_Config.GetParametre("impression_etiquettes_reperes", defaut=True)
        memoriser = UTILS_Config.GetParametre("impression_etiquettes_memoriser", defaut=1)
        
        self.ctrl_largeur_page.SetValue(largeurPage)
        self.ctrl_hauteur_page.SetValue(hauteurPage)
        self.ctrl_marge_haut.SetValue(margeHaut)
        self.ctrl_marge_bas.SetValue(margeBas)
        self.ctrl_marge_gauche.SetValue(margeGauche)
        self.ctrl_marge_droite.SetValue(margeDroite)
        self.ctrl_espace_vertic.SetValue(espaceV)
        self.ctrl_espace_horiz.SetValue(espaceH)
        
        self.check_contour.SetValue(contour)
        self.check_reperes.SetValue(reperes)
        self.ctrl_memoriser.SetValue(memoriser)
        
        self.ctrl_categorie.SetCategorie(self.categorie)
        
        # Init Aperçu
        self.ctrl_apercu.SetTaillePage((largeurPage, hauteurPage))
        self.ctrl_apercu.SetMargeHaut(margeHaut)
        self.ctrl_apercu.SetMargeGauche(margeGauche)
        self.ctrl_apercu.SetMargeBas(margeBas)
        self.ctrl_apercu.SetMargeDroite(margeDroite)
        self.ctrl_apercu.SetEspaceVertical(espaceV)
        self.ctrl_apercu.SetEspaceHorizontal(espaceH)
        self.ctrl_apercu.SetModele(self.ctrl_modele.GetID())
        self.ctrl_apercu.MAJ() 
        
        if IDindividu != None or IDfamille != None :
            self.ctrl_categorie.Enable(False)
        
        # Init liste données
        self.ctrl_donnees.IDindividu = IDindividu
        self.ctrl_donnees.IDfamille = IDfamille
        self.ctrl_donnees.MAJ(self.categorie) 
        self.ctrl_donnees.CocheTout() 
        
        del dlgAttente

    def __set_properties(self):
        self.ctrl_categorie.SetToolTipString(u"Sélectionnez ici une catégorie de données")
        self.ctrl_modele.SetToolTipString(u"Sélectionnez ici un modèle")
        self.bouton_modele.SetToolTipString(u"Cliquez ici pour accéder au paramétrage des modèles")
        self.ctrl_largeur_page.SetMinSize((60, -1))
        self.ctrl_largeur_page.SetToolTipString(u"Saisissez ici la largeur de la page (en mm)")
        self.ctrl_marge_haut.SetMinSize((60, -1))
        self.ctrl_marge_haut.SetToolTipString(u"Saisissez ici la marge de haut de page (en mm)")
        self.ctrl_hauteur_page.SetMinSize((60, -1))
        self.ctrl_hauteur_page.SetToolTipString(u"Saisissez ici la hauteur de la page (en mm)")
        self.ctrl_marge_bas.SetMinSize((60, -1))
        self.ctrl_marge_bas.SetToolTipString(u"Saisissez ici la marge de bas de page (en mm)")
        self.ctrl_espace_vertic.SetMinSize((60, -1))
        self.ctrl_espace_vertic.SetToolTipString(u"Saisissez ici l'espace vertical entre 2 étiquettes (en mm)")
        self.ctrl_marge_gauche.SetMinSize((60, -1))
        self.ctrl_marge_gauche.SetToolTipString(u"Saisissez ici la marge gauche de la page (en mm)")
        self.ctrl_espace_horiz.SetMinSize((60, -1))
        self.ctrl_espace_horiz.SetToolTipString(u"Saisissez ici l'espace horizontal entre 2 étiquettes de la page (en mm)")
        self.ctrl_marge_droite.SetMinSize((60, -1))
        self.ctrl_marge_droite.SetToolTipString(u"Saisissez ici la marge droite de la page (en mm)")
        self.check_contour.SetToolTipString(u"Cochez ici pour afficher un cadre noir autour de chaque étiquette")
        self.check_reperes.SetToolTipString(u"Cochez cette case pour afficher les repères de découpe sur chaque page")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour afficher un apercu du PDF")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.ctrl_memoriser.SetToolTipString(u"Cochez cette case pour mémoriser les paramètres pour la prochaine édition")
        self.SetMinSize((750, 770))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)

        # Modèle
        box_modele = wx.StaticBoxSizer(self.box_modele_staticbox, wx.VERTICAL)
        grid_sizer_modele1 = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_modele1.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele1.Add(self.ctrl_categorie, 0, wx.EXPAND, 0)
        grid_sizer_modele1.Add(self.label_modele, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_modele2 = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_modele2.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
        grid_sizer_modele2.Add(self.bouton_modele, 0, 0, 0)
        grid_sizer_modele2.AddGrowableCol(0)
        grid_sizer_modele1.Add(grid_sizer_modele2, 1, wx.EXPAND, 0)
        grid_sizer_modele1.AddGrowableCol(1)
        box_modele.Add(grid_sizer_modele1, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(box_modele, 1, wx.EXPAND, 0)
        
        # Gabarit
        box_gabarit = wx.StaticBoxSizer(self.box_gabarit_staticbox, wx.VERTICAL)
        grid_sizer_gabarit = wx.FlexGridSizer(rows=4, cols=4, vgap=2, hgap=5)
        grid_sizer_gabarit.Add(self.label_largeur_page, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_largeur_page, 0, wx.RIGHT, 10)
        grid_sizer_gabarit.Add(self.label_marge_haut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_marge_haut, 0, 0, 0)
        grid_sizer_gabarit.Add(self.label_hauteur_page, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_hauteur_page, 0, 0, 0)
        grid_sizer_gabarit.Add(self.label_marge_bas, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_marge_bas, 0, 0, 0)
        grid_sizer_gabarit.Add(self.label_espace_vertic, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_espace_vertic, 0, 0, 0)
        grid_sizer_gabarit.Add(self.label_marge_gauche, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_marge_gauche, 0, 0, 0)
        grid_sizer_gabarit.Add(self.label_espace_horiz, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_espace_horiz, 0, 0, 0)
        grid_sizer_gabarit.Add(self.label_marge_droite, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_gabarit.Add(self.ctrl_marge_droite, 0, 0, 0)
        box_gabarit.Add(grid_sizer_gabarit, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(box_gabarit, 1, wx.EXPAND, 0)

        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_options.Add(self.check_contour, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.check_reperes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_gauche.Add(box_options, 1, wx.EXPAND, 0)

        # Aperçu
        box_apercu = wx.StaticBoxSizer(self.box_apercu_staticbox, wx.VERTICAL)
        box_apercu.Add(self.ctrl_apercu, 1, wx.ALL|wx.EXPAND, 5)
        
        grid_sizer_haut.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        grid_sizer_haut.Add(box_apercu, 1, wx.EXPAND, 0)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Données
        box_donnees = wx.StaticBoxSizer(self.box_donnees_staticbox, wx.VERTICAL)
        grid_sizer_donnees = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_donnees.Add(self.ctrl_donnees, 1, wx.EXPAND, 0)
        
        # Commandes de liste
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=6, vgap=2, hgap=2)
        grid_sizer_commandes.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.hyper_filtrer, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_select, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.label_separation2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.hyper_deselect, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_donnees.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_donnees.AddGrowableRow(0)
        grid_sizer_donnees.AddGrowableCol(0)
        box_donnees.Add(grid_sizer_donnees, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(box_donnees, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Check Mémoriser
        grid_sizer_base.Add(self.ctrl_memoriser, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)

        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
        
        wx.CallLater(0, self.Layout) # Contre pb d'affichage du wx.Choice
    
    def OnChoixCategorie(self, event):
        self.categorie = self.ctrl_categorie.GetCategorie() 
        self.ctrl_modele.SetCategorie(self.categorie)
        self.ctrl_apercu.SetModele(self.ctrl_modele.GetID())
        self.ctrl_apercu.MAJ() 
        self.ctrl_donnees.MAJ(categorie=self.categorie)
        self.ctrl_donnees.CocheTout() 
        
    def OnChoixModele(self, event): 
        self.ctrl_apercu.SetModele(self.ctrl_modele.GetID())
        self.ctrl_apercu.MAJ() 

    def OnBoutonModele(self, event): 
        import DLG_Modeles_docs
        dlg = DLG_Modeles_docs.Dialog(self, categorie=self.categorie)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_modele.MAJ() 
        self.ctrl_apercu.SetModele(self.ctrl_modele.GetID())
        self.ctrl_apercu.MAJ() 

    def OnChoixTaille(self, event): 
        largeur = self.ctrl_largeur_page.GetValue()
        hauteur = self.ctrl_hauteur_page.GetValue()
        self.ctrl_apercu.SetTaillePage((largeur, hauteur))
        self.ctrl_apercu.MAJ() 

    def OnChoixMargeH(self, event): 
        valeur = self.ctrl_marge_haut.GetValue()
        self.ctrl_apercu.SetMargeHaut(valeur)
        self.ctrl_apercu.MAJ() 

    def OnChoixMargeB(self, event): 
        valeur = self.ctrl_marge_bas.GetValue()
        self.ctrl_apercu.SetMargeBas(valeur)
        self.ctrl_apercu.MAJ() 
        
    def OnChoixMargeG(self, event): 
        valeur = self.ctrl_marge_gauche.GetValue()
        self.ctrl_apercu.SetMargeGauche(valeur)
        self.ctrl_apercu.MAJ() 

    def OnChoixMargeD(self, event): 
        valeur = self.ctrl_marge_droite.GetValue()
        self.ctrl_apercu.SetMargeDroite(valeur)
        self.ctrl_apercu.MAJ() 

    def OnChoixEspaceV(self, event): 
        valeur = self.ctrl_espace_vertic.GetValue()
        self.ctrl_apercu.SetEspaceVertical(valeur)
        self.ctrl_apercu.MAJ() 

    def OnChoixEspaceH(self, event): 
        valeur = self.ctrl_espace_horiz.GetValue()
        self.ctrl_apercu.SetEspaceHorizontal(valeur)
        self.ctrl_apercu.MAJ() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Editiondtiquettesetdebadges")

    def OnBoutonAnnuler(self, event):
        self.MemoriserParametres() 
        self.EndModal(wx.ID_CANCEL)

    def MemoriserParametres(self):
        if self.ctrl_memoriser.GetValue() == True :
            UTILS_Config.SetParametre("impression_etiquettes_largeurpage", self.ctrl_largeur_page.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_hauteurpage", self.ctrl_hauteur_page.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_margehaut", self.ctrl_marge_haut.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_margebas", self.ctrl_marge_bas.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_margegauche", self.ctrl_marge_gauche.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_margedroite", self.ctrl_marge_droite.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_espacev", self.ctrl_espace_vertic.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_espaceh", self.ctrl_espace_horiz.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_contour", self.check_contour.GetValue())
            UTILS_Config.SetParametre("impression_etiquettes_reperes", self.check_reperes.GetValue())
        UTILS_Config.SetParametre("impression_etiquettes_memoriser", self.ctrl_memoriser.GetValue())
        
    def OnBoutonOk(self, event): 
        # Récupère les paramètres
        IDmodele = self.ctrl_modele.GetID() 
        if IDmodele == None :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un modèle !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # DLG Attente
        taillePage = (self.ctrl_largeur_page.GetValue(), self.ctrl_hauteur_page.GetValue())
        margeHaut = self.ctrl_marge_haut.GetValue()
        margeGauche = self.ctrl_marge_gauche.GetValue()
        margeBas = self.ctrl_marge_bas.GetValue()
        margeDroite = self.ctrl_marge_droite.GetValue()
        espaceVertical = self.ctrl_espace_vertic.GetValue()
        espaceHorizontal = self.ctrl_espace_horiz.GetValue()
        AfficherContourEtiquette = self.check_contour.GetValue()
        AfficherReperesDecoupe = self.check_reperes.GetValue()
        
        # Récupération des valeurs
        listeValeurs = self.ctrl_donnees.GetInfosCoches()
        if len(listeValeurs) == 0 :
            dlg = wx.MessageDialog(self, u"Il n'y a aucune donnée à imprimer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Impression PDF
        import UTILS_Impression_etiquettes
        UTILS_Impression_etiquettes.Impression(
                    IDmodele=IDmodele, 
                    taillePage=taillePage,
                    listeValeurs=listeValeurs,
                    margeHaut=margeHaut,
                    margeGauche=margeGauche,
                    margeBas=margeBas, 
                    margeDroite=margeDroite,
                    espaceVertical=espaceVertical,
                    espaceHorizontal=espaceHorizontal,
                    AfficherContourEtiquette=AfficherContourEtiquette,
                    AfficherReperesDecoupe=AfficherReperesDecoupe,
                    )
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
