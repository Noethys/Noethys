#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
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
        self.IDcategorie_tarif = donnees["IDcategorie_tarif"]
        self.nom_categorie_tarif = donnees["nomCategorieTarif"]
        
        # Nom Famille
        if self.IDfamille != None :
            self.titulaires = parent.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
        else :
            self.titulaires = _(u"Aucun titulaire")
        self.listeTitulaires = parent.dictTitulaires[self.IDfamille]["listeTitulaires"]
        
        # Nom Individu
        self.prenomIndividu = donnees["prenom"]
        if self.prenomIndividu == None :
            self.prenomIndividu = ""
        self.nomIndividu = donnees["nom"]
        self.nomCompletIndividu = u"%s %s" % (self.nomIndividu, self.prenomIndividu)

        # Prestations
        self.montant = donnees["montant"]
        
        # Unités de conso
        for IDunite, temp in parent.dictUnitesConso.iteritems() :
            setattr(self, "unite%d" % IDunite, 0)
            
        # Consommations
        self.conso = donnees["conso"]
        for IDunite, quantite in self.conso.iteritems() :
            setattr(self, "unite%d" % IDunite, quantite)
        
        
        self.statut = None
        

                                
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Initialisation du listCtrl
        self.IDactivite = 0
        self.date_debut = None
        self.date_fin = None
        self.categories_tarifs = []
        FastObjectListView.__init__(self, *args, **kwds)
        # DictTitulaires
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        listeListeView = []
        self.dictUnitesConso = {}
        
        if self.date_debut == None or self.date_fin == None :
            return listeListeView
        
        # Récupération des données        
        DB = GestionDB.DB()
        
        # Liste des inscrits
        if len(self.categories_tarifs) == 0 : conditionCategorie = "inscriptions.IDcategorie_tarif=0"
        elif len(self.categories_tarifs) == 1 : conditionCategorie = "inscriptions.IDcategorie_tarif=%d" % self.categories_tarifs[0]
        else : conditionCategorie = "inscriptions.IDcategorie_tarif IN %s" % str(tuple(self.categories_tarifs))
        
        req = """
        SELECT 
        individus.IDindividu, individus.nom, individus.prenom, inscriptions.IDfamille, inscriptions.IDcompte_payeur, inscriptions.IDcategorie_tarif, categories_tarifs.nom
        FROM inscriptions
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = inscriptions.IDcategorie_tarif
        WHERE inscriptions.IDactivite=%d AND %s
        ;""" % (self.IDactivite, conditionCategorie)
        DB.ExecuterReq(req)
        listeInscrits = DB.ResultatReq() 
        
        # Prestations
        req = """
        SELECT IDindividu, IDfamille, SUM(prestations.montant)
        FROM prestations
        WHERE date>='%s' AND date<='%s' AND IDactivite=%d AND categorie='consommation'
        GROUP BY IDindividu, IDfamille
        ;""" % (self.date_debut, self.date_fin, self.IDactivite)
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq() 
        dictPrestations = {}
        for IDindividu, IDfamille, montant in listePrestations :
            montant = FloatToDecimal(montant)
            dictPrestations[(IDindividu, IDfamille)] = montant
        
        # Consommations
        req = """
        SELECT 
        IDconso, consommations.IDindividu, comptes_payeurs.IDfamille, consommations.IDcompte_payeur, consommations.date, consommations.IDunite,
        unites.nom, unites.abrege, unites.ordre
        FROM consommations
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        LEFT JOIN unites ON unites.IDunite = consommations.IDunite
        WHERE consommations.date>='%s' AND consommations.date<='%s' AND consommations.IDactivite=%d
        ;""" % (self.date_debut, self.date_fin, self.IDactivite)
        DB.ExecuterReq(req)
        listeConso = DB.ResultatReq() 
        dictConso = {}
        for IDconso, IDindividu, IDfamille, IDcompte_payeur, date, IDunite, nomUnite, abregeUnite, ordreUnite in listeConso :
            
            # Mémorisation de l'unité de conso
            if self.dictUnitesConso.has_key(IDunite) == False :
                self.dictUnitesConso[IDunite] = {"nom" : nomUnite, "abrege" : abregeUnite, "ordre" : ordreUnite, "quantite" : 0}
            self.dictUnitesConso[IDunite]["quantite"] += 1
                
            # Mémorisation de la conso
            key = (IDindividu, IDfamille)
            if dictConso.has_key(key) == False :
                dictConso[key] = {}
            if dictConso[key].has_key(IDunite) == False :
                dictConso[key][IDunite] = 0
            dictConso[key][IDunite] += 1
        
        DB.Close() 
        
        # Parcours les inscrits
        for IDindividu, nom, prenom, IDfamille, IDcompte_payeur, IDcategorie_tarif, nomCategorieTarif in listeInscrits :
            
            # Recherche les prestations
            if dictPrestations.has_key((IDindividu, IDfamille)) :
                montant = dictPrestations[(IDindividu, IDfamille)]
            else :
                montant = FloatToDecimal(0.0)
            
            # Recherche les consommations
            if dictConso.has_key((IDindividu, IDfamille)) :
                dictConsoIndividu = dictConso[(IDindividu, IDfamille)]
            else :
                dictConsoIndividu = {}
            
            # Mémorisation
            dictTemp = {
                "IDindividu" : IDindividu, "nom" : nom, "prenom" : prenom, "IDfamille" : IDfamille, "IDcompte_payeur" : IDcompte_payeur,
                "IDcategorie_tarif" : IDcategorie_tarif, "nomCategorieTarif" : nomCategorieTarif, "montant" : montant, "conso" : dictConsoIndividu,
                }
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
        
        # Préparation des colonnes
        listeColonnes = [
            ColumnDefn(u"", "left", 0, "IDindividu", typeDonnee="entier"),
            ColumnDefn(_(u""), "left", 20, "statut", typeDonnee="texte", imageGetter=GetImageStatut),
            ColumnDefn(_(u"Individu"), "left", 170, "nomCompletIndividu", typeDonnee="texte"),
            ColumnDefn(_(u"Famille"), "left", 250, "titulaires", typeDonnee="texte"),
            ColumnDefn(_(u"Catégorie de tarif"), "left", 110, "nom_categorie_tarif", typeDonnee="texte"),
            ColumnDefn(_(u"Montant"), "right", 80, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ]
        
        # Ajout des colonnes unités de conso
        listeUnites = []
        for IDunite, dictTemp in self.dictUnitesConso.iteritems() :
            listeUnites.append((dictTemp["ordre"], dictTemp["nom"], dictTemp["abrege"], dictTemp["quantite"], IDunite))
        listeUnites.sort() 
        
        for ordre, nom, abrege, quantite, IDunite in listeUnites :
            listeColonnes.append(ColumnDefn(_(nom), "center", 80, "unite%d" % IDunite, typeDonnee="entier"))       
        
        self.SetColumns(listeColonnes)
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
    
    def SetCategoriesTarifs(self, categories_tarifs=[]):
        self.categories_tarifs = categories_tarifs
        
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
        self.myOlv.SetActivite(1)
        self.myOlv.SetPeriode(date_debut=datetime.date(2015, 1, 1), date_fin=datetime.date(2015, 12, 31))
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
