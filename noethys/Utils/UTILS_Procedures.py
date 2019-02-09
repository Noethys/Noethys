#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import datetime
import GestionDB
import six


DICT_PROCEDURES = {
    "A3687" : _(u"Transformation des QF de tarifs_lignes unicode->float"),
    "A3688" : _(u"Suppression des ouvertures avec IDunite=5"),
    "X1234" : _(u"Exportation des données d'une table dans la table DEFAUT"),
    "S1290" : _(u"Modification du IDcategorie_tarif"),
    "D1051" : _(u"Ajout du champ type dans la table Documents"),
    "E4072" : _(u"Suppression des prestations sans consommations associées"),
    "X0202" : _(u"Ajout de du champ forfait_date_debut à la table Prestations"),
    "G2345" : _(u"Attribution d'un ordre aux groupes"),
    "A4567" : _(u"Suppression de toutes les perspectives de la page d'accueil"),
    "A5000" : _(u"Réalisation d'une requête"),
    "A5134" : _(u"Exécution de l'ancienne version de l'état global des consommations"),
    "A5200" : _(u"Correction des arrondis"),
    "A5300" : _(u"Nettoyage des groupes d'activités"),
    "A5400" : _(u"Réparation de l'autoincrement sqlite de la table tarifs_lignes"),
    "A5500" : _(u"Réparation des liens prestations/factures"),
    "A7650" : _(u"Renseignement automatique du titulaire Hélios dans toutes les fiches familles"),
    "A8120" : _(u"Renseignement automatique du type comptable du mode de règlement (banque ou caisse)"),
    "A8260" : _(u"Modification de la table Paramètres"),
    "A8452" : _(u"Nettoyage des liens superflus"),
    "A8574" : _(u"Mise à niveau de la base de données"),
    "A8623" : _(u"Remplacement des exercices comptables par les dates budgétaires"),
    "A8733" : _(u"Correction des IDinscription disparus"),
    "A8823" : _(u"Création de tous les index"),
    "A8836" : _(u"Suppression des consommations avec prestation disparue"),
    "A8941" : _(u"Remplit automatiquement le champ états de la table Tarifs"),
    "A8956" : _(u"Réparation des factures : Rapprochement des factures et des prestations détachées"),
    "A8967" : _(u"Transfert des numéros des numéros des factures vers le champ str"),
    "A8971" : _(u"Attribution du type de quotient CAF à tous les quotients existants"),
    "A9001" : _(u"Modification de la structure de la table Documents"),
    "A9023" : _(u"Correction des ouvertures avec IDgroupe=0"),
    "A9054" : _(u"Importation des modèles d'Emails depuis la base défaut"),
    "A9061" : _(u"Modification de la structure de la table Documents"),
    "A9073" : _(u"Cryptage des mots de passe utilisateurs"),
    "A9074" : _(u"Cryptage des mots de passe utilisateurs dans nouveau champ mdpcrypt"),
    "A9075" : _(u"Suppression des mots de passe utilisateurs en clair"),
    "A9078" : _(u"Suppression des suppressions des consommations avec IDinscription null"),
    "A9079" : _(u"Création de la table PHOTOS"),
    "A9080" : _(u"Création de la table DOCUMENTS"),
    "A9081" : _(u"Création du profil de configuration par défaut pour la liste des infos médicales"),
    "A9102" : _(u"Suppression des données personnelles"),
    "A9105" : _(u"Remplissage du champ statut de la table inscriptions"),
    "A9120" : _(u"Effacement de toutes les actions du portail"),
    "A9122" : _(u"Réparation des prestations : Rapprochement des prestations et des consommations détachées"),
    "A9130" : _(u"Remplissage du champ moteur de la table adresses_mail"),
}



# -------------------------------------------------------------------------------------------------------------------------

