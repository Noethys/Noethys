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
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_heure
from Utils import UTILS_Dates
import GestionDB
import datetime


class Dialog(wx.Dialog):
    def __init__(self, parent, IDmessage=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDmessage = IDmessage

        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, -1, _(u"Généralités"))
        self.label_titre = wx.StaticText(self, -1, _(u"Titre :"))
        self.ctrl_titre = wx.TextCtrl(self, -1, "")
        self.label_texte = wx.StaticText(self, -1, _(u"Texte :"))
        self.ctrl_texte = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

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

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAffichage, self.radio_oui)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAffichage, self.radio_dates)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

        # Init contrôles
        self.Importation()
        self.OnRadioAffichage(None)

    def __set_properties(self):
        if self.IDmessage == None :
            self.SetTitle(_(u"Saisie d'un message"))
        else:
            self.SetTitle(_(u"Modification d'un message"))
        self.ctrl_titre.SetToolTipString(_(u"Saisissez ici un titre interne pour ce message. Ce titre n'apparaîtra pas sur le portail."))
        self.ctrl_texte.SetToolTipString(_(u"Saisissez ici le texte qui apparaîtra sur la page d'accueil du portail"))
        self.radio_oui.SetToolTipString(_(u"Sélectionnez cette option pour toujours afficher ce message sur le portail"))
        self.radio_dates.SetToolTipString(_(u"Sélectionnez cette option pour afficher message sur le portail uniquement entre les dates souhaitées"))
        self.SetMinSize((550, 450))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)

        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_generalites.Add(self.label_titre, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_generalites.Add(self.ctrl_titre, 0, wx.EXPAND, 0)
        grid_sizer_generalites.Add(self.label_texte, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_generalites.Add(self.ctrl_texte, 0, wx.EXPAND, 0)
        grid_sizer_generalites.AddGrowableCol(1)
        grid_sizer_generalites.AddGrowableRow(1)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_generalites, 1,wx.EXPAND, 0)

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

        grid_sizer_affichage.AddGrowableCol(0)
        box_affichage.Add(grid_sizer_affichage, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_affichage, 1,wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

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
        grid_sizer_base.AddGrowableRow(0)
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

    def Importation(self):
        """ Importation des données """
        if self.IDmessage == None :
            return

        DB = GestionDB.DB()
        req = """SELECT IDmessage, titre, texte, affichage_date_debut, affichage_date_fin
        FROM portail_messages
        WHERE IDmessage=%d;""" % self.IDmessage
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        IDmessage, titre, texte, affichage_date_debut, affichage_date_fin = listeDonnees[0]
        affichage_date_debut = UTILS_Dates.DateEngEnDateDDT(affichage_date_debut)
        affichage_date_fin = UTILS_Dates.DateEngEnDateDDT(affichage_date_fin)

        self.ctrl_titre.SetValue(titre)
        self.ctrl_texte.SetValue(texte)

        if affichage_date_debut == None or affichage_date_fin == None :
            self.radio_oui.SetValue(True)
        else :
            self.radio_dates.SetValue(True)
            self.ctrl_affichage_date_debut.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_debut),"%Y-%m-%d"))
            self.ctrl_affichage_date_fin.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_fin),"%Y-%m-%d"))
            self.ctrl_affichage_heure_debut.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_debut),"%H:%M"))
            self.ctrl_affichage_heure_fin.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(affichage_date_fin),"%H:%M"))


    def OnBoutonOk(self, event):
        # Validation des données
        titre = self.ctrl_titre.GetValue()
        if titre == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un titre !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_titre.SetFocus()
            return

        texte = self.ctrl_texte.GetValue()
        if texte == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un texte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_texte.SetFocus()
            return

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

        # Sauvegarde des données
        DB = GestionDB.DB()
        listeDonnees = [
            ("titre", titre),
            ("texte", texte),
            ("affichage_date_debut", affichage_date_debut),
            ("affichage_date_fin", affichage_date_fin),
            ]
        if self.IDmessage == None :
            self.IDmessage = DB.ReqInsert("portail_messages", listeDonnees)
        else :
            DB.ReqMAJ("portail_messages", listeDonnees, "IDmessage", self.IDmessage)
        DB.Close()

        self.EndModal(wx.ID_OK)




                


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDmessage=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
