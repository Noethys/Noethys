#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
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
        if self.feries == True : listeTemp.append(_(u"F�ri�s inclus"))
        self.criteres_txt = ", ".join(listeTemp)
        
        # Texte unit�s
        listeTemp = []
        for dictUnite in self.unites :
            if self.parent.dictUnites.has_key(dictUnite["IDunite"]) :
                listeTemp.append(self.parent.dictUnites[dictUnite["IDunite"]]["nom"])
        self.unites_txt = "+".join(listeTemp)
        
        
        

# ----------------------------------------------------------------------------------------------------------------------------------------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.IDactivite = kwds.pop("IDactivite", None)
        self.IDmodele = kwds.pop("IDmodele", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeDonnees = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.donnees = []
        self.InitObjectListView()
        
        self.Importation_unites() 
        
    def Importation_unites(self):
        # R�cup�ration des unit�s
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
        self.oddRowsBackColor = "#F0FBED" 
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
                return "n�%d"% numero
            
        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "", typeDonnee="entier"),
            ColumnDefn(_(u"Unit�s"), 'left', 200, "unites_txt", typeDonnee="texte"),
            ColumnDefn(_(u"Conditions"), 'left', 200, "criteres_txt", typeDonnee="texte", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun param�tre"))
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
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
                
        # Cr�ation du menu contextuel
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
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des p�riodes de contrats"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des p�riodes de contrats"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des p�riodes de contrats"), autoriseSelections=False)
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des p�riodes de contrats"), autoriseSelections=False)

    def Ajouter(self, event):  
        dlg = DLG_Saisie_contrat_conso_detail.Dialog(self, IDactivite=self.IDactivite)
        if dlg.ShowModal() == wx.ID_OK:
            dictDonnees = dlg.GetDonnees() 
            self.listeDonnees.append(dictDonnees)
            self.MAJ() 
        dlg.Destroy()
        
    def Modifier(self, event):  
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun �l�ment de planning � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = DLG_Saisie_contrat_conso_detail.Dialog(self, IDactivite=self.IDactivite)
        dlg.SetDonnees(track.dictValeurs)
        if dlg.ShowModal() == wx.ID_OK:
            self.listeDonnees[track.index] = dlg.GetDonnees() 
            self.MAJ() 
        dlg.Destroy()

    def Supprimer(self, event):  
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun �l�ment de planning � supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        track = self.Selection()[0]     
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer l'�l�ment de planning s�lectionn� ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        
        self.listeDonnees.pop(track.index)
        self.MAJ() 

##    def Importation(self):
##        """ Importation des donn�es """
##        DB = GestionDB.DB()
##        req = """SELECT IDmodele, nom, donnees 
##        FROM modeles_plannings
##        WHERE IDmodele=%d;""" % self.IDmodele
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        if len(listeDonnees) > 0 :
##            donnees = listeDonnees[0][2]
##            self.listeDonnees = cPickle.loads(str(donnees))
    
    def GetElementsStr(self):
        return cPickle.dumps(self.listeDonnees)
    
    def SetElementsStr(self, donnees=""):
        self.listeDonnees = cPickle.loads(str(donnees))
        self.MAJ() 
        
##    def Sauvegarde(self):
##        """ Sauvegarde des �l�ments de planning """
##        donneesStr = self.GetElementsStr() 
##        DB = GestionDB.DB() 
##        listeDonnees = [("donnees", donneesStr),]
##        DB.ReqMAJ("modeles_plannings", listeDonnees, "IDmodele", self.IDmodele)
##        DB.Close() 


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
