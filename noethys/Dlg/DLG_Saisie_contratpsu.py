#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import GestionDB
from Ctrl import CTRL_Bandeau
from dateutil import rrule
import datetime
import calendar
from Utils import UTILS_Dates
from Utils import UTILS_Texte
from Utils import UTILS_Identification
from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal

import DLG_Contratpsu_generalites
import DLG_Contratpsu_calendrier
import DLG_Contratpsu_tarification
import DLG_Contratpsu_mensualisation
import DLG_Contratpsu_recapitulatif

from Ol.OL_Contratspsu_previsions import Track as Track_conso
from Ol.OL_Contratspsu_tarifs import Track as Track_tarif
from Ol.OL_Contratspsu_mensualites import Track as Track_mensualite



TEXTE_INTRO = _(u"Vous pouvez saisir ici les paramètres d'un contrat P.S.U.")

class Base(object) :
    """ Classe commune à l'assistant et au notebook """
    def __init__(self, IDcontrat=None, IDinscription=None, DB=None):
        self.IDcontrat = IDcontrat
        self.IDinscription = IDinscription

        # Stockage des données du contrat
        self.dictContrat = {}

        # Importation des données
        self.Importation(DB)


    def InitPages(self, parent=None):
        """ Initialisation des pages """
        self.listePages = [
            {"code" : "generalites", "label" : _(u"Généralités"), "ctrl" : DLG_Contratpsu_generalites.Panel(parent, clsbase=self), "image" : "Maison.png"},
            {"code" : "previsions", "label" : _(u"Prévisions"), "ctrl" : DLG_Contratpsu_calendrier.Panel(parent, clsbase=self), "image" : "Calendrier.png"},
            {"code" : "tarification", "label" : _(u"Tarification"), "ctrl" : DLG_Contratpsu_tarification.Panel(parent, clsbase=self), "image" : "Calculatrice.png"},
            {"code" : "mensualisation", "label" : _(u"Mensualisation"), "ctrl" : DLG_Contratpsu_mensualisation.Panel(parent, clsbase=self), "image" : "Euro.png"},
            {"code" : "recapitulatif", "label" : _(u"Récapitulatif"), "ctrl" : DLG_Contratpsu_recapitulatif.Panel(parent, clsbase=self), "image" : "Information.png"},
            ]
        return self.listePages

    def GetPage(self, code=""):
        for dictPage in self.listePages :
            if dictPage["code"] == code :
                return dictPage["ctrl"]
        return None

    def SetValeur(self, key=None, valeur=None):
        self.dictContrat[key] = valeur

    def SetValeurs(self, dictValeurs={}):
        for key, valeur in dictValeurs.iteritems() :
            self.dictContrat[key] = valeur

    def GetValeur(self, key=None, defaut=None):
        if self.dictContrat.has_key(key) :
            return self.dictContrat[key]
        else :
            return defaut

    def Calculer(self, mode_test=False, dict_valeurs={}):
        """ Calcul des totaux et des mensualités """
        """ dict_valeurs : pour saisir des valeurs tests """
        # Récupération des données
        date_debut = self.GetValeur("date_debut")
        if dict_valeurs.has_key("date_debut") :
            date_debut = dict_valeurs["date_debut"]
        date_fin = self.GetValeur("date_fin")
        if dict_valeurs.has_key("date_fin") :
            date_fin = dict_valeurs["date_fin"]
        tracks_previsions = self.GetValeur("tracks_previsions", [])
        tracks_tarifs = self.GetValeur("tracks_tarifs", [])
        duree_heures_regularisation = self.GetValeur("duree_heures_regularisation", datetime.timedelta(0))
        arrondi_type = self.GetValeur("arrondi_type", "duree")
        arrondi_delta = self.GetValeur("arrondi_delta", 30)

        # Absences
        duree_absences_prevues = self.GetValeur("duree_absences_prevues", datetime.timedelta(0))
        duree_absences_prises = self.GetValeur("duree_absences_prises", datetime.timedelta(0))
        duree_absences_solde = duree_absences_prevues - duree_absences_prises
        self.SetValeur("duree_absences_solde", duree_absences_solde)

        # Vérifie si dates du contrat valides avant les calculs
        if date_debut != None and date_fin != None and date_fin > date_debut :
            dates_valides = True
        else :
            dates_valides = False

        # Calcul du nbre de semaines et de mois
        if dates_valides :
            nbre_semaines = rrule.rrule(rrule.WEEKLY, dtstart=date_debut, until=date_fin).count()
            nbre_mois = rrule.rrule(rrule.MONTHLY, dtstart=date_debut, until=date_fin).count()
        else :
            nbre_semaines = 0
            nbre_mois = 0

        # Analyse des heures prévues
        duree_heures_brut = datetime.timedelta(0)
        listeDatesUniques = []
        for track in tracks_previsions :
            duree_heures_brut += track.duree_arrondie
            if track.date not in listeDatesUniques :
                listeDatesUniques.append(track.date)

        # Calcul du nbre de dates uniques
        nbre_dates = len(listeDatesUniques)

        # Calcul des moyennes
        if nbre_dates == 0 :
            moy_heures_jour = datetime.timedelta(0)
            moy_heures_semaine = datetime.timedelta(0)
            moy_heures_mois = datetime.timedelta(0)
        else :
            moy_heures_jour = duree_heures_brut / nbre_dates
            moy_heures_semaine = duree_heures_brut / nbre_semaines
            moy_heures_mois = duree_heures_brut / nbre_mois

        # Calcul du nbre d'heures du contrat
        duree_heures_contrat = duree_heures_brut - duree_absences_prevues + duree_heures_regularisation

        # Génération des dates de facturation
        if dates_valides :
            liste_mois = list(rrule.rrule(rrule.MONTHLY, bymonthday=1, dtstart=date_debut, until=date_fin))
        else :
            liste_mois = []
        nbre_mois_factures = len(liste_mois)

        # Ajout de la date de début du contrat
        if dates_valides and date_debut.day > 1 :
            liste_mois.insert(0, date_debut)

        # Recherche s'il y a des mensualités déjà facturées
        # listePrestationsFacturees = []
        # heuresFacturees = datetime.timedelta(seconds=0)
        # for dictPrestation in self.GetValeur("liste_prestations", []) :
        #     if dictPrestation["IDfacture"] != None :
        #         listePrestationsFacturees.append(dictPrestation)
        #         heuresFacturees += dictPrestation["temps_facture"]
        # nbrePrestations = len(listePrestationsFacturees)

        # Conversion du nbre d'heures déjà facturées en entier
        # heuresFacturees = (nbre_heures_contrat.days*24) + (nbre_heures_contrat.seconds/3600)

        # Calcul du forfait mensuel
        # heures_restantes = nbre_heures_contrat - heuresFacturees
        # nbre_mois_restant = nbre_mois - nbrePrestations

        if nbre_mois_factures == 0 :
            forfait_horaire_mensuel, reste_division = 0, 0
        else :
            nbre_heures_contrat_float = UTILS_Dates.DeltaEnHeures(duree_heures_contrat)
            forfait_horaire_mensuel, reste_division = divmod(nbre_heures_contrat_float, nbre_mois_factures)
        forfait_horaire_dernier_mois = forfait_horaire_mensuel + reste_division

        forfait_horaire_mensuel = UTILS_Dates.FloatEnDelta(forfait_horaire_mensuel)
        forfait_horaire_dernier_mois = UTILS_Dates.FloatEnDelta(forfait_horaire_dernier_mois)

        # Calcul du forfait horaire mensuel
        # if nbre_mois == 0 :
        #     forfait_horaire_mensuel, reste_division = 0, 0
        # else :
        #     forfait_horaire_mensuel, reste_division = divmod(nbre_heures_contrat, nbre_mois)
        # forfait_horaire_dernier_mois = forfait_horaire_mensuel + reste_division

        # Génération des mensualités
        tracks_mensualites = []
        total_mensualites = FloatToDecimal(0.0)
        index = 0
        for date in liste_mois :
            date_facturation = datetime.date(date.year, date.month, date.day)

            # Calcul des dates du forfait
            forfait_date_debut = date_facturation
            if index == len(liste_mois) - 1 :
                dernierJour = date.day
            else :
                dernierJour = calendar.monthrange(date.year, date.month)[1]
            forfait_date_fin = datetime.date(date.year, date.month, dernierJour)

            # Calcul du forfait horaire mensuel
            if index == len(liste_mois) - 1 :
                heures_prevues = forfait_horaire_dernier_mois
            else :
                heures_prevues = forfait_horaire_mensuel

            # Recherche du tarif du mois
            listeTarifs = []
            for track in tracks_tarifs :
                listeTarifs.append((track.date_debut, track))
            listeTarifs.sort()

            track_tarif = None
            for date_debut_tarif, track in listeTarifs :
                if track_tarif == None or date_facturation >= date_debut_tarif :
                    track_tarif = track

            # Calcul du montant mensuel à facturer
            if track_tarif != None :
                tarif_base = track_tarif.tarif_base
                tarif_depassement = track_tarif.tarif_depassement
                taux = track_tarif.taux
            else :
                tarif_base = 0.0
                tarif_depassement = 0.0
                taux = 0.0

            montant_prevu = FloatToDecimal(tarif_base * UTILS_Dates.DeltaEnFloat(heures_prevues))
            total_mensualites += montant_prevu

            # Recherche d'une prestation existante
            IDprestation = None
            IDfacture = None
            num_facture = None
            heures_facturees = datetime.timedelta(seconds=0)
            montant_facture = FloatToDecimal(0.0)
            for dictPrestation in self.GetValeur("liste_prestations", []) :
                if dictPrestation["date_facturation"] == date_facturation :
                    IDprestation = dictPrestation["IDprestation"]
                    IDfacture = dictPrestation["IDfacture"]
                    num_facture = dictPrestation["num_facture"]
                    montant_facture = dictPrestation["montant"]
                    heures_facturees = dictPrestation["temps_facture"]

            # Mémorisation de la mensualité
            dictMensualite = {
                "IDprestation" : IDprestation,
                "date_facturation" : date_facturation,
                "taux" : taux,
                "track_tarif" : track_tarif,
                "tarif_base" : tarif_base,
                "tarif_depassement" : tarif_depassement,
                "heures_prevues" : heures_prevues,
                "montant_prevu" : montant_prevu,
                "heures_facturees" : heures_facturees,
                "montant_facture" : montant_facture,
                "IDfacture" : IDfacture,
                "forfait_date_debut" : forfait_date_debut,
                "forfait_date_fin" : forfait_date_fin,
                "num_facture" : num_facture,
            }
            tracks_mensualites.append(Track_mensualite(dictMensualite))
            index += 1

        # Vérifie si anomalies
        listeAnomalies = []

        # Vérifie que les prestations facturées sont toujours là
        # for dictPrestation in listePrestationsFacturees :
        #     present = False
        #     for track in tracks_mensualites :
        #         if track.IDprestation == dictPrestation["IDprestation"] :
        #             present = True
        #     if present == False :
        #         listeAnomalies.append(_(u"La prestation du %s ne peut pas être supprimée car elle apparaît déjà sur la facture n°%s." % (UTILS_Dates.DateDDEnFr(dictPrestation["date_facturation"]), dictPrestation["num_facture"])))

        # Vérifie si les consommations sont bien sur la période du contrat
        nbreConsoHorsPeriode = 0
        for track in tracks_previsions :
            if track.date < date_debut or track.date > date_fin :
                nbreConsoHorsPeriode += 1
        if nbreConsoHorsPeriode > 0 :
            listeAnomalies.append(_(u"%d consommations prévues sont en dehors de la période du contrat." % nbreConsoHorsPeriode))

        # Si mode test, renvoie la liste des anomalies
        if mode_test == True :
            if len(listeAnomalies) > 0 :
                import DLG_Messagebox
                introduction =_(u"Votre saisie ne peut pas être validée en raison des erreurs suivantes :")
                detail = "\n".join(listeAnomalies)
                conclusion =_(u"Veuillez modifier les données saisies.")
                dlg = DLG_Messagebox.Dialog(None, titre=_(u"Erreur"), introduction=introduction, detail=detail, conclusion=conclusion, icone=wx.ICON_INFORMATION, boutons=[_(u"Ok"),])
                dlg.ShowModal()
                dlg.Destroy()
                return False
            else :
                return True

        # Envoi des données à clsbase
        dictValeurs = {
            "nbre_semaines" : nbre_semaines,
            "nbre_mois" : nbre_mois,
            "duree_heures_brut" : duree_heures_brut,
            "nbre_dates" : nbre_dates,
            "moy_heures_jour" : moy_heures_jour,
            "moy_heures_semaine" : moy_heures_semaine,
            "moy_heures_mois" : moy_heures_mois,
            "duree_heures_contrat" : duree_heures_contrat,
            "forfait_horaire_mensuel" : forfait_horaire_mensuel,
            "forfait_horaire_dernier_mois" : forfait_horaire_dernier_mois,
            "tracks_mensualites" : tracks_mensualites,
            "nbre_mensualites" : len(tracks_mensualites),
            "total_mensualites" : total_mensualites,
        }
        self.SetValeurs(dictValeurs)

        return dictValeurs

    def Validation(self):
        return True

    def Sauvegarde(self):
        """ Sauvegarde dans la base """
        DB = GestionDB.DB()

        # Enregistrement des informations générales sur le contrat
        listeDonnees = (
            ("IDindividu", self.GetValeur("IDindividu", None)),
            ("IDinscription", self.GetValeur("IDinscription", None)),
            ("IDactivite", self.GetValeur("IDactivite", None)),
            ("date_debut", self.GetValeur("date_debut", None)),
            ("date_fin", self.GetValeur("date_fin", None)),
            ("observations", self.GetValeur("observations", None)),
            ("type", "psu"),
            ("duree_absences_prevues", UTILS_Dates.DeltaEnStr(self.GetValeur("duree_absences_prevues", datetime.timedelta(0)), separateur=":")),
            ("duree_heures_regularisation", UTILS_Dates.DeltaEnStr(self.GetValeur("duree_heures_regularisation", datetime.timedelta(0)), separateur=":")),
            ("arrondi_type", self.GetValeur("arrondi_type", None)),
            ("arrondi_delta", self.GetValeur("arrondi_delta", 30)),
            ("planning", self.GetValeur("planning", None)),
        )
        if self.IDcontrat == None :
            self.IDcontrat = DB.ReqInsert("contrats", listeDonnees)
        else :
            DB.ReqMAJ("contrats", listeDonnees, "IDcontrat", self.IDcontrat)

        # Enregistrement des consommations
        # liste_IDconso = []
        # for track in self.GetValeur("tracks_previsions", []):
        #     listeDonnees = (
        #         ("IDindividu", self.GetValeur("IDindividu", None)),
        #         ("IDinscription", self.GetValeur("IDinscription", None)),
        #         ("IDactivite", self.GetValeur("IDactivite", None)),
        #         ("date", track.date),
        #         ("IDunite", track.IDunite),
        #         ("IDgroupe", self.GetValeur("IDgroupe", None)),
        #         ("heure_debut", track.heure_debut),
        #         ("heure_fin", track.heure_fin),
        #         ("etat", track.etat),
        #         #("date_saisie", track.date_saisie),
        #         ("IDutilisateur", UTILS_Identification.GetIDutilisateur()),
        #         ("IDcategorie_tarif", self.GetValeur("IDcategorie_tarif", None)),
        #         ("IDcompte_payeur", self.GetValeur("IDcompte_payeur", None)),
        #         #("IDprestation", track.IDprestation),#TODO
        #         #("forfait", track.forfait),#TODO
        #         ("quantite", track.quantite),
        #         #("etiquettes", track.etiquettes),#TODO
        #     )
        #     if track.IDconso == None :
        #         IDconso = DB.ReqInsert("consommations", listeDonnees)
        #     else :
        #         IDconso = track.IDconso
        #         DB.ReqMAJ("consommations", listeDonnees, "IDconso", IDconso)
        #     liste_IDconso.append(IDconso)

        # Version optimisée
        listeChamps = [
            "IDindividu", "IDinscription", "IDactivite", "date", "IDunite", "IDgroupe", "heure_debut", "heure_fin",
            "etat", "IDutilisateur", "IDcategorie_tarif", "IDcompte_payeur", "quantite",
        ]
        liste_IDconso = []
        listeAjouts = []
        listeModifications = []
        for track in self.GetValeur("tracks_previsions", []):
            listeDonnees = [
                self.GetValeur("IDindividu", None),
                self.GetValeur("IDinscription", None),
                self.GetValeur("IDactivite", None),
                track.date,
                track.IDunite,
                self.GetValeur("IDgroupe", None),
                track.heure_debut,
                track.heure_fin,
                track.etat,
                UTILS_Identification.GetIDutilisateur(),
                self.GetValeur("IDcategorie_tarif", None),
                self.GetValeur("IDcompte_payeur", None),
                track.quantite,
                ]
            if track.IDconso == None :
                listeAjouts.append(listeDonnees)
            else :
                IDconso = track.IDconso
                listeDonnees.append(IDconso)
                listeModifications.append(listeDonnees)
                liste_IDconso.append(IDconso)

        # Ajout optimisé des conso
        if len(listeAjouts) > 0 :
            texteChampsTemp = ", ".join(listeChamps)
            listeInterrogations = []
            for champ in listeChamps :
                listeInterrogations.append("?")
            texteInterrogations = ", ".join(listeInterrogations)
            DB.Executermany("INSERT INTO consommations (%s) VALUES (%s)" % (texteChampsTemp, texteInterrogations), listeAjouts, commit=True)

        # Modification optimisée des conso
        if len(listeModifications) > 0 :
            listeChampsTemp = []
            for champ in listeChamps :
                listeChampsTemp.append(("%s=?" % champ))
            DB.Executermany("UPDATE consommations SET %s WHERE IDconso=?" % ", ".join(listeChampsTemp), listeModifications, commit=True)

        # Suppression des consommations supprimées
        listeSuppressions = []
        for IDconso in self.GetValeur("liste_IDconso", []):
            if IDconso not in liste_IDconso :
                listeSuppressions.append(IDconso)

        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 :
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else :
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM consommations WHERE IDconso IN %s" % conditionSuppression)

        # Enregistrement des tarifs
        liste_IDtarif = []
        for track in self.GetValeur("tracks_tarifs", []):
            listeDonnees = (
                ("IDcontrat", self.IDcontrat),
                ("date_debut", track.date_debut),
                ("revenu", track.revenu),
                ("quotient", track.quotient),
                ("taux", track.taux),
                ("tarif_base", track.tarif_base),
                ("tarif_depassement", track.tarif_depassement),
            )
            if track.IDcontrat_tarif == None :
                IDcontrat_tarif = DB.ReqInsert("contrats_tarifs", listeDonnees)
            else :
                IDcontrat_tarif = track.IDcontrat_tarif
                DB.ReqMAJ("contrats_tarifs", listeDonnees, "IDcontrat_tarif", IDcontrat_tarif)
            liste_IDtarif.append(IDcontrat_tarif)

        # Suppression des tarifs supprimés
        listeSuppressions = []
        for IDcontrat_tarif in self.GetValeur("liste_IDtarif", []):
            if IDcontrat_tarif not in liste_IDtarif :
                listeSuppressions.append(IDcontrat_tarif)

        if len(listeSuppressions) > 0 :
            if len(listeSuppressions) == 1 :
                conditionSuppression = "(%d)" % listeSuppressions[0]
            else :
                conditionSuppression = str(tuple(listeSuppressions))
            DB.ExecuterReq("DELETE FROM contrats_tarifs WHERE IDcontrat_tarif IN %s" % conditionSuppression)

        # Enregistrement des mensualités
        # liste_IDprestation = []
        # for track in self.GetValeur("tracks_mensualites", []):
        #     listeDonnees = (
        #         ("IDcompte_payeur", self.GetValeur("IDcompte_payeur", None)),
        #         ("date", track.date_facturation),
        #         ("categorie", "consommation"),
        #         ("label", track.label_prestation),
        #         ("montant_initial", track.montant_mois),
        #         ("montant", track.montant_mois),
        #         ("IDactivite", self.GetValeur("IDactivite", None)),
        #         ("IDtarif", self.GetValeur("IDtarif", None)),
        #         ("IDfacture", track.IDfacture),
        #         ("IDfamille", self.GetValeur("IDfamille", None)),
        #         ("IDindividu", self.GetValeur("IDindividu", None)),
        #         ("forfait", None),
        #         ("temps_facture", UTILS_Dates.DeltaEnStr(track.heures_facturees, ":")),
        #         ("IDcategorie_tarif", self.GetValeur("IDcategorie_tarif", None)),
        #         ("forfait_date_debut", track.forfait_date_debut),
        #         ("forfait_date_fin", track.forfait_date_fin),
        #         ("IDcontrat", self.IDcontrat),
        #     )
        #     if track.IDprestation == None :
        #         IDprestation = DB.ReqInsert("prestations", listeDonnees)
        #     else :
        #         IDprestation = track.IDprestation
        #         DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestation)
        #     liste_IDprestation.append(IDprestation)
        #
        # # Suppression des prestations supprimées
        # listeSuppressions = []
        # for IDprestation in self.GetValeur("liste_IDprestation", []):
        #     if IDprestation not in liste_IDprestation :
        #         listeSuppressions.append(IDprestation)
        #
        # if len(listeSuppressions) > 0 :
        #     if len(listeSuppressions) == 1 :
        #         conditionSuppression = "(%d)" % listeSuppressions[0]
        #     else :
        #         conditionSuppression = str(tuple(listeSuppressions))
        #     DB.ExecuterReq("DELETE FROM prestations WHERE IDprestation IN %s" % conditionSuppression)
        #     DB.ExecuterReq("DELETE FROM ventilation WHERE IDprestation IN %s" % conditionSuppression)
        #     DB.ExecuterReq("DELETE FROM deductions WHERE IDprestation IN %s" % conditionSuppression)

        DB.Commit()
        DB.Close()


    def Importation(self, DBtemp=None):
        """ Importation depuis la base """
        dictValeurs = {}

        # Lecture de la base
        if DBtemp == None :
            DB = GestionDB.DB()
        else :
            DB = DBtemp

        # Informations générales sur le contrat
        if self.IDcontrat != None :

            req = """SELECT contrats.IDindividu, IDinscription, date_debut, date_fin, observations, IDactivite, type,
            duree_absences_prevues, duree_heures_regularisation, arrondi_type, arrondi_delta, duree_tolerance_depassement, planning,
            individus.nom, individus.prenom
            FROM contrats
            LEFT JOIN individus ON individus.IDindividu = contrats.IDindividu
            WHERE IDcontrat=%d
            ;""" % self.IDcontrat
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                IDindividu, IDinscription, date_debut, date_fin, observations, IDactivite, type_contrat, duree_absences_prevues, duree_heures_regularisation, arrondi_type, arrondi_delta, duree_tolerance_depassement, planning, individu_nom, individu_prenom = listeDonnees[0]

                self.IDinscription = IDinscription
                dictValeurs["IDinscription"] = self.IDinscription
                dictValeurs["date_debut"] = UTILS_Dates.DateEngEnDateDD(date_debut)
                dictValeurs["date_fin"] = UTILS_Dates.DateEngEnDateDD(date_fin)
                dictValeurs["observations"] = observations
                dictValeurs["IDactivite"] = IDactivite
                dictValeurs["type_contrat"] = type_contrat
                dictValeurs["duree_absences_prevues"] = UTILS_Dates.HeureStrEnDelta(duree_absences_prevues)
                dictValeurs["duree_heures_regularisation"] = UTILS_Dates.HeureStrEnDelta(duree_heures_regularisation)
                dictValeurs["duree_tolerance_depassement"] = UTILS_Dates.HeureStrEnDelta(duree_tolerance_depassement)
                dictValeurs["individu_nom"] = individu_nom
                dictValeurs["individu_prenom"] = individu_prenom
                dictValeurs["arrondi_type"] = arrondi_type
                dictValeurs["arrondi_delta"] = arrondi_delta
                dictValeurs["planning"] = planning

                if individu_prenom != None :
                    dictValeurs["individu_nom_complet"] = u"%s %s" %(individu_nom, individu_prenom)
                else :
                    dictValeurs["individu_nom_complet"] = individu_nom

        # Importation des données de l'inscription
        if self.IDinscription != None :

            req = """SELECT IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, IDcompte_payeur, date_inscription, parti
            FROM inscriptions
            WHERE IDinscription=%d
            ;""" % self.IDinscription
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            IDindividu, IDfamille, IDactivite, IDgroupe, IDcategorie_tarif, IDcompte_payeur, date_inscription, parti = listeDonnees[0]

            dictValeurs["IDinscription"] = self.IDinscription
            dictValeurs["IDindividu"] = IDindividu
            dictValeurs["IDfamille"] = IDfamille
            dictValeurs["IDactivite"] = IDactivite
            dictValeurs["IDgroupe"] = IDgroupe
            dictValeurs["IDcategorie_tarif"] = IDcategorie_tarif
            dictValeurs["IDcompte_payeur"] = IDcompte_payeur
            dictValeurs["date_inscription"] = date_inscription
            dictValeurs["parti"] = parti

            # Infos sur le dernier contrat saisi
            req = """SELECT arrondi_type, arrondi_delta, duree_tolerance_depassement
            FROM contrats
            WHERE type='psu' AND IDactivite=%d
            ORDER BY IDcontrat DESC LIMIT 1
            ;""" % IDactivite
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            if len(listeDonnees) > 0 :
                arrondi_type, arrondi_delta, duree_tolerance_depassement = listeDonnees[0]
                dictValeurs["arrondi_type"] = arrondi_type
                dictValeurs["arrondi_delta"] = arrondi_delta
                dictValeurs["duree_tolerance_depassement"] = UTILS_Dates.HeureStrEnDelta(duree_tolerance_depassement)

        # Informations sur l'activité
        req = """SELECT psu_unite_prevision, psu_unite_presence, psu_tarif_forfait, psu_etiquette_rtt
        FROM activites
        WHERE IDactivite=%d
        ;""" % dictValeurs["IDactivite"]
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        psu_unite_prevision, psu_unite_presence, psu_tarif_forfait, psu_etiquette_rtt = listeDonnees[0]

        dictValeurs["IDunite_prevision"] = psu_unite_prevision
        dictValeurs["IDunite_presence"] = psu_unite_presence
        dictValeurs["IDtarif"] = psu_tarif_forfait
        dictValeurs["psu_etiquette_rtt"] = psu_etiquette_rtt
        dictValeurs["duree_absences_prises"] = datetime.timedelta(0)

        # Mémorise les données déjà importées
        self.SetValeurs(dictValeurs)

        # Echap sur nouveau contrat
        if self.IDcontrat == None :
            DB.Close()
            return

        # Lecture des consommations
        req = """SELECT IDconso, date, IDunite, IDgroupe, heure_debut, heure_fin, consommations.etat, verrouillage, date_saisie, IDutilisateur,
        IDcategorie_tarif, IDprestation, forfait, quantite, etiquettes
        FROM consommations
        WHERE IDinscription=%d AND date>='%s' AND date<='%s'
        ;""" % (self.IDinscription, dictValeurs["date_debut"], dictValeurs["date_fin"])
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        tracks_previsions = []
        liste_IDconso = []
        liste_conso = []
        dict_conso = {}
        for IDconso, date, IDunite, IDgroupe, heure_debut, heure_fin, etat, verrouillage, date_saisie, IDutilisateur,IDcategorie_tarif, IDprestation, forfait, quantite, etiquettes in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            date_saisie = UTILS_Dates.DateEngEnDateDD(date_saisie)
            heure_debut_time = UTILS_Dates.HeureStrEnTime(heure_debut)
            heure_fin_time = UTILS_Dates.HeureStrEnTime(heure_fin)
            etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)

            dictConso = {
                "IDconso" : IDconso, "date" : date, "IDunite" : IDunite, "IDgroupe" : IDgroupe, "heure_debut" : heure_debut, "heure_fin" : heure_fin,
                "etat" : etat, "verrouillage" : verrouillage, "date_saisie" : date_saisie, "IDutilisateur" : IDutilisateur,
                "IDcategorie_tarif" : IDcategorie_tarif, "IDprestation" : IDprestation, "forfait" : forfait,
                "quantite" : quantite, "etiquettes" : etiquettes, "heure_debut_time" : heure_debut_time, "heure_fin_time" : heure_fin_time,
            }

            track = Track_conso(self, dictConso)

            liste_conso.append(track)
            if dict_conso.has_key(date) == False :
                dict_conso[date] = []
            dict_conso[date].append(track)

            if IDunite == self.GetValeur("IDunite_prevision", None) :
                tracks_previsions.append(track)
                liste_IDconso.append(IDconso)

            if dictValeurs["psu_etiquette_rtt"] in etiquettes :
                dictValeurs["duree_absences_prises"] += track.duree_arrondie

        dictValeurs["liste_conso"] = liste_conso
        dictValeurs["dict_conso"] = dict_conso
        dictValeurs["tracks_previsions"] = tracks_previsions
        dictValeurs["liste_IDconso"] = liste_IDconso

        # Lecture des tarifs du contrat
        req = """SELECT IDcontrat_tarif, date_debut, revenu, quotient, taux, tarif_base, tarif_depassement
        FROM contrats_tarifs
        WHERE IDcontrat=%d
        ;""" % self.IDcontrat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        tracks_tarifs = []
        liste_IDtarif = []
        for IDcontrat_tarif, date_debut, revenu, quotient, taux, tarif_base, tarif_depassement in listeDonnees :
            date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
            dictTarif = {
                "IDcontrat_tarif" : IDcontrat_tarif, "date_debut" : date_debut, "revenu" : revenu, "quotient" : quotient,
                "taux" : taux, "tarif_base" : tarif_base, "tarif_depassement" : tarif_depassement,
            }
            tracks_tarifs.append(Track_tarif(dictTarif))
            liste_IDtarif.append(IDcontrat_tarif)
        dictValeurs["tracks_tarifs"] = tracks_tarifs
        dictValeurs["liste_IDtarif"] = liste_IDtarif

        # Lecture des mensualités
        req = """SELECT IDprestation, date, label, montant_initial, prestations.montant, prestations.IDfacture, temps_facture,
        forfait_date_debut, forfait_date_fin, factures.numero
        FROM prestations
        LEFT JOIN factures ON factures.IDfacture = prestations.IDfacture
        WHERE IDcontrat=%d
        ;""" % self.IDcontrat
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        liste_prestations = []
        liste_IDprestation = []
        for IDprestation, date_facturation, label, montant_initial, montant, IDfacture, temps_facture, forfait_date_debut, forfait_date_fin, num_facture in listeDonnees :
            date_facturation = UTILS_Dates.DateEngEnDateDD(date_facturation)
            forfait_date_debut = UTILS_Dates.DateEngEnDateDD(forfait_date_debut)
            forfait_date_fin = UTILS_Dates.DateEngEnDateDD(forfait_date_fin)
            montant_initial = FloatToDecimal(montant_initial)
            montant = FloatToDecimal(montant)
            temps_facture = UTILS_Dates.HeureStrEnDelta(temps_facture)
            dictMensualite = {
                "IDprestation" : IDprestation, "date_facturation" : date_facturation, "label" : label, "montant_initial" : montant_initial, "montant" : montant,
                "IDfacture" : IDfacture, "temps_facture" : temps_facture,
                "forfait_date_debut" : forfait_date_debut, "forfait_date_fin" : forfait_date_fin, "num_facture" : num_facture,
            }
            liste_prestations.append(dictMensualite)
            liste_IDprestation.append(IDprestation)
        dictValeurs["liste_prestations"] = liste_prestations
        dictValeurs["liste_IDprestation"] = liste_IDprestation

        # Fermeture de la base
        if DBtemp == None :
            DB.Close()

        # Mémorisation des données
        self.SetValeurs(dictValeurs)



