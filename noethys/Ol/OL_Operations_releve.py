#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from Ctrl import CTRL_Bouton_image
import GestionDB
from Dlg import DLG_Saisie_operation_tresorerie
from Dlg import DLG_Saisie_virement
import datetime

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")


from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

from Utils import UTILS_Utilisateurs
from Utils import UTILS_Dates


class Track(object):
    def __init__(self, donnees):
        self.IDoperation = donnees["IDoperation"]
        self.typeOperation = donnees["typeOperation"]
        self.date = donnees["date"]
        self.libelle = donnees["libelle"]
        self.IDtiers = donnees["IDtiers"]
        self.IDmode = donnees["IDmode"]
        self.num_piece = donnees["num_piece"]
        self.ref_piece = donnees["ref_piece"]
        self.Dcompte_bancaire = donnees["IDcompte_bancaire"]
        self.IDreleve = donnees["IDreleve"]
        self.observations = donnees["observations"]
        self.nomTiers = donnees["nomTiers"]
        self.nomMode = donnees["nomMode"]
        self.nomCompte = donnees["nomCompte"]
        self.nomReleve = donnees["nomReleve"]
        self.montant = donnees["montant"]
        self.IDvirement = donnees["IDvirement"]
        
        if self.typeOperation == "debit" :
            self.debit = self.montant
            self.credit = None
        else :
            self.debit = None
            self.credit = self.montant
            
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDcompte_bancaire = kwds.pop("IDcompte_bancaire", None)
        self.IDreleve = kwds.pop("IDreleve", None)
        self.ctrl_soldes = None
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
    
    def SetCompteBancaire(self, IDcompte_bancaire=None):
        self.IDcompte_bancaire = IDcompte_bancaire
    
    def SetReleve(self, IDreleve=None):
        self.IDreleve = IDreleve
                
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        if self.IDcompte_bancaire == None :
            return []
        
        conditions = "WHERE compta_operations.IDcompte_bancaire=%d" % self.IDcompte_bancaire
        if self.IDreleve != None :
            conditions += " AND (compta_operations.IDreleve IS NULL OR compta_operations.IDreleve=%d)" % self.IDreleve
        else :
            conditions += " AND compta_operations.IDreleve IS NULL"

        db = GestionDB.DB()
        req = """SELECT 
        IDoperation, type, date, libelle, compta_operations.IDtiers, compta_operations.IDmode, num_piece, ref_piece, compta_operations.IDcompte_bancaire, compta_operations.IDreleve, montant, compta_operations.observations, compta_operations.IDvirement,
        compta_tiers.nom, modes_reglements.label, comptes_bancaires.nom, compta_releves.nom
        FROM compta_operations 
        LEFT JOIN compta_tiers ON compta_tiers.IDtiers = compta_operations.IDtiers
        LEFT JOIN modes_reglements ON modes_reglements.IDmode = compta_operations.IDmode
        LEFT JOIN comptes_bancaires ON comptes_bancaires.IDcompte = compta_operations.IDcompte_bancaire
        LEFT JOIN compta_releves ON compta_releves.IDreleve = compta_operations.IDreleve
        %s
        ORDER BY date, IDoperation
        ;""" % conditions
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeListeView = []
        soldeDebit = 0.0
        soldeCredit = 0.0
        soldePointe = 0.0
        for IDoperation, typeOperation, date, libelle, IDtiers, IDmode, num_piece, ref_piece, IDcompte_bancaire, IDreleve, montant, observations, IDvirement, nomTiers, nomMode, nomCompte, nomReleve in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if typeOperation == "debit" :
                soldeDebit += montant
                montantTemp = - montant
            else :
                soldeCredit += montant
                montantTemp = + montant
            if IDreleve != None :
                soldePointe += montantTemp

            dictTemp = {
                "IDoperation" : IDoperation, "typeOperation" : typeOperation, "date" : date, "libelle" : libelle, "IDtiers" : IDtiers, "IDmode" : IDmode, "num_piece" : num_piece, 
                "ref_piece" : ref_piece, "IDcompte_bancaire" : IDcompte_bancaire, "IDreleve" : IDreleve, "montant" : montant, "observations" : observations, "IDvirement" : IDvirement,
                "nomTiers" : nomTiers, "nomMode" : nomMode, "nomCompte" : nomCompte, "nomReleve" : nomReleve, 
                }
            track = Track(dictTemp)
            listeListeView.append(track)
        
