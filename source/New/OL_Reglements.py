#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import decimal
import GestionDB
import UTILS_Historique
import UTILS_Utilisateurs

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

from ObjectListView import FastObjectListView, ColumnDefn, Filter, PanelAvecFooter

from UTILS_Decimal import FloatToDecimal as FloatToDecimal


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))


        
class Track(object):
    def __init__(self, donnees):
        self.IDreglement = donnees[0]
        self.compte_payeur = donnees[1]
        self.IDcompte_payeur = self.compte_payeur
        self.date = DateEngEnDateDD(donnees[2])
        self.IDmode = donnees[3]
        self.nom_mode = donnees[4]
        self.IDemetteur = donnees[5]
        self.nom_emetteur = donnees[6]
        self.numero_piece = donnees[7]
        self.montant = donnees[8]
        self.IDpayeur = donnees[9]
        self.nom_payeur = donnees[10]
        self.observations = donnees[11]
        self.numero_quittancier = donnees[12]
        self.IDprestation_frais = donnees[13]
        self.IDcompte = donnees[14]
        self.date_differe = donnees[15]
        if self.date_differe != None :
            self.date_differe = DateEngEnDateDD(self.date_differe)
        self.encaissement_attente = donnees[16]
        self.IDdepot = donnees[17]
        self.date_depot = donnees[18]
        if self.date_depot != None :
            self.date_depot = DateEngEnDateDD(self.date_depot)
        self.nom_depot = donnees[19]
        self.verrouillage_depot = donnees[20]
        self.date_saisie = donnees[21]
        if self.date_saisie != None :
            self.date_saisie = DateEngEnDateDD(self.date_saisie)
        self.IDutilisateur = donnees[22]
        self.montant_ventilation = donnees[23]
        if self.montant_ventilation == None :
            self.montant_ventilation = 0.0
        if self.montant < 0.0 :
            self.montant_ventilation = None
        self.inclus = True
        self.IDprelevement = donnees[24]

    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDcompte_payeur = kwds.pop("IDcompte_payeur", None)
        self.IDdepot = kwds.pop("IDdepot", None)
        self.mode = kwds.pop("mode", "famille")
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        self.numColonneTri = 1
        self.ordreAscendant = True
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
        if self.mode == "depot" :
            if self.IDdepot == None :
                criteres = "WHERE reglements.IDdepot IS NULL"
            else:
                criteres = "WHERE reglements.IDdepot=%d" % self.IDdepot
        elif self.mode == "liste" :
            criteres = ""
        else:
            criteres = "WHERE reglements.IDcompte_payeur=%d" % self.IDcompte_payeur
            
        # Filtres
        if len(self.listeFiltres) > 0 :
            filtreStr = " AND ".join(self.listeFiltres)
            if criteres == "" :
                criteres = "WHERE " + filtreStr
            else :
                criteres = criteres + " AND " + filtreStr
                
            
        db = GestionDB.DB()
        req = """SELECT 
        reglements.IDreglement, reglements.IDcompte_payeur, reglements.date, 
        reglements.IDmode, modes_reglements.label, 
        reglements.IDemetteur, emetteurs.nom, 
        reglements.numero_piece, reglements.montant, 
        payeurs.IDpayeur, payeurs.nom, 
        reglements.observations, numero_quittancier, IDprestation_frais, reglements.IDcompte, date_differe, 
        encaissement_attente, 
        reglements.IDdepot, depots.date, depots.nom, depots.verrouillage, 
        date_saisie, IDutilisateur,
        SUM(ventilation.montant) AS total_ventilation,
        reglements.IDprelevement
        FROM reglements
        LEFT JOIN ventilation ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN emetteurs ON reglements.IDemetteur=emetteurs.IDemetteur
        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        %s
        GROUP BY reglements.IDreglement
        ORDER BY reglements.date;
        """ % criteres
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
        self.oddRowsBackColor = "#F0FBED" 
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True
        
        # Image list
        self.imgVert = self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ventilation_vert.png", wx.BITMAP_TYPE_PNG))
        self.imgRouge = self.AddNamedImages("erreur", wx.Bitmap("Images/16x16/Ventilation_rouge.png", wx.BITMAP_TYPE_PNG))
        self.imgOrange = self.AddNamedImages("addition", wx.Bitmap("Images/16x16/Ventilation_orange.png", wx.BITMAP_TYPE_PNG))
        
        self.imgAttente = self.AddNamedImages("attente", wx.Bitmap("Images/16x16/Attente.png", wx.BITMAP_TYPE_PNG))
        self.imgOk = self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        self.imgNon = self.AddNamedImages("erreur", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        
        def GetImageVentilation(track):
            if track.montant < FloatToDecimal(0.0) :
                return None
            if track.montant_ventilation == None :
                return self.imgRouge
            resteAVentiler = FloatToDecimal(track.montant) - FloatToDecimal(track.montant_ventilation)
            if resteAVentiler == FloatToDecimal(0.0) :
                return self.imgVert
            if resteAVentiler > FloatToDecimal(0.0) :
                return self.imgOrange
            if resteAVentiler < FloatToDecimal(0.0) :
                return self.imgRouge
        
        def GetImageDepot(track):
            if track.IDdepot == None :
                if track.encaissement_attente == 1 :
                    return self.imgAttente
                else:
                    return self.imgNon
            else:
                return self.imgOk
            
        def FormateDateLong(dateDD):
            return DateComplete(dateDD)

        def FormateDateCourt(dateDD):
            if dateDD == None :
                return ""
            else:
                return DateEngFr(str(dateDD))

        def FormateMontant(montant):
            if montant == None : return u""
            return u"%.2f %s" % (montant, SYMBOLE)

        liste_Colonnes = [
            ColumnDefn(u"ID", "left", 0, "IDreglement"),
            ColumnDefn(u"Date", 'left', 160, "date", stringConverter=FormateDateLong),
            ColumnDefn(u"Mode", 'left', 110, "nom_mode"),
            ColumnDefn(u"Emetteur", 'left', 120, "nom_emetteur"),
            ColumnDefn(u"Numéro", 'left', 60, "numero_piece"),
            ColumnDefn(u"Payeur", 'left', 130, "nom_payeur"),
            ColumnDefn(u"Montant", 'right', 60, "montant", stringConverter=FormateMontant),
            ColumnDefn(u"Ventilé", 'right', 80, "montant_ventilation", stringConverter=FormateMontant, imageGetter=GetImageVentilation),
            ColumnDefn(u"Dépôt", 'left', 90, "date_depot", stringConverter=FormateDateCourt, imageGetter=GetImageDepot),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(u"Aucun règlement")
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
##        self.SetSortColumn(self.columns[1])
        self.SortBy(self.numColonneTri, ascending=self.ordreAscendant)
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
            ID = self.Selection()[0].IDreglement
                
        # Création du menu contextuel
        menuPop = wx.Menu()

        if self.mode != "liste" :

            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, u"Ajouter")
            bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        # Item Modifier
        item = wx.MenuItem(menuPop, 20, u"Modifier")
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, u"Supprimer")
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
        
        # Item Ventilation Automatique
        sousMenuVentilation = wx.Menu()
        
        item = wx.MenuItem(sousMenuVentilation, 201, u"Uniquement le règlement sélectionné")
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        sousMenuVentilation.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.VentilationAuto, id=201)
        if noSelection == True : item.Enable(False)

        item = wx.MenuItem(sousMenuVentilation, 202, u"Tous les règlements")
        item.SetBitmap(wx.Bitmap("Images/16x16/Magique.png", wx.BITMAP_TYPE_PNG))
        sousMenuVentilation.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.VentilationAuto, id=202)

        menuPop.AppendMenu(wx.NewId(), u"Ventilation automatique", sousMenuVentilation)
        
        menuPop.AppendSeparator()
        
        # Item Editer RECU
        item = wx.MenuItem(menuPop, 60, u"Editer un reçu (PDF)")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.EditerRecu, id=60)
        if noSelection == True : item.Enable(False)
        
        menuPop.AppendSeparator()
    
        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, u"Aperçu avant impression")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Apercu, id=40)
        
        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, u"Imprimer")
        bmp = wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Imprimer, id=50)
        
        menuPop.AppendSeparator()
    
        # Item Export Texte
        item = wx.MenuItem(menuPop, 600, u"Exporter au format Texte")
        bmp = wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportTexte, id=600)
        
        # Item Export Excel
        item = wx.MenuItem(menuPop, 700, u"Exporter au format Excel")
        bmp = wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ExportExcel, id=700)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def EditerRecu(self, event):
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun règlement dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDreglement = self.Selection()[0].IDreglement
        import DLG_Impression_recu
        dlg = DLG_Impression_recu.Dialog(self, IDreglement=IDreglement) 
        dlg.ShowModal()
        dlg.Destroy()

    def GetDetailReglements(self):
        # Récupération des chiffres
        nbreTotal = 0
        montantTotal = 0.0
        dictDetails = {}
        for track in self.donnees :
            if track.inclus == True :
                # Montant total
                nbreTotal += 1
                # Nbre total
                montantTotal += track.montant
                # Détail
                if dictDetails.has_key(track.IDmode) == False :
                    dictDetails[track.IDmode] = { "label" : track.nom_mode, "nbre" : 0, "montant" : 0.0}
                dictDetails[track.IDmode]["nbre"] += 1
                dictDetails[track.IDmode]["montant"] += track.montant
        # Création du texte
        texte = u"%d règlements (%.2f €) : " % (nbreTotal, montantTotal)
        for IDmode, dictDetail in dictDetails.iteritems() :
            texteDetail = u"%d %s (%.2f €), " % (dictDetail["nbre"], dictDetail["label"], dictDetail["montant"])
            texte += texteDetail
        if len(dictDetails) > 0 :
            texte = texte[:-2] + u"."
        else:
            texte = texte[:-7] 
        return texte

    def Impression(self, mode="preview"):
        if self.donnees == None or len(self.donnees) == 0 :
            dlg = wx.MessageDialog(self, u"Il n'y a aucune donnée à imprimer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        txtIntro = u""
        total = 0.0
        for track in self.donnees :
            total += track.montant
        txtTotal = self.GetDetailReglements() 
        import UTILS_Printer
        prt = UTILS_Printer.ObjectListViewPrinter(self, titre=u"Liste des règlements", intro=txtIntro, total=txtTotal, format="A", orientation=wx.LANDSCAPE)
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
        UTILS_Export.ExportTexte(self, titre=u"Liste des règlements")
        
    def ExportExcel(self, event):
        import UTILS_Export
        UTILS_Export.ExportExcel(self, titre=u"Liste des règlements")

    def Ajouter(self, event):
        if self.IDcompte_payeur != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_reglements", "creer") == False : return
        
        import DLG_Saisie_reglement
        dlg = DLG_Saisie_reglement.Dialog(self, IDcompte_payeur=self.IDcompte_payeur, IDreglement=None) 
        if dlg.ShowModal() == wx.ID_OK:
            IDreglement = dlg.GetIDreglement()
            self.MAJ(IDreglement)
        dlg.Destroy()

    def ReglerFacture(self, IDfacture=None):
        import DLG_Saisie_reglement
        dlg = DLG_Saisie_reglement.Dialog(self, IDcompte_payeur=self.IDcompte_payeur, IDreglement=None) 
        dlg.SelectionneFacture(IDfacture)
        if dlg.ShowModal() == wx.ID_OK:
            IDreglement = dlg.GetIDreglement()
            self.MAJ(IDreglement)
        dlg.Destroy()

    def Modifier(self, event):
        if self.IDcompte_payeur != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_reglements", "modifier") == False : return
        
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun règlement à modifier dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDreglement = self.Selection()[0].IDreglement

        # Avertissement si appartient à un prélèvement
        if self.Selection()[0].IDprelevement != None :
            dlg = wx.MessageDialog(self, u"Ce règlement est rattaché à un prélèvement automatique.\n\nSouhaitez-vous vraiment le modifier ?", u"Avertissement", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        import DLG_Saisie_reglement
        dlg = DLG_Saisie_reglement.Dialog(self, IDcompte_payeur=self.IDcompte_payeur, IDreglement=IDreglement)      
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(IDreglement)
        dlg.Destroy() 

    def Supprimer(self, event):
        if self.IDcompte_payeur != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_reglements", "supprimer") == False : return
        
        if len(self.Selection()) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun règlement à supprimer dans la liste", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDreglement = self.Selection()[0].IDreglement
        IDdepot = self.Selection()[0].IDdepot
        
        # Si appartient à un dépot : annulation
        if IDdepot != None :
            dlg = wx.MessageDialog(self, u"Ce règlement est déjà attribué à un dépôt. Vous ne pouvez donc pas le supprimer !", u"Règlement déposé", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Avertissement si appartient à un prélèvement
        if self.Selection()[0].IDprelevement != None :
            dlg = wx.MessageDialog(self, u"Ce règlement est rattaché à un prélèvement automatique.\n\nSouhaitez-vous vraiment le supprimer ?", u"Avertissement", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Recherche si frais de gestion existant pour ce règlement
        DB = GestionDB.DB()
        req = """SELECT IDprestation, montant_initial, label
        FROM prestations
        WHERE reglement_frais=%d;
        """ % IDreglement
        DB.ExecuterReq(req)
        listeFrais = DB.ResultatReq()
        DB.Close()
        if len(listeFrais) > 0 :
            IDprestationFrais, montantFrais, labelFrais = listeFrais[0]
            dlg = wx.MessageDialog(self, u"Une prestation d'un montant de %.2f %s pour frais de gestion est associée à ce règlement. Cette prestation sera automatiquement supprimée en même temps que le règlement.\n\nConfirmez-vous tout de même la suppression de ce règlement ?" % (montantFrais, SYMBOLE), u"Avertissement", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            if dlg.ShowModal() != wx.ID_YES :
                return
        else :
            IDprestationFrais = None
        
        # Demande de confirmation de suppression
        dlg = wx.MessageDialog(self, u"Confirmez-vous la suppression de ce règlement ?", u"Suppression", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("reglements", "IDreglement", IDreglement)
            DB.ReqDEL("ventilation", "IDreglement", IDreglement)
            # Mémorise l'action dans l'historique
            req = """SELECT IDfamille
            FROM comptes_payeurs
            WHERE IDcompte_payeur=%d
            """ % self.Selection()[0].compte_payeur
            DB.ExecuterReq(req)
            IDfamille = DB.ResultatReq()[0][0]
            
            montant = u"%.2f €" % self.Selection()[0].montant
            texteMode = self.Selection()[0].nom_mode
            textePayeur = self.Selection()[0].nom_payeur
            UTILS_Historique.InsertActions([{
                "IDfamille" : IDfamille,
                "IDcategorie" : 8, 
                "action" : u"Suppression du règlement ID%d : %s en %s payé par %s" % (IDreglement, montant, texteMode, textePayeur),
                },])
            
            # Suppression des frais de gestion
            if IDprestationFrais != None :
                DB.ReqDEL("prestations", "IDprestation", IDprestationFrais)
                DB.ReqDEL("ventilation", "IDprestation", IDprestationFrais)
            
            DB.Close()
            
            # MAJ de l'affichage
            self.MAJ()
        dlg.Destroy()
        

    def VentilationAuto(self, event):
        if self.IDcompte_payeur != None and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_reglements", "modifier") == False : return
        
        from OL_Verification_ventilation import VentilationAuto
        ID = event.GetId() 
        if ID == 201 :
            # Uniquement la ligne sélectionnée
            if len(self.Selection()) == 0 :
                dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucun règlement !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            track = self.Selection()[0]
            VentilationAuto(IDcompte_payeur=track.IDcompte_payeur, IDreglement=track.IDreglement)
            self.MAJ(track.IDreglement)
        # Toutes les lignes
        if ID == 202 :
            if len(self.donnees) == 0 :
                dlg = wx.MessageDialog(self, u"La liste des règlements est vide !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            track = self.donnees[0]
            VentilationAuto(IDcompte_payeur=track.IDcompte_payeur)
            self.MAJ()



# -------------------------------------------------------------------------------------------------------------------------------------------

class BarreRecherche(wx.SearchCtrl):
    def __init__(self, parent):
        wx.SearchCtrl.__init__(self, parent, size=(-1,20), style=wx.TE_PROCESS_ENTER)
        self.parent = parent
        self.rechercheEnCours = False
        
        self.SetDescriptiveText(u"Rechercher un règlement...")
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

class ListviewAvecFooter(PanelAvecFooter):
    def __init__(self, parent, kwargs={}):
        dictColonnes = {
            "nom_mode" : {"mode" : "nombre", "singulier" : u"règlement", "pluriel" : u"règlements", "alignement" : wx.ALIGN_CENTER},
            "montant" : {"mode" : "total"},
            "montant_ventilation" : {"mode" : "total"},
            }
        PanelAvecFooter.__init__(self, parent, ListView, kwargs, dictColonnes)


# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, id=-1, IDcompte_payeur=373, name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
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
