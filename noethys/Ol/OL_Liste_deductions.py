#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB

from Utils import UTILS_Dates
from Utils import UTILS_Titulaires
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter



        
class Track(object):
    def __init__(self, parent, donnees):
        self.IDdeduction = donnees["IDdeduction"]
        self.IDprestation = donnees["IDprestation"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]
        self.IDindividu = donnees["IDindividu"]
        self.date = donnees["date"]
        self.montant = donnees["montant"]
        self.label = donnees["label"]
        self.IDaide = donnees["IDaide"]
        if self.IDindividu != None :
            self.nomIndividu= donnees["nomIndividu"]
            self.prenomIndividu = donnees["prenomIndividu"]
            if self.prenomIndividu != None :
                self.nomComplet = u"%s %s" % (self.nomIndividu, self.prenomIndividu)
            else :
                self.nomComplet = self.nomIndividu
        else :
            self.nomIndividu = u""
            self.prenomIndividu = u""
            self.nomComplet = u""
        self.date_naiss = donnees["date_naiss"]
        self.labelPrestation = donnees["labelPrestation"]
        self.montantPrestation = donnees["montantPrestation"]
        self.montantInitialPrestation = donnees["montantInitialPrestation"]
        self.datePrestation = donnees["datePrestation"]
        self.IDfacture = donnees["IDfacture"]
        
        if self.labelPrestation != None and self.montantPrestation != None and self.montantInitialPrestation != None :
            self.textePrestation = _(u"%s (initial : %.2f %s - final : %.2f %s)") % (self.labelPrestation, self.montantInitialPrestation, SYMBOLE, self.montantPrestation, SYMBOLE)
        else:
            self.textePrestation = u""
        
        self.IDfamille = donnees["IDfamille"]
        self.nomTitulaires = parent.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]

        self.IDcaisse = donnees["IDcaisse"]
        self.num_allocataire = donnees["num_allocataire"]
        self.nomCaisse = donnees["nomCaisse"]

        self.IDactivite = donnees["IDactivite"]
        self.abregeActivite = donnees["abregeActivite"]
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires()

        self.date_debut = None
        self.date_fin = None
        self.listeActivites = "toutes"
        self.filtres = []
        self.labelParametres = ""

        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
