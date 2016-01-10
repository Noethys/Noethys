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
import decimal
import GestionDB
import UTILS_Dates
from UTILS_Decimal import FloatToDecimal as FloatToDecimal

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import UTILS_Titulaires
import UTILS_Utilisateurs

import UTILS_Interface
from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils, PanelAvecFooter


class Track(object):
    def __init__(self, parent, donnees):
        self.IDindividu = donnees["IDindividu"]
        self.IDfamille = donnees["IDfamille"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]    
        if self.IDfamille != None :
            self.titulaires = parent.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.titulaires = _(u"Aucun titulaire")
        self.listeTitulaires = parent.dictTitulaires[self.IDfamille]["listeTitulaires"]
        self.montant = donnees["montant"]
        self.quantite = donnees["quantite"]
        self.listePrestations = donnees["prestations"]
        
        self.prenomIndividu = donnees["prenomIndividu"]
        if self.prenomIndividu == None :
            self.prenomIndividu = ""
        self.nomIndividu = donnees["nomIndividu"]
        self.nomCompletIndividu = u"%s %s" % (self.nomIndividu, self.prenomIndividu)
        
        self.statut = None
        
        
                                
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.IDactivite = 0
        self.date_debut = None
        self.date_fin = None
        FastObjectListView.__init__(self, *args, **kwds)
        # DictTitulaires
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        # Récupération des données
        listeID = None
        
        DB = GestionDB.DB()
        
        req = """
        SELECT 
        IDprestation, prestations.IDindividu, IDfamille, IDcompte_payeur, date, montant,
        individus.nom, individus.prenom
        FROM prestations
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE date>='%s' AND date<='%s' AND IDactivite=%d AND categorie='consommation'
        GROUP BY IDprestation
        ;""" % (self.date_debut, self.date_fin, self.IDactivite)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq() 
        DB.Close() 
        
        dictResultats = {}
        for IDprestation, IDindividu, IDfamille, IDcompte_payeur, date, montant, nomIndividu, prenomIndividu in listePrestations :
            date = UTILS_Dates.DateEngEnDateDD(date)  
            montant = FloatToDecimal(montant)
            
            key = (IDindividu, IDfamille)
            if dictResultats.has_key(key) == False :
                dictResultats[key] = {"IDindividu" : IDindividu, "nomIndividu" : nomIndividu, "prenomIndividu" : prenomIndividu, "IDfamille" : IDfamille, "IDcompte_payeur" : IDcompte_payeur, "prestations" : [], "quantite" : 0, "montant" : FloatToDecimal(0.0)}            
            dictResultats[key]["prestations"].append({"IDprestation" : IDprestation, "montant" : montant})
            dictResultats[key]["montant"] += montant
            dictResultats[key]["quantite"] += 1
    
        listeListeView = []
        for key, dictTemp in dictResultats.iteritems() :
            track = Track(self, dictTemp)
            listeListeView.append(track)
        return listeListeView


    def InitObjectListView(self):
        # ImageList
        self.imageOk = self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.imageErreur = self.AddNamedImages("erreur", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageStatut(track):
            if track.statut == "ok" : 
                return self.imageOk
            if track.statut == "erreur" : 
                return self.imageErreur
            return None

        def FormateMontant(montant):
            if montant == None or montant == "" : return ""
            return u"%.2f %s" % (montant, SYMBOLE)
                   
        def rowFormatter(listItem, track):
            if track.valide == False :
                listItem.SetTextColour(wx.Colour(150, 150, 150))
                
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = "#FFFFFF" # Vert
        
        # Paramètres ListView
        self.useExpansionColumn = True
        self.SetColumns([
            ColumnDefn(u"", "left", 0, "IDindividu", typeDonnee="entier"),
            ColumnDefn(_(u""), "left", 20, "statut", typeDonnee="texte", imageGetter=GetImageStatut),
            ColumnDefn(_(u"Individu"), "left", 170, "nomCompletIndividu", typeDonnee="texte"),
            ColumnDefn(_(u"Famille"), "left", 250, "titulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Nbre Prest."), "center", 80, "quantite", typeDonnee="entier"),
            ColumnDefn(_(u"Montant"), "right", 80, "montant", typeDonnee="montant", stringConverter=FormateMontant),
        ])
        self.CreateCheckStateColumn(1)
        self.SetSortColumn(self.columns[3])
        self.SetEmptyListMsg(_(u"Aucun individu"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetObjects(self.donnees)
    
    def GetListeIndividus(self):
        return self.listeIndividus
            
    def GetTotal(self):
        return self.total 
    
    def SetPeriode(self, date_debut=None, date_fin=None):
        self.date_debut = date_debut
        self.date_fin = date_fin
    
    def SetActivite(self, IDactivite=None) :
        if IDactivite == None :
            IDactivite = 0
        self.IDactivite = IDactivite
        
    def MAJ(self, ID=None):
        self.InitModel()
        self.InitObjectListView()
        self.Refresh()
        self.CocheTout()
    
    def Selection(self):
        return self.GetSelectedObjects()
    
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        ID = None
        if len(self.Selection()) > 0 :
            ID = self.Selection()[0].IDfamille
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ouverture fiche famille
        item = wx.MenuItem(menuPop, 10, _(u"Ouvrir la fiche famille"))
        bmp = wx.Bitmap("Images/16x16/Famille.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OuvrirFicheFamille, id=10)
        if ID == None : item.Enable(False)
        
        menuPop.AppendSeparator()

        # Item Tout cocher
        item = wx.MenuItem(menuPop, 70, _(u"Tout cocher"))
        bmp = wx.Bitmap("Images/16x16/Cocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=70)

        # Item Tout décocher
        item = wx.MenuItem(menuPop, 80, _(u"Tout décocher"))
        bmp = wx.Bitmap("Images/16x16/Decocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=80)

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des individus"), format="A", orientation=wx.PORTRAIT)
        prt.Preview()

    def Imprimer(self, event):
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des individus"), format="A", orientation=wx.PORTRAIT)
        prt.Print()

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des individus"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des individus"))
        
    def CocheTout(self, event=None):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            self.Check(track)
            self.RefreshObject(track)
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)

    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def OuvrirFicheFamille(self, event):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_fiche", "consulter") == False : return
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune fiche famille à ouvrir !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        track = self.Selection()[0]
        import DLG_Famille
        dlg = DLG_Famille.Dialog(self, track.IDfamille)
        dlg.ShowModal()
        dlg.Destroy()
        self.MAJ(track.IDfamille)

# -------------------------------------------------------------------------------------------------------------------------------------------

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nomCompletIndividu" : {"mode" : "nombre", "singulier" : _(u"individu"), "pluriel" : _(u"individus"), "alignement" : wx.ALIGN_CENTER},
            "quantite" : {"mode" : "total", "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


# ----------------- FRAME DE TEST ----------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.myOlv.SetPeriode(date_debut=datetime.date(2013, 1, 1), date_fin=datetime.date(2013, 12, 31))
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((800, 400))
        self.Layout()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "GroupListView")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
