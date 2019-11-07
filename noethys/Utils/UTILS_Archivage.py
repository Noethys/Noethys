#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
from Utils import UTILS_Titulaires
import GestionDB
import wx
import wx.lib.agw.hypertreelist as HTL
from Ctrl import CTRL_Bouton_image
from Dlg import DLG_Messagebox
import operator
import datetime


def GetNomCategorie(IDcategorie=1):
    if IDcategorie == 1: nom_categorie = _(u"représentant")
    elif IDcategorie == 2: nom_categorie = _(u"enfant")
    elif IDcategorie == 3: nom_categorie = _(u"contact")
    else: nom_categorie = ""
    return nom_categorie


class Archivage():
    def __init__(self):
        self.liste_familles = []
        self.liste_individus = []

        # Importation des titulaires
        self.dict_titulaires = UTILS_Titulaires.GetTitulaires()

    def Archiver(self, etat="archiver", liste_familles=[], liste_individus=[]):
        resultat = False
        self.DB = GestionDB.DB()
        if liste_familles != [] :
            self.liste_familles = liste_familles
            resultat = self.Archiver_familles(etat)
        if liste_individus != [] :
            self.liste_individus = liste_individus
            resultat = self.Archiver_individus(etat)
        self.DB.Close()
        return resultat

    def Archiver_familles(self, etat="archiver"):
        if etat == "archiver" :
            valeur = "archive"
            label = _(u"archiver")
        elif etat == "desarchiver" :
            valeur = None
            label = _(u"désarchiver")

        # Sélection des individus
        liste_individus = self.SelectionIndividus(intro=_(u"Cochez les individus à %s :") % label)
        if liste_individus == False :
            return False

        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment %s %d fiches familles et %d fiches individuelles ?") % (label, len(self.liste_familles), len(liste_individus)), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        listeModifications = []
        for IDfamille in self.liste_familles :
            listeModifications.append((valeur, IDfamille))
        self.DB.Executermany("UPDATE familles SET etat=? WHERE IDfamille=?", listeModifications, commit=False)

        listeModifications = []
        for IDindividu in liste_individus :
            listeModifications.append((valeur, IDindividu))
        self.DB.Executermany("UPDATE individus SET etat=? WHERE IDindividu=?", listeModifications, commit=False)

        self.DB.Commit()
        return True

    def Archiver_individus(self, etat="archiver"):
        """ Effacer les individus """
        if etat == "archiver" :
            valeur = "archive"
            label = _(u"archiver")
        elif etat == "desarchiver" :
            valeur = None
            label = _(u"désarchiver")

        # Sélection des individus
        liste_individus = self.SelectionIndividus(intro=_(u"Cochez les individus à %s :") % label)
        if liste_individus == False :
            return False

        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment %s %d fiches individuelles ?") % (label, len(liste_individus)), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        listeModifications = []
        for IDindividu in liste_individus :
            listeModifications.append((valeur, IDindividu))
        self.DB.Executermany("UPDATE individus SET etat=? WHERE IDindividu=?", listeModifications, commit=False)

        self.DB.Commit()
        return True


    def Effacer(self, liste_familles=[], liste_individus=[]):
        resultat = False
        self.DB = GestionDB.DB()
        if liste_familles != [] :
            self.liste_familles = liste_familles
            resultat = self.Effacer_familles()
        if liste_individus != [] :
            self.liste_individus = liste_individus
            resultat = self.Effacer_individus()
        self.DB.Close()
        return resultat

    def Modifier(self, listeID=[], nom_table="", champ_condition="", liste_valeurs=[]):
        """ Fonction pour modifier une table donnée """
        # Préparation des champs
        liste_champs = []
        for nom_champ, valeur in liste_valeurs:
            liste_champs.append("%s=?" % nom_champ)

        # Préparation des valeurs
        listeModifications = []
        for ID in listeID:
            listeTemp = []
            for nom_champ, valeur in liste_valeurs:
                listeTemp.append(valeur)
            listeTemp.append(ID)
            listeModifications.append(listeTemp)

        # Requête de modification
        self.DB.Executermany("UPDATE %s SET %s WHERE %s=?" % (nom_table, ", ".join(liste_champs), champ_condition), listeModifications, commit=False)
        self.DB.Commit()

    def Supprimer(self, listeID=[], nom_table="", champ_condition=""):
        self.DB.ExecuterReq("DELETE FROM %s WHERE %s IN %s" % (nom_table, champ_condition, GestionDB.ConvertConditionChaine(listeID)))
        self.DB.Commit()

    def SelectionIndividus(self, intro=""):
        # Récupère les individus
        req = """SELECT IDindividu, nom, prenom
        FROM individus;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        dict_individus = {}
        for IDindividu, nom, prenom in listeDonnees:
            if prenom == None :
                prenom = ""
            nom_complet = u"%s %s" % (nom, prenom)
            dict_individus[IDindividu] = {"nom_complet" : nom_complet, "nom" : nom, "prenom" : prenom}

        # Récupère les individus rattachés
        req = """SELECT IDrattachement, IDindividu, IDfamille, IDcategorie
        FROM rattachements;"""
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        dict_rattachements_familles = {}
        dict_rattachements_individus = {}

        liste_individus_concernes = []
        for IDrattachement, IDindividu, IDfamille, IDcategorie in listeDonnees :

            if (IDfamille in dict_rattachements_familles) == False :
                dict_rattachements_familles[IDfamille] = []
            dict_rattachements_familles[IDfamille].append((IDindividu, IDcategorie))

            if (IDindividu in dict_rattachements_individus) == False :
                dict_rattachements_individus[IDindividu] = []
            dict_rattachements_individus[IDindividu].append((IDfamille, IDcategorie))

            if (IDfamille in self.liste_familles or IDindividu in self.liste_individus) and IDindividu not in liste_individus_concernes:
                liste_individus_concernes.append(IDindividu)

        # Recherche les prestations futures
        req = """SELECT IDindividu, IDfamille, COUNT(IDprestation)
        FROM prestations
        WHERE date>='%s' AND IDindividu IN %s
        GROUP BY IDindividu, IDfamille;""" % (datetime.date.today(), GestionDB.ConvertConditionChaine(liste_individus_concernes))
        self.DB.ExecuterReq(req)
        listePrestations = self.DB.ResultatReq()
        dictPrestations = {}
        for IDindividu, IDfamille, nbrePrestations in listePrestations:
            if nbrePrestations > 0:
                dictPrestations[(IDindividu, IDfamille)] = nbrePrestations

        # Variables
        liste_familles_temp = []
        liste_individus_temp = []

        # Version FAMILLES
        if self.liste_familles != [] :

            # Sélection des individus
            for IDfamille in self.liste_familles:
                nomTitulaires = self.dict_titulaires[IDfamille]["titulairesSansCivilite"]
                liste_rattaches = []
                if IDfamille in dict_rattachements_familles:
                    for IDindividu, IDcategorie in dict_rattachements_familles[IDfamille]:
                        nom_complet = dict_individus[IDindividu]["nom_complet"]
                        nom_categorie = GetNomCategorie(IDcategorie).capitalize()
                        infos = []

                        # Recherche si l'individu est rattaché à d'autres familles non inclues
                        if IDindividu in dict_rattachements_individus:
                            for IDfamilleTemp, IDcategorieTemp in dict_rattachements_individus[IDindividu]:
                                if IDfamilleTemp not in self.liste_familles:
                                    infos.append(_(u"Rattaché également à la famille de %s en tant que %s") % (self.dict_titulaires[IDfamilleTemp]["titulairesSansCivilite"], GetNomCategorie(IDcategorieTemp)))

                        if (IDindividu, IDfamille) in dictPrestations:
                            infos.append(_(u"Des prestations futures sont déjà enregistrées"))

                        liste_rattaches.append({"IDcategorie" : IDcategorie, "nom_complet" : nom_complet, "IDindividu" : IDindividu, "nom_categorie" : nom_categorie, "infos" : infos})
                        liste_rattaches = sorted(liste_rattaches, key=operator.itemgetter("IDcategorie"))
                #liste_rattaches.sort()
                liste_familles_temp.append({"nomTitulaires" : nomTitulaires, "IDfamille" : IDfamille, "liste_rattaches" : liste_rattaches})
            liste_familles_temp = sorted(liste_familles_temp, key=operator.itemgetter("nomTitulaires"))
            #liste_familles_temp.sort()

        # Version INDIVIDUS
        if self.liste_individus != [] :

            # Sélection des individus
            for IDindividu in self.liste_individus :
                nom_complet = dict_individus[IDindividu]["nom_complet"]
                liste_rattaches = []

                if IDindividu in dict_rattachements_individus:
                    for IDfamille, IDcategorie in dict_rattachements_individus[IDindividu]:
                        nomTitulaires = self.dict_titulaires[IDfamille]["titulairesSansCivilite"]
                        nom_categorie = GetNomCategorie(IDcategorie).capitalize()
                        infos = []

                        if (IDindividu, IDfamille) in dictPrestations:
                            infos.append(_(u"Des prestations futures sont déjà enregistrées"))

                        liste_rattaches.append({"IDcategorie": IDcategorie, "nomTitulaires": nomTitulaires, "IDfamille": IDfamille, "nom_categorie": nom_categorie, "infos": infos})
                        liste_rattaches = sorted(liste_rattaches, key=operator.itemgetter("IDcategorie"))
                liste_rattaches.sort()
                liste_individus_temp.append({"nom_complet": nom_complet, "IDindividu": IDindividu, "liste_rattaches": liste_rattaches})
            liste_individus_temp = sorted(liste_individus_temp, key=operator.itemgetter("nom_complet"))
            #liste_individus_temp.sort()

        # Affiche dlg de sélection
        dlg = DLG_Selection(None, intro=intro, liste_familles=liste_familles_temp, liste_individus=liste_individus_temp)
        listeIndividusCoches = False
        if dlg.ShowModal() == wx.ID_OK :
            listeIndividusCoches = dlg.GetCoches()
        dlg.Destroy()
        return listeIndividusCoches

    def Effacer_familles(self):
        """ Effacer les familles """
        # Sélection des individus
        liste_individus = self.SelectionIndividus(intro=_(u"Cochez les individus à effacer :"))
        if liste_individus == False :
            return False

        # Demande de confirmation
        dlg = wx.MessageDialog(None, _(u"Confirmez-vous l'effacement de %d fiches familles et de %d fiches individuelles ?\n\nAttention, cette action est irréversible !") % (len(self.liste_familles), len(liste_individus)), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
        reponse = dlg.ShowModal()
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Attente
        dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant l'effacement..."), None)

        # Récupère les comptes_payeurs
        req = """SELECT IDfamille, IDcompte_payeur
        FROM comptes_payeurs
        WHERE IDfamille IN %s;""" % GestionDB.ConvertConditionChaine(self.liste_familles)
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        liste_comptes_payeurs = []
        for IDfamille, IDcompte_payeur in listeDonnees:
            liste_comptes_payeurs.append(IDcompte_payeur)

        # Familles
        liste_valeurs = [
            ("IDcaisse", None),
            ("num_allocataire", None),
            ("allocataire", None),
            ("internet_actif", 0),
            ("memo", None),
            ("prelevement_activation", None),
            ("prelevement_etab", None),
            ("prelevement_guichet", None),
            ("prelevement_numero", None),
            ("prelevement_cle", None),
            ("prelevement_banque", None),
            ("prelevement_individu", None),
            ("prelevement_nom", None),
            ("prelevement_rue", None),
            ("prelevement_cp", None),
            ("prelevement_ville", None),
            ("prelevement_cle_iban", None),
            ("prelevement_iban", None),
            ("prelevement_bic", None),
            ("prelevement_reference_mandat", None),
            ("prelevement_date_mandat", None),
            ("prelevement_memo", None),
            ("email_factures", None),
            ("email_recus", None),
            ("email_depots", None),
            ("titulaire_helios", None),
            ("code_comptable", None),
            ("idtiers_helios", None),
            ("natidtiers_helios", None),
            ("reftiers_helios", None),
            ("cattiers_helios", None),
            ("natjur_helios", None),
            ("autorisation_cafpro", None),
            ("autre_adresse_facturation", None),
            ("etat", "efface"),
            ]
        self.Modifier(listeID=self.liste_familles, nom_table="familles", champ_condition="IDfamille", liste_valeurs=liste_valeurs)

        # Historique
        self.Supprimer(listeID=self.liste_familles, nom_table="historique", champ_condition="IDfamille")

        # Liens
        self.Supprimer(listeID=self.liste_familles, nom_table="liens", champ_condition="IDfamille")

        # Messages
        self.Supprimer(listeID=self.liste_familles, nom_table="messages", champ_condition="IDfamille")

        # Payeurs
        liste_valeurs = [("nom", _(u"Payeur effacé")),]
        self.Modifier(listeID=liste_comptes_payeurs, nom_table="payeurs", champ_condition="IDcompte_payeur", liste_valeurs=liste_valeurs)

        # Pièces
        self.Supprimer(listeID=self.liste_familles, nom_table="pieces", champ_condition="IDfamille")

        # Questionnaires
        self.Supprimer(listeID=self.liste_familles, nom_table="questionnaire_reponses", champ_condition="IDfamille")

        # Quotients
        self.Supprimer(listeID=self.liste_familles, nom_table="quotients", champ_condition="IDfamille")

        # Rappels
        self.Supprimer(listeID=liste_comptes_payeurs, nom_table="rappels", champ_condition="IDcompte_payeur")

        # Rattachements
        #self.Supprimer(listeID=self.liste_familles, nom_table="rattachements", champ_condition="IDfamille")

        # Recus
        self.Supprimer(listeID=self.liste_familles, nom_table="recus", champ_condition="IDfamille")

        # Individus
        self.Effacer_individus(liste_individus=liste_individus)

        # Détruit dlgAttente
        del dlgAttente

        # Fin de procédure
        dlg = wx.MessageDialog(None, _(u"L'effacement a été effectué !"), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        return True

    def Effacer_individus(self, liste_individus=None):
        """ Effacer les individus """
        if liste_individus == None :
            liste_individus = self.liste_individus

            # Sélection des individus
            liste_individus = self.SelectionIndividus(intro=_(u"Cochez les individus à effacer :"))
            if liste_individus == False :
                return False

            # Demande de confirmation
            dlg = wx.MessageDialog(None, _(u"Confirmez-vous l'effacement de %d fiches individuelles ?\n\nAttention, cette action est irréversible !") % len(liste_individus), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return False

            # Attente
            dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant l'effacement..."), None)

        # Individus
        liste_valeurs = [
            ("IDcivilite", 1),
            ("nom", _(u"Individu effacé")),
            ("nom_jfille", u""),
            ("prenom", u""),
            ("num_secu", ""),
            ("IDnationalite", 73),
            ("date_naiss", None),
            ("IDpays_naiss", 73),
            ("cp_naiss", None),
            ("ville_naiss", None),
            ("deces", 0),
            ("annee_deces", None),
            ("adresse_auto", None),
            ("rue_resid", ""),
            ("cp_resid", None),
            ("ville_resid", None),
            ("IDsecteur", None),
            ("IDcategorie_travail", None),
            ("profession", ""),
            ("employeur", ""),
            ("travail_tel", None),
            ("travail_fax", None),
            ("travail_mail", None),
            ("tel_domicile", None),
            ("tel_mobile", None),
            ("tel_fax", None),
            ("mail", None),
            ("travail_tel_sms", 0),
            ("tel_domicile_sms", 0),
            ("tel_mobile_sms", 0),
            ("IDmedecin", None),
            ("memo", ""),
            ("IDtype_sieste", None),
            ("etat", "efface"),
            ]
        self.Modifier(listeID=liste_individus, nom_table="individus", champ_condition="IDindividu", liste_valeurs=liste_valeurs)

        # Abonnements
        self.Supprimer(listeID=liste_individus, nom_table="abonnements", champ_condition="IDindividu")

        # Badgeage
        self.Supprimer(listeID=liste_individus, nom_table="badgeage_journal", champ_condition="IDindividu")

        # Historique
        self.Supprimer(listeID=liste_individus, nom_table="historique", champ_condition="IDindividu")

        # Liens
        self.Supprimer(listeID=liste_individus, nom_table="liens", champ_condition="IDindividu_sujet")
        self.Supprimer(listeID=liste_individus, nom_table="liens", champ_condition="IDindividu_objet")

        # Mémo journalier
        self.Supprimer(listeID=liste_individus, nom_table="memo_journee", champ_condition="IDindividu")

        # Messages
        self.Supprimer(listeID=liste_individus, nom_table="messages", champ_condition="IDindividu")

        # Pièces
        self.Supprimer(listeID=liste_individus, nom_table="pieces", champ_condition="IDindividu")

        # Pb santé
        self.Supprimer(listeID=liste_individus, nom_table="problemes_sante", champ_condition="IDindividu")

        # Questionnaires
        self.Supprimer(listeID=liste_individus, nom_table="questionnaire_reponses", champ_condition="IDindividu")

        # Rattachements
        #self.Supprimer(listeID=liste_individus, nom_table="rattachements", champ_condition="IDindividu")

        # Scolarité
        self.Supprimer(listeID=liste_individus, nom_table="scolarite", champ_condition="IDindividu")

        # Transports
        self.Supprimer(listeID=liste_individus, nom_table="transports", champ_condition="IDindividu")

        # Vaccins
        self.Supprimer(listeID=liste_individus, nom_table="vaccins", champ_condition="IDindividu")

        # Fin de procédure
        if self.liste_individus != []:
            # Détruit dlgAttente
            del dlgAttente

            # Succès
            dlg = wx.MessageDialog(None, _(u"L'effacement a été effectué !"), _(u"Information"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        return True


class CTRL_Selection(HTL.HyperTreeList):
    def __init__(self, parent, liste_familles=None, liste_individus=None):
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.liste_familles = liste_familles
        self.liste_individus = liste_individus

        self.SetBackgroundColour(wx.WHITE)
        self.SetAGWWindowStyleFlag(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | HTL.TR_COLUMN_LINES |wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT)
        self.EnableSelectionVista(True)

        # ImageList
        il = wx.ImageList(16, 16)
        self.img_attestation = il.Add(wx.Bitmap(Chemins.GetStaticPath('Images/16x16/Attention.png'), wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Création des colonnes
        if len(self.liste_familles) > 0 :
            self.AddColumn(_(u"Famille/Individu rattaché"))
        else :
            self.AddColumn(_(u"Individu/Famille rattachée"))
        self.SetColumnWidth(0, 300)
        self.AddColumn(_(u"Catégorie"))
        self.SetColumnWidth(1, 100)
        self.AddColumn(_(u"Avertissements"))
        self.SetColumnWidth(2, 1000)
        self.MAJ()

    def MAJ(self):
        """ Met à jour (redessine) tout le contrôle """
        self.DeleteAllItems()
        self.root = self.AddRoot(_(u"Racine"))
        self.Remplissage()

    def Remplissage(self):
        if len(self.liste_familles) > 0 :
            for dictFamille in self.liste_familles:
                niveau1 = self.AppendItem(self.root, dictFamille["nomTitulaires"])
                self.SetPyData(niveau1, {"type": "famille", "ID": dictFamille["IDfamille"], "label": dictFamille["nomTitulaires"]})
                self.SetItemBold(niveau1, True)

                for dictIndividu in dictFamille["liste_rattaches"] :
                    niveau2 = self.AppendItem(niveau1, dictIndividu["nom_complet"], ct_type=1)
                    self.SetPyData(niveau2, {"type": "individu", "ID": dictIndividu["IDindividu"], "label": dictIndividu["nom_complet"], "infos" : dictIndividu["infos"]})
                    self.CheckItem(niveau2, True)
                    self.SetItemText(niveau2, dictIndividu["nom_categorie"], 1)
                    self.SetItemText(niveau2, ". ".join(dictIndividu["infos"]), 2)
                    if len(dictIndividu["infos"]) > 0 :
                        self.SetItemImage(niveau2, self.img_attestation, which=wx.TreeItemIcon_Normal)

        if len(self.liste_individus) > 0 :
            for dictIndividu in self.liste_individus:
                niveau1 = self.AppendItem(self.root, dictIndividu["nom_complet"], ct_type=1)
                self.SetPyData(niveau1, {"type": "individu", "ID": dictIndividu["IDindividu"], "label": dictIndividu["nom_complet"]})
                self.SetItemBold(niveau1, True)
                self.CheckItem(niveau1, True)

                for dictFamille in dictIndividu["liste_rattaches"] :
                    niveau2 = self.AppendItem(niveau1, _(u"Famille de %s") % dictFamille["nomTitulaires"])
                    self.SetPyData(niveau2, {"type": "famille", "ID": dictFamille["IDfamille"], "label": dictFamille["nomTitulaires"], "infos" : dictFamille["infos"]})
                    self.SetItemText(niveau2, dictFamille["nom_categorie"], 1)
                    self.SetItemText(niveau2, ". ".join(dictFamille["infos"]), 2)
                    if len(dictFamille["infos"]) > 0 :
                        self.SetItemImage(niveau2, self.img_attestation, which=wx.TreeItemIcon_Normal)

        self.ExpandAllChildren(self.root)

    def GetCoches(self, afficher_avertissements=False):
        listeCoches = []
        item = self.root
        for index in range(0, self.GetChildrenCount(self.root)):
            item = self.GetNext(item)
            ID = self.GetPyData(item)["ID"]

            if self.liste_familles != [] and self.GetPyData(item)["type"] == "individu" and self.IsItemChecked(item) and self.IsItemEnabled(item):
                nom_complet = self.GetPyData(item)["label"]
                infos = self.GetPyData(item)["infos"]
                if ID not in listeCoches:
                    listeCoches.append(ID)

            elif self.liste_individus != [] and self.GetPyData(item)["type"] == "famille" :
                nom_complet = self.GetPyData(self.GetItemParent(item))["label"]
                ID = self.GetPyData(self.GetItemParent(item))["ID"]
                infos = self.GetPyData(item)["infos"]
                if ID not in listeCoches:
                    listeCoches.append(ID)

            else :
                infos = []

            # Vérifie si infos à confirmer
            if len(infos) > 0:
                if afficher_avertissements == True :
                    intro = _(u"Souhaitez-vous sélectionner %s malgré les avertissements suivants ?") % nom_complet
                    dlg = DLG_Messagebox.Dialog(self, titre=_(u"Avertissement"), introduction=intro, detail=u"\n".join(infos), icone=wx.ICON_EXCLAMATION, boutons=[_(u"Oui"), _(u"Non"), _(u"Annuler")], defaut=1)
                    reponse = dlg.ShowModal()
                    dlg.Destroy()
                    if reponse != 0 :
                        return False

        return listeCoches




# -----------------------------------------------------------------------------------------

class DLG_Selection(wx.Dialog):
    def __init__(self, parent, intro=_(u"Cochez les individus à effacer :"), liste_familles=None, liste_individus=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        self.parent = parent
        self.liste_familles = liste_familles
        self.liste_individus = liste_individus

        self.label_intro = wx.StaticText(self, -1, intro)
        self.ctrl_selection = CTRL_Selection(self, liste_familles=liste_familles, liste_individus=liste_individus)
        self.ctrl_selection.SetMinSize((700, 450))

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(_(u"Sélection des individus"))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider et fermer")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler et fermer")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.label_intro, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)
        grid_sizer_base.Add(self.ctrl_selection, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)

        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.CenterOnScreen()

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        if self.GetCoches(afficher_avertissements=True) == False :
            return False
        self.EndModal(wx.ID_OK)

    def GetCoches(self, afficher_avertissements=False):
        return self.ctrl_selection.GetCoches(afficher_avertissements=afficher_avertissements)


if __name__ == "__main__":
    app = wx.App(0)
    #Effacer(liste_familles=[1, 2])
    Effacer(liste_individus=[1, 2, 3, 4, 5, 6])
