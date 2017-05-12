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
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_euros

import GestionDB



class CTRL_Type_quotient(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(150, -1))
        self.parent = parent
        self.MAJ()
        self.Select(0)

    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)

    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDtype_quotient, nom
        FROM types_quotients
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDtype_quotient, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDtype_quotient, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]


# -----------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   
        
        # Dates
        self.staticbox_dates_staticbox = wx.StaticBox(self, -1, _(u"Dates de validité"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Paramètres
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres"))

        self.label_type_quotient = wx.StaticText(self, -1, _(u"Type de quotient :"))
        self.ctrl_type_quotient = CTRL_Type_quotient(self)
        self.ctrl_type_quotient.SetMinSize((140, -1))
        self.bouton_types_quotients = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))

        self.label_quotient = wx.StaticText(self, -1, _(u"Quotient familial :"))
        self.ctrl_quotient = wx.TextCtrl(self, -1, u"")

        self.label_revenu = wx.StaticText(self, -1, _(u"Revenu :"))
        self.ctrl_revenu = CTRL_Saisie_euros.CTRL(self)

        self.label_observations = wx.StaticText(self, -1, _(u"Observations :"))
        self.ctrl_observations = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonTypesQuotients, self.bouton_types_quotients)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de début de validité")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici la date de fin de validité")))
        self.ctrl_type_quotient.SetToolTip(wx.ToolTip(_(u"Sélectionnez un type de quotient")))
        self.bouton_types_quotients.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des types de quotients")))
        self.ctrl_quotient.SetToolTip(wx.ToolTip(_(u"Saisissez ici le quotient familial")))
        self.ctrl_revenu.SetToolTip(wx.ToolTip(_(u"Saisissez ici le revenu")))
        self.ctrl_observations.SetToolTip(wx.ToolTip(_(u"[Optionnel] Saisissez ici des commentaires sur ce quotient/revenu")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)

        staticbox_dates = wx.StaticBoxSizer(self.staticbox_dates_staticbox, wx.VERTICAL)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_dates.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        staticbox_dates.Add(grid_sizer_dates, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_dates, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_parametres = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)

        grid_sizer_parametres.Add(self.label_type_quotient, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_type_quotient = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_type_quotient.Add(self.ctrl_type_quotient, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_type_quotient.Add(self.bouton_types_quotients, 0, 0, 0)
        grid_sizer_type_quotient.AddGrowableCol(0)
        grid_sizer_parametres.Add(grid_sizer_type_quotient, 1, wx.ALL|wx.EXPAND, 0)

        grid_sizer_parametres.Add(self.label_quotient, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_quotient, 0, 0, 0)
        grid_sizer_parametres.Add(self.label_revenu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_revenu, 0, 0, 0)
        grid_sizer_parametres.Add(self.label_observations, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_parametres.Add(self.ctrl_observations, 0, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableRow(3)
        grid_sizer_parametres.AddGrowableCol(1)
        staticbox_parametres.Add(grid_sizer_parametres, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_base.Add(staticbox_parametres, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        self.SetMinSize((self.GetSize()))
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonTypesQuotients(self, event):
        IDtype_quotient = self.ctrl_type_quotient.GetID()
        import DLG_Types_quotients
        dlg = DLG_Types_quotients.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_type_quotient.MAJ()
        self.ctrl_type_quotient.SetID(IDtype_quotient)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Quotientsfamiliaux")
    
    def SetDateDebut(self, date=None):
        self.ctrl_date_debut.SetDate(date)

    def SetDateFin(self, date=None):
        self.ctrl_date_fin.SetDate(date)

    def SetTypeQuotient(self, IDtype_quotient=None):
        self.ctrl_type_quotient.SetID(IDtype_quotient)

    def SetQuotient(self, quotient=None):
        if quotient != None :
            self.ctrl_quotient.SetValue(str(quotient))

    def SetRevenu(self, revenu=None):
        if revenu != None :
            self.ctrl_revenu.SetMontant(revenu)

    def SetObservations(self, observations=None):
        if observations != None :
            self.ctrl_observations.SetValue(observations)
    
    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate() 

    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate() 

    def GetTypeQuotient(self):
        return self.ctrl_type_quotient.GetID()

    def GetQuotient(self):
        try :
            quotient = int(self.ctrl_quotient.GetValue())
        except :
            quotient = None
        return quotient

    def GetRevenu(self):
        return self.ctrl_revenu.GetMontant()

    def GetObservations(self):
        return self.ctrl_observations.GetValue()

    def OnBoutonOk(self, event):
        # Période
        if self.ctrl_date_debut.FonctionValiderDate() == False or self.GetDateDebut() == None :
            dlg = wx.MessageDialog(self, _(u"La date de début de validité n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        if self.ctrl_date_fin.FonctionValiderDate() == False or self.GetDateFin() == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de validité n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False

        # Quotient
        quotient = self.ctrl_quotient.GetValue()
        if len(quotient) > 0 :
            try :
                test = int(quotient)
            except :
                dlg = wx.MessageDialog(self, _(u"Le quotient familial que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_quotient.SetFocus()
                return False
        else :
            quotient = None

        # Revenu
        revenu = self.ctrl_revenu.GetMontant()
        if self.ctrl_revenu.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Le revenu que vous avez saisi n'est pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_revenu.SetFocus()
            return False

        if quotient == None and revenu == 0.0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un quotient familial ou un revenu !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
