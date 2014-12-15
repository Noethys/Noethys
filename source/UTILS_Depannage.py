#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import GestionDB
import UTILS_Dates
from UTILS_Decimal import FloatToDecimal as FloatToDecimal
import wx.lib.agw.pybusyinfo as PBI


def EcritStatusbar(texte=u""):
    try :
        topWindow = wx.GetApp().GetTopWindow() 
        topWindow.SetStatusText(texte)
    except : 
        pass

# --------------------------------------------------------------------------------------------------------------------------------------------

class Anomalie():
    def __init__(self, *args, **kwds):
        self.kwds = kwds
        self.label = kwds["label"]
        self.corrige = False

    def Correction(self, DB=None):
        pass

# --------------------------------------------------------------------------------------------------------------------------------------------

class InscriptionsSansIndividus(Anomalie):
    def Correction(self, DB=None):
        IDinscription = self.kwds["IDinscription"]
        IDindividu = self.kwds["IDindividu"]
        # Test de correction
        DB.ReqDEL("inscriptions", "IDinscription", IDinscription)
        self.corrige = True


class CotisationsSansIndividus(Anomalie):
    def Correction(self, DB=None):
        IDcotisation = self.kwds["IDcotisation"]
        IDindividu = self.kwds["IDindividu"]
        IDprestation = self.kwds["IDprestation"]
        DB.ReqDEL("cotisations", "IDcotisation", IDcotisation)
        if IDprestation != None :
            DB.ReqDEL("prestations", "IDprestation", IDprestation)
            DB.ReqDEL("ventilation", "IDprestation", IDprestation)
        self.corrige = True

class CotisationsSansFamilles(Anomalie):
    def Correction(self, DB=None):
        IDcotisation = self.kwds["IDcotisation"]
        IDfamille = self.kwds["IDfamille"]
        IDprestation = self.kwds["IDprestation"]
        DB.ReqDEL("cotisations", "IDcotisation", IDcotisation)
        if IDprestation != None :
            DB.ReqDEL("prestations", "IDprestation", IDprestation)
            DB.ReqDEL("ventilation", "IDprestation", IDprestation)
        self.corrige = True

class PrestationsSansFamilles(Anomalie):
    def Correction(self, DB=None):
        IDprestation = self.kwds["IDprestation"]
        IDfamille = self.kwds["IDfamille"]
        DB.ReqDEL("prestations", "IDprestation", IDprestation)
        DB.ReqDEL("ventilation", "IDprestation", IDprestation)
        self.corrige = True

class VentilationsSansPrestations(Anomalie):
    def Correction(self, DB=None):
        IDventilation = self.kwds["IDventilation"]
        IDprestation = self.kwds["IDprestation"]
        IDreglement = self.kwds["IDreglement"]
        IDfamille = self.kwds["IDfamille"]
        DB.ReqDEL("ventilation", "IDventilation", IDventilation)
        self.corrige = True

class VentilationsSansReglements(Anomalie):
    def Correction(self, DB=None):
        IDventilation = self.kwds["IDventilation"]
        IDprestation = self.kwds["IDprestation"]
        IDreglement = self.kwds["IDreglement"]
        IDfamille = self.kwds["IDfamille"]
        DB.ReqDEL("ventilation", "IDventilation", IDventilation)
        self.corrige = True

class IndividusIncomplets(Anomalie):
    def Correction(self, DB=None):
        IDindividu = self.kwds["IDindividu"]
        IDcivilite = self.kwds["IDcivilite"]
        nom = self.kwds["nom"]
        if IDcivilite == None : IDcivilite = 1
        if nom == None : nom = "INCONNU"
        DB.ReqMAJ("individus", [("IDcivilite", IDcivilite), ("nom", nom)], "IDindividu", IDindividu)
        self.corrige = True

class FamillesIncompletes(Anomalie):
    def Correction(self, DB=None):
        IDfamille = self.kwds["IDfamille"]
        DB.ReqMAJ("familles", [("IDcompte_payeur", IDfamille),], "IDfamille", IDfamille)
        self.corrige = True

