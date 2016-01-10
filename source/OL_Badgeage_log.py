#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import time
import GestionDB


import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils


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

def Purger():
    """ Purge de l'historique """
    texte = _(u"La purge du journal de badgeage vous permet de réduire la taille de la base de données. Il est conseillé d'y procéder une fois que vous n'avez plus besoin de l'historique de badgeage (soit quelques mois après).\n\nCommencez par sélectionner une date maximale.")
    dlg = wx.MessageDialog(None, texte, _(u"Purge du journal de badgeage"), wx.OK|wx.CANCEL|wx.ICON_INFORMATION)
    reponse = dlg.ShowModal()
    dlg.Destroy()
    if reponse != wx.ID_OK:
        return False

    # Sélection d'une date
    import DLG_calendrier_simple
    dlg = DLG_calendrier_simple.Dialog(None)
    if dlg.ShowModal() == wx.ID_OK :
        date = dlg.GetDate()
        dlg.Destroy()
    else :
        dlg.Destroy()
        return False
    
    # Demande de confirmation
    dlg = wx.MessageDialog(None, _(u"Confirmez-vous la purge de l'historique de badgeage jusqu'au %s inclus ?") % DateEngFr(str(date)), _(u"Purge du journal de badgeage"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
    reponse = dlg.ShowModal()
    dlg.Destroy()
    if reponse != wx.ID_YES:
        return False
    
    # Suppression
    DB = GestionDB.DB()
    req = """DELETE FROM badgeage_journal WHERE date<='%s';""" % str(date)
    DB.ExecuterReq(req)
    DB.Commit()
    DB.Close() 
    # Fin
    dlg = wx.MessageDialog(None, _(u"Purge du journal de badgeage terminée."), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


class Track(object):
    def __init__(self, parent, date=None, heure=None, action="", individu="", IDindividu=None, resultat=None):
        # Date
        if date == None :
            self.date = datetime.date.today()
        else :
            self.date = date
        # Heure
        if heure == None :
            heure = time.strftime('%H:%M', time.localtime()) 
        self.heure = heure
        # Action
        self.action = action
        # Individu
        self.individu = individu
        self.IDindividu = IDindividu
        # Résultat
        self.resultat = resultat
        if self.resultat == True :
            self.texteResultat = "Ok"
        elif self.resultat == None :
            self.texteResultat = u""
        else :
            self.texteResultat = self.resultat
        # Statut
        if self.resultat == True :
            self.statut = "ok"
        elif self.resultat == None :
            self.statut = None
        else :
            self.statut = "pasok"

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.modeHistorique = kwds.pop("modeHistorique", False)
        self.donnees = []
        # Initialisation du listCtrl
        kwds["sortable"] = False
        self.nbreActions = 0
        FastObjectListView.__init__(self, *args, **kwds)
        self.InitObjectListView() 

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        imgOk = self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        imgPasOk = self.AddNamedImages("pasok", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.imgVert = self.AddNamedImages("vert", wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("rouge", wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("orange", wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG))

        def GetImageStatut(track):
            return track.statut
        
        def FormateHeure(heure):
            heure = heure.replace(":", "h")
            return heure

        def FormateDate(dateDD):
            if dateDD == None : return u""
            return DateEngFr(str(dateDD))
        
        if self.modeHistorique == True :
            liste_Colonnes = [
                ColumnDefn(u"", "left", 0, ""),
                ColumnDefn(_(u"Date"), 'center', 88, "date", typeDonnee="date", stringConverter=FormateDate), 
                ColumnDefn(_(u"Heure"), 'center', 60, "heure", typeDonnee="texte", stringConverter=FormateHeure), 
                ColumnDefn(_(u"Action"), 'left', 270, "action", typeDonnee="texte"), 
                ColumnDefn(_(u"Individu"), 'left', 150, "individu", typeDonnee="texte"), 
                ColumnDefn(_(u"Résultat"), 'left', 150, "texteResultat", typeDonnee="texte", imageGetter=GetImageStatut, isSpaceFilling=True), 
                ]
        else :
            liste_Colonnes = [
                ColumnDefn(u"", "left", 0, ""),
                ColumnDefn(_(u"Date"), 'center', 88, "date", typeDonnee="date", stringConverter=FormateDate), 
                ColumnDefn(_(u"Heure"), 'center', 60, "heure", typeDonnee="texte", stringConverter=FormateHeure), 
                ColumnDefn(_(u"Action"), 'left', 270, "action", typeDonnee="texte"), 
                ColumnDefn(_(u"Individu"), 'left', 130, "individu", typeDonnee="texte"), 
                ColumnDefn(_(u"Résultat"), 'left', 150, "texteResultat", typeDonnee="texte", imageGetter=GetImageStatut, isSpaceFilling=True), 
                ]

        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune action"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetObjects(self.donnees)


    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """                
        # Création du menu contextuel
        menuPop = wx.Menu()

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Journal des actions"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Journal des actions"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Journal des actions"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Journal des actions"))

    def AjouterAction(self, individu=u"", IDindividu=None, heure=None, action="", resultat=None):
        """ Ajouter une action """
        """ heure="14:45" (Si heure=None : heure actuelle automatique), individu=_(u"DUPOND Kévin"), action="enregistrer", resultat=True """
        track = Track(self, date=None, heure=heure, action=action, individu=individu, IDindividu=IDindividu, resultat=resultat)
        self.AddObject(track)
        self.EnsureCellVisible(self.nbreActions, 0)
        self.nbreActions += 1
        self.MemoriserAction(track) 
    
    def MemoriserAction(self, track):
        """ Sauvegarde un track dans la base de données """
        DB = GestionDB.DB()
        listeDonnees = [    
                ("date", str(track.date)),
                ("heure", track.heure),
                ("IDindividu", track.IDindividu),
                ("individu", track.individu),
                ("action", track.action),
                ("resultat", track.resultat),
            ]
        IDaction = DB.ReqInsert("badgeage_journal", listeDonnees)
        DB.Close()
    
    def Importer(self, date=None):
        self.DeleteAllItems() 
        DB = GestionDB.DB()
        req = """SELECT IDaction, date, heure, IDindividu, individu, action, resultat
        FROM badgeage_journal
        WHERE date='%s'
        ORDER BY IDaction;""" % str(date)
        DB.ExecuterReq(req)
        listeActions = DB.ResultatReq()
        DB.Close() 
        listeTracks = []
        for IDaction, date, heure, IDindividu, individu, action, resultat in listeActions :
            if resultat == "1" : resultat = True
            listeTracks.append(Track(self, date=date, heure=heure, action=action, individu=individu, IDindividu=IDindividu, resultat=resultat))
        self.SetObjects(listeTracks)
    
    def Purger(self, date=None):
        Purger(date)

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une action..."))
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
        self.Refresh() 


# -------------------------------------------------------------------------------------------------------------------------------------------



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        # TEST
        self.myOlv.Importer() 
        
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
