#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Utils import UTILS_Dates
import wx.lib.agw.customtreectrl as CT


class CTRL(CT.CustomTreeCtrl):
    def __init__(self, parent, listeActivites=[], periode=None, activeCheck=False, activeMenu=True, onCheck=None):
        CT.CustomTreeCtrl.__init__(self, parent, -1, style=wx.BORDER_THEME)
        self.parent = parent
        self.activation = True
        self.activeCheck = activeCheck
        self.onCheck = onCheck
        self.listeActivites = listeActivites
        self.periode = periode
        self.dictItems = {}

        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT )
##        self.EnableSelectionVista(True)

        # Binds
        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.OnCheck)
        
        if activeMenu == True :
            self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

    def Activation(self, etat=True):
        """ Active ou désactive le contrôle """
        self.activation = etat
        self.MAJ() 
    
    def OnCheck(self, event=None):
        if self.onCheck != None :
            self.onCheck() 
        
    def SetActivites(self, listeActivites=[]):
        listeActivites.sort() 
        if self.listeActivites != listeActivites :
            self.listeActivites = listeActivites
            self.MAJ()

    def SetPeriode(self, periode=None):
        self.periode = periode
        self.MAJ()

    def SetDates(self, periode=None, listeDates=None):
        if periode != None :
            self.periode = ("periode", periode)
        elif listeDates != None :
            self.periode = ("dates", listeDates)
        else :
            self.periode = None
        self.MAJ()

    def Remplissage(self):
        """ Remplissage """
        self.dictItems = {}

        # Importation
        self.listeEvenements = self.Importation()

        # Création de la racine
        self.root = self.AddRoot(_(u"Evènements"))

        # Regroupement des données
        dictActivites = {}
        dictEvenements = {}
        for dictEvenement in self.listeEvenements :
            IDactivite = dictEvenement["IDactivite"]
            date = dictEvenement["date"]

            if (IDactivite in dictEvenements) == False :
                dictEvenements[IDactivite] = {}
                dictActivites[IDactivite] = dictEvenement["nomActivite"]

            if (date in dictEvenements[IDactivite]) == False :
                dictEvenements[IDactivite][date] = []

            dictEvenements[IDactivite][date].append(dictEvenement)

        # Tri des activités par ordre alpha
        listeActivites = [(dictActivites[IDactivite], IDactivite) for IDactivite in list(dictEvenements.keys())]
        listeActivites.sort()

        for nomActivite, IDactivite in listeActivites :
            niveauActivite = self.AppendItem(self.root, nomActivite)
            self.SetItemBold(niveauActivite)
            self.SetPyData(niveauActivite, {"type" : "activite", "IDactivite" : IDactivite})

            # Tri des dates
            listeDates = list(dictEvenements[IDactivite].keys())
            listeDates.sort()

            for date in listeDates :
                niveauDate = self.AppendItem(niveauActivite, UTILS_Dates.DateDDEnFr(date))

                for dictEvenement in dictEvenements[IDactivite][date] :
                    IDevenement = dictEvenement["IDevenement"]
                    label = dictEvenement["nom"]

                    if dictEvenement["heure_debut"] != None and dictEvenement["heure_fin"] != None :
                        label += u" (%s-%s)" % (dictEvenement["heure_debut"].replace(":", "h"), dictEvenement["heure_fin"].replace(":", "h"))

                    if self.activeCheck == True :
                        niveauEvenement = self.AppendItem(niveauDate, label, ct_type=1)
                    else:
                        niveauEvenement = self.AppendItem(niveauDate, label)
                    self.SetPyData(niveauEvenement, {"type": "evenement", "IDevenement": IDevenement})
                    self.dictItems[IDevenement] = niveauEvenement

        self.ExpandAll()

        if self.activation == False :
            self.EnableChildren(self.root, False)

    def MAJ(self):
        self.Freeze()
        listeCoches = self.GetCoches()
        self.DeleteAllItems()
        self.Remplissage()
        self.SetCoches(listeCoches)
        self.Thaw()

    def Importation(self):
        """ Importation de la liste des évènements """
        if len(self.listeActivites) == 0 : conditionActivites = "()"
        elif len(self.listeActivites) == 1 : conditionActivites = "(%d)" % self.listeActivites[0]
        else : conditionActivites = str(tuple(self.listeActivites))

        if self.periode != None :
            if self.periode[0] == "periode" :
                conditionPeriode = "AND date>='%s' AND date<='%s' " % (self.periode[1][0], self.periode[1][1])
            if self.periode[0] == "dates" :
                listeDates = [str(date) for date in self.periode[1]]
                if len(listeDates) == 0: conditionPeriode = "AND date=''"
                elif len(listeDates) == 1: conditionPeriode = "AND date='%s'" % listeDates[0]
                else: conditionPeriode = "AND date IN %s" % str(tuple(listeDates))
        else :
            conditionPeriode = ""

        DB = GestionDB.DB()
        req = """SELECT IDevenement, evenements.IDactivite, date, evenements.nom, heure_debut, heure_fin,
        activites.nom
        FROM evenements
        LEFT JOIN activites ON activites.IDactivite = evenements.IDactivite
        WHERE evenements.IDactivite IN %s %s
        ORDER BY date, heure_debut;""" % (conditionActivites, conditionPeriode)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeEvenements = []
        for IDevenement, IDactivite, date, nom, heure_debut, heure_fin, nomActivite in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)

            # Mémorisation de l'évènement
            dictTemp = {
                "IDevenement" : IDevenement, "IDactivite" : IDactivite, "date" : date, "nom" : nom,
                "heure_debut" : heure_debut, "heure_fin" : heure_fin, "nomActivite" : nomActivite,
                }
            listeEvenements.append(dictTemp)

        return listeEvenements

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """

        # Recherche et sélection de l'item pointé avec la souris
        item = self.FindTreeItem(event.GetPosition())
        if item == None:
            return
        self.SelectItem(item, True)
        dictData = self.GetPyData(item)
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        itemx = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Modifier
        itemx = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if dictData["type"] != "etiquette" : itemx.Enable(False)

        # Item Supprimer
        itemx = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if dictData["type"] != "etiquette" : itemx.Enable(False)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def FindTreeItem(self, position):
        """ Permet de retrouver l'item pointé dans le TreeCtrl """
        item, flags = self.HitTest(position)
        if item and flags & (wx.TREE_HITTEST_ONITEMLABEL |
                             wx.TREE_HITTEST_ONITEMICON):
            return item
        return None
    
    def Ajouter(self, event):
        """ Ajouter une étiquette """
        item = self.GetSelection()
        dictData = self.GetPyData(item)
        if dictData != None :
            parent = dictData["IDetiquette"]
            IDactivite = dictData["IDactivite"]
        else :
            parent = None
            IDactivite = None
            
        from Dlg import DLG_Saisie_etiquette
        dlg = DLG_Saisie_etiquette.Dialog(self, listeActivites=self.listeActivites, nomActivite=self.nomActivite)
        if parent == None and IDactivite == None :
            dlg.ctrl_parent.SelectPremierItem() 
        else :
            dlg.SetIDparent(parent, IDactivite)
        if dlg.ShowModal() == wx.ID_OK :
            label = dlg.GetLabel()
            couleur = dlg.GetCouleur()
            IDparent, IDactivite = dlg.GetIDparent()
            ordre = self.GetNbreEnfants(self.GetItem(IDparent, IDactivite)) + 1
            dictOptions = dlg.GetOptions()
            active = dictOptions["active"]
            
            # Sauvegarde de l'étiquette
            self.SauvegarderEtiquette(IDetiquette=None, label=label, IDactivite=IDactivite, parent=IDparent, couleur=couleur, ordre=ordre, active=active)
        dlg.Destroy()
            
    def Modifier(self, event):
        """ Modifier une étiquette """
        item = self.GetSelection()
        dictData = self.GetPyData(item)
        if dictData == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une étiquette à modifier !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        from Dlg import DLG_Saisie_etiquette
        dlg = DLG_Saisie_etiquette.Dialog(self, listeActivites=self.listeActivites, nomActivite=self.nomActivite)
        dlg.SetLabel(dictData["label"])
        dlg.SetCouleur(dictData["couleur"])
        dlg.SetIDparent(dictData["parent"], dictData["IDactivite"])
        dictOptions = {"active" : dictData["active"],}
        dlg.SetOptions(dictOptions)
        if dlg.ShowModal() == wx.ID_OK :
            label = dlg.GetLabel()
            couleur = dlg.GetCouleur()
            IDparent, IDactivite = dlg.GetIDparent()
            dictOptions = dlg.GetOptions()
            active = dictOptions["active"]

            if dictData["IDetiquette"] == IDparent :
                dlg2 = wx.MessageDialog(self, _(u"Vous ne pouvez pas sélectionner une étiquette parente qui est l'étiquette à modifier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                dlg.Destroy()
                return

            if IDparent == dictData["parent"] :
                ordre = dictData["ordre"]
            else :
                ordre = self.GetNbreEnfants(self.GetItem(IDparent)) + 1

            self.SauvegarderEtiquette(IDetiquette=dictData["IDetiquette"], label=label, IDactivite=IDactivite, parent=IDparent, couleur=couleur, ordre=ordre, active=active)
            
        dlg.Destroy()

    def GetItemsEnfants(self, liste=[], item=None, recursif=True):
        itemTemp, cookie = self.GetFirstChild(item)
        for index in range(0, self.GetChildrenCount(item, recursively=False)) :
            dictDataTemp = self.GetPyData(itemTemp)
            liste.append(dictDataTemp)
            if recursif == True and self.GetChildrenCount(itemTemp, recursively=False) > 0 :
                self.GetItemsEnfants(liste, itemTemp, recursif)
            itemTemp, cookie = self.GetNextChild(item, cookie)

    def Supprimer(self, event):
        item = self.GetSelection()
        dictData = self.GetPyData(item)
        if dictData == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une étiquette à supprimer !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        IDetiquette = dictData["IDetiquette"]
        
        dictConsoAssociees = self.RechercheNbreConsoAssociees() 
        if IDetiquette in dictConsoAssociees :
            if dictConsoAssociees[IDetiquette] > 0 :
                dlg = wx.MessageDialog(self, _(u"Cette étiquette a déjà été associée à %d consommation(s) !\n\nVous ne pouvez donc pas la supprimer." % dictConsoAssociees[IDetiquette]), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Confirmation de suppression des étiquettes enfants
        listeTousEnfants = []
        if self.GetChildrenCount(item, recursively=True) > 0 :

            # Récupère la liste des tous les items enfants (récursif)
            self.GetItemsEnfants(listeTousEnfants, item)
            
            # Va servir à vérifier les liens avec les autres tables :
            for dictDataTemp in listeTousEnfants :
                if dictDataTemp["IDetiquette"] in dictConsoAssociees :
                    if dictConsoAssociees[dictDataTemp["IDetiquette"]] > 0 :
                        dlg = wx.MessageDialog(self, _(u"L'étiquette enfant '%s' qui dépend de l'étiquette sélectionnée a déjà été associée à %d consommation(s) !\n\nVous ne pouvez donc pas supprimer l'étiquette parent." % (dictDataTemp["label"], dictDataTemp["IDetiquette"])), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return
            
            # Demande de confirmation
            dlg = wx.MessageDialog(self, _(u"Attention, cette étiquette comporte des étiquettes enfants.\n\nSouhaitez-vous vraiment supprimer cette étiquette ? Les étiquettes enfants seront également supprimées !"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette étiquette ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            
            # Suppression de l'étiquette
            DB.ReqDEL("etiquettes", "IDetiquette", dictData["IDetiquette"])

            # Suppression des étiquettes enfants également
            for dictTemp in listeTousEnfants :
                DB.ReqDEL("etiquettes", "IDetiquette", dictTemp["IDetiquette"])

            # Modification de l'ordre des étiquettes soeurs
            itemParent = self.GetItemParent(item)
            listeItemsSoeurs = []
            self.GetItemsEnfants(liste=listeItemsSoeurs, item=itemParent, recursif=False)
            ordre = 1
            for dictDataTemp in listeItemsSoeurs :
                if dictDataTemp["IDetiquette"] != dictData["IDetiquette"] :
                    DB.ReqMAJ("etiquettes", [("ordre", ordre),], "IDetiquette", dictDataTemp["IDetiquette"])
                    ordre += 1
                                                
            DB.Close() 
            self.MAJ()
            
        dlg.Destroy()
        


    def SetID(self, IDetiquette=None, IDactivite=None):
        item = None
        if IDetiquette in self.dictItems :
            item = self.dictItems[IDetiquette]
        else :
            if IDactivite in self.dictItemsActivites :
                item = self.dictItemsActivites[IDactivite]
        if item != None :
            self.EnsureVisible(item)
            self.SelectItem(item)
    
    def SelectPremierItem(self):
        item, cookie = self.GetFirstChild(self.root)
        self.SelectItem(item)
            
    def GetID(self):
        item = self.GetSelection()
        if item == None or item == self.root or item.IsOk() == False :
            return None, None
        dictData = self.GetPyData(item)
        return dictData["IDetiquette"], dictData["IDactivite"]
    
    def GetItem(self, IDetiquette=None, IDactivite=None):
        if IDetiquette in self.dictItems :
            return self.dictItems[IDetiquette]
        else :
            item, cookie = self.GetFirstChild(self.root)
            for index in range(0, self.GetChildrenCount(self.root, recursively=False)) :
                dictData = self.GetPyData(item)
                if dictData["IDetiquette"] == IDetiquette and dictData["IDactivite"] == IDactivite :
                    return item
                item, cookie = self.GetNextChild(item, cookie)
        return None
        
    def GetNbreEnfants(self, item):
        nbre = self.GetChildrenCount(item, recursively=False)
        return nbre

    def GetCoches(self):
        """ Obtient la liste des étiquettes cochées """
        listeCoches = []
        for IDevenement, item in self.dictItems.items() :
            if self.IsItemChecked(item) == True :
                listeCoches.append(IDevenement)
        listeCoches.sort() 
        return listeCoches
    
    def SetCoches(self, listeCoches=[], tout=False, rien=False):
        for IDevenement, item in self.dictItems.items() :
            if IDevenement in listeCoches or tout == True :
                item.Check(True)
            if rien == True :
                item.Check(False)
        self.Refresh()

    def CocheListeTout(self):
        self.SetCoches(tout=True)

    def CocheListeRien(self):
        self.SetCoches(rien=True)

    def GetDictEvenements(self):
        dictEvenements = {}
        for dictEvenement in self.listeEvenements :
            IDevenement = dictEvenement["IDevenement"]
            dictEvenements[IDevenement] = dictEvenement
        return dictEvenements


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, listeActivites=[1,], activeCheck=True)
        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
    
    # Test Dialog de sélection d'étiquettes
    # frame_1 = DialogSelection(None, listeActivites=[1,])
    # app.SetTopWindow(frame_1)
    # frame_1.ShowModal()
    # app.MainLoop()
