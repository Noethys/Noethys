#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Utils import UTILS_Dates
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal


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
        self.correction_manuelle = kwds.get("correction_manuelle", False)
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
            dlg = wx.TextEntryDialog(None, _(u"Corrigez l'heure de début de la consommation du %s de %s :\n\n(Obligatoirement au format HH:MM)") % (date.strftime("%d/%m/%Y"), individu), _(u"Correction d'une heure"), heure_debut)
            if dlg.ShowModal() == wx.ID_OK:
                DB.ReqMAJ("consommations", [("heure_debut", dlg.GetValue()),], "IDconso", IDconso)
                self.corrige = True
            else :
                self.corrige = False
            dlg.Destroy()
        
        if heure_fin != None : 
            dlg = wx.TextEntryDialog(None, _(u"Corrigez l'heure de fin de la consommation du %s de %s :\n\n(Obligatoirement au format HH:MM)") % (date.strftime("%d/%m/%Y"), individu), _(u"Correction d'une heure"), heure_fin)
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

class PrestationsFantomes(Anomalie):
    def Correction(self, DB=None):
        IDprestation = self.kwds["IDprestation"]
        DB.ReqDEL("prestations", "IDprestation", IDprestation)
        self.corrige = True

class MySQL8(Anomalie):
    correction_manuelle = True




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
                    texteCorrection = _(u"<A HREF='http://www.noethys.com'>Correction proposée : %s</A>") % labelCorrection
                    texte += u"&nbsp;&nbsp;&nbsp;<IMG SRC='Static/Images/16x16/Interdit2.png'>&nbsp;%s. %s<BR>" % (anomalie.label, texteCorrection)
            else :
                    texte += u"&nbsp;&nbsp;&nbsp;<IMG SRC='Static/Images/16x16/Ok4.png'>&nbsp;Aucune anomalie détectée...<BR>"
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
        EcritStatusbar(_(u"Recherche d'anomalies en cours...   Veuillez patienter..."))
        try :
            dlgAttente = wx.BusyInfo(_(u"Recherche d'anomalies en cours. Veuillez patienter..."), self.parent)
            if 'phoenix' not in wx.PlatformInfo:
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
        self.PrestationsFantomes()
        self.MySQL8()
                
        # Fermeture DB
        self.DB.Close()

        del dlgAttente
        EcritStatusbar("")
        
    def InscriptionsSansIndividus(self):
        labelProbleme = _(u"Inscriptions sans individus associés")
        labelCorrection = _(u"Supprimer l'inscription")
        req = """SELECT IDinscription, inscriptions.IDactivite, activites.nom, inscriptions.date_inscription, inscriptions.IDindividu 
        FROM inscriptions 
        LEFT JOIN individus ON individus.IDindividu = inscriptions.IDindividu 
        LEFT JOIN activites ON activites.IDactivite = inscriptions.IDactivite
        WHERE individus.IDindividu IS NULL;"""
        self.DB.ExecuterReq(req)
        listePrestations = self.DB.ResultatReq()
        listeTemp = []
        for IDinscription, IDactivite, nomActivite, dateInscription, IDindividu in listePrestations :
            label = _(u"Individu ID%d inscrit le %s à l'activité %s") % (IDindividu, UTILS_Dates.DateEngFr(dateInscription), nomActivite)
            listeTemp.append(InscriptionsSansIndividus(label=label, IDinscription=IDinscription, IDindividu=IDindividu))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def CotisationsSansIndividus(self):
        labelProbleme = _(u"Cotisations sans individus associés")
        labelCorrection = _(u"Supprimer la cotisation")
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
            label = _(u"Cotisation ID%d de type '%s - %s' saisie le %s pour l'individu ID%d") % (IDcotisation, nomType, nomUnite, UTILS_Dates.DateEngFr(dateSaisie), IDindividu)
            listeTemp.append(CotisationsSansIndividus(label=label, IDcotisation=IDcotisation, IDindividu=IDindividu, IDprestation=IDprestation))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def CotisationsSansFamilles(self):
        labelProbleme = _(u"Cotisations sans familles associées")
        labelCorrection = _(u"Supprimer la cotisation")
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
            label = _(u"Cotisation ID%d de type '%s - %s' saisie le %s pour la famille ID%d") % (IDcotisation, nomType, nomUnite, UTILS_Dates.DateEngFr(dateSaisie), IDfamille)
            listeTemp.append(CotisationsSansFamilles(label=label, IDcotisation=IDcotisation, IDfamille=IDfamille, IDprestation=IDprestation))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def PrestationsSansFamilles(self):
        labelProbleme = _(u"Prestations sans familles associées")
        labelCorrection = _(u"Supprimer la prestation")
        req = """SELECT IDprestation, date, label, prestations.IDfamille
        FROM prestations 
        LEFT JOIN familles ON familles.IDfamille = prestations.IDfamille
        WHERE familles.IDfamille IS NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDprestation, date, label, IDfamille in listeDonnees :
            label = _(u"Prestation ID%d '%s' saisie le %s pour la famille ID%d") % (IDprestation, label, UTILS_Dates.DateEngFr(date), IDfamille)
            listeTemp.append(PrestationsSansFamilles(label=label, IDprestation=IDprestation, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def VentilationsSansPrestations(self):
        labelProbleme = _(u"Ventilations sans prestations associées")
        labelCorrection = _(u"Supprimer la ventilation")
        req = """SELECT IDventilation, ventilation.IDprestation, IDreglement, comptes_payeurs.IDfamille
        FROM ventilation
        LEFT JOIN prestations ON prestations.IDprestation = ventilation.IDprestation 
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = ventilation.IDcompte_payeur
        WHERE prestations.IDprestation IS NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDventilation, IDprestation, IDreglement, IDfamille in listeDonnees :
            if IDventilation and IDprestation and IDreglement and IDfamille:
                label = _(u"Ventilation ID%d pour la prestation ID%d et le règlement ID%d pour la famille ID%d") % (IDventilation, IDprestation, IDreglement, IDfamille)
                listeTemp.append(VentilationsSansPrestations(label=label, IDventilation=IDventilation, IDprestation=IDprestation, IDreglement=IDreglement, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def VentilationsSansReglements(self):
        labelProbleme = _(u"Ventilations sans règlements associés")
        labelCorrection = _(u"Supprimer la ventilation")
        req = """SELECT IDventilation, IDprestation, ventilation.IDreglement, comptes_payeurs.IDfamille
        FROM ventilation
        LEFT JOIN reglements ON reglements.IDreglement = ventilation.IDreglement
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = ventilation.IDcompte_payeur
        WHERE reglements.IDreglement IS NULL;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDventilation, IDprestation, IDreglement, IDfamille in listeDonnees :
            label = _(u"Ventilation ID%d pour la prestation ID%d et le règlement ID%d pour la famille ID%d") % (IDventilation, IDprestation, IDreglement, IDfamille)
            listeTemp.append(VentilationsSansReglements(label=label, IDventilation=IDventilation, IDprestation=IDprestation, IDreglement=IDreglement, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def IndividusIncomplets(self):
        labelProbleme = _(u"Fiches individuelles tronquées")
        labelCorrection = _(u"Modifier la civilité et/ou le nom de famille")
        req = """SELECT IDindividu, IDcivilite, nom, prenom
        FROM individus 
        WHERE IDcivilite IS NULL OR nom IS NULL;"""
        self.DB.ExecuterReq(req)
        listeIndividus = self.DB.ResultatReq()
        listeTemp = []
        for IDindividu, IDcivilite, nom, prenom in listeIndividus :
            label = _(u"Individu ID%d (%s %s)") % (IDindividu, nom, prenom)
            listeTemp.append(IndividusIncomplets(label=label, IDindividu=IDindividu, IDcivilite=IDcivilite, nom=nom))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def FamillesIncompletes(self):
        labelProbleme = _(u"Fiches familles tronquées")
        labelCorrection = _(u"Réparer la fiche famille")
        req = """SELECT IDfamille, IDcompte_payeur
        FROM familles 
        WHERE IDcompte_payeur IS NULL;"""
        self.DB.ExecuterReq(req)
        listeFamilles = self.DB.ResultatReq()
        listeTemp = []
        for IDfamille, IDcompte_payeur in listeFamilles :
            label = _(u"Famille ID%d") % IDfamille
            listeTemp.append(FamillesIncompletes(label=label, IDfamille=IDfamille))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def InscriptionsIncompletes(self):
        labelProbleme = _(u"Inscriptions tronquées")
        labelCorrection = _(u"Réparer la table des inscriptions")
        req = """SELECT IDinscription, IDfamille, IDindividu, IDcompte_payeur
        FROM inscriptions 
        WHERE IDcompte_payeur IS NULL;"""
        self.DB.ExecuterReq(req)
        listeInscriptions = self.DB.ResultatReq()
        listeTemp = []
        for IDinscription, IDfamille, IDindividu, IDcompte_payeur in listeInscriptions :
            label = _(u"Inscription ID%d (Famille ID%d Individu ID%d)") % (IDinscription, IDfamille, IDindividu)
            listeTemp.append(InscriptionsIncompletes(label=label, IDinscription=IDinscription, IDfamille=IDfamille, IDcompte_payeur=IDcompte_payeur))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def ConsommationsIncompletes(self):
        labelProbleme = _(u"Consommations tronquées")
        labelCorrection = _(u"Réparer la table des consommations")
        req = """SELECT IDconso, consommations.IDindividu, consommations.IDinscription, inscriptions.IDcompte_payeur
        FROM consommations 
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        WHERE consommations.IDinscription IS NOT NULL AND consommations.IDcompte_payeur IS NULL;"""
        self.DB.ExecuterReq(req)
        listeInscriptions = self.DB.ResultatReq()
        listeTemp = []
        for IDconso, IDinscription, IDindividu, IDcompte_payeur in listeInscriptions :
            label = _(u"Conso ID%d (IDinscription ID%d Individu ID%d)") % (IDconso, IDinscription, IDindividu)
            listeTemp.append(ConsommationsIncompletes(label=label, IDconso=IDconso, IDcompte_payeur=IDcompte_payeur))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def FacturesErronees(self):
        labelProbleme = _(u"Factures erronées")
        labelCorrection = _(u"Recalculer le montant des factures")
        # Recherche des factures
        req = """SELECT factures.IDfacture, factures.numero, factures.IDcompte_payeur, comptes_payeurs.IDfamille,
        factures.total, factures.regle, factures.solde
        FROM factures
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = factures.IDcompte_payeur
        LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille
        WHERE factures.etat <> "annulation"
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
            if (IDfacture in dictPrestationsFacture) == False :
                dictPrestationsFacture[IDfacture] = []
            dictPrestationsFacture[IDfacture].append({"IDprestation":IDprestation, "montant" : FloatToDecimal(montant)})
        # Analyse
        listeTemp = []
        for IDfacture, numeroFacture, IDcompte_payeur, IDfamille, totalFacture, regleFacture, soldeFacture in listeFactures :
            totalFacture = FloatToDecimal(totalFacture)
            regleFacture = FloatToDecimal(regleFacture)
            soldeFacture = FloatToDecimal(soldeFacture)
            if IDfacture in dictPrestationsFacture :
                listePrestationsFacture = dictPrestationsFacture[IDfacture]
            else :
                listePrestationsFacture = []
            montantTotalPrestations = FloatToDecimal(0.0)
            for dictTemp in listePrestationsFacture :
                montantTotalPrestations += dictTemp["montant"]
            if montantTotalPrestations != FloatToDecimal(totalFacture) :
                # Si la facture n'a pas de famille rattachée
                if IDfamille == None : 
                    label = _(u"Facture ID%d : Famille inconnue") % IDfacture
                    listeTemp.append(FacturesAsupprimer(label=label, IDfacture=IDfacture))
                elif len(listePrestationsFacture) == 0 :
                    label = _(u"Facture ID%d : Aucune prestation correspondante") % IDfacture
                    listeTemp.append(FacturesAsupprimer(label=label, IDfacture=IDfacture))
                elif montantTotalPrestations == FloatToDecimal(0.0) :
                    label = _(u"Facture ID%d : Montant de la facture égal à 0") % IDfacture
                    listeTemp.append(FacturesAsupprimer(label=label, IDfacture=IDfacture))
                else :
                    label = _(u"Facture ID%d : Total à recalculer") % IDfacture
                    listeTemp.append(FacturesRecalcul(label=label, IDfacture=IDfacture, totalFacture=totalFacture, regleFacture=regleFacture, soldeFacture=soldeFacture, montantTotalPrestations=montantTotalPrestations))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def ConsommationsErronees(self):
        labelProbleme = _(u"Consommations erronées")
        labelCorrection = _(u"Réparer la table des consommations")
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
                    label = _(u"Conso ID%d de %s : Heure de début de consommation erronée ('%s')") % (IDconso, individu, heure_debut)
                    listeTemp.append(CorrigerHeuresConso(label=label, IDconso=IDconso, date=date, individu=individu, heure_debut=heure_debut, heure_fin=None))
            if heure_fin != None :
                if ValidationHeure(heure_fin) == False :
                    label = _(u"Conso ID%d de %s : Heure de fin de consommation erronée ('%s')") % (IDconso, individu, heure_fin)
                    listeTemp.append(CorrigerHeuresConso(label=label, IDconso=IDconso, date=date, individu=individu, heure_debut=None, heure_fin=heure_fin))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def LiensTronques(self):
        labelProbleme = _(u"Liens sans familles ou sans individus associés")
        labelCorrection = _(u"Supprimer le lien dans la base")

        req = """SELECT IDlien, IDindividu_sujet
        FROM liens 
        LEFT JOIN individus ON individus.IDindividu = liens.IDindividu_sujet
        WHERE individus.IDindividu IS NULL ;"""
        self.DB.ExecuterReq(req)
        listeSujets = self.DB.ResultatReq()
        
        req = """SELECT IDlien, IDindividu_objet
        FROM liens 
        LEFT JOIN individus ON individus.IDindividu = liens.IDindividu_objet
        LEFT JOIN familles ON familles.IDfamille = liens.IDfamille
        WHERE individus.IDindividu IS NULL OR familles.IDfamille IS NULL;"""
        self.DB.ExecuterReq(req)
        listeObjets = self.DB.ResultatReq()

        listeTemp = []
        for liste in (listeSujets, listeObjets) :
            for IDlien, IDindividu in liste :
                label = _(u"Lien ID%d (Individu ID%d)") % (IDlien, IDindividu)
                listeTemp.append(LiensTronques(label=label, IDlien=IDlien, IDindividu=IDindividu))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def RattachementsTronques(self):
        labelProbleme = _(u"Rattachements sans individus associés")
        labelCorrection = _(u"Supprimer le rattachement dans la base")
        req = """SELECT IDrattachement, rattachements.IDindividu, IDfamille
        FROM rattachements 
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE individus.IDindividu IS NULL ;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        for IDrattachement, IDindividu, IDfamille in listeDonnees :
            label = _(u"Rattachement ID%d (Famille ID%d - Individu ID%d)") % (IDrattachement, IDfamille, IDindividu)
            listeTemp.append(RattachementsTronques(label=label, IDrattachement=IDrattachement, IDfamille=IDfamille, IDindividu=IDindividu))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))
    
    def LiensErrones(self):
        labelProbleme = _(u"Liens de parenté erronés")
        labelCorrection = _(u"Supprimer les liens erronés")
        req = """SELECT IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, responsable, IDautorisation
        FROM liens
        ORDER BY IDlien;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        # Lecture des liens
        dictLiens = {}
        for IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, responsable, IDautorisation in listeDonnees :
            key = (IDindividu_sujet, IDindividu_objet)
            if (IDfamille in dictLiens) == False :
                dictLiens[IDfamille] = {}
            if (key in dictLiens[IDfamille]) == False :
                dictLiens[IDfamille][key] = []
            dictLiens[IDfamille][key].append(IDlien)
            dictLiens[IDfamille][key].sort() 
        # Analyse
        dictLiensASupprimer = {}
        for IDfamille, dictKeys in dictLiens.items() :
            for key, listeIDlien in dictKeys.items() :
                if len(listeIDlien) > 1 :
                    if (IDfamille in dictLiensASupprimer) == False :
                        dictLiensASupprimer[IDfamille] = []
                    # Suppression des liens obsolètes
                    for IDlien in listeIDlien[1:] :
                        dictLiensASupprimer[IDfamille].append(IDlien)
        # Mémorisation
        listeIDfamille = list(dictLiensASupprimer.keys()) 
        listeIDfamille.sort() 
        listeTemp = []
        for IDfamille in listeIDfamille :
            listeIDlien = dictLiensASupprimer[IDfamille]
            label = _(u"Famille ID%d : %d liens erronés") % (IDfamille, len(listeIDlien))
            listeTemp.append(LiensErrones(label=label, IDfamille=IDfamille, listeIDlien=listeIDlien))
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))
        
    def VentilationExcessive(self):
        labelProbleme = _(u"Ventilations excessives")
        labelCorrection = _(u"Supprimer la ventilation excessive")
        req = """SELECT IDventilation, ventilation.IDcompte_payeur, IDreglement, IDprestation, comptes_payeurs.IDfamille
        FROM ventilation
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = ventilation.IDcompte_payeur;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        listeTemp = []
        dictTemp = {}
        for IDventilation, IDcompte_payeur, IDreglement, IDprestation, IDfamille in listeDonnees :
            key = (IDcompte_payeur, IDreglement, IDprestation)
            if key in dictTemp :
                label = _(u"Ventilation ID%d pour la prestation ID%d et le règlement ID%d pour la famille ID%d") % (IDventilation, IDprestation, IDreglement, IDfamille)
                listeTemp.append(VentilationsExcessives(label=label, IDventilation=IDventilation, IDprestation=IDprestation, IDreglement=IDreglement, IDfamille=IDfamille))
            else :
                dictTemp[key] = IDventilation
        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def PrestationsFantomes(self):
        labelProbleme = _(u"Prestations fantômes")
        labelCorrection = _(u"Supprimer la prestation fantôme")

        # Récupération des prestations
        from dateutil import relativedelta
        date_limite = datetime.date.today() + relativedelta.relativedelta(months=-2)
        req = """SELECT IDprestation, label, date, IDfamille, prestations.IDindividu,
        individus.nom, individus.prenom
        FROM prestations
        LEFT JOIN individus ON individus.IDindividu = prestations.IDindividu
        WHERE categorie='consommation' AND forfait IS NULL AND IDfacture IS NULL AND date>='%s'
        ORDER BY date, prestations.IDfamille, prestations.IDindividu
        ;""" % date_limite
        self.DB.ExecuterReq(req)
        listePrestations = self.DB.ResultatReq()

        # Récupération des consommations
        req = """SELECT IDconso, IDprestation FROM consommations;"""
        self.DB.ExecuterReq(req)
        listeConsommations = self.DB.ResultatReq()

        # Analyse
        dictPrestations = {}
        for IDconso, IDprestation in listeConsommations:
            if (IDprestation in dictPrestations) == False:
                dictPrestations[IDprestation] = []
            dictPrestations[IDprestation].append(IDconso)

        listeTemp = []
        for IDprestation, label, date, IDfamille, IDindividu, nom, prenom in listePrestations:
            date = UTILS_Dates.DateEngEnDateDD(date)
            if (IDprestation in dictPrestations) == False:
                if nom != None and prenom != None:
                    nomIndividu = u"%s %s" % (nom, prenom)
                else:
                    nomIndividu = u""
                label = u"Prestation ID%d du %s pour %s : %s" % (IDprestation, UTILS_Dates.DateDDEnFr(date), nomIndividu, label)
                listeTemp.append(PrestationsFantomes(label=label, IDprestation=IDprestation))

        self.listeResultats.append((labelProbleme, labelCorrection, listeTemp))

    def MySQL8(self):
        labelProbleme = _(u"MySQL 8 Server détecté")
        labelCorrection = _(u"Correction manuelle requise : L'utilisation de la version 8 de MySQL est déconseillée. Faites une sauvegarde, désinstallez MySQL 8, installez MySQL 5.7 et restaurez la sauvegarde.")

        # Recherche si le serveur MySQL est une version 8
        nomFichier = self.DB.GetNomFichierDefaut()
        if "[RESEAU]" in nomFichier:
            req = """SHOW VARIABLES LIKE "version";"""
            self.DB.ExecuterReq(req)
            listeTemp = self.DB.ResultatReq()
            if len(listeTemp) > 0:
                num_serveur = listeTemp[0][1]
                if num_serveur.startswith("8"):
                    self.listeResultats.append((labelProbleme, labelCorrection, [MySQL8(label=labelCorrection),]))



if __name__ == "__main__":
    d = Depannage()
    print((d.GetTexte(),))
    
    
    pass
    