def Procedure(code=""):
    # Recherche si procédure existe
    if (code in DICT_PROCEDURES) == False :
        dlg = wx.MessageDialog(None, _(u"Désolé, cette procédure n'existe pas..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    titre = DICT_PROCEDURES[code]
    # Demande de confirmation de lancement
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer la procédure suivante ?\n\n   -> %s   ") % titre, _(u"Lancement de la procédure"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
    reponse = dlg.ShowModal() 
    dlg.Destroy()
    if reponse != wx.ID_YES :
        return
    # Lancement
    print("Lancement de la procedure '%s'..." % code)
    try :
        exec("%s()" % code)
    except Exception as err :
        dlg = wx.MessageDialog(None, _(u"Désolé, une erreur a été rencontrée :\n\n-> %s  ") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    # Fin
    dlg = wx.MessageDialog(None, _(u"La procédure s'est terminée avec succès."), _(u"Procédure terminée"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    print("Fin de la procedure '%s'." % code)
    return

def EcritStatusbar(texte=u""):
    try :
        topWindow = wx.GetApp().GetTopWindow() 
        topWindow.SetStatusText(texte)
    except : 
        pass

# -------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------

def A3687():
    """
    Vérifie que le montant du QF dans la table tarifs_lignes est un float et non un unicode
    """
    DB = GestionDB.DB()
    req = """SELECT IDligne, qf_min, qf_max
    FROM tarifs_lignes; """ 
    DB.ExecuterReq(req)
    listeLignes = DB.ResultatReq()
    for IDligne, qf_min, qf_max in listeLignes :
        if type(qf_min) == six.text_type or type(qf_min) == str : DB.ReqMAJ("tarifs_lignes", [("qf_min", float(qf_min.replace(",","."))),], "IDligne", IDligne)
        if type(qf_max) == six.text_type or type(qf_max) == str : DB.ReqMAJ("tarifs_lignes", [("qf_max", float(qf_max.replace(",","."))),], "IDligne", IDligne)
    DB.Close()

def A3688():
    DB = GestionDB.DB()
    DB.ReqDEL("ouvertures", "IDunite", 5)
    DB.Close()

def X1234():
    """ Exportation des données d'une table vers la table DEFAUT """
    # Demande le nom de la table à exporter
    DB = GestionDB.DB()
    listeTablesTemp = DB.GetListeTables() 
    listeTables = []
    for donnees in listeTablesTemp :
        listeTables.append(donnees[0])
    dlg = wx.MultiChoiceDialog(None, _(u"Cochez les tables à exporter :"), _(u"Exportation vers la table DEFAUT"), listeTables)
    if dlg.ShowModal() == wx.ID_OK :
        selections = dlg.GetSelections()
        nomsTable = [listeTables[x] for x in selections]
        for nomTable in nomsTable :
            DB.Exportation_vers_base_defaut(nomTable)
    dlg.Destroy()
    DB.Close()

def S1290():
    """
    Récupère le IDcategorie_tarif pour le mettre dans le nouveau champ 
    "categories_tarifs" de la table "tarifs"
    """
    DB = GestionDB.DB()
    
    # Déplace le champ IDcategorie_tarif dans la table tarifs
    req = """SELECT IDtarif, IDcategorie_tarif, IDnom_tarif FROM tarifs; """ 
    DB.ExecuterReq(req)
    listeTarifs = DB.ResultatReq()
    for IDtarif, IDcategorie_tarif, IDnom_tarif in listeTarifs :
        if IDcategorie_tarif != None :
            # Remplit le nouveau champ categories_tarifs de la table Tarifs
            DB.ReqMAJ("tarifs", [("categories_tarifs", str(IDcategorie_tarif)),], "IDtarif", IDtarif)
            
            # Vide le champ IDcategorie_tarif de la table Tarifs
            DB.ReqMAJ("tarifs", [("IDcategorie_tarif", None),], "IDtarif", IDtarif)
            
            # Remplit le nouveau champ IDcategorie_tarif de la table Prestations
            DB.ReqMAJ("prestations", [("IDcategorie_tarif", IDcategorie_tarif),], "IDtarif", IDtarif)
            
    # Recherche des noms de tarifs
    req = """SELECT IDnom_tarif, IDactivite, IDcategorie_tarif, nom FROM noms_tarifs ORDER BY IDnom_tarif; """ 
    DB.ExecuterReq(req)
    listeNomsTarifs = DB.ResultatReq()
    
    dictDonnees = {}
    for IDnom_tarif, IDactivite, IDcategorie_tarif, nom in listeNomsTarifs :

        # Vidage du champ IDcategorie_tarif de la table noms_tarifs
        DB.ReqMAJ("noms_tarifs", [("IDcategorie_tarif", None),], "IDnom_tarif", IDnom_tarif)

        # Regroupement par activité
        if (IDactivite in dictDonnees) == False :
            dictDonnees[IDactivite] = {}
        
        # Regroupement par nom de tarif
        if (nom in dictDonnees[IDactivite]) == False :
            dictDonnees[IDactivite][nom] = []
        dictDonnees[IDactivite][nom].append(IDnom_tarif)
    
    # Regroupement par activités et noms de tarifs
    for IDactivite, dictNoms in dictDonnees.items() :
        for nom, listeIDnom_tarif in dictNoms.items() :
            # Conservation du premier IDnom_tarif
            newIDnom_tarif = listeIDnom_tarif[0]
            
            if len(listeIDnom_tarif) > 1 :
                for IDnom_tarif in listeIDnom_tarif[1:] :
                    # Suppression des IDnom_tarifs suivants
                    DB.ReqDEL("noms_tarifs", "IDnom_tarif", IDnom_tarif)
                    # Ré-attribution du nouvel IDnom_tarif aux tarifs
                    DB.ReqMAJ("tarifs", [("IDnom_tarif", newIDnom_tarif),], "IDnom_tarif", IDnom_tarif)
    
    DB.Close()

def D1051():
    """ Création du champ TYPE dans la table DOCUMENTS """
    DB = GestionDB.DB(suffixe="DOCUMENTS") 
    DB.AjoutChamp("documents", "type", "VARCHAR(50)")
    DB.AjoutChamp("documents", "label", "VARCHAR(400)")
    DB.AjoutChamp("documents", "IDreponse", "INTEGER")
    DB.Close()
    
def E4072():
    """ Suppression des prestations sans consommations associées """    
    print("Lancement de la procedure E4072...")
    DB = GestionDB.DB()
    
    # Récupération des prestations
    req = """SELECT IDprestation, label FROM prestations 
    WHERE categorie='consommation' AND IDfacture IS NULL;"""
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    
    # Récupération des consommations
    req = """SELECT IDconso, IDprestation FROM consommations;""" 
    DB.ExecuterReq(req)
    listeConsommations = DB.ResultatReq()
    DB.Close()
    
    # Analyse
    dictPrestations = {}
    for IDconso, IDprestation in listeConsommations :
        if (IDprestation in dictPrestations) == False :
            dictPrestations[IDprestation] = []
        dictPrestations[IDprestation].append(IDconso)
    
    dictResultats = {}
    for IDprestation, label in listePrestations :
        if (IDprestation in dictPrestations) == False :
            if (label in dictResultats) == False :
                dictResultats[label] = []
            dictResultats[label].append(IDprestation)
    
    listeDonnees = []
    for label, listePrestationsTemp in dictResultats.items() :
        texte = _(u"%s (%d prestations)") % (label, len(listePrestationsTemp))
        listeDonnees.append((texte, label, listePrestationsTemp))
    listeDonnees.sort() 
    
    listeLabels = []
    for texte, label, listePrestationsTemp in listeDonnees :
        listeLabels.append(texte)
    
    message = _(u"Cochez les prestations sans consommations associées que vous souhaitez supprimer.\n(Pensez à sauvegarder votre fichier avant d'effectuer cette procédure !)")
    dlg = wx.MultiChoiceDialog(None, message, _(u"Suppression des prestations sans consommations associées"), listeLabels)
    dlg.SetSize((450, 500))
    dlg.CenterOnScreen() 
    if dlg.ShowModal() == wx.ID_OK:
        message = _(u"Veuillez patienter durant la procédure...")
        dlgAttente = wx.BusyInfo(message, None)
        if 'phoenix' not in wx.PlatformInfo:
            wx.Yield()
        selections = dlg.GetSelections()
        DB = GestionDB.DB()
        for index in selections :
            texte, label, listePrestationsTemp = listeDonnees[index]
            for IDprestation in listePrestationsTemp :
                DB.ReqDEL("prestations", "IDprestation", IDprestation)
        DB.Close()
        del dlgAttente
    dlg.Destroy()
    print("Fin de la procedure E4072.")
    
def X0202():
    """ Ajout du champ forfait_date_debut à la table Prestations """
    DB = GestionDB.DB() 
    DB.AjoutChamp("prestations", "forfait_date_debut", "VARCHAR(10)")
    DB.Close()
    
def G2345():
    """ Attribution d'un ordre aux groupes """
    DB = GestionDB.DB() 
    # Récupération des groupes
    req = """SELECT IDgroupe, IDactivite FROM groupes ORDER BY IDactivite, IDgroupe;""" 
    DB.ExecuterReq(req)
    listeGroupes = DB.ResultatReq()
    dictGroupes = {}
    for IDgroupe, IDactivite in listeGroupes :
        if (IDactivite in dictGroupes) == False :
            dictGroupes[IDactivite] = []
        dictGroupes[IDactivite].append(IDgroupe)
    # Attribution d'un numéro d'ordre
    for IDactivite, listeGroupes in dictGroupes.items() :
        ordre = 1
        for IDgroupe in listeGroupes :
            DB.ReqMAJ("groupes", [("ordre", ordre),], "IDgroupe", IDgroupe)
            ordre += 1
    DB.Close()

def A4567():
    """ Suppression de toutes les perspectives de la page d'accueil """
    topWindow = wx.GetApp().GetTopWindow() 
    topWindow.SupprimeToutesPerspectives()

def A5000():
    """ Requete sur base de données active """
    # Demande la requête souhaitée
    dlg = wx.TextEntryDialog(None, _(u"Saisissez la requête :"), _(u"Requête"), "")
    if dlg.ShowModal() == wx.ID_OK:
        req = dlg.GetValue()
        dlg.Destroy()
    else :
        dlg.Destroy()
        return
    # Réalisation de la requête
    try :
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        DB.Commit()
        DB.Close()
    except Exception as err:
        print("Erreur dans procedure A5000 :", err)

def A5134():
    """ Ancienne fonction Etat global des conso """
    from Dlg import DLG_Etat_global_archives
    dlg = DLG_Etat_global_archives.Dialog(None)
    dlg.ShowModal() 
    dlg.Destroy()

def A5200():
    """ Arrondi de toutes les prestations et ventilations de la base de données !!! """
    from Utils.UTILS_Decimal import FloatToDecimal as FloatToDecimal
    DB = GestionDB.DB() 

    dlgAttente = wx.BusyInfo(_(u"Veuillez patienter durant la procédure... Celle-ci peut nécessiter quelques minutes..."), None)
    if 'phoenix' not in wx.PlatformInfo:
        wx.Yield()

    # Récupère les prestations
    req = """SELECT IDprestation, montant FROM prestations;"""
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq() 
    
    # Récupère la ventilation
    req = """SELECT IDventilation, montant FROM ventilation;"""
    DB.ExecuterReq(req)
    listeVentilations = DB.ResultatReq() 

    # Modification des arrondis
    total = len(listePrestations) + len(listeVentilations)
    index = 0
    
    for IDprestation, montant in listePrestations :
        EcritStatusbar(_(u"Correction des arrondis... Merci de patienter...             -> %d %% effectués") % (index * 100 / total))
        DB.ReqMAJ("prestations", [("montant", FloatToDecimal(montant, plusProche=True)),], "IDprestation", IDprestation)
        index += 1
    
    for IDventilation, montant in listeVentilations :
        EcritStatusbar(_(u"Correction des arrondis... Merci de patienter...             - > %d %% effectués") % (index * 100 / total))
        DB.ReqMAJ("ventilation", [("montant", FloatToDecimal(montant, plusProche=True)),], "IDventilation", IDventilation)
        index += 1
        
    DB.Close()
    EcritStatusbar(u"")
    del dlgAttente

def A5300():
    """ Nettoyage des groupes d'activités en double """
    DB = GestionDB.DB() 
    req = """SELECT IDgroupe_activite, IDtype_groupe_activite, IDactivite
    FROM groupes_activites;"""
    DB.ExecuterReq(req)
    listeRegroupements = DB.ResultatReq()
    listeTraites = []
    for IDgroupe_activite, IDtype_groupe_activite, IDactivite in listeRegroupements :
        key = (IDtype_groupe_activite, IDactivite)
        if key in listeTraites :
            DB.ReqDEL("groupes_activites", "IDgroupe_activite", IDgroupe_activite)
        else :
            listeTraites.append(key)
    DB.Close()
    
def A5400():
    """ Réparation de l'autoincrement sqlite de la table tarifs_lignes """
    nomTable = "tarifs_lignes"
    DB = GestionDB.DB() 
    if DB.isNetwork == False :
        # Recherche si des enregistrements existent dans la table tarifs_lignes
        req = """SELECT * FROM %s;""" % nomTable
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        if len(listeTemp) > 0 :
            # Recherche si la table est présente dans la table sqlite_seq
            req = """SELECT name, seq
            FROM sqlite_sequence
            WHERE name='%s';""" % nomTable
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()    
            if len(listeDonnees) == 0 :
                # Si aucune référence dans la table sqlite_sequence, on répare la table
                DB.ReparationTable(nomTable)
    DB.Close()
    
    
def A5500():
    """ Réparation des liens prestations/factures """
    from Utils import UTILS_Dates
    import time
    from Dlg import DLG_Selection_dates
    
    dlg = DLG_Selection_dates.Dialog(None)
    if dlg.ShowModal() == wx.ID_OK:
        periode_date_debut = dlg.GetDateDebut() 
        periode_date_fin = dlg.GetDateFin() 
        dlg.Destroy()
    else :
        dlg.Destroy()
        return
    
    DB = GestionDB.DB() 
    
    # Lecture des factures
    req = """SELECT IDfacture, IDcompte_payeur, date_debut, date_fin
    FROM factures;"""
    DB.ExecuterReq(req)
    listeFactures = DB.ResultatReq()    
    dictFactures = {}
    for IDfacture, IDcompte_payeur, date_debut, date_fin in listeFactures :
        if (IDcompte_payeur in dictFactures) == False :
            dictFactures[IDcompte_payeur] = []
        dictFactures[IDcompte_payeur].append({"IDfacture":IDfacture, "date_debut":UTILS_Dates.DateEngEnDateDD(date_debut), "date_fin":UTILS_Dates.DateEngEnDateDD(date_fin)})
    
    # Lecture des prestations
    req = """SELECT IDprestation, IDcompte_payeur, date, IDfacture
    FROM prestations
    WHERE IDfacture IS NULL AND date>='%s' AND date<='%s';""" % (periode_date_debut, periode_date_fin)
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()    
    nbrePrestations = len(listePrestations)
    
    # Demande de confirmation
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer cette procédure pour %d prestations ?\n\n(Vous pourrez suivre la progression dans la barre d'état)") % nbrePrestations, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
    if dlg.ShowModal() != wx.ID_YES :
        dlg.Destroy()
        return
    dlg.Destroy()

    # Traitement
    index = 0
    nbreSucces = 0
    for IDprestation, IDcompte_payeur, date, IDfacture in listePrestations :
        date = UTILS_Dates.DateEngEnDateDD(date)
        
        # Recherche la facture probable
        if IDcompte_payeur in dictFactures :
            for dictFacture in dictFactures[IDcompte_payeur] :
                if date >= dictFacture["date_debut"] and date <= dictFacture["date_fin"] :
                    IDfacture = dictFacture["IDfacture"]
                    DB.ReqMAJ("prestations", [("IDfacture", IDfacture),], "IDprestation", IDprestation)
##                    print "Traitement en cours...   %d/%d ....  Prestation ID%d -> Facture ID%d" % (index, nbrePrestations, IDprestation, IDfacture)
                    EcritStatusbar(_(u"Traitement en cours...   %d/%d ....  Prestation ID%d -> Facture ID%d") % (index, nbrePrestations, IDprestation, IDfacture))
                    nbreSucces += 1
                    time.sleep(0.05)
        
        index += 1
    
    DB.Close()
    
    # Fin du traitement
    dlg = wx.MessageDialog(None, _(u"Procédure terminée !\n\n%d prestations sur %s ont été rattachées avec succès !") % (nbreSucces, nbrePrestations), _(u"Fin"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    
    
def A7650():
    """ Renseignement automatique du titulaire Hélios dans toutes les fiches familles """
    # Recherche des titulaires potentiels pour chaque famille (les pères en priorité)
    DB = GestionDB.DB()
    req = """SELECT IDfamille, individus.IDindividu, IDcivilite, nom, prenom
    FROM rattachements
    LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
    WHERE IDcategorie=1 AND titulaire=1
    ORDER BY IDcivilite, individus.IDindividu;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    dictIndividus = {}
    for IDfamille, IDindividu, IDcivilite, nom, prenom in listeDonnees :
        if (IDfamille in dictIndividus) == False :
            dictIndividus[IDfamille] = []
        dictIndividus[IDfamille].append({"IDcivilite":IDcivilite, "IDindividu":IDindividu, "nom":nom, "prenom":prenom})
    
    # Recherche des familles
    DB = GestionDB.DB()
    req = """SELECT IDfamille, titulaire_helios
    FROM familles
    WHERE titulaire_helios IS NULL OR titulaire_helios='';"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    listeModifications = []
    for IDfamille, titulaire_helios in listeDonnees :
        if titulaire_helios == None or titulaire_helios == "" :
            if IDfamille in dictIndividus :
                dictIndividu = dictIndividus[IDfamille][0]
                titulaire_helios = dictIndividu["IDindividu"]
                listeModifications.append((titulaire_helios, IDfamille))
    
    print("Nbre de titulaires HELIOS a enregistrer : %d" % len(listeModifications))
        
    # Enregistrement des modifications
    DB = GestionDB.DB() 
    DB.Executermany("UPDATE familles SET titulaire_helios=? WHERE IDfamille=?", listeModifications, commit=False)
    DB.Commit() 
    DB.Close()


def A8120():
    """ Renseignement automatique du type comptable du mode de règlement (banque ou caisse) """
    DB = GestionDB.DB() 
    DB.ExecuterReq("UPDATE modes_reglements SET type_comptable='caisse' WHERE IDmode=1")
    DB.ExecuterReq("UPDATE modes_reglements SET type_comptable='banque' WHERE IDmode<>1")
    DB.Commit() 
    DB.Close()

def A8260():
    """ Modification de la table Paramètres sur les fichiers réseau """
    DB = GestionDB.DB() 
    if DB.isNetwork == True :
        DB.ExecuterReq("ALTER TABLE parametres MODIFY parametre VARCHAR(455)")
        DB.Commit() 
    DB.Close()
    
def A8452():
    """ Nettoyage des liens superflus """
    DB = GestionDB.DB()
    req = """SELECT IDlien, IDfamille, IDindividu_sujet, IDtype_lien, IDindividu_objet, responsable, IDautorisation
    FROM liens
    ORDER BY IDlien;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
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
    listeLiensASupprimer = []
    listeIDfamille = []
    for IDfamille, dictKeys in dictLiens.items() :
        for key, listeIDlien in dictKeys.items() :
            if len(listeIDlien) > 1 :
                # Suppression des liens obsolètes
                for IDlien in listeIDlien[1:] :
                    DB.ReqDEL("liens", "IDlien", IDlien)
                    listeLiensASupprimer.append(IDlien)
                if IDfamille not in listeIDfamille :
                    listeIDfamille.append(IDfamille)
    DB.Close() 
    print("Nbre de liens supprimes :", len(listeLiensASupprimer))
    print(listeIDfamille)
    
def A8574():
    """ Mise à niveau de la base de données """
    import FonctionsPerso
    versionApplication = FonctionsPerso.GetVersionLogiciel()
    dlg = wx.TextEntryDialog(None, _(u"Saisissez le numéro de version à partir duquel vous souhaitez \neffectuer la mise à niveau ('x.x.x.x'):"), _(u"Mise à niveau de la base de données"), versionApplication)
    reponse = dlg.ShowModal() 
    version = dlg.GetValue()
    dlg.Destroy()
    if reponse != wx.ID_OK:
        return
    
    valide = True
    try :
        version = tuple([int(x) for x in version.split(".")])
    except :
        valide = False
    if len(version) != 4 :
        valide = False
    
    if valide == False :
        dlg = wx.MessageDialog(None, _(u"Impossible d'effectuer la procédure !\n\nLe numéro de version que vous avez saisi semble erroné. Vérifiez qu'il est formaté de la façon suivante : 'x.x.x.x'"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False
    
    print("Procedure manuelle de mise a niveau de la base de donnee depuis la version : ", version)
    DB = GestionDB.DB()        
    resultat = DB.ConversionDB(version)
    DB.Close()
    print(resultat)
    
def A8623():
    """ Remplacement des exercices comptables par les dates budgétaires """
    DB = GestionDB.DB()
    
    # Remplacement dans la ventilation des opérations de trésorerie
    req = """SELECT IDventilation, compta_ventilation.IDexercice, date_budget, compta_exercices.date_debut
    FROM compta_ventilation
    LEFT JOIN compta_exercices ON compta_exercices.IDexercice = compta_ventilation.IDexercice
    WHERE date_budget IS NULL;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    for IDventilation, IDexercice, date_budget, date_debut_exercice in listeDonnees :
        DB.ReqMAJ("compta_ventilation", [("date_budget", date_debut_exercice),], "IDventilation", IDventilation)
    
    # Remplacement dans les budgets
    req = """SELECT IDbudget, compta_budgets.IDexercice, compta_budgets.date_debut, compta_budgets.date_fin, compta_exercices.date_debut, compta_exercices.date_fin
    FROM compta_budgets
    LEFT JOIN compta_exercices ON compta_exercices.IDexercice = compta_budgets.IDexercice
    WHERE compta_budgets.date_debut IS NULL;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    for IDbudget, IDexercice, date_debut, date_fin, date_debut_exercice, date_fin_exercice in listeDonnees :
        DB.ReqMAJ("compta_budgets", [("date_debut", date_debut_exercice), ("date_fin", date_fin_exercice)], "IDbudget", IDbudget)
    
    DB.Close() 
    
def A8733():
    """ Correction des IDinscription disparus """
    DB = GestionDB.DB()
    
    # Récupération des tous les IDinscription
    req = """SELECT IDinscription, IDindividu, IDactivite, IDcompte_payeur
    FROM inscriptions;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictInscriptions = {}
    for IDinscription, IDindividu, IDactivite, IDcompte_payeur in listeDonnees :
        dictInscriptions[(IDindividu, IDactivite, IDcompte_payeur)] = IDinscription
            
    # Recherche des IDinscription NULL dans les consommations
    req = """SELECT IDconso, IDindividu, IDactivite, IDcompte_payeur
    FROM consommations
    WHERE IDinscription IS NULL;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    print("%d IDinscription NULL sont a corriger..." % len(listeDonnees))
    
    listeModifications = []
    for IDconso, IDindividu, IDactivite, IDcompte_payeur in listeDonnees :
        if (IDindividu, IDactivite, IDcompte_payeur) in dictInscriptions :
            IDinscription = dictInscriptions[(IDindividu, IDactivite, IDcompte_payeur)]
            listeModifications.append((IDinscription, IDconso)) 
            
    # Enregistrement du IDinscription dans la consommation
    if len(listeModifications) > 0 :
        DB.Executermany(_(u"UPDATE consommations SET IDinscription=? WHERE IDconso=?"), listeModifications, commit=False)
        DB.Commit() 
    
    DB.Close() 
    
    
def A8823():
    """ Creation de tous les index """
    DB = GestionDB.DB(suffixe="DATA")
    DB.CreationTousIndex() 
    DB.Close() 
    DB = GestionDB.DB(suffixe="PHOTOS")
    DB.CreationTousIndex() 
    DB.Close() 

def A8836():
    """ Suppression des consommations dont la prestation a été supprimée """
    # Recherche
    DB = GestionDB.DB()
    req = """SELECT IDconso, consommations.IDindividu, IDinscription, consommations.date, IDunite, consommations.IDprestation, prestations.IDprestation, consommations.etat FROM consommations
    LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
    WHERE consommations.IDprestation IS NOT NULL AND prestations.IDprestation IS NULL AND consommations.etat='reservation'
    ORDER BY consommations.IDindividu, IDunite;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    print("Nbre consommations avec prestations supprimées : ", len(listeDonnees))
    listeConso = []
    for listeTemp in listeDonnees :
        listeConso.append(listeTemp[0])
    # Suppression
    DB = GestionDB.DB()
    for IDconso in listeConso :
        DB.ReqDEL("consommations", "IDconso", IDconso)
    DB.Close()
    
def A8941():
    """ Remplit automatiquement le champs états de la table Tarifs """
    DB = GestionDB.DB()
    DB.ExecuterReq("""UPDATE tarifs SET etats='reservation;present;absenti';""")
    DB.Commit()
    DB.Close()

def A8956():
    """ Réparation des factures : Rapprochement des factures et des prestations détachées """
    from Utils.UTILS_Decimal import FloatToDecimal
    from Utils import UTILS_Dates
    import copy

    DB = GestionDB.DB()

    # Lecture des prestations
    req = """SELECT IDprestation, IDcompte_payeur, date, montant, IDfacture
    FROM prestations
    ;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictPrestations = {}
    dictPrestationsFactures = {}
    for IDprestation, IDcompte_payeur, date, montant, IDfacture in listeDonnees :
        montant = FloatToDecimal(montant)
        date = UTILS_Dates.DateEngEnDateDD(date)
        dictTemp = {"IDprestation":IDprestation, "IDcompte_payeur":IDcompte_payeur, "date":date, "montant":montant, "IDfacture":IDfacture}

        if (IDcompte_payeur in dictPrestations) == False :
            dictPrestations[IDcompte_payeur] = []
        dictPrestations[IDcompte_payeur].append(dictTemp)

        if (IDfacture in dictPrestationsFactures) == False :
            dictPrestationsFactures[IDfacture] = {"total" : FloatToDecimal(0.0), "prestations" : []}
        dictPrestationsFactures[IDfacture]["prestations"].append(dictTemp)
        dictPrestationsFactures[IDfacture]["total"] += montant

    # Lecture des factures
    req = """SELECT IDfacture, IDcompte_payeur, date_debut, date_fin, total
    FROM factures
    ;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listePrestationsReparees = []
    listeFacturesReparees = []
    for IDfacture, IDcompte_payeur, date_debut, date_fin, total_facture in listeDonnees :
        date_debut = UTILS_Dates.DateEngEnDateDD(date_debut)
        date_fin = UTILS_Dates.DateEngEnDateDD(date_fin)
        total_facture = FloatToDecimal(total_facture)

        # Vérifie si le total des prestations correspond bien au total de la facture
        if IDfacture in dictPrestationsFactures:
            total_prestations = dictPrestationsFactures[IDfacture]["total"]
        else :
            total_prestations = FloatToDecimal(0.0)

        if total_prestations < total_facture :
            #print "PROBLEME : ", IDcompte_payeur, IDfacture, total_prestations, total_facture

            # Recherche les possibles prestations à rattacher
            listePrestationsTrouvees = []
            totalPrestationsTrouvees = copy.copy(total_prestations)
            if IDcompte_payeur in dictPrestations :
                for dictPrestation in dictPrestations[IDcompte_payeur] :
                    if dictPrestation["IDfacture"] == None and dictPrestation["date"] >= date_debut and dictPrestation["date"] <= date_fin :
                        listePrestationsTrouvees.append(dictPrestation)
                        totalPrestationsTrouvees += dictPrestation["montant"]

                # Si la liste des prestations correspond bien aux prestations manquantes de la facture, on les associe
                if total_facture == totalPrestationsTrouvees :
                    for dictPrestation in listePrestationsTrouvees :
                        DB.ReqMAJ("prestations", [("IDfacture", IDfacture),], "IDprestation", dictPrestation["IDprestation"])
                        listePrestationsReparees.append(dictPrestation)
                        if IDfacture not in listeFacturesReparees :
                            listeFacturesReparees.append(IDfacture)

    DB.Close()

    # Message de fin
    dlg = wx.MessageDialog(None, _(u"Résultats :\n\nNombre de factures réparées = %d\nNombre de prestations réparées = %d" % (len(listeFacturesReparees), len(listePrestationsReparees))), _(u"Fin de la procédure"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def A8967():
    """ Transfert des numéros des numéros des factures vers le champ str """
    DB = GestionDB.DB()

    # Recherche des IDinscription NULL dans les consommations
    req = """SELECT IDfacture, numero
    FROM factures
    WHERE IDfacture IS NOT NULL;"""
    DB.ExecuterReq(req)
    listeFactures = DB.ResultatReq()

    listeModifications = []
    for IDfacture, numero in listeFactures :
        listeModifications.append((str(numero), IDfacture))

    if len(listeModifications) > 0 :
        DB.Executermany(_(u"UPDATE factures SET numerostr=? WHERE IDfacture=?"), listeModifications, commit=False)
        DB.Commit()

def A8971():
    """ Attribution du type de quotient CAF à tous les quotients existants """
    # Recherche des types de quotients existants
    DB = GestionDB.DB()
    req = """SELECT IDtype_quotient, nom FROM types_quotients;"""
    DB.ExecuterReq(req)
    listeTypesQuotients = DB.ResultatReq()
    if len(listeTypesQuotients) == 0 :
        IDtype_quotient = DB.ReqInsert("types_quotients", [("nom", u"CAF"),])
    else :
        IDtype_quotient = listeTypesQuotients[0][0]
    # Remplissage des quotients
    DB.ExecuterReq("UPDATE quotients SET IDtype_quotient=%d;" % IDtype_quotient)
    DB.Commit()
    DB.Close()

def A9001():
    """ Modification de la table DOCUMENTS """
    try :
        DB = GestionDB.DB(suffixe="DOCUMENTS")
        DB.AjoutChamp("documents", "IDtype_piece", "INTEGER")
        DB.Close()
    except :
        pass

def A9023():
    """ Correction des ouvertures avec IDgroupe=0 """
    DB = GestionDB.DB()

    # Récupération des groupes
    req = """SELECT IDgroupe, IDactivite FROM groupes;"""
    DB.ExecuterReq(req)
    liste_groupes = DB.ResultatReq()
    dict_groupes = {}
    for IDgroupe, IDactivite in liste_groupes :
        if IDactivite not in dict_groupes :
            dict_groupes[IDactivite] = []
        dict_groupes[IDactivite].append(IDgroupe)

    # Récupération des ouvertures
    req = """SELECT IDouverture, IDactivite, IDgroupe FROM ouvertures;"""
    DB.ExecuterReq(req)
    liste_ouvertures = DB.ResultatReq()
    liste_modifications = []
    for IDouverture, IDactivite, IDgroupe in liste_ouvertures :
        if IDgroupe == 0 :
            # Recherche un groupe pour cette activité
            if IDactivite in dict_groupes :
                if len(dict_groupes[IDactivite]) == 1 :
                    IDgroupe = dict_groupes[IDactivite][0]
                    liste_modifications.append((IDgroupe, IDouverture))

    print("Procedure A9023 : Nbre ouvertures a corriger =", len(liste_modifications))

    # Enoi des modifications à la DB
    DB.Executermany("UPDATE ouvertures SET IDgroupe=? WHERE IDouverture=?", liste_modifications, commit=True)
    DB.Close()


def A9054():
    """ Importation des modèles d'Emails depuis la base défaut """

    # Récupération des modèles d'Emails dans la base Défaut
    DB = GestionDB.DB(nomFichier=Chemins.GetStaticPath("Databases/Defaut.dat"), suffixe=None)
    req = """SELECT IDmodele, categorie, nom, description, objet, texte_xml, IDadresse, defaut
    FROM modeles_emails;"""
    DB.ExecuterReq(req)
    liste_modeles_defaut = DB.ResultatReq()
    DB.Close()

    # Récupération des modèles d'Emails de la base actuelle
    DB = GestionDB.DB()
    req = """SELECT IDmodele, categorie
    FROM modeles_emails;"""
    DB.ExecuterReq(req)
    liste_modeles = DB.ResultatReq()

    # Recensement des catégories pour lesquelles des modèles existant déjà
    liste_categories_presentes = []
    for IDmodele, categorie in liste_modeles :
        if categorie not in liste_categories_presentes :
            liste_categories_presentes.append(categorie)

    # Ajout des modèles dans les catégories qui n'ont aucun modèle existant
    nbre_ajouts = 0
    for IDmodele, categorie, nom, description, objet, texte_xml, IDadresse, defaut in liste_modeles_defaut :
        if categorie not in liste_categories_presentes :
            liste_donnees = [("categorie", categorie), ("nom", nom), ("description", description), ("objet", objet),
                             ("texte_xml", texte_xml), ("IDadresse", IDadresse), ("defaut", defaut)]
            IDmodele = DB.ReqInsert("modeles_emails", liste_donnees)
            nbre_ajouts += 1

    print("%d modeles d'Emails ajoutes" % nbre_ajouts)
    DB.Close()

def A9061():
    """ Modification de la table DOCUMENTS """
    try :
        DB = GestionDB.DB(suffixe="DOCUMENTS")
        DB.AjoutChamp("documents", "last_update", "VARCHAR(50)")
        DB.Close()
    except :
        pass

    # Ajoute l'horodatage dans chaque document
    try :
        DB = GestionDB.DB(suffixe="DOCUMENTS")
        req = "UPDATE documents SET last_update='%s';" % datetime.datetime.now()
        DB.ExecuterReq(req)
        DB.Commit()
        DB.Close()
    except :
        pass

def A9073():
    """ Cryptage des mots de passe utilisateurs """
    from Crypto.Hash import SHA256

    DB = GestionDB.DB()
    req = """SELECT IDutilisateur, mdp FROM utilisateurs;"""
    DB.ExecuterReq(req)
    liste_utilisateurs = DB.ResultatReq()
    liste_modifications = []
    for IDutilisateur, mdp in liste_utilisateurs :
        mdp_crypte = SHA256.new(mdp.encode('utf-8')).hexdigest()
        liste_modifications.append((mdp_crypte, IDutilisateur))

    # Enregistrement des mots de passe cryptés
    DB.Executermany("UPDATE utilisateurs SET mdp=? WHERE IDutilisateur=?", liste_modifications, commit=True)
    DB.Close()

def A9074():
    """ Cryptage des mots de passe utilisateurs dans nouveau champ mdpcrypt """
    from Crypto.Hash import SHA256

    DB = GestionDB.DB()
    req = """SELECT IDutilisateur, mdp FROM utilisateurs;"""
    DB.ExecuterReq(req)
    liste_utilisateurs = DB.ResultatReq()
    liste_modifications = []
    for IDutilisateur, mdp in liste_utilisateurs :
        if mdp != None and len(mdp) < 40 :
            mdp_crypte = SHA256.new(mdp.encode('utf-8')).hexdigest()
        else :
            mdp_crypte = mdp
        liste_modifications.append((mdp_crypte, IDutilisateur))

    # Enregistrement des mots de passe cryptés
    DB.Executermany("UPDATE utilisateurs SET mdpcrypt=? WHERE IDutilisateur=?", liste_modifications, commit=True)
    DB.Close()

def A9075():
    """ Suppression des mots de passe utilisateurs en clair """
    DB = GestionDB.DB()
    DB.Executermany("UPDATE utilisateurs SET mdp=NULL WHERE IDutilisateur<>?", [(9999999,),], commit=True)
    DB.Close()

def A9078():
    """ Suppression des consommations avec IDinscription null """
    DB = GestionDB.DB()
    DB.ExecuterReq("DELETE FROM consommations WHERE IDinscription IS NULL;")
    DB.Commit()
    DB.Close()

def A9079():
    """ Création de la table PHOTOS """
    from Data import DATA_Tables as Tables
    DB = GestionDB.DB(suffixe="PHOTOS", modeCreation=True)
    if DB.echec == 1:
        dlg = wx.MessageDialog(None, _(u"Erreur dans la création du fichier de photos.\n\nErreur : %s") % DB.erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False
    DB.CreationTables(Tables.DB_PHOTOS)
    DB.Close()

def A9080():
    """ Création de la table DOCUMENTS """
    from Data import DATA_Tables as Tables
    DB = GestionDB.DB(suffixe="DOCUMENTS", modeCreation=True)
    if DB.echec == 1:
        dlg = wx.MessageDialog(None, _(u"Erreur dans la création du fichier de documents.\n\nErreur : %s") % DB.erreur, _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False
    DB.CreationTables(Tables.DB_DOCUMENTS)
    DB.Close()

def A9081():
    """ Création du profil de configuration par défaut pour la liste des infos médicales """
    DB = GestionDB.DB()
    IDprofil = DB.ReqInsert("profils", [("label", u"Liste par défaut"), ("categorie", "impression_infos_medicales"), ("defaut", 1)])
    DB.ReqInsert("profils_parametres", [("IDprofil", IDprofil), ("nom", "colonnes"), ("type_donnee", "autre"), ("parametre", "[(u'Informations alimentaires', '2'), (u'Autres informations', '0')]")])
    DB.Close()

def A9102():
    """ Suppression des données personnelles """
    import random

    DB = GestionDB.DB()

    # Tables diverses
    DB.ExecuterReq("DELETE FROM messages;")
    DB.ExecuterReq("DELETE FROM problemes_sante;")
    DB.ExecuterReq("DELETE FROM memo_journee;")
    DB.ExecuterReq("UPDATE familles SET num_allocataire='', internet_actif=0, internet_identifiant='', internet_mdp='';")
    DB.ExecuterReq("UPDATE payeurs SET nom='XXX';")
    DB.ExecuterReq("UPDATE comptes_bancaires SET numero='XXX';")
    DB.ExecuterReq("DELETE FROM rappels;")
    DB.ExecuterReq("DELETE FROM historique;")
    DB.ExecuterReq("DELETE FROM adresses_mail;")
    DB.ExecuterReq("DELETE FROM sauvegardes_auto;")
    DB.ExecuterReq("DELETE FROM portail_actions;")
    DB.ExecuterReq("DELETE FROM portail_reservations;")
    DB.ExecuterReq("DELETE FROM portail_renseignements;")
    DB.ExecuterReq("DELETE FROM portail_messages;")

    # Modification des individus
    req = """SELECT IDindividu, nom, prenom FROM individus;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    liste_modifications = []
    for IDindividu, nom, prenom in listeDonnees :
        nom += u"AEIOU"
        prenom += u"aeiou"
        nom = ''.join(random.sample(nom, len(nom)))
        prenom = ''.join(random.sample(prenom, len(prenom))).capitalize()
        num_secu = None
        date_naiss = None
        rue_resid = "10 rue des oiseaux"
        cp_resid = "29200"
        ville_resid = "BREST"
        employeur = None
        travail_tel = "01.02.03.04.05."
        travail_mail = None
        tel_domicile = None
        tel_mobile = None
        mail = None

        liste_modifications.append((nom, prenom, num_secu, date_naiss, rue_resid, cp_resid, ville_resid, employeur, travail_tel, travail_mail, tel_domicile, tel_mobile, mail, IDindividu))

    DB.Executermany("UPDATE individus SET nom=?, prenom=?, num_secu=?, date_naiss=?, rue_resid=?, cp_resid=?, ville_resid=?, employeur=?, travail_tel=?, travail_mail=?, tel_domicile=?, tel_mobile=?, mail=? WHERE IDindividu=?", liste_modifications, commit=True)

    DB.Close()

    DB = GestionDB.DB(suffixe="PHOTOS")
    DB.ExecuterReq("DELETE FROM photos;")
    DB.Commit()
    DB.Close()

    DB = GestionDB.DB(suffixe="DOCUMENTS")
    DB.ExecuterReq("DELETE FROM documents;")
    DB.Commit()
    DB.Close()


def A9105():
    """ Remplissage du champ statut de la table inscriptions """
    DB = GestionDB.DB()
    DB.ExecuterReq("UPDATE inscriptions SET statut='ok';")
    DB.Commit()
    DB.Close()

def A9120():
    """ Effacement de toutes les actions du portail """
    DB = GestionDB.DB()
    DB.ExecuterReq("DELETE FROM portail_actions;")
    DB.ExecuterReq("DELETE FROM portail_reservations;")
    DB.ExecuterReq("DELETE FROM portail_renseignements;")
    DB.Commit()
    DB.Close()

def A9122():
    """ Réparation des prestations : Rapprochement des prestations et des consommations détachées """
    from Utils.UTILS_Decimal import FloatToDecimal
    from Utils.UTILS_Divers import DictionnaireImbrique
    DB = GestionDB.DB()

    # Importation des individus
    req = """SELECT IDindividu, nom, prenom FROM individus;"""
    DB.ExecuterReq(req)
    listeIndividus = DB.ResultatReq()
    dict_individus = {}
    for IDindividu, nom, prenom in listeIndividus:
        if prenom == None : prenom = ""
        dict_individus[IDindividu] = u"%s %s" % (nom, prenom)

    # Importation des prestations
    req = """SELECT IDprestation, IDindividu, date, label, IDtarif, montant, IDfacture
    FROM prestations
    WHERE IDtarif IS NOT NULL AND IDindividu IS NOT NULL AND IDindividu<>0;"""
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    dict_prestations = {}
    for IDprestation, IDindividu, date, label, IDtarif, montant, IDfacture in listePrestations:
        dict_prestations[IDprestation] = {"IDprestation": IDprestation, "label": label, "IDindividu": IDindividu, "date": date, "IDtarif": IDtarif, "montant": FloatToDecimal(montant), "IDfacture": IDfacture}

    # Importation des consommations
    req = """SELECT IDconso, IDindividu, IDprestation, date, consommations.IDunite, unites.nom 
    FROM consommations
    LEFT JOIN unites ON unites.IDunite = consommations.IDunite;"""
    DB.ExecuterReq(req)
    listeConsommations = DB.ResultatReq()
    dict_consos = {}
    dict_IDprestation_consos = {}
    dict_consos_regroupements = {}
    for IDconso, IDindividu, IDprestation, date, IDunite, nom_unite in listeConsommations:
        dict_consos[IDconso] = {"IDindividu": IDindividu, "IDprestation": IDprestation, "date": date, "IDunite": IDunite, "nom_unite": nom_unite}
        dict_IDprestation_consos[IDprestation] = None
        dict_consos_regroupements = DictionnaireImbrique(dictionnaire=dict_consos_regroupements, cles=[IDindividu, date, IDunite], valeur=IDconso)

    # Importation des tarifs et des unités de conso
    req = """SELECT IDcombi_tarif_unite, IDcombi_tarif, IDtarif, IDunite FROM combi_tarifs_unites;"""
    DB.ExecuterReq(req)
    listeConsommations = DB.ResultatReq()
    dict_unites_tarifs = {}
    for IDcombi_tarif_unite, IDcombi_tarif, IDtarif, IDunite in listeConsommations:
        if (IDtarif in dict_unites_tarifs) == False :
            dict_unites_tarifs[IDtarif] = {}
        if (IDcombi_tarif in dict_unites_tarifs[IDtarif]) == False :
            dict_unites_tarifs[IDtarif][IDcombi_tarif] = []
        dict_unites_tarifs[IDtarif][IDcombi_tarif].append(IDunite)

    # Recherche les consommations avec prestations disparues
    liste_consos_malades = []
    for IDconso, dict_conso in dict_consos.items():
        if dict_conso["IDprestation"] != None and (dict_conso["IDprestation"] in dict_prestations) == False:
            liste_consos_malades.append(dict_conso)

    print("liste_consos_malades=", len(liste_consos_malades))

    # Recherche les prestations sans consommations associées
    liste_prestations_sans_conso = []
    for IDprestation in list(dict_prestations.keys()):
        if (IDprestation in dict_IDprestation_consos) == False :
            liste_prestations_sans_conso.append(dict_prestations[IDprestation])

    print("liste_prestations_sans_conso=", len(liste_prestations_sans_conso))

    # Recherche les consommations qui pourraient associées à des prestations
    dict_rapprochements = {}
    liste_IDprestation_corrigees = []
    for dict_prestation in liste_prestations_sans_conso:
        if True:#dict_prestation["IDindividu"] == 157:

            IDprestation = dict_prestation["IDprestation"]
            IDtarif = dict_prestation["IDtarif"]
            IDindividu = dict_prestation["IDindividu"]
            date = dict_prestation["date"]

            # Recherche les combinaisons d'unités du tarif
            if IDtarif in dict_unites_tarifs:
                for IDcombi_tarif, combi_unites in dict_unites_tarifs.get(IDtarif, {}).items():
                    if len(combi_unites) > 0 :
                        combi_found = True
                        for IDunite in combi_unites :
                            if (date in dict_consos_regroupements[IDindividu]) == False or IDunite not in list(dict_consos_regroupements[IDindividu][date].keys()):
                                combi_found = False

                        # Si combi trouvée, on cherche les conso potentielles :
                        if combi_found == True :
                            for IDunite in combi_unites:
                                IDconso = dict_consos_regroupements[IDindividu][date][IDunite]

                                dict_rapprochements = DictionnaireImbrique(dictionnaire=dict_rapprochements, cles=[IDindividu, date, IDprestation], valeur=[])
                                dict_rapprochements[IDindividu][date][IDprestation].append(IDconso)
                                liste_IDprestation_corrigees.append(IDprestation)

    print("liste_IDprestation_corrigees =", len(liste_IDprestation_corrigees))

    # Réparation
    for IDindividu, dict_individu in dict_rapprochements.items():
        for date, dict_prestations_temp in dict_individu.items():
            for IDprestation, liste_consos in dict_prestations_temp.items():
                for IDconso in liste_consos:
                    DB.ReqMAJ("consommations", [("IDprestation", IDprestation), ], "IDconso", IDconso)

    DB.Close()

    # Message de fin
    dlg = wx.MessageDialog(None, _(u"Réparation terminée : %d prestations corrigées.") % len(liste_IDprestation_corrigees), _(u"Fin de la procédure"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()


def A9130():
    """ Remplissage du champ moteur de la table adresses_mail """
    DB = GestionDB.DB()
    DB.ExecuterReq("UPDATE adresses_mail SET moteur='smtp';")
    DB.Commit()
    DB.Close()




##def A8360():
##    """ Importation des familles d'un fichier local """
##    from Data import DATA_Tables as Tables
##    
##    # Recherche des fichiers importables
##    listeNomsFichiers = []
##    for fichier in os.listdir("Data/") :
##        if fichier.endswith("_DATA.dat") :
##            listeNomsFichiers.append(fichier[:-9])
##    listeNomsFichiers.sort() 
##    
##    # Demande le fichier à importer
##    dlg = wx.SingleChoiceDialog(None, _(u"Sélectionnez le fichier contenant les données à importer :"), _(u"Importation"), listeNomsFichiers)
##    dlg.SetSize((500, 400))
##    dlg.CenterOnScreen() 
##    nomExtension = None
##    if dlg.ShowModal() == wx.ID_OK :
##        nomFichier = dlg.GetStringSelection()
##        dlg.Destroy()
##    else :
##        dlg.Destroy()
##        return
##    
##    # Demande les options
##    listeOptions = [
##        ("abonnements", _(u"Listes de diffusion et abonnements")),
##        ("scolarite", _(u"Données de scolarité : étapes, écoles, classes...")),
##        ("questionnaire", _(u"Questionnaires familiaux et individuels")),
##        ("pieces", _(u"Pièces et types de pièces")),
##        ("messages", _(u"Messages de type famille, individuel ou accueil")),
##        ("quotients", _(u"Quotients familiaux des familles")),
##        ("mandats", _(u"Mandats SEPA des familles")),
##        ]
##        
##    dlg = wx.MultiChoiceDialog(None, _(u"Cochez les données optionnelles à inclure :"), _(u"Importation"), [x[1] for x in listeOptions])
##    if dlg.ShowModal() == wx.ID_OK :
##        selections = dlg.GetSelections()
##        options = [listeOptions[x][0] for x in selections]
##        dlg.Destroy()
##    else :
##        dlg.Destroy()
##        return
##
##    # Demande de confirmation
##    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer l'importation des familles du fichier '%s' ?\n\nAttention, toutes les données actuelles seront écrasées !") % nomFichier, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
##    if dlg.ShowModal() != wx.ID_YES :
##        dlg.Destroy()
##        return
##    dlg.Destroy()
##    
##    # Importation des tables
##    listeTables = [
##        "comptes_payeurs", "familles", "individus", "liens", 
##        "medecins", "payeurs", "categories_travail", "caisses", 
##        "rattachements", "regimes", "secteurs", "types_sieste", 
##        "problemes_sante", "types_maladies", "types_vaccins", "vaccins", "vaccins_maladies",
##        ]
##        
##    if "abonnements" in options : listeTables.extend(["abonnements", "listes_diffusion"])
##    if "scolarite" in options : listeTables.extend(["classes", "ecoles", "niveaux_scolaires", "scolarite"])
##    if "questionnaire" in options : listeTables.extend(["questionnaire_categories", "questionnaire_choix", "questionnaire_filtres", "questionnaire_questions", "questionnaire_reponses"])
##    if "pieces" in options : listeTables.extend(["pieces", "types_pieces"])
##    if "messages" in options : listeTables.extend(["messages", "messages_categories"])
##    if "quotients" in options : listeTables.extend(["quotients",])
##    if "mandats" in options : listeTables.extend(["mandats",])
##        
##    DB = GestionDB.DB() 
##    for nomTable in listeTables :
##        # Réinitialisation de la table
##        print "Reinitialisation de la table %s..." % nomTable
##        DB.ExecuterReq("DROP TABLE %s;" % nomTable)
##        DB.Commit() 
##        DB.CreationTable(nomTable, Tables.DB_DATA)
##        # Importation des données
##        print "Importation de la table %s..." % nomTable
##        DB.Importation_table(nomTable=nomTable, nomFichierdefault=u"Data/%s_DATA.dat" % nomFichier)
##    DB.Close()
##    print "Importation terminee."
    

if __name__ == u"__main__":
    app = wx.App(0)
    # TEST D'UNE PROCEDURE :
    E4072()
    app.MainLoop()