class InscriptionsIncompletes(Anomalie):
    def Correction(self, DB=None):
        IDinscription = self.kwds["IDinscription"]
        IDfamille = self.kwds["IDfamille"]
        IDcompte_payeur = self.kwds["IDcompte_payeur"]
        DB.ReqMAJ("inscriptions", [("IDcompte_payeur", IDfamille),], "IDinscription", IDinscription)
        self.corrige = True

class ConsommationsIncompletes(Anomalie):
    def Correction(self, DB=None):
        IDconso = self.kwds["IDconso"]
        IDcompte_payeur = self.kwds["IDcompte_payeur"]
        DB.ReqMAJ("consommations", [("IDcompte_payeur", IDcompte_payeur),], "IDconso", IDconso)
        self.corrige = True

class FacturesAsupprimer(Anomalie):
    def Correction(self, DB=None):
        IDfacture = self.kwds["IDfacture"]
        DB.ReqDEL("factures", "IDfacture", IDfacture)
        self.corrige = True

class FacturesRecalcul(Anomalie):
    def Correction(self, DB=None):
        IDfacture = self.kwds["IDfacture"]
        totalFacture = self.kwds["totalFacture"]
        regleFacture = self.kwds["regleFacture"]
        soldeFacture = self.kwds["soldeFacture"]
        montantTotalPrestations = self.kwds["montantTotalPrestations"]
        # Recalcul des montants des factures
        if montantTotalPrestations < totalFacture : 
            totalFacture = montantTotalPrestations
        if montantTotalPrestations < regleFacture : 
            regleFacture = montantTotalPrestations
        soldeFacture = totalFacture - regleFacture
        DB.ReqMAJ("factures", [("total", float(totalFacture)), ("regle", float(regleFacture)), ("solde", float(soldeFacture))], "IDfacture", IDfacture)
        self.corrige = True

class CorrigerHeuresConso(Anomalie):
    def Correction(self, DB=None):
        IDconso = self.kwds["IDconso"]
        heure_debut = self.kwds["heure_debut"]
        heure_fin = self.kwds["heure_fin"]
        date = self.kwds["date"]
        individu = self.kwds["individu"]
        
        if heure_debut != None : 
            dlg = wx.TextEntryDialog(None, u"Corrigez l'heure de début de la consommation du %s de %s :\n\n(Obligatoirement au format HH:MM)" % (date.strftime("%d/%m/%Y"), individu), u"Correction d'une heure", heure_debut)
            if dlg.ShowModal() == wx.ID_OK:
                DB.ReqMAJ("consommations", [("heure_debut", dlg.GetValue()),], "IDconso", IDconso)
                self.corrige = True
            else :
                self.corrige = False
            dlg.Destroy()
        
        if heure_fin != None : 
            dlg = wx.TextEntryDialog(None, u"Corrigez l'heure de fin de la consommation du %s de %s :\n\n(Obligatoirement au format HH:MM)" % (date.strftime("%d/%m/%Y"), individu), u"Correction d'une heure", heure_fin)
            if dlg.ShowModal() == wx.ID_OK:
                DB.ReqMAJ("consommations", [("heure_fin", dlg.GetValue()),], "IDconso", IDconso)
                self.corrige = True
            else :
                self.corrige = False
            dlg.Destroy()

class LiensTronques(Anomalie):
    def Correction(self, DB=None):
        IDlien = self.kwds["IDlien"]
        IDindividu = self.kwds["IDindividu"]
        DB.ReqDEL("liens", "IDlien", IDlien)
        self.corrige = True

class RattachementsTronques(Anomalie):
    def Correction(self, DB=None):
        IDrattachement = self.kwds["IDrattachement"]
        IDfamille = self.kwds["IDfamille"]
        IDindividu = self.kwds["IDindividu"]
        DB.ReqDEL("rattachements", "IDrattachement", IDrattachement)
        self.corrige = True

class LiensErrones(Anomalie):
    def Correction(self, DB=None):
        IDfamille = self.kwds["IDfamille"]
        listeIDlien = self.kwds["listeIDlien"]
        for IDlien in listeIDlien :
            DB.ReqDEL("liens", "IDlien", IDlien)
        self.corrige = True


