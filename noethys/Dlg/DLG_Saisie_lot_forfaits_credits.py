#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import decimal

from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date

import GestionDB
from Ol import OL_Saisie_lot_forfaits_credits
from Utils import UTILS_Identification
from Utils import UTILS_Dates
from Utils import UTILS_Gestion
from Utils import UTILS_Config
SYMBOLE = UTILS_Config.GetParametre("monnaie_symbole", u"€")

import DLG_Badgeage_grille
from threading import Thread 
import time

from Ctrl import CTRL_Ultrachoice



def ConvertStrToListe(texte=None):
    """ Convertit un texte "1;2;3;4" en [1, 2, 3, 4] """
    if texte == None :
        return None
    listeResultats = []
    temp = texte.split(";")
    for ID in temp :
        listeResultats.append(int(ID))
    return listeResultats


class CTRL_Forfait(CTRL_Ultrachoice.CTRL):
    def __init__(self, parent, donnees=[]):
        CTRL_Ultrachoice.CTRL.__init__(self, parent, donnees) 
        self.parent = parent
        self.IDactivite = None
        self.listeTarifs= []
        self.MAJ() 
##        if len(self.listeTarifs) > 0 :
##            self.SetSelection2(0)
    
    def SetActivite(self, IDactivite=None):
        self.IDactivite = IDactivite
        
    def Importation(self):
        if self.IDactivite == None :
            return []
        
        DB = GestionDB.DB()
        
        # Recherche des catégories de tarifs
        dictCategoriesTarifs = {}
        req = """SELECT IDcategorie_tarif, nom
        FROM categories_tarifs;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDcategorie_tarif, nom in listeDonnees :
            dictCategoriesTarifs[IDcategorie_tarif] = nom

        # Recherche les tarifs
        dictIndividus = {}
        req = """SELECT IDtarif, tarifs.IDactivite, 
        tarifs.IDnom_tarif, noms_tarifs.nom, 
        date_debut, date_fin, methode, categories_tarifs, groupes, description
        FROM tarifs
        LEFT JOIN noms_tarifs ON tarifs.IDnom_tarif = noms_tarifs.IDnom_tarif
        WHERE type='CREDIT' AND forfait_beneficiaire='individu' AND tarifs.IDactivite=%d
        ORDER BY noms_tarifs.nom, date_debut;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeTarifs = []
        for IDtarif, IDactivite, IDnom_tarif, nomTarif, date_debut, date_fin, methode, categories_tarifs, groupes, description in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
            listeCategoriesTarifs = ConvertStrToListe(categories_tarifs)
            listeNomsCategories = []
            for IDcategorie_tarif in listeCategoriesTarifs :
                nomCategorieTarif = _(u"Categorie de tarif inconnue")
                if dictCategoriesTarifs.has_key(IDcategorie_tarif) :
                    nomCategorieTarif = dictCategoriesTarifs[IDcategorie_tarif]
                listeNomsCategories.append(nomCategorieTarif)
            
            dictTemp = {
                    "IDtarif" : IDtarif, "IDactivite" : IDactivite, 
                    "IDnom_tarif" : IDnom_tarif, "nomTarif" : nomTarif, "date_debut" : date_debut,
                    "date_fin" : date_fin, "methode" : methode, "categories_tarifs":categories_tarifs, "groupes":groupes,
                    "listeNomsCategories" : listeNomsCategories, "nomPrecisTarif":description, "listeCategoriesTarifs" : listeCategoriesTarifs,
                    }
            
            listeTarifs.append(dictTemp)
            
        return listeTarifs
    
    def MAJ(self):
        selectionActuelle = None#self.GetID()
        self.listeTarifs = self.Importation() 
        listeItems = []
        for dictTarif in self.listeTarifs :
            IDtarif = dictTarif["IDtarif"]
            nom = dictTarif["nomTarif"]
            date_debut = dictTarif["date_debut"]
            date_fin = dictTarif["date_fin"]
            if date_debut == None and date_fin == None : label = _(u"%s (Sans période de validité)") % nom
            if date_debut == None and date_fin != None : label = _(u"%s (Jusqu'au %s)") % (nom, UTILS_Dates.DateDDEnFr(date_fin))
            if date_debut != None and date_fin == None : label = _(u"%s (A partir du %s)") % (nom, UTILS_Dates.DateDDEnFr(date_debut))
            if date_debut != None and date_fin != None : label = _(u"%s (Du %s au %s)") % (nom, UTILS_Dates.DateDDEnFr(date_debut), UTILS_Dates.DateDDEnFr(date_fin))
            
            if len(dictTarif["nomPrecisTarif"]) > 0 :
                description = dictTarif["nomPrecisTarif"] + " --- " + " ou ".join(dictTarif["listeNomsCategories"])
            else :
                description = " ou ".join(dictTarif["listeNomsCategories"])
            listeItems.append({"label" : label, "description" : description})
        self.SetDonnees(listeItems)
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
            if selectionActuelle != None :
                self.SetID(selectionActuelle)
            else :
                self.SetSelection2(0)
        
    def SetID(self, ID=None):
        index = 0
        for dictTarif in self.listeTarifs :
            IDtarif = dictTarif["IDtarif"]
            if IDtarif == ID :
                 self.SetSelection2(index)
            index += 1

    def GetID(self):
        index = self.GetSelection2()
        if index == -1 or index == None : return None
        print index, len(self.listeTarifs)
        return self.listeTarifs[index]["IDtarif"]
    
    def GetDictTarif(self):
        index = self.GetSelection2()
        if index == -1 or len(self.listeTarifs) == 0 : return None
        return self.listeTarifs[index]

