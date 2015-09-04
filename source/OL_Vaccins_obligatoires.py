#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import CTRL_Saisie_date
import GestionDB
import calendar
from dateutil import relativedelta

from ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils

try: import psyco; psyco.full()
except: pass


def FormatDuree(duree):
    posM = duree.find("m")
    posA = duree.find("a")
    jours = int(duree[1:posM-1])
    mois = int(duree[posM+1:posA-1])
    annees = int(duree[posA+1:])
    return jours, mois, annees

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def CalcValidite(date_vaccin, duree_validite):
    jours, mois, annees = FormatDuree(duree_validite)
    
    if jours==0 and mois==0 and annees==0:
        # Si illimité
        dateFin = datetime.date(2999, 1, 1)
        return str(dateFin), None
    else:
        # Calcul de la date de fin de validité
        dateFin = date_vaccin
        if jours != 0 : dateFin = dateFin + relativedelta.relativedelta(days=+jours)
        if mois != 0 : dateFin = dateFin + relativedelta.relativedelta(months=+mois)
        if annees != 0 : dateFin = dateFin + relativedelta.relativedelta(years=+annees)
    
    # Calcule le nbre de jours restants
    nbreJours = (dateFin - datetime.date.today()).days
    
    return str(dateFin), nbreJours


def GetListeEtatsMaladies(IDindividu):
    # Récupère la liste des maladies dont le vaccin est obligatoire
    db = GestionDB.DB()
    req = """
    SELECT nom, IDtype_maladie
    FROM types_maladies
    WHERE vaccin_obligatoire=1
    ORDER BY nom;
    """
    db.ExecuterReq(req)
    listeMaladies = db.ResultatReq()
    
    # Récupère la liste des vaccins de l'individu
    req = """
    SELECT 
    vaccins.IDvaccin, vaccins.IDtype_vaccin, vaccins.date, vaccins_maladies.IDtype_maladie, 
    types_vaccins.nom, types_vaccins.duree_validite,
    types_maladies.nom, types_maladies.vaccin_obligatoire
    FROM vaccins 
    LEFT JOIN vaccins_maladies ON vaccins.IDtype_vaccin = vaccins_maladies.IDtype_vaccin
    LEFT JOIN types_vaccins ON vaccins.IDtype_vaccin = types_vaccins.IDtype_vaccin
    LEFT JOIN types_maladies ON vaccins_maladies.IDtype_maladie = types_maladies.IDtype_maladie
    WHERE vaccins.IDindividu=%d AND types_maladies.vaccin_obligatoire=1;
    """ % IDindividu
    db.ExecuterReq(req)
    listeVaccins = db.ResultatReq()
    db.Close()
    
    dictMaladiesIndividus = {}
    for IDvaccin, IDtype_vaccin, date, IDtype_maladie, nomVaccin, duree_validite, nomMaladie, vaccin_obligatoire in listeVaccins :
        dateDD = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))
        dateFinValidite, nbreJoursRestants = CalcValidite(dateDD, duree_validite)
        if dictMaladiesIndividus.has_key(IDtype_maladie) :
            if dictMaladiesIndividus[IDtype_maladie] < nbreJoursRestants :
                dictMaladiesIndividus[IDtype_maladie] = nbreJoursRestants
        else:
            dictMaladiesIndividus[IDtype_maladie] = nbreJoursRestants
    
    listeMaladiesFinal = []
    for nom, IDtype_maladie in listeMaladies :
        if dictMaladiesIndividus.has_key(IDtype_maladie) :
            if dictMaladiesIndividus[IDtype_maladie] <= 0 :
                etat = "pasok"
            elif dictMaladiesIndividus[IDtype_maladie] > 0 and dictMaladiesIndividus[IDtype_maladie] <= 15 :
                etat = "attention"
            else:
                etat = "ok"
        else:
            etat = "pasok"
        # Ajout à la liste finale
        listeMaladiesFinal.append((nom, IDtype_maladie, etat))
    
    return listeMaladiesFinal
            
            

class Track(object):
    def __init__(self, donnees):
        self.nom = donnees[0]
        self.IDtype_maladie = donnees[1]
        self.etat = donnees[2]
        
    
class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.IDindividu = kwds.pop("IDindividu", None)
        self.selectionID = None
        self.selectionTrack = None
        self.criteres = ""
        self.itemSelected = False
        self.popupIndex = -1
        self.listeFiltres = []
        # Initialisation du listCtrl
        FastObjectListView.__init__(self, *args, **kwds)
        
    def InitModel(self):
        self.donnees = self.GetTracks()

    def GetTracks(self):
        """ Récupération des données """
        listeID = None
        
        listeDonnees = GetListeEtatsMaladies(self.IDindividu)

        listeListeView = []
        for item in listeDonnees :
            valide = True
            if listeID != None :
                if item[0] not in listeID :
                    valide = False
            if valide == True :
                track = Track(item)
                listeListeView.append(track)
                if self.selectionID == item[0] :
                    self.selectionTrack = track
        return listeListeView
        
        
    def InitObjectListView(self):            
        # Couleur en alternance des lignes
        self.oddRowsBackColor = "#F0FBED"
        self.evenRowsBackColor = "#F0FBED"
        self.useExpansionColumn = True
        
        # ListImages
        self.AddNamedImages("pasok", wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("attention", wx.Bitmap("Images/16x16/Attention.png", wx.BITMAP_TYPE_PNG))
        self.AddNamedImages("ok", wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        
        def GetImage(track):
            return track.etat
        
        liste_Colonnes = [
            ColumnDefn(_(u"ID"), "left", 23, "IDvaccin", imageGetter=GetImage),
            ColumnDefn(_(u"Nom du vaccin"), 'left', 100, "nom"),
            ]
        
        self.SetColumns(liste_Colonnes)
        self.SetEmptyListMsg(_(u"Aucune maladie"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, face="Tekton"))
        self.SetSortColumn(self.columns[1])
        self.SetObjects(self.donnees)
       
    def MAJ(self, ID=None):
        if ID != None :
            self.selectionID = ID
            self.selectionTrack = None
        else:
            self.selectionID = None
            self.selectionTrack = None
        self.InitModel()
        self.InitObjectListView()
        # Sélection d'un item
        if self.selectionTrack != None :
            self.SelectObject(self.selectionTrack, deselectOthers=True, ensureVisible=True)
        self.selectionID = None
        self.selectionTrack = None
    


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.myOlv = ListView(panel, IDindividu=46, id=-1, name="OL_test", style=wx.LC_NO_HEADER|wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
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
    
##    for x in range(100000) :
##        for mois in range(1, 12) :
##            date = datetime.date(2007, 1, 1)
##            date +=  datetime.timedelta(days=1)
##            dateAnnee = date.year
##            dateMois = date.month
##            dateJour = date.day
##            dateMois = dateMois + mois
##            if dateMois > 12:
##                division = divmod(dateMois, 12)
##                dateAnnee = dateAnnee + division[0]
##                dateMois = division[1]
##            dateFin = datetime.date(dateAnnee, dateMois, dateJour)
##            dateJour, dateMois, dateAnnee = dateFin.day, dateFin.month, dateFin.year

