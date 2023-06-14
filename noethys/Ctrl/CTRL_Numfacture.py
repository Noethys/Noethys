#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB


class CTRL(wx.SearchCtrl):
    def __init__(self, parent, size=(-1,20), IDfamille=None):
        wx.SearchCtrl.__init__(self, parent, size=size, style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.IDfamille = IDfamille
        self.IDutilisateurActif = None
        self.SetDescriptiveText(_(u"N° de facture"))
            
        # Options
        self.ShowSearchButton(True)
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Codebarre.png"), wx.BITMAP_TYPE_PNG))
        
        # Binds
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.Recherche)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.Recherche)
        self.Bind(wx.EVT_TEXT, self.OnText)
            
    def OnCancel(self, evt):
        self.SetValue("")

    def OnText(self, event):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        if len(txtSearch) > 6 and txtSearch.startswith("F") and "-" not in txtSearch:
            numFacture = txtSearch[1:]
            self.ReglerFacture(numFacture)
            self.SetValue("")

    def Recherche(self, event):
        numFacture = self.GetValue()
        # try :
        #     numFacture = int(txtSearch)
        # except :
        #     dlg = wx.MessageDialog(self, _(u"Ce numéro de facture n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
        #     dlg.ShowModal()
        #     dlg.Destroy()
        #     return
        self.ReglerFacture(numFacture)
    
    def ReglerFacture(self, numFacture=None):
        if self.IDfamille != None :
            texteSupp = _(u"pour cette famille ")
            conditionFamille = " AND comptes_payeurs.IDfamille=%d" % self.IDfamille
        else:
            texteSupp = u""
            conditionFamille = ""

        try :
            if "-" in numFacture :
                prefixe, numero = numFacture.split("-")
                numero = int(numero)
                conditionNumero = u"WHERE factures_prefixes.prefixe='%s' AND factures.numero=%d" % (prefixe, numero)
            else :
                numero = int(numFacture)
                conditionNumero = u"WHERE factures.numero=%d" % numero
        except :
            conditionNumero = None

        if conditionNumero == None :
            dlg = wx.MessageDialog(self, _(u"Ce numéro de facture ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        DB = GestionDB.DB()

##        # Récupération des totaux des prestations pour chaque facture
##        req = """
##        SELECT 
##        IDfacture, SUM(montant)
##        FROM prestations
##        WHERE IDfacture IS NOT NULL %s
##        GROUP BY IDfacture
##        ;""" % conditionFamille
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()     
##        dictPrestations = {}
##        for IDfacture, totalPrestations in listeDonnees :
##            if IDfacture != None :
##                dictPrestations[IDfacture] = totalPrestations

        # Recherche si le numéro de facture existe
        req = u"""
        SELECT 
        factures.IDfacture, factures.total, factures.regle, factures.solde,
        SUM(ventilation.montant), etat,
        comptes_payeurs.IDfamille
        FROM factures
        LEFT JOIN prestations ON prestations.IDfacture = factures.IDfacture
        LEFT JOIN ventilation ON prestations.IDprestation = ventilation.IDprestation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        LEFT JOIN factures_prefixes ON factures_prefixes.IDprefixe = factures.IDprefixe
        %s %s
        GROUP BY factures.IDfacture
        ;""" % (conditionNumero, conditionFamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        DB.Close() 
        # Si le numéro de facture n'existe pas
        if len(listeDonnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Ce numéro ne correspond à aucune facture existante %s!") % texteSupp, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        IDfacture, totalInitial, regleInitial, soldeInitial, regleActuel, etat, IDfamille = listeDonnees[0]
        if etat == "annulation" :
            dlg = wx.MessageDialog(self, _(u"La facture n°%s a été annulée !") % numFacture, _(u"Facture annulée"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Recherche si la facture a déjà été réglée
        
        DB = GestionDB.DB()
        req = """SELECT IDfacture, SUM(montant)
        FROM prestations
        WHERE IDfacture=%d
        GROUP BY IDfacture
        ;""" % IDfacture
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        if len(listeDonnees) > 0 :
            totalActuel = listeDonnees[0][1]
        else :
            totalActuel = 0.0
        DB.Close() 
        
        if totalActuel == None : totalActuel = 0.0 
        if regleActuel == None : regleActuel = 0.0 
        if totalActuel - regleActuel == 0.0 :
            dlg = wx.MessageDialog(self, _(u"La facture n°%s a déjà été réglée en intégralité !") % numFacture, _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Ouverture de la fiche famille
        if self.IDfamille != None :
            self.GetGrandParent().ReglerFacture() 
        else:
            from Dlg import DLG_Famille
            dlg = DLG_Famille.Dialog(self, IDfamille=IDfamille, AfficherMessagesOuverture=False)
            dlg.ReglerFacture(IDfacture)
            dlg.ShowModal() 
            dlg.Destroy()
        
        self.SetValue("")
        if self.GetParent().GetName() == "DLG_Regler_facture" :
            self.GetParent().Destroy() 
        



# ----------------- FRAME DE TEST ----------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel)
        self.myOlv2 = wx.TextCtrl(panel, -1, "test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 0, wx.ALL|wx.EXPAND, 10)
        sizer_2.Add(self.myOlv2, 0, wx.ALL|wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.SetSize((500, 150))
        self.Layout()
        self.CenterOnScreen()


# --------------------------- DLG de saisie de mot de passe ----------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, id=-1, title=_(u"Régler une facture"), IDfamille=None):
        wx.Dialog.__init__(self, parent, id, title, name="DLG_Regler_facture")
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.staticbox = wx.StaticBox(self, -1, "")

        self.label = wx.StaticText(self, -1, _(u"Veuillez saisir le numéro de la facture à régler ou\nscannez directement le code-barre sur la facture :"))
        self.ctrl_mdp = CTRL(self, IDfamille=self.IDfamille)
        
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.__set_properties()
        self.__do_layout()
        
    def __set_properties(self):
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.ctrl_mdp.SetMinSize((200, -1))

    def __do_layout(self):
        grid_sizer_2 = wx.FlexGridSizer(rows=3, cols=1, vgap=0, hgap=0)
        grid_sizer_4 = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        sizer_3 = wx.StaticBoxSizer(self.staticbox, wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_2.Add(self.label, 0, wx.ALL, 10)
        grid_sizer_3.Add(self.ctrl_mdp, 1, wx.EXPAND, 0)
        grid_sizer_3.AddGrowableCol(0)
        sizer_3.Add(grid_sizer_3, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_2.Add(sizer_3, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_4.Add((20, 20), 0, 0, 0)
        grid_sizer_4.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_4.AddGrowableCol(0)
        grid_sizer_2.Add(grid_sizer_4, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_2)
        grid_sizer_2.AddGrowableCol(0)
        grid_sizer_2.Fit(self)
        self.Layout()
        self.CentreOnScreen()



# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()


##if __name__ == '__main__':
##    app = wx.App(0)
##    #wx.InitAllImageHandlers()
##    frame_1 = MyFrame(None, -1, "GroupListView")
##    app.SetTopWindow(frame_1)
##    frame_1.Show()
##    app.MainLoop()
