#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import decimal
import GestionDB
import UTILS_Dates
import DLG_Saisie_prelevement
import DLG_Saisie_prelevement_sepa
import UTILS_Identification
import UTILS_Prelevements
import UTILS_Mandats
import wx.lib.dialogs as dialogs

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"�")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

import UTILS_Titulaires

DICT_BANQUES = {}




class Track(object):
    def __init__(self, donnees, dictTitulaires):
        self.dictTitulaires = dictTitulaires
        self.IDprelevement = donnees["IDprelevement"]
        self.IDlot = donnees["IDlot"]
        self.IDfamille = donnees["IDfamille"]
        self.IDcompte_payeur = donnees["IDcompte_payeur"]

        self.prelevement_banque = donnees["prelevement_banque"]
        self.prelevement_iban =  donnees["prelevement_iban"]
        self.prelevement_bic =  donnees["prelevement_bic"]
        
        self.IDmandat = donnees["IDmandat"]
        self.prelevement_reference_mandat =  donnees["prelevement_reference_mandat"]
        self.prelevement_date_mandat =  donnees["prelevement_date_mandat"]
        self.sequence = donnees["sequence"]
        
        self.titulaire = donnees["titulaire"]
        self.type = donnees["type"]
        self.IDfacture = donnees["IDfacture"]
        self.libelle = donnees["libelle"]
        self.montant = donnees["montant"]
        self.statut = donnees["statut"]
        
        self.MAJnomBanque()
        
        self.titulaires = ""
        self.InitNomsTitulaires() 
        
        self.IDreglement = donnees["IDreglement"]
        if self.IDreglement == None :
            self.reglement = False
        else :
            self.reglement = True
        self.dateReglement = donnees["dateReglement"]
        self.IDdepot = donnees["IDdepot"]
        
        # Lot de pr�l�vements
        self.dateLot = donnees["dateLot"]
        self.nomLot = donnees["nomLot"]
            

    def InitNomsTitulaires(self):
        if self.IDfamille != None :
            self.titulaires = self.dictTitulaires[self.IDfamille]["titulairesSansCivilite"]
    
    def MAJnomBanque(self):
        if DICT_BANQUES.has_key(self.prelevement_banque) :
            self.nomBanque = DICT_BANQUES[self.prelevement_banque]
        else :
            self.nomBanque = u""




    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # R�cup�ration des param�tres perso
        self.IDfamille = kwds.pop("IDfamille", None)
        self.IDmandat = kwds.pop("IDmandat", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.tracks = []
        self.numColonneTri = 1
        self.ordreAscendant = True
        self.dictBanques = {}
        # Initialisation du listCtrl
        self.InitBanques() 
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ R�cup�ration des donn�es """
        self.InitBanques() 
        dictTitulaires = UTILS_Titulaires.GetTitulaires() 
        criteres = ""
        if self.IDfamille != None :
            criteres = "WHERE prelevements.IDfamille=%d" % self.IDfamille
        if self.IDmandat != None :
            criteres = "WHERE prelevements.IDmandat=%d" % self.IDmandat
        DB = GestionDB.DB()
        req = """SELECT 
        prelevements.IDprelevement, prelevements.IDlot, prelevements.IDfamille, 
        prelevement_banque, prelevement_iban, prelevement_bic, 
        prelevements.IDmandat, prelevement_reference_mandat, prelevement_date_mandat,
        prelevements.sequence,
        titulaire, prelevements.type, IDfacture, libelle, prelevements.montant, statut,
        banques.nom,
        reglements.IDreglement, reglements.date, reglements.IDdepot,
        comptes_payeurs.IDcompte_payeur,
        lots_prelevements.date, lots_prelevements.nom
        FROM prelevements
        LEFT JOIN banques ON banques.IDbanque = prelevements.prelevement_banque
        LEFT JOIN reglements ON reglements.IDprelevement = prelevements.IDprelevement
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDfamille = prelevements.IDfamille
        LEFT JOIN lots_prelevements ON lots_prelevements.IDlot = prelevements.IDlot
        %s
        ;""" % criteres
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeListeView = []
        for IDprelevement, IDlot, IDfamille, prelevement_banque, prelevement_iban, prelevement_bic, IDmandat, prelevement_reference_mandat, prelevement_date_mandat, sequence, titulaire, type_prelevement, IDfacture, libelle, montant, statut, nomBanque, IDreglement, dateReglement, IDdepot, IDcompte_payeur, dateLot, nomLot in listeDonnees :
            prelevement_date_mandat = UTILS_Dates.DateEngEnDateDD(prelevement_date_mandat)
            dateLot = UTILS_Dates.DateEngEnDateDD(dateLot)
            dictTemp = {
                "IDprelevement" : IDprelevement, "IDlot" : IDlot, "IDfamille" : IDfamille, 
                "prelevement_banque" : prelevement_banque, "prelevement_iban" : prelevement_iban, "prelevement_bic" : prelevement_bic, 
                "IDmandat" : IDmandat, "prelevement_reference_mandat" : prelevement_reference_mandat, "prelevement_date_mandat" : prelevement_date_mandat,
                "sequence" : sequence, "titulaire" : titulaire, "type" : type_prelevement, "IDfacture" : IDfacture, 
                "libelle" : libelle, "montant" : montant, "statut" : statut, "IDlot" : IDlot, "IDmandat" : IDmandat, "nomBanque" : nomBanque, 
                "IDreglement" : IDreglement, "dateReglement" : dateReglement, "IDdepot" : IDdepot, "IDcompte_payeur" : IDcompte_payeur,
                "dateLot" : dateLot, "nomLot" : nomLot,
                }
            track = Track(dictTemp, dictTitulaires)
            listeListeView.append(track)
        return listeListeView
        
    def InitBanques(self):
        global DICT_BANQUES
        DICT_BANQUES = self.GetNomsBanques()
    
    def GetNomsBanques(self):
        DB = GestionDB.DB()
        req = """SELECT IDbanque, nom
        FROM banques;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictBanques = {}
        for IDbanque, nom in listeDonnees :
            dictBanques[IDbanque] = nom
        return dictBanques
                
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
                
        # Image list
        self.imgValide = self.AddNamedImages("valide", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.imgRefus = self.AddNamedImages("refus", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.imgAttente = self.AddNamedImages("attente", wx.Bitmap("Images/16x16/Attente.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageStatut(track):
            if track.statut == "valide" : return self.imgValide
            if track.statut == "refus" : return self.imgRefus
            if track.statut == "attente" : return self.imgAttente

        def GetImageReglement(track):
            if track.reglement == False :
                return self.imgRefus
            else :
                return self.imgValide

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return UTILS_Dates.DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        def FormateType(statut):
            if statut == "manuel" : return _(u"Manuel")
            if statut == "facture" : return _(u"Facture")
            return ""

        def FormateStatut(statut):
            if statut == "valide" : return _(u"Valide")
            if statut == "refus" : return _(u"Refus")
            if statut == "attente" : return _(u"Attente")

        def FormateReglement(reglement):
            if reglement == True :
                return _(u"Oui")
            else:
                return u""

        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 0, "IDprelevement", typeDonnee="entier"),
            ColumnDefn(_(u"Date pr�l�v."), 'left', 75, "dateLot", typeDonnee="date", stringConverter=FormateDateCourt),
            ColumnDefn(_(u"Lot pr�l�v."), 'left', 150, "nomLot", typeDonnee="texte"),
##            ColumnDefn(_(u"Type"), 'left', 70, "type", stringConverter=FormateType),
            ColumnDefn(_(u"Libell�"), 'left', 110, "libelle", typeDonnee="texte"),
##            ColumnDefn(_(u"Banque"), 'left', 120, "nomBanque"),
            ColumnDefn(_(u"Montant"), 'right', 70, "montant", typeDonnee="montant", stringConverter=FormateMontant),
            ColumnDefn(_(u"Statut"), 'left', 80, "statut", typeDonnee="texte", stringConverter=FormateStatut, imageGetter=GetImageStatut),
            ColumnDefn(_(u"R�glement"), 'left', 70, "reglement", typeDonnee="texte", stringConverter=FormateReglement, imageGetter=GetImageReglement),
            ColumnDefn(_(u"S�quence"), 'left', 70, "sequence", typeDonnee="texte"),
            ColumnDefn(_(u"IBAN"), 'left', 190, "prelevement_iban", typeDonnee="texte"),
            ColumnDefn(_(u"BIC"), 'left', 100, "prelevement_bic", typeDonnee="texte"),
##            ColumnDefn(_(u"Etab."), 'left', 50, "prelevement_etab"),
##            ColumnDefn(_(u"Guich."), 'left', 50, "prelevement_guichet"),
##            ColumnDefn(_(u"Compte"), 'left', 90, "prelevement_numero"),
##            ColumnDefn(_(u"Cl�"), 'left', 30, "prelevement_cle"),
            ColumnDefn(_(u"Banque"), 'left', 130, "nomBanque", typeDonnee="texte"),
            ColumnDefn(_(u"Titulaire du compte"), 'left', 160, "titulaire", typeDonnee="texte"),
            ColumnDefn(_(u"Ref. mandat"), 'left', 90, "prelevement_reference_mandat", typeDonnee="texte"),
            ColumnDefn(_(u"Date mandat"), 'left', 100, "prelevement_date_mandat", typeDonnee="date", stringConverter=FormateDateCourt),
            ]
        
##        if self.IDfamille == None :
##            liste_Colonnes.insert(3, ColumnDefn(_(u"Famille"), 'left', 210, "titulaires"))
            
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucun pr�l�vement"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
##        self.SetSortColumn(self.columns[self.numColonneTri])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
        self.SetObjects(self.donnees)
       
    def MAJ(self):
        self.InitModel()
        self.InitObjectListView()

    def Selection(self):
        return self.GetSelectedObjects()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Cr�ation du menu contextuel
        menuPop = wx.Menu()
    
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

    def Impression(self):
        # R�cup�re l'intitul� du compte
        txtIntro = _(u"Liste des pr�l�vements")
        # R�cup�re le total
        total = 0.0
        for track in self.donnees :
            total += track.montant
        txtTotal = self.GetTexteTotaux().replace("<B>", "").replace("</B>", "")
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=_(u"Liste des pr�l�vements"), intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
        return prt
        
    def Apercu(self, event=None):
        self.Impression().Preview()

    def Imprimer(self, event=None):
        self.Impression().Print()

    def ExportTexte(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportTexte(self, titre=_(u"Liste des pr�l�vements"))
        
    def ExportExcel(self, event=None):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=_(u"Liste des pr�l�vements"))
        
    def GetLabelListe(self):
        """ R�cup�re le nombre de pr�l�vements et le montant total de la liste """
        nbre = 0
        montant = 0.0
        for track in self.GetObjects() :
            nbre += 1
            montant += track.montant
        # Label de staticbox
        if nbre > 1 :
            texte = _(u"pr�l�vements")
        else :
            texte = _(u"pr�l�vement")
        label = u"%d %s (%.2f %s)" % (nbre, texte, montant, SYMBOLE)
        return label          

    def MAJtotaux(self):
        """ Cr�� le texte infos avec les stats du lot """
        if self.GetParent().GetName() != "DLG_Saisie_prelevement_lot" :
            return
        # Label de staticbox
        texte = self.GetTexteTotaux()
        self.GetParent().ctrl_totaux.SetLabel(texte)
        self.GetParent().box_prelevements_staticbox.SetLabel(self.GetLabelListe())

    def GetTexteTotaux(self):
        # R�cup�ration des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.GetObjects() :
            nbreTotal += 1
            montantTotal += track.montant
            # Regroupement par statut
            if dictDetails.has_key(track.statut) == False :
                dictDetails[track.statut] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[track.statut]["nbre"] += 1
            dictDetails[track.statut]["montant"] += track.montant
            # Regroupement par r�glemennt
            if track.reglement == True :
                reglement = "regle"
            else :
                reglement = "pasregle"
            if dictDetails.has_key(reglement) == False :
                dictDetails[reglement] = {"nbre" : 0, "montant" : 0.0}
            dictDetails[reglement]["nbre"] += 1
            dictDetails[reglement]["montant"] += track.montant
            
        # Cr�ation du texte
        if nbreTotal == 0 :
            texte = _(u"<B>Aucun pr�l�vement.   </B>")
        elif nbreTotal == 1 :
            texte = _(u"<B>%d pr�l�vement (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        else :
            texte = _(u"<B>%d pr�l�vements (%.2f %s) : </B>") % (nbreTotal, montantTotal, SYMBOLE)
        
        for key in ("attente", "valide", "refus", "regle", "pasregle") :
            if dictDetails.has_key(key) :
                dictDetail = dictDetails[key]
                if dictDetail["nbre"] == 1 :
                    if key == "attente" : label = _(u"en attente")
                    if key == "valide" : label = _(u"valid�")
                    if key == "refus" : label = _(u"refus�")
                    if key == "regle" : label = _(u"r�gl�")
                    if key == "pasregle" : label = _(u"non r�gl�")
                else :
                    if key == "attente" : label = _(u"en attente")
                    if key == "valide" : label = _(u"valid�s")
                    if key == "refus" : label = _(u"refus�s")
                    if key == "regle" : label = _(u"r�gl�s")
                    if key == "pasregle" : label = _(u"non r�gl�s")
                texteDetail = u"%d %s (%.2f %s), " % (dictDetail["nbre"], label, dictDetail["montant"], SYMBOLE)
                texte += texteDetail
        if len(dictDetails) > 0 :
            texte = texte[:-2] + u"."
        else:
            texte = texte[:-7] + u"</B>"
        return texte






# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1, -1), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(_(u"Rechercher..."))
        self.ShowSearchButton(True)
        
        self.listView = self.parent.ctrl_reglements
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
        
        self.myOlv = ListView(panel, id=-1, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.myOlv.MAJ() 
        
        self.bouton_test = wx.Button(panel, -1, _(u"Bouton test"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.bouton_test)
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton_test, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.SetSize((800, 400))
        self.CenterOnScreen()
        
    def OnBoutonTest(self, event):
        print "Test de la sauvegarde des reglements :"
        self.myOlv.SauvegardeReglements(date=datetime.date.today(), IDcompte=99)
        
        
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
