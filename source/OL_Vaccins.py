#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import CTRL_Saisie_date
import GestionDB
from dateutil import relativedelta

import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Utilisateurs

DICT_MALADIES = {}
DICT_LIENS_MALADIES = {}


def FormatDuree(duree):
    posM = duree.find("m")
    posA = duree.find("a")
    jours = int(duree[1:posM-1])
    mois = int(duree[posM+1:posA-1])
    annees = int(duree[posA+1:])
    return jours, mois, annees

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class Track(object):
    def __init__(self, donnees):
        self.IDvaccin = donnees[0]
        self.IDindividu = donnees[1]
        self.IDtype_vaccin = donnees[2]
        self.date = donnees[3]
        self.dateDD = datetime.date(int(self.date[:4]), int(self.date[5:7]), int(self.date[8:10]))
        self.nom = donnees[4]
        self.duree_validite = donnees[5]
        # validité
        jours, mois, annees = FormatDuree(self.duree_validite)
        self.date_expiration, self.nbreJoursRestants = self.CalcValidite(jours, mois, annees)
        # Maladies associées
        self.txt_maladies_associees = ""
        if DICT_LIENS_MALADIES.has_key(self.IDtype_vaccin) :
            self.listeMaladiesAssociees = DICT_LIENS_MALADIES[self.IDtype_vaccin]
            for IDtype_maladie in self.listeMaladiesAssociees :
                self.txt_maladies_associees += DICT_MALADIES[IDtype_maladie]["nom"] + ", "
            self.txt_maladies_associees = self.txt_maladies_associees[:-2]
        else:
            self.listeMaladiesAssociees = []
            
    def CalcValidite(self, jours, mois, annees):
        date_jour = datetime.date.today()
        date_vaccin = self.dateDD
        dateJour, dateMois, dateAnnee = date_vaccin.day, date_vaccin.month, date_vaccin.year
        
        if jours==0 and mois==0 and annees==0:
            # Si illimité
            dateFin = datetime.date(2999, 1, 1)
            return str(dateFin), None
        else:
            # Limité
            dateFin = date_vaccin
            if jours != 0 : dateFin = dateFin + relativedelta.relativedelta(days=+jours)
            if mois != 0 : dateFin = dateFin + relativedelta.relativedelta(months=+mois)
            if annees != 0 : dateFin = dateFin + relativedelta.relativedelta(years=+annees)

