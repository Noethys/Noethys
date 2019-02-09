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
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.easter import easter 


class MyDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=-1, style=wx.DEFAULT_DIALOG_STYLE)

        self.label_intro = wx.StaticText(self, -1, _(u"""Cette fonctionnalité vous permet de générer automatiquement les jours fériés variables\nd'une ou plusieurs années selon des algorithmes de calcul intégrés. Saisissez une\nannée de départ, renseignez le nombre d'années à générer puis cochez les fériés à créer."""))

        self.label_nbre = wx.StaticText(self, -1, _(u"Nombre d'années à générer :"))
        self.ctrl_nbre = wx.SpinCtrl(self, -1, u"", min=1, max=50)

        self.label_annee = wx.StaticText(self, -1, _(u"Depuis l'année :"))
        self.ctrl_annee = wx.SpinCtrl(self, -1, u"", min=1970, max=2999)
        self.ctrl_annee.SetValue(datetime.date.today().year)

        self.label_jours = wx.StaticText(self, -1, _(u"Cochez les fériés à générer :"))
        listeJours = [_(u"Lundi de Pâques"), _(u"Jeudi de l'ascension"), _(u"Lundi de Pentecôte")]
        self.ctrl_jours = wx.CheckListBox(self, -1, (-1, -1), wx.DefaultSize, listeJours)
        if 'phoenix' in wx.PlatformInfo:
            self.ctrl_jours.SetCheckedItems((0, 1, 2))
        else:
            self.ctrl_jours.SetChecked((0, 1, 2))
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
        self.SetTitle(_(u"Saisie automatique des jours fériés variables"))
        self.ctrl_nbre.SetToolTip(wx.ToolTip(_(u"Saisissez le nombre d'années à générer")))
        self.ctrl_annee.SetToolTip(wx.ToolTip(_(u"Saisissez l'année de départ")))
        self.ctrl_jours.SetToolTip(wx.ToolTip(_(u"Cochez les jours fériés à créer")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer les jours fériés")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 0)
        grid_sizer_base.Add(self.label_intro, 0, wx.ALL, 10)

        grid_sizer_contenu = wx.FlexGridSizer(6, 1, 10, 10)

        grid_sizer_contenu.Add(self.label_nbre, 0, 0, 0)
        grid_sizer_contenu.Add(self.ctrl_nbre, 0, wx.EXPAND, 0)

        grid_sizer_contenu.Add(self.label_annee, 0, 0, 0)
        grid_sizer_contenu.Add(self.ctrl_annee, 0, wx.EXPAND, 0)

        grid_sizer_contenu.Add(self.label_jours, 0, 0, 0)
        grid_sizer_contenu.Add(self.ctrl_jours, 0, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
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
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Joursfris")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # Récupération des années
        annee_depart = self.ctrl_annee.GetValue()
        nbre_annees = self.ctrl_nbre.GetValue()

        # Génération de la liste des années :
        listeAnnees = range(annee_depart, annee_depart+nbre_annees)

        # Récupération jours fériés à créer
        listeCoches = []
        for index in range(0, self.ctrl_jours.GetCount()):
            if self.ctrl_jours.IsChecked(index):
                listeCoches.append(index)

        if len(listeCoches) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement cocher au moins un jour férié à créer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Récupération des jours déjà présents dans la base de données
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


        # Calcul des jours fériés
        for annee in listeAnnees :
            
            # Dimanche de Paques
            dimanche_paques = easter(annee)
            
            # Lundi de Pâques
            lundi_paques = dimanche_paques + relativedelta(days=+1)
            if 0 in listeCoches : SauvegarderDate(_(u"Lundi de Pâques"), lundi_paques)
            
            # Ascension
            ascension = dimanche_paques + relativedelta(days=+39)
            if 1 in listeCoches : SauvegarderDate(_(u"Jeudi de l'Ascension"), ascension)

            # Pentecote
            pentecote = dimanche_paques + relativedelta(days=+50)
            if 2 in listeCoches : SauvegarderDate(_(u"Lundi de Pentecôte"), pentecote)
        
        DB.Close()
        
        # Fermeture
        self.EndModal(wx.ID_OK)

        



if __name__ == u"__main__":
    app = wx.App(0)
    dlg = MyDialog(None)
    dlg.ShowModal() 
    dlg.Destroy() 
    app.MainLoop()
