#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_mail
import GestionDB

class CTRL_compte_bancaire(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.IDdefaut = None
        self.MAJ()

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
        self.SetID(0)
        #if self.IDdefaut != None :
        #    self.SetID(self.IDdefaut)

    def GetListeDonnees(self):
        self.dictDonnees = {}
        listeItems = [u"- - - - -",]
        db = GestionDB.DB()
        req = """SELECT IDcompte, nom
        FROM comptes_bancaires
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        self.dictDonnees[0] = { "ID" : 0 }
        index = 1
        for IDcompte, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcompte }
            listeItems.append(nom)
            #if defaut == 1 :
            #    self.IDdefaut = IDcompte
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

class Dialog(wx.Dialog):
    def __init__(self, parent, IDregie=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDregie = IDregie

        self.label_nom = wx.StaticText(self, wx.ID_ANY, _(u"Nom :"))
        self.ctrl_nom = wx.TextCtrl(self, wx.ID_ANY, u"")
        
        self.label_numclitipi = wx.StaticText(self, wx.ID_ANY, _(u"Numéro Client TIPI :"))
        self.ctrl_numclitipi = wx.TextCtrl(self, wx.ID_ANY, u"")

        self.label_emailregisseur = wx.StaticText(self, wx.ID_ANY, _(u"Mail du régisseur :"))
        self.ctrl_emailregisseur = CTRL_Saisie_mail.Mail(self)

        self.label_compte_bancaire = wx.StaticText(self, wx.ID_ANY, _(u"Compte bancaire associé :"))
        self.ctrl_compte_bancaire = CTRL_compte_bancaire(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init contrôles
        if self.IDregie != None :
            self.SetTitle(_(u"Modification d'une régie de facturation"))
            self.Importation() 
        else :
            self.SetTitle(_(u"Saisie d'une régie de facturation"))

    def __set_properties(self):
        self.ctrl_nom.SetToolTip(wx.ToolTip(_(u"Saisissez le nom de la régie")))
        self.ctrl_numclitipi.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro de client TIPI")))
        self.ctrl_emailregisseur.SetToolTip(wx.ToolTip(_(u"Saisissez l addresse mail du régisseur")))
        self.ctrl_compte_bancaire.SetToolTip(wx.ToolTip(_(u"Sélectionnez le compte bancaire associé a cette régie")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        
        grid_sizer_haut = wx.FlexGridSizer(5, 2, 10, 10)

        grid_sizer_haut.Add(self.label_nom, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_nom, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_numclitipi, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_numclitipi, 0, 0, 0)

        grid_sizer_haut.Add(self.label_emailregisseur, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_emailregisseur, 0, wx.EXPAND, 0)

        grid_sizer_haut.Add(self.label_compte_bancaire, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_haut.Add(self.ctrl_compte_bancaire, 0, wx.EXPAND, 0)

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

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

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
        numclitipi = self.ctrl_numclitipi.GetValue()
        emailregisseur = self.ctrl_emailregisseur.GetValue()
        IDcompte_bancaire = self.ctrl_compte_bancaire.GetID()
        
        # Validation des données saisies
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return False

        #if numclitipi == "" :
        #    dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un numéro de client TIPI!"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
        #    dlg.ShowModal()
        #    dlg.Destroy()
        #    self.ctrl_numclitipi.SetFocus()
        #    return False

        for caract in numclitipi :
            if caract not in "0123456789" :
                dlg = wx.MessageDialog(self, _(u"Le numéro de client TIPI ne peut comporter que des chiffres !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_numclitipi.SetFocus()
                return False

        if numclitipi != "" and emailregisseur == "":
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir l addresse mail du régisseur si vous avez saisi un numéro de client TIPI !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_emailregisseur.SetFocus()
            return False

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("nom", nom),
            ("numclitipi", numclitipi),
            ("email_regisseur", emailregisseur),
            ("IDcompte_bancaire", IDcompte_bancaire),
            ]
        if self.IDregie == None :
            self.IDregie = DB.ReqInsert("factures_regies", listeDonnees)
        else :
            DB.ReqMAJ("factures_regies", listeDonnees, "IDregie", self.IDregie)
        DB.Close()

    def Importation(self):
        """ Importation des valeurs """
        DB = GestionDB.DB()
        req = """SELECT nom, numclitipi, COUNT(factures.IDregie), email_regisseur, IDcompte_bancaire
        FROM factures_regies
        LEFT JOIN factures ON factures.IDregie = factures_regies.IDregie
        WHERE factures_regies.IDregie=%d
        GROUP BY factures_regies.IDregie;""" % self.IDregie
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        nom, numclitipi, nbre_factures, email_regisseur, IDcompte_bancaire = listeTemp[0]
        if nom == None : nom = ""
        if numclitipi == None : numclitipi = ""
        if email_regisseur == None: email_regisseur = ""
        
        self.ctrl_nom.SetValue(nom)
        self.ctrl_numclitipi.SetValue(numclitipi)
        self.ctrl_emailregisseur.SetValue(email_regisseur)
        self.ctrl_compte_bancaire.SetID(IDcompte_bancaire)
        if nbre_factures > 0 :
            self.ctrl_nom.Enable(False)

    def GetIDregie(self):
        return self.IDregie



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
