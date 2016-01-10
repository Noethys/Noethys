#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import GestionDB
import UTILS_Dates
import datetime
import calendar
from UTILS_Decimal import FloatToDecimal as FloatToDecimal
import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


import UTILS_Interface
from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter

import UTILS_Interface
from ObjectListView import EVT_CELL_EDIT_STARTING, EVT_CELL_EDIT_FINISHING, CellEditorRegistry

from DLG_Saisie_contratpsu import Base
import CTRL_Saisie_duree

LISTE_MOIS = [_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]




class Track(object):
    def __init__(self, mois=1, annee=2015, clsbase=None, track_mensualite=None):
        self.mois = mois
        self.annee = annee
        self.clsbase = clsbase
        self.track_mensualite = track_mensualite

        # Généralités
        self.IDinscription = self.clsbase.GetValeur("IDinscription", None)
        self.date_debut_contrat = self.clsbase.GetValeur("date_debut", None)
        self.date_fin_contrat = self.clsbase.GetValeur("date_fin", None)
        self.individu_nom_complet = self.clsbase.GetValeur("individu_nom_complet", "")
        self.duree_tolerance_depassement = self.clsbase.GetValeur("duree_tolerance_depassement", datetime.timedelta(0))
        self.arrondi_type = self.clsbase.GetValeur("arrondi_type", datetime.timedelta(0))
        self.arrondi_delta = self.clsbase.GetValeur("arrondi_delta", datetime.timedelta(0))
        self.IDunite_prevision = self.clsbase.GetValeur("IDunite_prevision", None)
        self.IDunite_presence = self.clsbase.GetValeur("IDunite_presence", None)

        # Ajout les RTT non prises si dernier mois du contrat
        if self.date_fin_contrat.month == mois and self.date_fin_contrat.year == annee :
            self.duree_solde_rtt = self.clsbase.GetValeur("duree_absences_solde", datetime.timedelta(0))
        else :
            self.duree_solde_rtt = datetime.timedelta(0)

        # Mensualité
        self.label_prestation = self.track_mensualite.label_prestation
        self.heures_prevues = self.track_mensualite.heures_prevues
        self.montant_prevu = self.track_mensualite.montant_prevu
        self.IDprestation = self.track_mensualite.IDprestation
        self.date_facturation = self.track_mensualite.date_facturation
        self.forfait_date_debut = self.track_mensualite.forfait_date_debut
        self.forfait_date_fin = self.track_mensualite.forfait_date_fin
        self.taux = self.track_mensualite.taux
        self.tarif_base = self.track_mensualite.tarif_base
        self.tarif_depassement = self.track_mensualite.tarif_depassement

        # Prestation existante
        self.IDfacture = self.track_mensualite.IDfacture
        self.num_facture = self.track_mensualite.num_facture
        self.heures_facturees = self.track_mensualite.heures_facturees
        self.montant_facture = self.track_mensualite.montant_facture

        # Consommations
        self.heures_prevues_mois = datetime.timedelta(seconds=0)
        self.heures_presences = datetime.timedelta(seconds=0)
        self.heures_absences_deductibles = datetime.timedelta(seconds=0)
        self.heures_absences_non_deductibles = datetime.timedelta(seconds=0)
        self.heures_depassements = datetime.timedelta(seconds=0)
        self.heures_regularisation = datetime.timedelta(seconds=0)

        # Récupération des paramètres d'arrondis du contrat
        # arrondi_type = self.clsbase.GetValeur("arrondi_type")
        # arrondi_delta = self.clsbase.GetValeur("arrondi_delta")

        dict_conso = self.clsbase.GetValeur("dict_conso", {})
        self.dict_dates = {}
        for date, listeConso in dict_conso.iteritems() :

            # Recherche des consommations de la date
            if date.month == self.mois and date.year == self.annee :

                dict_date = {
                    "prevision" : {
                        "heure_debut" : None,
                        "heure_fin" : None,
                        "duree_reelle" : datetime.timedelta(0),
                        "duree_arrondie" : datetime.timedelta(0),
                    },
                    "presence" : {
                        "heure_debut" : None,
                        "heure_fin" : None,
                        "duree_reelle" : datetime.timedelta(0),
                        "duree_arrondie" : datetime.timedelta(0),
                    },
                    "heures_absences_non_deductibles" : datetime.timedelta(0),
                    "heures_absences_deductibles" : datetime.timedelta(0),
                    "depassement" : datetime.timedelta(0),
                    "absences_rtt" : datetime.timedelta(0),
                }



                for track in listeConso :

                    # Recherche des prévisions
                    if track.IDunite == self.clsbase.GetValeur("IDunite_prevision") :
                        self.heures_prevues_mois += track.duree_arrondie # track.duree_reelle

                        if dict_date["prevision"]["heure_debut"] == None or dict_date["prevision"]["heure_debut"] < track.heure_debut_time :
                            dict_date["prevision"]["heure_debut"] = track.heure_debut_time
                        if dict_date["prevision"]["heure_fin"] == None or dict_date["prevision"]["heure_fin"] > track.heure_fin_time :
                            dict_date["prevision"]["heure_fin"] = track.heure_fin_time
                        dict_date["prevision"]["duree_reelle"] += track.duree_reelle
                        dict_date["prevision"]["duree_arrondie"] += track.duree_arrondie

                    # Recherche des présences
                    if track.IDunite == self.clsbase.GetValeur("IDunite_presence") :

                        if track.etat in ("reservation", "present") :
                            self.heures_presences += track.duree_arrondie

                            if dict_date["presence"]["heure_debut"] == None or dict_date["presence"]["heure_debut"] < track.heure_debut_time :
                                dict_date["presence"]["heure_debut"] = track.heure_debut_time
                            if dict_date["presence"]["heure_fin"] == None or dict_date["presence"]["heure_fin"] > track.heure_fin_time :
                                dict_date["presence"]["heure_fin"] = track.heure_fin_time
                            dict_date["presence"]["duree_reelle"] += track.duree_reelle
                            dict_date["presence"]["duree_arrondie"] += track.duree_arrondie

                        if track.etat in ("absenti",) :
                            self.heures_absences_non_deductibles += track.duree_arrondie
                            dict_date["heures_absences_non_deductibles"] = self.heures_absences_non_deductibles

                        if track.etat in ("absentj",) :
                            self.heures_absences_deductibles += track.duree_arrondie
                            dict_date["heures_absences_deductibles"] = self.heures_absences_deductibles

                    # Recherche des absences RTT
                    if self.clsbase.GetValeur("psu_etiquette_rtt") in track.etiquettes :
                        dict_date["absences_rtt"] += track.duree_arrondie




        #         # Recherche des dépassements
        #         if track.IDunite == self.clsbase.GetValeur("IDunite_depassement") :
        #             self.heures_depassements += duree

                # Vérifie dépassement du début puis le dépassement de la fin
                depassement_debut = ("debut", dict_date["presence"]["heure_debut"], dict_date["prevision"]["heure_debut"])
                depassement_fin = ("fin", dict_date["prevision"]["heure_fin"], dict_date["presence"]["heure_fin"])

                for type_depassement, heure_min, heure_max in [depassement_debut, depassement_fin] :
                    depassement_arrondi = datetime.timedelta(0)

                    # Vérifie s'il y a bien une présence
                    if dict_date["presence"]["duree_arrondie"] != datetime.timedelta(0) :

                        # S'il y avait une prévision :
                        if dict_date["prevision"]["duree_arrondie"] != datetime.timedelta(0) :

                            if heure_min < heure_max :

                                # Vérifie si la tolérance est dépassée
                                depassement_reel = UTILS_Dates.TimeEnDelta(heure_max) - UTILS_Dates.TimeEnDelta(heure_min)

                                if depassement_reel > self.duree_tolerance_depassement :

                                    # Vérifie s'il y a un dépassement
                                    if heure_min < heure_max :
                                        depassement_arrondi = UTILS_Dates.CalculerArrondi(arrondi_type=self.arrondi_type, arrondi_delta=self.arrondi_delta, heure_debut=heure_min, heure_fin=heure_max)

                        else :
                            # S'il n'y avait pas de prévision
                            depassement_arrondi = dict_date["presence"]["duree_arrondie"]

                        # Mémorisation du dépassement
                        if depassement_arrondi > datetime.timedelta(0) :
                            dict_date["depassement"] += depassement_arrondi
                            self.heures_depassements += depassement_arrondi

                # Mémorisation des données de la date
                self.dict_dates[date] = dict_date

        # MAJ du track mensualité
        self.MAJ()

    def MAJ(self):
        # Calcul des heures à facturer
        self.heures_a_facturer = self.heures_prevues - self.heures_absences_deductibles + self.heures_regularisation + self.duree_solde_rtt
        self.montant_a_facturer = FloatToDecimal(self.tarif_base * UTILS_Dates.DeltaEnFloat(self.heures_a_facturer))

        # Calcul des dépassements
        self.montant_depassements = FloatToDecimal(self.tarif_depassement * UTILS_Dates.DeltaEnFloat(self.heures_depassements))
        self.montant_a_facturer += self.montant_depassements

        self.heures_a_facturer += self.heures_depassements

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.mois = None
        self.annee = None
        self.IDactivite = None
        self.nomActivite = ""

        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        # self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(EVT_CELL_EDIT_FINISHING, self.handleCellEditFinishing)
        self.donnees = []
        self.InitObjectListView()

        def TimedeltaEditor(olv, rowIndex, subItemIndex):
            ctrl = CTRL_Saisie_duree.CTRL(self)
            return ctrl

        # Register the "editor factory" for wx.Colour objects
        CellEditorRegistry().RegisterCreatorFunction(datetime.timedelta, TimedeltaEditor)

    def handleCellEditFinishing(self, event):
        index = event.rowIndex
        wx.CallAfter(self.MAJtracks)

    def OnItemActivated(self,event):
        self.Detail(None)

    def MAJtracks(self):
        for track in self.donnees :
            track.MAJ()
        self.RefreshObjects()

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        # Préparation de la listeImages
        imageValide = self.AddNamedImages("valide", wx.Bitmap("Images/16x16/Ok4.png", wx.BITMAP_TYPE_PNG))

        def GetImage(track):
            if track.IDprestation != None :
                return "valide"
            else:
                return None

        def FormateDate(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateDDEnFr(dateDD)

        def FormateMontant(montant):
            if montant in ("", None, FloatToDecimal(0.0)) :
                return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateMontant2(montant):
            if montant == None or montant == "" : return ""
            return u"%.5f %s" % (montant, SYMBOLE)

        def FormateDuree(duree):
            if duree in (None, "", datetime.timedelta(seconds=0)):
                return ""
            if type(duree) == datetime.timedelta :
                return UTILS_Dates.DeltaEnStr(duree, separateur="h")
            if type(duree) in (str, unicode) :
                duree = duree.replace(' ','')
                duree = duree.replace(":", "h")
                return duree


        liste_Colonnes = [
            # ColumnDefn(_(u""), "left", 0, "IDprestation", typeDonnee="entier", isEditable=False),
            ColumnDefn(_(u""), "left", 18, "", typeDonnee="texte", imageGetter=GetImage, isEditable=False),
            ColumnDefn(_(u"Individu"), 'left', 150, "individu_nom_complet", typeDonnee="texte", isEditable=False),
            # ColumnDefn(_(u"Mois"), 'left', 100, "label_prestation", typeDonnee="texte", isEditable=False),
            ColumnDefn(_(u"H. forfait."), 'center', 80, "heures_prevues", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Mt. forfait"), 'center', 80, "montant_prevu", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),

            ColumnDefn(_(u"H. prévues"), 'center', 80, "heures_prevues_mois", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Présences"), 'center', 80, "heures_presences", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Abs déduc."), 'center', 80, "heures_absences_deductibles", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Abs non déduc."), 'center', 95, "heures_absences_non_deductibles", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"H. compl."), 'center', 80, "heures_depassements", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"RTT non prises"), 'center', 95, "duree_solde_rtt", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"H. régular."), 'center', 80, "heures_regularisation", typeDonnee="duree", stringConverter=FormateDuree, isEditable=True),

            ColumnDefn(_(u"HEURES"), 'center', 80, "heures_a_facturer", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"MONTANT"), 'center', 80, "montant_a_facturer", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),

            ColumnDefn(_(u""), 'center', 2, "", typeDonnee="texte", isEditable=False),

            ColumnDefn(_(u"Date"), 'center', 80, "date_facturation", typeDonnee="date", stringConverter=FormateDate, isEditable=False),
            ColumnDefn(_(u"H. facturées"), 'center', 80, "heures_facturees", typeDonnee="duree", stringConverter=FormateDuree, isEditable=False),
            ColumnDefn(_(u"Montant fact."), 'center', 90, "montant_facture", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),
            ColumnDefn(_(u"N° Facture"), 'center', 70, "num_facture", typeDonnee="entier", isEditable=False),

            # ColumnDefn(_(u"Taux"), 'center', 80, "taux", typeDonnee="montant", stringConverter=FormateMontant2, isEditable=False),
            # ColumnDefn(_(u"Tarif de base"), 'center', 80, "tarif_base", typeDonnee="montant", stringConverter=FormateMontant2, isEditable=False),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune mensualité"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(2)

        self.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK # ObjectListView.CELLEDIT_DOUBLECLICK

    def SetParametres(self, mois=1, annee=2015, IDactivite=None, nomActivite=""):
        self.mois = mois
        self.annee = annee
        self.IDactivite = IDactivite
        self.nomActivite = nomActivite
        # MAJ des données
        self.MAJ_donnees()

    def MAJ_donnees(self):
        # Recherche des dates extrêmes du mois
        dernierJourMois = calendar.monthrange(self.annee, self.mois)[1]
        date_debut = datetime.date(self.annee, self.mois, 1)
        date_fin = datetime.date(self.annee, self.mois, dernierJourMois)

        if self.IDactivite == None :
            self.IDactivite = 0

        # Recherche des contrats
        DB = GestionDB.DB()
        req = """SELECT IDcontrat, IDindividu
        FROM contrats
        WHERE type='psu' AND date_debut<='%s' AND date_fin>='%s' AND IDactivite=%d
        ;""" % (date_fin, date_debut, self.IDactivite)
        DB.ExecuterReq(req)
        listeContrats = DB.ResultatReq()

        listeIDcontrats = []
        for IDcontrat, IDindividu in listeContrats :
            listeIDcontrats.append(IDcontrat)

        # Recherche des données de chaque contrat
        self.donnees = []
        for IDcontrat in listeIDcontrats :
            clsbase = Base(IDcontrat=IDcontrat, DB=DB)
            clsbase.Calculer()

            # Recherche d'une mensualité valide
            track_mensualite = None
            liste_mensualites = clsbase.GetValeur("tracks_mensualites", [])
            for track in liste_mensualites :
                if track.mois == self.mois and track.annee == self.annee :
                    track_mensualite = track
                    break

            # Création du track
            track = Track(self.mois, self.annee, clsbase, track_mensualite)
            track.MAJ()
            self.donnees.append(track)

        DB.Close()

        # MAJ du listview
        self.MAJ()
        self.CocheListeTout()

    def MAJ(self):
        self.SetObjects(self.donnees)
        self._ResizeSpaceFillingColumns() 

    def GetTracks(self):
        return self.GetObjects()

    def SetTracks(self, tracks=[]):
        self.donnees = tracks
        self.MAJ()

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """        
        # Création du menu contextuel
        menuPop = wx.Menu()

        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Détail
        item = wx.MenuItem(menuPop, 20, _(u"Détail de la mensualité"))
        bmp = wx.Bitmap("Images/16x16/zoom_plus.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Detail, id=20)
        if noSelection == True : item.Enable(False)

        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer la prestation"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)

        menuPop.AppendSeparator()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def Apercu(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par sélectionner une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualités"), intro=self.GetIntro(), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par sélectionner une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des mensualités"), intro=self.GetIntro(), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par sélectionner une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des mensualités"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        if self.IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez commencer par sélectionner une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des mensualités"), autoriseSelections=False)

    def GetIntro(self):
        return u"Mensualités de %s %d de l'activité %s" % (LISTE_MOIS[self.mois-1], self.annee, self.nomActivite)

    def Supprimer(self, event=None):
        if len(self.Selection()) == 0 and len(self.GetCheckedObjects()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune aucune ligne dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.GetCheckedObjects()) > 0 :
            # Suppression multiple
            listeSelections = self.GetCheckedObjects()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les prestations des mensualités cochées ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        else :
            # Suppression unique
            listeSelections = self.Selection()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la prestation de la mensualité sélectionnée ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        # Suppression
        listeSuppressions = []
        for track in listeSelections :
            if track.IDfacture != None :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la prestation de %s car elle apparaît déjà sur une facture !") % track.individu_nom_complet, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

            if track.IDprestation != None :
                listeSuppressions.append(track.IDprestation)

        # Suppression dans la base
        DB = GestionDB.DB()

        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 :
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else :
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM prestations WHERE IDprestation IN %s" % conditionSuppression)
            DB.ExecuterReq("DELETE FROM ventilation WHERE IDprestation IN %s" % conditionSuppression)
            DB.ExecuterReq("DELETE FROM deductions WHERE IDprestation IN %s" % conditionSuppression)

            # MAJ des consommations
            listeUnites = []
            for IDunite in (track.IDunite_prevision, track.IDunite_presence) :
                if IDunite != None :
                    listeUnites.append(IDunite)

            if len(listeUnites) == 0 : conditionUnites = "()"
            elif len(listeUnites) == 1 : conditionUnites = "(%d)" % listeUnites[0]
            else : conditionUnites = str(tuple(listeUnites))

            req = """UPDATE consommations SET IDprestation=NULL
            WHERE IDinscription=%d AND date>='%s' AND date<='%s' AND IDunite IN %s
            ;"""% (track.IDinscription, track.forfait_date_debut, track.forfait_date_fin, conditionUnites)
            DB.ExecuterReq(req)

        DB.Commit()
        DB.Close()

        # MAJ de la liste
        self.MAJ_donnees()

        # Confirmation succès
        dlg = wx.MessageDialog(self, _(u"%d prestations ont été supprimées avec succès !") % len(listeSuppressions), _(u"Suppression terminée"), wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def Detail(self, event=None):
        if len(self.Selection()) == 0 :
           dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune mensualité dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
           dlg.ShowModal()
           dlg.Destroy()
           return False
        track = self.Selection()[0]
        import DLG_Contratpsu_detail
        titre = u"%s %d" % (LISTE_MOIS[self.mois-1], self.annee)
        dlg = DLG_Contratpsu_detail.Dialog(self, track_mensualite=track, titre_detail=titre)
        dlg.ShowModal()
        dlg.Destroy()

    def Valider(self):
        """ Valider les mensualités """
        listeTracks = self.GetCheckedObjects()

        # Vérifications
        if len(listeTracks) == 0 :
           dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune mensualité à générer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
           dlg.ShowModal()
           dlg.Destroy()
           return False

        for track in listeTracks :
            if track.IDprestation != None :
                dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas sélectionner des lignes dont les mensualités ont déjà été générées !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la validation des %d mensualités sélectionnées sur le mois de %s %d ?" % (len(listeTracks), LISTE_MOIS[self.mois-1], self.annee)), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Enregistrement des mensualités
        DB = GestionDB.DB()

        for track in listeTracks :
            listeDonnees = (
                ("IDcompte_payeur", track.clsbase.GetValeur("IDcompte_payeur", None)),
                ("date", track.date_facturation),
                ("categorie", "consommation"),
                ("label", track.label_prestation),
                ("montant_initial", track.montant_a_facturer),
                ("montant", track.montant_a_facturer),
                ("IDactivite", track.clsbase.GetValeur("IDactivite", None)),
                ("IDtarif", track.clsbase.GetValeur("IDtarif", None)),
                ("IDfacture", track.IDfacture),
                ("IDfamille", track.clsbase.GetValeur("IDfamille", None)),
                ("IDindividu", track.clsbase.GetValeur("IDindividu", None)),
                ("forfait", None),
                ("temps_facture", UTILS_Dates.DeltaEnStr(track.heures_a_facturer, ":")),
                ("IDcategorie_tarif", track.clsbase.GetValeur("IDcategorie_tarif", None)),
                ("forfait_date_debut", track.forfait_date_debut),
                ("forfait_date_fin", track.forfait_date_fin),
                ("IDcontrat", track.clsbase.IDcontrat),
            )
            if track.IDprestation == None :
                IDprestation = DB.ReqInsert("prestations", listeDonnees)
            else :
                IDprestation = track.IDprestation
                DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestation)

            # MAJ des consommations
            listeUnites = []
            for IDunite in (track.IDunite_prevision, track.IDunite_presence) :
                if IDunite != None :
                    listeUnites.append(IDunite)
            if len(listeUnites) == 0 : conditionUnites = "()"
            elif len(listeUnites) == 1 : conditionUnites = "(%d)" % listeUnites[0]
            else : conditionUnites = str(tuple(listeUnites))

            req = """UPDATE consommations SET IDprestation=%d
            WHERE IDinscription=%d AND date>='%s' AND date<='%s' AND IDunite IN %s
            ;"""% (IDprestation, track.IDinscription, track.forfait_date_debut, track.forfait_date_fin, conditionUnites)
            DB.ExecuterReq(req)

            # MAJ du track
            track.IDprestation = IDprestation
            track.heures_facturees = track.heures_a_facturer
            track.montant_facture = track.montant_a_facturer
            self.RefreshObject(track)

        DB.Commit()
        DB.Close()

        # Confirmation succès
        dlg = wx.MessageDialog(self, _(u"Les mensualités ont été générées avec succès !"), _(u"Génération terminée"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True




# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "individu_nom_complet" : {"mode" : "nombre", "singulier" : _(u"individu"), "pluriel" : _(u"individus"), "alignement" : wx.ALIGN_CENTER},
            "heures_prevues" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_prevu" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},

            "heures_prevues_mois" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_presences" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_absences_deductibles" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_absences_non_deductibles" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_depassements" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "heures_regularisation" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},

            "heures_a_facturer" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_a_facturer" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},

            "heures_facturees" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER, "format" : "temps"},
            "montant_facture" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        ctrl = ListviewAvecFooter(panel, kwargs={})
        listview = ctrl.GetListview()
        listview.MAJ()

        listview.SetParametres(mois=12, annee=2015, IDactivite=43)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(ctrl, 1, wx.ALL|wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((1200, 400))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
