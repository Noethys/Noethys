#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from CTRL_Questionnaire import LISTE_CONTROLES

DICT_QUESTIONS = {}
DICT_CHOIX = {}
DICT_CONTROLES = {}

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


def GetCondition(filtre="", choix="", criteres=""):
    description = u""
    
    # TEXTE
    if filtre == "texte" :
        if choix == "EGAL" : description = _(u"Est �gal � '%s'") % criteres
        if choix == "DIFFERENT" : description = _(u"Est diff�rent de '%s'") % criteres
        if choix == "CONTIENT" : description = _(u"Contient '%s'") % criteres
        if choix == "CONTIENTPAS" : description = _(u"Ne contient pas '%s'") % criteres
        if choix == "VIDE" : description = _(u"Est vide")
        if choix == "PASVIDE" : description = _(u"N'est pas vide")
    
    # ENTIER
    if filtre == "entier" :
        if choix == "EGAL" : description = _(u"Est �gal � '%s'") % criteres
        if choix == "DIFFERENT" : description = _(u"Est diff�rent de '%s'") % criteres
        if choix == "SUP" : description = _(u"Est sup�rieur � '%s'") % criteres
        if choix == "SUPEGAL" : description = _(u"Est sup�rieur ou �gal � '%s'") % criteres
        if choix == "INF" : description = _(u"Est inf�rieur � '%s'") % criteres
        if choix == "INFEGAL" : description = _(u"Est inf�rieur ou �gal � '%s'") % criteres
        if choix == "COMPRIS" : description = _(u"Est compris entre '%s' et '%s'") % (criteres.split(";")[0], criteres.split(";")[1])

    # DATE
    if filtre == "date" :
        if choix == "EGAL" : description = _(u"Est �gal au '%s'") % DateEngFr(criteres)
        if choix == "DIFFERENT" : description = _(u"Est diff�rent du '%s'") % DateEngFr(criteres)
        if choix == "SUP" : description = _(u"Est sup�rieur au '%s'") % DateEngFr(criteres)
        if choix == "SUPEGAL" : description = _(u"Est sup�rieur ou �gal au '%s'") % DateEngFr(criteres)
        if choix == "INF" : description = _(u"Est inf�rieur au '%s'") % DateEngFr(criteres)
        if choix == "INFEGAL" : description = _(u"Est inf�rieur ou �gal au '%s'") % DateEngFr(criteres)
        if choix == "COMPRIS" : description = _(u"Est compris entre le '%s' et le '%s'") % (DateEngFr(criteres.split(";")[0]), DateEngFr(criteres.split(";")[1]))

    # COCHE
    if filtre == "coche" :
        if choix == "COCHE" : description = _(u"Est 'oui'")
        if choix == "DECOCHE" : description = _(u"Est 'non'")

    # CHOIX
    if filtre == "choix" :
        listeLabelsChoix = []
        listeIDchoix = criteres.split(";")
        for IDchoix in listeIDchoix :
            IDchoix = int(IDchoix)
            if DICT_CHOIX.has_key(IDchoix) :
                listeLabelsChoix.append("'%s'" % DICT_CHOIX[IDchoix]["label"])
        description = _(u"Doit �tre %s") % _(u" ou ").join(listeLabelsChoix)

    return description




