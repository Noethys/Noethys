#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB



class CTRL_Compte(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
        self.SetSelection(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
    
    def GetListeDonnees(self):
        listeItems = [u"",]
        self.dictDonnees = { 0 : {"ID":None}, }
        DB = GestionDB.DB()
        req = """SELECT IDcompte, nom, numero
        FROM compta_comptes_comptables
        ORDER BY numero; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        index = 1
        for IDcompte, nom, numero in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcompte }
            label = u"%s%s  -  %s" % (" "*len(numero)*2, numero, nom)
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.items():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDcategorie=None, typeCategorie="credit"):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent   
        self.IDcategorie = IDcategorie
        self.typeCategorie = typeCategorie

        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.label_abrege = wx.StaticText(self, wx.ID_ANY, _(u"Abrégé :"))
        self.ctrl_abrege = wx.TextCtrl(self, wx.ID_ANY, u"")

        self.label_compte = wx.StaticText(self, wx.ID_ANY, _(u"Compte :"))
        self.ctrl_compte = CTRL_Compte(self)
        self.ctrl_compte.SetMinSize((400, -1))
        self.bouton_comptes = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        
        self.label_journal = wx.StaticText(self, wx.ID_ANY, _(u"Journal :"))
        self.ctrl_journal = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonComptes, self.bouton_comptes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        if self.IDcategorie != None :
            titre = _(u"Modification d'une catégorie")
            self.Importation() 
        else :
            titre = _(u"Saisie d'une catégorie")
        if self.typeCategorie == "credit" : titre += _(u" de crédit")
        if self.typeCategorie == "debit" : titre += _(u" de débit")
        self.SetTitle(titre)

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez le nom de la catégorie")))
        self.ctrl_abrege.SetToolTip(wx.ToolTip(_(u"Saisissez le nom abrégé de la catégorie")))
        self.ctrl_compte.SetToolTip(wx.ToolTip(_(u"Sélectionnez un compte comptable")))
        self.bouton_comptes.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des comptes comptables")))
        self.ctrl_journal.SetToolTip(wx.ToolTip(_(u"Saisissez le code du journal")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(5, 2, 10, 10)

        grid_sizer_haut.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_abrege, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_abrege, 0, 0, 0)


        grid_sizer_haut.Add(self.label_compte, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_compte = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_compte.Add(self.ctrl_compte, 0, wx.EXPAND, 0)
        grid_sizer_compte.Add(self.bouton_comptes, 0, 0, 0)
        grid_sizer_compte.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_compte, 1, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_journal, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_journal, 0, 0, 0)
        
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.ALL | wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonComptes(self, event):  
        IDmode = self.ctrl_compte.GetID()
        from Dlg import DLG_Comptes_comptables
        dlg = DLG_Comptes_comptables.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_compte.MAJ()
        self.ctrl_compte.SetID(IDmode)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Categoriescomptables")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        if self.Sauvegarde()  == False :
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def Sauvegarde(self):
        """ Sauvegarde des données """
        nom = self.ctrl_nom.GetValue() 
        abrege = self.ctrl_abrege.GetValue()
        IDcompte = self.ctrl_compte.GetID() 
        journal = self.ctrl_journal.GetValue() 
        
        # Validation des données saisies
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        if abrege == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le nom abrégé.\n\nSouhaitez-vous tout de même valider ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                self.ctrl_abrege.SetFocus()
                return False

        if IDcompte == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le compte comptable.\n\nSouhaitez-vous tout de même valider ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                self.ctrl_compte.SetFocus()
                return False

        if journal == "" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas renseigné le code journal.\n\nSouhaitez-vous tout de même valider ?"), _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                self.ctrl_journal.SetFocus()
                return False

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("nom", nom ),
            ("abrege", abrege ),
            ("IDcompte", IDcompte ),
            ("journal", journal),
            ("type", self.typeCategorie),
            ]
        if self.IDcategorie == None :
            self.IDcategorie = DB.ReqInsert("compta_categories", listeDonnees)
        else :
            DB.ReqMAJ("compta_categories", listeDonnees, "IDcategorie", self.IDcategorie)
        DB.Close()
        
        return True

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT nom, abrege, IDcompte, journal, type
        FROM compta_categories WHERE IDcategorie=%d;""" % self.IDcategorie
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        nom, abrege, IDcompte, journal, typeCategorie = listeTemp[0]
        if nom == None : nom = ""
        if abrege == None : abrege = ""
        if journal == None : journal = ""
        
        self.ctrl_nom.SetValue(nom)
        self.ctrl_abrege.SetValue(abrege)
        self.ctrl_compte.SetID(IDcompte)
        self.ctrl_journal.SetValue(journal)
        self.typeCategorie = typeCategorie
        
        
    def GetIDcategorie(self):
        return self.IDcategorie



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
