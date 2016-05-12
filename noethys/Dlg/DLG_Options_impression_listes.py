#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB

from Utils import UTILS_Config
from Utils import UTILS_Parametres

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Propertygrid
import wx.propgrid as wxpg
import copy




class CTRL_Parametres(CTRL_Propertygrid.CTRL) :
    def __init__(self, parent):
        CTRL_Propertygrid.CTRL.__init__(self, parent)
    
    def Remplissage(self):
        listeChampsPiedsPages = ["{DATE_JOUR}", "{TITRE_DOCUMENT}", "{NOM_ORGANISATEUR}", "{NUM_PAGE}", "{NBRE_PAGES}"]

        # --------------------------- Divers ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Divers")) )

        # Inclure les images
        propriete = wxpg.BoolProperty(label=_(u"Inclure les images"), name="inclure_images", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour inclure les images")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Entete de colonne sur chaque page
        propriete = wxpg.BoolProperty(label=_(u"Afficher les entêtes sur chaque page"), name="entetes_toutes_pages", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour afficher les entêtes de colonne sur chaque page")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)

        # Qualité de l'impression
        labels = [_(u"Brouillon"), _(u"Basse"), _(u"Moyenne"), _(u"Haute")]
        propriete = wxpg.EnumProperty(label=_(u"Qualité d'impression"), name="qualite_impression", labels=labels, values=[wx.PRINT_QUALITY_DRAFT, wx.PRINT_QUALITY_LOW, wx.PRINT_QUALITY_MEDIUM, wx.PRINT_QUALITY_HIGH] , value=wx.PRINT_QUALITY_MEDIUM)
        propriete.SetHelpString(_(u"Sélectionnez la qualité d'impression (Moyenne par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # --------------------------- Marges ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Marges")) )

        # Gauche
        propriete = wxpg.IntProperty(label=_(u"Gauche"), name="marge_gauche", value=5)
        propriete.SetHelpString(_(u"Saisissez une taille de marge")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("marge_gauche", "SpinCtrl")

        # Droite
        propriete = wxpg.IntProperty(label=_(u"Droite"), name="marge_droite", value=5)
        propriete.SetHelpString(_(u"Saisissez une taille de marge")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("marge_droite", "SpinCtrl")

        # Haut
        propriete = wxpg.IntProperty(label=_(u"Haut"), name="marge_haut", value=5)
        propriete.SetHelpString(_(u"Saisissez une taille de marge")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("marge_haut", "SpinCtrl")

        # Bas
        propriete = wxpg.IntProperty(label=_(u"Bas"), name="marge_bas", value=5)
        propriete.SetHelpString(_(u"Saisissez une taille de marge")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("marge_bas", "SpinCtrl")

        # --------------------------- Quadrillage ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Quadrillage")) )

        # Epaisseur de trait
        propriete = wxpg.FloatProperty(label=_(u"Epaisseur de trait"), name="grille_trait_epaisseur", value=0.25)
        propriete.SetHelpString(_(u"Saisissez une épaisseur de trait (Par défaut '0.25')")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur de trait
        propriete = wxpg.ColourProperty(label=_(u"Couleur de trait"), name="grille_trait_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur de trait")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- Titre de liste ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Titre")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="titre_taille_texte", value=16)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (16 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("titre_taille_texte", "SpinCtrl")

        # Style
        labels = [_(u"Normal"), _(u"Light"), "Gras"]
        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="titre_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_BOLD)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="titre_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="titre_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"Sélectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # --------------------------- Intro ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Introduction")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="intro_taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("intro_taille_texte", "SpinCtrl")

        # Style
        labels = [_(u"Normal"), _(u"Light"), "Gras"]
        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="intro_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_NORMAL)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="intro_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="intro_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"Sélectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- Titre de colonne  ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Entête de colonne")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="titre_colonne_taille_texte", value=8)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (8 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("titre_colonne_taille_texte", "SpinCtrl")

        #  Style
        labels = [_(u"Normal"), _(u"Light"), "Gras"]
        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="titre_colonne_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_NORMAL)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="titre_colonne_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="titre_colonne_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_CENTER)
        propriete.SetHelpString(_(u"Sélectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur de fond
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond"), name="titre_colonne_couleur_fond", value=wx.Colour(240, 240, 240))
        propriete.SetHelpString(_(u"Sélectionnez une couleur de fond")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- Ligne  ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Ligne")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="ligne_taille_texte", value=8)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (8 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("ligne_taille_texte", "SpinCtrl")

        #  Style
        labels = [_(u"Normal"), _(u"Light"), "Gras"]
        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="ligne_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_NORMAL)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="ligne_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Multilignes autorisé
        propriete = wxpg.BoolProperty(label=_(u"Autoriser saut à la ligne"), name="ligne_multilignes", value=True)
        propriete.SetHelpString(_(u"Cochez cette case pour autoriser le saut à la ligne en cas de colonne trop étroite")) 
        propriete.SetAttribute("UseCheckbox", True)
        self.Append(propriete)


        # --------------------------- Pied de page  ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Pied de page")) )
        
        # Texte de gauche
        valeur = "{DATE_JOUR}"
        propriete = wxpg.StringProperty(label=_(u"Texte de gauche"), name="pied_page_texte_gauche", value=valeur)
        propriete.SetHelpString(_(u"Saisissez le texte de gauche du pied de page (Par défaut '%s'). Vous pouvez intégrer les mots-clés suivants : %s") % (valeur, ", ".join(listeChampsPiedsPages)))
        self.Append(propriete)

        # Texte du milieu
        valeur = "{TITRE_DOCUMENT} - {NOM_ORGANISATEUR}"
        propriete = wxpg.StringProperty(label=_(u"Texte du milieu"), name="pied_page_texte_milieu", value=valeur)
        propriete.SetHelpString(_(u"Saisissez le texte du milieu du pied de page (Par défaut '%s'). Vous pouvez intégrer les mots-clés suivants : %s") % (valeur, ", ".join(listeChampsPiedsPages)))
        self.Append(propriete)

        # Texte de droite
        valeur = "{NUM_PAGE} / {NBRE_PAGES}"
        propriete = wxpg.StringProperty(label=_(u"Texte de droite"), name="pied_page_texte_droite", value=valeur)
        propriete.SetHelpString(_(u"Saisissez le texte de droite du pied de page (Par défaut '%s'). Vous pouvez intégrer les mots-clés suivants : %s") % (valeur, ", ".join(listeChampsPiedsPages)))
        self.Append(propriete)

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="pied_page_taille_texte", value=8)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (8 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("pied_page_taille_texte", "SpinCtrl")

        #  Style
        labels = [_(u"Normal"), _(u"Light"), "Gras"]
        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="pied_page_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_NORMAL)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="pied_page_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # --------------------------- Pied de colonne  ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Pied de colonne")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="pied_colonne_taille_texte", value=8)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (8 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("pied_colonne_taille_texte", "SpinCtrl")

        #  Style
        labels = [_(u"Normal"), _(u"Light"), "Gras"]
        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="pied_colonne_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_NORMAL)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="pied_colonne_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="pied_colonne_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_CENTER)
        propriete.SetHelpString(_(u"Sélectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur de fond
        propriete = wxpg.ColourProperty(label=_(u"Couleur de fond"), name="pied_colonne_couleur_fond", value=wx.Colour(240, 240, 240))
        propriete.SetHelpString(_(u"Sélectionnez une couleur de fond")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # --------------------------- Pied de liste ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Conclusion")) )

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="conclusion_taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("conclusion_taille_texte", "SpinCtrl")

        # Style
        labels = [_(u"Normal"), _(u"Light"), "Gras"]
        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="conclusion_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_BOLD)
        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        
        # Couleur
        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="conclusion_couleur", value=wx.BLACK)
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="conclusion_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"Sélectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)






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
        dictParametres = UTILS_Parametres.ParametresCategorie(mode="get", categorie="impression_facture", dictParametres=dictValeurs)
        # Envoie les paramètres dans le contrôle
        for nom, valeur in dictParametres.iteritems() :
            propriete = self.GetPropertyByName(nom)
            ancienneValeur = propriete.GetValue() 
            propriete.SetValue(valeur)
    
    def Sauvegarde(self, forcer=False):
        """ Mémorisation des valeurs du contrôle """
        dictValeurs = copy.deepcopy(self.GetPropertyValues())
        UTILS_Parametres.ParametresCategorie(mode="set", categorie="impression_facture", dictParametres=dictValeurs)
        
    def GetValeurs(self) :
        return self.GetPropertyValues()


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, dictOptions={}):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Orientation
        self.box_orientation_staticbox = wx.StaticBox(self, -1, _(u"Orientation"))
        self.ctrl_radio_portrait = wx.RadioButton(self, -1, u"", style=wx.RB_GROUP)
        self.ctrl_image_portrait = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Orientation_vertical.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_radio_paysage = wx.RadioButton(self, -1, u"")
        self.ctrl_image_paysage = wx.StaticBitmap(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/32x32/Orientation_horizontal.png"), wx.BITMAP_TYPE_ANY))
        
        # Textes
        self.box_document_staticbox = wx.StaticBox(self, -1, _(u"Document"))
        self.label_titre = wx.StaticText(self, -1, _(u"Titre :"))
        self.ctrl_titre = wx.TextCtrl(self, -1, u"")
        self.label_introduction = wx.StaticText(self, -1, _(u"Introduction :"))
        self.ctrl_introduction = wx.TextCtrl(self, -1, u"")
        self.label_conclusion = wx.StaticText(self, -1, _(u"Conclusion :"))
        self.ctrl_conclusion = wx.TextCtrl(self, -1, u"")
        
        # Paramètres généraux
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options d'impression"))
        self.ctrl_parametres = CTRL_Parametres(self)
        self.ctrl_parametres.Importation() 
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)
        self.ctrl_parametres.SetMinSize((440, 120)) 
        
        self.__do_layout()
        
        # Properties
        self.ctrl_radio_portrait.SetToolTipString(_(u"Cliquez ici pour sélectionner une orientation portrait"))
        self.ctrl_image_portrait.SetToolTipString(_(u"Cliquez ici pour sélectionner une orientation portrait"))
        self.ctrl_radio_paysage.SetToolTipString(_(u"Cliquez ici pour sélectionner une orientation paysage"))
        self.ctrl_image_paysage.SetToolTipString(_(u"Cliquez ici pour sélectionner une orientation paysage"))
        self.ctrl_titre.SetToolTipString(_(u"Vous pouvez modifier ici le titre du document"))
        self.ctrl_introduction.SetToolTipString(_(u"Vous pouvez modifier ici l'introduction du document"))
        self.ctrl_conclusion.SetToolTipString(_(u"Vous pouvez modifier ici la conclusion du document"))

        # Bind
        self.ctrl_image_portrait.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDownPortrait)
        self.ctrl_image_paysage.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDownPaysage)
        
        # Init contrôle
        if dictOptions.has_key("titre") and dictOptions["titre"] != None : 
            self.ctrl_titre.SetValue(dictOptions["titre"])
        if dictOptions.has_key("introduction") and dictOptions["introduction"] != None : 
            self.ctrl_introduction.SetValue(dictOptions["introduction"])
        if dictOptions.has_key("conclusion") and dictOptions["conclusion"] != None : 
            self.ctrl_conclusion.SetValue(dictOptions["conclusion"])
        if dictOptions.has_key("orientation") and dictOptions["orientation"] != None : 
            self.SetOrientation(dictOptions["orientation"])
            
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=20)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(1)
        
        grid_sizer_haut = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Orientation
        box_orientation = wx.StaticBoxSizer(self.box_orientation_staticbox, wx.VERTICAL)
        grid_sizer_orientation = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_orientation.Add(self.ctrl_radio_portrait, 0, wx.EXPAND, 0)
        grid_sizer_orientation.Add(self.ctrl_image_portrait, 0, wx.EXPAND, 0)
        grid_sizer_orientation.Add(self.ctrl_radio_paysage, 0, wx.EXPAND, 0)
        grid_sizer_orientation.Add(self.ctrl_image_paysage, 0, wx.EXPAND, 0)
        box_orientation.Add(grid_sizer_orientation, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_haut.Add(box_orientation, 0, wx.EXPAND, 0)

        # Paramètres du document
        box_document = wx.StaticBoxSizer(self.box_document_staticbox, wx.VERTICAL)
        grid_sizer_document = wx.FlexGridSizer(rows=3, cols=2, vgap=2, hgap=10)
        grid_sizer_document.Add(self.label_titre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_document.Add(self.ctrl_titre, 0, wx.EXPAND, 0)
        grid_sizer_document.Add(self.label_introduction, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_document.Add(self.ctrl_introduction, 0, wx.EXPAND, 0)
        grid_sizer_document.Add(self.label_conclusion, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_document.Add(self.ctrl_conclusion, 0, wx.EXPAND, 0)
        grid_sizer_document.AddGrowableCol(1)
        box_document.Add(grid_sizer_document, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_haut.Add(box_document, 1, wx.EXPAND, 0)

        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND|wx.ALL, 0)

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
        grid_sizer_base.Add(box_options, 1, wx.EXPAND, 0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
    
    def OnLeftDownPortrait(self, event):
        self.ctrl_radio_portrait.SetValue(True)
        
    def OnLeftDownPaysage(self, event):
        self.ctrl_radio_paysage.SetValue(True)
        
    def MemoriserParametres(self):
        self.ctrl_parametres.Sauvegarde() 
    
    def SetOrientation(self, orientation=wx.PORTRAIT):
        if orientation == wx.PORTRAIT :
            self.ctrl_radio_portrait.SetValue(True)
        else :
            self.ctrl_radio_paysage.SetValue(True)
        
    def GetOrientation(self):
        if self.ctrl_radio_portrait.GetValue() == True :
            return wx.PORTRAIT
        else :
            return wx.LANDSCAPE
        
    def GetOptions(self):
        dictOptions = {} 
        
        # Orientation
        dictOptions["orientation"] = self.GetOrientation() 
        
        # Document
        dictOptions["titre"] = self.ctrl_titre.GetValue() 
        dictOptions["introduction"] = self.ctrl_introduction.GetValue() 
        dictOptions["conclusion"] = self.ctrl_conclusion.GetValue() 
        
        # Récupération des paramètres
        if self.ctrl_parametres.Validation() == False :
            return False
        for nom, valeur in self.ctrl_parametres.GetValeurs().iteritems()  :
            dictOptions[nom] = valeur

        return dictOptions


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, dictOptions={}):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   

        # Bandeau
        titre = _(u"Paramètres d'impression")
        intro = _(u"Vous pouvez ici modifier les paramètres d'impression par défaut des listes. Cliquez sur le bouton 'Mémoriser les paramètres' pour réutiliser les même paramètres pour toutes les autres impressions de listes.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Document_parametres.png")

        # Paramètres
        self.ctrl_parametres = CTRL(self, dictOptions=dictOptions)
                
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        self.bouton_ok.SetFocus() 

    def __set_properties(self):
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((550, 550))

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
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)        
        
    def OnBoutonOk(self, event): 
        dictOptions = self.ctrl_parametres.GetOptions() 
        if dictOptions == False :
            return        
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetOptions(self):
        return self.ctrl_parametres.GetOptions() 



if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
