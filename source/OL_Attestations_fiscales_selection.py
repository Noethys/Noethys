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
import GestionDB
import datetime
import copy

from ObjectListView import ObjectListView, FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from UTILS_Decimal import FloatToDecimal as FloatToDecimal
import UTILS_Titulaires



class Track(object):
    def __init__(self, dictValeurs):
        self.IDcompte_payeur = dictValeurs["IDcompte_payeur"]
        self.IDfamille = dictValeurs["IDfamille"]
        self.nomsTitulairesAvecCivilite = dictValeurs["nomsTitulairesAvecCivilite"]
        self.nomsTitulairesSansCivilite = dictValeurs["nomsTitulairesSansCivilite"]
        self.nomsTitulaires = self.nomsTitulairesSansCivilite
        self.rue_resid = dictValeurs["rue_resid"]
        self.cp_resid = dictValeurs["cp_resid"]
        self.ville_resid = dictValeurs["ville_resid"]
        
        self.montant_total = dictValeurs["montant_total"]
        self.montant_regle = dictValeurs["montant_regle"]
        self.montant_impaye = dictValeurs["montant_impaye"]
        self.listePrestations = dictValeurs["prestations"]
        


class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        self.listePrestations = []
        self.dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

    def OnLeftDown(self, event):
        event.Skip() 
        wx.CallAfter(self.MAJLabelListe)

    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        listePrestations = self.listePrestations 
        dictComptes = {}
        
        for track in listePrestations :
            
            # Recherche si un ajustement est demand�
            ajustement = FloatToDecimal(0.0)
            if track.ajustement not in ("", None) :
                ajustement = FloatToDecimal(float(track.ajustement))
                
            for dictPrestation in track.listePrestations :
                IDcompte_payeur = dictPrestation["IDcompte_payeur"]
                IDfamille = dictPrestation["IDfamille"]

                if dictComptes.has_key(IDcompte_payeur) == False :

                    # R�cup�ration des infos sur la famille
                    dictInfosTitulaires = self.dictTitulaires[IDfamille]
                    rue_resid = dictInfosTitulaires["adresse"]["rue"]
                    cp_resid = dictInfosTitulaires["adresse"]["cp"]
                    if cp_resid == None : cp_resid = u""
                    ville_resid = dictInfosTitulaires["adresse"]["ville"]
                    if ville_resid == None : ville_resid = u""

                    dictComptes[IDcompte_payeur] = {
                        "IDcompte_payeur" : IDcompte_payeur, "IDfamille" : IDfamille, 
                        "nomsTitulairesAvecCivilite" : dictInfosTitulaires["titulairesAvecCivilite"], 
                        "nomsTitulairesSansCivilite" : dictInfosTitulaires["titulairesSansCivilite"], 
                        "rue_resid" : rue_resid,
                        "cp_resid" : cp_resid,
                        "ville_resid" : ville_resid,
                        "prestations" : [], 
                        "montant_total" : FloatToDecimal(0.0), "montant_regle" : FloatToDecimal(0.0), "montant_impaye" : FloatToDecimal(0.0)
                        }
                
                dictPrestation = copy.deepcopy(dictPrestation) 
                
                # Applique les �ventuels ajustements
                montant = dictPrestation["montant"] + ajustement
                if montant < FloatToDecimal(0.0) : 
                    montant = FloatToDecimal(0.0)
                regle = dictPrestation["regle"] + ajustement
                if regle < FloatToDecimal(0.0) : 
                    regle = FloatToDecimal(0.0)
                impaye = montant - regle
                if impaye < FloatToDecimal(0.0) : 
                    impaye = FloatToDecimal(0.0)
                
                dictPrestation["montant"] = montant
                dictPrestation["regle"] = regle
                dictPrestation["impaye"] = impaye
                
                # M�morise les donn�es
                dictComptes[IDcompte_payeur]["prestations"].append(dictPrestation)

                dictComptes[IDcompte_payeur]["montant_total"] += dictPrestation["montant"]
                dictComptes[IDcompte_payeur]["montant_regle"] += dictPrestation["regle"]
                dictComptes[IDcompte_payeur]["montant_impaye"] += dictPrestation["impaye"]
        
        # Regroupement des prestations par label
        listeListeView = []
        for IDcompte_payeur, dictValeurs in dictComptes.iteritems() :
            track = Track(dictValeurs)
            listeListeView.append(track)
        return listeListeView

    def InitObjectListView(self):

        def FormateDate(dateStr):
            if dateStr == "" or dateStr == None : return ""
            date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
            text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
            return text

        def FormateMontant(montant):
            if montant == None or montant == "" or montant == FloatToDecimal(0.0) : return ""
            return u"%.2f %s" % (montant, SYMBOLE)

        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        liste_Colonnes = [
            ColumnDefn(_(u"IDcompte_payeur"), 'left', 0, "IDcompte_payeur", typeDonnee="entier", isEditable=False),
            ColumnDefn(_(u"Famille"), 'left', 290, "nomsTitulairesSansCivilite", typeDonnee="texte", isEditable=True),
            ColumnDefn(_(u"Total"), 'right', 70, "montant_total", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),
            ColumnDefn(_(u"R�gl�"), 'right', 70, "montant_regle", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),
            ColumnDefn(_(u"Impay�"), 'right', 70, "montant_impaye", typeDonnee="montant", stringConverter=FormateMontant, isEditable=False),
            ColumnDefn(_(u"Rue"), 'left', 150, "rue_resid", typeDonnee="texte", isEditable=True),
            ColumnDefn(_(u"CP"), 'left', 50, "cp_resid", typeDonnee="texte", isEditable=True),
            ColumnDefn(_(u"Ville"), 'left', 150, "ville_resid", typeDonnee="texte", isEditable=True),
            ]
        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)

        self.SetEmptyListMsg(_(u"Aucune donn�e"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
        self.cellEditMode = ObjectListView.CELLEDIT_SINGLECLICK
       
    def MAJ(self, listePrestations=[]):
        self.listePrestations = listePrestations
        self.InitModel()
        self.InitObjectListView()
        self._ResizeSpaceFillingColumns() 
        self.CocherPayes()

    def Selection(self):
        return self.GetSelectedObjects()
    
    def CocherPayes(self, event=None):
        for track in self.donnees :
            if track.montant_impaye == FloatToDecimal(0.0) :
                self.Check(track)
            else :
                self.Uncheck(track)
            self.RefreshObject(track)
        self.MAJLabelListe() 

    def CocherTout(self, event=None):
        for track in self.donnees :
            self.Check(track)
            self.RefreshObject(track)
        self.MAJLabelListe() 

    def CocherRien(self, event=None):
        for track in self.donnees :
            self.Uncheck(track)
            self.RefreshObject(track)
        self.MAJLabelListe() 
    
    def MAJLabelListe(self):
        if self.GetParent().GetName() == "DLG_Attestations_fiscales_selection" :
            self.GetParent().staticbox_attestations_staticbox.SetLabel(_(u"Attestations � g�n�rer (%d)") % len(self.GetTracksCoches()))
        
    def GetTracksCoches(self):
        return self.GetCheckedObjects()
    
    def GetInfosCoches(self):
        listeDonnees = []
        for track in self.GetTracksCoches() :
            dictTemp = track.GetDict()
            for code, valeur in self.dictOrganisme.iteritems() :
                dictTemp[code] = valeur
            listeDonnees.append(dictTemp)
        return listeDonnees
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()

        # S�lectionner les pay�s
        item = wx.MenuItem(menuPop, 10, _(u"Cocher uniquement les pay�s"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocherPayes, id=10)

        # Tout s�lectionner
        item = wx.MenuItem(menuPop, 20, _(u"Tout cocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocherTout, id=20)

        # Tout d�-s�lectionner
        item = wx.MenuItem(menuPop, 30, _(u"Tout d�cocher"))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocherRien, id=30)
        
        menuPop.AppendSeparator()
        
        # Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aper�u avant impression"))
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer"))
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Export Texte
        item = wx.MenuItem(menuPop, 600, _(u"Exporter au format Texte"))
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Export Excel
        item = wx.MenuItem(menuPop, 700, _(u"Exporter au format Excel"))
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune donn�e � imprimer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des prestations"), intro="", total="", format="A", orientation=wx.LANDSCAPE)
        if mode == "preview" :
            prt.Preview()
        else:
            prt.Print()
        
    def Apercu(self, event):
        self.Impression("preview")

    def Imprimer(self, event):
        self.Impression("print")

    def ExportTexte(self, event):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des prestations"))
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des prestations"))


# -------------------------------------------------------------------------------------------------------------------------------------


class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
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
    def __init__(self, parent, listePrestations=[]):
        wx.Frame.__init__(self, parent, -1)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ(listePrestations)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
##    import DLG_Attestations_fiscales_parametres
##    frame_1 = DLG_Attestations_fiscales_parametres.MyFrame(None)
##    frame_1.SetSize((980, 650))
##    frame_1.CenterOnScreen() 
##    app.SetTopWindow(frame_1)
##    frame_1.Show()
##    app.MainLoop()

    import DLG_Attestations_fiscales_generation
    dlg = DLG_Attestations_fiscales_generation.Dialog(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()