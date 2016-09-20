#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-16 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import datetime
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_heure
from Utils import UTILS_Dates
import GestionDB


class Dialog(wx.Dialog):
    def __init__(self, parent, IDperiode=None, IDactivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDperiode = IDperiode
        self.IDactivite = IDactivite
                
        # Bandeau
        if self.IDperiode == None :
            titre = _(u"Saisie d'une nouvelle période de réservations")
        else :
            titre = _(u"Modification d'une période de réservations")
        self.SetTitle(titre)
        intro = _(u"Définissez ici une période en renseignant le nom de la période, la période correspondante dans le calendrier des ouvertures et une éventuelle période daffichage sur le portail.")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Emails_exp.png")
        
        # Nom
        self.box_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de la période"))
        self.ctrl_nom = wx.TextCtrl(self, -1, "")

        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période de réservations"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Affichage
        self.box_affichage_staticbox = wx.StaticBox(self, -1, _(u"Affichage sur le portail"))
        self.radio_oui = wx.RadioButton(self, -1, _(u"Toujours afficher"), style=wx.RB_GROUP)
        self.radio_dates = wx.RadioButton(self, -1, _(u"Afficher uniquement sur la période suivante :"))
        self.label_affichage_date_debut = wx.StaticText(self, -1, _(u"Du"))
        self.ctrl_affichage_date_debut = CTRL_Saisie_date.Date2(self)
        self.ctrl_affichage_heure_debut = CTRL_Saisie_heure.Heure(self)
        self.label_affichage_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_affichage_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_affichage_heure_fin = CTRL_Saisie_heure.Heure(self)
        self.radio_non = wx.RadioButton(self, -1, _(u"Ne pas afficher"))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAffichage, self.radio_oui)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAffichage, self.radio_dates)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAffichage, self.radio_non)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.Importation()
        self.OnRadioAffichage(None)


    def __set_properties(self):
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici un nom pour cette période (Ex : 'Juillet 2016', 'Année 2016', etc...)"))
        self.radio_oui.SetToolTipString(_(u"Sélectionnez cette option pour afficher cette période sur le portail"))
        self.radio_dates.SetToolTipString(_(u"Sélectionnez cette option pour afficher cette période sur le portail uniquement entre les dates souhaitées"))
        self.radio_non.SetToolTipString(_(u"Sélectionnez cette option pour ne pas afficher cette période sur le portail"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        # Nom
        box_nom = wx.StaticBoxSizer(self.box_nom_staticbox, wx.VERTICAL)
        box_nom.Add(self.ctrl_nom, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 10)

        grid_sizer_contenu.Add(box_nom, 1, wx.EXPAND, 0)

        # Période
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)

        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL | wx.EXPAND, 10)

        grid_sizer_contenu.Add(box_periode, 0, wx.EXPAND, 0)

        # Affichage
        box_affichage = wx.StaticBoxSizer(self.box_affichage_staticbox, wx.VERTICAL)

        grid_sizer_affichage = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_affichage.Add(self.radio_dates, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_affichage_periode = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_affichage_periode.Add(self.label_affichage_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_affichage_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_affichage_heure_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.label_affichage_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_affichage_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage_periode.Add(self.ctrl_affichage_heure_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(grid_sizer_affichage_periode, 0, wx.EXPAND | wx.LEFT, 16)

        grid_sizer_affichage.Add(self.radio_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.AddGrowableCol(0)

        box_affichage.Add(grid_sizer_affichage, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_affichage, 1,wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioAffichage(self, event):
        etat = self.radio_dates.GetValue()
        self.label_affichage_date_debut.Enable(etat)
        self.ctrl_affichage_date_debut.Enable(etat)
        self.ctrl_affichage_date_fin.Enable(etat)
        self.label_affichage_date_fin.Enable(etat)
        self.ctrl_affichage_heure_debut.Enable(etat)
        self.ctrl_affichage_heure_fin.Enable(etat)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def Importation(self):
        """ Importation des données """
        if self.IDperiode == None :
            return

        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, date_debut, date_fin, affichage, affichage_date_debut, affichage_date_fin
        FROM portail_periodes
        WHERE IDperiode=%d;""" % self.IDperiode
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDactivite, nom, date_debut, date_fin, affichage, affichage_date_debut, affichage_date_fin = listeDonnees[0]
        affichage_date_debut = UTILS_Dates.DateEngEnDateDDT(affichage_date_debut)
        affichage_date_fin = UTILS_Dates.DateEngEnDateDDT(affichage_date_fin)

        self.IDactivite = IDactivite
        self.ctrl_nom.SetValue(nom)
        self.ctrl_date_debut.SetDate(date_debut)
        self.ctrl_date_fin.SetDate(date_fin)

        if affichage == 1 and affichage_date_debut == None :
            self.radio_oui.SetValue(True)
        elif affichage == 1 and affichage_date_debut != None :
            self.radio_dates.SetValue(True)
            self.ctrl_affichage_date_debut.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_debut),"%Y-%m-%d"))
            self.ctrl_affichage_date_fin.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_fin),"%Y-%m-%d"))
            self.ctrl_affichage_heure_debut.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_debut),"%H:%M"))
            self.ctrl_affichage_heure_fin.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_fin),"%H:%M"))
        else :
            self.radio_non.SetValue(True)


    def OnBoutonOk(self, event):
        # Récupération des données
        nom = self.ctrl_nom.GetValue()
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom pour cette période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_nom.SetFocus()
            return

        date_debut = self.ctrl_date_debut.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début pour cette période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return

        date_fin = self.ctrl_date_fin.GetDate()
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin pour cette période !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return

        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin supérieure à la date de début !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return

        if self.radio_oui.GetValue() == True : affichage = True
        if self.radio_dates.GetValue() == True : affichage = True
        if self.radio_non.GetValue() == True : affichage = False

        if self.radio_dates.GetValue() == True :

            affichage_date_debut = self.ctrl_affichage_date_debut.GetDate()
            if affichage_date_debut == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_affichage_date_debut.SetFocus()
                return

            affichage_heure_debut = self.ctrl_affichage_heure_debut.GetHeure()
            if affichage_heure_debut == None or self.ctrl_affichage_heure_debut.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de début valide pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_affichage_heure_debut.SetFocus()
                return

            affichage_date_fin = self.ctrl_affichage_date_fin.GetDate()
            if affichage_date_fin == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_affichage_date_fin.SetFocus()
                return

            affichage_heure_fin = self.ctrl_affichage_heure_fin.GetHeure()
            if affichage_heure_fin == None or self.ctrl_affichage_heure_fin.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure de fin valide pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_affichage_heure_fin.SetFocus()
                return

            if affichage_date_debut > affichage_date_fin :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin supérieure à la date de début pour l'affichage !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_affichage_date_fin.SetFocus()
                return

            # Assemblage des dates et heures d'affichage
            affichage_date_debut = datetime.datetime(year=affichage_date_debut.year, month=affichage_date_debut.month, day=affichage_date_debut.day, hour=int(affichage_heure_debut[:2]), minute=int(affichage_heure_debut[3:]))
            affichage_date_fin = datetime.datetime(year=affichage_date_fin.year, month=affichage_date_fin.month, day=affichage_date_fin.day, hour=int(affichage_heure_fin[:2]), minute=int(affichage_heure_fin[3:]))

        else :
            affichage_date_debut = None
            affichage_date_fin = None

        # Sauvegarde
        DB = GestionDB.DB()
        listeDonnees = [
            ("IDactivite", self.IDactivite),
            ("nom", nom),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("affichage", int(affichage)),
            ("affichage_date_debut", affichage_date_debut),
            ("affichage_date_fin", affichage_date_fin),
            ]
        if self.IDperiode == None :
            self.IDperiode = DB.ReqInsert("portail_periodes", listeDonnees)
        else :
            DB.ReqMAJ("portail_periodes", listeDonnees, "IDperiode", self.IDperiode)
        DB.Close()

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDperiode(self):
        return self.IDperiode



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDperiode=1, IDactivite=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
