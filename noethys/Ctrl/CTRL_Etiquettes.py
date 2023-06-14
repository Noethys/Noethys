#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Utils import UTILS_Texte


import wx.lib.agw.customtreectrl as CT


class CTRL(CT.CustomTreeCtrl):
    def __init__(self, parent, listeActivites=[], nomActivite=None, activeMenu=True, onCheck=None):
        CT.CustomTreeCtrl.__init__(self, parent, -1, style=wx.BORDER_THEME)
        self.parent = parent
        self.activation = True
        self.onCheck = onCheck
        self.listeActivites = listeActivites
        self.nomActivite = nomActivite
        self.dictItems = {}
        self.dictItemsActivites = {}
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT )
##        self.EnableSelectionVista(True)
        
        # Importation des activit�s
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        self.listeActivitesTemp = []
        for IDactivite, nom in listeDonnees :
            if not nom:
                nom = ""
            self.listeActivitesTemp.append((nom, IDactivite)) 
        self.listeActivitesTemp.sort() 
        DB.Close() 
    
        # Binds
        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.OnCheck)
        
        if activeMenu == True :
            self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)

    def Activation(self, etat=True):
        """ Active ou d�sactive le contr�le """
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
        
    def FormateCouleur(self, texte=None):
        if texte == None :
            return None
        pos1 = texte.index(",")
        pos2 = texte.index(",", pos1+1)
        r = int(texte[1:pos1])
        v = int(texte[pos1+2:pos2])
        b = int(texte[pos2+2:-1])
        return (r, v, b)

    def CreationImage(self, tailleImages, couleur=(255, 255, 255)):
        """ Cr�ation des images pour le TreeCtrl """
        if couleur == None :
            return None
        
##        r, v, b = couleur
##        bmp = wx.EmptyImage(tailleImages[0], tailleImages[1], True)
##        bmp.SetRGBRect((0, 0, 16, 16), 255, 255, 255)
##        bmp.SetRGBRect((6, 4, 8, 8), r, v, b)
##        return bmp.ConvertToBitmap()
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(tailleImages[0], tailleImages[1])
        else :
            bmp = wx.EmptyBitmap(tailleImages[0], tailleImages[1])
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(dc)
        gc.PushState() 
        gc.SetBrush(wx.Brush(couleur, wx.SOLID))