# ------------------------------------------------------------------------------------------------------------------------------------------



class Abort(Exception): 
    pass 

class Traitement(Thread): 
    def __init__(self, parent, IDactivite=None, dictTarif={}, date_debut=None, date_fin=None, tracks=[]): 
        Thread.__init__(self) 
        self.parent = parent
        self.IDactivite = IDactivite
        self.dictTarif = dictTarif
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.tracks = tracks
        self.succes = False
        self.stop = False 
        self.index = 0
        self.parent.ctrl_gauge.SetRange(len(self.tracks))
        self.parent.ctrl_gauge.SetValue(0)

    def run(self): 
        try: 
            
            listeAnomalies = []
            for track in self.tracks :
                
                # Affichage
                texte = u"[%d/%d] %s..." % (self.index+1, len(self.tracks), track.nomCompletIndividu)
                self.parent.EcritLog(texte) 
                self.parent.ctrl_gauge.SetValue(self.index+1)
                                    
                # Initialisation de la grille
                self.parent.ctrl_grille.InitGrille(IDindividu=track.IDindividu, IDfamille=track.IDfamille, IDactivite=self.IDactivite, periode=(self.date_debut, self.date_fin))
                time.sleep(0.2)
                
                # Saisie du forfait
                grille = self.parent.ctrl_grille.grille
                
                dictTarifsDisponibles = grille.GetTarifsForfaitsCreditDisponibles(self.date_debut)
                listeTarifs = dictTarifsDisponibles[track.IDfamille]["individus"][track.IDindividu]["forfaits"]
                dictTarif = {}
                for dictTarifTemp in listeTarifs :
                    if dictTarifTemp["IDtarif"] == self.dictTarif["IDtarif"] :
                        dictTarif = dictTarifTemp
                
                if len(dictTarif) > 0 :
                    
                    # Recherche date de facturation du forfait
                    date_facturation_tarif = dictTarif["date_facturation"]
                    if date_facturation_tarif == "date_debut_forfait" : 
                        date_facturation = self.date_debut
                    elif date_facturation_tarif == "date_saisie" : 
                        date_facturation = datetime.date.today()
                    elif date_facturation_tarif != None and date_facturation_tarif.startswith("date:") : 
                        date_facturation = UTILS_Dates.DateEngEnDateDD(date_facturation_tarif[5:])
                    else :
                        date_facturation = self.date_debut
                    
                    # Mémorisation de la prestation
                    IDprestation = grille.MemorisePrestation(track.IDcompte_payeur, date_facturation, self.IDactivite, dictTarif["IDtarif"], self.dictTarif["nomTarif"], 
                                                                                    dictTarif["resultat"]["montant_tarif"], dictTarif["resultat"]["montant_tarif"], track.IDfamille, track.IDindividu, 
                                                                                    listeDeductions=[], temps_facture=dictTarif["resultat"]["temps_facture"], IDcategorie_tarif=dictTarif["resultat"]["IDcategorie_tarif"],
                                                                                    forfait_date_debut=self.date_debut, forfait_date_fin=self.date_fin)
                    
                    # Affichage dans la liste des forfaits
                    dictTemp = grille.dictPrestations[IDprestation].copy()
                    dictTemp["forfait_date_debut"] = self.date_debut
                    dictTemp["forfait_date_fin"] = self.date_fin
                    dictTemp["couleur"] = grille.CreationCouleurForfait(index=len(grille.dictForfaits))
                    grille.dictForfaits[IDprestation] = dictTemp

                    # Recalcul des prestations
                    self.parent.ctrl_grille.RecalculerToutesPrestations() 
                    time.sleep(0.2)
                    
                    # Sauvegarde de la grille des conso + Ecrit log
                    self.parent.ctrl_grille.Sauvegarde()
                    self.parent.SetStatutTrack(track, "ok")
                
                else :
                    
                    # Si aucun tarif trouvé :
                    self.parent.EcritLog(u"Erreur : Aucun tarif valide trouvé pour %s" % track.nomCompletIndividu)
                    self.parent.SetStatutTrack(track, "erreur")
                
                # Arrête le traitement si bouton arrêter enfoncé
                if self.stop: 
                    raise Abort
                
                time.sleep(0.2)
                self.index += 1
            
            # Si fin 
            self.succes = True
            raise Abort
        
        except Abort, KeyBoardInterrupt: 
            if self.succes == True :
                self.parent.EcritLog(_(u"Traitement terminé")) 
                self.parent.Arreter(forcer=True) 

            self.parent.bouton_ok.SetImageEtTexte(cheminImage="Images/32x32/Valider.png", texte=u"Commencer")
            self.parent.bouton_fermer.Enable(True)
            self.parent.Layout()
            
        except Exception, err : 
            self.parent.EcritLog("Erreur : " + str(err))
            self.stop = True 
            self.parent.bouton_ok.SetImageEtTexte(cheminImage="Images/32x32/Valider.png", texte=u"Commencer")
            self.parent.bouton_fermer.Enable(True)
            self.parent.Layout()
            raise 
        
    def abort(self): 
        self.stop = True


