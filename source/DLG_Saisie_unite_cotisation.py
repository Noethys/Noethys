#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import GestionDB

import CTRL_Saisie_date
import CTRL_Saisie_euros

try: import psyco; psyco.full()
except: pass



class Dialog(wx.Dialog):
    def __init__(self, parent, nomTypeCotisation=u"", dictDonnees={}):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Saisie_unite_cotisation", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDunite_cotisation = None
        self.defaut = 0
        self.nomTypeCotisation = nomTypeCotisation
        self.dictDonnees = dictDonnees
        
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, u"Nom de l'unité")
        self.label_nom = wx.StaticText(self, -1, u"Nom :")
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        # Dates validité
        self.staticbox_validite_staticbox = wx.StaticBox(self, -1, u"Dates de validité")
        self.label_date_debut = wx.StaticText(self, -1, u"Du", style=wx.ALIGN_RIGHT)
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, u"au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
                
        # Prestation
        self.staticbox_prestation_staticbox = wx.StaticBox(self, -1, u"Prestation")
        self.label_montant = wx.StaticText(self, -1, u"Montant :")
        self.ctrl_montant = CTRL_Saisie_euros.CTRL(self)
        self.label_label_prestation = wx.StaticText(self, -1, u"Label de la\nprestation :", style=wx.ALIGN_RIGHT)
        self.radio_label_defaut = wx.RadioButton(self, -1, u"Par défaut :", style=wx.RB_GROUP)
        self.ctrl_label_defaut = wx.StaticText(self, -1, u"")
        self.radio_label_personnalise = wx.RadioButton(self, -1, u"Personnalisé :")
        self.ctrl_label_personnalise = wx.TextCtrl(self, -1, u"")
        
        # Commandes
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, wx.ID_CANCEL, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.OnTextNom, self.ctrl_nom)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLabel, self.radio_label_defaut)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLabel, self.radio_label_personnalise)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        # Init contrôles
        if len(dictDonnees) == 0 :
            self.SetTitle(u"Saisie d'une nouvelle unité de cotisation")
            self.SetLabelPrestationDefaut() 
        else:
            self.SetTitle(u"Modification d'une unité de cotisation")
            self.Importation()
        self.OnRadioLabel(None) 

    def __set_properties(self):
        self.ctrl_label_defaut.SetForegroundColour((100, 100, 100))
        self.ctrl_nom.SetToolTipString(u"Saisissez ici le nom de l'unité")
        self.label_date_debut.SetMinSize((30, -1))
        self.ctrl_date_debut.SetToolTipString(u"Saisissez ici la date de début de validité")
        self.ctrl_date_fin.SetToolTipString(u"Saisissez ici la date de fin de validité")
        self.ctrl_montant.SetToolTipString(u"Saisissez ici le montant en euros de l'unité de cotisation")
        self.radio_label_defaut.SetToolTipString(u"Cochez cette case pour utiliser le label de prestation par défaut")
        self.radio_label_personnalise.SetToolTipString(u"Cochez cette case pour utiliser un label de prestation personnalisé")
        self.ctrl_label_personnalise.SetToolTipString(u"Saisissez ici un label personnalisé")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")
        self.SetMinSize((470, 360))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_prestation = wx.StaticBoxSizer(self.staticbox_prestation_staticbox, wx.VERTICAL)
        grid_sizer_prestation = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_label_prestation = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        staticbox_validite = wx.StaticBoxSizer(self.staticbox_validite_staticbox, wx.VERTICAL)
        grid_sizer_validite = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_validite.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_validite.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_validite.Add(self.ctrl_date_fin, 0, 0, 0)
        staticbox_validite.Add(grid_sizer_validite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_validite, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_prestation.Add(self.label_montant, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_prestation.Add(self.ctrl_montant, 0, 0, 0)
        grid_sizer_prestation.Add(self.label_label_prestation, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_label_prestation.Add(self.radio_label_defaut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_label_prestation.Add(self.ctrl_label_defaut, 0, wx.EXPAND, 0)
        grid_sizer_label_prestation.Add(self.radio_label_personnalise, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_label_prestation.Add(self.ctrl_label_personnalise, 0, wx.EXPAND, 0)
        grid_sizer_label_prestation.AddGrowableCol(1)
        grid_sizer_prestation.Add(grid_sizer_label_prestation, 1, wx.EXPAND, 0)
        grid_sizer_prestation.AddGrowableCol(1)
        staticbox_prestation.Add(grid_sizer_prestation, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_prestation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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

    def OnTextNom(self, event): 
        self.SetLabelPrestationDefaut()

    def OnRadioLabel(self, event): 
        if self.radio_label_defaut.GetValue() == True :
            self.ctrl_label_personnalise.Enable(False)
        else:
            self.ctrl_label_personnalise.Enable(True)
            self.ctrl_label_personnalise.SetFocus() 

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Cotisations")

    def OnBoutonOk(self, event):         
        # Récupération des données
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        nom  = self.ctrl_nom.GetValue()
        montant = self.ctrl_montant.GetMontant()
        if self.radio_label_defaut.GetValue() == True :
            label_prestation = None
        else:
            label_prestation = self.ctrl_label_personnalise.GetValue()
        
        # Vérification des données
        if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, u"La date de début de validité n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        
        if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, u"La date de fin de validité n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        
        if  date_debut > date_fin :
            dlg = wx.MessageDialog(self, u"La date de début de validité est supérieure à la date de fin !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if self.ctrl_nom.GetValue() == "" :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement saisir un nom pour cette unité de cotisation !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False
            
        montant = self.ctrl_montant.GetValue()
        try :
            montant = float(montant)
        except :
            dlg = wx.MessageDialog(self, u"Le montant que vous avez saisi n'est pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_montant.SetFocus()
            return False
        
        # Sauvegarde
        self.dictDonnees["IDunite_cotisation"] = self.IDunite_cotisation
        self.dictDonnees["date_debut"] = date_debut
        self.dictDonnees["date_fin"] = date_fin
        self.dictDonnees["defaut"] = self.defaut
        self.dictDonnees["nom"] = nom 
        self.dictDonnees["montant"] = montant
        self.dictDonnees["label_prestation"] = label_prestation
        self.dictDonnees["etat"] = "MODIF"
        
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDunite_cotisation(self):
        return self.IDunite_cotisation
    
    def GetDictDonnees(self):
        return self.dictDonnees
    
    def SetLabelPrestationDefaut(self):
        if self.radio_label_defaut.GetValue() == True :
            label = u"'%s - %s'" % (self.nomTypeCotisation, self.ctrl_nom.GetValue()) 
            self.ctrl_label_defaut.SetLabel(label)
    
    def Importation(self):
        self.IDunite_cotisation = self.dictDonnees["IDunite_cotisation"]
        date_debut = self.dictDonnees["date_debut"]
        date_fin = self.dictDonnees["date_fin"]
        self.defaut = self.dictDonnees["defaut"]
        nom = self.dictDonnees["nom"]
        montant = self.dictDonnees["montant"]
        label_prestation = self.dictDonnees["label_prestation"]
        
        if date_debut != None : self.ctrl_date_debut.SetDate(date_debut)
        if date_fin != None : self.ctrl_date_fin.SetDate(date_fin)
        
        self.ctrl_nom.SetValue(nom)
        self.ctrl_montant.SetMontant(montant)
        
        if label_prestation == None :
            self.radio_label_defaut.SetValue(True)
        else:
            self.radio_label_personnalise.SetValue(True)
            self.ctrl_label_personnalise.SetValue(label_prestation)


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
