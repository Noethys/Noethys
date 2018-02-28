#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
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
# if 'phoenix' in wx.PlatformInfo:
#     from wx.adv import BitmapComboBox
# else :
#     from wx.combo import BitmapComboBox
from Ctrl import CTRL_Saisie_date
import GestionDB


# LISTE_TYPES = [
#     (1, _(u"Maladie"), "Medical.png"),
#     (2, _(u"Alimentation"), "Medical.png"),
#     (3, _(u"Médicamentation"), "Medicament.png"),
#     (4, _(u"Allergie"), "Medical.png"),
#     (5, _(u"Accident"), "Pansement.png"),
#     (6, _(u"Hospitalisation"), "Hopital.png"),
#     (7, _(u"Opération"), "Stethoscope.png"),
#     (8, _(u"Autre"), "Medical.png"),
#     ]



# class MyBitmapComboBox(BitmapComboBox):
#     def __init__(self, parent, listeImages=[], size=(-1,  -1) ):
#         BitmapComboBox.__init__(self, parent, size=size, style=wx.CB_READONLY)
#         self.dictID = {}
#
#     def Remplissage(self, listeDonnees=[]):
#         # listeDonnees = [ ID, texte, CheminImage]
#         self.dictID = {}
#         index = 0
#         for ID, texte, nomImage in listeDonnees :
#             img = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/%s" % nomImage), wx.BITMAP_TYPE_ANY)
#             self.Append(texte, img, texte)
#             self.dictID[index] = ID
#             index += 1
#         # Sélection par défaut
#         self.Select(0)
#
#     def GetIDselection(self):
#         index = self.GetSelection()
#         return self.dictID[index]
#
#     def SetIDselection(self, ID):
#         for index, IDtmp, in self.dictID.iteritems():
#             if ID == IDtmp :
#                 self.Select(index)
#                 return


