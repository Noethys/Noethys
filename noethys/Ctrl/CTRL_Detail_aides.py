#!/usr/bin/env python
# -*- coding: utf8 -*-
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

from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import GestionDB
from Ol import OL_Detail_aides


DICT_INDIVIDUS = {}


            
def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
def PeriodeComplete(mois, annee):
    listeMois = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))
    periodeComplete = u"%s %d" % (listeMois[mois-1], annee)
    return periodeComplete




class Track(object):
    def __init__(self, donnees):
        self.IDaide = donnees[0]
        self.IDfamille = donnees[1]
        self.IDactivite = donnees[2]
        self.nom_activite = donnees[3]
        self.nom = donnees[4]
        self.date_debut = DateEngEnDateDD(donnees[5])
        self.date_fin = DateEngEnDateDD(donnees[6])
        self.date_debut_str = DateEngFr(donnees[5])
        self.date_fin_str = DateEngFr(donnees[6])
        self.periodeComplete = _(u"Du %s au %s") % (self.date_debut_str, self.date_fin_str)
        self.IDcaisse = donnees[7]
        self.nom_caisse = donnees[8]
        if self.nom_caisse == None :
            self.nom_caisse = u""
        self.montant_max = donnees[9]
        self.nbre_dates_max = donnees[10]
        self.total_deductions = donnees[11]
        self.nbre_deductions = donnees[12]
        
        if self.total_deductions == None : self.total_deductions = 0.0
        if self.nbre_deductions == None : self.nbre_deductions = 0
        
        if self.montant_max != None :
            self.texte_montant_max = _(u"%.2f %s (%.2f %s max)") % (self.total_deductions, SYMBOLE, self.montant_max, SYMBOLE)
        else:
            self.texte_montant_max = u"%.2f %s" % (self.total_deductions, SYMBOLE)
            
        if self.nbre_dates_max != None :
            self.texte_dates_max = _(u"%d dates (%d dates max)") % (self.nbre_deductions, self.nbre_dates_max)
        else:
            self.texte_dates_max = _(u"%d dates") % self.nbre_deductions
        
        # Encore valide ?
        dateJour = datetime.date.today()
        if self.date_debut <= dateJour and self.date_fin >= dateJour :
            self.valide = True
        else:
            self.valide = False
        
        # Noms des bénéficiaires
        self.texteBeneficiaires = u""
        if self.IDaide in DICT_INDIVIDUS :
            for IDindividu, nom, prenom in DICT_INDIVIDUS[self.IDaide] :
                self.texteBeneficiaires += u"%s, " % prenom
            if len(DICT_INDIVIDUS[self.IDaide]) > 0 :
                self.texteBeneficiaires = self.texteBeneficiaires[:-2]


            
