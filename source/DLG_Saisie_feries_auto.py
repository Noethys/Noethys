#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import GestionDB
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.easter import easter 


class MyDialog(wx.Dialog):
    def __init__(self, parent, fichierOuvert=None):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE)

        self.label_intro = wx.StaticText(self, -1, _(u"Cette fonctionnalit� vous permet de laisser Noethys cr�er les jours f�ri�s variables \nd'une ou plusieurs ann�es selon des algorithmes de calcul int�gr�s. Saisissez une \nou plusieurs ann�es s�par�es d'un point-virgule, cochez les jours � cr�er puis \ncliquez sur le bouton OK."))
        self.label_annees = wx.StaticText(self, -1, _(u"Ann�es :"))
        self.ctrl_annees = wx.TextCtrl(self, -1, u"")
        self.label_jours = wx.StaticText(self, -1, _(u"Jours f�ri�s :"))
        listeJours = [_(u"Lundi de P�ques"), _(u"Jeudi de l'ascension"), _(u"Lundi de Pentec�te")]
        self.ctrl_jours = wx.CheckListBox(self, -1, (-1, -1), wx.DefaultSize, listeJours)
        self.ctrl_jours.SetMinSize((-1, 80))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie automatique des jours f�ri�s variables"))
        self.ctrl_annees.SetToolTipString(_(u"Saisissez une ann�e ou plusieurs ann�es s�par�es de points-virgules (;). Exemple : '2011;2012;2013' "))
        self.ctrl_jours.SetToolTipString(_(u"Cochez les jours f�ri�s � cr�er"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour cr�er les jours f�ri�s"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 0)
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_contenu = wx.FlexGridSizer(2, 2, 10, 10)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALL, 10)
        grid_sizer_contenu.Add(self.label_annees, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_annees, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_jours, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_contenu.Add(self.ctrl_jours, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Joursfris")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # R�cup�ration des ann�es
        if self.ctrl_annees.GetValue() == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une ann�e !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        listeAnnees = []
        for annee in self.ctrl_annees.GetValue().split(";") :
            try :
                listeAnnees.append(int(annee))
                if int(annee) < 1900 or int(annee) > 3000 :
                    raise Exception()
            except :
                dlg = wx.MessageDialog(self, _(u"Les ann�es saisies ne semblent pas valides !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # R�cup�ration jours f�ri�s � cr�er
        listeCoches = []
        for index in range(0, self.ctrl_jours.GetCount()):
            if self.ctrl_jours.IsChecked(index):
                listeCoches.append(index)

        if len(listeCoches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un jour f�ri� � cr�er !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # R�cup�ration des jours d�j� pr�sents dans la base de donn�es
        DB = GestionDB.DB() 
        req = """SELECT IDferie, nom, jour, mois, annee
        FROM jours_feries
        WHERE type='variable' ; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        listeJoursExistants = []
        for IDferie, nom, jour, mois, annee in listeDonnees :
            try :
                listeJoursExistants.append(datetime.date(annee, mois, jour))
            except :
                pass
        
        def SauvegarderDate(nom="", date=None):
            if date not in listeJoursExistants :
                IDferie = DB.ReqInsert("jours_feries", [("type", "variable"), ("nom", nom), ("annee", date.year), ("mois", date.month), ("jour", date.day)])


        # Calcul des jours f�ri�s
        for annee in listeAnnees :
            
            # Dimanche de Paques
            dimanche_paques = easter(annee)
            
            # Lundi de P�ques
            lundi_paques = dimanche_paques + relativedelta(days=+1)
            if 0 in listeCoches : SauvegarderDate(_(u"Lundi de P�ques"), lundi_paques)
            
            # Ascension
            ascension = dimanche_paques + relativedelta(days=+39)
            if 1 in listeCoches : SauvegarderDate(_(u"Jeudi de l'Ascension"), ascension)

            # Pentecote
            pentecote = dimanche_paques + relativedelta(days=+50)
            if 2 in listeCoches : SauvegarderDate(_(u"Lundi de Pentec�te"), pentecote)
        
        DB.Close()
        
        # Fermeture
        self.EndModal(wx.ID_OK)

        



if __name__ == u"__main__":
    app = wx.App(0)
    dlg = MyDialog(None)
    dlg.ShowModal() 
    dlg.Destroy() 
    app.MainLoop()
