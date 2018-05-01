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
"""
IMPORTANT :
J'ai rajoute la ligne 101 de gridlabelrenderer.py dans wxPython mixins :
if rows == [-1] : return
"""

import wx
import CTRL_Bouton_image
import wx.grid as gridlib
import wx.lib.wordwrap as wordwrap
import Outils.gridlabelrenderer as glr
import datetime
import calendar
import textwrap 

if 'phoenix' in wx.PlatformInfo:
    from wx.grid import GridCellRenderer
else :
    from wx.grid import PyGridCellRenderer as GridCellRenderer

import GestionDB
from Utils import UTILS_Config
from Utils import UTILS_Texte
from Utils import UTILS_Dates

# Colonnes unités
LARGEUR_COLONNE_UNITE = 60
ABREGE_GROUPES = 0
AFFICHE_TOTAUX = 1

# Colonnes Activités
LARGEUR_COLONNE_ACTIVITE = 18
COULEUR_COLONNE_ACTIVITE = (205, 144, 233)

COULEUR_COLONNE_TOTAL = "#C5DDFA"

# Cases
COULEUR_RESERVATION = (252, 213, 0) # ancien vert : "#A6FF9F"
COULEUR_ATTENTE = "YELLOW"
COULEUR_REFUS = "RED"
COULEUR_DISPONIBLE = "#E3FEDB"
COULEUR_ALERTE = "#FEFCDB"
COULEUR_COMPLET = "#F7ACB2"
COULEUR_NORMAL = "WHITE"
COULEUR_FERME = (220, 220, 220)


def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (_(u"Lundi"), _(u"Mardi"), _(u"Mercredi"), _(u"Jeudi"), _(u"Vendredi"), _(u"Samedi"), _(u"Dimanche"))
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def HeureStrEnTime(heureStr):
    if heureStr == None or heureStr == "" : return datetime.time(0, 0)
    heures, minutes = heureStr.split(":")
    return datetime.time(int(heures), int(minutes))



class CaseSeparationActivite():
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, IDactivite=None):
        self.typeCase = "activite"
        self.IDactivite = IDactivite
        self.couleurFond = COULEUR_COLONNE_ACTIVITE
        
        # Dessin de la case
        self.renderer = RendererCaseActivite(self)
        if self.IDactivite != None :
            if grid.dictActivites != None :
                labelActivite = grid.dictActivites[IDactivite]["nom"]
            else:
                labelActivite = _(u"Activité ID%d") % IDactivite
        grid.SetCellValue(numLigne, numColonne, labelActivite)
        grid.SetCellAlignment(numLigne, numColonne, wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
        grid.SetCellRenderer(numLigne, numColonne, self.renderer)
        grid.SetReadOnly(numLigne, numColonne, True)
    
    def OnClick(self):
        pass
    
    def OnContextMenu(self):
        pass

    def GetTexteInfobulle(self):
        return ""



class Evenement():
    def __init__(self, case=None, dict_evenement=None):
        self.case = case

        # Caractéristiques de l'évènement
        self.IDevenement = dict_evenement["IDevenement"]
        self.IDactivite = dict_evenement["IDactivite"]
        self.IDunite = dict_evenement["IDunite"]
        self.IDgroupe = dict_evenement["IDgroupe"]
        self.date = dict_evenement["date"]
        self.nom = dict_evenement["nom"]
        self.capacite_max = dict_evenement["capacite_max"]
        self.heure_debut = dict_evenement["heure_debut"]
        self.heure_fin = dict_evenement["heure_fin"]

        # Rattachement d'une conso
        self.conso = None

    def SetConso(self, conso=None):
        self.conso = conso
        if self.conso != None :
            self.conso.IDevenement = self.IDevenement
            self.conso.evenement = self
            self.conso.case = self.case

    def GetTexteInfobulle(self):
        return self.case.GetTexteInfobulleConso(self.conso, evenement=self)

    def GetStatutTexte(self, x=None, y=None):
        heure_debut = UTILS_Dates.DatetimeTimeEnStr(self.heure_debut)
        heure_fin = UTILS_Dates.DatetimeTimeEnStr(self.heure_fin)
        if heure_debut != "00h00" and heure_fin != "00h00" :
            texte = _(u"%s : %s > %s") % (self.nom, heure_debut, heure_fin)
        else:
            texte = _(u"%s") % self.nom
        return texte

    def Refresh(self):
        self.case.Refresh()

    def MemoriseValeurs(self):
        if self.case.grid.dictConsoIndividus.has_key(self.case.IDindividu) == False:
            self.case.grid.dictConsoIndividus[self.case.IDindividu] = {}
        if self.case.grid.dictConsoIndividus[self.case.IDindividu].has_key(self.case.date) == False:
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date] = {}
        if self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date].has_key(self.case.IDunite) == False:
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite] = []

        listeConso = self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite]
        position = None
        index = 0
        for conso in listeConso:
            if self.conso == conso:
                position = index
            index += 1

        if position == None:
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite].append(self.conso)
        else:
            if self.conso.statut not in ("ajout", "suppression"):
                self.conso.statut = "modification"
            self.case.grid.dictConsoIndividus[self.case.IDindividu][self.case.date][self.case.IDunite][position] = self.conso

    def MAJ_facturation(self):
        self.case.MAJ_facturation(evenement=self)

    def GetCouleur(self):
        """ Retourn la couleur de fond du bouton """
        # Recherche nbre places évènements
        dictPlacesEvenement = self.GetPlacesEvenement()
        if dictPlacesEvenement["nbrePlacesInitial"] != None :
            if dictPlacesEvenement["nbrePlacesRestantes"] == None or dictPlacesEvenement["nbrePlacesRestantes"] > 0 :
                return COULEUR_DISPONIBLE
            else :
                return COULEUR_COMPLET

        # Sinon on retourne la couleur de remplissage
        if self.case.dictInfosPlaces["nbrePlacesInitial"] != None:
            nbrePlacesRestantes = self.case.dictInfosPlaces["nbrePlacesRestantes"]
            seuil_alerte = self.case.dictInfosPlaces["seuil_alerte"]
            if nbrePlacesRestantes > seuil_alerte: return COULEUR_DISPONIBLE
            if nbrePlacesRestantes > 0 and nbrePlacesRestantes <= seuil_alerte: return COULEUR_ALERTE
            if nbrePlacesRestantes <= 0: return COULEUR_COMPLET

        # Si aucun remplissage, on retourne du blanc
        return wx.WHITE

    def GetPlacesEvenement(self):
        nbrePlacesRestantes, nbrePlacesPrises = None, None

        if self.capacite_max != None:
            if self.case.grid.dictRemplissageEvenements.has_key(self.IDevenement) :
                nbrePlacesPrises = self.case.grid.dictRemplissageEvenements[self.IDevenement]["reservation"] + self.case.grid.dictRemplissageEvenements[self.IDevenement]["present"]
                nbrePlacesRestantes = self.capacite_max - nbrePlacesPrises

        if self.case.grid.dictRemplissageEvenements.has_key(self.IDevenement) :
            nbrePlacesAttente = self.case.grid.dictRemplissageEvenements[self.IDevenement]["attente"]
        else :
            nbrePlacesAttente = 0

        return {"nbrePlacesPrises" : nbrePlacesPrises, "nbrePlacesInitial" : self.capacite_max, "nbrePlacesRestantes" : nbrePlacesRestantes, "nbreAttente" : nbrePlacesAttente}

    def GetValeur(self):
        dictPlacesEvenement = self.GetPlacesEvenement()
        if dictPlacesEvenement != None :
            valeur = dictPlacesEvenement[self.case.ligne.modeAffichage]
            if valeur not in (None, 0) :
                return str(valeur)
        return ""



