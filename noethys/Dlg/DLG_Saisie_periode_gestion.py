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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import GestionDB
from Utils import UTILS_Dates
import datetime
from Ctrl import CTRL_Saisie_date


LISTE_CATEGORIES = [
    ("consommations", _(u"Consommations")),
    ("prestations", _(u"Prestations")),
    ("factures", _(u"Factures")),
    ("reglements", _(u"Règlements")),
    ("depots", _(u"Dépôts de règlements")),
    ("cotisations", _(u"Cotisations")),
]


class CTRL_Categories(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.SetMinSize((-1, 60))
        self.MAJ() 
    
    def MAJ(self):
        index = 0
        self.dictDonnees = {}
        for code, label in LISTE_CATEGORIES :
            self.dictDonnees[index] = {"code" : code, "label" : label}
            self.Append(label)
            index += 1

    def GetCoches(self):
        listeIDcoches = []
        NbreItems = len(self.dictDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.dictDonnees[index]["code"])
        return listeIDcoches

    def SetCoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.dictDonnees)):
            ID = self.dictDonnees[index]["code"]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDperiode=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent 
        self.IDperiode = IDperiode
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_periode = wx.StaticText(self, wx.ID_ANY, _(u"Période :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.label_observations = wx.StaticText(self, wx.ID_ANY, _(u"Notes :"))
        self.ctrl_observations = wx.TextCtrl(self, wx.ID_ANY, u"", style=wx.TE_MULTILINE)
        self.ctrl_observations.SetMinSize((270, -1))
        
        # Verrouillage
        self.box_verrou_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Verrous"))
        self.ctrl_verrou = CTRL_Categories(self)
        self.ctrl_verrou.SetMinSize((50, 130))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Importation de l'opération
        if self.IDperiode != None :
            self.Importation()
            titre = _(u"Modification d'une période de gestion")
        else :
            titre = _(u"Saisie d'une période de gestion")
        self.SetTitle(titre)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de la période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de la période")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"Saisissez des observations")))
        self.ctrl_verrou.SetToolTip(wx.ToolTip(_(u"Cochez les éléments à verrouiller")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(5, 2, 10, 10)

        grid_sizer_generalites.Add(self.label_periode, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_periode = wx.FlexGridSizer(1, 4, 5, 5)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        
        grid_sizer_generalites.Add(self.label_observations, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        
        grid_sizer_generalites.AddGrowableCol(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # Verrou
        box_verrou = wx.StaticBoxSizer(self.box_verrou_staticbox, wx.VERTICAL)
        box_verrou.Add(self.ctrl_verrou, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_verrou, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize((self.GetSize()))
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Budgets")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        etat = self.Sauvegarde() 
        if etat == False :
            return
        self.EndModal(wx.ID_OK)
        
    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT date_debut, date_fin, observations,
        verrou_consommations, verrou_prestations, verrou_factures, verrou_reglements, verrou_depots, verrou_cotisations
        FROM periodes_gestion WHERE IDperiode=%d;""" % self.IDperiode
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        DB.Close()
        if len(listeTemp) == 0 : return
        date_debut, date_fin, observations, verrou_consommations, verrou_prestations, verrou_factures, verrou_reglements, verrou_depots, verrou_cotisations = listeTemp[0]
        date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
        date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)
        self.ctrl_observations.SetValue(observations)

        # Verrous
        liste_verrous = []
        if verrou_consommations == 1 : liste_verrous.append("consommations")
        if verrou_prestations == 1 : liste_verrous.append("prestations")
        if verrou_factures == 1 : liste_verrous.append("factures")
        if verrou_reglements == 1 : liste_verrous.append("reglements")
        if verrou_depots == 1 : liste_verrous.append("depots")
        if verrou_cotisations == 1 : liste_verrous.append("cotisations")
        self.ctrl_verrou.SetCoches(liste_verrous)

    def Sauvegarde(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        observations = self.ctrl_observations.GetValue()
        liste_verrous = self.ctrl_verrou.GetCoches()

        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin supérieure à la date de début de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        # Verrous
        verrou_consommations = int("consommations" in liste_verrous)
        verrou_prestations = int("prestations" in liste_verrous)
        verrou_factures = int("factures" in liste_verrous)
        verrou_reglements = int("reglements" in liste_verrous)
        verrou_depots = int("depots" in liste_verrous)
        verrou_cotisations = int("cotisations" in liste_verrous)

        # Sauvegarde de l'opération
        DB = GestionDB.DB()
        
        listeDonnees = [ 
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("observations", observations),
            ("verrou_consommations", verrou_consommations),
            ("verrou_prestations", verrou_prestations),
            ("verrou_factures", verrou_factures),
            ("verrou_reglements", verrou_reglements),
            ("verrou_depots", verrou_depots),
            ("verrou_cotisations", verrou_cotisations),
            ]
        if self.IDperiode == None :
            self.IDperiode = DB.ReqInsert("periodes_gestion", listeDonnees)
        else :
            DB.ReqMAJ("periodes_gestion", listeDonnees, "IDperiode", self.IDperiode)

        DB.Close()

        return True
    
    def GetIDperiode(self):
        return self.IDperiode
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDperiode=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
