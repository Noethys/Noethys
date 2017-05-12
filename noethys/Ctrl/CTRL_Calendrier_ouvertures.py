#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime
import GestionDB

try: import psyco; psyco.full()
except: pass

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
    
class Calendrier(HTL.HyperTreeList):
    def __init__(self, parent, IDactivite=None): 
        HTL.HyperTreeList.__init__(self, parent, -1, style = wx.TR_DEFAULT_STYLE)
        self.IDactivite = IDactivite

        # Adapte taille Police pour Linux
        from Utils import UTILS_Linux
        UTILS_Linux.AdaptePolice(self)

        # Création de la colonne principale
        self.AddColumn(_(u"Périodes / Groupes"))
        self.SetMainColumn(0)
        self.SetColumnWidth(0, 190)

        # wx.TR_COLUMN_LINES |  | wx.TR_HAS_BUTTONS
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT  | TR_COLUMN_LINES | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER

    
    def Initialisation(self):
        # Récupération des données
        listeDates = (datetime.date(1977, 1, 1), datetime.date(2999, 1, 1))
        dictNomsGroupes = self.GetDictGroupes() 
        listeUnites = self.GetListeUnites(listeDates[0], listeDates[-1])
        self.dictOuvertures = {}
        self.GetDictOuvertures(listeDates[0], listeDates[-1])
        
        # Analyse et traitement des données dans un dictionnaire
        self.dictDonnees = {}
        dictTotaux = {}
        for dateDD, dictGroupes in self.dictOuvertures.iteritems() :
            for IDgroupe, dictUnites in dictGroupes.iteritems() :
                for IDunite, valeurs in dictUnites.iteritems() :
                    annee = dateDD.year
                    mois = dateDD.month
                    
                    if self.dictDonnees.has_key(annee) == False :
                        self.dictDonnees[annee] = {}
                    if self.dictDonnees[annee].has_key(mois) == False :
                        self.dictDonnees[annee][mois] = {}
                    if self.dictDonnees[annee][mois].has_key(IDgroupe) == False :
                        self.dictDonnees[annee][mois][IDgroupe] = {}
                    if self.dictDonnees[annee][mois][IDgroupe].has_key(IDunite) == False :
                        self.dictDonnees[annee][mois][IDgroupe][IDunite] = 0
                    self.dictDonnees[annee][mois][IDgroupe][IDunite] += 1
                    
                    if dictTotaux.has_key(annee) == False :
                        dictTotaux[annee] = {"toutes" : [], "unites" : {} }
                    if dateDD not in dictTotaux[annee]["toutes"] :
                        dictTotaux[annee]["toutes"].append(dateDD)
                    if dictTotaux[annee]["unites"].has_key(IDunite) == False :
                        dictTotaux[annee]["unites"][IDunite] = []
                    if dateDD not in dictTotaux[annee]["unites"][IDunite] :
                        dictTotaux[annee]["unites"][IDunite].append(dateDD)
                    
        # Création des colonnes
        numColonne = 1
        dictColonnes = {}
        for dictUnite in listeUnites :
            IDunite = dictUnite["IDunite"]
            abrege = dictUnite["abrege"]
            self.AddColumn(abrege)
            self.SetColumnWidth(numColonne, 70)
            dictColonnes[IDunite] = numColonne
            numColonne += 1
        
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))

        # Création des branches
        listeAnnees = self.dictDonnees.keys()
        listeAnnees.sort()
        for annee in listeAnnees :
            # Année
            label = _(u"Année %d") % annee
            if dictTotaux.has_key(annee) :
                total = len(dictTotaux[annee]["toutes"])
                if total == 1 :
                    label = _(u"Année %d (1 date)") % annee
                else :
                    label = _(u"Année %d (%d dates)") % (annee, total)

            dictMois = self.dictDonnees[annee]
            branche1 = self.AppendItem(self.root, label)
            self.SetItemBold(branche1, True)
            self.SetItemBackgroundColour(branche1, (220, 220, 220))
            listeMois = dictMois.keys()
            listeMois.sort()
            for mois in listeMois :
                
                # Mois
                dictGroupes = self.dictDonnees[annee][mois]
                listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
                branche2 = self.AppendItem(branche1, listeMois[mois-1])
                
                # tri des groupes
                listeGroupesTemp = []
                for IDgroupe, dictUnites in dictGroupes.iteritems() :
                    ordre = dictNomsGroupes[IDgroupe]["ordre"]
                    listeGroupesTemp.append((ordre, IDgroupe))
                listeGroupesTemp.sort()
                
                for ordre, IDgroupe in listeGroupesTemp :
                    dictUnites = dictGroupes[IDgroupe]

                    # Groupes
                    branche3 = self.AppendItem(branche2, dictNomsGroupes[IDgroupe]["nom"])

                    for IDunite, nbreOuvertures in dictUnites.iteritems() :
                        if dictColonnes.has_key(IDunite) :
                            numColonne = dictColonnes[IDunite]
                            if nbreOuvertures == 1 :
                                texte = _(u"1 date")
                            else:
                                texte = _(u"%s dates") % nbreOuvertures
                            self.SetItemText(branche3, texte, numColonne)
                        
                        # Totaux par année
                        if dictTotaux.has_key(annee) :
                            if dictTotaux[annee]["unites"].has_key(IDunite) :
                                total = len(dictTotaux[annee]["unites"][IDunite])
                                if total == 1 : 
                                    label = _(u"1 date")
                                else :
                                    label = _(u"%d dates") % total
                                self.SetItemText(branche1, label, numColonne)

                    self.Expand(branche3)
                self.Expand(branche2)
                        
            if annee >= datetime.date.today().year :
                self.Expand(branche1)
                