##            # Calcul des jours
##            if jours != 0:
##                dateFin = date_vaccin + (datetime.timedelta(days = jours))
##                dateJour, dateMois, dateAnnee = dateFin.day, dateFin.month, dateFin.year
##
##            # Calcul des mois
##            if mois != 0:
##                if dateMois + mois > 12:
##                    for temp in range(0, mois):
##                        dateMois += 1
##                        if dateMois > 12 :
##                            dateAnnee += 1
##                            dateMois = 1
##                else:
##                    dateMois = dateMois + mois
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
##                dateJour, dateMois, dateAnnee = dateFin.day, dateFin.month, dateFin.year
##
##            # Calcul des années
##            if annees != 0:
##                dateAnnee = dateAnnee + annees
##                dateFin = datetime.date(dateAnnee, dateMois, dateJour)
        
        # Calcule le nbre de jours restants
        nbreJours = (dateFin - date_jour).days
        
        return str(dateFin), nbreJours
    
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def OnItemActivated(self,event):
        self.Modifier(None)
                
    def InitModel(self):
        self.SetDictMaladies() 
        self.SetDictLiens() 
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        req = """
        SELECT vaccins.IDvaccin, vaccins.IDindividu, vaccins.IDtype_vaccin, vaccins.date, types_vaccins.nom, types_vaccins.duree_validite
        FROM vaccins LEFT JOIN types_vaccins ON vaccins.IDtype_vaccin = types_vaccins.IDtype_vaccin
        WHERE vaccins.IDindividu=%d;
        """ % self.IDindividu
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
    
    def SetDictMaladies(self):
        global DICT_MALADIES
        db = GestionDB.DB()
        req = """SELECT IDtype_maladie, nom, vaccin_obligatoire
        FROM types_maladies ORDER BY nom; """ 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictMaladies = {}
        for IDtype_maladie, nom, vaccin_obligatoire in listeDonnees :
            dictMaladies[IDtype_maladie] = { "nom" : nom, "vaccin_obligatoire" : vaccin_obligatoire }
        DICT_MALADIES = dictMaladies

    def SetDictLiens(self):
        global DICT_LIENS_MALADIES
        db = GestionDB.DB()
        req = """SELECT IDvaccins_maladies, IDtype_vaccin, IDtype_maladie
        FROM vaccins_maladies; """ 
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictLiensMaladies = {}
        for IDvaccins_maladies, IDtype_vaccin, IDtype_maladie in listeDonnees :
            if dictLiensMaladies.has_key(IDtype_vaccin) == False :
                dictLiensMaladies[IDtype_vaccin] = [IDtype_maladie,]
            else:
                dictLiensMaladies[IDtype_vaccin].append(IDtype_maladie)
        DICT_LIENS_MALADIES = dictLiensMaladies        
        
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        def FormateValidite(nbreJoursRestants):
            if nbreJoursRestants == None :
                return _(u"Validité illimitée")
            elif nbreJoursRestants == 0 :
                return _(u"Expire aujourd'hui")
            elif nbreJoursRestants < 0 :
                return _(u"Vaccin périmé")
            else:
                return _(u"Expire dans %d jours") % nbreJoursRestants
        
        def rowFormatter(listItem, track):
            if track.nbreJoursRestants < 0 :
                listItem.SetTextColour((180, 180, 180))

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDvaccin", typeDonnee="entier"),
            ColumnDefn(_(u"Nom du vaccin"), 'left', 140, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Validité"), "left", 120, "nbreJoursRestants", typeDonnee="texte", stringConverter=FormateValidite), 
            ColumnDefn(_(u"Maladies associées"), "left", 110, "txt_maladies_associees", typeDonnee="texte", isSpaceFilling=True), 
            ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun vaccin"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
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
        self._ResizeSpaceFillingColumns() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDvaccin
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des vaccins"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des vaccins"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_vaccins", "creer") == False : return
        dlg = Saisie(self)
        if dlg.ShowModal() == wx.ID_OK:
            IDtype_vaccin = dlg.GetIDtype_vaccin()
            date = str(dlg.GetDate())
            DB = GestionDB.DB()
            listeDonnees = [
                ("IDindividu", self.IDindividu ),
                ("IDtype_vaccin", IDtype_vaccin ),
                ("date", date),
                ]
            IDvaccin = DB.ReqInsert("vaccins", listeDonnees)
            DB.Close()
            self.MAJ(IDvaccin)
            self.MAJctrlMaladies()
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_vaccins", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun vaccin à modifier dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDvaccin = self.Selection()[0].IDvaccin
        IDtype_vaccin = self.Selection()[0].IDtype_vaccin
        date = self.Selection()[0].date
        dlg = Saisie(self, IDtype_vaccin, date)
        if dlg.ShowModal() == wx.ID_OK:
            IDtype_vaccin = dlg.GetIDtype_vaccin()
            date = str(dlg.GetDate())
            DB = GestionDB.DB()
            listeDonnees = [
                ("IDindividu", self.IDindividu ),
                ("IDtype_vaccin", IDtype_vaccin ),
                ("date", date),
                ]
            DB.ReqMAJ("vaccins", listeDonnees, "IDvaccin", IDvaccin)
            DB.Close()
            self.MAJ(IDvaccin)
            self.MAJctrlMaladies()
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_vaccins", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun vaccin à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce vaccin ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            IDvaccin = self.Selection()[0].IDvaccin
            DB = GestionDB.DB()
            DB.ReqDEL("vaccins", "IDvaccin", IDvaccin)
            DB.Close() 
            self.MAJ()
            self.MAJctrlMaladies()
        dlg.Destroy()
    
    def MAJctrlMaladies(self):
        """ MAJ le ctrl Maladies dt le vaccin est obligatoire dans la fiche individu """
        if self.GetParent().GetName() == "panel_medical" :
            self.GetParent().ctrl_maladies.MAJ()

# -------------------------------------------------------------------------------------------------------------------------------------------

class Choice(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.listeData = []
        self.SetToolTipString(_(u"Sélectionnez le vaccin"))
    
    def SetListe(self, listeData=[]):
        self.Clear()
        self.listeData = listeData
        for nom, ID in listeData :
            self.Append(nom)

    def SetID(self, ID=0):
        index = 0
        for nom, IDtmp in self.listeData:
            if IDtmp == ID :
                 self.SetSelection(index)
            index += 1

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.listeData[index][1]
    

    
    
class Saisie(wx.Dialog):
    def __init__(self, parent, IDtype_vaccin=None, date=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent

        listeVaccins = self.GetListeVaccins()
        
        self.label_vaccin = wx.StaticText(self, -1, _(u"Vaccin :"))
        self.ctrl_vaccin = Choice(self)
        self.ctrl_vaccin.SetListe(listeVaccins)
        if IDtype_vaccin != None :
            self.ctrl_vaccin.SetID(IDtype_vaccin)
        self.label_date = wx.StaticText(self, -1, _(u"Date :"))
        self.ctrl_date = CTRL_Saisie_date.Date(self, date_max=DateEngFr(str(datetime.date.today())))
        if date !=None :
            self.ctrl_date.SetDate(date)
            
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        if IDtype_vaccin == None :
            self.SetTitle(_(u"Saisie d'un vaccin"))
        else:
            self.SetTitle(_(u"Modification d'un vaccin"))
        self.SetMinSize((350, -1))

        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_vaccin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_vaccin, 0, wx.EXPAND, 0)
        grid_sizer_contenu.Add(self.label_date, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_contenu.Add(self.ctrl_date, 0, 0, 0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
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
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixVaccin, self.ctrl_vaccin)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
    
    def GetListeVaccins(self):
        db = GestionDB.DB()
        req = """SELECT nom, IDtype_vaccin
        FROM types_vaccins ORDER BY nom; """ 
        db.ExecuterReq(req)
        listeVaccins = db.ResultatReq()
        db.Close()
        return listeVaccins
    
    def GetIDtype_vaccin(self):
        return self.ctrl_vaccin.GetID()
    
    def GetDate(self):
        return self.ctrl_date.GetDate()
    
    def OnChoixVaccin(self, event):
        self.ctrl_date.SetFocus()
        
    def OnBoutonOk(self, event):
        if self.ctrl_vaccin.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un vaccin dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_vaccin.SetFocus()
            return
        
        if self.ctrl_date.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date pour ce vaccin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return
                
        self.EndModal(wx.ID_OK)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Mdical")










# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un vaccin..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_listview
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, IDindividu=27, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