# ----------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Activite(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom, abrege
        FROM activites
        ORDER BY date_fin DESC;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDactivite, nom, abrege in listeDonnees :
            if nom == None : nom = u"Activité inconnue"
            self.dictDonnees[index] = {"ID" : IDactivite, "nom" : nom, "abrege" : abrege}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetInfos(self):
        """ Récupère les infos sur le compte sélectionné """
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]
        

# -----------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent   

        # Bandeau
        titre = _(u"Saisir un lot de forfaits-crédits")
        intro = _(u"Vous pouvez ici saisir des forfaits-crédits individuels pour un ensemble d'individus. Sélectionnez une activité, le forfait-crédit à appliquer puis la période à impacter. Cochez les individus souhaités puis cliquez sur le bouton Commencer pour lancer le traitement.")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        
        # Paramètres
        self.box_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres du forfait"))
        self.label_periode = wx.StaticText(self, -1, u"Période :")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, "au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        self.label_activite = wx.StaticText(self, -1, u"Activité :")
        self.ctrl_activite = CTRL_Activite(self)

        self.label_forfait = wx.StaticText(self, -1, u"Forfait :")
        self.ctrl_forfait = CTRL_Forfait(self)

        self.bouton_actualiser = wx.Button(self, -1, _(u"Actualiser la liste"))
        
        # Individus
        self.box_individus_staticbox = wx.StaticBox(self, -1, _(u"Sélection des individus"))
        self.listviewAvecFooter = OL_Saisie_lot_forfaits_credits.ListviewAvecFooter(self, kwargs={}) 
        self.ctrl_individus = self.listviewAvecFooter.GetListview()
        self.ctrl_recherche = OL_Saisie_lot_forfaits_credits.CTRL_Outils(self, listview=self.ctrl_individus, afficherCocher=True)

        # Grille des conso
        self.box_grille_staticbox = wx.StaticBox(self, -1, _(u"Journal"))
        self.ctrl_log = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.ctrl_log.SetMinSize((-1, 60))
        self.ctrl_gauge = wx.Gauge(self, -1, style=wx.GA_SMOOTH)
        self.ctrl_grille = DLG_Badgeage_grille.CTRL(self)
        self.ctrl_grille.Show(False)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Commencer"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixActivite, self.ctrl_activite)
        self.Bind(wx.EVT_COMBOBOX, self.OnChoixForfait, self.ctrl_forfait)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        
        self.ctrl_individus.MAJ() 
        wx.CallLater(0, self.Layout)

    def __set_properties(self):
        self.ctrl_activite.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'activité pour laquelle vous souhaitez recalculer les prestations")))
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez une date de début")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez une date de fin")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser la liste")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((720, 800))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        # Paramètres
        box_parametres = wx.StaticBoxSizer(self.box_parametres_staticbox, wx.VERTICAL)
        grid_sizer_parametres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)

        grid_sizer_parametres.Add(self.label_activite, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_parametres.Add(self.ctrl_activite, 1, wx.EXPAND, 0)
        grid_sizer_parametres.AddGrowableCol(1)

        grid_sizer_parametres.Add(self.label_forfait, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_parametres.Add(self.ctrl_forfait, 1, wx.EXPAND, 0)

        grid_sizer_parametres.Add(self.label_periode, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_periode.Add((10, 10), 0, 0, 0)
        grid_sizer_periode.Add(self.bouton_actualiser, 1, wx.EXPAND, 0)
        grid_sizer_periode.AddGrowableCol(4)
        grid_sizer_parametres.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        
        box_parametres.Add(grid_sizer_parametres, 1, wx.EXPAND | wx.ALL, 10)
        grid_sizer_contenu.Add(box_parametres, 1, wx.EXPAND, 0)
        
        # Individus
        box_individus = wx.StaticBoxSizer(self.box_individus_staticbox, wx.VERTICAL)
        grid_sizer_individus = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        grid_sizer_individus.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        grid_sizer_individus.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_individus.AddGrowableCol(0)
        grid_sizer_individus.AddGrowableRow(0)
        box_individus.Add(grid_sizer_individus, 1, wx.EXPAND | wx.ALL, 10)
        
        grid_sizer_contenu.Add(box_individus, 1, wx.EXPAND, 0)

        # Grille des conso
        box_grille = wx.StaticBoxSizer(self.box_grille_staticbox, wx.VERTICAL)
        grid_sizer_grille = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_grille.Add(self.ctrl_log, 1, wx.EXPAND, 0)
        grid_sizer_grille.Add(self.ctrl_gauge, 1, wx.EXPAND, 0)
        grid_sizer_grille.Add(self.ctrl_grille, 1, wx.EXPAND, 0)
        grid_sizer_grille.AddGrowableRow(0)
        grid_sizer_grille.AddGrowableCol(0)
        
        box_grille.Add(grid_sizer_grille, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_grille, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(0)

        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnChoixActivite(self, event):
        IDactivite = self.ctrl_activite.GetID()

        # MAJ CTRL forfait
        self.ctrl_forfait.SetActivite(IDactivite)
        self.ctrl_forfait.MAJ()

        self.Actualiser()

    def OnChoixForfait(self, event):
        self.Actualiser()

    def Actualiser(self, event=None):

        dictTarif = self.ctrl_forfait.GetDictTarif()
        if dictTarif != None :
            categories_tarifs = dictTarif["listeCategoriesTarifs"]
        else :
            categories_tarifs = []
        
        # Récupération de la période
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        
        # MAJ liste individus
        IDactivite = self.ctrl_activite.GetID()
        self.ctrl_individus.SetActivite(IDactivite)
        self.ctrl_individus.SetCategoriesTarifs(categories_tarifs)
        self.ctrl_individus.SetPeriode(date_debut, date_fin)
        self.ctrl_individus.MAJ() 

    def OnBoutonActualiser(self, event): 
        IDactivite = self.ctrl_activite.GetID()
        if IDactivite == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_activite.SetFocus() 
            return False

        date_debut = self.ctrl_date_debut.GetDate()
        if date_debut == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus() 
            return False

        date_fin = self.ctrl_date_fin.GetDate()
        if date_fin == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus() 
            return False
        
        self.Actualiser() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        if self.Arreter() == True :
            return
        self.EndModal(wx.ID_CANCEL)        

    def EcritLog(self, texte="", saut=True):
        if saut == True and len(self.ctrl_log.GetValue()) > 0 :
            texte = u"\n" + texte
        try :
            self.ctrl_log.AppendText(texte)
        except :
            pass

    def SetStatutTrack(self, track=None, statut=None):
        track.statut = statut
        try :
            self.ctrl_individus.EnsureCellVisible(self.ctrl_individus.GetIndexOf(track)+1, 0)
        except :
            try :
                self.ctrl_individus.EnsureCellVisible(self.ctrl_individus.GetIndexOf(track), 0)
            except :
                pass

        self.ctrl_individus.RefreshObject(track)
        if statut == "ok" :
            self.ctrl_individus.Uncheck(track)
    
    def Arreter(self, forcer=False):
        try:
            TraitmentEnCours = self.traitement.isAlive()
        except AttributeError :
            TraitmentEnCours = False
            
        if TraitmentEnCours:
            if forcer == True :
                self.traitement.abort()
                return True
            else :
                # Demande la confirmation de l'arrêt
                dlgConfirm = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment arrêter le traitement ?"), _(u"Confirmation d'arrêt"), wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
                reponse = dlgConfirm.ShowModal()
                dlgConfirm.Destroy()
                if reponse == wx.ID_NO:
                    return True
                # Si le traitement est en cours, on le stoppe :
                self.traitement.abort()
                time.sleep(0.2)
                self.EcritLog(_(u"Vous avez interrompu le traitement."))
                return True

    def OnBoutonOk(self, event): 
        try:
            TraitmentEnCours = self.traitement.isAlive()
        except AttributeError :
            TraitmentEnCours = False
            
        if TraitmentEnCours:
            # Stopper traitement
            self.Arreter() 
        else :
            # Récupération des paramètres de sélection
            IDactivite = self.ctrl_activite.GetID()
            dictTarif = self.ctrl_forfait.GetDictTarif() 
            date_debut = self.ctrl_date_debut.GetDate()
            date_fin = self.ctrl_date_fin.GetDate()
            tracks = self.ctrl_individus.GetTracksCoches()

            # Périodes de gestion
            gestion = UTILS_Gestion.Gestion(None)
            if gestion.IsPeriodeinPeriodes("prestations", date_debut, date_fin) == False: return False

            if len(tracks) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez cocher au moins un individu dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False

            # Demande confirmation de lancement
            dlgConfirm = wx.MessageDialog(self, _(u"Souhaitez-vous saisir le forfait pour les %d individus cochés ?\n\nLe traitement peut prendre quelques minutes...") % len(tracks), _(u"Confirmation"), wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.ICON_QUESTION)
            reponse = dlgConfirm.ShowModal()
            dlgConfirm.Destroy()
            if reponse != wx.ID_YES :
                return False
            
            # Lancer traitement
            self.EcritLog(_(u"Lancement du traitement"))
            self.bouton_ok.SetImageEtTexte(cheminImage="Images/32x32/Arreter.png", texte=u"Arrêter")
            self.bouton_fermer.Enable(False)
            self.Layout()
            
            # Traitement
            self.traitement = Traitement(self, IDactivite=IDactivite, dictTarif=dictTarif, date_debut=date_debut, date_fin=date_fin, tracks=tracks) 
            self.traitement.start()
        
        

if __name__ == "__main__":
    app = wx.App(0)
    dlg = Dialog(None)
    dlg.ctrl_date_debut.SetDate(datetime.date(2015, 9, 1))
    dlg.ctrl_date_fin.SetDate(datetime.date(2015, 9, 30))
    dlg.ctrl_activite.SetID(1)
    dlg.OnBoutonActualiser(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
