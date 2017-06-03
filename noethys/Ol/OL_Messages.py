#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Utils import UTILS_Historique


from Utils import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs


MODE = ""


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
        self.IDmessage = donnees[0]
        self.type = donnees[1]
        self.IDcategorie = donnees[2]
        self.date_saisie = DateEngEnDateDD(donnees[3])
        self.IDutilisateur = donnees[4]
        self.date_parution = DateEngEnDateDD(donnees[5])
        self.priorite = donnees[6]
        self.afficher_accueil = donnees[7]
        self.afficher_liste = donnees[8]
        self.IDfamille = donnees[9]
        self.IDindividu = donnees[10]
        self.texte = donnees[11]
        self.nom = donnees[12]
        self.rappel_accueil = donnees[13]
        self.rappel_famille = donnees[14]

        if MODE == "accueil" and self.IDfamille != None and self.nom != None :
            self.texte = _(u"Famille de %s : %s") % (self.nom, self.texte)
        
        if MODE == "accueil" and self.IDindividu != None and self.nom != None :
            self.texte = u"%s : %s" % (self.nom, self.texte) 

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        mode = kwds.pop("mode", "accueil") # "accueil", "famille", "individu", "liste"
        self.IDfamille = kwds.pop("IDfamille", None)
        self.IDindividu = kwds.pop("IDindividu", None)
        global MODE
        MODE = mode
        
        self.donnees = []
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
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        
        condition = ""
        # Si on vient d'une fiche famille
        if MODE == "famille" : condition = "WHERE IDfamille=%d" % self.IDfamille
        # Si on vient d'une fiche individu
        if MODE == "individu" : condition = "WHERE IDindividu=%d" % self.IDindividu
        # Si on vient de l'accueil
        if MODE == "accueil" : condition = "WHERE afficher_accueil=1 AND date_parution<='%s'" % str(datetime.date.today())
        # Si on souhaite une liste complète des messages
        if MODE == "liste" : condition = ""

        DB = GestionDB.DB()
        req = """SELECT IDmessage, type, IDcategorie, date_saisie, IDutilisateur, date_parution, priorite,
        afficher_accueil, afficher_liste, IDfamille, IDindividu, texte, nom, rappel, rappel_famille
        FROM messages 
        %s;""" % condition
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()

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
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Préparation de la listeImages
        imgImportant = self.AddNamedImages("attention", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attention.png"), wx.BITMAP_TYPE_PNG))
        
        # Formatage des données
        def GetImagePriorite(track):
            if track.priorite == "HAUTE" : return imgImportant
            else: return None
            
        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDmessage", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'centre', 75, "date_parution", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Texte"), 'left', 420, "texte", typeDonnee="texte", imageGetter=GetImagePriorite, isSpaceFilling=True),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun message"))
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
        self._ResizeSpaceFillingColumns() 
        if ID == None :
            wx.CallAfter(self.DefileDernier)

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDmessage
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
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
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Apercu(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des messages"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des messages"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def Ajouter(self, event):
        if MODE in ("accueil", "liste") and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_messages", "creer") == False : return
        if MODE == "famille" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "creer") == False : return
        if MODE == "individu" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_messages", "creer") == False : return
        from Dlg import DLG_Saisie_message
        dlg = DLG_Saisie_message.Dialog(self, IDmessage=None, mode="accueil")
        if dlg.ShowModal() == wx.ID_OK:
            IDmessage = dlg.GetIDmessage()
            self.MAJ(IDmessage)
        dlg.Destroy()

    def Modifier(self, event):
        if MODE in ("accueil", "liste") and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_messages", "modifier") == False : return
        if MODE == "famille" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "modifier") == False : return
        if MODE == "individu" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_messages", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmessage = self.Selection()[0].IDmessage
        from Dlg import DLG_Saisie_message
        dlg = DLG_Saisie_message.Dialog(self, IDmessage=IDmessage, mode="accueil")
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDmessage)
        dlg.Destroy()

    def Supprimer(self, event):
        if MODE in ("accueil", "liste") and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("outils_messages", "supprimer") == False : return
        if MODE == "famille" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_messages", "supprimer") == False : return
        if MODE == "individu" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_messages", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun message à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDmessage = self.Selection()[0].IDmessage
        IDfamille = self.Selection()[0].IDfamille
        IDindividu = self.Selection()[0].IDindividu
        texte = self.Selection()[0].texte
        
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce message ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("messages", "IDmessage", IDmessage)
            DB.Close() 
            
            # Mémorise l'action dans l'historique
            if len(texte) > 450 : texte = texte[450:] + u"..."
            UTILS_Historique.InsertActions([{
                "IDindividu" : IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : 26, 
                "action" : _(u"Suppression du message ID%d : '%s'") % (IDmessage, texte)
            },])
            
            # Actualisation de l'affichage
            self.MAJ()
        dlg.Destroy()



# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher un message..."))
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
        self.myOlv = ListView(panel, id=-1, mode="accueil", name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
