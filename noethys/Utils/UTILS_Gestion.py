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
from Utils.UTILS_Traduction import _
import wx
import datetime
from Ctrl import CTRL_Bouton_image
import wx.lib.dialogs
import GestionDB
from Utils import UTILS_Dates
import six


class Track_periode(object):
    def __init__(self, donnees):
        self.IDperiode = donnees[0]
        self.date_debut = UTILS_Dates.DateEngEnDateDD(donnees[1])
        self.date_fin = UTILS_Dates.DateEngEnDateDD(donnees[2])
        self.observations = donnees[3]
        self.verrou_consommations = donnees[4]
        self.verrou_prestations = donnees[5]
        self.verrou_factures = donnees[6]
        self.verrou_reglements = donnees[7]
        self.verrou_depots = donnees[8]
        self.verrou_cotisations = donnees[9]

        # Texte verrous
        liste_categories = []
        if self.verrou_consommations == 1 : liste_categories.append(_(u"consommations"))
        if self.verrou_prestations == 1 : liste_categories.append(_(u"prestations"))
        if self.verrou_factures == 1 : liste_categories.append(_(u"factures"))
        if self.verrou_reglements == 1 : liste_categories.append(_(u"règlements"))
        if self.verrou_depots == 1 : liste_categories.append(_(u"dépôts"))
        if self.verrou_cotisations == 1 : liste_categories.append(_(u"cotisations"))
        self.texte_verrous = ", ".join(liste_categories).capitalize()



class Gestion():
    def __init__(self, parent=None):
        self.parent = parent
        self.liste_periodes = self.Importation()

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDperiode, date_debut, date_fin, observations,
        verrou_consommations, verrou_prestations, verrou_factures, verrou_reglements, verrou_depots, verrou_cotisations
        FROM periodes_gestion
        ORDER BY date_debut;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        liste_periodes = []
        for donnees in listeDonnees :
            liste_periodes.append(Track_periode(donnees))
        return liste_periodes

    def Verification(self, categorie=None, donnees=None, silencieux=False):
        liste_problemes = []

        # Formate les données reçues
        if type(donnees) in (datetime.date, str, six.text_type) :
            listeDonnees = [{"date" : donnees},]
        elif type(donnees) == dict :
            listeDonnees = [donnees,]
        elif donnees == None :
            listeDonnees = []
        else :
            listeDonnees = donnees

        if type(categorie) == list :
            listeCategories = categorie
        else:
            listeCategories = [categorie,]

        # Spécial consommations
        if "consommations" in listeCategories :
            listeCategories.append("prestations")

        # Analyse des données
        for donnees in listeDonnees :

            # Recherche le format de la donnée
            if type(donnees) == datetime.date:
                date = donnees
            elif type(donnees) in (str, six.text_type):
                date = UTILS_Dates.DateEngEnDateDD(donnees)
            elif type(donnees) == dict:
                date = donnees["date"]
                if type(date) in (str, six.text_type):
                    date = UTILS_Dates.DateEngEnDateDD(date)

            # Vérifie que la date n'est pas dans une période de gestion
            for periode in self.liste_periodes :
                if date >= periode.date_debut and date <= periode.date_fin :

                    # Vérifie que la catégorie est verrouillée
                    verrou = False
                    for categorie in listeCategories:
                        if hasattr(periode, "verrou_%s" % categorie) :
                            if getattr(periode, "verrou_%s" % categorie) == 1 :
                                verrou = True

                    if verrou == True :
                        liste_problemes.append("- Probleme le " + str(date))
                        break

        if len(liste_problemes) > 0 :
            if silencieux == False :
                dlg = DLG_Verrouillage(self.parent)#, liste_problemes=liste_problemes)
                dlg.ShowModal()
                dlg.Destroy()
            return False

        return True

    def IsPeriodeinPeriodes(self, categorie="", date_debut=None, date_fin=None):
        for periode in self.liste_periodes:
            if date_debut <= periode.date_fin and date_fin >= periode.date_debut:

                # Vérifie que la catégorie est verrouillée
                verrou = False
                if hasattr(periode, "verrou_%s" % categorie):
                    if getattr(periode, "verrou_%s" % categorie) == 1:
                        verrou = True

                if verrou == True:
                    dlg = DLG_Verrouillage(self.parent)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

        return True

# ------------------------------------------- BOITE DE DIALOGUE ----------------------------------------------------------------------------------------

class DLG_Verrouillage(wx.Dialog):
    def __init__(self, parent, liste_problemes=[], intro=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.liste_problemes = liste_problemes

        titre = _(u"Période verrouillée")
        self.SetTitle(titre)
        self.ctrl_image = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(Chemins.GetStaticPath(u"Images/48x48/Cadenas_ferme.png"), wx.BITMAP_TYPE_ANY))
        self.label_ligne_1 = wx.StaticText(self, wx.ID_ANY, titre)
        if intro == None :
            intro = _(u"Vous ne pouvez pas modifier les données d'une période de gestion qui a été verrouillée.")
        self.label_ligne_2 = wx.StaticText(self, wx.ID_ANY, intro)
        self.ctrl_detail = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.ctrl_detail.SetMinSize((500, 300))

        # Insertion du texte de détail
        texte = u"\n".join(liste_problemes)
        if len(texte) > 0 :
            self.ctrl_detail.SetValue(texte)
        else :
            self.ctrl_detail.Show(False)

        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.bouton_fermer.SetFocus()


    def __set_properties(self):
        self.label_ligne_1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(2, 1, 10, 10)
        grid_sizer_bas = wx.FlexGridSizer(1, 5, 10, 10)
        grid_sizer_haut = wx.FlexGridSizer(1, 2, 10, 10)
        grid_sizer_droit = wx.FlexGridSizer(3, 1, 10, 10)
        grid_sizer_haut.Add(self.ctrl_image, 0, wx.ALL, 10)
        grid_sizer_droit.Add(self.label_ligne_1, 0, 0, 0)
        grid_sizer_droit.Add(self.label_ligne_2, 0, 0, 0)
        grid_sizer_droit.Add(self.ctrl_detail, 0, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableRow(2)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_haut.Add(grid_sizer_droit, 1, wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_haut.AddGrowableRow(0)
        grid_sizer_haut.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_haut, 1, wx.EXPAND, 0)
        grid_sizer_bas.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_bas.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_bas.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 

    def OnBoutonFermer(self, event):  
        self.EndModal(wx.ID_CANCEL)





if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()

    gestion = Gestion()

    listeDonnees = [
        {"date" : datetime.date(2016, 1, 1)},
        {"date" : datetime.date(2017, 1, 2)},
    ]

    print(gestion.Verification(listeDonnees))

    #dialog_1 = DLG_Verrouillage(None)
    #app.SetTopWindow(dialog_1)
    #dialog_1.ShowModal()
    app.MainLoop()
