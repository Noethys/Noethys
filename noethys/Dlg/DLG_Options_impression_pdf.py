#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Utils import UTILS_Parametres
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Propertygrid
import wx.propgrid as wxpg
import copy



class CTRL_Parametres(CTRL_Propertygrid.CTRL) :
    def __init__(self, parent, categorie=""):
        self.categorie = categorie
        CTRL_Propertygrid.CTRL.__init__(self, parent)

    
    def Remplissage(self):
        # --------------------------- TYPE DE DOCUMENT------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Type de document")) )
    
        # Type
        propriete = wxpg.EnumProperty(label=_(u"Type"), name="type_document", labels=[_(u"Détaillé"), _(u"Simplifié"), _(u"Totaux")], values=[0, 1, 2], value=0)
        propriete.SetHelpString(_(u"Sélectionnez un type de document")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- COULEURS DE FOND ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Couleurs de fond")) )

        # Couleur 3
        propriete = wxpg.ColourProperty(label=_(u"Fond ligne entêtes"), name="couleur_fond_3", value=wx.Colour(230, 230, 255))
        propriete.SetHelpString(_(u"Sélectionnez une couleur"))
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur 1
        propriete = wxpg.ColourProperty(label=_(u"Fond ligne dépôt"), name="couleur_fond_1", value=wx.Colour(204, 204, 255))
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # Couleur 2
        propriete = wxpg.ColourProperty(label=_(u"Fond ligne total"), name="couleur_fond_2", value=wx.Colour(230, 230, 255))
        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- TITRE ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Titre")) )

        # Texte
        propriete = wxpg.StringProperty(label=_(u"Texte"), name="titre_texte", value=_(u"Récapitulatif des factures"))
        propriete.SetHelpString(_(u"Saisissez un texte"))
        self.Append(propriete)

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="titre_taille_texte", value=16)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (16 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("titre_taille_texte", "SpinCtrl")
        
        # Couleur
##        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="titre_couleur", value=wx.BLACK)
##        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="titre_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"Sélectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)

        # --------------------------- INTRODUCTION ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Introduction")) )

        # Texte
        propriete = wxpg.StringProperty(label=_(u"Texte"), name="intro_texte", value=u"")
        propriete.SetHelpString(_(u"Saisissez un texte"))
        self.Append(propriete)

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="intro_taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("intro_taille_texte", "SpinCtrl")

        # Style
##        labels = [_(u"Normal"), _(u"Light"), "Gras"]
##        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
##        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="intro_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_NORMAL)
##        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)
        
        # Couleur
##        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="intro_couleur", value=wx.BLACK)
##        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)

        # Alignement
        labels = [_(u"Gauche"), _(u"Centre"), _(u"Droite")]
        propriete = wxpg.EnumProperty(label=_(u"Alignement du texte"), name="intro_alignement", labels=labels, values=[wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_RIGHT] , value=wx.ALIGN_LEFT)
        propriete.SetHelpString(_(u"Sélectionnez le type d'alignement")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)


        # --------------------------- CONCLUSION ------------------------------------------
        self.Append( wxpg.PropertyCategory(_(u"Conclusion")) )

        # Texte
        propriete = wxpg.StringProperty(label=_(u"Texte"), name="conclusion_texte", value=_(u"{NBRE_FACTURES} factures | Montant total : {TOTAL_FACTURES}"))
        propriete.SetHelpString(_(u"Saisissez un texte. Vous pouvez utiliser les mots-clés suivants : {NBRE_FACTURES}, {TOTAL_FACTURES}, {NBRE_FACT_PRELEV}, {TOTAL_FACT_PRELEV}"))
        self.Append(propriete)

        # Taille police
        propriete = wxpg.IntProperty(label=_(u"Taille de texte"), name="conclusion_taille_texte", value=7)
        propriete.SetHelpString(_(u"Saisissez une taille de texte (7 par défaut)")) 
        propriete.SetAttribute("obligatoire", True)
        self.Append(propriete)
        self.SetPropertyEditor("conclusion_taille_texte", "SpinCtrl")

        # Style
##        labels = [_(u"Normal"), _(u"Light"), "Gras"]
##        valeurs = [wx.FONTWEIGHT_NORMAL, wx.FONTWEIGHT_LIGHT, wx.FONTWEIGHT_BOLD]
##        propriete = wxpg.EnumProperty(label=_(u"Style de texte"), name="conclusion_style", labels=labels, values=valeurs, value=wx.FONTWEIGHT_BOLD)
##        propriete.SetHelpString(_(u"Sélectionnez un style de texte")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)
        
        # Couleur
##        propriete = wxpg.ColourProperty(label=_(u"Couleur de texte"), name="conclusion_couleur", value=wx.BLACK)
##        propriete.SetHelpString(_(u"Sélectionnez une couleur")) 
##        propriete.SetAttribute("obligatoire", True)
##        self.Append(propriete)

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


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(wx.Panel):
    def __init__(self, parent, categorie="", ctrl=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.categorie = categorie
        
        # Paramètres généraux
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options d'impression"))
        if ctrl == None :
            self.ctrl_parametres = CTRL_Parametres(self, categorie=categorie)
        else :
            self.ctrl_parametres = ctrl(self)
        self.ctrl_parametres.Importation() 
        self.bouton_reinitialisation = CTRL_Propertygrid.Bouton_reinitialisation(self, self.ctrl_parametres)
        self.bouton_sauvegarde = CTRL_Propertygrid.Bouton_sauvegarde(self, self.ctrl_parametres)
        self.ctrl_parametres.SetMinSize((50, 50)) 
        
        self.__do_layout()
                    
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=20)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.AddGrowableRow(0)

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
            
    def MemoriserParametres(self):
        self.ctrl_parametres.Sauvegarde() 
            
    def GetOptions(self):
        dictOptions = {} 
        
        # Récupération des paramètres
        if self.ctrl_parametres.Validation() == False :
            return False
        for nom, valeur in self.ctrl_parametres.GetValeurs().iteritems()  :
            dictOptions[nom] = valeur

        return dictOptions


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, categorie="", ctrl=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.categorie = categorie

        # Bandeau
        titre = _(u"Options d'impression")
        intro = _(u"Vous pouvez ici modifier les paramètres d'impression du document. Cliquez sur le bouton 'Mémoriser les paramètres' pour réutiliser les mêmes paramètres pour les impressions suivantes.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Imprimante.png")


        # Paramètres
        self.ctrl_parametres = CTRL(self, categorie=categorie, ctrl=ctrl)
                
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
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((520, 520))

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
        
    def GetOptions(self):
        return self.ctrl_parametres.GetOptions() 

    def OnBoutonOk(self, event):
        dictOptions = self.ctrl_parametres.GetOptions()
        if dictOptions == False :
            return        
        self.EndModal(wx.ID_OK)



if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
