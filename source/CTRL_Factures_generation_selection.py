#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import wx.lib.agw.hypertreelist as HTL
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED
import datetime
import time
import copy
import sys
import traceback
import wx.lib.agw.pybusyinfo as PBI

import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import DATA_Civilites as Civilites
DICT_CIVILITES = Civilites.GetDictCivilites()

import GestionDB
import FonctionsPerso
import UTILS_Impression_facture
import DLG_Apercu_facture
import UTILS_Facturation


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.dictParametres = {}
        self.dictComptes = {}
                
        # Création des colonnes
        listeColonnes = [
            ( u"Famille/Individu", 200, wx.ALIGN_LEFT),
            ( u"Total période", 80, wx.ALIGN_RIGHT),
            ( u"Déjà réglé", 80, wx.ALIGN_RIGHT),
            ( u"Dû période", 80, wx.ALIGN_RIGHT),
            ( u"Report", 80, wx.ALIGN_RIGHT),
            ( u"Dû total", 80, wx.ALIGN_RIGHT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
##        # Création de l'ImageList
##        il = wx.ImageList(16, 16)
##        self.img_ok = il.Add(wx.Bitmap('Images/16x16/Ok.png', wx.BITMAP_TYPE_PNG))
##        self.img_pasok = il.Add(wx.Bitmap('Images/16x16/Interdit.png', wx.BITMAP_TYPE_PNG))
##        self.AssignImageList(il)
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_COLUMN_LINES | wx.TR_HAS_BUTTONS |wx.TR_HIDE_ROOT  | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT | HTL.TR_AUTO_CHECK_CHILD | HTL.TR_AUTO_CHECK_PARENT) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)

        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu) 
        self.Bind(EVT_TREE_ITEM_CHECKED, self.OnCheckItem) 

    def SetParametres(self, dictParametres={}):
        self.dictParametres = dictParametres
        self.MAJ() 

    def AfficheNbreComptes(self, nbreComptes=0):
        if self.parent.GetName() == "DLG_Factures_generation_selection" :
            if nbreComptes == 0 : label = u"Aucune facture sélectionnée"
            elif nbreComptes == 1 : label = u"1 facture sélectionnée"
            else: label = u"%d factures sélectionnées" % nbreComptes
            self.parent.box_factures_staticbox.SetLabel(label)
        
    def OnCheckItem(self, event):
        if self.MAJenCours == False :
            item = event.GetItem()
            if self.GetPyData(item)["type"] == "individu" :
                # Récupère les données sur le compte payeur
                itemParent = self.GetItemParent(item)
                IDcompte_payeur = self.GetPyData(itemParent)["valeur"]
                compte_total = self.dictComptes[IDcompte_payeur]["total"]
                compte_ventilation = self.dictComptes[IDcompte_payeur]["ventilation"]
                compte_reports = self.dictComptes[IDcompte_payeur]["total_reports"]
                # Récupère les données sur l'individu
                IDindividu = self.GetPyData(item)["valeur"]
                individu_total = self.dictComptes[IDcompte_payeur]["individus"][IDindividu]["total"]
                individu_ventilation = self.dictComptes[IDcompte_payeur]["individus"][IDindividu]["ventilation"]
                individu_reports = self.dictComptes[IDcompte_payeur]["individus"][IDindividu]["total_reports"]
                
            self.AfficheNbreComptes(len(self.GetCoches()))
                
    def CocheTout(self):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            self.CheckItem(item, True)
        self.MAJenCours = False
        self.AfficheNbreComptes(len(self.GetCoches()))

    def DecocheTout(self):
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            self.CheckItem(item, False)
        self.MAJenCours = False
        self.AfficheNbreComptes(len(self.GetCoches()))
    
    def SelectImpayes(self):
        """ Sélectionne uniquement les familles avec un compte débiteur """
        self.MAJenCours = True
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item) 
            if self.GetPyData(item)["type"] == "compte" :
                IDcompte_payeur = self.GetPyData(item)["valeur"]
                total = self.dictComptes[IDcompte_payeur]["total"]
                ventilation = self.dictComptes[IDcompte_payeur]["ventilation"]
                solde = total - ventilation
                if solde > 0.0 :
                    self.CheckItem(item, True)
                else:
                    self.CheckItem(item, False)
        self.MAJenCours = False
        self.AfficheNbreComptes(len(self.GetCoches()))
        
    def GetCoches(self):
        dictCoches = {}
        # Parcours des items COMPTE
        parent = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            parent = self.GetNext(parent) 
            if self.IsItemChecked(parent) :
                IDcompte_payeur = self.GetPyData(parent)["valeur"]
                # Parcours des items INDIVIDUS
                listeIDindividus = []
                item, cookie = self.GetFirstChild(parent)
                for index in range(0, self.GetChildrenCount(parent)):
                    if self.IsItemChecked(item) or 1 == 1 : # <<<<<<<<<<<< ICI j'ai désactivé la recherche des individus COCHES
                        IDindividu = self.GetPyData(item)["valeur"]
                        listeIDindividus.append(IDindividu)
                    item = self.GetNext(item) 
                if len(listeIDindividus) > 0 :
                    # Mémorisation de la famille et des individus cochés
                    dictCoches[IDcompte_payeur] = listeIDindividus
        return dictCoches

    def GetListeComptes(self):
        return self.dictComptes.keys() 
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(u"Racine")
        self.Remplissage()
        self.CocheTout() 

    def Remplissage(self):
        dlgAttente = PBI.PyBusyInfo(u"Recherche des prestations à facturer en cours...", parent=None, title=u"Veuillez patienter...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        try :
            facturation = UTILS_Facturation.Facturation()
            self.dictComptes = facturation.GetDonnees(     liste_activites=self.dictParametres["listeActivites"],
                                                                                date_debut=self.dictParametres["date_debut"], 
                                                                                date_fin=self.dictParametres["date_fin"], 
                                                                                date_edition=self.dictParametres["date_emission"],
                                                                                date_echeance=self.dictParametres["date_echeance"],
                                                                                prestations=self.dictParametres["prestations"],
                                                                                )
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, u"Désolé, le problème suivant a été rencontré dans la recherche de factures : \n\n%s" % err, u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Condition famille unique
        if self.dictParametres["IDcompte_payeur"] != None :
            IDcompte_payeur = self.dictParametres["IDcompte_payeur"]
            if self.dictComptes.has_key(IDcompte_payeur) :
                self.dictComptes = { IDcompte_payeur : self.dictComptes[IDcompte_payeur],}
            else :
                self.dictComptes = {}
            
        # Branches COMPTE
        listeNomsSansCivilite = []
        for IDcompte_payeur, dictCompte in self.dictComptes.iteritems() :
            listeNomsSansCivilite.append((dictCompte["nomSansCivilite"], IDcompte_payeur))
        listeNomsSansCivilite.sort() 
        
        for nomSansCivilite, IDcompte_payeur in listeNomsSansCivilite :
            dictCompte = self.dictComptes[IDcompte_payeur]
            IDfamille = dictCompte["IDfamille"]
            total = dictCompte["total"]
            ventilation = dictCompte["ventilation"]
            total_reports = dictCompte["total_reports"]
                        
            niveauCompte = self.AppendItem(self.root, nomSansCivilite, ct_type=1)
            self.SetPyData(niveauCompte, {"type" : "compte", "valeur" : IDcompte_payeur, "IDfamille" : IDfamille, "nom" : nomSansCivilite})

            self.SetItemText(niveauCompte, u"%.02f %s" % (total, SYMBOLE), 1)
            self.SetItemText(niveauCompte, u"%.02f %s" % (ventilation, SYMBOLE), 2)
            self.SetItemText(niveauCompte, u"%.02f %s" % (total-ventilation, SYMBOLE), 3)
            if total_reports > 0.0 :
                self.SetItemText(niveauCompte, u"%.02f %s" % (total_reports, SYMBOLE), 4)
                self.SetItemText(niveauCompte, u"%.02f %s" % (total-ventilation+total_reports, SYMBOLE), 5)
            
            # Branches INDIVIDUS
            listeIndividus = []
            for IDindividu, dictIndividu in dictCompte["individus"].iteritems() :
                nomIndividu = dictIndividu["nom"]
                listeIndividus.append((nomIndividu, IDindividu))
            listeIndividus.sort() 
            
            for nomIndividu, IDindividu in listeIndividus :
                dictIndividu = dictCompte["individus"][IDindividu]
                total = dictIndividu["total"]
                ventilation = dictIndividu["ventilation"]
                total_reports = dictIndividu["total_reports"]
                            
                niveauIndividu = self.AppendItem(niveauCompte, nomIndividu)#, ct_type=1)
                self.SetPyData(niveauIndividu, {"type" : "individu", "valeur" : IDindividu, "dictIndividu" : dictIndividu})
                
                self.SetItemText(niveauIndividu, u"%.02f %s" % (total, SYMBOLE), 1)
                self.SetItemText(niveauIndividu, u"%.02f %s" % (ventilation, SYMBOLE), 2)
                self.SetItemText(niveauIndividu, u"%.02f %s" % (total-ventilation, SYMBOLE), 3)
                if total_reports > 0.0 :
                    self.SetItemText(niveauIndividu, u"%.02f %s" % (total_reports, SYMBOLE), 4)
                    self.SetItemText(niveauIndividu, u"%.02f %s" % (total-ventilation+total_reports, SYMBOLE), 5)
                
                
        
        #self.ExpandAllChildren(self.root)
    
    def OnCompareItems(self, item1, item2):
        if self.GetPyData(item1) > self.GetPyData(item2) :
            return 1
        elif self.GetPyData(item1) < self.GetPyData(item2) :
            return -1
        else:
            return 0
        
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        if type != "compte" : return
        nomIndividu = dictItem["nom"]
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Ouvrir fiche famille
        item = wx.MenuItem(menuPop, 10, u"Afficher un aperçu PDF")
        bmp = wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.AfficherApercu, id=10)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def AfficherApercu(self, event=None):
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        if dictItem == None :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune famille dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        type = dictItem["type"]
        if type != "compte" : 
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune famille dans la liste !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        IDfamille = dictItem["IDfamille"]
        IDcompte_payeur = dictItem["IDfamille"]
        
        # Récupération des données
        dictCompte = self.dictComptes[IDcompte_payeur]

        # Récupération des paramètres d'affichage
        dlg = DLG_Apercu_facture.Dialog(self, provisoire=True)
        if dlg.ShowModal() == wx.ID_OK:
            dictOptions = dlg.GetParametres()
            dlg.Destroy()
        else :
            dlg.Destroy()
            return False
                   
        # Fabrication du PDF
        dlgAttente = PBI.PyBusyInfo(u"Création de l'aperçu au format PDF...", parent=None, title=u"Veuillez patienter...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        try :
            UTILS_Impression_facture.Impression({IDcompte_payeur : dictCompte}, dictOptions, IDmodele=dictOptions["IDmodele"])
            del dlgAttente
        except Exception, err:
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, u"Désolé, le problème suivant a été rencontré dans la création de l'aperçu de la facture : \n\n%s" % err, u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        










        

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        # Données pour les tests
        date_debut = datetime.date(2010, 10, 4)
        date_fin = datetime.date(2012, 11, 30)
        liste_activites = [1, 3]
        
        self.myOlv = CTRL(panel)

        dictParametres = {
            "date_debut" : datetime.date(2013, 2, 1),
            "date_fin" : datetime.date(2013, 3, 28),
            "date_emission" : datetime.date.today(),
            "date_echeance" : None,
            "prestations" : ["consommation", "cotisation", "autre"],
            "IDcompte_payeur" : None,
            "listeActivites" : [1, 2, 3],
            }
        self.myOlv.SetParametres(dictParametres) 
        
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
