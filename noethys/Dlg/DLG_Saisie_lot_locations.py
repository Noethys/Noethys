#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
import datetime
from Utils.UTILS_Traduction import _
import wx
import copy
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Utils import UTILS_Dates
import wx.lib.agw.hyperlink as Hyperlink
import GestionDB


def FormateDate(date):
    if date == None :
        return _(u"Non définie")
    else :
        return datetime.datetime.strftime(date, "%d/%m/%Y - %Hh%M")


class CTRL_Semaines(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1)
        self.parent = parent
        self.listeEtats = [
            (1, _(u"Toutes les semaines")),
            (2, _(u"Une semaine sur deux")),
            (3, _(u"Une semaine sur trois")),
            (4, _(u"Une semaine sur quatre")),
            (5, _(u"Les semaines paires")),
            (6, _(u"Les semaines impaires")),
        ]
        self.MAJ()

    def MAJ(self):
        listeLabels = []
        for code, label in self.listeEtats:
            listeLabels.append(label)
        self.SetItems(listeLabels)
        self.Select(0)

    def GetValeur(self):
        index = self.GetSelection()
        return self.listeEtats[index][0]

    def GetLabel(self):
        return self.GetStringSelection()

    def SetValeur(self, valeur=1):
        index = 0
        for code, label in self.listeEtats:
            if code == valeur:
                self.Select(index)
            index += 1


# ----------------------------------------------------------------------------------------------------------------------------------

class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
        self.parent = parent

        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)

    def OnLeftLink(self, event):
        if self.URL == "tout": self.parent.CocherTout()
        if self.URL == "rien": self.parent.CocherRien()
        self.UpdateLink()


