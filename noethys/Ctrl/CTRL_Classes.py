#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB

from Utils import UTILS_Utilisateurs

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


    
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style= wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT,
                 modeSelection=False,
                 ):
        HTL.HyperTreeList.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.modeSelection = modeSelection
        self.IDecole = None
        
        self.SetBackgroundColour(wx.WHITE)
        
        self.dictNiveaux = self.ImportationNiveaux()

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.img_ecole = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Ecole.png'), wx.BITMAP_TYPE_PNG))
        self.img_classe = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Classe.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Creation des colonnes
        self.AddColumn(_(u"Saison / Classe"))
        self.SetColumnWidth(0, 370)
        self.AddColumn(_(u"Niveaux scolaires"))
        self.SetColumnWidth(1, 120)
        self.SetMainColumn(0)
                                
        # Création des branches
        self.root = self.AddRoot(_(u"Classes"))
        self.SetPyData(self.root, {"type" : "root", "ID" : None} )
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | TR_COLUMN_LINES | wx.TR_HAS_BUTTONS)
        
        # Binds
        if self.modeSelection == False :
            self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
            self.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        else :
            self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectItem)
                        
    def MAJ(self, IDecole=None, selection=None):
        """ Met à jour (redessine) tout le contrôle """
        self.IDecole = IDecole
        nbreBranches = 1#self.GetMainWindow().GetCount()
        if nbreBranches > 0 :
            self.DeleteChildren(self.root)
        if self.IDecole != None :
            self.CreationBranches()
            # Sélection
            if selection != None :
                branche = self.dictBranches[selection]
                self.SelectItem(branche)

    def ImportationNiveaux(self):
        dictNiveaux = {}
        DB = GestionDB.DB()
        req = """SELECT IDniveau, ordre, nom, abrege
        FROM niveaux_scolaires
        ORDER BY ordre; """ 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        for IDniveau, ordre, nom, abrege in listeDonnees :
            dictNiveaux[IDniveau] = {"nom" : nom, "abrege" : abrege, "ordre" : ordre}
        return dictNiveaux

    def CreationBranches(self):
        """ Met uniquement à jour le contenu du contrôle """
        self.dictBranches = {} 
        
        # --- Importation des données ---
        DB = GestionDB.DB()
        req = """SELECT IDclasse, nom, date_debut, date_fin, niveaux
        FROM classes 
        WHERE IDecole=%d
        ORDER BY date_debut, nom; """ % self.IDecole
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        
        # Regroupement par saison
        dictClasses = {}
        for IDclasse, nom, date_debut, date_fin, niveaux in listeDonnees :
            
            # Formatage des dates de la saison
            date_debut = DateEngEnDateDD(date_debut)
            date_fin = DateEngEnDateDD(date_fin)
            saison = (date_debut, date_fin) 
            
            # Formatage des niveaux
            listeNiveaux = []
            listeOrdresNiveaux = []
            txtNiveaux = u""
            if niveaux != None and niveaux != "" and niveaux != " " :
                listeTemp = niveaux.split(";")
                txtTemp = []
                for niveau in listeTemp :
                    IDniveau = int(niveau)
                    if IDniveau in self.dictNiveaux :
                        nomNiveau = self.dictNiveaux[IDniveau]["abrege"]
                        ordreNiveau = self.dictNiveaux[IDniveau]["ordre"]
                        listeNiveaux.append(IDniveau)
                        txtTemp.append(nomNiveau)
                        listeOrdresNiveaux.append(ordreNiveau)
                txtNiveaux = ", ".join(txtTemp)
            
            # Création du dict Classes
            if (saison in dictClasses) == False :
                dictClasses[saison] = []
            
            donnees = (listeOrdresNiveaux, nom, txtNiveaux, IDclasse) 
            dictClasses[saison].append(donnees)
        
        # Tri des saisons par date
        listeSaisons = list(dictClasses.keys()) 
        listeSaisons.sort() 
        
        
        # Création des saisons
        indexSaison = 1
        for saison in listeSaisons :
            nomSaison = _(u"Du %s au %s") % (DateEngFr(str(saison[0])), DateEngFr(str(saison[1])) )
            brancheSaison = self.AppendItem(self.root, nomSaison)
            self.SetPyData(brancheSaison, {"type" : "saison", "ID" : saison, "nom" : nomSaison} )
            self.SetItemBold(brancheSaison, True)
            
            # Création des classes
            listeClasses = dictClasses[saison]
            listeClasses.sort() 
            
            # Tri des classes par niveau
            for listeOrdresNiveaux, nomClasse, txtNiveaux, IDclasse in listeClasses :
                brancheClasse = self.AppendItem(brancheSaison, nomClasse)
                self.SetPyData(brancheClasse, {"type" : "classe", "ID" : IDclasse, "nom" : nomClasse} )
                self.SetItemText(brancheClasse, txtNiveaux, 1)
                
                self.dictBranches[IDclasse] = brancheClasse
            
            if indexSaison == len(listeSaisons) :
                self.Expand(brancheSaison)
            indexSaison += 1
    
    def OnLeftDClick(self, event):
        dictItem = self.GetMainWindow().GetItemPyData(self.GetSelection())
        type = dictItem["type"]
        ID = dictItem["ID"]    
        if type == "classe" : self.Modifier(ID)
        event.Skip()
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        ID = dictItem["ID"]
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)

        if type == "classe" : 
            menuPop.AppendSeparator() 
            
            # Item Modifier
            item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Modifier.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Modifier, id=20)
            
            # Item Supprimer
            item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.Bind(wx.EVT_MENU, self.Supprimer, id=30)

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
                    

    def Ajouter(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_classes", "creer") == False : return
        from Dlg import DLG_Saisie_classe
        dlg = DLG_Saisie_classe.Dialog(self, IDecole=self.IDecole)
        if dlg.ShowModal() == wx.ID_OK:
            IDclasse = dlg.GetIDclasse()
            self.MAJ(IDecole=self.IDecole, selection=IDclasse)
        dlg.Destroy()

    def Modifier(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_classes", "modifier") == False : return
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        IDclasse = dictItem["ID"]
        
        if type != "classe" : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune classe à modifier !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return        

        from Dlg import DLG_Saisie_classe
        dlg = DLG_Saisie_classe.Dialog(self, IDecole=self.IDecole, IDclasse=IDclasse)
        if dlg.ShowModal() == wx.ID_OK:
            IDclasse = dlg.GetIDclasse()
            self.MAJ(IDecole=self.IDecole, selection=IDclasse)
        dlg.Destroy()


    def Supprimer(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_classes", "supprimer") == False : return
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        IDclasse = dictItem["ID"]
        
        if type != "classe" : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune classe à supprimer !"), _(u"Erreur"), wx.OK | wx.ICON_QUESTION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Vérifie que cette classe n'a pas été attribuée à un individu
        DB = GestionDB.DB()
        req = """SELECT COUNT(IDclasse)
        FROM scolarite 
        WHERE IDclasse=%d
        ;""" % IDclasse
        DB.ExecuterReq(req)
        nbre = int(DB.ResultatReq()[0][0])
        DB.Close()
        if nbre > 0 :
            dlg = wx.MessageDialog(self, _(u"Cette classe a déjà été attribuée %d fois.\n\nVous ne pouvez donc pas la supprimer !") % nbre, _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Confirmation de suppression
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette classe ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        if dlg.ShowModal() == wx.ID_YES :
            DB = GestionDB.DB()
            DB.ReqDEL("classes", "IDclasse", IDclasse)
            DB.Close() 
            self.MAJ(IDecole=self.IDecole)
        dlg.Destroy()
    
    def OnSelectItem(self, event=None):
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        IDclasse = dictItem["ID"]
        try :
            self.parent.OnChoixClasse()
        except :
            pass
    
    def GetClasse(self):
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        type = dictItem["type"]
        IDclasse = dictItem["ID"]
        if type == "classe" : 
            return IDclasse
        else :
            None

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = CTRL(panel)
        self.myOlv.MAJ(IDecole=2) 
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