class Assistant(wx.Dialog, Base):
    def __init__(self, parent, IDcontrat=None, IDinscription=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_activite", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        Base.__init__(self, IDcontrat=IDcontrat, IDinscription=IDinscription)
        self.parent = parent

        titre = _(u"Création d'un contrat PSU")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=TEXTE_INTRO, hauteurHtml=30, nomImage="Images/32x32/Contrat.png")

        # Initialisation des pages
        self.InitPages(self)

        self.static_line = wx.StaticLine(self, -1)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_retour = CTRL_Bouton_image.CTRL(self, texte=_(u"Retour"), cheminImage="Images/32x32/Fleche_gauche.png")
        self.bouton_suite = CTRL_Bouton_image.CTRL(self, texte=_(u"Suite"), cheminImage="Images/32x32/Fleche_droite.png", margesImage=(0, 0, 4, 0), positionImage=wx.RIGHT)
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
                
        self.Bind(wx.EVT_BUTTON, self.Onbouton_aide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_retour, self.bouton_retour)
        self.Bind(wx.EVT_BUTTON, self.Onbouton_suite, self.bouton_suite)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.bouton_retour.Enable(False)
        self.nbrePages = len(self.listePages)    
        self.pageVisible = 0
                        
        # Création des pages
        self.Creation_Pages()
        self.GetPage("generalites").MAJ()

    def Creation_Pages(self):
        """ Creation des pages """
        self.dictPages = {}
        index = 0
        for dictPage in self.listePages :
            self.sizer_pages.Add(dictPage["ctrl"], 1, wx.EXPAND, 0)
            if index > 0 :
                dictPage["ctrl"].Show(False)
            index += 1
        self.sizer_pages.Layout()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_retour.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour revenir à la page précédente")))
        self.bouton_suite.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour passer à l'étape suivante")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez pour annuler")))
        self.SetMinSize((700, 640))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=0, hgap=0)
        # Bandeau
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        # Contenu
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_pages = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_base.Add(sizer_pages, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.static_line, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=6, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_retour, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_suite, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, wx.LEFT, 10)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
        
        self.sizer_pages = sizer_pages

    def Onbouton_aide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def AfficherPage(self, numPage=0):
        # rend invisible la page affichée
        page = self.listePages[self.pageVisible]["ctrl"]
        page.Sauvegarde()
        page.Show(False)
        # Fait apparaître nouvelle page
        self.pageVisible = numPage
        page = self.listePages[self.pageVisible]["ctrl"]
        page.MAJ()
        page.Show(True)
        self.sizer_pages.Layout()

    def Onbouton_retour(self, event):
        # Affiche nouvelle page
        self.AfficherPage(self.pageVisible - 1)
        # Si on quitte l'avant-dernière page, on active le bouton Suivant
        if self.pageVisible == self.nbrePages-1:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage(Chemins.GetStaticPath("Images/32x32/Valider.png"))
            self.bouton_suite.SetTexte(_(u"Valider"))
        else:
            self.bouton_suite.Enable(True)
            self.bouton_suite.SetImage(Chemins.GetStaticPath("Images/32x32/Fleche_droite.png"))
            self.bouton_suite.SetTexte(_(u"Suite"))
        # Si on revient à la première page, on désactive le bouton Retour
        if self.pageVisible == 0 :
            self.bouton_retour.Enable(False)

    def Onbouton_suite(self, event):
        # Vérifie que les données de la page en cours sont valides
        validation = self.ValidationPages()
        if validation == False : return
        # Si on est déjà sur la dernière page : on termine
        if self.pageVisible == self.nbrePages-1 :
            self.listePages[self.pageVisible]["ctrl"].Sauvegarde()
            self.Terminer()
            return
        # Affiche nouvelle page
        self.AfficherPage(self.pageVisible + 1)
        # Si on arrive à la dernière page, on désactive le bouton Suivant
        if self.pageVisible == self.nbrePages-1 :
            self.bouton_suite.SetImage(Chemins.GetStaticPath("Images/32x32/Valider.png"))
            self.bouton_suite.SetTexte(_(u"Valider"))
        # Si on quitte la première page, on active le bouton Retour
        if self.pageVisible > 0 :
            self.bouton_retour.Enable(True)

    def OnClose(self, event):
        self.OnBoutonAnnuler()

    def OnBoutonAnnuler(self, event=None):
        self.Annuler()

    def Annuler(self):
        """ Annulation des modifications """
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment abandonner la saisie de ce nouveau contrat ?\n\nLes éventuelles données saisies seront perdues."), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        self.EndModal(wx.ID_CANCEL)

    def ValidationPages(self) :
        """ Validation des données avant changement de pages """
        return self.listePages[self.pageVisible]["ctrl"].Validation()

    def Terminer(self):
        if self.Validation() == False :
            return False

        # Sauvegarde des données
        self.Sauvegarde()

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDcontrat(self):
        return self.IDcontrat