##        gc.DrawRectangle(0, 0, tailleImages[0], tailleImages[1])
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.SetPen(wx.Pen((0, 0, 0), 1, wx.SOLID))
        gc.DrawEllipse(0, 3, 10, 10)
        gc.PopState() 
        del dc
        return bmp


    def Remplissage(self):
        """ Remplissage """
        self.dictItems = {}
        self.dictItemsActivites = {}
        
        # Importation
        self.listeEtiquettes = self.Importation()
        
        # Imagelist
        tailleImages = (11,16)
        self.il = wx.ImageList(tailleImages[0], tailleImages[1])
        if 'phoenix' in wx.PlatformInfo:
            self.imgRoot = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, tailleImages))
        else :
            self.imgRoot = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, tailleImages))

        self.dictImages = {}
        for dictEtiquette in self.listeEtiquettes :
            couleur = dictEtiquette["couleurRVB"]
            IDetiquette = dictEtiquette["IDetiquette"]
            if couleur != None and couleur != (255, 255, 255) :
                self.dictImages[IDetiquette] = self.il.Add(self.CreationImage(tailleImages, couleur))

        self.SetImageList(self.il)
        
        # Cr�ation de la racine
        self.root = self.AddRoot(_(u"Etiquettes"))
        
        # Cr�ation des branches activit�s
        for nomActivite, IDactivite in self.listeActivitesTemp :
            if IDactivite in self.listeActivites :
                if nomActivite == None : 
                    nomActivite = u"Activit�"
                if self.nomActivite != None :
                    nomActivite = self.nomActivite
                item = self.AppendItem(self.root, nomActivite)
                self.dictItemsActivites[IDactivite] = item
                self.SetItemBold(item)
                self.SetPyData(item, {"type" : "activite", "IDetiquette" : None, "IDactivite" : IDactivite})
                self.SetItemImage(self.root, self.imgRoot, wx.TreeItemIcon_Normal)
            
                # Cr�ation des branches �tiquettes
                self.Boucle(None, item, IDactivite)
        
                self.Expand(item)

        if self.activation == False :
            self.EnableChildren(self.root, False)

    def Boucle(self, IDparent, itemParent, IDactivite):
        """ Boucle de remplissage du TreeCtrl """
        for dictEtiquette in self.listeEtiquettes :
            IDetiquette = dictEtiquette["IDetiquette"]
            
            if dictEtiquette["parent"] == IDparent and IDactivite == dictEtiquette["IDactivite"]:
                
                # Cr�ation de la branche
                if dictEtiquette["active"] == 0:
                    item = self.AppendItem(itemParent, dictEtiquette["label"])
                else :
                    item = self.AppendItem(itemParent, dictEtiquette["label"], ct_type=1)
                dictEtiquette["type"] = "etiquette"
                self.SetPyData(item, dictEtiquette)
                self.dictItems[IDetiquette] = item
                if IDetiquette in self.dictImages :
                    self.SetItemImage(item, self.dictImages[IDetiquette], wx.TreeItemIcon_Normal)

                # Recherche des branches enfants
                self.Boucle(IDetiquette, item, IDactivite)
                self.Expand(item)

    def MAJ(self):
        self.Freeze()
        listeCoches = self.GetCoches()
        self.DeleteAllItems()
        self.Remplissage()
        self.SetCoches(listeCoches)
        self.Thaw()

    def Importation(self):
        """ Importation de la liste des �tiquettes """
        if len(self.listeActivites) == 0 :
            conditionActivites = "()"
        elif len(self.listeActivites) == 1 :
            if self.listeActivites == [None,] :
                conditionActivites = "()"
            else :
                conditionActivites = "(%d)" % self.listeActivites[0]
        else :
            conditionActivites = str(tuple(self.listeActivites))
        
        DB = GestionDB.DB()
        req = """SELECT IDetiquette, label, IDactivite, parent, ordre, couleur, active
        FROM etiquettes
        WHERE etiquettes.IDactivite IN %s
        ORDER BY IDactivite, parent, ordre;""" % conditionActivites
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeEtiquettes = []
        for IDetiquette, label, IDactivite, parent, ordre, couleur, active in listeDonnees :     
            couleurRVB = self.FormateCouleur(couleur)       
            
            # M�morisation de l'�tiquette
            dictTemp = {
                "IDetiquette" : IDetiquette, "label" : label, "IDactivite" : IDactivite, "parent" : parent, 
                "ordre" : ordre, "couleur" : couleur, "couleurRVB" : couleurRVB, "active" : active,
                }
            listeEtiquettes.append(dictTemp)
        
        return listeEtiquettes

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """

        # Recherche et s�lection de l'item point� avec la souris
        item = self.FindTreeItem(event.GetPosition())
        if item == None:
            return
        self.SelectItem(item, True)
        dictData = self.GetPyData(item)
        
        # Cr�ation du menu contextuel
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

        menuPop.AppendSeparator()

        # Item Deplacer vers le haut
        itemx = wx.MenuItem(menuPop, 40, _(u"D�placer vers le haut"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_haut.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)
        if dictData["type"] != "etiquette" : itemx.Enable(False)

        # Item D�placer vers le bas
        itemx = wx.MenuItem(menuPop, 50, _(u"D�placer vers le bas"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Fleche_bas.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        if dictData["type"] != "etiquette" : itemx.Enable(False)
        
        menuPop.AppendSeparator()
        
        # Item Range par ordre alphab�tique
        itemx = wx.MenuItem(menuPop, 60, _(u"Trier par ordre alphab�tique"))
        itemx.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Tri_za.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(itemx)
        self.Bind(wx.EVT_MENU, self.TrierOrdreAlpha, id=60)
        if dictData["type"] != "etiquette" : itemx.Enable(False)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def FindTreeItem(self, position):
        """ Permet de retrouver l'item point� dans le TreeCtrl """
        item, flags = self.HitTest(position)
        if item and flags & (wx.TREE_HITTEST_ONITEMLABEL |
                             wx.TREE_HITTEST_ONITEMICON):
            return item
        return None
    
    def Ajouter(self, event):
        """ Ajouter une �tiquette """
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
            
            # Sauvegarde de l'�tiquette
            self.SauvegarderEtiquette(IDetiquette=None, label=label, IDactivite=IDactivite, parent=IDparent, couleur=couleur, ordre=ordre, active=active)
        dlg.Destroy()
            
    def Modifier(self, event):
        """ Modifier une �tiquette """
        item = self.GetSelection()
        dictData = self.GetPyData(item)
        if dictData == None or ("label" in dictData) == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner une �tiquette � modifier !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
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
                dlg2 = wx.MessageDialog(self, _(u"Vous ne pouvez pas s�lectionner une �tiquette parente qui est l'�tiquette � modifier !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
    
    def SauvegarderEtiquette(self, IDetiquette=None, label="", IDactivite=None, parent=None, couleur=None, ordre=None, active=1):
        DB = GestionDB.DB()
        listeDonnees = [    
            ("label", label),
            ("IDactivite", IDactivite),
            ("parent", parent),
            ("couleur", couleur),
            ("ordre", ordre),
            ("active", int(active)),
            ]
        if IDetiquette == None :
            IDetiquette = DB.ReqInsert("etiquettes", listeDonnees)
        else :
            DB.ReqMAJ("etiquettes", listeDonnees, "IDetiquette", IDetiquette)
        DB.Close()
        self.MAJ()
        self.SetID(IDetiquette)
    
    def GetItemsEnfants(self, liste=[], item=None, recursif=True):
        itemTemp, cookie = self.GetFirstChild(item)
        for index in range(0, self.GetChildrenCount(item, recursively=False)) :
            dictDataTemp = self.GetPyData(itemTemp)
            liste.append(dictDataTemp)
            if recursif == True and self.GetChildrenCount(itemTemp, recursively=False) > 0 :
                self.GetItemsEnfants(liste, itemTemp, recursif)
            itemTemp, cookie = self.GetNextChild(item, cookie)
    
    def RechercheNbreConsoAssociees(self):
        """ Recherche si les IDetiquette donn�es sont d�j� associ�es � des consommations """
        DB = GestionDB.DB()
        req = """SELECT IDconso, etiquettes
        FROM consommations
        WHERE etiquettes IS NOT NULL or etiquettes='';"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictResultats = {}
        for IDconso, etiquettes in listeDonnees :
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
            for IDetiquette in etiquettes :
                if (IDetiquette in dictResultats) == False :
                    dictResultats[IDetiquette] = 0
                dictResultats[IDetiquette] += 1
        return dictResultats

    def Supprimer(self, event):
        item = self.GetSelection()
        dictData = self.GetPyData(item)
        if dictData == None or dictData["IDetiquette"] == None:
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement s�lectionner une �tiquette � supprimer !"), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        IDetiquette = dictData["IDetiquette"]
        
        dictConsoAssociees = self.RechercheNbreConsoAssociees() 
        if IDetiquette in dictConsoAssociees :
            if dictConsoAssociees[IDetiquette] > 0 :
                dlg = wx.MessageDialog(self, _(u"Cette �tiquette a d�j� �t� associ�e � %d consommation(s) !\n\nVous ne pouvez donc pas la supprimer." % dictConsoAssociees[IDetiquette]), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
        
        # Confirmation de suppression des �tiquettes enfants
        listeTousEnfants = []
        if self.GetChildrenCount(item, recursively=True) > 0 :

            # R�cup�re la liste des tous les items enfants (r�cursif)
            self.GetItemsEnfants(listeTousEnfants, item)
            
            # Va servir � v�rifier les liens avec les autres tables :
            for dictDataTemp in listeTousEnfants :
                if dictDataTemp["IDetiquette"] in dictConsoAssociees :
                    if dictConsoAssociees[dictDataTemp["IDetiquette"]] > 0 :
                        dlg = wx.MessageDialog(self, _(u"L'�tiquette enfant '%s' qui d�pend de l'�tiquette s�lectionn�e a d�j� �t� associ�e � %d consommation(s) !\n\nVous ne pouvez donc pas supprimer l'�tiquette parent." % (dictDataTemp["label"], dictDataTemp["IDetiquette"])), "Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
                        dlg.ShowModal()
                        dlg.Destroy()
                        return
            
            # Demande de confirmation
            dlg = wx.MessageDialog(self, _(u"Attention, cette �tiquette comporte des �tiquettes enfants.\n\nSouhaitez-vous vraiment supprimer cette �tiquette ? Les �tiquettes enfants seront �galement supprim�es !"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return
        
        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette �tiquette ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            
            # Suppression de l'�tiquette
            DB.ReqDEL("etiquettes", "IDetiquette", dictData["IDetiquette"])

            # Suppression des �tiquettes enfants �galement
            for dictTemp in listeTousEnfants :
                DB.ReqDEL("etiquettes", "IDetiquette", dictTemp["IDetiquette"])

            # Modification de l'ordre des �tiquettes soeurs
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
        

    def Monter(self, event):
        """ D�placer vers le haut """
        self.Deplacer(-1)

    def Descendre(self, event):
        self.Deplacer(1)

    def Deplacer(self, sens=-1) :
        item = self.GetSelection()
        if item == None or self.GetPyData(item) == None :
            return
        
        # Recherche l'item � remplacer
        if sens == -1 :
            itemRemplace = self.GetPrevSibling(item)
        else :
            itemRemplace = self.GetNextSibling(item)
        if itemRemplace == None or itemRemplace.IsOk() == False :
            return
        
        dictData = self.GetPyData(item)
        dictDataRemplace = self.GetPyData(itemRemplace)
        
        DB = GestionDB.DB()
        DB.ReqMAJ("etiquettes", [("ordre", dictData["ordre"] + sens),], "IDetiquette", dictData["IDetiquette"])
        DB.ReqMAJ("etiquettes", [("ordre", dictData["ordre"]),], "IDetiquette", dictDataRemplace["IDetiquette"])
        DB.Commit()
        DB.Close()
        
        # MAJ du contr�le
        self.MAJ() 
        self.SetID(dictData["IDetiquette"])
    
    def TrierOrdreAlpha(self, event=None):
        """ Range les branches enfants par ordre alphab�tique """
        item = self.GetSelection()
        if item == None or self.GetPyData(item) == None :
            return

        listeItems = []
        itemParent = self.GetItemParent(item)
        self.GetItemsEnfants(liste=listeItems, item=itemParent, recursif=False)
        
        # Tri alpha
        listeTemp = []
        for dictData in listeItems :
            listeTemp.append((dictData["label"], dictData))
        listeTemp.sort() 

        DB = GestionDB.DB()
        ordre = 1
        for label, dictData in listeTemp :
            DB.ReqMAJ("etiquettes", [("ordre", ordre),], "IDetiquette", dictData["IDetiquette"])
            ordre += 1
        DB.Close() 
        
        self.MAJ()
        
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
        if item == None:
            return 0
        nbre = self.GetChildrenCount(item, recursively=False)
        return nbre

    def GetCoches(self, IDactivite=None):
        """ Obtient la liste des �tiquettes coch�es """
        listeCoches = []
        for IDetiquette, item in self.dictItems.items() :
            if self.IsItemChecked(item) == True :
                dictData = self.GetPyData(item)
                if dictData["IDactivite"] == IDactivite or IDactivite == None :
                    listeCoches.append(dictData["IDetiquette"])
        listeCoches.sort() 
        return listeCoches
    
    def SetCoches(self, listeCoches=[], tout=False, rien=False):
        for IDetiquette, item in self.dictItems.items() :
            if IDetiquette in listeCoches or tout == True :
                item.Check(True)
            if rien == True :
                item.Check(False)
        self.Refresh()

    def CocheListeTout(self):
        self.SetCoches(tout=True)

    def CocheListeRien(self):
        self.SetCoches(rien=True)

    def GetDictEtiquettes(self):
        dictEtiquettes = {}
        for dictEtiquette in self.listeEtiquettes :
            IDetiquette = dictEtiquette["IDetiquette"]
            dictEtiquettes[IDetiquette] = dictEtiquette
        return dictEtiquettes
    
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class DialogSelection(wx.Dialog):
    def __init__(self, parent, listeActivites=[], nomActivite=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent      
        self.listeActivites = listeActivites
        self.SetTitle(_(u"S�lectionner des �tiquettes"))
        
        self.ctrl_etiquettes = CTRL(self, listeActivites=listeActivites, nomActivite=nomActivite, activeMenu=False)
        self.ctrl_etiquettes.MAJ() 
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((550, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        
        grid_sizer_base.Add(self.ctrl_etiquettes, 1, wx.ALL|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Etiquettes")

    def OnBoutonOk(self, event): 
        # Fermeture de la fen�tre
        self.EndModal(wx.ID_OK)

    def GetCoches(self):
        return self.ctrl_etiquettes.GetCoches() 
    
    def SetCoches(self, listeCoches=[]):
        return self.ctrl_etiquettes.SetCoches(listeCoches) 




# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, listeActivites=[1,])
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
    
    # Test Dialog de s�lection d'�tiquettes
    # frame_1 = DialogSelection(None, listeActivites=[1,])
    # app.SetTopWindow(frame_1)
    # frame_1.ShowModal()
    # app.MainLoop()
