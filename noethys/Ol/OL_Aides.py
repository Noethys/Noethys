#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs


DICT_INDIVIDUS = {}

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))



class Track(object):
    def __init__(self, donnees):
##        IDaide, IDfamille, IDactivite, nom, date_debut, date_fin, IDcaisse, montant_max, nbre_dates_max
        self.IDaide = donnees["IDaide"]
        self.IDfamille = donnees["IDfamille"]
        self.IDactivite = donnees["IDactivite"]
        self.nom_activite = donnees["abregeActivite"]
        self.nom = donnees["nomAide"]
        self.date_debut = DateEngEnDateDD(donnees["dateDebutAide"])
        self.date_fin = DateEngEnDateDD(donnees["dateFinAide"])
        self.IDcaisse = donnees["IDcaisse"]
        self.nom_caisse = donnees["nomCaisse"]
        self.montant_max = donnees["montantMax"]
        self.nbre_dates_max = donnees["nbreDatesMax"]
        self.total_deductions = donnees["totalDeductions"]
        self.nbre_deductions = len(donnees["listeDates"])
        
        if self.total_deductions == None : self.total_deductions = 0.0
        if self.nbre_deductions == None : self.nbre_deductions = 0
        
        if self.montant_max != None :
            self.texte_montant_max = _(u"%.2f %s (%.2f %s max)") % (self.total_deductions, SYMBOLE, self.montant_max, SYMBOLE)
        else:
            self.texte_montant_max = u"%.2f %s" % (self.total_deductions, SYMBOLE)
            
        if self.nbre_dates_max != None :
            self.texte_dates_max = _(u"%d dates (%d dates max)") % (self.nbre_deductions, self.nbre_dates_max)
        else:
            self.texte_dates_max = _(u"%d dates") % self.nbre_deductions
        
        # Encore valide ?
        dateJour = datetime.date.today()
        if self.date_debut <= dateJour and self.date_fin >= dateJour :
            self.valide = True
        else:
            self.valide = False
        
        # Noms des bénéficiaires
        self.texteBeneficiaires = u""
        if self.IDaide in DICT_INDIVIDUS :
            for IDindividu, nom, prenom in DICT_INDIVIDUS[self.IDaide] :
                self.texteBeneficiaires += u"%s, " % prenom
            if len(DICT_INDIVIDUS[self.IDaide]) > 0 :
                self.texteBeneficiaires = self.texteBeneficiaires[:-2]
                
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        if self.GetParent().GetName() == "DLG_Choix_modele_aide" :
            # Sélection d'un modèle
            self.GetParent().OnBoutonOk(None)
        else:
            # Modification 
            self.Modifier(None)
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        global DICT_INDIVIDUS
        
        listeID = None
        criteresAides = ""
        if self.IDfamille == None :
            criteresAides = "WHERE aides.IDfamille IS NULL"
        else:
