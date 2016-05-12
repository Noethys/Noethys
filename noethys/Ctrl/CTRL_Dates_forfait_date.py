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
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import copy
import operator
import sys
import GestionDB
from Utils import UTILS_Dates

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)
            


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, IDactivite=None, IDtarif=None):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDtarif = IDtarif

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)
                
        # Création des colonnes
        listeColonnes = [
            ( _(u"Groupe/Date"), 200, wx.ALIGN_LEFT),
            ( _(u"Combinaisons d'unités"), 280, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
                
        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | wx.TR_COLUMN_LINES | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
        
        # Init contrôle
        self.ImportationInitiale() 
        self.MAJ() 
    
    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()

    def ImportationInitiale(self):
        """ Importation initiale des données """
        DB = GestionDB.DB()
        
        # Importation des unités de l'activité
        req = """SELECT IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeUnites = DB.ResultatReq()
        self.dictUnites = {}
        for IDunite, ordre, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin in listeUnites :
            self.dictUnites[IDunite] = {"ordre":ordre, "nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "date_debut":date_debut, "date_fin":date_fin}

        # Importation des groupes de l'activité
        req = """SELECT IDgroupe, nom, ordre, abrege
        FROM groupes
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeGroupes = DB.ResultatReq()
        self.dictGroupes = {}
        for IDgroupe, nom, ordre, abrege in listeGroupes :
            self.dictGroupes[IDgroupe] = {"ordre":ordre, "nom":nom, "abrege":abrege, "IDgroupe":IDgroupe}
        
        # Importation des combinaisons
        req = """SELECT IDcombi_tarif, IDtarif, date, IDgroupe
        FROM combi_tarifs
        WHERE IDtarif=%d AND type='FORFAIT'
        ORDER BY IDcombi_tarif;""" % self.IDtarif
        DB.ExecuterReq(req)
        self.listeCombinaisons = DB.ResultatReq()
        self.listeAnciennesCombi = []
        for IDcombi_tarif, IDtarif, date, IDgroupe in self.listeCombinaisons :
            self.listeAnciennesCombi.append(IDcombi_tarif)
            
        # Importation des unités des combinaisons
        req = """SELECT IDcombi_tarif_unite, IDcombi_tarif, IDunite
        FROM combi_tarifs_unites
        WHERE IDtarif=%d;""" % self.IDtarif
        DB.ExecuterReq(req)
        self.listeUnitesCombi = DB.ResultatReq()

        self.dictUnitesCombi = {}
        self.listeAnciennesUnites = []
        for IDcombi_tarif_unite, IDcombi_tarif, IDunite in self.listeUnitesCombi :
            self.listeAnciennesUnites.append(IDcombi_tarif_unite)
            dictTemp = {"IDcombi_tarif_unite":IDcombi_tarif_unite, "IDunite":IDunite}
            if self.dictUnitesCombi.has_key(IDcombi_tarif) :
                self.dictUnitesCombi[IDcombi_tarif].append(dictTemp)
            else:
                self.dictUnitesCombi[IDcombi_tarif] = [dictTemp,]
                
        # Création de la liste des données
        self.listeDonneesInitiale = []
        for IDcombi_tarif, IDtarif, date, IDgroupe in self.listeCombinaisons :
            if date != None : date = UTILS_Dates.DateEngEnDateDD(date)
            listeUnites = []
            if self.dictUnitesCombi.has_key(IDcombi_tarif) :
                listeUnites = self.dictUnitesCombi[IDcombi_tarif]
            
            if IDgroupe != None :
                # Nouvelle version
                self.listeDonneesInitiale.append({"date":date, "IDcombi_tarif":IDcombi_tarif, "IDgroupe":IDgroupe, "unites":listeUnites})
            else :
                # Pour gérer ancienne version
                for IDgroupe, x in self.dictGroupes.iteritems() :
                    self.listeDonneesInitiale.append({"date":date, "IDcombi_tarif":IDcombi_tarif, "IDgroupe":IDgroupe, "unites":listeUnites})
                
        self.listeDonnees = copy.deepcopy(self.listeDonneesInitiale)
        DB.Close()

    def Remplissage(self):
        """ Remplissage """
        # Branches GROUPE
        dictTemp = {}
        for dictCombi in self.listeDonnees :
            IDgroupe = dictCombi["IDgroupe"]
            if IDgroupe == None :
                nomGroupe = _(u"Tous les groupes")
            else :
                if self.dictGroupes.has_key(IDgroupe) :
                    nomGroupe = self.dictGroupes[IDgroupe]["nom"]
                else :
                    nomGroupe = _(u"Groupe inconnu")
            groupe = (nomGroupe, IDgroupe)
            if dictTemp.has_key(groupe) == False :
                dictTemp[groupe] = []
            dictTemp[groupe].append(dictCombi)
            dictTemp[groupe] = sorted(dictTemp[groupe], key=operator.itemgetter("date"), reverse=False)
        listeGroupes = dictTemp.keys() 
        listeGroupes.sort() 
        
        for groupe in listeGroupes :
            nomGroupe, IDgroupe = groupe
            niveauGroupe = self.AppendItem(self.root, nomGroupe)
            self.SetItemBold(niveauGroupe, True)
##            self.SetItemBackgroundColour(niveauGroupe, COULEUR_FOND_REGROUPEMENT)
            
            # Branches DATE
            listeCombi = dictTemp[groupe]
            for dictCombi in listeCombi :
                date = dictCombi["date"]
                niveauDate = self.AppendItem(niveauGroupe, UTILS_Dates.DateComplete(date))
                
                # Combinaisons d'unités
                texteTemp = []
                for dictUniteCombi in dictCombi["unites"] :
                    IDunite = dictUniteCombi["IDunite"]
                    texteTemp.append((self.dictUnites[IDunite]["ordre"], self.dictUnites[IDunite]["nom"]))
                texteTemp.sort()
                texteTemp2 = []
                for ordre, nomUnite in texteTemp :
                    texteTemp2.append(nomUnite)
                texteUnites = u" + ".join(texteTemp2)
                self.SetItemText(niveauDate, texteUnites, 1)
                
        self.ExpandAllChildren(self.root)
            
    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()
    
    def Modifier(self):
        # Préparation du dictSelections
        dictSelections = {}
        dictTempCombi = {}
        dictTempUnites = {}
        for dictCombi in self.listeDonnees :
            date = dictCombi["date"]
            listeUnites = dictCombi["unites"]
            IDcombi_tarif = dictCombi["IDcombi_tarif"]
            IDgroupe = dictCombi["IDgroupe"]
            dictTempCombi[(date, IDgroupe)] = {"IDcombi_tarif":IDcombi_tarif, "listeUnites":listeUnites}
            for dictUniteCombi in listeUnites :
                IDcombi_tarif_unite = dictUniteCombi["IDcombi_tarif_unite"]
                IDunite = dictUniteCombi["IDunite"]
                if dictSelections.has_key(date) == False :
                    dictSelections[date] = {}
                if dictSelections[date].has_key(IDgroupe) == False :
                    dictSelections[date][IDgroupe] = []
                if IDunite not in dictSelections[date][IDgroupe] :
                    dictSelections[date][IDgroupe].append(IDunite)
                dictTempUnites[(date, IDgroupe, IDunite)] = IDcombi_tarif_unite
                
        # DLG Calendrier
        from Dlg import DLG_Dates_forfait_date
        dlg = DLG_Dates_forfait_date.Dialog(self, IDactivite=self.IDactivite, dictSelections=dictSelections)
        if dlg.ShowModal() == wx.ID_OK:
            dictSelections = dlg.GetSelections() 
            dlg.Destroy()
        else:
            dlg.Destroy()
            return
        
        # Conversion pour le listeDonnees
        self.listeDonnees = []
        for date, dictDates in dictSelections.iteritems() :
            
            for IDgroupe, listeUnites in dictDates.iteritems() :
                
                if dictTempCombi.has_key((date, IDgroupe)) :
                    IDcombi_tarif = dictTempCombi[(date, IDgroupe)]["IDcombi_tarif"]
                else :
                    IDcombi_tarif = None
                
                listeTemp = []
                for IDunite in listeUnites :
                    if dictTempUnites.has_key((date, IDgroupe, IDunite)) :
                        IDcombi_tarif_unite = dictTempUnites[(date, IDgroupe, IDunite)]
                    else :
                        IDcombi_tarif_unite = None
                    listeTemp.append({"IDcombi_tarif_unite":IDcombi_tarif_unite, "IDunite":IDunite})
        
                self.listeDonnees.append({"date":date, "IDcombi_tarif":IDcombi_tarif, "IDgroupe":IDgroupe, "unites":listeTemp})
        
        # MAJ Contrôle
        self.MAJ() 

    def ToutSupprimer(self):
        self.listeDonnees = []
        self.MAJ() 

    def Sauvegarde(self):
        DB = GestionDB.DB()
        
        listeIDcombi = []
        listeIDunites = []
        
        for dictCombi in self.listeDonnees :
            date = dictCombi["date"]
            IDcombi_tarif = dictCombi["IDcombi_tarif"]
            IDgroupe = dictCombi["IDgroupe"]

            # Sauvegarde des nouvelles combinaisons
            if IDcombi_tarif == None :
                listeDonnees = [ ("IDtarif", self.IDtarif ), ("type", "FORFAIT" ), ("date", str(date) ), ("IDgroupe", IDgroupe) ]
                IDcombi_tarif = DB.ReqInsert("combi_tarifs", listeDonnees)
            else:
                listeIDcombi.append(IDcombi_tarif)
            
            # Sauvegarde des unités de combi
            for dictUnitesCombi in dictCombi["unites"] :
                IDcombi_tarif_unite = dictUnitesCombi["IDcombi_tarif_unite"]
                IDunite = dictUnitesCombi["IDunite"]
                
                # Nouvelles unités
                if IDcombi_tarif_unite == None :
                    listeDonnees = [ ("IDcombi_tarif", IDcombi_tarif ), ("IDtarif", self.IDtarif ), ("IDunite", IDunite ), ]
                    IDcombi_tarif_unite = DB.ReqInsert("combi_tarifs_unites", listeDonnees)
                else:
                    listeIDunites.append(IDcombi_tarif_unite)
        
        # Suppression des combi supprimées
        for IDcombi_tarif in self.listeAnciennesCombi :
            if IDcombi_tarif not in listeIDcombi :
                DB.ReqDEL("combi_tarifs", "IDcombi_tarif", IDcombi_tarif)
            
        # Suppression des unités supprimées
        for IDcombi_tarif_unite in self.listeAnciennesUnites :
            if IDcombi_tarif_unite not in listeIDunites :
                DB.ReqDEL("combi_tarifs_unites", "IDcombi_tarif_unite", IDcombi_tarif_unite)
        
        DB.Close()

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
                
        self.ctrl = CTRL(panel, IDactivite=1, IDtarif=1)
        self.bouton1 = wx.Button(panel, -1, _(u"Modifier"))
        self.bouton2 = wx.Button(panel, -1, _(u"Sauvegarder"))

        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton1, 0, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton2, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((900, 500))
        self.Layout()
        self.CenterOnScreen()
        
        self.Bind(wx.EVT_BUTTON, self.OnBouton1, self.bouton1)
        self.Bind(wx.EVT_BUTTON, self.OnBouton2, self.bouton2)

    def OnBouton1(self, event):
        self.ctrl.Modifier()
        
    def OnBouton2(self, event):
        self.ctrl.Sauvegarde()
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
