#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB
import UTILS_Dates
import DLG_Saisie_contrat_conso_detail
import cPickle
import copy

import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


LISTE_JOURS = [_(u"LU"), _(u"MA"), _(u"ME"), _(u"JE"), _(u"VE"), _(u"SA"), _(u"DI")]

def ConvertJoursStr(listeJours):
    listeStr = []
    for IDjour in listeJours :
        listeStr.append(LISTE_JOURS[IDjour])
    return "+".join(listeStr)
    
  
class Track(object):
    def __init__(self, parent, dictValeurs={}, index=0):
        self.index = index
        self.dictValeurs = dictValeurs
        self.parent = parent

        self.semaines = dictValeurs["semaines"]
        self.jours_vacances = dictValeurs["jours_vacances"]
        self.jours_scolaires = dictValeurs["jours_scolaires"]
        self.feries = dictValeurs["feries"]
        self.unites = dictValeurs["unites"]
        
        # texte conditions
        listeTemp = []
        for code, label in DLG_Saisie_contrat_conso_detail.LISTE_SEMAINES :
            if self.semaines == code and code != 1 :
                listeTemp.append(label)
        if len(self.jours_scolaires) > 0 : listeTemp.append(ConvertJoursStr(self.jours_scolaires) + " (scol)")
        if len(self.jours_vacances) > 0 : listeTemp.append(ConvertJoursStr(self.jours_vacances) + " (vac)")
        if self.feries == True : listeTemp.append(_(u"Fériés inclus"))
        self.criteres_txt = ", ".join(listeTemp)
        
        # Texte unités
        listeTemp = []
        for dictUnite in self.unites :
            if self.parent.dictUnites.has_key(dictUnite["IDunite"]) :
                nomUnite = self.parent.dictUnites[dictUnite["IDunite"]]["nom"]
                if dictUnite.has_key("options") :
                    if dictUnite["options"].has_key("heure_debut") :
                        nomUnite += u" (%s-%s)" % (dictUnite["options"]["heure_debut"].replace(":", "h"), dictUnite["options"]["heure_fin"].replace(":", "h"))
                listeTemp.append(nomUnite)
        self.unites_txt = " + ".join(listeTemp)
        
        
        

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDactivite = kwds.pop("IDactivite", None)
        self.IDmodele = kwds.pop("IDmodele", None)
        self.IDunite = kwds.pop("IDunite", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeDonnees = []

        # Init autres données
        self.listeVacances = self.GetListeVacances()
        self.listeFeries = self.GetListeFeries()

        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.donnees = []
        self.InitObjectListView()
        
        self.Importation_unites() 
        
    def Importation_unites(self):
        # Récupération des unités
        DB = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        DB.Close() 
        self.dictUnites = {}
        for IDunite, nom, abrege, type, heure_debut, heure_fin in listeDonnees :
            self.dictUnites[IDunite] = {"nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin}

    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.donnees = []
        index = 0
        for dictTemp in self.listeDonnees :
            track = Track(self, dictTemp, index)
            self.donnees.append(track)
            index += 1
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))
        
        def FormateNumFacture(numero):
            if numero == None :
                return ""
            else :
                return "n°%d"% numero
            
        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "", typeDonnee="entier"),
            ColumnDefn(_(u"Unités"), 'left', 150, "unites_txt", typeDonnee="texte"),
            ColumnDefn(_(u"Conditions"), 'left', 200, "criteres_txt", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun paramètre de planning"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(0)
        
    def MAJ(self):
        self.InitModel()
        self.SetObjects(self.donnees)
        self._ResizeSpaceFillingColumns() 

    def SetDonnees(self, listeDonnees={}):
        self.listeDonnees = listeDonnees
        self.MAJ() 
    
    def GetDonnees(self):
        return self.listeDonnees
    
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

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
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
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des périodes de contrats"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des périodes de contrats"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des périodes de contrats"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des périodes de contrats"), autoriseSelections=False)

    def Ajouter(self, event):  
        dlg = DLG_Saisie_contrat_conso_detail.Dialog(self, IDactivite=self.IDactivite, IDunite=self.IDunite)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees() 
            self.listeDonnees.append(dictDonnees)
            self.MAJ() 
        dlg.Destroy()
        
    def Modifier(self, event):  
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun élément de planning à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie_contrat_conso_detail.Dialog(self, IDactivite=self.IDactivite, IDunite=self.IDunite)
        dlg.SetDonnees(track.dictValeurs)
        if dlg.ShowModal() == wx.ID_OK:
            self.listeDonnees[track.index] = dlg.GetDonnees() 
            self.MAJ() 
        dlg.Destroy()

    def Supprimer(self, event):  
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun élément de planning à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        track = self.Selection()[0]     
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer l'élément de planning sélectionné ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        
        self.listeDonnees.pop(track.index)
        self.MAJ() 

    def GetElementsStr(self):
        return cPickle.dumps(self.listeDonnees)
    
    def SetElementsStr(self, donnees=""):
        if donnees == None : return
        self.listeDonnees = cPickle.loads(str(donnees))
        self.MAJ() 

    def GetListeVacances(self):
        db = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances
        ORDER BY date_debut; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

    def GetListeFeries(self):
        db = GestionDB.DB()
        req = """SELECT type, nom, jour, mois, annee
        FROM jours_feries
        ; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

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

    def GetConso(self, date_debut=None, date_fin=None):
        """ Récupération des conso générées par le planning saisi """
        donneesPlanning = self.GetDonnees()

        listeConso = []
        for dictPlanning in donneesPlanning :

            # Recherche des dates
            listeDates = []
            date = date_debut
            semaines = dictPlanning["semaines"]
            numSemaine = copy.copy(semaines)
            dateTemp = date
            while date < (date_fin + datetime.timedelta(days=1)) :

                # Vérifie période et jour
                valide = False
                if self.EstEnVacances(date) :
                    if date.weekday() in dictPlanning["jours_vacances"] :
                        valide = True
                else :
                    if date.weekday() in dictPlanning["jours_scolaires"] :
                        valide = True

                # Vérifie si férié
                if dictPlanning["feries"] == False and self.EstFerie(date) == True :
                    valide = False

                # Calcul le numéro de semaine
                if len(listeDates) > 0 :
                    if date.weekday() < dateTemp.weekday() :
                        numSemaine += 1

                # Fréquence semaines
                if semaines in (2, 3, 4) :
                    if numSemaine % semaines != 0 :
                        valide = False

                # Semaines paires et impaires
                if valide == True and semaines in (5, 6) :
                    numSemaineAnnee = date.isocalendar()[1]
                    if numSemaineAnnee % 2 == 0 and semaines == 6 :
                        valide = False
                    if numSemaineAnnee % 2 != 0 and semaines == 5 :
                        valide = False

                # Ajout de la date à la liste
                if valide == True :
                    listeDates.append(date)

                dateTemp = date
                date += datetime.timedelta(days=1)

            # Mémorisation des consommations
            for date in listeDates :

                for dictUnite in dictPlanning["unites"] :
                    IDunite = dictUnite["IDunite"]
                    options = dictUnite["options"]

                    if options.has_key("heure_debut"):
                        heure_debut = options["heure_debut"]
                    else :
                        heure_debut = self.dictUnites[IDunite]["heure_debut"]
                    if options.has_key("heure_fin"):
                        heure_fin = options["heure_fin"]
                    else :
                        heure_fin = self.dictUnites[IDunite]["heure_fin"]

                    if options.has_key("quantite"):
                        quantite = options["quantite"]
                    else :
                        quantite = None

                    dictConso = {
                        "IDconso" : None,
                        "date" : date,
                        "IDunite" : IDunite,
                        "heure_debut" : heure_debut,
                        "heure_fin" : heure_fin,
                        "quantite" : quantite,
                        "etat" : "reservation",
                        "etiquettes" : [],
                        }
                    listeConso.append(dictConso)

        return listeConso


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_soldes
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap("Images/16x16/Loupe.png", wx.BITMAP_TYPE_PNG))
        
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch)
        self.Bind(wx.EVT_TEXT, self.OnDoSearch)

    def OnSearch(self, evt):
        self.Recherche()
            
    def OnCancel(self, evt):
        self.SetValue("")
        self.Recherche()

    def OnDoSearch(self, evt):
        self.Recherche()
        
    def Recherche(self):
        txtSearch = self.GetValue()
        self.ShowCancelButton(len(txtSearch))
        self.listView.GetFilter().SetText(txtSearch)
        self.listView.RepopulateList()
        self.Refresh() 




class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        listview = ListView(panel, id=-1, IDactivite=1, IDmodele=1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        listview.MAJ() 
        
        self.bouton_test = wx.Button(panel, -1, _(u"Test de sauvegarde"))
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(listview, 1, wx.ALL|wx.EXPAND, 10)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 10)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))
        
        self.Bind(wx.EVT_BUTTON, self.OnTest, self.bouton_test)
        
    def OnTest(self, event):
        print "ok"
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
