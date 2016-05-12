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
import GestionDB

from Ctrl import CTRL_Saisie_date


class CTRL_Niveaux(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.listeNiveaux, self.dictNiveaux = self.Importation()
        self.SetListeChoix()

    def Importation(self):
        listeNiveaux = []
        dictNiveaux = {}
        DB = GestionDB.DB()
        req = """SELECT IDniveau, ordre, nom, abrege FROM niveaux_scolaires ORDER BY ordre;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()   
        DB.Close() 
        for IDniveau, ordre, nom, abrege in listeDonnees :
            nom =u" %s (%s)" % (nom, abrege)
            dictTemp = { "nom" : nom, "IDniveau" : IDniveau, "ordre" : ordre}
            dictNiveaux[IDniveau] = dictTemp
            listeNiveaux.append((nom, IDniveau))
        return listeNiveaux, dictNiveaux

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        index = 0
        for nom, IDniveau in self.listeNiveaux :
            self.Append(nom)
            index += 1
                            
    def GetIDcoches(self, modeTexte=False):
        listeIDcoches = []
        NbreItems = len(self.listeNiveaux)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                if modeTexte == False :
                    ID = self.listeNiveaux[index][1]
                else:
                    ID = str(self.listeNiveaux[index][1])
                listeIDcoches.append(ID)
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeNiveaux)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeNiveaux)):
            ID = self.listeNiveaux[index][1]
            if ID in listeIDcoches or str(ID) in listeIDcoches :
                self.Check(index)
            index += 1
    

# ----------------------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent   

        self.label_nom = wx.StaticText(self, -1, _(u"Nom :"), style=wx.ALIGN_RIGHT)
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        
        self.label_saison = wx.StaticText(self, -1, _(u"Saison :"), style=wx.ALIGN_RIGHT)
        self.label_du = wx.StaticText(self, -1, u"Du", style=wx.ALIGN_RIGHT)
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"), style=wx.ALIGN_RIGHT)
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        self.label_niveaux = wx.StaticText(self, -1, _(u"Niveaux :"), style=wx.ALIGN_RIGHT)
        self.ctrl_niveaux = CTRL_Niveaux(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une classe"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom de la classe. Ex : 'CP - Mme PICHON'..."))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez ici la date de début de saison"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez ici la date de fin de saison"))
        self.ctrl_niveaux.SetToolTipString(_(u"Cochez les niveaux scolaires de la classe"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((400, 400))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_saison = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_contenu.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_saison, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_saison.Add(self.label_du, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_saison.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_saison.Add(self.label_au, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_saison.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_saison, 1, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_niveaux, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_niveaux, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(2)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
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
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Classes")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def GetNom(self):
        return self.ctrl_nom.GetValue()

    def GetDateDebut(self):
        return self.ctrl_date_debut.GetDate()   
    
    def GetDateFin(self):
        return self.ctrl_date_fin.GetDate()
    
    def GetNiveaux(self):
        listeID = self.ctrl_niveaux.GetIDcoches(modeTexte=True) 
        txt = ";".join(listeID)
        return txt

    def SetNom(self, nom=""):
        self.ctrl_nom.SetValue(nom)

    def SetDateDebut(self, date=None):
        self.ctrl_date_debut.SetDate(date)   
    
    def SetDateFin(self, date=None):
        self.ctrl_date_fin.SetDate(date)   
        
    def SetNiveaux(self, txt=""):
        listeID = txt.split(";")
        self.ctrl_niveaux.SetIDcoches(listeID) 

    def OnBoutonOk(self, event):
        nom = self.GetNom()
        dateDebut = self.GetDateDebut() 
        dateFin = self.GetDateFin() 
        listeNiveaux = self.ctrl_niveaux.GetIDcoches(modeTexte=False) 
        
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette classe !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        if dateDebut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une date de début de saison !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        if dateFin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une date de fin de saison !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return

        if dateDebut > dateFin :
            dlg = wx.MessageDialog(self, _(u"La date de début ne peut pas être supérieure à celle de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return
        
        if len(listeNiveaux) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun niveau scolaire pour cette classe. \n\nEtes-vous sûr de vouloir tout de même valider cette saisie ?"), _(u"Attention"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            if dlg.ShowModal() != wx.ID_YES :
                return
            dlg.Destroy()

        # Valide la saisie
        self.EndModal(wx.ID_OK)



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
