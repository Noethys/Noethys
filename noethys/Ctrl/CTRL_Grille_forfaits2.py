#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB
from Utils import UTILS_Gestion
from Utils import UTILS_Titulaires
            

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        

class CTRL_Forfait(HTL.HyperTreeList):
    def __init__(self, parent, grille=None, listePrestations=[]): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.SetAGWWindowStyleFlag(HTL.TR_NO_HEADER | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT )
        self.parent = parent
        self.grille = grille
        self.dictForfaits = {}
        self.listeSelectionIndividus = []
        self.dictActivites = {}
        
        self.SetBackgroundColour(wx.WHITE)
        
        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Périodes de gestion
        self.gestion = UTILS_Gestion.Gestion(self)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.Modifier)
        self.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnContextMenu) 
        
    def Initialisation(self):               
        # Création des colonnes
        self.AddColumn(_(u"Prestations"))
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 200)
        
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))

        # Préparation des données
        dictDonnees = {}
        self.dictImages = {}
        il = wx.ImageList(9, 16)
        for IDprestation, dictForfait in self.dictForfaits.items() :
            IDfamille = dictForfait["IDfamille"]
            IDindividu = dictForfait["IDindividu"]
            
            if IDindividu == 0 or IDindividu == None :
                # Forfait familial
                if (IDfamille in dictDonnees) == False :
                    dictDonnees[IDfamille] = {"forfaits":[], "individus":{}}
                dictDonnees[IDfamille]["forfaits"].append(dictForfait)
            else :
                # Forfait individuel
                if IDindividu in self.listeSelectionIndividus :
                    if (IDfamille in dictDonnees) == False :
                        dictDonnees[IDfamille] = {"forfaits":[], "individus":{}}
                    if (IDindividu in dictDonnees[IDfamille]["individus"]) == False :
                        dictDonnees[IDfamille]["individus"][IDindividu] = {"nomIndividu":dictForfait["nomIndividu"], "forfaits":[]}
                    dictDonnees[IDfamille]["individus"][IDindividu]["forfaits"].append(dictForfait)
            
            # Couleur du forfait
            couleur = dictForfait["couleur"]
            self.dictImages[IDprestation] = il.Add(self.CreationImage(couleur))
            
        if il.GetImageCount() > 0 :
            self.AssignImageList(il)
        
        # Recherche du nom des titulaires
        dictTitulaires = UTILS_Titulaires.GetTitulaires(list(dictDonnees.keys()))

        # Création des branches
        famillesAffichees = False
        for IDfamille, dictFamille in dictDonnees.items() :
            
            # Branche famille
            if len(list(dictDonnees.keys())) > 1 or len(dictFamille["forfaits"]) > 0 :
                famillesAffichees = True
                label = _(u"Famille %s") % dictTitulaires[IDfamille]["titulairesSansCivilite"]
                brancheFamille = self.AppendItem(self.root, label)
                self.SetPyData(brancheFamille, {"type":"famille", "donnees":IDfamille})
                self.SetItemBackgroundColour(brancheFamille, (200, 200, 200) )
                self.SetItemTextColour(brancheFamille, (120, 120, 120) )

                
                for dictForfait in dictFamille["forfaits"] :
                    self.CreationBrancheForfait(brancheFamille, dictForfait)
            else :
                brancheFamille = self.root
            
            # Branche Individu
            for IDindividu, dictIndividu in dictFamille["individus"].items() :
                
                if len(dictFamille["individus"]) > 1 or famillesAffichees == True or len(self.listeSelectionIndividus) > 1 :
                    label = dictIndividu["nomIndividu"]
                    brancheIndividu = self.AppendItem(brancheFamille, label)
                    self.SetItemBold(brancheIndividu, True)
                    self.SetPyData(brancheIndividu, {"type":"individu", "donnees":IDindividu})
                else:
                    brancheIndividu = brancheFamille
                    
                # Branche Forfait
                for dictForfait in dictIndividu["forfaits"] :
                    self.CreationBrancheForfait(brancheIndividu, dictForfait)
                    
        self.ExpandAllChildren(self.root)
                
    def CreationBrancheForfait(self, brancheParente, dictForfait):
        label = dictForfait["label"]
        branche = self.AppendItem(brancheParente, label)
        self.SetPyData(branche, {"type":"forfait", "donnees":dictForfait})
        self.SetItemImage(branche, self.dictImages[dictForfait["IDprestation"]], wx.TreeItemIcon_Normal)
        return branche
        
    def CreationImage(self, couleur=(0, 0, 0)):
        """ Création des images pour le TreeCtrl """
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(9, 16)
        else :
            bmp = wx.EmptyBitmap(9, 16)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush("WHITE"))
        dc.Clear()
        dc.SetBrush(wx.Brush(couleur, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
##        dc.DrawCircle(5, 9, 4)
        dc.DrawPolygon([(0, 0), (9, 0), (0, 9)], xoffset=0, yoffset=4)
        del dc
        return bmp
                        
                            
    def OnCompareItems(self, item1, item2):
        if self.GetPyData(item1) > self.GetPyData(item2) :
            return 1
        elif self.GetPyData(item1) < self.GetPyData(item2) :
            return -1
        else:
            return 0
                    
    def MAJ(self, dictForfaits={}, listeSelectionIndividus=[]):
        self.dictForfaits = dictForfaits
        self.listeSelectionIndividus = listeSelectionIndividus
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
            
    def OnContextMenu(self, event):
        pos = event.GetPosition()
        item, flags, col = self.HitTest(pos)
        if col != -1 :
            self.SelectItem(item)
        
        if item != None :
            dataItem = self.GetItemPyData(item)
        else:
            dataItem = None
        
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
        if col == -1 or dataItem == None or dataItem["type"] != "forfait" : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if col == -1 or dataItem == None or dataItem["type"] != "forfait" : item.Enable(False)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event=None, date_debut=None, IDfamille=None):
        from Dlg import DLG_Saisie_forfait_credit
        dlg = DLG_Saisie_forfait_credit.Dialog(self, grille=self.grille, listeFamilles=self.grille.GetFamillesAffichees())
        if date_debut != None :
            dlg.SetDateDebut(date_debut)
        if IDfamille != None :
            dlg.SetFamille(IDfamille)
        if dlg.ShowModal() == wx.ID_OK:
            IDfamille = dlg.GetFamille() 
            IDcompte_payeur = dlg.GetComptePayeur()
            date_debut = dlg.GetDateDebut() 
            date_fin = dlg.GetDateFin()
            dictTarif = dlg.GetForfait()
            label = dlg.GetLabel()
            datePrestation = dlg.GetDatePrestation() 
            montant = dlg.GetMontant()
            
            IDindividu = dictTarif["resultat"]["IDindividu"]
            
            # Création de la prestation
            IDprestation = self.grille.MemorisePrestation(IDcompte_payeur, datePrestation, dictTarif["IDactivite"], dictTarif["IDtarif"], label, 
                                                                            montant, dictTarif["resultat"]["montant_tarif"], IDfamille, IDindividu, 
                                                                            listeDeductions=[], temps_facture=dictTarif["resultat"]["temps_facture"], IDcategorie_tarif=dictTarif["resultat"]["IDcategorie_tarif"],
                                                                            forfait_date_debut=date_debut, forfait_date_fin=date_fin)
            
            # Affichage de la prestation
            try :
                listeNouvellesPrestations = [IDprestation,]
                listeAnciennesPrestations = []
                self.grille.GetGrandParent().panel_facturation.SaisiePrestation(
                        self.grille.dictPrestations,
                        self.grille.dictDeductions,
                        listeNouvellesPrestations,
                        listeAnciennesPrestations,
                        self.grille.listeSelectionIndividus,
                        self.grille.listeActivites,
                        self.grille.listePeriodes,
                        )
            except :
                pass
                
            # Affichage dans la liste des forfaits
            dictTemp = self.grille.dictPrestations[IDprestation].copy()
            dictTemp["forfait_date_debut"] = date_debut
            dictTemp["forfait_date_fin"] = date_fin
            dictTemp["couleur"] = self.grille.CreationCouleurForfait(index=len(self.grille.dictForfaits))
            self.grille.dictForfaits[IDprestation] = dictTemp

            # MAJ du contrôle Forfaits
            self.MAJ(self.grille.dictForfaits, self.grille.listeSelectionIndividus)

            # Propose éventuellement un recalcul des conso déjà présentes
            nbreConso = 0
            for IDindividuTemp, dictIndividu in self.grille.dictConsoIndividus.items() :
                for dateDD, dictDate in dictIndividu.items() :
                    for IDunite, listeConso in dictDate.items() :
                        for conso in listeConso :
                            case = conso.case
                            if case != None and case.date >= date_debut and case.date <= date_fin :
                                if case.IDindividu == IDindividu or IDindividu == None or IDindividu == 0 : 
                                    nbreConso += 1

            # Demande la confirmation de la suppression du forfait
            if nbreConso > 0 :
                dlg2 = wx.MessageDialog(None, _(u"Souhaitez-vous recalculer les prestations affichées (conseillé) ?"), _(u"Recalcul"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                if dlg2.ShowModal() == wx.ID_YES :
                    self.grille.RecalculerToutesPrestations() 
                dlg2.Destroy()

        dlg.Destroy()
        


    def Modifier(self, event=None):
        item = self.GetSelection()
        dataItem = self.GetItemPyData(item)
        if dataItem == None or dataItem["type"] != "forfait" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun forfait à modifier dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        donnees = dataItem["donnees"]
        IDprestation = donnees["IDprestation"] 

        # Vérifie si le forfait est déjà facturé
        if donnees["IDfacture"] != None :
            dlg = wx.MessageDialog(self, _(u"Ce forfait apparaît déjà sur une facture. Il n'est pas possible de le modifier !"), _(u"Attention"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Périodes de gestion
        if self.gestion.IsPeriodeinPeriodes("consommations", donnees["forfait_date_debut"], donnees["forfait_date_fin"]) == False: return False
        if self.gestion.Verification("prestations", donnees["date"]) == False: return False

        from Dlg import DLG_Saisie_forfait_credit
        dlg = DLG_Saisie_forfait_credit.Dialog(self, grille=self.grille, listeFamilles=self.grille.GetFamillesAffichees())
        dlg.SetFamille(donnees["IDfamille"]) 
        dlg.SetDateDebut(donnees["forfait_date_debut"]) 
        dlg.SetDateFin(donnees["forfait_date_fin"])
        dlg.SetForfait(donnees["IDindividu"], donnees["IDtarif"])
        dlg.SetLabel(donnees["label"])
        dlg.SetDatePrestation(donnees["date"]) 
        dlg.SetMontant(donnees["montant_initial"])
        dlg.ctrl_famille.Enable(False)
##        dlg.ctrl_forfaits.Activation(False)

        if dlg.ShowModal() == wx.ID_OK:
            date_debut = dlg.GetDateDebut()
            date_fin = dlg.GetDateFin()
            dictTarif = dlg.GetForfait()
            label = dlg.GetLabel()
            datePrestation = dlg.GetDatePrestation() 
            montant = dlg.GetMontant()
            
            IDindividu = dictTarif["resultat"]["IDindividu"]
            
            # Création de la prestation
            self.grille.dictPrestations[IDprestation]["label"] = label
            self.grille.dictPrestations[IDprestation]["date"] = datePrestation
            self.grille.dictPrestations[IDprestation]["montant_initial"] = montant
            self.grille.dictPrestations[IDprestation]["montant"] = montant
            self.grille.dictPrestations[IDprestation]["forfait_date_debut"] = date_debut
            self.grille.dictPrestations[IDprestation]["forfait_date_fin"] = date_fin
            self.grille.listePrestationsModifiees.append(IDprestation)
            
            # Affichage de la prestation
            if IDindividu == None :
                IDindividu = 0
            try :
                self.grille.GetGrandParent().panel_facturation.ModifiePrestation(datePrestation, IDindividu, IDprestation, 
                                                                                self.grille.dictPrestations[IDprestation]["montantVentilation"], nouveauMontant=montant,
                                                                                nouveauLabel=label)
            except :
                pass
                
            # Affichage dans la liste des forfaits
            dictTemp = self.grille.dictPrestations[IDprestation].copy()
            dictTemp["forfait_date_debut"] = date_debut
            dictTemp["forfait_date_fin"] = date_fin
            dictTemp["couleur"] = self.grille.dictForfaits[IDprestation]["couleur"]
            self.grille.dictForfaits[IDprestation] = dictTemp

            # MAJ du contrôle Forfaits
            self.MAJ(self.grille.dictForfaits, self.grille.listeSelectionIndividus)

            # Propose éventuellement un recalcul des conso déjà présentes
            nbreConso = 0
            for IDindividuTemp, dictIndividu in self.grille.dictConsoIndividus.items() :
                for dateDD, dictDate in dictIndividu.items() :
                    for IDunite, listeConso in dictDate.items() :
                        for conso in listeConso :
                            case = conso.case
                            if case != None and case.date >= date_debut and case.date <= date_fin :
                                if case != None and case.IDindividu == IDindividu or IDindividu == None or IDindividu == 0 : 
                                    nbreConso += 1

            # Demande la confirmation de la suppression du forfait
            if nbreConso > 0 :
                dlg2 = wx.MessageDialog(None, _(u"Souhaitez-vous recalculer les prestations affichées (conseillé) ?"), _(u"Recalcul"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                if dlg2.ShowModal() == wx.ID_YES :
                    self.grille.RecalculerToutesPrestations() 
                dlg2.Destroy()

        dlg.Destroy()

    def Supprimer(self, event=None):
        item = self.GetSelection()
        dataItem = self.GetItemPyData(item)
        if dataItem == None or dataItem["type"] != "forfait" :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucun forfait à supprimer dans la liste !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        donnees = dataItem["donnees"]
        IDprestation = donnees["IDprestation"] 

        # Vérifie si le forfait est déjà facturé
        if donnees["IDfacture"] != None :
            dlg = wx.MessageDialog(self, _(u"Ce forfait apparaît déjà sur une facture. Il n'est pas possible de le supprimer !"), _(u"Attention"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Périodes de gestion
        if self.gestion.IsPeriodeinPeriodes("consommations", donnees["forfait_date_debut"], donnees["forfait_date_fin"]) == False: return False
        if self.gestion.Verification("prestations", donnees["date"]) == False: return False

        # Vérifie si des consommations du forfait existent déjà sur d'autres périodes non affichées
        listeConso = []
        for IDindividu, dictIndividu in self.grille.dictConsoIndividus.items() :
            for dateDD, dictDate in dictIndividu.items() :
                for IDunite, listeConsoTemp in dictDate.items() :
                    for conso in listeConsoTemp :
                        if conso.IDconso != None :
                            listeConso.append(conso.IDconso)
        
        DB = GestionDB.DB()
        req = """SELECT IDconso, IDindividu, date
        FROM consommations
        WHERE IDprestation=%d;""" % IDprestation
        DB.ExecuterReq(req)
        listeConsommations = DB.ResultatReq()
        DB.Close()
        nbreConsoNonAffichees = 0
        for IDconso, IDindividu, date in listeConsommations :
            if IDconso not in listeConso :
                nbreConsoNonAffichees += 1
        
        if nbreConsoNonAffichees > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce forfait contient %d consommation(s) qui ne sont pas affichées ici. Il n'est donc pas possible de le supprimer maintenant !") % nbreConsoNonAffichees, _(u"Attention"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Demande la confirmation de la suppression du forfait
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment supprimer ce forfait ?"), _(u"Suppression"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        dlg.Destroy()

        # Supprime la prestation dans le dictPrestations
        self.grille.SupprimerPrestation(IDprestation, donnees["categorie"])
        
        # Supprime la prestation dans le dictForfaits
        del self.grille.dictForfaits[IDprestation]
        self.MAJ(self.grille.dictForfaits, self.grille.listeSelectionIndividus)
        
        self.grille.RecalculerToutesPrestations()



    def Modifier_forfait(self, IDprestation=None, montant_initial=0.0, montant=0.0):
        """ Tentative de MAJ de la prestation pour l'intégration des aides journalières dans les forfaits-crédits """
        self.grille.dictPrestations[IDprestation]["montant_initial"] = montant
        self.grille.dictPrestations[IDprestation]["montant"] = montant
        self.grille.listePrestationsModifiees.append(IDprestation)

        IDindividu = self.grille.dictPrestations[IDprestation]["IDindividu"]
        datePrestation = self.grille.dictPrestations[IDprestation]["date"]
        IDindividu = self.grille.dictPrestations[IDprestation]["IDindividu"]
        label = self.grille.dictPrestations[IDprestation]["label"]

        # Affichage de la prestation
        if IDindividu == None:
            IDindividu = 0
        try:
            self.grille.GetGrandParent().panel_facturation.ModifiePrestation(datePrestation, IDindividu, IDprestation,
                                                                             self.grille.dictPrestations[IDprestation]["montantVentilation"], nouveauMontant=montant,
                                                                             nouveauLabel=label)
        except:
            pass



class CTRL(wx.Panel):
    def __init__(self, parent, grille=None, listePrestations=[]):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)     
        
        self.ctrl_forfaits = CTRL_Forfait(self, grille=grille, listePrestations=listePrestations)

        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir un forfait crédit")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier le forfait sélectionné dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer le forfait sélectionné dans la liste")))
        
        # Binds
        self.Bind(wx.EVT_BUTTON, self.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.Supprimer, self.bouton_supprimer)
        
        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_messages = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)
        grid_sizer_messages.Add(self.ctrl_forfaits, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.BOTTOM, 0)
        grid_sizer_boutons.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_messages.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 5)
        grid_sizer_messages.AddGrowableRow(0)
        grid_sizer_messages.AddGrowableCol(0)
        self.SetSizer(grid_sizer_messages)
        self.Layout()
    
    def Ajouter(self, event=None, date_debut=None, IDfamille=None):
        self.ctrl_forfaits.Ajouter(date_debut=date_debut, IDfamille=IDfamille)

    def Modifier(self, event=None):
        self.ctrl_forfaits.Modifier()

    def Supprimer(self, event=None):
        self.ctrl_forfaits.Supprimer()
    
    def MAJ(self, dictForfaits={}, listeSelectionIndividus=[]):
        self.ctrl_forfaits.MAJ(dictForfaits=dictForfaits, listeSelectionIndividus=listeSelectionIndividus)

# -------------------------------------------------------------------------------------------------------------------------------------------

##class MyFrame(wx.Frame):
##    def __init__(self, *args, **kwds):
##        wx.Frame.__init__(self, *args, **kwds)
##        panel = wx.Panel(self, -1, name="test1")
##        sizer_1 = wx.BoxSizer(wx.VERTICAL)
##        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
##        self.SetSizer(sizer_1)
##        self.myOlv = CTRL(panel)
##        self.myOlv.MAJ() 
##        sizer_2 = wx.BoxSizer(wx.VERTICAL)
##        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
##        panel.SetSizer(sizer_2)
##        self.Layout()
##
##if __name__ == '__main__':
##    app = wx.App(0)
##    #wx.InitAllImageHandlers()
##    frame_1 = MyFrame(None, -1, "OL TEST")
##    app.SetTopWindow(frame_1)
##    frame_1.Show()
##    app.MainLoop()


if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    from Dlg import DLG_Grille
    frame_1 = DLG_Grille.Dialog(None, IDfamille=14, selectionIndividus=[46,])
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