class Track(object):
    def __init__(self, parent, donnees):
        self.IDfiltre = donnees["IDfiltre"]
        self.IDquestion = donnees["IDquestion"]
        self.choix = donnees["choix"]
        self.criteres = donnees["criteres"]
        
        self.controle = DICT_QUESTIONS[self.IDquestion]["controle"]
        self.filtre = DICT_CONTROLES[self.controle]["filtre"]
        
        # Cr�ation du label de la question
        self.label = DICT_QUESTIONS[self.IDquestion]["label"]
        
        # Cr�ation de la description
        self.condition = GetCondition(self.filtre, self.choix, self.criteres)


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.listeDonnees = kwds.pop("listeDonnees", [])
        self.listeTypes = kwds.pop("listeTypes", ("famille", "individu"))
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.dictTracks = {}
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
    
    def SetDonnees(self, listeDonnees=[]):
        self.listeDonnees = listeDonnees
        self.MAJ() 
    
    def GetDonnees(self):
        return self.listeDonnees 
    
    def OnItemActivated(self,event):
        self.Modifier(None)
    
    def GetAutresDonnees(self):
        global DICT_QUESTIONS, DICT_CHOIX, DICT_CONTROLES
        
        # Importation des questions
        DB = GestionDB.DB()
        req = """SELECT IDquestion, label, controle
        FROM questionnaire_questions;"""
        DB.ExecuterReq(req)
        listeQuestions = DB.ResultatReq()
        DICT_QUESTIONS = {}
        for IDquestion, label, controle in listeQuestions :
            DICT_QUESTIONS[IDquestion] = {"label":label, "controle":controle}
        
        # Importation des choix
        DB = GestionDB.DB()
        req = """SELECT IDchoix, IDquestion, label
        FROM questionnaire_choix
        ORDER BY ordre;"""
        DB.ExecuterReq(req)
        listeChoix = DB.ResultatReq()
        DICT_CHOIX = {}
        for IDchoix, IDquestion, label in listeChoix :
            DICT_CHOIX[IDchoix] = {"label":label, "IDquestion":IDquestion, }
        
        # Importation des contr�les
        DICT_CONTROLES = {}
        for controle in LISTE_CONTROLES :
            DICT_CONTROLES[controle["code"]] = controle

        DB.Close()

    def InitModel(self):
        self.GetAutresDonnees() 
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        listeID = None
        listeListeView = []
        
        self.dictTracks = {}
        index = 0
        for dictTemp in self.listeDonnees :
            track = Track(self, dictTemp)
            listeListeView.append(track)
            self.dictTracks[track] = index
            if self.selectionID == dictTemp["IDfiltre"] :
                self.selectionTrack = track
            index += 1
        return listeListeView
    
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDfiltre"),
            ColumnDefn(_(u"Question"), "left", 120, "label"), 
            ColumnDefn(_(u"Condition"), 'left', 165, "condition", isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun filtre"))
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
        # S�lection d'un item
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
                
        # Cr�ation du menu contextuel
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des filtres"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des filtres"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des filtres"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des filtres"))

    def Ajouter(self, event):
        # Ouverture de la fen�tre de saisie
        import DLG_Saisie_filtre_questionnaire
        dlg = DLG_Saisie_filtre_questionnaire.Dialog(self, listeTypes=self.listeTypes)
        if dlg.ShowModal() == wx.ID_OK:
            IDquestion = dlg.GetQuestion() 
            choix, criteres = dlg.GetValeur() 
            dictTemp = {"IDfiltre":None, "IDquestion":IDquestion, "choix":choix, "criteres":criteres}
            self.listeDonnees.append(dictTemp)
            self.MAJ()
        dlg.Destroy()

    def Modifier(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun filtre � modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        import DLG_Saisie_filtre_questionnaire
        dlg = DLG_Saisie_filtre_questionnaire.Dialog(self, listeTypes=self.listeTypes)
        dlg.SetQuestion(track.IDquestion)
        dlg.SetValeur(track.choix, track.criteres)
        if dlg.ShowModal() == wx.ID_OK:
            IDquestion = dlg.GetQuestion() 
            choix, criteres = dlg.GetValeur() 
            dictTemp = {"IDfiltre":track.IDfiltre, "IDquestion":IDquestion, "choix":choix, "criteres":criteres}
            self.listeDonnees[self.dictTracks[track]] = dictTemp
            self.MAJ()
        dlg.Destroy()

    def Supprimer(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez s�lectionn� aucun filtre � supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce filtre ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            self.listeDonnees.pop(self.dictTracks[track])
            self.MAJ()
        dlg.Destroy()
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un filtre..."))
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
        
        listeDonnees = [
            {"IDfiltre":222, "IDquestion":5, "choix":"", "criteres":u"4;5"},
            ]
        
        self.myOlv = ListView(panel, listeDonnees=listeDonnees, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