class CTRL_Categorie(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(170, -1))
        self.parent = parent
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 1:
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDcategorie, nom
        FROM categories_medicales
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDcategorie, nom in listeDonnees:
            self.dictDonnees[index] = {"ID": IDcategorie, "nom ": nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None:
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID:
                self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0: return None
        return self.dictDonnees[index]["ID"]


# ---------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDindividu=None, IDprobleme=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDprobleme = IDprobleme
                
        # Caractéristiques
        self.staticbox_gauche_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))
        self.label_categorie = wx.StaticText(self, -1, _(u"Catégorie :"))
        self.ctrl_categorie = CTRL_Categorie(self)
        self.bouton_categories = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        #self.ctrl_categorie = MyBitmapComboBox(self)
        #self.ctrl_categorie.Remplissage(LISTE_TYPES)

        self.label_intitule = wx.StaticText(self, -1, _(u"Intitulé :"))
        self.ctrl_intitule = wx.TextCtrl(self, -1, u"")
        self.label_periode = wx.StaticText(self, -1, _(u"Période :"))
        self.radio_indefinie = wx.RadioButton(self, -1, _(u"Indéfinie"), style = wx.RB_GROUP)
        self.radio_definie = wx.RadioButton(self, -1, u"")
        self.label_periode_du = wx.StaticText(self, -1, u"Du")
        self.ctrl_periode_debut = CTRL_Saisie_date.Date(self)
        self.label_periode_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_periode_fin = CTRL_Saisie_date.Date(self)
        self.label_description = wx.StaticText(self, -1, _(u"Description :"))
        self.ctrl_description = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Traitement
        self.staticbox_traitement_staticbox = wx.StaticBox(self, -1, _(u"Traitement médical"))
        self.ctrl_coche_traitement = wx.CheckBox(self, -1, _(u"Traitement médical"))
        self.ctrl_description_traitement = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        self.ctrl_description_traitement.SetMinSize((-1, 60))
        self.label_traitement_du = wx.StaticText(self, -1, u"Du")
        self.ctrl_traitement_debut = CTRL_Saisie_date.Date(self)
        self.label_traitement_periode_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_traitement_fin = CTRL_Saisie_date.Date(self)
        
        # Eviction
        self.staticbox_eviction_staticbox = wx.StaticBox(self, -1, _(u"Eviction de l'activité"))
        self.ctrl_coche_eviction = wx.CheckBox(self, -1, _(u"Eviction de l'activité"))
        self.label_eviction_du = wx.StaticText(self, -1, u"Du")
        self.ctrl_eviction_debut = CTRL_Saisie_date.Date(self)
        self.label_eviction_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_eviction_fin = CTRL_Saisie_date.Date(self)
        
        # Diffusion de l'info
        self.staticbox_diffusion_staticbox = wx.StaticBox(self, -1, _(u"Diffusion de l'information"))
        self.ctrl_listing_enfants = wx.CheckBox(self, -1, _(u"Afficher sur le listing des informations médicales"))
        self.ctrl_listing_presences = wx.CheckBox(self, -1, _(u"Afficher sur le listing des consommations"))
        self.ctrl_listing_repas = wx.CheckBox(self, -1, _(u"Afficher sur la commande des repas"))
        
        # Commandes générales
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio_periode, self.radio_indefinie)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio_periode, self.radio_definie)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck_traitement, self.ctrl_coche_traitement)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck_eviction, self.ctrl_coche_eviction)
        self.Bind(wx.EVT_BUTTON, self.OnBouton_ok, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategories, self.bouton_categories)

        # Importation des données
        if self.IDprobleme != None :
            self.Importation() 
            
        # Initialisation des contrôles
        self.OnRadio_periode(None)
        self.OnCheck_traitement(None)
        self.OnCheck_eviction(None)
        
        self.ctrl_intitule.SetFocus() 

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une information médicale"))
        self.ctrl_categorie.SetToolTip(wx.ToolTip(_(u"Selectionnez une catégorie médicale")))
        self.bouton_categories.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder au paramétrage des catégories médicales")))
        self.ctrl_intitule.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, u""))
        self.ctrl_intitule.SetToolTip(wx.ToolTip(_(u"Saisissez l'intitule de l'information")))
        self.radio_indefinie.SetToolTip(wx.ToolTip(_(u"Sans période définie")))
        self.radio_definie.SetToolTip(wx.ToolTip(_(u"Définir une période")))
        self.ctrl_periode_debut.SetToolTip(wx.ToolTip(_(u"Saisissez une date de début")))
        self.ctrl_periode_fin.SetToolTip(wx.ToolTip(_(u"Saisissez une date de fin")))
        self.ctrl_description.SetToolTip(wx.ToolTip(_(u"Saisissez une description pour le problème de santé")))
        self.ctrl_coche_traitement.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour saisir un traitement médical")))
        self.ctrl_description_traitement.SetToolTip(wx.ToolTip(_(u"Saisissez ici le détail du traitement médical")))
        self.ctrl_traitement_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de debut du traitement")))
        self.ctrl_traitement_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de traitement")))
        self.ctrl_coche_eviction.SetToolTip(wx.ToolTip(_(u"Cochez cette case si cette information médicale nécessite une éviction de l'activité")))
        self.ctrl_eviction_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de début de l'éviction")))
        self.ctrl_eviction_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de la periode d'éviction")))
        self.ctrl_listing_enfants.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour diffuser l'information sur le listing enfants")))
        self.ctrl_listing_presences.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour diffuser l'information sur le listing des consommations")))
        self.ctrl_listing_repas.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour diffuser l'information sur la commande des repas")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider la saisie")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_droit = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        staticbox_diffusion = wx.StaticBoxSizer(self.staticbox_diffusion_staticbox, wx.VERTICAL)
        grid_sizer_diffusion = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        staticbox_eviction = wx.StaticBoxSizer(self.staticbox_eviction_staticbox, wx.VERTICAL)
        grid_sizer_eviction = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        staticbox_traitement = wx.StaticBoxSizer(self.staticbox_traitement_staticbox, wx.VERTICAL)
        grid_sizer_traitement = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_periode_traitement = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        staticbox_gauche = wx.StaticBoxSizer(self.staticbox_gauche_staticbox, wx.VERTICAL)
        grid_sizer_caract = wx.FlexGridSizer(rows=5, cols=2, vgap=5, hgap=5)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=5, vgap=5, hgap=5)
        grid_sizer_caract.Add(self.label_categorie, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_type = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_type.Add(self.ctrl_categorie, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 0)
        grid_sizer_type.Add(self.bouton_categories, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_type.AddGrowableCol(0)

        grid_sizer_caract.Add(grid_sizer_type, 0, wx.EXPAND|wx.BOTTOM, 5)

        grid_sizer_caract.Add(self.label_intitule, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.ctrl_intitule, 0, wx.EXPAND|wx.BOTTOM, 10)
        grid_sizer_caract.Add(self.label_periode, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.radio_indefinie, 0, 0, 0)
        grid_sizer_caract.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.radio_definie, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer_periode.Add(self.label_periode_du, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_periode_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_periode_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_periode_fin, 0, 0, 0)
        grid_sizer_caract.Add(grid_sizer_periode, 1, wx.EXPAND|wx.BOTTOM, 10)
        grid_sizer_caract.Add(self.label_description, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_caract.Add(self.ctrl_description, 0, wx.EXPAND, 0)
        grid_sizer_caract.AddGrowableRow(4)
        grid_sizer_caract.AddGrowableCol(1)
        staticbox_gauche.Add(grid_sizer_caract, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(staticbox_gauche, 1, wx.EXPAND, 0)
        grid_sizer_traitement.Add(self.ctrl_coche_traitement, 0, wx.BOTTOM, 5)
        grid_sizer_traitement.Add(self.ctrl_description_traitement, 0, wx.LEFT|wx.EXPAND, 20)
        grid_sizer_periode_traitement.Add(self.label_traitement_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode_traitement.Add(self.ctrl_traitement_debut, 0, 0, 0)
        grid_sizer_periode_traitement.Add(self.label_traitement_periode_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode_traitement.Add(self.ctrl_traitement_fin, 0, 0, 0)
        grid_sizer_traitement.Add(grid_sizer_periode_traitement, 1, wx.LEFT|wx.EXPAND, 20)
        staticbox_traitement.Add(grid_sizer_traitement, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(staticbox_traitement, 1, wx.EXPAND, 0)
        staticbox_eviction.Add(self.ctrl_coche_eviction, 0, wx.LEFT|wx.RIGHT|wx.TOP, 10)
        grid_sizer_eviction.Add(self.label_eviction_du, 0, wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 20)
        grid_sizer_eviction.Add(self.ctrl_eviction_debut, 0, 0, 0)
        grid_sizer_eviction.Add(self.label_eviction_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_eviction.Add(self.ctrl_eviction_fin, 0, 0, 0)
        staticbox_eviction.Add(grid_sizer_eviction, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(staticbox_eviction, 1, wx.EXPAND, 0)
        grid_sizer_diffusion.Add(self.ctrl_listing_enfants, 0, 0, 0)
        grid_sizer_diffusion.Add(self.ctrl_listing_presences, 0, 0, 0)
        grid_sizer_diffusion.Add(self.ctrl_listing_repas, 0, 0, 0)
        staticbox_diffusion.Add(grid_sizer_diffusion, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(staticbox_diffusion, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()
    
    def OnRadio_periode(self, event):
        if self.radio_definie.GetValue() == True : etat = True
        else: etat = False
        self.label_periode_du.Enable(etat)
        self.label_periode_au.Enable(etat)
        self.ctrl_periode_debut.Enable(etat)
        self.ctrl_periode_fin.Enable(etat)
        
    def OnCheck_traitement(self, event):
        if self.ctrl_coche_traitement.GetValue() == True : etat = True
        else : etat = False
        self.ctrl_description_traitement.Enable(etat)
        self.ctrl_traitement_debut.Enable(etat)
        self.ctrl_traitement_fin.Enable(etat)
        self.label_traitement_du.Enable(etat)
        self.label_traitement_periode_au.Enable(etat)
        
    def OnCheck_eviction(self, event):
        if self.ctrl_coche_eviction.GetValue() == True : etat = True
        else : etat = False
        self.label_eviction_du.Enable(etat)
        self.label_eviction_au.Enable(etat)
        self.ctrl_eviction_debut.Enable(etat)
        self.ctrl_eviction_fin.Enable(etat)

    def OnBoutonCategories(self, event):
        IDcategorie = self.ctrl_categorie.GetID()
        from Dlg import DLG_Categories_medicales
        dlg = DLG_Categories_medicales.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_categorie.MAJ()
        self.ctrl_categorie.SetID(IDcategorie)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Mdical")

    def OnBouton_ok(self, event):
        etat = self.Sauvegarde() 
        if etat == False :
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetIDprobleme(self):
        return self.IDprobleme
    
    def Importation(self):
        """ Importation des valeurs """
        listeChamps = [
        "IDtype", "intitule", "date_debut", "date_fin", "description",
        "traitement_medical", "description_traitement", "date_debut_traitement", "date_fin_traitement",
        "eviction", "date_debut_eviction", "date_fin_eviction", 
        "diffusion_listing_enfants", "diffusion_listing_conso", "diffusion_listing_repas"]
        db = GestionDB.DB()
        req = """
        SELECT %s
        FROM problemes_sante
        WHERE IDprobleme=%d
        """ % (", ".join(listeChamps), self.IDprobleme)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictDonnees = {}
        for valeurs in listeDonnees :
            index = 0
            for valeur in valeurs :
                dictDonnees[listeChamps[index]] = valeur
                index += 1
        
        # Caractéristiques
        self.ctrl_categorie.SetID(dictDonnees["IDtype"])
        self.ctrl_intitule.SetValue(dictDonnees["intitule"])
        if dictDonnees["date_debut"] == "1900-01-01" and dictDonnees["date_fin"] == "2999-01-01" :
            self.radio_indefinie.SetValue(True)
        else:
            self.radio_definie.SetValue(True)
            self.ctrl_periode_debut.SetDate(dictDonnees["date_debut"])
            self.ctrl_periode_fin.SetDate(dictDonnees["date_fin"])
        self.ctrl_description.SetValue(dictDonnees["description"])
        
        # Traitement
        self.ctrl_coche_traitement.SetValue(dictDonnees["traitement_medical"])
        if dictDonnees["traitement_medical"] == 1 :
            self.ctrl_description_traitement.SetValue(dictDonnees["description_traitement"])
            self.ctrl_traitement_debut.SetDate(dictDonnees["date_debut_traitement"]) 
            self.ctrl_traitement_fin.SetDate(dictDonnees["date_fin_traitement"]) 
        
        # Eviction
        self.ctrl_coche_eviction.SetValue(dictDonnees["eviction"])
        if dictDonnees["eviction"] == 1 :
            self.ctrl_eviction_debut.SetDate(dictDonnees["date_debut_eviction"]) 
            self.ctrl_eviction_fin.SetDate(dictDonnees["date_fin_eviction"]) 
        
        # Diffusion
        self.ctrl_listing_enfants.SetValue(dictDonnees["diffusion_listing_enfants"])
        self.ctrl_listing_presences.SetValue(dictDonnees["diffusion_listing_conso"])
        self.ctrl_listing_repas.SetValue(dictDonnees["diffusion_listing_repas"])
        
            
        
    def Sauvegarde(self):
        # Caractéristiques
        IDtype = self.ctrl_categorie.GetID()
        intitule = self.ctrl_intitule.GetValue()
        if self.radio_indefinie.GetValue() == True :
            date_debut = "1900-01-01"
            date_fin = "2999-01-01"
        else:
            date_debut = self.ctrl_periode_debut.GetDate()
            date_fin = self.ctrl_periode_fin.GetDate()
        description = self.ctrl_description.GetValue()
        
        if intitule == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un intitulé"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_intitule.SetFocus()
            return False
        if self.radio_definie.GetValue() == True : 
            if date_debut == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_periode_debut.SetFocus()
                return False
            if date_fin == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_periode_fin.SetFocus()
                return False
        
        # Traitement
        traitement_medical = int(self.ctrl_coche_traitement.GetValue()) 
        if traitement_medical == 1 :
            description_traitement = self.ctrl_description_traitement.GetValue()
            date_debut_traitement = self.ctrl_traitement_debut.GetDate() 
            date_fin_traitement = self.ctrl_traitement_fin.GetDate() 
        else:
            description_traitement = None
            date_debut_traitement = None
            date_fin_traitement = None
        
        if description_traitement == 1 : 
            if description_traitement == "" :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir le détail du traitement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_description_traitement.SetFocus()
                return False
            if date_debut_traitement == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début pour le traitement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_traitement_debut.SetFocus()
                return False
            if date_fin_traitement == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin pour le traitement !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_traitement_fin.SetFocus()
                return False

        # Eviction
        eviction = int(self.ctrl_coche_eviction.GetValue()) 
        if eviction == 1 :
            date_debut_eviction = self.ctrl_eviction_debut.GetDate() 
            date_fin_eviction = self.ctrl_eviction_fin.GetDate() 
        else:
            date_debut_eviction = None
            date_fin_eviction = None
        
        if eviction == 1 : 
            if date_debut_eviction == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début pour l'éviction !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_eviction_debut.SetFocus()
                return False
            if date_fin_eviction == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin pour l'éviction !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_eviction_fin.SetFocus()
                return False
            
        # Diffusion
        diffusion_listing_enfants = int(self.ctrl_listing_enfants.GetValue())
        diffusion_listing_conso = int(self.ctrl_listing_presences.GetValue())
        diffusion_listing_repas = int(self.ctrl_listing_repas.GetValue())

        # Enregistrement
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("IDindividu", self.IDindividu ),
            ("IDtype", IDtype ),
            ("intitule", intitule ),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("description", description),
            
            ("traitement_medical", traitement_medical),
            ("description_traitement", description_traitement),
            ("date_debut_traitement", date_debut_traitement),
            ("date_fin_traitement", date_fin_traitement),
            
            ("eviction", eviction),
            ("date_debut_eviction", date_debut_eviction),
            ("date_fin_eviction", date_fin_eviction),
            
            ("diffusion_listing_enfants", diffusion_listing_enfants),
            ("diffusion_listing_conso", diffusion_listing_conso),
            ("diffusion_listing_repas", diffusion_listing_repas),
            ]
        
        if self.IDprobleme == None :
            self.IDprobleme = DB.ReqInsert("problemes_sante", listeDonnees)
        else:
            DB.ReqMAJ("problemes_sante", listeDonnees, "IDprobleme", self.IDprobleme)
        DB.Close()
        
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDindividu=27, IDprobleme=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
