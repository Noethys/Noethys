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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import datetime

import GestionDB
import CTRL_Saisie_euros
from Ol import OL_Prestations_repartition

try: import psyco; psyco.full()
except: pass

COULEUR_FOND_REGROUPEMENT = (200, 200, 200)
COULEUR_TEXTE_REGROUPEMENT = (140, 140, 140)

COULEUR_NUL = (255, 0, 0)
COULEUR_PARTIEL = (255, 193, 37)
COULEUR_TOTAL = (0, 238, 0)
        
        
            
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
        self.IDreglement = donnees[0]
        self.compte_payeur = donnees[1]
        self.date = DateEngEnDateDD(donnees[2])
        self.dateComplete = DateComplete(self.date)
        self.IDmode = donnees[3]
        self.nom_mode = donnees[4]
        self.IDemetteur = donnees[5]
        self.nom_emetteur = donnees[6]
        if self.nom_emetteur == None :
            self.nom_emetteur = u""
        self.numero_piece = donnees[7]
        if self.numero_piece == None :
            self.numero_piece = u""
        self.montant = donnees[8]
        self.montant_str = u"%.2f € " % self.montant
        self.IDpayeur = donnees[9]
        self.nom_payeur = donnees[10]
        self.observations = donnees[11]
        self.numero_quittancier = donnees[12]
        self.IDprestation_frais = donnees[13]
        self.IDcompte = donnees[14]
        self.date_differe = donnees[15]
        if self.date_differe != None :
            self.date_differe = DateEngEnDateDD(self.date_differe)
        self.encaissement_attente = donnees[16]
        self.IDdepot = donnees[17]
        self.date_depot = donnees[18]
        if self.date_depot != None :
            self.date_depot = DateEngEnDateDD(self.date_depot)
            self.date_depot_str = DateEngFr(donnees[18])
        else:
            self.date_depot_str = u""
        self.nom_depot = donnees[19]
        self.verrouillage_depot = donnees[20]
        self.date_saisie = donnees[21]
        if self.date_saisie != None :
            self.date_saisie = DateEngEnDateDD(self.date_saisie)
        self.IDutilisateur = donnees[22]
        self.montant_ventilation = donnees[23]
        if self.montant_ventilation == None :
            self.montant_ventilation = 0.0
        self.montant_ventilation_str = u"%.2f € " % self.montant_ventilation
    
    def GetImageVentilation(self):
        if self.montant_ventilation == None :
            return "vert"
        resteAVentiler = self.montant - self.montant_ventilation
        if resteAVentiler == 0.0 :
            return "vert"
        if resteAVentiler > 0.0 :
            return "orange"
        if resteAVentiler < 0.0 :
            return "rouge"
    
    def GetImageDepot(self):
        if self.IDdepot == None :
            if self.encaissement_attente == 1 :
                return "attente"
            else:
                return "non"
        else:
            return "ok"


            
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
            ( _(u"Date"), 180, wx.ALIGN_LEFT),
            ( _(u"Mode"), 130, wx.ALIGN_LEFT),
            ( _(u"Emetteur"), 130, wx.ALIGN_LEFT),
            ( _(u"Numéro"), 70, wx.ALIGN_LEFT),
            ( _(u"Payeur"), 100, wx.ALIGN_LEFT),
            ( _(u"Montant"), 70, wx.ALIGN_LEFT),
            ( _(u"Ventilé"), 80, wx.ALIGN_LEFT),
            ( _(u"Dépôt"), 100, wx.ALIGN_LEFT),
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
        listeID = None
        db = GestionDB.DB()
        req = """SELECT 
        reglements.IDreglement, reglements.IDcompte_payeur, reglements.date, 
        reglements.IDmode, modes_reglements.label, 
        reglements.IDemetteur, emetteurs.nom, 
        reglements.numero_piece, reglements.montant, 
        payeurs.IDpayeur, payeurs.nom, 
        reglements.observations, numero_quittancier, IDprestation_frais, reglements.IDcompte, date_differe, 
        encaissement_attente, 
        reglements.IDdepot, depots.date, depots.nom, depots.verrouillage, 
        date_saisie, IDutilisateur,
        SUM(ventilation.montant) AS total_ventilation
        FROM reglements
        LEFT JOIN ventilation ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN modes_reglements ON reglements.IDmode=modes_reglements.IDmode
        LEFT JOIN emetteurs ON reglements.IDemetteur=emetteurs.IDemetteur
        LEFT JOIN payeurs ON reglements.IDpayeur=payeurs.IDpayeur
        LEFT JOIN depots ON reglements.IDdepot=depots.IDdepot
        WHERE reglements.IDcompte_payeur=%d
        GROUP BY reglements.IDreglement
        ORDER BY reglements.date;
        """ % self.IDcompte_payeur
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        
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
        
        il = wx.ImageList(16, 16)
        self.imgVert = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_vert.png"), wx.BITMAP_TYPE_PNG))
        self.imgRouge = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_rouge.png"), wx.BITMAP_TYPE_PNG))
        self.imgOrange = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ventilation_orange.png"), wx.BITMAP_TYPE_PNG))
        self.imgAttente = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Attente.png"), wx.BITMAP_TYPE_PNG))
        self.imgOk = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG))
        self.imgNon = il.Add(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)
        
        # Création des branches
        for track in listeTracks :
            
            # Niveau 1
            regroupement = self.AppendItem(self.root, track.dateComplete)
            self.SetPyData(regroupement, None)