##            criteresAides = "WHERE aides.IDfamille IS NOT NULL"
            criteresAides = "WHERE aides.IDfamille=%d" % self.IDfamille
        
        # Récupération des aides
        db = GestionDB.DB()
        req = """SELECT 
        aides.IDaide, aides.IDfamille, 
        aides.IDactivite, activites.abrege, 
        aides.nom, aides.date_debut, aides.date_fin, 
        aides.IDcaisse, caisses.nom,
        aides.montant_max, aides.nbre_dates_max
        FROM aides
        LEFT JOIN activites ON activites.IDactivite = aides.IDactivite
        LEFT JOIN caisses ON caisses.IDcaisse = aides.IDcaisse
        %s
        ORDER BY aides.date_debut
        ;""" % criteresAides
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        
        dictDonnees = {}
        for IDaide, IDfamille, IDactivite, abregeActivite, nomAide, dateDebutAide, dateFinAide, IDcaisse, nomCaisse, montantMax, nbreDatesMax in listeDonnees :
            dictTemp = {"IDaide":IDaide, "IDfamille":IDfamille, "IDactivite":IDactivite, "abregeActivite":abregeActivite, "nomAide":nomAide, 
                            "dateDebutAide":dateDebutAide, "dateFinAide":dateFinAide, "IDcaisse":IDcaisse, "nomCaisse":nomCaisse, 
                            "montantMax":montantMax, "nbreDatesMax":nbreDatesMax, "totalDeductions":0.0, "listeDates":[]}
            if (IDaide in dictDonnees) == False :
                dictDonnees[IDaide] = dictTemp
        
        # Récupération des déductions déjà effectuées
        req = """SELECT IDdeduction, date, montant, deductions.IDaide
        FROM deductions
        LEFT JOIN aides ON aides.IDaide = deductions.IDaide
        %s;""" % criteresAides
        db.ExecuterReq(req)
        listeDeductions = db.ResultatReq()

        for IDdeduction, date, montant, IDaide in listeDeductions :
            if IDaide in dictDonnees :
                dictDonnees[IDaide]["totalDeductions"] += montant
                if date not in dictDonnees[IDaide]["listeDates"] :
                    dictDonnees[IDaide]["listeDates"].append(date)

        # Récupération des noms des bénéficiaires
        req = """SELECT 
        aides_beneficiaires.IDaide_beneficiaire, aides_beneficiaires.IDaide, aides_beneficiaires.IDindividu,
        individus.nom, individus.prenom
        FROM aides_beneficiaires
        LEFT JOIN aides ON aides.IDaide = aides_beneficiaires.IDaide
        LEFT JOIN individus ON individus.IDindividu = aides_beneficiaires.IDindividu
        ;"""
        db.ExecuterReq(req)
        listeNoms = db.ResultatReq()
        db.Close()
        
        dictNoms = {}
        for IDaide_beneficiaire, IDaide, IDindividu, nom, prenom in listeNoms :
            if (IDaide in dictNoms) == False :
                dictNoms[IDaide] = [] 
            if IDindividu not in dictNoms[IDaide] :
                dictNoms[IDaide].append((IDindividu, nom, prenom))
        DICT_INDIVIDUS = dictNoms

        listeListeView = []
        for IDaide, dictValeurs in dictDonnees.items() :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(dictValeurs)
                listeListeView.append(track)
                if self.selectionID == IDaide :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                    
        def FormateDateLong(dateDD):
            return DateComplete(dateDD)

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))
        
        if self.IDfamille == None :
            # Version MODELES
            liste_Colonnes = [
                ColumnDefn(_(u"ID"), "left", 0, "IDaide", typeDonnee="entier"),
                ColumnDefn(u"Du", 'left', 75, "date_debut", typeDonnee="date", stringConverter=FormateDateCourt),
                ColumnDefn(_(u"Au"), 'left', 75, "date_fin", typeDonnee="date", stringConverter=FormateDateCourt),
                ColumnDefn(_(u"Nom"), 'left', 160, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Activité"), 'left', 60, "nom_activite", typeDonnee="texte"),
                ColumnDefn(_(u"Caisse"), 'left', 140, "nom_caisse", typeDonnee="texte"), 
                ]
        else:
            # Version FAMILLE
            liste_Colonnes = [
                ColumnDefn(_(u"ID"), "left", 0, "IDaide", typeDonnee="entier"),
                ColumnDefn(u"Du", 'left', 75, "date_debut", typeDonnee="date", stringConverter=FormateDateCourt),
                ColumnDefn(_(u"Au"), 'left', 75, "date_fin", typeDonnee="date", stringConverter=FormateDateCourt),
                ColumnDefn(_(u"Nom"), 'left', 130, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Activité"), 'left', 60, "nom_activite", typeDonnee="texte"),
                ColumnDefn(_(u"Caisse"), 'left', 80, "nom_caisse", typeDonnee="texte"), 
                ColumnDefn(_(u"Bénéficiaires"), 'left', 130, "texteBeneficiaires", typeDonnee="texte"),
                ColumnDefn(_(u"Total des déductions"), 'left', 140, "texte_montant_max", typeDonnee="texte"),
                ColumnDefn(_(u"Nbre de dates"), 'left', 130, "texte_dates_max", typeDonnee="texte"),
                ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune aide journalière"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
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
        if ID == None :
            self.DefileDernier() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDaide
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
            
        menuPop.AppendSeparator()

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
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Texte2.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des aides journalières"), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des aides journalières"), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des aides journalières"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des aides journalières"))

    def Ajouter(self, event):
        if self.IDfamille == None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_aides", "creer") == False : return
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_aides", "creer") == False : return
        from Dlg import DLG_Saisie_aide
        dlg = DLG_Saisie_aide.Dialog(self, IDaide=None, IDfamille=self.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.IDaide = dlg.GetIDaide()
            self.MAJ(self.IDaide)
        dlg.Destroy()

    def Modifier(self, event):
        if self.IDfamille== None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_aides", "modifier") == False : return
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_aides", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune aide à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDaide = self.Selection()[0].IDaide
        from Dlg import DLG_Saisie_aide
        dlg = DLG_Saisie_aide.Dialog(self, IDaide=IDaide, IDfamille=self.IDfamille) 
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDaide)
        dlg.Destroy() 

    def Supprimer(self, event):
        if self.IDfamille== None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_modeles_aides", "supprimer") == False : return
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_aides", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune aide à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDaide = self.Selection()[0].IDaide
        
        # Vérifie que cette aide n'a pas déjà été utilisée pour une prestation
        DB = GestionDB.DB()
        req = """SELECT IDdeduction, IDaide
        FROM deductions
        WHERE IDaide=%d
        ;""" % IDaide
        DB.ExecuterReq(req)
        listeDeductions = DB.ResultatReq()
        DB.Close() 
        if len(listeDeductions) > 0 :
            dlg = wx.MessageDialog(self, _(u"Cette aide a déjà été attribuée à %s déductions. Il est donc impossible de la supprimer !") % len(listeDeductions), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette aide ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("aides", "IDaide", IDaide)
            DB.ReqDEL("aides_beneficiaires", "IDaide", IDaide)
            DB.ReqDEL("aides_montants", "IDaide", IDaide)
            DB.ReqDEL("aides_combinaisons", "IDaide", IDaide)
            DB.ReqDEL("aides_combi_unites", "IDaide", IDaide)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()









# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un modèle..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
        nbreColonnes = self.listView.GetColumnCount()
        self.listView.SetFilter(Filter.TextSearch(self.listView, self.listView.columns[0:nbreColonnes]))
        
        self.SetCancelBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.SetSearchBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Loupe.png"), wx.BITMAP_TYPE_PNG))
        
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, IDfamille=7, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
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
