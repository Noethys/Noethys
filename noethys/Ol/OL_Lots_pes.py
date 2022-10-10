#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Dates
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils
from Dlg import DLG_Saisie_lot_tresor_public
from Dlg import DLG_Saisie_lot_tresor_public_pes
from Dlg import DLG_Saisie_lot_tresor_public_magnus
from Dlg import DLG_Saisie_lot_tresor_public_jvs
from Dlg import DLG_Saisie_lot_tresor_public_corail


class Track(object):
    def __init__(self, donnees):
        self.IDlot = donnees[0]
        self.nom = donnees[1]
        self.verrouillage = donnees[2]
        self.observations = donnees[3]
        self.format = donnees[4]
        self.exercice = donnees[5]
        self.mois = donnees[6]
        self.nbrePieces = donnees[7]

        self.nom_format = DLG_Saisie_lot_tresor_public.GetFormatByCode(self.format)["label"]
        self.periode = "%d-%d" % (self.exercice, self.mois)
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
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
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        db = GestionDB.DB()
        req = """SELECT pes_lots.IDlot, pes_lots.nom, pes_lots.verrouillage, pes_lots.observations, pes_lots.format, exercice, mois, Count(pes_pieces.IDlot) AS nbrePieces
        FROM pes_lots
        LEFT JOIN pes_pieces ON pes_pieces.IDlot = pes_lots.IDlot
        GROUP BY pes_lots.IDlot;"""
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
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        # Image list
        self.imgVerrouillage = self.AddNamedImages("verrouillage", wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas_ferme.png"), wx.BITMAP_TYPE_PNG))

        def FormateDate(dateDD):
            if dateDD == None : return u""
            return UTILS_Dates.DateEngFr(str(dateDD))

        def GetImageVerrouillage(track):
            if track.verrouillage == 1 :
                return self.imgVerrouillage
            else:
                return None

        def FormatePeriode(periode):
            if periode == None or periode == "" : return u""
            annee, mois = periode.split("-")
            listeMois = [u"_", _(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre")]
            return u"%s %s" % (listeMois[int(mois)], annee)

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 42, "IDlot", typeDonnee="entier", imageGetter=GetImageVerrouillage),
            ColumnDefn(_(u"Période"), "left", 150, "periode", typeDonnee="texte", stringConverter=FormatePeriode), 
            ColumnDefn(_(u"Nom du lot"), "left", 190, "nom", typeDonnee="texte"),
            ColumnDefn(_(u"Format"), "left", 170, "nom_format", typeDonnee="texte"),
            ColumnDefn(_(u"Nbre pièces"), "center", 80, "nbrePieces", typeDonnee="entier"), 
            ColumnDefn(_(u"Observations"), "left", 200, "observations", typeDonnee="texte"), 
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun lot"))
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
    
    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        if len(self.Selection()) == 0:
            noSelection = True
        else:
            noSelection = False
            ID = self.Selection()[0].IDlot
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des bordereaux PES ORMC"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des bordereaux PES ORMC"), format="A", orientation=wx.PORTRAIT)
        prt.Print()


    def Ajouter(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "creer") == False : return
        reponse = self.Get_classe()
        if not reponse:
            return False
        format, classe = reponse
        dlg = classe(self, format=format)
        if dlg.ShowModal() == wx.ID_OK:
            IDlot = dlg.GetIDlot()
            self.MAJ(IDlot)
        dlg.Destroy()

    def Modifier(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "modifier") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun bordereau à modifier dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        format, classe = self.Get_classe(format=track.format)
        if not format:
            return False
        dlg = classe(self, IDlot=track.IDlot, format=track.format)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDlot)
        dlg.Destroy()

    def Supprimer(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("facturation_helios", "supprimer") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun bordereau à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        if track.verrouillage == 1 :
            dlg = wx.MessageDialog(self, _(u"Il est impossible de supprimer ce bordereau car il est verrouillé."), _(u"Suppression impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        nbrePieces = track.nbrePieces
        if nbrePieces > 0 :
            dlg = wx.MessageDialog(self, _(u"Il est impossible de supprimer ce bordereau puisqu'il est déjà constitué de %d pièce(s) !") % nbrePieces, _(u"Suppression impossible"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce bordereau ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("pes_lots", "IDlot", track.IDlot)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()

    def Assistant(self, filtres=[], nomLot=None):
        format, classe = self.Get_classe()
        if not format:
            return False
        dlg = classe(self, format=format)
        dlg.Assistant(filtres=filtres, nomLot=nomLot)
        if dlg.ShowModal() == wx.ID_OK:
            IDlot = dlg.GetIDlot()
            self.MAJ(IDlot)
        dlg.Destroy()

    def Get_classe(self, format=None):
        if not format:
            dlg = DLG_Saisie_lot_tresor_public.DLG_Choix_format(self)
            if dlg.ShowModal() == wx.ID_OK:
                format = dlg.GetFormat()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return False
        if format == "pes":
            classe = DLG_Saisie_lot_tresor_public_pes.Dialog
        if format == "magnus":
            classe = DLG_Saisie_lot_tresor_public_magnus.Dialog
        if format == "jvs":
            classe = DLG_Saisie_lot_tresor_public_jvs.Dialog
        if format == "corail":
            classe = DLG_Saisie_lot_tresor_public_corail.Dialog
        return (format, classe)

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