##            self.SetItemBold(regroupement, True)
##            self.SetItemBackgroundColour(regroupement, COULEUR_FOND_REGROUPEMENT)
            
            self.SetItemText(regroupement, track.nom_mode, 1)
            self.SetItemText(regroupement, track.nom_emetteur, 2)
            self.SetItemText(regroupement, track.numero_piece, 3)
            self.SetItemText(regroupement, track.nom_payeur, 4)
            self.SetItemText(regroupement, track.montant_str, 5)
            self.SetItemText(regroupement, track.montant_ventilation_str, 6)
            self.SetItemText(regroupement, track.date_depot_str, 7)
            
            imageVentilation = track.GetImageVentilation()
            if imageVentilation == "vert" : regroupement.SetImage(6, self.imgVert, which=wx.TreeItemIcon_Normal)
            if imageVentilation == "orange" : regroupement.SetImage(6, self.imgOrange, which=wx.TreeItemIcon_Normal)
            if imageVentilation == "rouge" : regroupement.SetImage(6, self.imgRouge, which=wx.TreeItemIcon_Normal)
            
            imageDepot = track.GetImageDepot() 
            if imageDepot == "ok" : regroupement.SetImage(7, self.imgOk, which=wx.TreeItemIcon_Normal)
            if imageDepot == "attente" : regroupement.SetImage(7, self.imgAttente, which=wx.TreeItemIcon_Normal)
            if imageDepot == "non" : regroupement.SetImage(7, self.imgNon, which=wx.TreeItemIcon_Normal)

            # Niveau 2
            prestations = self.AppendItem(regroupement, "")
            self.SetPyData(prestations, track.IDreglement)
            
            # Liste des prestations
            ctrl_prestations = OL_Prestations_repartition.ListView(self.GetMainWindow(), -1, IDfamille=self.IDfamille, size=(-1, -1), style=wx.LC_REPORT|wx.SUNKEN_BORDER)
            ctrl_prestations.SetFiltre("ventilation.IDreglement", track.IDreglement)
            largeur = 840
            hauteur = 35 + len(ctrl_prestations.donnees) * 18
            ctrl_prestations.SetSize((largeur, hauteur))
            self.SetItemWindow(prestations, ctrl_prestations, 0)
            track.ctrl_prestations = ctrl_prestations
                        
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
        
        self.myOlv = CTRL(panel, IDfamille=84)
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
