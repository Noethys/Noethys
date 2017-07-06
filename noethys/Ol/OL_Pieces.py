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

DICT_DOCUMENTS = {}


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
    def __init__(self, parent, donnees):
        self.IDpiece = donnees[0]
        self.IDtype_piece = donnees[1]
        self.IDindividu = donnees[2]
        self.IDfamille = donnees[3]
        self.date_debut = donnees[4]
        self.date_fin = donnees[5]
        self.nom = donnees[6]
        self.public = donnees[7]
        self.duree_validite = donnees[8]
        self.valide_rattachement = donnees[9]
        self.individu_nom = donnees[10]
        self.individu_prenom = donnees[11]
        
        # Nbre documents scannés
        if DICT_DOCUMENTS.has_key(self.IDpiece) :
            self.nbre_documents = DICT_DOCUMENTS[self.IDpiece]
        else:
            self.nbre_documents = 0
        
        # Validité de la pièce
        if str(datetime.date.today()) <= self.date_fin :
            self.valide = True
        else:
            self.valide = False
            
        # Nom complet de l'individu
        self.individu_nomComplet = ""
        if parent.IDfamille != None and self.public != "famille" :
            self.individu_nomComplet = u"%s %s" % (self.individu_prenom, self.individu_nom)
            self.nom += _(u" de ") + self.individu_nomComplet
        
        # Nom des titulaires de famille
        if self.IDfamille != None :
            self.nomTitulaires = _(u"IDfamille n°%d") % self.IDfamille
            if parent.dictFamillesRattachees != None :
                if parent.dictFamillesRattachees.has_key(self.IDfamille) :
                    self.nomTitulaires = parent.dictFamillesRattachees[self.IDfamille]["nomsTitulaires"]
        else:
            self.nomTitulaires = None
                


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", None)
        self.IDfamille = kwds.pop("IDfamille", None)
        self.dictFamillesRattachees = kwds.pop("dictFamillesRattachees", None)
        self.nbreFamilles = 0
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
        self.Modifier(None)
                
    def InitModel(self):
        global DICT_DOCUMENTS
        DICT_DOCUMENTS = self.GetDocumentsScan() 
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        
        if self.IDindividu != None :
            # Pour un individu
            if self.dictFamillesRattachees != None :
                listeIDfamille = []
                for IDfamille, dictFamille in self.dictFamillesRattachees.iteritems() :
                    if dictFamille["IDcategorie"] in (1, 2) :
                        listeIDfamille.append(IDfamille)
                if len(listeIDfamille) == 0 : conditionIDfamille = "()"
                if len(listeIDfamille) == 1 : conditionIDfamille = "(%d)" % listeIDfamille[0]
                else : conditionIDfamille = str(tuple(listeIDfamille))
            else:
                conditionIDfamille = "()"
            req = """
            SELECT 
            IDpiece, pieces.IDtype_piece, pieces.IDindividu, pieces.IDfamille, date_debut, date_fin, 
            types_pieces.nom, public, duree_validite, valide_rattachement, 
            individus.nom, individus.prenom
            FROM pieces 
            LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
            LEFT JOIN individus ON pieces.IDindividu = individus.IDindividu
            WHERE pieces.IDindividu=%d OR (pieces.IDfamille IN %s AND pieces.IDindividu IS NULL);
            """ % (self.IDindividu, conditionIDfamille)
        else:
            # Pour une famille
            req = """
            SELECT IDindividu, IDcategorie
            FROM rattachements 
            WHERE IDfamille=%d AND IDcategorie IN (1, 2);
            """ % self.IDfamille
            db.ExecuterReq(req)
            listeDonnees = db.ResultatReq()
            listeIDindividus = []
            for IDindividu, IDcategorie in listeDonnees :
                if IDindividu not in listeIDindividus :
                    listeIDindividus.append(IDindividu) 
            if len(listeIDindividus) == 0 : conditionIndividus = "()"
            if len(listeIDindividus) == 1 : conditionIndividus = "(%d)" % listeIDindividus[0]
            else : conditionIndividus = str(tuple(listeIDindividus))
            req = """
            SELECT 
            IDpiece, pieces.IDtype_piece, pieces.IDindividu, pieces.IDfamille, date_debut, date_fin, 
            types_pieces.nom, public, duree_validite, valide_rattachement, 
            individus.nom, individus.prenom
            FROM pieces 
            LEFT JOIN types_pieces ON types_pieces.IDtype_piece = pieces.IDtype_piece
            LEFT JOIN individus ON pieces.IDindividu = individus.IDindividu
            WHERE pieces.IDfamille=%d OR (pieces.IDindividu IN %s AND pieces.IDfamille IS NULL);
            """ % (self.IDfamille, conditionIndividus)

        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()

        listeListeView = []
        
        listeIDfamilles = []
        for item in listeDonnees :
            
            # Pour compter le nbre de familles
            IDfamille = item[3]
            if IDfamille not in listeIDfamilles and IDfamille != None :
                listeIDfamilles.append(IDfamille) 
                
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(self, item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        
        self.nbreFamilles = len(listeIDfamilles)
        
        return listeListeView
    
    def GetDocumentsScan(self):
        """ Retourne le nbre de documents scannés pour chaque pièce """
        DB = GestionDB.DB(suffixe="DOCUMENTS")
        req = "SELECT IDdocument, IDpiece FROM documents;"
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictDocuments = {}
        for IDdocument, IDpiece in listeDonnees :
            if dictDocuments.has_key(IDpiece) == False :
                dictDocuments[IDpiece] = 1
            else:
                dictDocuments[IDpiece] += 1
        return dictDocuments
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Image list
        self.imgDocument = self.AddNamedImages("document", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Document.png"), wx.BITMAP_TYPE_PNG))
        
        def FormateDate(dateStr):
            if dateStr == "" : return ""
            if dateStr == "2999-01-01" : return _(u"Illimitée")
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text
        
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour((180, 180, 180))
        
        def GetImageDocument(track):
            if track.nbre_documents > 0 :
                return self.imgDocument
            else:
                return None

        if self.IDindividu != None :
            # Si On est dans une fiche INDIVIDU
            if self.nbreFamilles < 2 :
                liste_Colonnes = [
                    ColumnDefn(_(u"ID"), "left", 0, "IDpiece", typeDonnee="entier"),
                    ColumnDefn(u"Du", "left", 85, "date_debut", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"au"), "left", 85, "date_fin", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"Nom de la pièce"), 'left', 190, "nom", typeDonnee="texte", imageGetter=GetImageDocument, isSpaceFilling=True),
                    ]
            else:
                liste_Colonnes = [
                    ColumnDefn(_(u"ID"), "left", 0, "IDpiece", typeDonnee="entier"),
                    ColumnDefn(u"Du", "left", 85, "date_debut", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"au"), "left", 85, "date_fin", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"Nom de la pièce"), 'left', 165, "nom", typeDonnee="texte", imageGetter=GetImageDocument, isSpaceFilling=True),
                    ColumnDefn(_(u"Famille"), 'left', 150, "nomTitulaires", typeDonnee="texte"),
                    ]
        else :
            # Si On est dans une fiche FAMILLE
            if self.nbreFamilles < 2 :
                liste_Colonnes = [
                    ColumnDefn(_(u"ID"), "left", 0, "IDpiece", typeDonnee="entier"),
                    ColumnDefn(u"Du", "left", 85, "date_debut", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"au"), "left", 85, "date_fin", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"Nom de la pièce"), 'left', 340, "nom", typeDonnee="texte", imageGetter=GetImageDocument, isSpaceFilling=True),
                    ]
            else:
                liste_Colonnes = [
                    ColumnDefn(_(u"ID"), "left", 0, "IDpiece", typeDonnee="entier"),
                    ColumnDefn(u"Du", "left", 85, "date_debut", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"au"), "left", 85, "date_fin", typeDonnee="date", stringConverter=FormateDate), 
                    ColumnDefn(_(u"Nom de la pièce"), 'left', 165, "nom", typeDonnee="texte", imageGetter=GetImageDocument, isSpaceFilling=True),
                    ColumnDefn(_(u"Famille"), 'left', 150, "nomTitulaires", typeDonnee="texte"),
                    ]
        
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune pièce"))
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

    def MAJctrlPiecesObligatoires(self):
        if self.GetParent().GetName() == "DLG_Individu_pieces" or self.GetParent().GetName() == "DLG_Famille_pieces" :
            self.GetParent().ctrl_pieces_obligatoires.MAJ() 

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDpiece
                
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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pièces"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pièces"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des pièces"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des pièces"))

    def AjoutExpress(self, IDfamille=None, IDtype_piece=None, IDindividu=None):
        if IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_pieces", "creer") == False : return
        if IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_pieces", "creer") == False : return
        
        # Vérifie que l'individu est rattaché comme REPRESENTANT ou ENFANT à une famille
        if self.dictFamillesRattachees != None :
            valide = False
            for IDfamilleTmp, dictFamille in self.dictFamillesRattachees.iteritems() :
                if dictFamille["IDcategorie"] in (1, 2) :
                    valide = True
            if valide == False :
                dlg = wx.MessageDialog(self, _(u"Pour saisir une pièce, un individu doit obligatoirement être\nrattaché comme représentant ou enfant à une fiche famille !"), _(u"Saisie de pièce impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Ouverture de la fenêtre de saisie
        from Dlg import DLG_Saisie_piece
        dlg = DLG_Saisie_piece.Dialog(self, IDpiece=None, IDfamille=self.IDfamille, IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)
        dlg.SelectPiece(IDfamille, IDtype_piece, IDindividu)
        if dlg.Sauvegarde() == True :
            IDpiece = dlg.GetIDpiece() 
            self.MAJ(IDpiece)
            self.MAJctrlPiecesObligatoires() 
        else :
            if dlg.ShowModal() == wx.ID_OK:
                IDpiece = dlg.GetIDpiece()
                self.MAJ(IDpiece)
                self.MAJctrlPiecesObligatoires()
        dlg.Destroy()


    def Ajouter(self, event):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_pieces", "creer") == False : return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_pieces", "creer") == False : return

        # Vérifie que l'individu est rattaché comme REPRESENTANT ou ENFANT à une famille
        if self.dictFamillesRattachees != None :
            valide = False
            for IDfamilleTmp, dictFamille in self.dictFamillesRattachees.iteritems() :
                if dictFamille["IDcategorie"] in (1, 2) :
                    valide = True
            if valide == False :
                dlg = wx.MessageDialog(self, _(u"Pour saisir une pièce, un individu doit obligatoirement être\nrattaché comme représentant ou enfant à une fiche famille !"), _(u"Saisie de pièce impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return

        # Ouverture de la fenêtre de saisie
        from Dlg import DLG_Saisie_piece
        dlg = DLG_Saisie_piece.Dialog(self, IDpiece=None, IDfamille=self.IDfamille, IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)
        if dlg.ShowModal() == wx.ID_OK:
            IDpiece = dlg.GetIDpiece() 
            self.MAJ(IDpiece)
            self.MAJctrlPiecesObligatoires() 
        dlg.Destroy()

    def Modifier(self, event):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_pieces", "modifier") == False : return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_pieces", "modifier") == False : return
        
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune pièce à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDpiece = self.Selection()[0].IDpiece
        from Dlg import DLG_Saisie_piece
        dlg = DLG_Saisie_piece.Dialog(self, IDpiece=IDpiece, IDfamille=self.IDfamille, IDindividu=self.IDindividu, dictFamillesRattachees=self.dictFamillesRattachees)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDpiece)
            self.MAJctrlPiecesObligatoires() 
        dlg.Destroy()

    def Supprimer(self, event):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_pieces", "supprimer") == False : return
        if self.IDindividu != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_pieces", "supprimer") == False : return

        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune pièce à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDpiece = self.Selection()[0].IDpiece
        nomPiece = self.Selection()[0].nom
        IDindividu = self.Selection()[0].IDindividu
        IDfamille = self.Selection()[0].IDfamille
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette pièce ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            # Suppression de la pièce
            DB = GestionDB.DB()
            DB.ReqDEL("pieces", "IDpiece", IDpiece)
            DB.Close() 
            # Suppression des documents scannés rattachés
            DB = GestionDB.DB(suffixe="DOCUMENTS")
            DB.ReqDEL("documents", "IDpiece", IDpiece)
            DB.Close()
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                "IDindividu" : IDindividu,
                "IDfamille" : IDfamille,
                "IDcategorie" : 17, 
                "action" : _(u"Suppression de la pièce ID%d '%s'") % (IDpiece, nomPiece),
                },])
                
            # Actualisation de l'affichage
            self.MAJ()
            self.MAJctrlPiecesObligatoires() 
        dlg.Destroy()
    

# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher une pièce..."))
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


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, IDindividu=None, IDfamille=3, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