class VentilationsExcessives(Anomalie):
    def Correction(self, DB=None):
        IDventilation = self.kwds["IDventilation"]
        IDprestation = self.kwds["IDprestation"]
        IDreglement = self.kwds["IDreglement"]
        IDfamille = self.kwds["IDfamille"]
        DB.ReqDEL("ventilation", "IDventilation", IDventilation)
        self.corrige = True


# --------------------------------------------------------------------------------------------------------------------------------------------

class Depannage():
    def __init__(self, parent=None):
        self.parent = parent
    
    def GetTexte(self):
        self.RechercheDonnees() 
        texte = u""
        for labelProbleme, labelCorrection, listeDonnees in self.listeResultats :
            texte += u"<P><B>%s (%d) :</B><FONT SIZE=2><BR>" % (labelProbleme, len(listeDonnees))
            
            if len(listeDonnees) > 0 :
                for anomalie in listeDonnees :
                    texteCorrection = u"<A HREF='http://www.noethys.com'>Correction proposée : %s</A>" % labelCorrection
                    texte += u"&nbsp;&nbsp;&nbsp;<IMG SRC='Images/16x16/Interdit2.png'>&nbsp;%s. %s<BR>" % (anomalie.label, texteCorrection)
            else :
                    texte += u"&nbsp;&nbsp;&nbsp;<IMG SRC='Images/16x16/Ok4.png'>&nbsp;Aucune anomalie détectée...<BR>"
            texte += u"</FONT></P>"
        return texte
    
    def GetResultats(self):
        self.RechercheDonnees() 
        return self.listeResultats
    
    def GetNbreAnomalies(self):
        nbreAnomalies = 0
        try :
            for labelAnomalie, labelCorrection, listeAnomalies in self.listeResultats :
                nbreAnomalies += len(listeAnomalies)
        except :
            pass
        return nbreAnomalies

    def RechercheDonnees(self):        
        self.listeResultats = []
        EcritStatusbar(u"Recherche d'anomalies en cours...   Veuillez patientez...")
        try :
            dlgAttente = PBI.PyBusyInfo(u"Recherche d'anomalies en cours...", parent=self.parent, title=u"Merci de patienter", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
            wx.Yield() 
        except :
            dlgAttente = None
        
        # Init DB
        self.DB = GestionDB.DB()
        # Recherches
        self.InscriptionsSansIndividus()
        self.CotisationsSansIndividus()
        self.CotisationsSansFamilles() 
        self.PrestationsSansFamilles() 
        self.VentilationsSansPrestations() 
        self.VentilationsSansReglements() 
        self.IndividusIncomplets()
        self.FamillesIncompletes()
        self.InscriptionsIncompletes()
        self.ConsommationsIncompletes()
        self.FacturesErronees()
        self.ConsommationsErronees() 
        self.LiensTronques() 
        self.RattachementsTronques() 
        self.LiensErrones() 
        self.VentilationExcessive()
                
        # Fermeture DB
        self.DB.Close()
        
        del dlgAttente
        EcritStatusbar("")
        
    def InscriptionsSansIndividus(self):
        labelProbleme = u"Inscriptions sans individus associés"
        labelCorrection = u"Supprimer l'inscription"
        req = """SELECT IDinscription, inscriptions.IDactivite, activites.nom, inscriptions.date_inscription, inscriptions.IDindividu 
        FROM inscriptions 
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu 
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        WHERE individus.IDindividu IS NULL;"""
        self.DB.ExecuterReq(req)
        listePrestations = self.DB.ResultatReq()
        listeTemp = []
        for IDinscription, IDactivite, nomActivite, dateInscription, IDindividu in listePrestations :
            label = u"Individu ID%d inscrit le %s à l'activité %s" % (IDindividu, UTILS_Dates.DateEngFr(dateInscription), nomActivite)
            listeTemp.append(InscriptionsSansIndividus(label=label, IDinscription=IDinscription, IDindividu=IDindividu))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def CotisationsSansIndividus(self):
        labelProbleme = u"Cotisations sans individus associés"
        labelCorrection = u"Supprimer la cotisation"
        req = """SELECT IDcotisation, types_cotisations.nom, unites_cotisations.nom, cotisations.date_saisie, cotisations.IDindividu, cotisations.IDprestation
        FROM cotisations 
        LEFT JOIN individus ON individus.IDindividu = cotisations.IDindividu 
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN unites_cotisations ON unites_cotisations.IDunite_cotisation = cotisations.IDunite_cotisation
        WHERE individus.IDindividu IS NULL AND cotisations.IDindividu IS NOT NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDcotisation, nomType, nomUnite, dateSaisie, IDindividu, IDprestation in listeDonnees :
            label = u"Cotisation ID%d de type '%s - %s' saisie le %s pour l'individu ID%d" % (IDcotisation, nomType, nomUnite, UTILS_Dates.DateEngFr(dateSaisie), IDindividu)
            listeTemp.append(CotisationsSansIndividus(label=label, IDcotisation=IDcotisation, IDindividu=IDindividu, IDprestation=IDprestation))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def CotisationsSansFamilles(self):
        labelProbleme = u"Cotisations sans familles associées"
        labelCorrection = u"Supprimer la cotisation"
        req = """SELECT IDcotisation, types_cotisations.nom, unites_cotisations.nom, cotisations.date_saisie, cotisations.IDfamille, cotisations.IDprestation
        FROM cotisations 
        LEFT JOIN familles ON familles.IDfamille = cotisations.IDfamille
        LEFT JOIN types_cotisations ON types_cotisations.IDtype_cotisation = cotisations.IDtype_cotisation
        LEFT JOIN unites_cotisations ON unites_cotisations.IDunite_cotisation = cotisations.IDunite_cotisation
        WHERE familles.IDfamille IS NULL AND cotisations.IDfamille IS NOT NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDcotisation, nomType, nomUnite, dateSaisie, IDfamille, IDprestation in listeDonnees :
            label = u"Cotisation ID%d de type '%s - %s' saisie le %s pour la famille ID%d" % (IDcotisation, nomType, nomUnite, UTILS_Dates.DateEngFr(dateSaisie), IDfamille)
            listeTemp.append(CotisationsSansFamilles(label=label, IDcotisation=IDcotisation, IDfamille=IDfamille, IDprestation=IDprestation))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def PrestationsSansFamilles(self):
        labelProbleme = u"Prestations sans familles associées"
        labelCorrection = u"Supprimer la prestation"
        req = """SELECT IDprestation, date, label, prestations.IDfamille
        FROM prestations 
        LEFT JOIN familles ON familles.IDfamille = prestations.IDfamille
        WHERE familles.IDfamille IS NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDprestation, date, label, IDfamille in listeDonnees :
            label = u"Prestation ID%d '%s' saisie le %s pour la famille ID%d" % (IDprestation, label, UTILS_Dates.DateEngFr(date), IDfamille)
            listeTemp.append(PrestationsSansFamilles(label=label, IDprestation=IDprestation, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def VentilationsSansPrestations(self):
        labelProbleme = u"Ventilations sans prestations associées"
        labelCorrection = u"Supprimer la ventilation"
        req = """SELECT IDventilation, ventilation.IDprestation, IDreglement, comptes_payeurs.IDfamille
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = ventilation.IDcompte_payeur
        WHERE prestations.IDprestation IS NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDventilation, IDprestation, IDreglement, IDfamille in listeDonnees :
            label = u"Ventilation ID%d pour la prestation ID%d et le règlement ID%d pour la famille ID%d" % (IDventilation, IDprestation, IDreglement, IDfamille)
            listeTemp.append(VentilationsSansPrestations(label=label, IDventilation=IDventilation, IDprestation=IDprestation, IDreglement=IDreglement, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def VentilationsSansReglements(self):
        labelProbleme = u"Ventilations sans règlements associés"
        labelCorrection = u"Supprimer la ventilation"
        req = """SELECT IDventilation, IDprestation, ventilation.IDreglement, comptes_payeurs.IDfamille
        FROM ventilation
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = ventilation.IDcompte_payeur
        WHERE reglements.IDreglement IS NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDventilation, IDprestation, IDreglement, IDfamille in listeDonnees :
            label = u"Ventilation ID%d pour la prestation ID%d et le règlement ID%d pour la famille ID%d" % (IDventilation, IDprestation, IDreglement, IDfamille)
            listeTemp.append(VentilationsSansReglements(label=label, IDventilation=IDventilation, IDprestation=IDprestation, IDreglement=IDreglement, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def IndividusIncomplets(self):
        labelProbleme = u"Fiches individuelles tronquées"
        labelCorrection = u"Modifier la civilité et/ou le nom de famille"
        req = """SELECT IDindividu, IDcivilite, nom, prenom
        FROM individus 
        WHERE IDcivilite IS NULL OR nom IS NULL;"""
        self.DB.ExecuterReq(req)
        listeIndividus = self.DB.ResultatReq()
        listeTemp = []
        for IDindividu, IDcivilite, nom, prenom in listeIndividus :
            label = u"Individu ID%d (%s %s)" % (IDindividu, nom, prenom)
            listeTemp.append(IndividusIncomplets(label=label, IDindividu=IDindividu, IDcivilite=IDcivilite, nom=nom))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def FamillesIncompletes(self):
        labelProbleme = u"Fiches familles tronquées"
        labelCorrection = u"Réparer la fiche famille"
        req = """SELECT IDfamille, IDcompte_payeur
        FROM familles 
        WHERE IDcompte_payeur IS NULL;"""
        self.DB.ExecuterReq(req)
        listeFamilles = self.DB.ResultatReq()
        listeTemp = []
        for IDfamille, IDcompte_payeur in listeFamilles :
            label = u"Famille ID%d" % IDfamille
            listeTemp.append(FamillesIncompletes(label=label, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def InscriptionsIncompletes(self):
        labelProbleme = u"Inscriptions tronquées"
        labelCorrection = u"Réparer la table des inscriptions"
        req = """SELECT IDinscription, IDfamille, IDindividu, IDcompte_payeur
        FROM inscriptions 
        WHERE IDcompte_payeur IS NULL;"""
        self.DB.ExecuterReq(req)
        listeInscriptions = self.DB.ResultatReq()
        listeTemp = []
        for IDinscription, IDfamille, IDindividu, IDcompte_payeur in listeInscriptions :
            label = u"Inscription ID%d (Famille ID%d Individu ID%d)" % (IDinscription, IDfamille, IDindividu)
            listeTemp.append(InscriptionsIncompletes(label=label, IDinscription=IDinscription, IDfamille=IDfamille, IDcompte_payeur=IDcompte_payeur))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def ConsommationsIncompletes(self):
        labelProbleme = u"Consommations tronquées"
        labelCorrection = u"Réparer la table des consommations"
        req = """SELECT IDconso, consommations.IDindividu, consommations.IDinscription, inscriptions.IDcompte_payeur
        FROM consommations 
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        WHERE consommations.IDinscription IS NOT NULL AND consommations.IDcompte_payeur IS NULL;"""
        self.DB.ExecuterReq(req)
        listeInscriptions = self.DB.ResultatReq()
        listeTemp = []
        for IDconso, IDinscription, IDindividu, IDcompte_payeur in listeInscriptions :
            label = u"Conso ID%d (IDinscription ID%d Individu ID%d)" % (IDconso, IDinscription, IDindividu)
            listeTemp.append(ConsommationsIncompletes(label=label, IDconso=IDconso, IDcompte_payeur=IDcompte_payeur))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def FacturesErronees(self):
        labelProbleme = u"Factures erronées"
        labelCorrection = u"Recalculer le montant des factures"
        # Recherche des factures
        req = """SELECT factures.IDfacture, factures.numero, factures.IDcompte_payeur, comptes_payeurs.IDfamille,
        factures.total, factures.regle, factures.solde
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille
        ORDER BY factures.date_edition;"""
        self.DB.ExecuterReq(req)
        listeFactures = self.DB.ResultatReq()
        # Recherche des prestations
        req = """SELECT IDprestation, montant, IDfacture
        FROM prestations;"""
        self.DB.ExecuterReq(req)
        listePrestations = self.DB.ResultatReq()
        dictPrestationsFacture = {}
        for IDprestation, montant, IDfacture in listePrestations :
            if dictPrestationsFacture.has_key(IDfacture) == False :
                dictPrestationsFacture[IDfacture] = []
            dictPrestationsFacture[IDfacture].append({"IDprestation":IDprestation, "montant" : FloatToDecimal(montant)})
        # Analyse
        listeTemp = []
        for IDfacture, numeroFacture, IDcompte_payeur, IDfamille, totalFacture, regleFacture, soldeFacture in listeFactures :
            totalFacture = FloatToDecimal(totalFacture)
            regleFacture = FloatToDecimal(regleFacture)
            soldeFacture = FloatToDecimal(soldeFacture)
            if dictPrestationsFacture.has_key(IDfacture) :
                listePrestationsFacture = dictPrestationsFacture[IDfacture]
            else :
                listePrestationsFacture = []
            montantTotalPrestations = FloatToDecimal(0.0)
            for dictTemp in listePrestationsFacture :
                montantTotalPrestations += dictTemp["montant"]
            if montantTotalPrestations != FloatToDecimal(totalFacture) :
                # Si la facture n'a pas de famille rattachée
                if IDfamille == None : 
                    label = u"Facture ID%d : Famille inconnue" % IDfacture
                    listeTemp.append(FacturesAsupprimer(label=label, IDfacture=IDfacture))
                elif len(listePrestationsFacture) == 0 :
                    label = u"Facture ID%d : Aucune prestation correspondante" % IDfacture
                    listeTemp.append(FacturesAsupprimer(label=label, IDfacture=IDfacture))
                elif montantTotalPrestations == FloatToDecimal(0.0) :
                    label = u"Facture ID%d : Montant de la facture égal à 0" % IDfacture
                    listeTemp.append(FacturesAsupprimer(label=label, IDfacture=IDfacture))
                else :
                    label = u"Facture ID%d : Total à recalculer" % IDfacture
                    listeTemp.append(FacturesRecalcul(label=label, IDfacture=IDfacture, totalFacture=totalFacture, regleFacture=regleFacture, soldeFacture=soldeFacture, montantTotalPrestations=montantTotalPrestations))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def ConsommationsErronees(self):
        labelProbleme = u"Consommations erronées"
        labelCorrection = u"Réparer la table des consommations"
        req = """SELECT IDconso, date, heure_debut, heure_fin, individus.nom, individus.prenom
        FROM consommations
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        ;"""
        self.DB.ExecuterReq(req)
        listeConso = self.DB.ResultatReq()
        listeTemp = []
        def ValidationHeure(heure):
            if len(heure) < 5 : return False
            if heure[0] not in ("0", "1", "2") : return False
            if heure[1] not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9") : return False
            if heure[2] != ":" : return False
            if heure[3] not in ("0", "1", "2", "3", "4", "5") : return False
            if heure[4] not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9") : return False
            if int(heure[:2]) > 24 : return False
            if int(heure[-2:]) > 59 : return False
            return True
        for IDconso, date, heure_debut, heure_fin, nomIndividu, prenomIndividu in listeConso :
            date = UTILS_Dates.DateEngEnDateDD(date)
            individu = ""
            if nomIndividu != None : individu += nomIndividu
            if prenomIndividu != None : individu += " " + prenomIndividu
            if heure_debut != None :
                if ValidationHeure(heure_debut) == False :
                    label = u"Conso ID%d de %s : Heure de début de consommation erronée ('%s')" % (IDconso, individu, heure_debut)
                    listeTemp.append(CorrigerHeuresConso(label=label, IDconso=IDconso, date=date, individu=individu, heure_debut=heure_debut, heure_fin=None))
            if heure_fin != None :
                if ValidationHeure(heure_fin) == False :
                    label = u"Conso ID%d de %s : Heure de fin de consommation erronée ('%s')" % (IDconso, individu, heure_fin)
                    listeTemp.append(CorrigerHeuresConso(label=label, IDconso=IDconso, date=date, individu=individu, heure_debut=None, heure_fin=heure_fin))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def LiensTronques(self):
        labelProbleme = u"Liens sans individus associés"
        labelCorrection = u"Supprimer le lien dans la base"

        req = """SELECT IDlien, IDindividu_sujet
        FROM liens 
        LEFT JOIN individus ON individus.IDindividu = liens.IDindividu_sujet
        WHERE individus.IDindividu IS NULL ;"""
        self.DB.ExecuterReq(req)
        listeSujets = self.DB.ResultatReq()
        
        req = """SELECT IDlien, IDindividu_objet
        FROM liens 
        LEFT JOIN individus ON individus.IDindividu = liens.IDindividu_objet
        WHERE individus.IDindividu IS NULL ;"""
        self.DB.ExecuterReq(req)
        listeObjets = self.DB.ResultatReq()

        listeTemp = []
        for liste in (listeSujets, listeObjets) :
            for IDlien, IDindividu in liste :
                label = u"Lien ID%d (Individu ID%d)" % (IDlien, IDindividu)
                listeTemp.append(LiensTronques(label=label, IDlien=IDlien, IDindividu=IDindividu))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def RattachementsTronques(self):
        labelProbleme = u"Rattachements sans individus associés"
        labelCorrection = u"Supprimer le rattachement dans la base"
        req = """SELECT IDrattachement, rattachements.IDindividu, IDfamille
        FROM rattachements 
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE individus.IDindividu IS NULL ;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDrattachement, IDindividu, IDfamille in listeDonnees :
            label = u"Rattachement ID%d (Famille ID%d - Individu ID%d)" % (IDrattachement, IDfamille, IDindividu)
            listeTemp.append(RattachementsTronques(label=label, IDrattachement=IDrattachement, IDfamille=IDfamille, IDindividu=IDindividu))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))
    
    def LiensErrones(self):
        labelProbleme = u"Liens de parenté erronés"
        labelCorrection = u"Supprimer les liens erronés"
        req = """SELECT IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, responsable, IDautorisation
        FROM liens
        ORDER BY IDlien;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        # Lecture des liens
        dictLiens = {}
        for IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, responsable, IDautorisation in listeDonnees :
            key = (IDindividu_sujet, IDindividu_objet)
            if dictLiens.has_key(IDfamille) == False :
                dictLiens[IDfamille] = {}
            if dictLiens[IDfamille].has_key(key) == False :
                dictLiens[IDfamille][key] = []
            dictLiens[IDfamille][key].append(IDlien)
            dictLiens[IDfamille][key].sort() 
        # Analyse
        dictLiensASupprimer = {}
        for IDfamille, dictKeys in dictLiens.iteritems() :
            for key, listeIDlien in dictKeys.iteritems() :
                if len(listeIDlien) > 1 :
                    if dictLiensASupprimer.has_key(IDfamille) == False :
                        dictLiensASupprimer[IDfamille] = []
                    # Suppression des liens obsolètes
                    for IDlien in listeIDlien[1:] :
                        dictLiensASupprimer[IDfamille].append(IDlien)
        # Mémorisation
        listeIDfamille = dictLiensASupprimer.keys() 
        listeIDfamille.sort() 
        listeTemp = []
        for IDfamille in listeIDfamille :
            listeIDlien = dictLiensASupprimer[IDfamille]
            label = u"Famille ID%d : %d liens erronés" % (IDfamille, len(listeIDlien))
            listeTemp.append(LiensErrones(label=label, IDfamille=IDfamille, listeIDlien=listeIDlien))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))
        
    def VentilationExcessive(self):
        labelProbleme = u"Ventilations excessives"
        labelCorrection = u"Supprimer la ventilation excessive"
        req = """SELECT IDventilation, ventilation.IDcompte_payeur, IDreglement, IDprestation, comptes_payeurs.IDfamille
        FROM ventilation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = ventilation.IDcompte_payeur;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        dictTemp = {}
        for IDventilation, IDcompte_payeur, IDreglement, IDprestation, IDfamille in listeDonnees :
            key = (IDcompte_payeur, IDreglement, IDprestation)
            if dictTemp.has_key(key) :
                label = u"Ventilation ID%d pour la prestation ID%d et le règlement ID%d pour la famille ID%d" % (IDventilation, IDprestation, IDreglement, IDfamille)
                listeTemp.append(VentilationsExcessives(label=label, IDventilation=IDventilation, IDprestation=IDprestation, IDreglement=IDreglement, IDfamille=IDfamille))
            else :
                dictTemp[key] = IDventilation
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))




if __name__ == "__main__":
    d = Depannage()
    print (d.GetTexte(),)
    
    
    pass
    