##        self.ctrl_soldes.label_solde_jour.SetLabel(_(u"Solde du jour : %.2f %s") % (soldeJour, SYMBOLE))
##        self.ctrl_soldes.label_solde_pointe.SetLabel(_(u"Solde pointé : %.2f %s") % (soldePointe, SYMBOLE))
##        self.ctrl_soldes.label_solde.SetLabel(_(u"Solde final : %.2f %s") % (solde, SYMBOLE))
##        self.ctrl_soldes.Layout() 
        
        return listeListeView
      
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def rowFormatter(listItem, track):
            if track.date > datetime.date.today() :
                listItem.SetTextColour((180, 180, 180))

        def FormateDate(date):
            return UTILS_Dates.DateDDEnFr(date)

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(u"", "left", 0, "IDoperation", typeDonnee="entier"),
            ColumnDefn(_(u"Date"), 'left', 80, "date", typeDonnee="date", stringConverter=FormateDate),
            ColumnDefn(_(u"Libellé"), 'left', 180, "libelle", typeDonnee="texte", isSpaceFilling=True),
            ColumnDefn(_(u"Tiers"), 'left', 130, "nomTiers", typeDonnee="texte"),
            ColumnDefn(_(u"Mode"), 'left', 90, "nomMode", typeDonnee="texte"),
            ColumnDefn(_(u"N° Chèque"), 'left', 80, "num_piece", typeDonnee="texte"),
            ColumnDefn(_(u"Débit"), "right", 80, "debit", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Crédit"), "right", 80, "credit", typeDonnee="montant", stringConverter=FormateMontant),
            ]

        self.rowFormatter = rowFormatter
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        self.SetEmptyListMsg(_(u"Aucune opération"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, track=None, IDoperation=None, IDvirement=None):
        self.Freeze()
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 
        
        if self.IDreleve != None :
            for track in self.donnees :
                 if track.IDreleve == self.IDreleve :
                    self.Check(track)

        self.MAJInformations()
        self.Thaw() 

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Tout cocher
        item = wx.MenuItem(menuPop, 70, _(u"Tout cocher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cocher.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=70)

        # Item Tout décocher
        item = wx.MenuItem(menuPop, 80, _(u"Tout décocher"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Decocher.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=80)

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
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des opérations"), format="A", orientation=wx.LANDSCAPE)
        prt.Preview()

    def Imprimer(self, event):
        from Utils import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des opérations"), format="A", orientation=wx.LANDSCAPE)
        prt.Print()

    def ExportTexte(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des opérations"))
        
    def ExportExcel(self, event):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des opérations"))

    def CocheTout(self, event=None):
        if self.GetFilter() != None :
            listeObjets = self.GetFilteredObjects()
        else :
            listeObjets = self.GetObjects()
        for track in listeObjets :
            self.Check(track)
            self.RefreshObject(track)
        self.MAJInformations() 
        
    def CocheRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)
        self.MAJInformations() 

    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def OnCheck(self, track):
        self.MAJInformations() 
    
    def MAJInformations(self):
        """ MAJ du texte Informations """
        dictDonnees = {
            "nbreOperationsRapprochees" : 0,
            "nbreOperationsDebit" : 0,
            "totalOperationsDebit" : 0.0,
            "nbreOperationsCredit" : 0,
            "totalOperationsCredit" : 0.0,
            "modes" : {},
            }
                    
        for track in self.GetTracksCoches() :
            dictDonnees["nbreOperationsRapprochees"] += 1
            
            if track.typeOperation == "debit" :
                dictDonnees["nbreOperationsDebit"] += 1
                dictDonnees["totalOperationsDebit"] += track.montant
            else :
                dictDonnees["nbreOperationsCredit"] += 1
                dictDonnees["totalOperationsCredit"] += track.montant
            
            if track.IDmode != None :
                if (track.IDmode in dictDonnees["modes"]) == False :
                    dictDonnees["modes"][track.IDmode] = {"nom" : track.nomMode, "nbre" : 0, "total" : 0.0}
                dictDonnees["modes"][track.IDmode]["nbre"] += 1
                dictDonnees["modes"][track.IDmode]["total"] += track.montant

        # Nbre opérations rapprochées
        if dictDonnees["nbreOperationsRapprochees"] == 0 :
            texte = _(u"Aucune opération rapprochée")
        elif dictDonnees["nbreOperationsRapprochees"] == 1 :
            texte = _(u"1 opération rapprochée")
        else :
            texte = _(u"%d opérations rapprochées") % dictDonnees["nbreOperationsRapprochees"]
        
        # Opérations au débit
        if dictDonnees["nbreOperationsDebit"] > 0 :
            if dictDonnees["nbreOperationsDebit"] == 1 :
                texte += _(u"<BR>1 opération au débit : %.2f %s") % (dictDonnees["totalOperationsDebit"], SYMBOLE)
            else :
                texte += _(u"<BR>%d opérations au débit : %.2f %s") % (dictDonnees["nbreOperationsDebit"], dictDonnees["totalOperationsDebit"], SYMBOLE)
                
        # Opérations au crédit
        if dictDonnees["nbreOperationsCredit"] > 0 :
            if dictDonnees["nbreOperationsCredit"] == 1 :
                texte += _(u"<BR>1 opération au crédit : %.2f %s") % (dictDonnees["totalOperationsCredit"], SYMBOLE)
            else :
                texte += _(u"<BR>%d opérations au crédit : %.2f %s") % (dictDonnees["nbreOperationsCredit"], dictDonnees["totalOperationsCredit"], SYMBOLE)
        
        # Modes
        for IDmode, donnees in dictDonnees["modes"].items() :
            if donnees["nbre"] == 1 :
                texte += _(u"<BR>1 opération de type '%s' : %.2f %s") % (donnees["nom"], donnees["total"], SYMBOLE)
            else :
                texte += _(u"<BR>%d opérations de type '%s' : %.2f %s") % (donnees["nbre"], donnees["nom"], donnees["total"], SYMBOLE)
        
        try :
            self.GetParent().SetInformations(texte) 
        except :
            print((texte,))
        
        
        
# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent, listview=None):
        wx.SearchCtrl.__init__(self, parent, size=(-1, 20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = listview
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



### -------------------------------------------------------------------------------------------------------------------------------------------
##
##class ListviewAvecFooter(PanelAvecFooter):
##    def __init__(self, parent, kwargs={}):
##        dictColonnes = {
##            "nomTiers" : {"mode" : "nombre", "singulier" : _(u"opération"), "pluriel" : _(u"opérations"), "alignement" : wx.ALIGN_CENTER},
##            "libelle" : {"mode" : "texte", "texte" : _(u"Solde du jour : 10000.00 €"), "alignement" : wx.ALIGN_CENTER},
##            "solde" : {"mode" : "total"},
##            }
##        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)
##
### -------------------------------------------------------------------------------------------------------------------------------------------

class BarreSoldes(wx.Panel):
    def __init__(self, parent, listview=None):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        self.barreRecherche = BarreRecherche(self, listview)
        self.label_solde_jour = wx.StaticText(self, wx.ID_ANY, _(u"Solde du jour : 0.00 €"))
        self.label_solde_pointe = wx.StaticText(self, wx.ID_ANY, _(u"Solde pointé : 0.00 €"))
        self.label_solde = wx.StaticText(self, wx.ID_ANY, _(u"Solde final : 0.00 €"))

        grid_sizer_1 = wx.FlexGridSizer(1, 4, 0, 0)
        grid_sizer_1.Add(self.barreRecherche, 0, wx.EXPAND | wx.RIGHT, 40)
        
        grid_sizer_1.Add(self.label_solde_jour, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 40)
        grid_sizer_1.Add(self.label_solde_pointe, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 40)
        grid_sizer_1.Add(self.label_solde, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        grid_sizer_1.AddGrowableRow(0)
        grid_sizer_1.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self)
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
    def OnSize(self, event):
        self.Refresh() 
        event.Skip()



class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        self.ctrl_operations = ListView(panel, id=-1, IDcompte_bancaire=1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        
        self.ctrl_soldes = BarreSoldes(self, listview=self.ctrl_operations)
        self.ctrl_operations.ctrl_soldes = self.ctrl_soldes
        
        self.ctrl_operations.MAJ() 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_operations, 1, wx.ALL|wx.EXPAND)
        sizer_2.Add(self.ctrl_soldes, 0, wx.ALL|wx.EXPAND)
        panel.SetSizer(sizer_2)
        self.Layout()



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