class Case():
    def __init__(self, ligne, grid, numLigne=None, numColonne=None, date=None, IDunite=None, IDactivite=None, IDgroupe=None, estTotal=False, total=None):
        self.typeCase = "consommation"
        self.grid = grid
        self.ligne = ligne
        self.numLigne = numLigne
        self.numColonne = numColonne
        self.IDgroupe = IDgroupe
        self.date = date
        self.IDunite = IDunite
        self.IDactivite = IDactivite
        self.estTotal = estTotal
        self.total = total

        # Création des évènements
        self.liste_evenements = self.CreationEvenements()

        # Recherche si l'activité est ouverte
        self.ouvert = self.EstOuvert()

        # Récupère les infos de remplissage de la case
        self.dictInfosPlaces = self.GetInfosPlaces() 
        
        # Définition des couleurs de la case
        self.couleurFond = self.GetCouleur()

        # Dessin de la case
        modeEvenement = self.GetNbreEvenements() # Todo : Provisoire !!!
        if modeEvenement :
            self.renderer = RendererCaseEvenement(self)
        else :
            self.renderer = RendererCase(self)

        self.valeurCase = self.dictInfosPlaces[self.ligne.modeAffichage] 
        # "nbrePlacesInitial" , "nbrePlacesPrises", "nbrePlacesRestantes", "seuil_alerte", "nbreAttente"
        
        if self.valeurCase == None or self.ouvert == False or self.valeurCase == 0 :
            self.valeurCase = u""
        
        if self.estTotal == True :
            if self.total != 0 :
                self.valeurCase = self.total 
            else:
                self.valeurCase = u""
            
        self.grid.SetCellValue(self.numLigne, self.numColonne, str(self.valeurCase))
        self.grid.SetCellAlignment(self.numLigne, self.numColonne, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.grid.SetCellRenderer(self.numLigne, self.numColonne, self.renderer)
        self.grid.SetReadOnly(self.numLigne, self.numColonne, True)

    def GetNbreEvenements(self):
        return len(self.liste_evenements)

    def CreationEvenements(self):
        """ Génère les évènements """
        # Recherche les évènements dans toutes les unités de conso associées à l'unité de remplissage
        liste_donnees = []
        for IDunite, listeUnitesRemplissage in self.grid.dictUnitesRemplissage.iteritems() :
            if self.IDunite in listeUnitesRemplissage :
                try :
                    liste_donnees.extend(self.grid.dictOuvertures[self.date][self.IDgroupe][IDunite]["liste_evenements"])
                except :
                    pass

        liste_evenements = []
        for dict_evenement in liste_donnees :
            evenement = Evenement(case=self, dict_evenement=dict_evenement)
            liste_evenements.append(evenement)
        return liste_evenements

    def GetInfosPlaces(self):
        IDunite_remplissage = self.IDunite
        
        # Recherche des nbres de places
        try :
            nbrePlacesPrises = self.grid.dictRemplissage[self.IDunite][self.date][self.IDgroupe]["nbrePlacesPrises"]
        except :
            nbrePlacesPrises = 0
        try :
            nbrePlacesInitial = self.grid.dictRemplissage[self.IDunite][self.date][self.IDgroupe]["nbrePlacesInitial"]
            nbrePlacesRestantes = nbrePlacesInitial - nbrePlacesPrises
        except :
            nbrePlacesInitial = None
            nbrePlacesRestantes = None
        try :
            seuil_alerte = self.grid.dictRemplissage[self.IDunite]["seuil_alerte"]
        except :
            seuil_alerte = None
        # Attente
        try :
            nbreAttente = self.grid.dictConsoAttente[self.date][self.IDgroupe][self.IDunite]
        except : 
            nbreAttente = 0


        # Récupère le nombre de places restantes pour l'ensemble des groupes
        nbrePlacesInitialTousGroupes = 0
        try :
            nbrePlacesInitialTousGroupes = self.grid.dictRemplissage[IDunite_remplissage][self.date][None]["nbrePlacesInitial"]
        except :
            pass
        
        if nbrePlacesInitialTousGroupes > 0 :
            nbrePlacesPrisesTousGroupes = 0
            try :
                for IDgroupe, d in self.grid.dictRemplissage[IDunite_remplissage][self.date].iteritems() :
                    nbrePlacesPrisesTousGroupes += d["nbrePlacesPrises"]
            except :
                pass
            
            nbrePlacesRestantesTousGroupes = nbrePlacesInitialTousGroupes - nbrePlacesPrisesTousGroupes
            if nbrePlacesRestantesTousGroupes < nbrePlacesRestantes or nbrePlacesInitial == 0 :
                nbrePlacesInitial = nbrePlacesInitialTousGroupes
##                nbrePlacesPrises = nbrePlacesPrisesTousGroupes
                nbrePlacesRestantes = nbrePlacesRestantesTousGroupes


        # Création d'un dictionnaire de réponses
        dictInfosPlaces = {
            "nbrePlacesInitial" : nbrePlacesInitial, 
            "nbrePlacesPrises" : nbrePlacesPrises, 
            "nbrePlacesRestantes" : nbrePlacesRestantes, 
            "seuil_alerte" : seuil_alerte,
            "nbreAttente" : nbreAttente,
            }
        return dictInfosPlaces
                
    def GetCouleur(self):
        """ Obtient la couleur à appliquer à la case """    
        if self.estTotal == True :
            return COULEUR_COLONNE_TOTAL

        # Si fermée
        if self.ouvert == False : return COULEUR_FERME
        
        if self.dictInfosPlaces["nbrePlacesInitial"] != None :
            nbrePlacesRestantes = self.dictInfosPlaces["nbrePlacesRestantes"]
            seuil_alerte = self.dictInfosPlaces["seuil_alerte"]
            if nbrePlacesRestantes > seuil_alerte : return COULEUR_DISPONIBLE
            if nbrePlacesRestantes > 0 and nbrePlacesRestantes <= seuil_alerte : return COULEUR_ALERTE
            if nbrePlacesRestantes <= 0 : return COULEUR_COMPLET
        
        return COULEUR_NORMAL
        
    def EstOuvert(self):
        """ Recherche si l'unité est ouverte à cette date """
        ouvert = False
        if self.grid.dictOuvertures.has_key(self.date):
            if self.grid.dictOuvertures[self.date].has_key(self.IDgroupe):
                ouvert = True
        
        date_debut = self.grid.dictRemplissage[self.IDunite]["date_debut"]
        date_fin = self.grid.dictRemplissage[self.IDunite]["date_fin"]
        if self.date < date_debut or self.date > date_fin :
            ouvert = False
        return ouvert
    
    def GetTexteInfobulle(self):
        """ Renvoie le texte pour l'infobulle de la case """
        nomUnite = self.grid.dictUnites[self.IDunite]["nom"]
        dateComplete = DateComplete(self.date)
        texte = u"%s du %s\n\n" % (nomUnite, dateComplete)
        texte = texte.upper()
        # Heures de la consommation
        if self.etat in ("reservation", "attente", "present") :
            if self.heure_debut == None or self.heure_fin == None :
                texte += _(u"Horaire de la consommation non spécifié\n")
            else:
                texte += _(u"De %s à %s\n") % (self.heure_debut.replace(":","h"), self.heure_fin.replace(":","h"))
            texte += _(u"Sur le groupe %s \n") % self.grid.dictGroupes[self.IDgroupe]["nom"]
        texte += u"-------------------------------------------------------------------\n" 
        
        # Si unité fermée
        if self.ouvert == False :
            return _(u"Unité fermée")
        # Nbre de places
        if self.dictInfosPlaces != None :
            nbrePlacesInitial = self.dictInfosPlaces["nbrePlacesInitial"]
            nbrePlacesPrises = self.dictInfosPlaces["nbrePlacesPrises"]
            nbrePlacesRestantes = self.dictInfosPlaces["nbrePlacesRestantes"]
            seuil_alerte = self.dictInfosPlaces["seuil_alerte"]
            nbreAttente = self.dictInfosPlaces["nbreAttente"]
            texte += _(u"Nbre initial de places  : %d \n") % nbrePlacesInitial
            texte += _(u"Nbre de places prises : %d \n") % nbrePlacesPrises
            texte += _(u"Nbre de places disponibles : %d \n") % nbrePlacesRestantes
            texte += _(u"Seuil d'alerte : %d \n") % seuil_alerte
            texte += _(u"Nbre d'individus sur liste d'attente : %d \n") % nbreAttente
        else:
            texte += _(u"Aucune limitation du nombre de places\n")
        # Etat de la case
        texte += "-------------------------------------------------------------------\n"
        if self.etat in ("reservation", "attente", "present") :
            date_saisie_FR = DateComplete(self.date_saisie)
            if self.etat == "reservation" or self.etat == "present" : texte += _(u"Consommation réservée le %s\n") % date_saisie_FR
            if self.etat == "attente" : texte += _(u"Consommation mise en attente le %s\n") % date_saisie_FR
            if self.IDutilisateur != None :
                texte += _(u"Par l'utilisateur ID%d\n") % self.IDutilisateur
            texte += "-------------------------------------------------------------------\n"
        # Infos Individu
        nom = self.grid.dictInfosIndividus[self.IDindividu]["nom"]
        prenom = self.grid.dictInfosIndividus[self.IDindividu]["prenom"]
        texte += _(u"Informations concernant %s %s : \n") % (prenom, nom)
        date_naiss = self.grid.dictInfosIndividus[self.IDindividu]["date_naiss"]
        if date_naiss != None :
            ageActuel = CalculeAge(datetime.date.today(), date_naiss)
            texte += _(u"Age actuel : %d ans \n") % ageActuel
            if self.etat != None :
                ageConso = CalculeAge(self.date, date_naiss)
                texte += _(u"Age lors de la consommation : %d ans \n") % ageConso
        else:
            texte += _(u"Date de naissance inconnue ! \n")
        # Infos inscription :
        nom_categorie_tarif = self.dictInfosInscriptions["nom_categorie_tarif"]
        if self.etat in ("reservation", "absent", "present") :
            texte += "-------------------------------------------------------------------\n"
            texte += _(u"Catégorie de tarif : '%s'\n") % nom_categorie_tarif
        
        return texte
    
    def OnContextMenu(self):
        if self.ouvert == False :
            return
        
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item IDENTIFICATION DE LA CASE
        nomUnite = self.grid.dictUnites[self.IDunite]["nom"]
        dateComplete = DateComplete(self.date)
        texteItem = u"%s du %s" % (nomUnite, dateComplete)
        item = wx.MenuItem(menuPop, 10, texteItem)
        menuPop.AppendItem(item)
        item.Enable(False)
        
        # Etat de la consommation
        if self.etat in ("reservation", "present", "absent") :
            menuPop.AppendSeparator()
            item = wx.MenuItem(menuPop, 60, _(u"Pointage en attente"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if self.etat == "reservation" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=60)
            item = wx.MenuItem(menuPop, 70, _(u"Présent"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if self.etat == "present" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=70)
            item = wx.MenuItem(menuPop, 80, _(u"Absent"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if self.etat == "absent" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=80)
        
        if self.etat in ("reservation", "attente", "refus") :
            menuPop.AppendSeparator()
            item = wx.MenuItem(menuPop, 30, _(u"Réservation"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if self.etat == "reservation" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=30)
            item = wx.MenuItem(menuPop, 40, _(u"Attente"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if self.etat == "attente" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=40)
            item = wx.MenuItem(menuPop, 50, _(u"Refus"), kind=wx.ITEM_RADIO)
            menuPop.AppendItem(item)
            if self.etat == "refus" : item.Check(True)
            self.grid.Bind(wx.EVT_MENU, self.SetEtat, id=50)
        
        # Changement de Groupe
        listeGroupes = []
        for IDgroupe, dictGroupe in self.grid.dictGroupes.iteritems():
            if dictGroupe["IDactivite"] == self.IDactivite :
                listeGroupes.append( (dictGroupe["nom"], IDgroupe) )
        listeGroupes.sort() 
        if len(listeGroupes) > 0 and self.etat in ("reservation", "attente", "refus") :
            menuPop.AppendSeparator()
            for nomGroupe, IDgroupe in listeGroupes :
                IDitem = 10000 + IDgroupe
                item = wx.MenuItem(menuPop, IDitem, nomGroupe, kind=wx.ITEM_RADIO)
                menuPop.AppendItem(item)
                if self.IDgroupe == IDgroupe : item.Check(True)
                self.grid.Bind(wx.EVT_MENU, self.SetGroupe, id=IDitem)
                
        # Détail de la consommation
        if self.etat in ("reservation", "present", "absent", "attente", "refus") :
            menuPop.AppendSeparator()
            item = wx.MenuItem(menuPop, 20, _(u"Détail de la consommation"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier_zoom.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.DLG_detail, id=20)
            
        # Item Verrouillage
##        if self.verrouillage == 0 and self.etat != None :
##            item = wx.MenuItem(menuPop, 10, _(u"Verrouiller cette consommation"))
##            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas_ferme.png"), wx.BITMAP_TYPE_PNG)
##            item.SetBitmap(bmp)
##            menuPop.AppendItem(item)
##            self.grid.Bind(wx.EVT_MENU, self.Verrouillage, id=10)
##        if self.verrouillage == 1 and self.etat != None :
##            item = wx.MenuItem(menuPop, 10, _(u"Déverrouiller cette consommation"))
##            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas.png"), wx.BITMAP_TYPE_PNG)
##            item.SetBitmap(bmp)
##            menuPop.AppendItem(item)
##            self.grid.Bind(wx.EVT_MENU, self.Deverrouillage, id=10)
        
                
        self.grid.PopupMenu(menuPop)
        menuPop.Destroy()
        
        
        
class Ligne():
    def __init__(self, grid, numLigne, date, dictGroupeTemp, dictListeRemplissage, modeAffichage):
        self.grid = grid
        self.numLigne = numLigne
        self.date = date
        self.modeAffichage = modeAffichage
        
        # Label de la ligne
        self.labelLigne = DateComplete(self.date)
        
        # Couleurs de label
        couleurLigneDate = "#C0C0C0"
        self.couleurOuverture = (0, 230, 0)
        self.couleurFermeture = "#F7ACB2"
        couleurVacances = "#F3FD89"
        
        # Création du label de ligne
        self.grid.SetRowLabelValue(numLigne, self.labelLigne)
        if self.EstEnVacances(self.date) == True :
            couleurCase = couleurVacances
        else:
            couleurCase = None
        self.renderer = MyRowLabelRenderer(couleurCase, self.date)
        self.grid.SetRowLabelRenderer(numLigne, self.renderer)
        self.grid.dictLignes[numLigne] = self.renderer
        
        # Création des cases
        self.dictCases = {}
        self.dictTotaux = {}
        nbre_evenements = 0

        numColonne = 0
        for IDactivite in self.grid.listeActivites :
            
            # Création de la colonne activité
            if len(self.grid.listeActivites) > 1 and dictGroupeTemp.has_key(IDactivite) :
                case = CaseSeparationActivite(self, self.grid, self.numLigne, numColonne, IDactivite)
                self.dictCases[numColonne] = case
                numColonne += 1
                
            # Création des cases unités de remplissage
            if dictGroupeTemp.has_key(IDactivite):
                for IDgroupe in dictGroupeTemp[IDactivite] :
                    if dictListeRemplissage.has_key(IDactivite) :
                        for ordre, IDunite_remplissage in dictListeRemplissage[IDactivite] :
                            case = Case(self, self.grid, self.numLigne, numColonne, self.date, IDunite_remplissage, IDactivite, IDgroupe)
                            nbre_evenements += case.GetNbreEvenements()
                            if self.dictTotaux.has_key(IDunite_remplissage) == False :
                                self.dictTotaux[IDunite_remplissage] = 0
                            if case.valeurCase != u"" and case.valeurCase != None :
                                self.dictTotaux[IDunite_remplissage] += case.valeurCase
                            self.dictCases[numColonne] = case
                            numColonne += 1
                        
            # Création des colonnes totaux
            if AFFICHE_TOTAUX == 1 and dictListeRemplissage.has_key(IDactivite) and dictGroupeTemp.has_key(IDactivite) :
                if len(dictListeRemplissage[IDactivite]) > 0 and len(dictGroupeTemp[IDactivite]) > 0 :
                    for ordre, IDunite_remplissage in dictListeRemplissage[IDactivite] :
                        if self.dictTotaux.has_key(IDunite_remplissage) :
                            total = self.dictTotaux[IDunite_remplissage]
                        else:
                            total = None
                        case = Case(self, self.grid, self.numLigne, numColonne, self.date, IDunite_remplissage, IDactivite, None, True, total)
                        self.dictCases[numColonne] = case
                        numColonne += 1

        # Ajustement de la hauteur de la ligne
        if nbre_evenements > 0 :
            hauteurLigne = 36
        else :
            hauteurLigne = 30
        self.grid.SetRowSize(numLigne, hauteurLigne)

    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.grid.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def OnContextMenu(self):
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Item IDENTIFICATION DE LA LIGNE
        item = wx.MenuItem(menuPop, 10, self.labelLigne)
        menuPop.AppendItem(item)
        item.Enable(False)
        
        menuPop.AppendSeparator()

##        # Item Verrouillage
##        item = wx.MenuItem(menuPop, 10, _(u"Verrouiller toutes les consommations"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas_ferme.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.grid.Bind(wx.EVT_MENU, self.Verrouillage, id=10)
##        
##        item = wx.MenuItem(menuPop, 20, _(u"Déverrouiller toutes les consommations"))
##        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Cadenas.png"), wx.BITMAP_TYPE_PNG)
##        item.SetBitmap(bmp)
##        menuPop.AppendItem(item)
##        self.grid.Bind(wx.EVT_MENU, self.Deverrouillage, id=20)
        
        # Etat des consommations de la ligne
        nbreCasesReservations = 0
        for numColonne, case in self.dictCases.iteritems() :
            if case.typeCase == "consommation" :
                if case.etat in ("reservation", "present", "absent") :
                    nbreCasesReservations += 1
                    
        if nbreCasesReservations > 0 :
            item = wx.MenuItem(menuPop, 30, _(u"Définir toutes les pointages de la ligne comme 'Pointage en attente'"))
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=30)
            item = wx.MenuItem(menuPop, 40, _(u"Pointer toutes les consommations de la ligne sur 'Présent'"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Ok.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=40)
            item = wx.MenuItem(menuPop, 50, _(u"Pointer toutes les consommations de la ligne sur 'Absent'"))
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Interdit.png"), wx.BITMAP_TYPE_PNG)
            item.SetBitmap(bmp)
            menuPop.AppendItem(item)
            self.grid.Bind(wx.EVT_MENU, self.SetPresentAbsent, id=50)
            
        self.grid.PopupMenu(menuPop)
        menuPop.Destroy()
    

        

class RendererCase(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.case.couleurFond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
            dc.DrawRectangleRect(rect)

        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        texte = grid.GetCellValue(row, col)
        largeurTexte, hauteurTexte = dc.GetTextExtent(texte)
        if self.case.ouvert == True or self.case.estTotal == True :
            self.DrawBorder(grid, dc, rect)
        dc.DrawText(texte, rect[0] + rect[2]/2.0 - largeurTexte/2.0, rect[1] + rect[3]/2.0 - hauteurTexte/2.0)            
            
    def MAJ(self):
        self.grid.Refresh()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()

    def DrawBorder(self, grid, dc, rect):
        """
        Draw a standard border around the label, to give a simple 3D
        effect like the stock wx.grid.Grid labels do.
        """
        top = rect.top
        bottom = rect.bottom
        left = rect.left
        right = rect.right        
        dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
        dc.DrawLine(right, top, right, bottom)
        dc.DrawLine(left, top, left, bottom)
        dc.DrawLine(left, bottom, right, bottom)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawLine(left+1, top, left+1, bottom)
        dc.DrawLine(left+1, top, right, top)
    
    def AdapteTailleTexte(self, dc, texte, tailleMaxi):
        """ Raccourcit le texte de l'intitulé en fonction de la taille donnée """
        # Pas de retouche nécessaire
        if dc.GetTextExtent(texte)[0] < tailleMaxi : return texte
        # Renvoie aucun texte si tailleMaxi trop petite
        if tailleMaxi <= dc.GetTextExtent("W...")[0] : return "..."
        # Retouche nécessaire
        tailleTexte = dc.GetTextExtent(texte)[0]
        texteTemp = ""
        texteTemp2 = ""
        for lettre in texte :
            texteTemp += lettre
            if dc.GetTextExtent(texteTemp +"...")[0] < tailleMaxi :
               texteTemp2 = texteTemp 
            else:
                return texteTemp2 + "..." 


# ----------------------------------------------------------------------------------------------

class RendererCaseEvenement(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid

        # Préparation du buffer Image
        dcGrid = dc
        if 'phoenix' in wx.PlatformInfo:
            bmp = wx.Bitmap(rect.GetWidth(), rect.GetHeight())
        else :
            bmp = wx.EmptyBitmap(rect.GetWidth(), rect.GetHeight())
        image = wx.MemoryDC()
        image.SelectObject(bmp)
        gc = wx.GraphicsContext.Create(image)
        gc.PushState()
        if 'phoenix' in wx.PlatformInfo:
            gc.SetFont(attr.GetFont(), wx.Colour(0, 0, 0))
        else :
            gc.SetFont(attr.GetFont())

        rectCase = wx.Rect(0, 0, rect.GetWidth(), rect.GetHeight())
        x, y, largeur, hauteur = rectCase.x, rectCase.y, rectCase.width, rectCase.height

        if self.case.ouvert == True :
            self.couleurFond = self.grid.GetBackgroundColour()
        else :
            self.couleurFond = COULEUR_FERME
        gc.SetBrush(wx.Brush(self.couleurFond, wx.SOLID))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(x, y, largeur, hauteur)

        # Calcul de la largeur d'un bouton
        nbre_evenements = len(self.case.liste_evenements)
        marge = 2
        if len(self.case.liste_evenements) :
            largeur_bouton = (1.0 * (rectCase.width - marge -1) / nbre_evenements) - marge*2

        # Dessin de boutons
        x = 1
        for evenement in self.case.liste_evenements :

            # Calcul de la taille du rectangle
            rectEvenement = wx.Rect(x + marge, rectCase.y + marge, largeur_bouton, rectCase.height - marge*2 - marge)

            # Dessin du rectangle
            couleur = evenement.GetCouleur()
            gc.SetBrush(wx.Brush(couleur, wx.SOLID))
            gc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DSHADOW)))
            gc.DrawRoundedRectangle(rectEvenement.x, rectEvenement.y, rectEvenement.width, rectEvenement.height, 5)

            # Dessin de la valeur
            couleur_nom = wx.Colour(0, 0, 0)
            texte = evenement.GetValeur()
            font = wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL)
            gc.SetFont(font, couleur_nom)
            largeurTexte, hauteurTexte = gc.GetTextExtent(texte)
            rect_texte = self.DrawTexte(gc, rectEvenement, texte, couleur=couleur_nom, position=(rectEvenement.width - largeurTexte -4, 2), font=font)

            # Dessin du nom de l'évènement
            couleur_nom = wx.Colour(150, 150, 150)
            rectTemp = wx.Rect(rectEvenement.x, rectEvenement.y, rectEvenement.width - largeurTexte, rectEvenement.height)
            rect_texte = self.DrawTexte(gc, rectTemp, evenement.nom, couleur=couleur_nom, position=(4, 2), font=wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

            # Dessin des horaires
            if evenement.heure_debut != None and evenement.heure_fin != None :
                heure_debut = UTILS_Dates.DatetimeTimeEnStr(evenement.heure_debut, "h")
                heure_fin = UTILS_Dates.DatetimeTimeEnStr(evenement.heure_fin, "h")
                if heure_debut != "00h00" and heure_fin != "00h00":
                    texte = u"%s - %s" % (heure_debut, heure_fin)
                    couleur_horaires = wx.Colour(200, 200, 200)
                    rect_texte = self.DrawTexte(gc, rectEvenement, texte, couleur=couleur_horaires, position=(4, rect_texte.height + 5), font=wx.Font(6, wx.SWISS, wx.NORMAL, wx.NORMAL))

            # Calcul de la position x suivante
            x += rectEvenement.width + marge*2

        gc.PopState()

        # Envoi du buffer au DC
        dcGrid.Blit(rect.x, rect.y, bmp.GetWidth(), bmp.GetHeight(), image, 0, 0)

    def DrawTexte(self, gc, rect, texte="Texte", couleur=wx.Colour(0, 0, 0), position=(0, 0), font=None):
        # Ajuste la font
        if font == None :
            font = wx.Font(7, wx.SWISS, wx.NORMAL, wx.NORMAL)
        gc.SetFont(font, couleur)

        # Calcul la largeur du texte
        largeurTexte, hauteurTexte = gc.GetTextExtent(texte)

        # Raccourci le texte si besoin
        if largeurTexte > (rect.width - position[0] -2) :
            texte = wordwrap.wordwrap(texte, rect.width-10, gc).split("\n")[0] + "..."
            largeurTexte, hauteurTexte = gc.GetTextExtent(texte)

        # Calcul le rect du texte
        rect_texte = wx.Rect(rect.x + position[0], rect.y + position[1], largeurTexte, hauteurTexte)

        # Dessin du texte
        if 'phoenix' in wx.PlatformInfo:
            if rect.Contains(rect_texte):
                gc.DrawText(texte, rect_texte.x, rect_texte.y)
        else :
            if rect.ContainsRect(rect_texte):
                gc.DrawText(texte, rect_texte.x, rect_texte.y)

        return rect_texte

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()












# ------------------------------------------------------------------------------------------------

class RendererCaseActivite(GridCellRenderer):
    def __init__(self, case):
        GridCellRenderer.__init__(self)
        self.case = case

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.grid = grid
        dc.SetBackgroundMode(wx.SOLID)
        dc.SetBrush(wx.Brush(self.case.couleurFond, wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        if 'phoenix' in wx.PlatformInfo:
            dc.DrawRectangle(rect)
        else :
            dc.DrawRectangleRect(rect)
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont(attr.GetFont())
        
        hAlign, vAlign = grid.GetCellAlignment(row, col)
        text = grid.GetCellValue(row, col)
##        dc.DrawText(text, rect[0], rect[1])
        if row == 0 :
            largeurTexte, hauteurTexte = dc.GetTextExtent(text)
            dc.DrawRotatedText(text, rect[0], rect[1]+largeurTexte+10, 90)
                    
    def MAJ(self):
        self.grid.Refresh()

    def GetBestSize(self, grid, attr, dc, row, col):
        text = grid.GetCellValue(row, col)
        dc.SetFont(attr.GetFont())
        w, h = dc.GetTextExtent(text)
        return wx.Size(w, h)

    def Clone(self):
        return RendererCase()
    
    
class MyRowLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, bgcolor, date):
        self._bgcolor = bgcolor
        self.date = date
        
    def Draw(self, grid, dc, rect, row):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
                dc.DrawRectangleRect(rect)
        else:
            pass
        hAlign, vAlign = grid.GetRowLabelAlignment()
        text = grid.GetRowLabelValue(row)
        self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)

        # Indicateur date du jour
        if self.date == datetime.date.today() :
            dc.SetBrush(wx.Brush(wx.Colour(255, 0, 0), wx.SOLID))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawPolygon([(0, 0), (-7, 0), (0, 7)], xoffset=rect[2]-2, yoffset=rect[1]+1)
            
    
    def MAJ(self, couleur):
        self._bgcolor = couleur
        

class MyColLabelRenderer(glr.GridLabelRenderer):
    def __init__(self, typeColonne=None, bgcolor=None):
        self.typeColonne = typeColonne
        self._bgcolor = bgcolor
        
    def Draw(self, grid, dc, rect, col):
        if self._bgcolor != None :
            dc.SetBrush(wx.Brush(self._bgcolor))
            dc.SetPen(wx.TRANSPARENT_PEN)
            if 'phoenix' in wx.PlatformInfo:
                dc.DrawRectangle(rect)
            else:
                dc.DrawRectangleRect(rect)
        hAlign, vAlign = grid.GetColLabelAlignment()
        text = grid.GetColLabelValue(col)
        if self.typeColonne == "unite" :
            text = wordwrap.wordwrap(text, LARGEUR_COLONNE_UNITE, dc)
        if self.typeColonne == "unite" :
            self.DrawBorder(grid, dc, rect)
        self.DrawText(grid, dc, rect, text, hAlign, vAlign)



# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL(gridlib.Grid, glr.GridWithLabelRenderersMixin): 
    def __init__(self, parent, dictDonnees=None):
        gridlib.Grid.__init__(self, parent, -1, size=(1, 1), style=wx.WANTS_CHARS)
        glr.GridWithLabelRenderersMixin.__init__(self)
        self.listePeriodes = []
        self.listeActivites = []
        self.dictLignes = {}
        self.SetModeAffichage("nbrePlacesPrises")
        self.moveTo = None
        tip = _(u"Double-cliquez sur une case contenant des valeurs pour consulter la liste des consommations associées")
        try :
            self.GetGridWindow().SetToolTip(tip)
        except :
            self.GetGridWindow().SetToolTip(wx.ToolTip(tip))
        self.caseSurvolee = None
        
        global LARGEUR_COLONNE_UNITE
        LARGEUR_COLONNE_UNITE = UTILS_Config.GetParametre("largeur_colonne_unite_remplissage", 60)

        global ABREGE_GROUPES
        ABREGE_GROUPES = UTILS_Config.GetParametre("remplissage_abrege_groupes", 0)

        global AFFICHE_TOTAUX
        AFFICHE_TOTAUX = UTILS_Config.GetParametre("remplissage_affiche_totaux", 1)

        # Création initiale de la grille
        self.CreateGrid(0, 0)
        self.SetRowLabelSize(180)
        self.EnableGridLines(False)
        #self.DisableDragColSize()
        self.DisableDragRowSize()
        
        self.SetDefaultCellBackgroundColour(self.GetBackgroundColour())
        
        # Binds
        self.Bind(gridlib.EVT_GRID_COL_SIZE, self.OnChangeColSize)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)

##        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnCellLeftClick)
##        self.Bind(gridlib.EVT_GRID_CELL_RIGHT_CLICK, self.OnCellRightClick)
##        self.Bind(gridlib.EVT_GRID_LABEL_RIGHT_CLICK, self.OnLabelRightClick)
##        self.GetGridWindow().Bind(wx.EVT_MOTION, self.OnMouseOver)

        # Dict de données de sélection
        self.dictDonnees = dictDonnees

    def SetDictDonnees(self, dictDonnees=None):
        self.dictDonnees = dictDonnees
        self.listeActivites = self.dictDonnees["listeActivites"]
        self.listePeriodes = self.dictDonnees["listePeriodes"]
        if self.dictDonnees.has_key("modeAffichage") :
            self.SetModeAffichage(self.dictDonnees["modeAffichage"])
                        
    def Tests(self):
        """ Commande de test pour le développement """
        # Param pour les tests
        self.listeActivites = [1,]
        self.listePeriodes = [(datetime.date(2011, 12, 31), datetime.date(2013, 12, 31)), (datetime.date(2011, 5, 1), datetime.date(2011, 12, 31)),]
        self.SetModeAffichage("nbrePlacesPrises")
        # Lancement
        self.MAJ_donnees()
        self.MAJ_affichage()
    
    def SetListeActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites

    def SetListePeriodes(self, listePeriodes=[]):
        self.listePeriodes = listePeriodes
    
    def SetModeAffichage(self, mode):
        # "nbrePlacesInitial" , "nbrePlacesPrises", "nbrePlacesRestantes", "seuil_alerte", "nbreAttente"
        self.modeAffichage = mode
            
    def MAJ(self):
        self.Freeze() 
        self.MAJ_donnees()
        self.MAJ_affichage()
        self.Thaw()
            
    def MAJ_donnees(self):
        if self.dictDonnees != None :
            self.SetDictDonnees(self.dictDonnees)
        # Récupération des données
        self.DB = GestionDB.DB() 
        self.dictActivites = self.Importation_activites()
        self.dictOuvertures, listeUnitesUtilisees, self.listeGroupesUtilises = self.GetDictOuvertures(self.listeActivites, self.listePeriodes)
        self.listeVacances = self.GetListeVacances() 
        self.dictRemplissage, self.dictUnitesRemplissage, self.dictConsoAttente, self.dictRemplissageEvenements = self.GetDictRemplissage(self.listeActivites, self.listePeriodes)
        self.dictGroupes = self.GetDictGroupes()
        self.DB.Close()

    def MAJ_affichage(self):
        if self.GetNumberRows() > 0 : 
            self.DeleteRows(0, self.GetNumberRows())
        if self.GetNumberCols() > 0 : 
            self.DeleteCols(0, self.GetNumberCols())
        self.ClearGrid()
        self.InitGrid()
        self.Refresh()
                
    def InitGrid(self):
        # ----------------- Création des colonnes -------------------------
        
        # Récupération des groupes
        dictGroupeTemp = {}
        for IDgroupe, dictGroupe in self.dictGroupes.iteritems() : 
            IDactivite = dictGroupe["IDactivite"]
            ordre = dictGroupe["ordre"]
            if dictGroupeTemp.has_key(IDactivite) == False :
                dictGroupeTemp[IDactivite] = []
            dictGroupeTemp[IDactivite].append((ordre, IDgroupe))
            dictGroupeTemp[IDactivite].sort()
        
        for IDactivite, listeGroupesTemp in dictGroupeTemp.iteritems() :
            listeTemp = []
            for ordre, IDgroupe in listeGroupesTemp :
                listeTemp.append(IDgroupe)
            dictGroupeTemp[IDactivite] = listeTemp
            
        # Récupération des unités de remplissage
        dictListeRemplissage = {}
        for IDunite_remplissage, dictRemplissage in self.dictRemplissage.iteritems() :
            if dictRemplissage.has_key("IDactivite") :
                IDactivite = dictRemplissage["IDactivite"]
                ordre = dictRemplissage["ordre"]
                donnees = (ordre, IDunite_remplissage)
                if dictListeRemplissage.has_key(IDactivite) == True :
                    dictListeRemplissage[IDactivite].append(donnees)
                else:
                    dictListeRemplissage[IDactivite] = [(donnees),]
                dictListeRemplissage[IDactivite].sort()
        
        nbreColonnes = 0
        for IDactivite in self.listeActivites :
            # Compte colonne titre activité
            if len(self.listeActivites) > 1 and dictGroupeTemp.has_key(IDactivite) :
                nbreColonnes += 1
            if dictGroupeTemp.has_key(IDactivite) :
                for IDgroupe in dictGroupeTemp[IDactivite] :
                    if dictListeRemplissage.has_key(IDactivite) :
                        for ordre, IDunite_remplissage in dictListeRemplissage[IDactivite] :
                            nbreColonnes += 1
                if AFFICHE_TOTAUX == 1 and dictListeRemplissage.has_key(IDactivite) and len(dictListeRemplissage[IDactivite]) > 0 and len(dictGroupeTemp[IDactivite]) > 0 :
                    nbreColonnes += len(dictListeRemplissage[IDactivite])
        self.AppendCols(nbreColonnes)
        
        # Colonnes
        self.SetColLabelSize(45)
        numColonne = 0
        listeColonnesActivites = []
        for IDactivite in self.listeActivites :

            # Création de la colonne activité
            if len(self.listeActivites) > 1 and dictGroupeTemp.has_key(IDactivite) :
                renderer = MyColLabelRenderer("activite", COULEUR_COLONNE_ACTIVITE)
                self.SetColLabelRenderer(numColonne, renderer)
                self.SetColSize(numColonne, LARGEUR_COLONNE_ACTIVITE)
                self.SetColLabelValue(numColonne, "")
                listeColonnesActivites.append(numColonne)
                numColonne += 1

            # Création des colonnes unités
            if dictGroupeTemp.has_key(IDactivite):

                # Parcours des groupes
                if dictListeRemplissage.has_key(IDactivite) :
                    for IDgroupe in dictGroupeTemp[IDactivite] :
                        for ordre, IDunite_remplissage in dictListeRemplissage[IDactivite] :
                            renderer = MyColLabelRenderer("unite", None)
                            self.SetColLabelRenderer(numColonne, renderer)
                            if ABREGE_GROUPES == 0 :
                                nomGroupe = self.dictGroupes[IDgroupe]["nom"]
                            else :
                                nomGroupe = self.dictGroupes[IDgroupe]["abrege"]
                            if nomGroupe != "" : nomGroupe += u"\n"
                            nomUniteRemplissage = self.dictRemplissage[IDunite_remplissage]["abrege"]
                            largeurColonne = self.dictRemplissage[IDunite_remplissage]["largeur"]
                            if largeurColonne == None :
                                largeurColonne = LARGEUR_COLONNE_UNITE
                            labelColonne = u"%s%s" % (nomGroupe, nomUniteRemplissage)
                            self.SetColSize(numColonne, largeurColonne)
                            self.SetColLabelValue(numColonne, labelColonne)
                            numColonne += 1

                    # Création des colonnes totaux
                    if AFFICHE_TOTAUX == 1 and len(dictListeRemplissage[IDactivite]) > 0 and len(dictGroupeTemp[IDactivite]) > 0 :
                        for ordre, IDunite_remplissage in dictListeRemplissage[IDactivite] :
                            renderer = MyColLabelRenderer("unite", None)
                            self.SetColLabelRenderer(numColonne, renderer)
                            nomUniteRemplissage = self.dictRemplissage[IDunite_remplissage]["abrege"]
                            labelColonne = _(u"Total\n%s") % nomUniteRemplissage
                            self.SetColSize(numColonne, LARGEUR_COLONNE_UNITE)
                            self.SetColLabelValue(numColonne, labelColonne)
                            numColonne += 1
        
        # ------------------ Création des lignes -----------------------------
        
        # Tri des dates
        listeDatesTmp = self.dictOuvertures.keys()
        listeDates = []
        for dateDD in listeDatesTmp :
            listeDates.append(dateDD)
        listeDates.sort()
        nbreDates = len(listeDates)
        
        # Calcul du nombre de lignes
        self.AppendRows(nbreDates)
        
        # Span des colonnes Activités
        if nbreDates > 0 :
            for numColonneActivite in listeColonnesActivites :
                self.SetCellSize(0, numColonneActivite, nbreDates, 1)
        
        # Création des lignes
        self.dictLignes = {}
        numLigne = 0
        for dateDD in listeDates :
            ligne = Ligne(self, numLigne, dateDD, dictGroupeTemp, dictListeRemplissage, self.modeAffichage)
            self.dictLignes[numLigne] = ligne
            numLigne += 1

    def OnCellLeftDClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        ligne = self.dictLignes[numLigne]
        #if ligne.estSeparation == True:
        #    return
        case = ligne.dictCases[numColonne]

        # Recherche des conso
        try :
            listeConsoPresents = self.dictRemplissage[case.IDunite][case.date][case.IDgroupe]["listeConsoPresents"]
        except :
            listeConsoPresents = []

        if len(listeConsoPresents) > 0 :
            from Dlg import DLG_Liste_presents
            dlg = DLG_Liste_presents.Dialog(self, listeIDconso=listeConsoPresents)
            dlg.ShowModal()
            dlg.Destroy()

        event.Skip()

    def OnCellLeftClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        ligne = self.dictLignes[numLigne]
        if ligne.estSeparation == True :
            return
        case = ligne.dictCases[numColonne]
        case.OnClick()
        self.ClearSelection()
        event.Skip()
    
    def OnCellRightClick(self, event):
        numLigne = event.GetRow()
        numColonne = event.GetCol()
        ligne = self.dictLignes[numLigne]
        if ligne.estSeparation == True :
            return
        case = ligne.dictCases[numColonne]
        case.OnContextMenu()
        event.Skip()

    def OnLabelRightClick(self, event):
        numLigne = event.GetRow()
        if numLigne == -1 : return
        ligne = self.dictLignes[numLigne]
        ligne.OnContextMenu()
        event.Skip()
    
    def OnMouseOver(self, event):
        x, y = self.CalcUnscrolledPosition(event.GetPosition())
        numLigne = self.YToRow(y)
        numColonne = self.XToCol(x)
        if numLigne != -1 and numColonne != -1 : 
            ligne = self.dictLignes[numLigne]
            if ligne.estSeparation == True : 
                return
            case = ligne.dictCases[numColonne]
            if case != self.caseSurvolee :
                # Attribue une info-bulle
                self.GetGridWindow().SetToolTip(wx.ToolTip(case.GetTexteInfobulle()))
                tooltip = self.GetGridWindow().GetToolTip()
                tooltip.SetDelay(1500)
                self.caseSurvolee = case
        else:
            self.caseSurvolee = None
            self.GetGridWindow().SetToolTip(wx.ToolTip(""))
        event.Skip()
        
    def GetListeVacances(self):
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        return listeDonnees
        
    def GetListeUnites(self, listeUnitesUtilisees):
        dictListeUnites = {}
        dictUnites = {}
        conditionSQL = ""
        if len(listeUnitesUtilisees) == 0 : conditionSQL = "()"
        elif len(listeUnitesUtilisees) == 1 : conditionSQL = "(%d)" % listeUnitesUtilisees[0]
        else : conditionSQL = str(tuple(listeUnitesUtilisees))
        # Récupère la liste des unités
        req = """SELECT IDunite, IDactivite, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin, ordre, touche_raccourci
        FROM unites 
        WHERE IDunite IN %s
        ORDER BY ordre; """ % conditionSQL
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDunite, IDactivite, nom, abrege, type, heure_debut, heure_fin, date_debut, date_fin, ordre, touche_raccourci in listeDonnees :
            dictTemp = { "unites_incompatibles" : [], "IDunite" : IDunite, "IDactivite" : IDactivite, "nom" : nom, "abrege" : abrege, "type" : type, "heure_debut" : heure_debut, "heure_fin" : heure_fin, "date_debut" : date_debut, "date_fin" : date_fin, "ordre" : ordre, "touche_raccourci" : touche_raccourci}
            if dictListeUnites.has_key(IDactivite) :
                dictListeUnites[IDactivite].append(dictTemp)
            else:
                dictListeUnites[IDactivite] = [dictTemp,]
            dictUnites[IDunite] = dictTemp
        # Récupère les incompatibilités entre unités
##        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
##        FROM unites_incompat;"""
##        self.DB.ExecuterReq(req)
##        listeDonnees = self.DB.ResultatReq()
##        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
##            if dictUnites.has_key(IDunite) : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
##            if dictUnites.has_key(IDunite_incompatible) : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)
        return dictListeUnites, dictUnites
        
    def GetDictOuvertures(self, listeActivites=[], listePeriodes=[]):
        dictOuvertures = {}
        listeUnitesUtilisees = []
        listeGroupesUtilises = []
        # Get Conditions
        conditions = self.GetSQLdates(listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))

        # Importation des évènements
        req = """SELECT IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, capacite_max, heure_debut, heure_fin
        FROM evenements 
        WHERE IDactivite IN %s %s
        ORDER BY date, heure_debut;""" % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeTemp = self.DB.ResultatReq()
        dictEvenements = {}
        for IDevenement, IDactivite, IDunite, IDgroupe, date, nom, description, capacite_max, heure_debut, heure_fin in listeTemp :
            date = UTILS_Dates.DateEngEnDateDD(date)
            heure_debut = UTILS_Dates.HeureStrEnTime(heure_debut)
            heure_fin = UTILS_Dates.HeureStrEnTime(heure_fin)
            dict_evenement = {"IDevenement" : IDevenement, "IDactivite" : IDactivite, "IDunite" : IDunite, "IDgroupe" : IDgroupe,
                              "date": date, "nom" : nom, "description" : description, "capacite_max" : capacite_max,
                              "heure_debut": heure_debut, "heure_fin" : heure_fin}

            key = (IDunite, IDgroupe, date)
            if dictEvenements.has_key(key) == False:
                dictEvenements[key] = []
            dictEvenements[key].append(dict_evenement)

        # Importation des ouvertures
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures 
        WHERE IDactivite IN %s %s
        ORDER BY date; """ % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
            if IDunite not in listeUnitesUtilisees :
                listeUnitesUtilisees.append(IDunite)
            if IDgroupe not in listeGroupesUtilises :
                listeGroupesUtilises.append(IDgroupe)
            date = UTILS_Dates.DateEngEnDateDD(date)

            key = (IDunite, IDgroupe, date)
            if dictEvenements.has_key(key):
                liste_evenements = dictEvenements[key]
            else :
                liste_evenements = []

            dictValeurs = {"IDouverture": IDouverture, "etat": True, "initial": True, "liste_evenements": liste_evenements}
            if dictOuvertures.has_key(date) == False :
                dictOuvertures[date] = {}
            if dictOuvertures[date].has_key(IDgroupe) == False :
                dictOuvertures[date][IDgroupe] = {}
            if dictOuvertures[date][IDgroupe].has_key(IDunite) == False :
                dictOuvertures[date][IDgroupe][IDunite] = dictValeurs

        return dictOuvertures, listeUnitesUtilisees, listeGroupesUtilises

    def GetDictRemplissage(self, listeActivites=[], listePeriodes=[]):
        dictRemplissage = {}
        dictUnitesRemplissage = {}
        dictConsoAttente = {}
        dictRemplissageEvenements = {}
        
        # Get Conditions
        conditions = self.GetSQLdates(listePeriodes)
        if len(conditions) > 0 :
            conditionDates = " AND %s" % conditions
        else:
            conditionDates = ""
        
        conditions2 = self.GetSQLdates2(listePeriodes)
        if len(conditions2) > 0 :
            conditionDates2 = " AND %s" % conditions2
        else:
            conditionDates2 = ""
            
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        # Récupération des unités de remplissage
        req = """SELECT IDunite_remplissage_unite, IDunite_remplissage, IDunite
        FROM unites_remplissage_unites; """ 
        self.DB.ExecuterReq(req)
        listeUnites = self.DB.ResultatReq()
        for IDunite_remplissage_unite, IDunite_remplissage, IDunite in listeUnites :
            if dictUnitesRemplissage.has_key(IDunite) == False :
                dictUnitesRemplissage[IDunite] = [IDunite_remplissage,]
            else:
                dictUnitesRemplissage[IDunite].append(IDunite_remplissage)
                                
        # Récupération des unités de remplissage
        req = """SELECT IDunite_remplissage, IDactivite, ordre, nom, abrege, date_debut, date_fin, seuil_alerte, heure_min, heure_max, etiquettes, largeur
        FROM unites_remplissage 
        WHERE IDactivite IN %s %s
        AND (afficher_page_accueil IS NULL OR afficher_page_accueil=1)
        ;""" % (conditionActivites, conditionDates2)
        self.DB.ExecuterReq(req)
        listeUnitesRemplissage = self.DB.ResultatReq()
        for IDunite_remplissage, IDactivite, ordre, nom, abrege, date_debut, date_fin, seuil_alerte, heure_min, heure_max, etiquettes, largeur in listeUnitesRemplissage :
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)

            # Mémorise l'unité de remplissage
            dictRemplissage[IDunite_remplissage] = {"IDactivite" : IDactivite,
                                                                        "ordre" : ordre,
                                                                        "nom" : nom,
                                                                        "abrege" : abrege,
                                                                        "date_debut" : DateEngEnDateDD(date_debut),
                                                                        "date_fin" : DateEngEnDateDD(date_fin),
                                                                        "seuil_alerte" : seuil_alerte,
                                                                        "heure_min" : heure_min,
                                                                        "heure_max" : heure_max,
                                                                        "etiquettes" : etiquettes,
                                                                        "largeur" : largeur,
                                                                        }
                                                                        
        # Récupération des paramètres de remplissage
        req = """SELECT IDremplissage, IDactivite, IDunite_remplissage, IDgroupe, date, places
        FROM remplissage 
        WHERE IDactivite IN %s %s
        ORDER BY date;""" % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeRemplissage = self.DB.ResultatReq()
        for IDremplissage, IDactivite, IDunite_remplissage, IDgroupe, date, places in listeRemplissage :
            if places == 0 : places = None
            dateDD = DateEngEnDateDD(date)
            dictValeursTemp = { "nbrePlacesInitial" : places, "nbrePlacesPrises" : 0, "nbrePlacesAttente" : 0 }
            if dictRemplissage.has_key(IDunite_remplissage) == False:
                dictRemplissage[IDunite_remplissage] = {}
            if dictRemplissage[IDunite_remplissage].has_key(dateDD) == False:
                dictRemplissage[IDunite_remplissage][dateDD] = {}
            if dictRemplissage[IDunite_remplissage][dateDD].has_key(IDgroupe) == False:
                dictRemplissage[IDunite_remplissage][dateDD][IDgroupe] = dictValeursTemp

        # Récupération des consommations existantes 
        req = """SELECT IDconso, IDactivite, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, quantite, etiquettes, IDevenement
        FROM consommations 
        WHERE IDactivite IN %s %s; """ % (conditionActivites, conditionDates)
        self.DB.ExecuterReq(req)
        listeConso = self.DB.ResultatReq()
        for IDconso, IDactivite, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, quantite, etiquettesConso, IDevenement in listeConso :
            dateDD = DateEngEnDateDD(date)
            etiquettesConso = UTILS_Texte.ConvertStrToListe(etiquettesConso)

            # Mémorisation spéciale si c'est un évènement
            if IDevenement != None and etat in ["reservation", "present", "attente"] :
                if dictRemplissageEvenements.has_key(IDevenement) == False:
                    dictRemplissageEvenements[IDevenement] = {"reservation": 0, "present": 0, "attente": 0}
                dictRemplissageEvenements[IDevenement][etat] += 1

            # Quantité
            if quantite == None :
                quantite = 1
                        
            # Mémorisation des nbre de places
            if dictUnitesRemplissage.has_key(IDunite) :
                for IDunite_remplissage in dictUnitesRemplissage[IDunite] :
                    if dictRemplissage.has_key(IDunite_remplissage) == False :
                        dictRemplissage[IDunite_remplissage] = {}
                    if dictRemplissage[IDunite_remplissage].has_key(dateDD) == False :
                        dictRemplissage[IDunite_remplissage][dateDD] = {}
                    if dictRemplissage[IDunite_remplissage][dateDD].has_key(IDgroupe) == False :
                        dictRemplissage[IDunite_remplissage][dateDD][IDgroupe] = {}
                    if dictRemplissage[IDunite_remplissage][dateDD][IDgroupe].has_key("nbrePlacesPrises") == False :
                        dictRemplissage[IDunite_remplissage][dateDD][IDgroupe]["nbrePlacesPrises"] = 0
                        dictRemplissage[IDunite_remplissage][dateDD][IDgroupe]["listeConsoPresents"] = []

                    # Réservations
                    if etat in ["reservation", "present"] :
                        valide = True
                        
                        # Vérifie s'il y a une plage horaire conditionnelle :
                        try :
                            heure_min = dictRemplissage[IDunite_remplissage]["heure_min"]
                            heure_max = dictRemplissage[IDunite_remplissage]["heure_max"]
                            if heure_min != None and heure_max != None and heure_debut != None and heure_fin != None :
                                heure_min_TM = HeureStrEnTime(heure_min)
                                heure_max_TM = HeureStrEnTime(heure_max)
                                heure_debut_TM = HeureStrEnTime(heure_debut)
                                heure_fin_TM = HeureStrEnTime(heure_fin)
                                
                                if heure_debut_TM <= heure_max_TM and heure_fin_TM >= heure_min_TM :
                                    valide = True
                                else:
                                    valide = False
                        except :
                            pass
                        
                        # Vérifie si condition étiquettes
                        if dictRemplissage[IDunite_remplissage].has_key("etiquettes") :
                            etiquettes = dictRemplissage[IDunite_remplissage]["etiquettes"]
                            if len(etiquettes) > 0 :
                                etiquettesCommunes = set(etiquettes) & set(etiquettesConso)
                                if len(etiquettesCommunes) == 0 :
                                    valide = False

                        # Mémorisation de la place prise
                        if valide == True :
                            dictRemplissage[IDunite_remplissage][dateDD][IDgroupe]["nbrePlacesPrises"] += quantite
                            dictRemplissage[IDunite_remplissage][dateDD][IDgroupe]["listeConsoPresents"].append(IDconso)

                    # Mémorisation des places sur liste d'attente
                    if etat == "attente" :
                        if dictConsoAttente.has_key(dateDD) == False :
                            dictConsoAttente[dateDD] = {}
                        if dictConsoAttente[dateDD].has_key(IDgroupe) == False :
                            dictConsoAttente[dateDD][IDgroupe] = {}
                        if dictConsoAttente[dateDD][IDgroupe].has_key(IDunite_remplissage) == False :
                            dictConsoAttente[dateDD][IDgroupe][IDunite_remplissage] = quantite
                        else:
                            dictConsoAttente[dateDD][IDgroupe][IDunite_remplissage] += quantite

        # Renvoie les données
        return dictRemplissage, dictUnitesRemplissage, dictConsoAttente, dictRemplissageEvenements
    


    def GetDictGroupes(self):
        dictGroupes = {}
        req = """SELECT IDgroupe, IDactivite, nom, ordre, abrege
        FROM groupes
        ORDER BY nom;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        dictGroupes[0] = { "IDactivite" : 0, "nom" : _(u"Sans groupe"), "ordre" : 0, "abrege" : _(u"SANS")}
        for IDgroupe, IDactivite, nom, ordre, abrege in listeDonnees :
            if IDgroupe in self.listeGroupesUtilises :
                if abrege == None : abrege = u""
                dictGroupes[IDgroupe] = { "IDactivite" : IDactivite, "nom" : nom, "ordre" : ordre, "abrege" : abrege }
        return dictGroupes
        
    def GetSQLdates(self, listePeriodes=[]):
        """ Avec date """
        texteSQL = ""
        for date_debut, date_fin in listePeriodes :
            texteSQL += "(date>='%s' AND date<='%s') OR " % (date_debut, date_fin)
        if len(texteSQL) > 0 :
            texteSQL = "(" + texteSQL[:-4] + ")"
        else:
            texteSQL = "date='3000-01-01'"
        return texteSQL

    def GetSQLdates2(self, listePeriodes=[]):
        """ Avec date_debut et date_fin """
        texteSQL = ""
        for date_debut, date_fin in listePeriodes :
            texteSQL += "(date_fin>='%s' AND date_debut<='%s') OR " % (date_debut, date_fin)
        if len(texteSQL) > 0 :
            texteSQL = "(" + texteSQL[:-4] + ")"
        else:
            texteSQL = "date_debut='3000-01-01'"
        return texteSQL    

    def Importation_activites(self):
        
        # Recherche les activites disponibles
        dictActivites = {}
        req = """SELECT activites.IDactivite, activites.nom, abrege, date_debut, date_fin
        FROM activites
        LEFT JOIN categories_tarifs ON categories_tarifs.IDactivite = activites.IDactivite
        ORDER BY activites.nom;"""
        self.DB.ExecuterReq(req)
        listeActivites = self.DB.ResultatReq()      
        for IDactivite, nom, abrege, date_debut, date_fin in listeActivites :
            if date_debut != None : date_debut = DateEngEnDateDD(date_debut)
            if date_fin != None : date_fin = DateEngEnDateDD(date_fin)
            dictTemp = { "nom" : nom, "abrege" : abrege, "date_debut" : date_debut, "date_fin" : date_fin }
            dictActivites[IDactivite] = dictTemp
        return dictActivites
    
    def GetEtatPlaces(self):
        """ Fonction qui sert au DLG_Attente pour savoir si des places se sont libérées """
        dictEtatPlaces = {}
        # Parcours les lignes
        for numLigne, ligne in self.dictLignes.iteritems() :
            # Parcours les cases :
            for numColonne, case in ligne.dictCases.iteritems() :
                if case.typeCase == "consommation" :
                    dictInfosPlaces = case.dictInfosPlaces
                    liste_evenements = case.liste_evenements
                    date = case.date
                    IDgroupe = case.IDgroupe
                    IDuniteRemplissage = case.IDunite
                    IDactivite = case.IDactivite
                    # Mémorisation dans un dict
                    if len(liste_evenements) > 0 :
                        listeTemp = [(evenement.IDevenement, evenement) for evenement in liste_evenements]
                    else :
                        listeTemp = [(None, None),]
                    for IDevenement, evenement in listeTemp :
                        dictEtatPlaces[(date, IDactivite, IDgroupe, IDuniteRemplissage, IDevenement)] = {"remplissage" : dictInfosPlaces, "evenement" : evenement}
        return dictEtatPlaces
    
    # def GetLargeurColonneUnite(self):
    #     return LARGEUR_COLONNE_UNITE
    #
    # def SetLargeurColonneUnite(self, largeur=60):
    #     global LARGEUR_COLONNE_UNITE
    #     LARGEUR_COLONNE_UNITE = largeur
    #     UTILS_Config.SetParametre("largeur_colonne_unite_remplissage", largeur)

    def GetAbregeGroupes(self):
        return ABREGE_GROUPES
    
    def SetAbregeGroupes(self, etat=0):
        global ABREGE_GROUPES
        ABREGE_GROUPES = int(etat)
        UTILS_Config.SetParametre("remplissage_abrege_groupes", etat)

    def GetAfficheTotaux(self):
        return AFFICHE_TOTAUX

    def SetAfficheTotaux(self, etat=0):
        global AFFICHE_TOTAUX
        AFFICHE_TOTAUX = int(etat)
        UTILS_Config.SetParametre("remplissage_affiche_totaux", etat)

    def GetDataImpression(self):
        from Outils import printout
##        import wx.lib.printout as printout
        
        prt = printout.PrintTable(None)
        prt.SetLandscape() 
        data = []
        
        nbreLignes = self.GetNumberRows()
        nbreColonnes = self.GetNumberCols()
        if nbreLignes == 0 or nbreColonnes == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a rien à imprimer !"), "Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return None
        
        # Entete des colonnes
        ligne = [u"",]
        largeursColonnes = [1.8,]
        for numCol in range(0, nbreColonnes):
            valeur = self.GetColLabelValue(numCol)
            ligne.append(valeur.replace("\n", " "))
            largeursColonnes.append(0.5)
        data.append(ligne)
        
        # Contenu du tableau
        dictCouleurs = {}
        listeCouleursEntetes = {}
        for numLigne in range(0, nbreLignes):
            ligne = []
            labelLigne = self.GetRowLabelValue(numLigne)
            couleurEntete = self.dictLignes[numLigne].renderer._bgcolor
            listeCouleursEntetes[numLigne] = couleurEntete
            ligne.append(labelLigne)
            for numCol in range(0, nbreColonnes):
                couleur = self.GetCellRenderer(numLigne, numCol).case.couleurFond
                dictCouleurs[(numLigne, numCol)] = couleur
                ligne.append(self.GetCellValue(numLigne, numCol))
            data.append(ligne)
        
        prt.data = data
        prt.set_column = largeursColonnes
        prt.SetRowSpacing(4, 4)
        
        # Aligne toutes les colonnes au milieu
        for numCol in range(0, nbreColonnes+1):
            prt.SetColAlignment(numCol, wx.ALIGN_CENTRE)
        
        # Colore les entetes de colonnes
        for numCol in range(0, nbreColonnes+1) :
            prt.SetCellColour(0, numCol, (210, 210, 210) )
            
        # Colore les entetes de lignes
        for numLigne, couleur in listeCouleursEntetes.iteritems() :
            prt.SetCellColour(numLigne+1, 0, couleur)
        
        # Colore les cases du contenu
        for coords, couleur in dictCouleurs.iteritems() :
            numLigne, numCol = coords
            prt.SetCellColour(numLigne+1, numCol+1, couleur)
            
        prt.SetHeader(_(u"Effectifs"), colour = wx.NamedColour('BLACK'))
##        prt.SetHeader("Le ", type = "Date & Time", align=wx.ALIGN_RIGHT, indent = -1, colour = wx.NamedColour('BLACK'))
        prt.SetFooter("Page ", colour = wx.NamedColour('BLACK'), type ="Num")
        return prt

    def Apercu(self):
        from Utils import UTILS_Printer
        prt = self.GetDataImpression()
        if prt == None : return
        # Preview
        data = wx.PrintDialogData(prt.printData)
        printout = prt.GetPrintout()
        printout2 = prt.GetPrintout()
        preview = wx.PrintPreview(printout, printout2, data)
        if not preview.Ok():
            wx.MessageBox(_(u"Désolé, un problème a été rencontré dans l'aperçu avant impression..."), "Erreur", wx.OK)
            return
##        frm = UTILS_Printer.PreviewFrame(preview, None)
        frame = wx.GetApp().GetTopWindow() 
        frm = wx.PreviewFrame(preview, None, _(u"Aperçu avant impression"))
        frm.Initialize()
        frm.MakeModal(False)
        frm.SetPosition(frame.GetPosition())
        frm.SetSize(frame.GetSize())
        frm.Show(True)
    
    def Imprimer(self):
        prt = self.GetDataImpression()
        if prt == None : return
        prt.Print()

    def ExportTexte(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportTexte(grid=self, titre=_(u"Remplissage"))
        
    def ExportExcel(self, event=None):
        from Utils import UTILS_Export
        UTILS_Export.ExportExcel(grid=self, titre=_(u"Remplissage"))

    def OnChangeColSize(self, event):
        numColonne = event.GetRowOrCol()
        largeur = self.GetColSize(numColonne)
        if len(self.dictLignes) == 0: return
        ligne = self.dictLignes[0]
        case = ligne.dictCases[numColonne]

        if case.typeCase == "activite":
            self.SetColSize(numColonne, LARGEUR_COLONNE_ACTIVITE)

        if case.typeCase == "consommation" and case.estTotal == True :
            self.SetColSize(numColonne, LARGEUR_COLONNE_UNITE)

        if case.typeCase == "consommation" and case.estTotal == False :
            DB = GestionDB.DB()
            DB.ReqMAJ("unites_remplissage", [("largeur", int(largeur)),], "IDunite_remplissage", case.IDunite)
            DB.Close()



# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.grille = CTRL(panel)
        self.grille.Tests()
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.grille, 1, wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.SetSize((750, 400))
        self.Layout()
        
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", name="test")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
    GestionDB.AfficheConnexionOuvertes() 