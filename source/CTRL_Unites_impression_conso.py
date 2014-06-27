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
import datetime
import GestionDB
import UTILS_Config
import copy

try: import psyco; psyco.full()
except: pass

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)

LARGEUR_COLONNE_AFFICHAGE = 185


class Track(object):
    def __init__(self, donnees, type="conso"):
        self.type = type
        if type == "conso" :
            self.texteType = "Consommation"
        else:
            self.texteType = "Remplissage"
        self.IDunite = donnees[0]
        self.IDactivite = donnees[1]
        self.nomUnite = donnees[2]
        self.abrege = donnees[3]
        self.ordre = donnees[4]
        self.nomActivite = donnees[5]
        self.affichage = None
        self.position = 0
        
        # Items HyperTreeList
        self.item = None
        self.itemParent = None
        
        # Contrôles
        self.ctrl_affichage = None
        
    def ReinitAffichage(self):
        self.affichage = None
        self.ctrl_affichage.SetDefaut()
    

# --------------------------------------------------------------------------------------------------------------------------------

class CTRL_Affichage(wx.Choice):
    def __init__(self, parent, id=-1, item=None, track=None):
        """ Type d'affichage """
        wx.Choice.__init__(self, parent, id=id, size=(LARGEUR_COLONNE_AFFICHAGE-7, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        if self.track.type == "conso" :
            self.SetItems([u"Toujours afficher", u"Ne jamais afficher", u"Afficher uniquement si ouvert"])
        else:
            self.SetItems([u"Toujours afficher", u"Ne jamais afficher"])
        self.SetToolTipString(u"Sélectionnez un type d'affichage pour cette unité")
        # Defaut
        self.SetDefaut() 
        # Bind
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
    
    def SetDefaut(self):
        if self.track.affichage == None :
            if self.track.type == "conso" : 
                self.SetSelection(2)
                self.track.affichage = "utilise"
            if self.track.type == "remplissage" : 
                self.SetSelection(1)
                self.track.affichage = "jamais"
        else:
            if self.track.affichage == "toujours" : self.SetSelection(0)
            if self.track.affichage == "jamais" : self.SetSelection(1)
            if self.track.affichage == "utilise" : self.SetSelection(2)

    def OnChoice(self, event):
        if self.GetSelection() == 0 : self.track.affichage = "toujours"
        if self.GetSelection() == 1 : self.track.affichage = "jamais"
        if self.GetSelection() == 2 : self.track.affichage = "utilise"

# -------------------------------------------------------------------------------------------------------------------
            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.typeListe = "journ" # ou "period"
        self.listeActivites = []
        
        # Importation des données
        self.dictTracks, self.dictActivites, self.dictInitial = self.Importation() 
                
        # Création des colonnes
        listeColonnes = [
            ( u"Activité / Unité", 190, wx.ALIGN_LEFT),
            ( u"Abrégé", 60, wx.ALIGN_LEFT),
            ( u"Type", 90, wx.ALIGN_LEFT),
            ( u"Affichage", LARGEUR_COLONNE_AFFICHAGE, wx.ALIGN_LEFT),
            ( u"Ordre", 40, wx.ALIGN_CENTER),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1

        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu)
        
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_ROW_LINES |  wx.TR_COLUMN_LINES |wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
                    
    def Importation(self):
        """ Importation des unités de conso et de remplissage """
        DB = GestionDB.DB()
        listeTracks = []
        dictActivites = {}
        
        # Importation des unités de consommations
        type = "conso"
        req = """SELECT 
        unites.IDunite, unites.IDactivite, unites.nom, unites.abrege, unites.ordre,
        activites.nom
        FROM unites
        LEFT JOIN activites ON activites.IDactivite = unites.IDactivite
        ORDER BY unites.IDactivite, ordre
        ;""" 
        DB.ExecuterReq(req)
        listeUnitesConso = DB.ResultatReq()     
        for item in listeUnitesConso :
            track = Track(item, type)
            listeTracks.append(track)
            dictActivites[track.IDactivite] = track.nomActivite

        # Importation des unités de remplissage
        type="remplissage"
        req = """SELECT 
        unites_remplissage.IDunite_remplissage, unites_remplissage.IDactivite, 
        unites_remplissage.nom, unites_remplissage.abrege, unites_remplissage.ordre, activites.nom
        FROM unites_remplissage
        LEFT JOIN activites ON activites.IDactivite = unites_remplissage.IDactivite
        ORDER BY unites_remplissage.IDactivite, ordre
        ;"""
        DB.ExecuterReq(req)
        listeUnitesRemplissage = DB.ResultatReq()     
        for item in listeUnitesRemplissage :
            track = Track(item, type)
            listeTracks.append(track)
            dictActivites[track.IDactivite] = track.nomActivite

        DB.Close() 

        # Met les tracks de la base de données dans un dict
        dictTracks = {}
        for track in listeTracks :
            key = track.IDactivite
            if dictTracks.has_key(key) :
                dictTracks[key][(track.type, track.IDunite)] = track
            else:
                dictTracks[key] = { (track.type, track.IDunite) : track }

        # Tri et récupération des valeurs par défaut
        dictInitial = { "journ" : {}, "period" : {} }
        dictFinal = { "journ" : {}, "period" : {} }
        for typeListe in dictFinal.keys() :

            # Création d'un dict avec les données initiales pour une ré-initialisation du tri
            for track in listeTracks :
                IDactivite = track.IDactivite
                if dictInitial[typeListe].has_key(IDactivite) == False :
                    dictInitial[typeListe][IDactivite] = []
                trackTemp = copy.deepcopy(track)
                dictInitial[typeListe][IDactivite].append(trackTemp)

            # récupère les valeurs mémorisées dans le fichier Config
            dictUnites = UTILS_Config.GetParametre("impression_conso_%s_unites" % typeListe, defaut={})
            listeTracksTemp = listeTracks[:]
            for IDactivite, listeUnites in dictUnites.iteritems() :
                if dictFinal[typeListe].has_key(IDactivite) == False :
                    dictFinal[typeListe][IDactivite] = []
                for type, IDunite, affichage in listeUnites :
                    if dictTracks.has_key(IDactivite) :
                        if dictTracks[IDactivite].has_key((type, IDunite)) :
                            track = dictTracks[IDactivite][(type, IDunite)]
                            track.affichage = affichage
                            dictFinal[typeListe][IDactivite].append(copy.deepcopy(track))
                            listeTracksTemp.remove(track)
            
            # Rajoute les tracks n'apparaissant pas dans le dict par défaut
            for track in listeTracksTemp :
                IDactivite = track.IDactivite
                if dictFinal[typeListe].has_key(IDactivite) == False :
                    dictFinal[typeListe][IDactivite] = []
                dictFinal[typeListe][IDactivite].append(copy.deepcopy(track))

        return dictFinal, dictActivites, dictInitial
    
    def MemoriseParametres(self):
        for typeListe in ("journ", "period") :
            dictValeurs = {}
            for IDactivite, listeTracks in self.dictTracks[typeListe].iteritems() :
                if dictValeurs.has_key(IDactivite) == False :
                    dictValeurs[IDactivite] = []
                for track in listeTracks :
                    dictValeurs[IDactivite].append((track.type, track.IDunite, track.affichage)) 
            UTILS_Config.SetParametre("impression_conso_%s_unites" % typeListe, dictValeurs)   
    
    def SetTypeListe(self, type="journ") :
        self.typeListe = type

    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
        self.MAJ() 
        
    def MAJ(self, selectionItem=None):
        """ Met à jour (redessine) tout le contrôle """
        self.Freeze()
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(u"Racine")
        self.Remplissage(selectionItem)
        self.Thaw() 

    def Remplissage(self, selectionItem=None):
        # Regroupement
        listeKeys = []
        for IDactivite, nomActivite in self.dictActivites.iteritems() :
            key = (nomActivite, IDactivite)
            if key not in listeKeys :
                listeKeys.append(key)
        listeKeys.sort()
        
        # Création des branches
        for nomActivite, IDactivite in listeKeys :
            
            if IDactivite in self.listeActivites :
            
                # Niveau Nom de l'activité
                brancheActivite = self.AppendItem(self.root, nomActivite)
                self.SetPyData(brancheActivite, IDactivite)
                self.SetItemBold(brancheActivite, True)
                self.SetItemBackgroundColour(brancheActivite, COULEUR_FOND_REGROUPEMENT)
                
                # Niveau Unités de consommation ou de remplissage
                index = 0
                for track in self.dictTracks[self.typeListe][IDactivite] :
                    
                    if track.IDactivite == IDactivite :
                    
                        brancheUnite = self.AppendItem(brancheActivite, track.nomUnite)
                        self.SetPyData(brancheUnite, track) # track.IDunite
                        
                        # Mémorisation des items dans le track
                        track.item = brancheUnite
                        track.itemParent = brancheActivite
                        
                        # Colonnes textes
                        self.SetItemText(brancheUnite, track.abrege, 1)
                        self.SetItemText(brancheUnite, track.texteType, 2)
                        
                        # CTRL de l'affichage
                        ctrl_affichage = CTRL_Affichage(self.GetMainWindow(), item=brancheUnite, track=track)
                        self.SetItemWindow(brancheUnite, ctrl_affichage, 3)        
                        track.ctrl_affichage = ctrl_affichage      
                        
                        # Colonnes textes
                        self.SetItemText(brancheUnite, str(index+1), 4)
                        track.position = index
                        index += 1
                        
                        # Sélection d'un item
                        if selectionItem == track :
                            self.SelectItem(brancheUnite, True)
                            self.ScrollTo(brancheUnite)
                                                
        self.ExpandAllChildren(self.root)
        
        # Pour éviter le bus de positionnement des contrôles
        self.GetMainWindow().CalculatePositions() 
                
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
    
    def GetDonnees(self):
        """ Récupère les résultats des données saisies """
        dictDonnees = {}
        for IDactivite, listeTracks in self.dictTracks[self.typeListe].iteritems() :
            if dictDonnees.has_key(IDactivite) == False : 
                dictDonnees[IDactivite] = []
            for track in listeTracks :
                dictDonnees[IDactivite].append((track.type, track.IDunite, track.affichage))
        return dictDonnees

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        item = self.GetSelection()
        dictItem = self.GetMainWindow().GetItemPyData(item)
        
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Monter
        item = wx.MenuItem(menuPop, 10, u"Monter")
        bmp = wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=10)
        
        # Item Descendre
        item = wx.MenuItem(menuPop, 20, u"Descendre")
        bmp = wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=20) 
        
        menuPop.AppendSeparator()
        
        # Item Descendre
        item = wx.MenuItem(menuPop, 30, u"Réinitialiser")
        bmp = wx.Bitmap("Images/16x16/Actualiser.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Reinit, id=30)            

        # Finalisation du menu
        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
##    def RechercherTrack(self, trackSelection=None):
##        for IDactivite, listeTracks in self.dictTracks[self.typeListe].iteritems() :
##            index = 0
##            for track in listeTracks :
##                if track == trackSelection :
##                    return track, position
##                index += 1

    def Monter(self, event):
        item = self.GetSelection()
        track = self.GetMainWindow().GetItemPyData(item)
        if track == None :
            dlg = wx.MessageDialog(self, u"Nous n'avez sélectionné aucune unité à déplacer !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if track.position == 0 :
            dlg = wx.MessageDialog(self, u"Cette unité est déjà en première position !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        listeTemp = self.dictTracks[self.typeListe][track.IDactivite]
        listeTemp.remove(track) 
        track.position -= 1
        listeTemp.insert(track.position, track)
        self.MAJ(track) 
        
    def Descendre(self, event):
        item = self.GetSelection()
        track = self.GetMainWindow().GetItemPyData(item)
        if track == None :
            dlg = wx.MessageDialog(self, u"Nous n'avez sélectionné aucune unité à déplacer !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if track.position == len(self.dictTracks[self.typeListe][track.IDactivite])-1 :
            dlg = wx.MessageDialog(self, u"Cette unité est déjà en dernière position !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        listeTemp = self.dictTracks[self.typeListe][track.IDactivite]
        listeTemp.remove(track) 
        track.position += 1
        listeTemp.insert(track.position, track)
        self.MAJ(track) 
    
    def Reinit(self, event):
        dlg = wx.MessageDialog(self, u"Souhaitez-vous vraiment réinitialiser la liste des unités ?", u"Réinitialisation", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES :
            self.dictTracks = copy.deepcopy(self.dictInitial)
            self.MAJ() 
        dlg.Destroy()

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.listeActivites = [1, 3]
        self.ctrl.MAJ() 
        self.boutonTest = wx.Button(panel, -1, u"Test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
    
    def OnBoutonTest(self, event):
        print self.ctrl.GetDonnees()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