##        self.Expand(self.root)
        
    def MAJ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, 0, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def GetListeDates(self, annee, mois) :
        tmp, nbreJours = calendar.monthrange(annee, mois)
        listeDates = []
        for numJour in range(1, nbreJours+1):
            date = datetime.date(annee, mois, numJour)
            listeDates.append(date)
        return listeDates
        
    def GetListeUnites(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, date_debut, date_fin, ordre
        FROM unites 
        WHERE date_debut<='%s' and date_fin>='%s' and IDactivite=%d
        ORDER BY ordre; """ % (date_fin, date_debut, self.IDactivite)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeUnites = []
        for IDunite, nom, abrege, type, date_debut, date_fin, ordre in listeDonnees :
            dictTemp = { "IDunite" : IDunite, "nom" : nom, "abrege" : abrege, "type" : type, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre }
            listeUnites.append(dictTemp)
        return listeUnites
    
    def GetListeUnitesRemplissage(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDunite_remplissage, nom, abrege, date_debut, date_fin, seuil_alerte
        FROM unites_remplissage
        WHERE date_debut<='%s' and date_fin>='%s' and IDactivite=%d
        ORDER BY ordre; """ % (date_fin, date_debut, self.IDactivite)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeUnites = []
        for IDunite_remplissage, nom, abrege, date_debut, date_fin, seuil_alerte in listeDonnees :
            dictTemp = { "IDunite_remplissage" : IDunite_remplissage, "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin, "seuil_alerte" : seuil_alerte }
            listeUnites.append(dictTemp)
        return listeUnites
    
    def GetDictGroupes(self):
        db = GestionDB.DB()
        req = """SELECT IDgroupe, nom, ordre
        FROM groupes 
        WHERE IDactivite=%d
        ORDER BY ordre; """ % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        dictGroupes = {}
        for IDgroupe, nom, ordre in listeDonnees :
            dictGroupes[IDgroupe] = {"nom":nom, "ordre":ordre}
        dictGroupes[0] = {"nom":_(u"Sans groupe"), "ordre":0}
        return dictGroupes
    
    def GetListeVacances(self):
        db = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

    def GetDictOuvertures(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
            dateDD = DateEngEnDateDD(date)
            dictValeurs = { "IDouverture" : IDouverture, "etat" : True, "initial" : True}
            if self.dictOuvertures.has_key(dateDD) == False :
                self.dictOuvertures[dateDD] = {}
            if self.dictOuvertures[dateDD].has_key(IDgroupe) == False :
                self.dictOuvertures[dateDD][IDgroupe] = {}
            if self.dictOuvertures[dateDD][IDgroupe].has_key(IDunite) == False :
                self.dictOuvertures[dateDD][IDgroupe][IDunite] = {}
            self.dictOuvertures[dateDD][IDgroupe][IDunite] = dictValeurs

    def GetDictRemplissage(self, date_debut, date_fin):
        db = GestionDB.DB()
        req = """SELECT IDremplissage, IDunite_remplissage, IDgroupe, date, places
        FROM remplissage 
        WHERE IDactivite=%d AND date>='%s' AND date<='%s'
        ORDER BY date; """ % (self.IDactivite, date_debut, date_fin)
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        for IDremplissage, IDunite_remplissage, IDgroupe, date, places in listeDonnees :
            dateDD = DateEngEnDateDD(date)
            dictValeurs = { "IDremplissage" : IDremplissage, "places" : places, "initial" : places}
            if self.dictRemplissage.has_key(dateDD) == False :
                self.dictRemplissage[dateDD] = {}
            if self.dictRemplissage[dateDD].has_key(IDgroupe) == False :
                self.dictRemplissage[dateDD][IDgroupe] = {}
            if self.dictRemplissage[dateDD][IDgroupe].has_key(IDunite_remplissage) == False :
                self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = {}
            self.dictRemplissage[dateDD][IDgroupe][IDunite_remplissage] = dictValeurs






# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = Calendrier(panel, IDactivite=1)
        self.myOlv.Initialisation() 
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