# ------------------------------------------------------------------------------------------------------------------------------------------



class Notebook(wx.Notebook, Base):
    def __init__(self, parent, IDcontrat=None):
        wx.Notebook.__init__(self, parent, id=10, style= wx.BK_DEFAULT)
        Base.__init__(self, IDcontrat=IDcontrat)

        # Initialisation des pages
        self.InitPages(self)

        # ImageList pour le NoteBook
        il = wx.ImageList(16, 16)
        index = 0
        self.dictImages = {}
        for dictPage in self.listePages :
            self.dictImages[dictPage["code"]] = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/%s' % dictPage["image"]), wx.BITMAP_TYPE_PNG))
            index += 1
        self.AssignImageList(il)

        # Création des pages
        index = 0
        self.dictPages = {}
        for dictPage in self.listePages :
            self.AddPage(dictPage["ctrl"], dictPage["label"])
            self.SetPageImage(index, self.dictImages[dictPage["code"]])
            self.dictPages[dictPage["code"]] = {'ctrl' : dictPage["ctrl"], 'index' : index}
            index += 1

        # Binds
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging)

        # Init
        self.GetPage(0).MAJ()

    def OnPageChanging(self, event):
        if event.GetId() == 10 :

            page = self.GetPage(event.GetOldSelection())

            # Validation de la page quittée
            if page.Validation() == False :
                event.Veto()
                return

            # Sauvegarde de la page quittée
            page.Sauvegarde()

        event.Skip()

    def OnPageChanged(self, event):
        if event.GetId() == 10 :

            # MAJ de la page affichée
            page = self.GetPage(event.GetSelection())
            page.MAJ()

        event.Skip()

    def GetPageActuelle(self):
        index = self.GetSelection()
        return self.listePages[index]["ctrl"]

    def GetPage(self, index=0):
        return self.listePages[index]["ctrl"]







