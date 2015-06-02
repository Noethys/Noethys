#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import wx.lib.agw.hyperlink as Hyperlink
import datetime
from CTRL_Tarification_calcul import LISTE_METHODES
import GestionDB

try: import psyco; psyco.full()
except: pass

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", ID=None, size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.ID = ID
        self.URL = URL
        
        # Construit l'hyperlink
        self.SetFont(wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        self.SetBackgroundColour((255, 255, 255))
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        if self.URL == "nouvelleCategorie" :
            self.GetGrandParent().AjouterCategorie()
        elif self.URL == "nouveauNom" :
            self.GetGrandParent().AjouterNom(self.ID)
        elif self.URL == "nouveauTarif" :
            self.GetGrandParent().AjouterTarif(self.ID)
        else:
            pass
        self.UpdateLink()

# -----------------------------------------------------------------------------------------------------------------
    
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style= wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT,
                 IDactivite=None,
                 ):
        HTL.HyperTreeList.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.IDactivite = IDactivite
        
        self.SetBackgroundColour(wx.WHITE)

        # Adapte taille Police pour Linux
        import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.img_categorie = il.Add(wx.Bitmap('Images/16x16/Dossier.png', wx.BITMAP_TYPE_PNG))
        self.img_categorie_gris = il.Add(wx.Bitmap('Images/16x16/Dossier_gris.png', wx.BITMAP_TYPE_PNG))
        self.img_nom = il.Add(wx.Bitmap('Images/16x16/Etiquette.png', wx.BITMAP_TYPE_PNG))
        self.img_nom_gris = il.Add(wx.Bitmap('Images/16x16/Etiquette_gris.png', wx.BITMAP_TYPE_PNG))
        self.img_tarif = il.Add(wx.Bitmap('Images/16x16/Euro.png', wx.BITMAP_TYPE_PNG))
        self.img_tarif_gris = il.Add(wx.Bitmap('Images/16x16/Euro_gris.png', wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Creation des colonnes
        self.AddColumn(_(u"Prestations / Tarifs"))
        self.SetColumnWidth(0, 250)
        self.AddColumn(_(u"Nom du tarif"))
        self.SetColumnWidth(1, 230)
        self.AddColumn(_(u"Catégories de tarifs"))
        self.SetColumnWidth(2, 180)
        self.AddColumn(_(u"Méthode de calcul"))
        self.SetColumnWidth(3, 230)
        self.SetMainColumn(0)
                                
        # Création des branches
        self.root = self.AddRoot(_(u"Tarifs"))
        self.SetPyData(self.root, {"type" : "root", "ID" : None} )
        self.SetAGWWindowStyleFlag(wx.TR_COLUMN_LINES)
        
        # Binds
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
                        
    def MAJ(self, selection=None):
        """ Met à jour (redessine) tout le contrôle """
        nbreBranches = 1#self.GetMainWindow().GetCount()
        if nbreBranches > 0 :
            self.DeleteChildren(self.root)
        self.CreationBranches()
        # Sélection
        if selection != None :
            typeBranche, ID = selection
            branche = self.dictBranches[typeBranche][ID]
            self.SelectItem(branche)
    
    def CreationBranches(self):
        """ Met uniquement à jour le contenu du contrôle """
        # --- Importation des données ---
        DB = GestionDB.DB()
        
        # Importation des catégories de tarifs
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs 
        WHERE IDactivite=%d
        ORDER BY nom; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()
        dictCategories = {}
        for IDcategorie_tarif, nom in listeCategories :
            dictCategories[IDcategorie_tarif] = nom
        
        # Importation des noms de tarifs
        req = """SELECT IDnom_tarif, nom
        FROM noms_tarifs 
        WHERE IDactivite=%d
        ORDER BY nom; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeNoms = DB.ResultatReq()
        
        # Importation des tarifs
        req = """SELECT IDtarif, IDnom_tarif, date_debut, date_fin, methode, categories_tarifs, groupes, description
        FROM tarifs 
        WHERE IDactivite=%d
        ORDER BY date_debut DESC; """ % self.IDactivite
        DB.ExecuterReq(req)
        listeTarifs = DB.ResultatReq()
        
        DB.Close()
        
        dictTarifs = {}
        for IDtarif, IDnom_tarif, date_debut, date_fin, methode, categories_tarifs, groupes, description in listeTarifs :
            if dictTarifs.has_key(IDnom_tarif) == False :
                dictTarifs[IDnom_tarif] = []
            dictTemp = { "IDtarif" : IDtarif, "date_debut" : date_debut, "date_fin" : date_fin, "methode" : methode, "categories_tarifs" : categories_tarifs, "groupes" : groupes, "description" : description}
            dictTarifs[IDnom_tarif].append(dictTemp)
                    
        # --- Création des branches ---
        self.dictBranches = {"noms_tarifs" : {}, "tarifs" : {} } 
        
        # Noms de tarifs
        for IDnom_tarif, nom in listeNoms :
            brancheNom = self.AppendItem(self.root, nom)
            self.SetItemImage(brancheNom, self.img_nom, which=wx.TreeItemIcon_Normal)
            self.SetPyData(brancheNom, {"type" : "nom", "ID" : IDnom_tarif, "nom":nom} )
            self.SetItemBold(brancheNom, True)
            self.dictBranches["noms_tarifs"][IDnom_tarif] = brancheNom
            
            # Tarifs
            if dictTarifs.has_key(IDnom_tarif) :
                for dictTarifTemp in dictTarifs[IDnom_tarif] :
                    IDtarif = dictTarifTemp["IDtarif"]
                    
                    # Dates de validité
                    if dictTarifTemp["date_debut"] != None :
                        date_debut = DateEngFr(dictTarifTemp["date_debut"])
                    else:
                        date_debut = u"?"
                    label = _(u"A partir du %s") % date_debut
                    if dictTarifTemp["date_fin"] != None :
                        date_fin = DateEngFr(dictTarifTemp["date_fin"])
                        label = _(u"Du %s au %s") % (date_debut, date_fin)
                        
                    brancheTarif = self.AppendItem(brancheNom, label)
                    self.SetPyData(brancheTarif, {"type" : "tarif", "ID" : IDtarif, "IDnom_tarif":IDnom_tarif})
                    self.SetItemImage(brancheTarif, self.img_tarif, which=wx.TreeItemIcon_Normal)
                    self.dictBranches["tarifs"][IDtarif] = brancheTarif

                    # Description
                    description = dictTarifTemp["description"]
                    if description == None :
                        description = u""
                        
                    self.SetItemText(brancheTarif, description, 1)

                    # Catégories rattachées
                    categoriesTemp = dictTarifTemp["categories_tarifs"]
                    if categoriesTemp != None :
                        listeTemp = categoriesTemp.split(";")
                        listeCategories = []
                        for IDcategorie in listeTemp :
                            IDcategorie = int(IDcategorie)
                            nomCategorie = dictCategories[IDcategorie]
                            listeCategories.append(nomCategorie)
                        texteCategories = "; ".join(listeCategories)
                    else :
                        texteCategories = ""
                        
                    self.SetItemText(brancheTarif, texteCategories, 2)
                    
                    # Méthode
                    methode = dictTarifTemp["methode"]
                    labelMethode = None
                    for dictValeurs in LISTE_METHODES :
                        if dictValeurs["code"] == methode :
                            labelMethode = dictValeurs["label"]
                    if labelMethode == None :
                        labelMethode = _(u"-- Aucune --")
                        
                    self.SetItemText(brancheTarif, labelMethode, 3)

        self.ExpandAll()
    
    def OnLeftDClick(self, event):
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        type = dictItem["type"]
        ID = dictItem["ID"]    
##        if type == "categorie" : self.ModifierCategorie(ID)
        if type == "nom" : self.ModifierNom(ID)
        if type == "tarif" : self.ModifierTarif(IDtarif=ID, IDnom_tarif=dictItem["IDnom_tarif"] )
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        ID = dictItem["ID"]
        
        # Création du menu contextuel
        menuPop = wx.Menu()

##        if type == "root" :
##            # Item Ajouter
##            item = wx.MenuItem(menuPop, 10, _(u"Ajouter un catégorie de tarif"))
##            bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
##            item.SetBitmap(bmp)
##            menuPop.AppendItem(item)
##            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        if type == "root" :
            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter un nom de prestation"))
            bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
##            menuPop.AppendSeparator()
##            # Item Modifier
##            item = wx.MenuItem(menuPop, 20, _(u"Modifier la catégorie de tarif"))
##            bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
##            item.SetBitmap(bmp)
##            menuPop.AppendItem(item)
##            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
##            # Item Supprimer
##            item = wx.MenuItem(menuPop, 30, _(u"Supprimer la catégorie de tarif"))
##            bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
##            item.SetBitmap(bmp)
##            menuPop.AppendItem(item)
##            self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
##            menuPop.AppendSeparator()
##            # Item Dupliquer
##            item = wx.MenuItem(menuPop, 40, _(u"Dupliquer cette catégorie de tarif"))
##            bmp = wx.Bitmap("Images/16x16/Dupliquer.png", wx.BITMAP_TYPE_PNG)
##            item.SetBitmap(bmp)
##            menuPop.AppendItem(item)
##            self.Bind(wx.EVT_MENU, self.Dupliquer, id=40)
            
        if type == "nom" :
            # Item Ajouter
            item = wx.MenuItem(menuPop, 10, _(u"Ajouter un tarif pour cette prestation"))
            bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
            menuPop.AppendSeparator()
            # Item Modifier
            item = wx.MenuItem(menuPop, 20, _(u"Modifier le nom de la prestation"))
            bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer ce nom de prestation"))
            bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
            menuPop.AppendSeparator()
            # Item Dupliquer
            item = wx.MenuItem(menuPop, 40, _(u"Dupliquer ce nom de prestation"))
            bmp = wx.Bitmap("Images/16x16/Dupliquer.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Dupliquer, id=40)
            
        if type == "tarif" :
            # Item Modifier
            item = wx.MenuItem(menuPop, 20, _(u"Modifier ce tarif"))
            bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer ce tarif"))
            bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
            menuPop.AppendSeparator()
            # Item Dupliquer
            item = wx.MenuItem(menuPop, 40, _(u"Dupliquer ce tarif"))
            bmp = wx.Bitmap("Images/16x16/Dupliquer.png", wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Dupliquer, id=40)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
            
    def Ajouter(self, event):
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        type = dictItem["type"]
        ID = dictItem["ID"]
##        if type == "root" : self.AjouterCategorie()
        if type == "root" : self.AjouterNom()
        if type == "nom" : self.AjouterTarif(ID)
        
    def Modifier(self, event):
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        type = dictItem["type"]
        ID = dictItem["ID"]
##        if type == "categorie" : self.ModifierCategorie(ID)
        if type == "nom" : self.ModifierNom(ID)
        if type == "tarif" : self.ModifierTarif(IDtarif=ID, IDnom_tarif=dictItem["IDnom_tarif"])
        
    def Supprimer(self, event):
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        type = dictItem["type"]
        ID = dictItem["ID"]
##        if type == "categorie" : self.SupprimerCategorie(ID)
        if type == "nom" : self.SupprimerNom(ID)
        if type == "tarif" : self.SupprimerTarif(ID)

    def Dupliquer(self, event):
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        type = dictItem["type"]
        
        if type == "nom" : 
            # Dupliquer un nom
            IDnom_tarif = dictItem["ID"]
            nomTarif = dictItem["nom"]
            newIDnom_tarif = self.DupliquerNom(IDnom_tarif, nomTarif)
            self.ModifierNom(IDnom_tarif=newIDnom_tarif)
            self.MAJ(selection=("noms_tarifs", newIDnom_tarif))
            
        if type == "tarif" : 
            # Dupliquer un tarif
            IDtarif = dictItem["ID"]
            IDnom_tarif = dictItem["IDnom_tarif"]
            newIDtarif = self.DupliquerTarif(IDtarif)
            self.ModifierTarif(IDtarif=newIDtarif, IDnom_tarif=IDnom_tarif)
            self.MAJ(selection=("tarifs", newIDtarif))
            
            
##    def AjouterCategorie(self):
##        import DLG_Saisie_categorie_tarif 
##        dlg = DLG_Saisie_categorie_tarif.Dialog(self, IDactivite=self.IDactivite, IDcategorie_tarif=None)
##        if dlg.ShowModal() == wx.ID_OK:
##            IDcategorie_tarif = dlg.GetIDcategorieTarif()
##            dlg.Destroy()
##            self.MAJ()
##        else:
##            dlg.Destroy()
##
##    def ModifierCategorie(self, IDcategorie_tarif=None):
##        import DLG_Saisie_categorie_tarif
##        dlg = DLG_Saisie_categorie_tarif.Dialog(self, IDactivite=self.IDactivite, IDcategorie_tarif=IDcategorie_tarif)
##        if dlg.ShowModal() == wx.ID_OK:
##            dlg.Destroy()
##            self.MAJ()
##        else:
##            dlg.Destroy()
##
##    def SupprimerCategorie(self, IDcategorie_tarif=None):
##        DB = GestionDB.DB()
##        req = """SELECT IDcategorie_tarif FROM noms_tarifs WHERE IDcategorie_tarif=%d;""" % IDcategorie_tarif
##        DB.ExecuterReq(req)
##        listeDonnees = DB.ResultatReq()
##        DB.Close()
##        if len(listeDonnees) > 0 :
##            dlg = wx.MessageDialog(self, _(u"Il est impossible de supprimer une catégorie qui comporte au moins un tarif !"), _(u"Suppression impossible"), wx.OK | wx.ICON_INFORMATION)
##            dlg.ShowModal()
##            dlg.Destroy()
##            return
##        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette catégorie ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
##        if dlg.ShowModal() == wx.ID_YES :
##            DB = GestionDB.DB()
##            DB.ReqDEL("categories_tarifs", "IDcategorie_tarif", IDcategorie_tarif)
##            DB.ReqDEL("categories_tarifs_villes", "IDcategorie_tarif", IDcategorie_tarif)
##            DB.Close() 
##            self.MAJ()
##        dlg.Destroy()
##
##    def DupliquerCategorie(self, IDcategorie_tarif):
##        IDcategorie_tarif_modele = IDcategorie_tarif
##        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous dupliquer également les tarifs et paramétrages de cette catégorie ?"), _(u"Duplication"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
##        reponse = dlg.ShowModal() 
##        if reponse == wx.ID_YES :
##            dupliqueEnfants = True
##        elif reponse == wx.ID_NO :
##            dupliqueEnfants = False
##        else :
##            dlg.Destroy()
##            return
##        dlg.Destroy()
##        DB = GestionDB.DB()
##        
##        # Duplication de la catégorie
##        req = """SELECT IDactivite, nom FROM categories_tarifs WHERE IDcategorie_tarif=%d;""" % IDcategorie_tarif_modele
##        DB.ExecuterReq(req)
##        listeCategories = DB.ResultatReq()
##        IDactivite = listeCategories[0][0]
##        nom = listeCategories[0][1]
##        listeDonnees = [
##            ("IDactivite", IDactivite),
##            ("nom", _(u"Copie de %s") % nom),
##            ]
##        IDcategorie_tarif_nouveau = DB.ReqInsert("categories_tarifs", listeDonnees)
##        
##        # Duplication des villes associées
##        req = """SELECT cp, nom FROM categories_tarifs_villes WHERE IDcategorie_tarif=%d;""" % IDcategorie_tarif_modele
##        DB.ExecuterReq(req)
##        listeVilles = DB.ResultatReq()
##        for cp, nom in listeVilles :
##            listeDonnees = [
##                ("IDcategorie_tarif", IDcategorie_tarif_nouveau),
##                ("cp", cp),
##                ("nom", nom),
##                ]
##            IDville_nouveau = DB.ReqInsert("categories_tarifs_villes", listeDonnees)
##        
##        if dupliqueEnfants == True :
##            # Duplication des noms de tarifs
##            req = """SELECT IDactivite, nom FROM noms_tarifs WHERE IDcategorie_tarif=%d;""" % IDcategorie_tarif_modele
##            DB.ExecuterReq(req)
##            listeNoms = DB.ResultatReq()
##            for IDactivite, nom in listeNoms :
##                listeDonnees = [
##                    ("IDactivite", IDactivite),
##                    ("IDcategorie_tarif", IDcategorie_tarif_nouveau),
##                    ("nom", nom),
##                    ]
##                IDnom_tarif_nouveau = DB.ReqInsert("noms_tarifs", listeDonnees)
##                
##                # ICI : Duplication des paramétrages à programmer... <<<<<<<<<<<<<<<<<<<<
##            
##        DB.Close()
##        self.MAJ()
##        # Ouverture de la fiche
##        self.ModifierCategorie(IDcategorie_tarif=IDcategorie_tarif_nouveau)

    def AjouterNom(self):
        dlg = wx.TextEntryDialog(self, _(u"Saisissez le nouveau nom de prestation :"), _(u"Saisie d'un nouveau nom de prestation"), u"")
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg2 = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg2.ShowModal()
                dlg2.Destroy()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ 
                    ("IDactivite", self.IDactivite ), 
                    ("nom", nom ),
                    ]
                IDnom_tarif = DB.ReqInsert("noms_tarifs", listeDonnees)
                DB.Close()
                dlg.Destroy()
                self.MAJ(selection=("noms_tarifs", IDnom_tarif))
        else:
            dlg.Destroy()
        

    def ModifierNom(self, IDnom_tarif=None):
        DB = GestionDB.DB()
        req = """SELECT nom FROM noms_tarifs WHERE IDnom_tarif=%d;""" % IDnom_tarif
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 : return
        nom = listeDonnees[0][0]
        DB.Close()
        dlg = wx.TextEntryDialog(self, _(u"Modifiez le nom de la prestation :"), _(u"Modification d'un nom de prestation"), nom)
        if dlg.ShowModal() == wx.ID_OK:
            nom = dlg.GetValue()
            if nom == "":
                dlg = wx.MessageDialog(self, _(u"Le nom que vous avez saisi n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            else:
                DB = GestionDB.DB()
                listeDonnees = [ ("nom", nom ), ]
                DB.ReqMAJ("noms_tarifs", listeDonnees, "IDnom_tarif", IDnom_tarif)
                DB.Close()
                self.MAJ(selection=("noms_tarifs", IDnom_tarif))
        dlg.Destroy()

    def SupprimerNom(self, IDnom_tarif=None):
        DB = GestionDB.DB()
        req = """SELECT IDtarif FROM tarifs WHERE IDnom_tarif=%d;""" % IDnom_tarif
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Il est impossible de supprimer un tarif qui comporte au moins un paramétrage !"), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce tarif ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("noms_tarifs", "IDnom_tarif", IDnom_tarif)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()

    def AjouterTarif(self, IDnom_tarif=None): 
        import DLG_Saisie_tarification 
        dlg = DLG_Saisie_tarification.Dialog(self, IDactivite=self.IDactivite, IDtarif=None, IDnom_tarif=IDnom_tarif)
        if dlg.ShowModal() == wx.ID_OK:
            IDtarif = dlg.GetIDtarif()
            self.MAJ(selection=("tarifs", IDtarif))
        dlg.Destroy()

    def ModifierTarif(self, IDtarif=None, IDnom_tarif=None):
        import DLG_Saisie_tarification
        dlg = DLG_Saisie_tarification.Dialog(self, IDactivite=self.IDactivite, IDtarif=IDtarif, IDnom_tarif=IDnom_tarif)
        if dlg.ShowModal() == wx.ID_OK:
            self.MAJ(selection=("tarifs", IDtarif))
        dlg.Destroy()

    def SupprimerTarif(self, IDtarif=None):
        DB = GestionDB.DB()
        req = """SELECT IDprestation FROM prestations WHERE IDtarif=%d;""" % IDtarif
        DB.ExecuterReq(req)
        listePrestations = DB.ResultatReq()
        DB.Close()
        nbrePrestations = len(listePrestations)
        if nbrePrestations > 0 :
            dlg = wx.MessageDialog(self, _(u"Ce tarif a déjà été attribué à %d prestations.\nIl est donc impossible de le supprimer !") % nbrePrestations, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer ce tarif ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("tarifs", "IDtarif", IDtarif)
            DB.ReqDEL("combi_tarifs", "IDtarif", IDtarif)
            DB.ReqDEL("combi_tarifs_unites", "IDtarif", IDtarif)
            DB.ReqDEL("tarifs_lignes", "IDtarif", IDtarif)
            DB.Close() 
            self.MAJ()
        dlg.Destroy()
    
    def DupliquerNom(self, IDnom_tarif, nomTarif):
        """ Duplication d'un nom de tarif """
        IDnom_tarif_modele = IDnom_tarif
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous dupliquer également les tarifs ?"), _(u"Duplication"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        if reponse == wx.ID_YES :
            dupliqueEnfants = True
        elif reponse == wx.ID_NO :
            dupliqueEnfants = False
        else :
            dlg.Destroy()
            return
        dlg.Destroy()
        DB = GestionDB.DB()

        # Duplication des noms de tarifs
        newIDnom_tarif = DB.Dupliquer(nomTable="noms_tarifs", nomChampCle="IDnom_tarif", conditions="IDnom_tarif=%d" % IDnom_tarif, dictModifications={"nom":_(u"Copie de %s") % nomTarif})
        
        # Duplication des tarif
        if dupliqueEnfants == True :
            req = """SELECT IDtarif, IDactivite FROM tarifs WHERE IDnom_tarif=%d;""" % IDnom_tarif
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            for IDtarif, IDactivite in listeDonnees :
                self.DupliquerTarif(IDtarif, nouveauIDnom_tarif=newIDnom_tarif)
        
        DB.Close() 
        return newIDnom_tarif
            
    def DupliquerTarif(self, IDtarif=None, nouveauIDnom_tarif=None):
        DB = GestionDB.DB()
        
        # Duplication du tarif 
        if nouveauIDnom_tarif != None :
            dictModifications = {"IDnom_tarif":nouveauIDnom_tarif}
        else :
            dictModifications = {}
        newIDtarif = DB.Dupliquer(nomTable="tarifs", nomChampCle="IDtarif", conditions="IDtarif=%d" % IDtarif, dictModifications=dictModifications)

        # Duplication des combinaisons de tarifs
        dictCorrespondances = DB.Dupliquer(nomTable="combi_tarifs", nomChampCle="IDcombi_tarif", conditions="IDtarif=%d" % IDtarif, dictModifications={"IDtarif":newIDtarif}, renvoieCorrespondances=True)
        
        # Duplication des unités de combinaisons de tarifs
        if type(dictCorrespondances) == dict :
            for ancienIDcombi, newIDcombi in dictCorrespondances.iteritems() :
                DB.Dupliquer(nomTable="combi_tarifs_unites", nomChampCle="IDcombi_tarif_unite", conditions="IDcombi_tarif=%d" % ancienIDcombi, dictModifications={"IDcombi_tarif":newIDcombi, "IDtarif":newIDtarif})
        
        # Duplication des lignes de tarifs
        DB.Dupliquer(nomTable="tarifs_lignes", nomChampCle="IDligne", conditions="IDtarif=%d" % IDtarif, dictModifications={"IDtarif":newIDtarif}, IDmanuel=True)

        # Duplication des filtres de questionnaire
        DB.Dupliquer(nomTable="questionnaire_filtres", nomChampCle="IDfiltre", conditions="IDtarif=%d" % IDtarif, dictModifications={"IDtarif":newIDtarif})

        DB.Close()
        return newIDtarif
        

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel, IDactivite=1)
        self.myOlv.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.myOlv, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
