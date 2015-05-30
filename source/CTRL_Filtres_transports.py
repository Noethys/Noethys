#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.customtreectrl as CT
import datetime
import GestionDB

from CTRL_Saisie_transport import DICT_CATEGORIES



class CTRL(CT.CustomTreeCtrl):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.SUNKEN_BORDER) :
        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style)
        self.parent = parent
        self.root = self.AddRoot(_(u"Transports"))
        self.listeBranches = []
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | CT.TR_AUTO_CHECK_PARENT | CT.TR_AUTO_CHECK_CHILD)
        self.EnableSelectionVista(True)

        # Création de l'ImageList
        self.dictImages = {}
        for code, valeurs in DICT_CATEGORIES.iteritems() :
            self.dictImages[code] = {"img" : wx.Bitmap('Images/16x16/%s.png' % valeurs["image"], wx.BITMAP_TYPE_PNG), "index" : None}
        
        il = wx.ImageList(16, 16)
        index =0
        for code, dictImage in self.dictImages.iteritems() :
            il.Add(dictImage["img"])
            dictImage["index"] = index
            index += 1
        self.AssignImageList(il)

        # Binds
        self.Bind(CT.EVT_TREE_ITEM_CHECKED, self.OnCheck)
    
    def MAJ(self, date_debut=None, date_fin=None, listeDates=[]):
        self.listeBranches = []
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Objets"))
        
        # Création de la condition
        if date_debut != None and date_fin != None :
            conditionDates = "(depart_date>='%s' AND depart_date<='%s') OR (arrivee_date>='%s' AND arrivee_date<='%s')" % (date_debut, date_fin, date_debut, date_fin)
        else :
            if len(listeDates) == 0 : conditionDates = "depart_date='2999-01-01' "
            elif len(listeDates) == 1 : conditionDates = "(depart_date='%s' OR arrivee_date='%s')" % (listeDates[0], listeDates[0])
            else : 
                listeTmp = []
                for dateTmp in listeDates :
                    listeTmp.append(str(dateTmp))
                conditionDates = "(depart_date IN %s OR arrivee_date IN %s)" % (str(tuple(listeTmp)), str(tuple(listeTmp)))

        DB = GestionDB.DB()
        
        # Récupération des lignes
        req = """SELECT IDligne, categorie, nom
        FROM transports_lignes;""" 
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        dictLignes = {}
        for IDligne, categorie, nom in listeValeurs :
            dictLignes[IDligne] = nom
            
        # Récupération des arrêts
        req = """SELECT IDarret, IDligne, nom
        FROM transports_arrets
        ORDER BY ordre;""" 
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        dictArrets = {}
        for IDarret, IDligne, nom in listeValeurs :
            dictArrets[IDarret] = {"IDligne":IDligne, "nom":nom}
            
        # Récupération des lieux
        req = """SELECT IDlieu, categorie, nom
        FROM transports_lieux;""" 
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        dictLieux = {}
        for IDlieu, categorie, nom in listeValeurs :
            dictLieux[IDlieu] = nom
            
        # Récupération des transports
        req = """SELECT IDtransport, categorie, IDligne, depart_IDarret, depart_IDlieu, arrivee_IDarret, arrivee_IDlieu
        FROM transports 
        WHERE %s;""" % conditionDates
        DB.ExecuterReq(req)
        listeValeurs = DB.ResultatReq()
        DB.Close()
        
        dictResultats = {}
        for IDtransport, categorie, IDligne, depart_IDarret, depart_IDlieu, arrivee_IDarret, arrivee_IDlieu in listeValeurs :

            typeTransports = DICT_CATEGORIES[categorie]["type"]
            
            # Ajout catégorie
            if dictResultats.has_key(categorie) == False :
                dictResultats[categorie] = {"lignes":[], "arrets":[], "lieux":[]}
            
            # Ajout Ligne
            if typeTransports == "lignes" :
                if IDligne not in dictResultats[categorie]["lignes"] :
                    dictResultats[categorie]["lignes"].append(IDligne)
            
                # Ajout Arret
                if depart_IDarret not in dictResultats[categorie]["arrets"] :
                        dictResultats[categorie]["arrets"].append(depart_IDarret)
                if arrivee_IDarret not in dictResultats[categorie]["arrets"] :
                        dictResultats[categorie]["arrets"].append(arrivee_IDarret)

            # Ajout Lieu
            if typeTransports == "lieux" :
                if depart_IDlieu not in dictResultats[categorie]["lieux"] :
                        dictResultats[categorie]["lieux"].append(depart_IDlieu)
                if arrivee_IDlieu not in dictResultats[categorie]["lieux"] :
                        dictResultats[categorie]["lieux"].append(arrivee_IDlieu)
        
        # Remplissage
        listeCategories = []
        if len(dictResultats) > 0 :
            listeCategories = dictResultats.keys() 
        listeCategories.sort() 
        
        for categorie in listeCategories :
            
            # Catégories
            brancheCategorie = self.AppendItem(self.root, DICT_CATEGORIES[categorie]["label"], ct_type=1)
            self.SetPyData(brancheCategorie, {"categorie":"categories", "code":categorie})
            self.SetItemBold(brancheCategorie)
            self.SetItemImage(brancheCategorie, self.dictImages[categorie]["index"])
            brancheCategorie.Check() 
            self.listeBranches.append(brancheCategorie) 
            
            # Lignes
            listeLignes = []
            for IDligne in dictResultats[categorie]["lignes"] :
                if dictLignes.has_key(IDligne) :
                    label = dictLignes[IDligne]
                else :
                    label = _(u"Ligne inconnue")
                listeLignes.append((label, IDligne))
            listeLignes.sort() 
            
            for label, IDligne in listeLignes :
                brancheLigne = self.AppendItem(brancheCategorie, label, ct_type=1)
                self.SetPyData(brancheLigne, {"categorie":"lignes", "code":IDligne})
                brancheLigne.Check() 
                self.listeBranches.append(brancheLigne) 
                
                # Arrêts
                for IDarret in dictResultats[categorie]["arrets"] :
                    if dictArrets.has_key(IDarret) :
                        label = dictArrets[IDarret]["nom"]
                    else :
                        label = _(u"Arrêt inconnu")
                    if IDarret == None or dictArrets[IDarret]["IDligne"] == IDligne :
                        brancheArret = self.AppendItem(brancheLigne, label, ct_type=1)
                        self.SetPyData(brancheArret, {"categorie":"arrets", "code":IDarret})
                        brancheArret.Check() 
                        self.listeBranches.append(brancheArret) 
                        
            # Lieux
            listeLieux = []
            for IDlieu in dictResultats[categorie]["lieux"] :
                if dictLieux.has_key(IDlieu) :
                    label = dictLieux[IDlieu]
                else :
                    label = _(u"Lieu inconnu")
                listeLieux.append((label, IDlieu))
            listeLieux.sort() 
            
            for label, IDlieu in listeLieux :
                brancheLieu = self.AppendItem(brancheCategorie, label, ct_type=1)
                self.SetPyData(brancheLieu, {"categorie":"lieux", "code":IDlieu})
                brancheLieu.Check() 
                self.listeBranches.append(brancheLieu) 
                
        self.ExpandAll() 
        
    def OnCheck(self, event):
        item = event.GetItem()
        categorie = self.GetPyData(item)["categorie"]
        code = self.GetPyData(item)["code"]
        etat = self.IsItemChecked(item)
        try :
            self.parent.OnCocheFiltres()
        except :
            pass
        
    def GetCoches(self):
        """ Obtient la liste des éléments cochés """
        dictCoches = {}
        for branche in self.listeBranches :
            if self.IsItemChecked(branche) == True :
                data = self.GetPyData(branche)
                if dictCoches.has_key(data["categorie"]) == False :
                    dictCoches[data["categorie"]] = []
                dictCoches[data["categorie"]].append(data["code"])
        return dictCoches
    
    def Coche(self, etat=True):
        """ Coche tout ou rien """
        for branche in self.listeBranches :
            self.CheckItem(branche, etat)


# ------------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.myOlv = CTRL(panel)
        self.myOlv.MAJ(date_debut = datetime.date(2012, 3, 4), date_fin = datetime.date(2012, 5, 22)) 

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