class CTRL_Jours(wx.Panel):
    def __init__(self, parent, periode="scolaire"):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.periode = periode
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        for jour in self.liste_jours :
            exec("self.check_%s = wx.CheckBox(self, -1, u'%s')" % (jour, jour[0].upper()) )
            exec("self.check_%s.SetToolTip(wx.ToolTip(u'%s'))" % (jour, jour.capitalize()) )

        self.hyper_tout = Hyperlien(self, label=_(u"Tout"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, u"|")
        self.hyper_rien = Hyperlien(self, label=_(u"Rien"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=10, vgap=0, hgap=0)
        for jour in self.liste_jours :
            exec("grid_sizer_base.Add(self.check_%s, 0, 0, 0)" % jour)

        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=5, vgap=0, hgap=3)
        grid_sizer_options.Add(self.hyper_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(grid_sizer_options, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

        # Init
        self.SetJours("0;1;2;3;4;5;6")

    def GetJours(self):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            exec("etat = self.check_%s.GetValue()" % jour)
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp
    
    def SetJours(self, texteJours=""):
        if texteJours == None :
            return

        listeJoursTemp = texteJours.split(";")
        listeJours = []
        for jour in listeJoursTemp :
            if len(jour) > 0 :
                listeJours.append(int(jour))
        index = 0
        for jour in self.liste_jours :
            if index in listeJours :
                etat = "True"
            else :
                etat = "False"
            exec("self.check_%s.SetValue(%s)" % (jour, etat))
            index += 1

    def CocherTout(self):
        self.SetJours("0;1;2;3;4;5;6")

    def CocherRien(self):
        self.SetJours("")


# ----------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDlocation=None, periode=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDlocation = IDlocation
        self.periode = periode

        # Importation de la location modèle
        self.Importation()

        # Action
        self.box_action_staticbox = wx.StaticBox(self, -1, _(u"Location à recopier"))
        if len(self.dictModele) > 0 :
            texte = _(u"Produit : %s\nDu %s au %s\nDurée : %s") % (self.dictModele["nom_produit"], self.dictModele["date_debut_str"], self.dictModele["date_fin_str"], self.dictModele["duree_str"])
        else :
            texte = _(u"ERREUR : Location introuvable")
        self.ctrl_info = wx.StaticText(self, -1, texte)
        self.ctrl_info.SetMinSize((-1, 50))

        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, _(u"Période d'application"))
        
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.ctrl_feries = wx.CheckBox(self, -1, _(u"Inclure les fériés"))

        # Jours
        self.box_jours_staticbox = wx.StaticBox(self, -1, _(u"Jours"))
        
        self.label_scolaires = wx.StaticText(self, -1, _(u"Scolaires :"))
        self.ctrl_scolaires = CTRL_Jours(self, "scolaire")
        self.label_vacances = wx.StaticText(self, -1, _(u"Vacances :"))
        self.ctrl_vacances = CTRL_Jours(self, "vacances")
        self.label_semaines = wx.StaticText(self, -1, _(u"Fréquence :"))
        self.ctrl_semaines = CTRL_Semaines(self)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)

        # Init
        if len(self.dictModele) > 0:
            self.ctrl_date_debut.SetDate(self.dictModele["date_debut"] + datetime.timedelta(days=1))
        if self.periode != None :
            self.ctrl_date_fin.SetDate(self.periode[1])

    def __set_properties(self):
        self.SetTitle(_(u"Saisie par lot"))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de début de période cible")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Sélectionnez une date de fin de période cible")))
        self.ctrl_semaines.SetToolTip(wx.ToolTip(_(u"Sélectionnez une fréquence")))
        self.ctrl_feries.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour modifier également les jours fériés")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Action
        box_action = wx.StaticBoxSizer(self.box_action_staticbox, wx.VERTICAL)
        box_action.Add(self.ctrl_info, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_action, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        grid_sizer_bas = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

        # Périodes
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add( (5, 5), 0, 0, 0)
        grid_sizer_periode.Add(self.ctrl_feries, 0, 0, 0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_bas.Add(box_periode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)
        
        # Jours
        box_jours = wx.StaticBoxSizer(self.box_jours_staticbox, wx.VERTICAL)
        grid_sizer_jours = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)
        grid_sizer_jours.Add(self.label_scolaires, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_scolaires, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_vacances, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_vacances, 0, wx.EXPAND, 0)
        grid_sizer_jours.Add(self.label_semaines, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_jours.Add(self.ctrl_semaines, 0, wx.EXPAND, 0)
        #grid_sizer_jours.Add(self.label_feries, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_sizer_jours.Add(self.ctrl_feries, 0, wx.EXPAND, 0)
        grid_sizer_jours.AddGrowableCol(1)
        box_jours.Add(grid_sizer_jours, 1, wx.ALL|wx.EXPAND, 10)

        grid_sizer_bas.Add(box_jours, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)

        grid_sizer_base.Add(grid_sizer_bas, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

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
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def Importation(self):
        DB = GestionDB.DB()

        # Importation des vacances
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut;"""
        DB.ExecuterReq(req)
        self.listeVacances = DB.ResultatReq()

        # Importation des fériés
        req = """SELECT type, nom, jour, mois, annee
        FROM jours_feries;"""
        DB.ExecuterReq(req)
        self.listeFeries = DB.ResultatReq()

        # Importation de la location modèle
        req = """SELECT locations.IDfamille, locations.IDproduit, 
        locations.observations, locations.date_debut, locations.date_fin, locations.quantite,
        produits.nom, 
        produits_categories.nom
        FROM locations
        LEFT JOIN produits ON produits.IDproduit = locations.IDproduit
        LEFT JOIN produits_categories ON produits_categories.IDcategorie = produits.IDcategorie
        WHERE locations.IDlocation=%d;""" % self.IDlocation
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.dictModele = {}
        if len(listeDonnees) > 0:
            IDfamille, IDproduit, observations, date_debut, date_fin, quantite, nom_produit, nom_categorie = listeDonnees[0]

            if quantite == None:
                quantite = 1

            # Période
            if isinstance(date_debut, str) or isinstance(date_debut, unicode):
                date_debut = datetime.datetime.strptime(date_debut, "%Y-%m-%d %H:%M:%S")

            if isinstance(date_fin, str) or isinstance(date_fin, unicode):
                date_fin = datetime.datetime.strptime(date_fin, "%Y-%m-%d %H:%M:%S")
                duree = date_fin - date_debut
                duree_str = UTILS_Dates.FormatDelta(duree)
            elif isinstance(date_fin, datetime.datetime):
                duree = date_fin - date_debut
                duree_str = UTILS_Dates.FormatDelta(duree)
            else :
                duree = None
                duree_str = _(u"Non définie")

            self.dictModele = {
                "IDfamille" : IDfamille, "IDproduit" : IDproduit, "observations" : observations,
                "date_debut" : date_debut, "date_fin" : date_fin,
                "duree" : duree, "duree_str" : duree_str,
                "date_debut_str": FormateDate(date_debut), "date_fin_str": FormateDate(date_fin),
                "quantite": quantite, "nom_produit" : nom_produit, "nom_categorie" : nom_categorie}


    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def EstFerie(self, dateDD):
        jour = dateDD.day
        mois = dateDD.month
        annee = dateDD.year
        for type, nom, jourTmp, moisTmp, anneeTmp in self.listeFeries :
            jourTmp = int(jourTmp)
            moisTmp = int(moisTmp)
            anneeTmp = int(anneeTmp)
            if type == "fixe" :
                if jourTmp == jour and moisTmp == mois :
                    return True
            else:
                if jourTmp == jour and moisTmp == mois and anneeTmp == annee :
                    return True
        return False



    def OnBoutonOk(self, event):
        # Période
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de début de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez saisir une date de fin de période !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        if date_debut > date_fin :
            dlg = wx.MessageDialog(self, _(u"La date de début ne peut pas être supérieure à la date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        # Jours
        jours_scolaires = self.ctrl_scolaires.GetJours()
        jours_vacances = self.ctrl_vacances.GetJours()
        if len(jours_scolaires) == 0 and len(jours_vacances) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un jour scolaire ou de vacances !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        feries = self.ctrl_feries.GetValue()
        semaines = self.ctrl_semaines.GetValeur()

        # Recherche des dates valides
        listeDates = []
        date = date_debut
        numSemaine = copy.copy(semaines)
        dateTemp = date
        while date < (date_fin + datetime.timedelta(days=1)):

            # Vérifie période et jour
            valide = False
            if self.EstEnVacances(date):
                if date.weekday() in jours_vacances:
                    valide = True
            else:
                if date.weekday() in jours_scolaires:
                    valide = True

            # Vérifie si férié
            if feries == False and self.EstFerie(date) == True:
                valide = False

            # Calcul le numéro de semaine
            if len(listeDates) > 0:
                if date.weekday() < dateTemp.weekday():
                    numSemaine += 1

            # Fréquence semaines
            if semaines in (2, 3, 4):
                if numSemaine % semaines != 0:
                    valide = False

            # Semaines paires et impaires
            if valide == True and semaines in (5, 6):
                numSemaineAnnee = date.isocalendar()[1]
                if numSemaineAnnee % 2 == 0 and semaines == 6:
                    valide = False
                if numSemaineAnnee % 2 != 0 and semaines == 5:
                    valide = False

            # Ajout de la date à la liste
            if valide == True:
                listeDates.append(date)

            dateTemp = date
            date += datetime.timedelta(days=1)

        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Confirmez-vous le recopiage de la location sur %d dates ?") % len(listeDates), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

        # Recopiage de la location
        DB = GestionDB.DB()

        dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant le traitement..."), None)

        for date in listeDates :

            date_debut = self.dictModele["date_debut"]
            date_debut = date_debut.replace(year=date.year, month=date.month, day=date.day)

            if self.dictModele["duree"] != None :
                date_fin = date_debut + self.dictModele["duree"]
            else :
                date_fin = self.dictModele["date_fin"]

            # Duplication de la location
            conditions = "IDlocation=%d" % self.IDlocation
            dictModifications = {"date_debut" : date_debut, "date_fin" : date_fin, "date_saisie": datetime.date.today()}
            newIDlocation = DB.Dupliquer("locations", "IDlocation", conditions, dictModifications)

            # Duplication de la prestation
            conditions = "IDdonnee=%d" % self.IDlocation
            dictModifications = {"IDdonnee": newIDlocation}
            newIDprestation = DB.Dupliquer("prestations", "IDlocation", conditions, dictModifications)

        DB.Close()

        del dlgAttente

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        return self.dictDonnees




if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDlocation=8)
    dlg.ctrl_date_debut.SetDate("2018-01-01")
    dlg.ctrl_date_fin.SetDate("2018-12-31")
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
