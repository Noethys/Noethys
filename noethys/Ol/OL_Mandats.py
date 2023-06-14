#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Dates
from Utils import UTILS_Titulaires


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils.UTILS_Mandats import LISTE_SEQUENCES




class Track(object):
    def __init__(self, donnees, dictTitulaires):
        self.IDmandat = donnees[0]
        self.IDfamille = donnees[1]
        self.rum = donnees[2]
        self.typeMandat = donnees[3]
        if self.typeMandat == "recurrent" :
            self.typeMandatStr = _(u"Récurrent")
        else :
            self.typeMandatStr = _(u"Ponctuel")
        self.date = donnees[4]
        if self.date != None :
            self.date = UTILS_Dates.DateEngEnDateDD(self.date)
##        self.IDbanque = donnees[5]
        self.IDindividu = donnees[6]
        self.individu_nom = donnees[7]
        self.individu_rue = donnees[8]
        self.individu_cp = donnees[9]
        self.individu_ville = donnees[10]
        self.iban = donnees[11]
        self.bic = donnees[12]
        self.memo = donnees[13]
        
        # Séquence
        self.sequence = donnees[14]
        self.sequenceStr = ""
        for label, code in LISTE_SEQUENCES :
            if code == self.sequence :
                self.sequenceStr = label
        
        # Actif
        self.actif = donnees[15]
        if self.actif == 1 : 
            self.actif = True
        else :
            self.actif = False
        
        # Titulaire du compte
        if self.IDindividu != None :
            self.individu_nom = donnees[16]
            self.individu_prenom = donnees[17]
            self.individu_nom_complet = u""
            if self.individu_nom != None : self.individu_nom_complet += self.individu_nom + u" "
            if self.individu_prenom != None : self.individu_nom_complet += self.individu_prenom
        else :
            self.individu_nom_complet = self.individu_nom
            
        # Banque
        self.nomBanque = donnees[18]
        
        # NomFamille
        if dictTitulaires != None and self.IDfamille in dictTitulaires :
            self.titulairesFamille = dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.titulairesFamille = u""
        
        # Nbre prélèvements associés
        self.nbrePrelevementsSEPA = donnees[19]
        if self.nbrePrelevementsSEPA == None :
            self.nbrePrelevementsSEPA = 0
        
        self.nbrePieces = donnees[20]
        if self.nbrePieces == None :
            self.nbrePieces = 0
            
        self.nbrePrelevements = self.nbrePrelevementsSEPA + self.nbrePieces
        
        
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.mode = kwds.pop("mode", "famille")
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
        if self.mode == "famille" :
            criteres = "WHERE mandats.IDfamille=%d" % self.IDfamille
            dictTitulaires = None
        else :
            criteres = ""
            dictTitulaires = UTILS_Titulaires.GetTitulaires()
        DB = GestionDB.DB()
        req = """SELECT 
        mandats.IDmandat, mandats.IDfamille, rum, mandats.type, mandats.date, mandats.IDbanque, mandats.IDindividu, individu_nom, individu_rue, individu_cp, individu_ville, iban, bic, mandats.memo, mandats.sequence, actif,
        individus.nom, individus.prenom, banques.nom,
        COUNT(prelevements.IDprelevement), COUNT(pes_pieces.IDpiece)
        FROM mandats
        LEFT JOIN individus ON individus.IDindividu = mandats.IDindividu
        LEFT JOIN banques ON banques.IDbanque = mandats.IDbanque
        LEFT JOIN prelevements ON prelevements.IDmandat = mandats.IDmandat
        LEFT JOIN pes_pieces ON pes_pieces.prelevement_IDmandat = mandats.IDmandat
        %s
        GROUP BY mandats.IDmandat
        """ % criteres
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
                track = Track(item, dictTitulaires)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
            
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def rowFormatter(listItem, track):
            valide = True
            if track.actif == False :
                valide = False
            if valide == False :
                listItem.SetTextColour((180, 180, 180))

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDmandat", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 75, "date", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"RUM"), 'left', 60, "rum", typeDonnee="texte"),
            ColumnDefn(_(u"Type"), 'left', 70, "typeMandatStr", typeDonnee="texte"),
            ColumnDefn(_(u"Nbre prélèv."), 'center', 80, "nbrePrelevements", typeDonnee="entier"),
            ColumnDefn(_(u"IBAN"), 'left', 180, "iban", typeDonnee="texte"),
            ColumnDefn(_(u"BIC"), 'left', 100, "bic", typeDonnee="texte"),
            ColumnDefn(_(u"Titulaire"), 'left', 110, "individu_nom_complet", typeDonnee="texte"),
            ColumnDefn(_(u"Séquence suiv."), 'left', 100, "sequenceStr", typeDonnee="texte"),
            ColumnDefn(_(u"Observations"), 'left', 120, "memo", typeDonnee="texte"),
            ]
        
        if self.mode == "liste" :
            liste_Colonnes.insert(4, ColumnDefn(_(u"Famille"), 'left', 150, "titulairesFamille", typeDonnee="texte"))
            
        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun mandat"))
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
            ID = self.Selection()[0].IDmandat
                
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        if self.mode == "famille" :

            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

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
        self.GenerationContextMenu(menuPop, titre=_(u"Liste des mandats"), orientation=wx.LANDSCAPE)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_mandats", "creer") == False : return
        from Dlg import DLG_Saisie_mandat
        dlg = DLG_Saisie_mandat.Dialog(self, IDfamille=self.IDfamille, IDmandat=None) 
        if dlg.ShowModal() == wx.ID_OK:
            IDmandat = dlg.GetIDmandat()
            self.MAJ(IDmandat)
        dlg.Destroy()

    def Modifier(self, event):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_mandats", "modifier") == False : return
        
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun mandat à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]

        if track.nbrePrelevements > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce mandat a déjà été utilisé pour %d prélèvements. Souhaitez-vous tout de même l'ouvrir ?\n\nAttention, il est déconseillé de modifier un mandat déjà utilisé.") % track.nbrePrelevements, _(u"Avertissement"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
            
        from Dlg import DLG_Saisie_mandat
        dlg = DLG_Saisie_mandat.Dialog(self, IDfamille=track.IDfamille, IDmandat=track.IDmandat)      
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDmandat)
        dlg.Destroy() 

    def Supprimer(self, event):
        if self.IDfamille != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_mandats", "supprimer") == False : return
        
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun mandat à supprimer dans la liste"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        
        # Avertissement si appartient à un prélèvement
        if track.nbrePrelevements > 0 :
            dlg = wx.MessageDialog(self, _(u"Suppression impossible ! \n\nCe mandat est déjà rattaché à %d prélèvements.") % track.nbrePrelevements, _(u"Suppression impossible"), wx.OK|wx.ICON_ERROR)
            dlg.ShowModal() 
            dlg.Destroy()
            return
        
        # Demande de confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la suppression de ce mandat ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("mandats", "IDmandat", track.IDmandat)

##            # Mémorise l'action dans l'historique
##            montant = u"%.2f €" % self.Selection()[0].montant
##            texteMode = self.Selection()[0].nom_mode
##            textePayeur = self.Selection()[0].nom_payeur
##            UTILS_Historique.InsertActions([{
##                "IDfamille" : IDfamille,
##                "IDcategorie" : 8, 
##                "action" : _(u"Suppression du règlement ID%d : %s en %s payé par %s") % (IDreglement, montant, texteMode, textePayeur),
##                },])
            
            DB.Close()
            
            # MAJ de l'affichage
            self.MAJ()
        dlg.Destroy()
        
    def OuvrirFicheFamille(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        from Dlg import DLG_Famille
        dlg = DLG_Famille.Dialog(self, track.IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(track.IDmandat)
        dlg.Destroy()
        


# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, listView=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.listView = listView
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
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
        self.myOlv = ListView(panel, id=-1, mode="liste", IDfamille=14, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
