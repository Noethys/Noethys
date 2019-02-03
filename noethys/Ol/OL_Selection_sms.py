#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import GestionDB
import datetime
from Utils import UTILS_Titulaires
from Data import DATA_Civilites as Civilites
from Utils import UTILS_Infos_individus
import copy
from Utils import UTILS_Interface
from Ctrl.CTRL_ObjectListView import FastObjectListView, ColumnDefn, Filter, CTRL_Outils



def FormateStr(valeur=u""):
    try :
        if valeur == None : return u""
        elif type(valeur) == int : return str(valeur)
        elif type(valeur) == float : return str(valeur)
        else : return valeur
    except : 
        return u""


def FormateDate(dateStr):
    if dateStr == "" or dateStr == None : return ""
    date = str(datetime.date(year=int(dateStr[:4]), month=int(dateStr[5:7]), day=int(dateStr[8:10])))
    text = str(date[8:10]) + "/" + str(date[5:7]) + "/" + str(date[:4])
    return text





#-----------INDIVIDUS-----------

class TrackIndividu(object):
    def __init__(self, donnees):
        self.IDindividu = donnees["IDindividu"]
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        self.categorie = donnees["categorie"]
        self.tel = donnees["tel"]
        self.sms = donnees["sms"]



def GetListeIndividus(listview=None):
    DB = GestionDB.DB()
    req = """
    SELECT IDindividu, nom, prenom, travail_tel, travail_tel_sms, tel_domicile, tel_domicile_sms, tel_mobile, tel_mobile_sms
    FROM individus 
    ;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 

    listeListeView = []
    for IDindividu, nom, prenom, travail_tel, travail_tel_sms, tel_domicile, tel_domicile_sms, tel_mobile, tel_mobile_sms in listeDonnees :
        dictTemp = {"IDindividu" : IDindividu, "nom" : nom, "prenom" : prenom}

        if travail_tel != None :
            dictTemp2 = copy.deepcopy(dictTemp)
            dictTemp2["tel"] = travail_tel
            dictTemp2["sms"] = bool(travail_tel_sms)
            dictTemp2["categorie"] = _(u"Professionnel")
            if listview.afficher_uniquement_sms == False or (listview.afficher_uniquement_sms == True and dictTemp2["sms"] == True):
                listeListeView.append(TrackIndividu(dictTemp2))

        if tel_domicile != None :
            dictTemp2 = copy.deepcopy(dictTemp)
            dictTemp2["tel"] = tel_domicile
            dictTemp2["sms"] = bool(tel_domicile_sms)
            dictTemp2["categorie"] = _(u"Domicile")
            if listview.afficher_uniquement_sms == False or (listview.afficher_uniquement_sms == True and dictTemp2["sms"] == True):
                listeListeView.append(TrackIndividu(dictTemp2))

        if tel_mobile != None :
            dictTemp2 = copy.deepcopy(dictTemp)
            dictTemp2["tel"] = tel_mobile
            dictTemp2["sms"] = bool(tel_mobile_sms)
            dictTemp2["categorie"] = _(u"Mobile")
            if listview.afficher_uniquement_sms == False or (listview.afficher_uniquement_sms == True and dictTemp2["sms"] == True):
                listeListeView.append(TrackIndividu(dictTemp2))

    return listeListeView


#-----------FAMILLES-----------

class TrackFamille(object):
    def __init__(self, donnees):
        self.IDfamille = donnees["IDfamille"]
        self.nomTitulaires = donnees["nomTitulaires"]
        self.IDindividu = donnees["IDindividu"]
        self.nom = donnees["nom"]
        self.prenom = donnees["prenom"]
        self.categorie = donnees["categorie"]
        self.tel = donnees["tel"]
        self.sms = donnees["sms"]



def GetListeFamilles(listview=None, listeActivites=None, presents=None, IDfamille=None, infosIndividus=None):
    """ Récupération des infos familles """
    listeListeView = []
    titulaires = UTILS_Titulaires.GetTitulaires(inclure_telephones=True)
    for IDfamille, dictTemp in titulaires.items() :
        nomTitulaires = dictTemp["titulairesSansCivilite"]

        for dictTitulaire in dictTemp["listeTitulaires"] :
            dictTemp = {"IDfamille" : IDfamille, "nomTitulaires" : nomTitulaires, "IDindividu": dictTitulaire["IDindividu"], "nom": dictTitulaire["nom"], "prenom": dictTitulaire["prenom"]}

            dictTelephones = dictTitulaire["telephones"]

            if dictTelephones["travail_tel"] != None:
                dictTemp2 = copy.deepcopy(dictTemp)
                dictTemp2["tel"] = dictTelephones["travail_tel"]
                dictTemp2["sms"] = bool(dictTelephones["travail_tel_sms"])
                dictTemp2["categorie"] = _(u"Professionnel")
                if listview.afficher_uniquement_sms == False or (listview.afficher_uniquement_sms == True and dictTemp2["sms"] == True):
                    listeListeView.append(TrackFamille(dictTemp2))

            if dictTelephones["tel_domicile"] != None:
                dictTemp2 = copy.deepcopy(dictTemp)
                dictTemp2["tel"] = dictTelephones["tel_domicile"]
                dictTemp2["sms"] = bool(dictTelephones["tel_domicile_sms"])
                dictTemp2["categorie"] = _(u"Domicile")
                if listview.afficher_uniquement_sms == False or (listview.afficher_uniquement_sms == True and dictTemp2["sms"] == True):
                    listeListeView.append(TrackFamille(dictTemp2))

            if dictTelephones["tel_mobile"] != None:
                dictTemp2 = copy.deepcopy(dictTemp)
                dictTemp2["tel"] = dictTelephones["tel_mobile"]
                dictTemp2["sms"] = bool(dictTelephones["tel_mobile_sms"])
                dictTemp2["categorie"] = _(u"Mobile")
                if listview.afficher_uniquement_sms == False or (listview.afficher_uniquement_sms == True and dictTemp2["sms"] == True):
                    listeListeView.append(TrackFamille(dictTemp2))

    return listeListeView


#-----------LISTVIEW-----------

class ListView(FastObjectListView):
    def __init__(self, *args, **kwds):
        # Récupération des paramètres perso
        self.categorie = kwds.pop("categorie", "individus")
        self.IDindividu = kwds.pop("IDindividu", None)
        self.IDfamille = kwds.pop("IDfamille", None)
        self.afficher_uniquement_sms = False
        # Initialisation du listCtrl
        self.nom_fichier_liste = __file__
        FastObjectListView.__init__(self, *args, **kwds)
        # Binds perso
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def InitModel(self):
        # Récupération des tracks
        if self.categorie == "individus" :
            self.donnees = GetListeIndividus(self)
        else:
            self.donnees = GetListeFamilles(self)

    def InitObjectListView(self):
        # Couleur en alternance des lignes
        self.oddRowsBackColor = UTILS_Interface.GetValeur("couleur_tres_claire", wx.Colour(240, 251, 237))
        self.evenRowsBackColor = wx.Colour(255, 255, 255)
        self.useExpansionColumn = True

        def FormateSMS(sms):
            if sms == True :
                return _(u"Oui")
            else :
                return _(u"Non")

        if self.categorie == "individus" :
            # INDIVIDUS
            liste_Colonnes = [
                ColumnDefn(u"", "left", 0, "IDindividu", typeDonnee="entier"),
                ColumnDefn(_(u"Nom"), 'left', 140, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Prénom"), "left", 140, "prenom", typeDonnee="texte"),
                ColumnDefn(_(u"Catégorie"), "left", 100, "categorie", typeDonnee="texte"),
                ColumnDefn(_(u"Téléphone"), "left", 100, "tel", typeDonnee="texte"),
                ColumnDefn(_(u"SMS"), "left", 50, "sms", typeDonnee="bool", stringConverter=FormateSMS),
                ]
        
        else:
            # FAMILLES
            liste_Colonnes = [
                ColumnDefn(_(u"ID"), "left", 0, "IDfamille", typeDonnee="entier"),
                ColumnDefn(_(u"Famille"), 'left', 180, "nomTitulaires", typeDonnee="texte"),
                ColumnDefn(_(u"Nom"), 'left', 100, "nom", typeDonnee="texte"),
                ColumnDefn(_(u"Prénom"), "left", 100, "prenom", typeDonnee="texte"),
                ColumnDefn(_(u"Catégorie"), "left", 100, "categorie", typeDonnee="texte"),
                ColumnDefn(_(u"Téléphone"), "left", 100, "tel", typeDonnee="texte"),
                ColumnDefn(_(u"SMS"), "left", 50, "sms", typeDonnee="bool", stringConverter=FormateSMS),
            ]

        self.SetColumns(liste_Colonnes)
        self.CreateCheckStateColumn(0)
        
        if self.categorie == "individus" :
            self.SetEmptyListMsg(_(u"Aucun individu"))
        else:
            self.SetEmptyListMsg(_(u"Aucune famille"))
        self.SetEmptyListMsgFont(wx.FFont(11, wx.DEFAULT, False, "Tekton"))
        self.SetSortColumn(self.columns[2])
        self.SetObjects(self.donnees)
       
    def MAJ(self, categorie=None):
        if categorie != None :
            if categorie =="individu" : self.categorie = "individus"
            if categorie =="famille" : self.categorie = "familles"
        self.InitModel()
        self.InitObjectListView()

    def Selection(self):
        return self.GetSelectedObjects()
    
    def GetTracksCoches(self):
        return self.GetCheckedObjects()

    def SetIDcoches(self, listeID=[]):
        for track in self.donnees :
            if self.categorie == "individus" :
                ID = track.IDindividu
            else :
                ID = track.IDfamille
            if ID in listeID :
                self.Check(track)
                self.RefreshObject(track)

    def OnCheck(self, track):
        self.GetParent().OnCheck(track)

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """            
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()
        
        # Génération automatique des fonctions standards
        self.GenerationContextMenu(menuPop, dictParametres=self.GetParametresImpression())

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def GetParametresImpression(self):
        dictParametres = {
            "titre" : _(u"Liste des %s") % self.categorie,
            "total" : _(u"> %s %s") % (len(self.donnees), self.categorie),
            "orientation" : wx.PORTRAIT,
            }
        return dictParametres



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl_listview = ListView(panel, id=-1, categorie="familles", name="OL_test", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_recherche = CTRL_Outils(panel, listview=self.ctrl_listview, afficherCocher=True)

        self.ctrl_listview.MAJ()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl_listview, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.ctrl_recherche, 0, wx.ALL, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