class Dialog(wx.Dialog):
    def __init__(self, parent, IDcontrat=None, IDinscription=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDcontrat = IDcontrat

        titre = _(u"Modification d'un contrat PSU")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=TEXTE_INTRO, hauteurHtml=30, nomImage="Images/32x32/Contrat.png")
        
        self.ctrl_notebook = Notebook(self, IDcontrat=IDcontrat)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        
    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_base.Add(self.ctrl_notebook, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 10)
        
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.SetMinSize((700, 640))
        self.CenterOnScreen()

    def OnClose(self, event):
        self.OnBoutonAnnuler()

    def OnBoutonAnnuler(self, event=None):
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment annuler ?\n\nLes éventuelles modifications que vous avez effectué seront perdues."), _(u"Annulation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")
        
    def OnBoutonOk(self, event):
        if self.ctrl_notebook.GetPageActuelle().Validation() == False :
            return False

        # Sauvegarde des données
        self.ctrl_notebook.GetPageActuelle().Sauvegarde()
        self.ctrl_notebook.Sauvegarde()

        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetIDcontrat(self):
        return self.IDcontrat
        
        
        
        
        
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    #frame_1 = Assistant(None, IDinscription=1856)
    frame_1 = Dialog(None, IDcontrat=8)
    app.SetTopWindow(frame_1)
    frame_1.ShowModal()
    app.MainLoop()