##        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        # Modification 
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()
    
    def Importation(self):
        """ Importation """
        # Condition dates
        condition = " (deductions.date>='%s' and deductions.date<='%s') " % (self.date_debut, self.date_fin)

        # Conditions Activités
        if self.listeActivites == "toutes" or self.listeActivites == None :
            conditionActivites = ""
        else :
            if len(self.listeActivites) == 0 : conditionActivites = "AND prestations.IDactivite IN ()"
            elif len(self.listeActivites) == 1 : conditionActivites = "AND prestations.IDactivite IN (%d)" % self.listeActivites[0]
            else : conditionActivites = "AND prestations.IDactivite IN %s" % str(tuple(self.listeActivites))

        # Filtres
        listeFiltres = []
        texteFiltres = ""
        if "consommation" in self.filtres : 
            listeFiltres.append("(prestations.categorie='consommation' %s)" % conditionActivites)
        if "cotisation" in self.filtres : 
            listeFiltres.append("(prestations.categorie='cotisation')")
        if "location" in self.filtres :
            listeFiltres.append("(prestations.categorie='location')")
        if "autre" in self.filtres : 
            listeFiltres.append("(prestations.categorie='autre')")
        if len(listeFiltres) > 0 :
            texteFiltres = "AND (%s)" % " OR ".join(listeFiltres)
        else :
            texteFiltres = " AND deductions.IDdeduction=0"

        db = GestionDB.DB()
        req = """SELECT 
        IDdeduction, deductions.IDprestation, deductions.IDcompte_payeur, deductions.date, deductions.montant, deductions.label, IDaide, 
        individus.nom, individus.prenom, individus.date_naiss,
        prestations.label, prestations.montant, prestations.montant_initial, prestations.IDfamille, prestations.IDactivite, activites.abrege, prestations.IDindividu, prestations.date, prestations.IDfacture,
        familles.IDcaisse, familles.num_allocataire, caisses.nom
        FROM deductions
        LEFT JOIN prestations ON prestations.IDprestation = deductions.IDprestation
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
        LEFT JOIN familles ON familles.IDfamille = prestations.IDfamille
        LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
        WHERE %s %s;""" % (condition, texteFiltres)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close() 
        listeDeductions = []
        for IDdeduction, IDprestation, IDcompte_payeur, date, montant, label, IDaide, nomIndividu, prenomIndividu, date_naiss, labelPrestation, montantPrestation, montantInitialPrestation, IDfamille, IDactivite, abregeActivite, IDindividu, datePrestation, IDfacture, IDcaisse, num_allocataire, nomCaisse in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            datePrestation = UTILS_Dates.DateEngEnDateDD(datePrestation)
            date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)
            dictTemp = {
                "IDdeduction" : IDdeduction, "IDprestation" : IDprestation, "IDcompte_payeur" : IDcompte_payeur, 
                "date" : date, "montant" : montant, "label" : label, "IDaide" : IDaide, 
                "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu, "date_naiss" : date_naiss,
                "labelPrestation" : labelPrestation, "montantPrestation" : montantPrestation, "montantInitialPrestation" : montantInitialPrestation,
                "IDfamille" : IDfamille, "IDactivite" : IDactivite, "abregeActivite" : abregeActivite, "IDindividu" : IDindividu, "datePrestation" : datePrestation, "IDfacture" : IDfacture,
                "IDcaisse" : IDcaisse, "num_allocataire" : num_allocataire, "nomCaisse" : nomCaisse,
                }
            listeDeductions.append(dictTemp)
        return listeDeductions

    def GetTracks(self):
        """ Récupération des données """
        listeDeductions = self.Importation() 

        listeID = None
        listeListeView = []
        for item in listeDeductions :
            valide = True            
            if listeID != None :
                if item["IDdeduction"] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item["IDdeduction"] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateDateLong(dateDD):
            return UTILS_Dates.DateComplete(dateDD)

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)
        
        def FormateFacture(IDfacture):
            if IDfacture == None :
                return _(u"Non")
            else :
                return _(u"Oui")

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDdeduction", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 90, "date", typeDonnee="date", stringConverter=FormateDateCourt), 
            ColumnDefn(_(u"Famille"), 'left', 160, "nomTitulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Caisse"), 'left', 80, "nomCaisse", typeDonnee="texte"),
            ColumnDefn(_(u"n° Alloc."), 'left', 80, "num_allocataire", typeDonnee="texte"),
            ColumnDefn(_(u"Individu"), 'left', 140, "nomComplet", typeDonnee="texte"),
            ColumnDefn(_(u"Date naiss."), 'left', 90, "date_naiss", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Label déduction"), 'left', 220, "label", typeDonnee="texte"), 
            ColumnDefn(_(u"Montant"), 'right', 90, "montant", typeDonnee="montant", stringConverter=FormateMontant), 
            ColumnDefn(_(u"Label prestation"), 'left', 150, "labelPrestation", typeDonnee="texte"), 
            ColumnDefn(_(u"Date prestation"), 'left', 90, "datePrestation", typeDonnee="date", stringConverter=FormateDateCourt), 
            ColumnDefn(_(u"Activité"), 'left', 70, "abregeActivite", typeDonnee="texte"), 
            ColumnDefn(_(u"Montant initial"), 'right', 90, "montantInitialPrestation", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Montant final"), 'right', 90, "montantPrestation", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Facturé"), 'left', 60, "IDfacture", typeDonnee="texte", stringConverter=FormateFacture),
            ]

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune déduction"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)

    def MAJ(self, date_debut=None, date_fin=None, listeActivites=[], filtres=[], ID=None, labelParametres=""):     
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.listeActivites = listeActivites
        self.filtres = filtres
        self.labelParametres = labelParametres

        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDdeduction
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()

        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre" : _(u"Liste des déductions"),
            "intro" : self.labelParametres,
            "total" : _(u"%s déductions") % len(self.donnees),
            "orientation" : wx.LANDSCAPE,
            }
        return dictParametres

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune déduction à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDdeduction = self.Selection()[0].IDdeduction
        label = self.Selection()[0].label
        montant = self.Selection()[0].montant
        IDprestation = self.Selection()[0].IDprestation
        
        from Dlg import DLG_Saisie_deduction
        dlg = DLG_Saisie_deduction.Dialog(self, IDdeduction=IDdeduction)
        dlg.SetLabel(label)
        dlg.SetMontant(montant)
        if dlg.ShowModal() == wx.ID_OK:
            newLabel = dlg.GetLabel()
            newMontant = dlg.GetMontant()
            DB = GestionDB.DB()
            listeDonnees = [    
                ("label", newLabel),
                ("montant", newMontant),
                ]
            DB.ReqMAJ("deductions", listeDonnees, "IDdeduction", IDdeduction)
            DB.Close()
            self.MAJ(date_debut=self.date_debut, date_fin=self.date_fin, listeActivites=self.listeActivites, filtres=self.filtres, ID=IDdeduction)
        dlg.Destroy() 

    def Supprimer(self, event):
        if len(self.Selection()) == 0 and len(self.GetTracksCoches()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune déduction à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if len(self.GetTracksCoches()) > 0 :
            # Suppression multiple
            listeSelections = self.GetTracksCoches()
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer les %d déductions cochées ?") % len(listeSelections), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        else :
            # Suppression unique
            listeSelections = self.Selection()        
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer la déduction n°%d ?") % listeSelections[0].IDdeduction, _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Vérifie les prestations déjà facturées
        nbreFactures = 0
        for track in listeSelections :
            if track.IDfacture != None :
                nbreFactures += 1
        if nbreFactures > 0 :
            dlg = wx.MessageDialog(self, _(u"Suppression impossible : %d déductions sont associées à des prestations déjà facturées !") % nbreFactures, _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False                
            
        # Sauvegarde
        listeSupprDeductions = []
        listeSupprVentilations = []
        listeModifications = []
        dictMontantsPrestations = {}
        for track in listeSelections :
            if track.IDprestation in dictMontantsPrestations :
                montantPrestation = dictMontantsPrestations[track.IDprestation]
            else :
                montantPrestation = track.montantPrestation
            listeSupprDeductions.append(track.IDdeduction)
            if track.IDprestation not in listeSupprVentilations :
                listeSupprVentilations.append(track.IDprestation)
            newMontantPrestation = montantPrestation + track.montant
            listeModifications.append((newMontantPrestation, track.IDprestation))
            dictMontantsPrestations[track.IDprestation] = newMontantPrestation
            
        DB = GestionDB.DB()
        if len(listeSupprDeductions) > 0 :
            if len(listeSupprDeductions) == 1 : conditionSuppressions = "(%d)" % listeSupprDeductions[0]
            else : conditionSuppressions = str(tuple(listeSupprDeductions))
            DB.ExecuterReq("DELETE FROM deductions WHERE IDdeduction IN %s" % conditionSuppressions)
        if len(listeSupprVentilations) > 0 :
            if len(listeSupprVentilations) == 1 : conditionSuppressions = "(%d)" % listeSupprVentilations[0]
            else : conditionSuppressions = str(tuple(listeSupprVentilations))
            DB.ExecuterReq("DELETE FROM ventilation WHERE IDprestation IN %s" % conditionSuppressions)
        if len(listeModifications) > 0 :
            DB.Executermany(_(u"UPDATE prestations SET montant=? WHERE IDprestation=?"), listeModifications, commit=False)
        DB.Commit()
        DB.Close() 

        # MAJ affichage
        self.MAJ(date_debut=self.date_debut, date_fin=self.date_fin, listeActivites=self.listeActivites, filtres=self.filtres)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def GetTotalDeductions(self):
        """ Est utilisée par la DLG_Saisie_prestation pour connaître le montant total des déductions """
        total = 0.0
        for IDdeduction, dictDeduction in self.dictDeductions.items() :
            total += dictDeduction["montant"]
        return total


# -------------------------------------------------------------------------------------------------------------------------------------------


class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomTitulaires" : {"mode" : "nombre", "singulier" : _(u"déduction"), "pluriel" : _(u"déductions"), "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            "montantInitialPrestation" : {"mode" : "total"},
            "montantPrestation" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(date_debut=datetime.date(2010, 1, 1), date_fin=datetime.date(2018, 1, 1), listeActivites="toutes", filtres=['cotisation', 'consommation', 'location', 'autre'])
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 200))

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