class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, IDfamille=None): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.IDfamille = IDfamille
        self.listeTracks = []
        
        # Recherche du IDcompte_payeur
        DB = GestionDB.DB()
        req = """SELECT IDcompte_payeur
        FROM familles
        WHERE IDfamille=%d
        """ % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        self.IDcompte_payeur = listeDonnees[0][0]

        # Création des colonnes
        listeColonnes = [
            ( _(u"Période de validité"), 180, wx.ALIGN_LEFT),
            ( _(u"Nom"), 130, wx.ALIGN_LEFT),
            ( _(u"Activité"), 70, wx.ALIGN_LEFT),
            ( _(u"Caisse"), 100, wx.ALIGN_LEFT),
            ( _(u"Bénéficiaires"), 120, wx.ALIGN_LEFT),
            ( _(u"Total des déductions"), 150, wx.ALIGN_LEFT),
            ( _(u"Nbre de dates"), 130, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        self.SetBackgroundColour(wx.WHITE)
        if 'phoenix' in wx.PlatformInfo:
            TR_COLUMN_LINES = HTL.TR_COLUMN_LINES
        else :
            TR_COLUMN_LINES = wx.TR_COLUMN_LINES
        self.SetAGWWindowStyleFlag(wx.TR_ROW_LINES |  TR_COLUMN_LINES |wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT ) # HTL.TR_NO_HEADER
        self.EnableSelectionVista(True)
                    
    def Importation(self):
        """ Récupération des données """
        global DICT_INDIVIDUS
        listeID = None
        criteresAides = ""
        if self.IDfamille == None :
            criteresAides = "WHERE aides.IDfamille IS NULL"
        else:
##            criteresAides = "WHERE aides.IDfamille IS NOT NULL"
            criteresAides = "WHERE aides.IDfamille=%d" % self.IDfamille
        db = GestionDB.DB()
        req = """SELECT 
        aides.IDaide, aides.IDfamille, 
        aides.IDactivite, activites.abrege, 
        aides.nom, aides.date_debut, aides.date_fin, 
        aides.IDcaisse, caisses.nom,
        aides.montant_max, aides.nbre_dates_max,
        SUM(deductions.montant) as total_deductions,
        COUNT(deductions.IDdeduction) as nbre_deductions
        FROM aides
        LEFT JOIN activites ON activites.IDactivite = aides.IDactivite
        LEFT JOIN caisses ON caisses.IDcaisse = aides.IDcaisse
        LEFT JOIN deductions ON deductions.IDaide = aides.IDaide
        %s
        GROUP BY aides.IDaide
        ORDER BY aides.date_debut
        ;""" % criteresAides
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        
        # Récupération des noms des bénéficiaires
        req = """SELECT 
        aides_beneficiaires.IDaide_beneficiaire, aides_beneficiaires.IDaide, aides_beneficiaires.IDindividu,
        individus.nom, individus.prenom
        FROM aides_beneficiaires
        LEFT JOIN aides ON aides.IDaide = aides_beneficiaires.IDaide
        LEFT JOIN individus ON individus.IDindividu = aides_beneficiaires.IDindividu
        """
        db.ExecuterReq(req)
        listeNoms = db.ResultatReq()
        db.Close()
        
        dictNoms = {}
        for IDaide_beneficiaire, IDaide, IDindividu, nom, prenom in listeNoms :
            if (IDaide in dictNoms) == False :
                dictNoms[IDaide] = [] 
            if IDindividu not in dictNoms[IDaide] :
                dictNoms[IDaide].append((IDindividu, nom, prenom))
        DICT_INDIVIDUS = dictNoms
        
        listeListeView = []
        for item in listeDonnees :
            track = Track(item)
            listeListeView.append(track)
            
        return listeListeView


    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
##        self.Freeze()
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()
##        self.Thaw() 

    def Remplissage(self):
        listeTracks = self.Importation() 
        
        # Création des branches
        for track in listeTracks :
            
            # Niveau 1
            regroupement = self.AppendItem(self.root, track.periodeComplete) 
            self.SetPyData(regroupement, track.IDaide)
##            self.SetItemBold(regroupement, True)
##            self.SetItemBackgroundColour(regroupement, COULEUR_FOND_REGROUPEMENT)
            
            self.SetItemText(regroupement, track.nom, 1)
            self.SetItemText(regroupement, track.nom_activite, 2)
            self.SetItemText(regroupement, track.nom_caisse, 3)
            self.SetItemText(regroupement, track.texteBeneficiaires, 4)
            self.SetItemText(regroupement, track.texte_montant_max, 5)
            self.SetItemText(regroupement, track.texte_dates_max, 6)
            
            # Niveau 2
            deductions = self.AppendItem(regroupement, "")
            self.SetPyData(deductions, track.IDaide)
            
            # Liste des prestations
            ctrl_deductions = OL_Detail_aides.ListView(self.GetMainWindow(), -1, IDaide=track.IDaide, modificationsVirtuelles=False, size=(-1, -1), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            ctrl_deductions.MAJ() 
            largeur = 840
            hauteur = 30 + len(ctrl_deductions.donnees) * 18
            ctrl_deductions.SetSize((largeur, hauteur))
            self.SetItemWindow(deductions, ctrl_deductions, 0)
            track.ctrl_deductions = ctrl_deductions
                        
##        self.ExpandAllChildren(self.root)
        
        # Pour éviter le bus de positionnement des contrôles
        self.GetMainWindow().CalculatePositions() 
        
        self.listeTracks = listeTracks
            

    
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
    



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        
        self.myOlv = CTRL(panel, IDfamille=7)
        self.myOlv.MAJ() 
        
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
