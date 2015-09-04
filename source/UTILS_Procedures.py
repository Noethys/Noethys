#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import sys

import GestionDB



DICT_PROCEDURES = {
    "A3687" : _(u"Transformation des QF de tarifs_lignes unicode->float"),
    "A3688" : _(u"Suppression des ouvertures avec IDunite=5"),
    "X1234" : _(u"Exportation des donn�es d'une table dans la table DEFAUT"),
    "S1290" : _(u"Modification du IDcategorie_tarif"),
    "D1051" : _(u"Ajout du champ type dans la table Documents"),
    "E4072" : _(u"Suppression des prestations sans consommations associ�es"),
    "X0202" : _(u"Ajout de du champ forfait_date_debut � la table Prestations"),
    "G2345" : _(u"Attribution d'un ordre aux groupes"),
    "A4567" : _(u"Suppression de toutes les perspectives de la page d'accueil"),
    "A5000" : _(u"R�alisation d'une requ�te"),
    "A5134" : _(u"Ex�cution de l'ancienne version de l'�tat global des consommations"),
    "A5200" : _(u"Correction des arrondis"),
    "A5300" : _(u"Nettoyage des groupes d'activit�s"),
    "A5400" : _(u"R�paration de l'autoincrement sqlite de la table tarifs_lignes"),
    "A5500" : _(u"R�paration des liens prestations/factures"),
    "A7650" : _(u"Renseignement automatique du titulaire H�lios dans toutes les fiches familles"),
    "A8120" : _(u"Renseignement automatique du type comptable du mode de r�glement (banque ou caisse)"),
    "A8260" : _(u"Modification de la table Param�tres"),
    "A8452" : _(u"Nettoyage des liens superflus"),
    "A8574" : _(u"Mise � niveau de la base de donn�es"),
    "A8623" : _(u"Remplacement des exercices comptables par les dates budg�taires"),
    "A8733" : _(u"Correction des IDinscription disparus"),
    "A8823" : _(u"Cr�ation de tous les index"),
    "A8836" : _(u"Suppression des consommations avec prestation disparue"),
    }



# -------------------------------------------------------------------------------------------------------------------------

def Procedure(code=""):
    # Recherche si proc�dure existe
    if DICT_PROCEDURES.has_key(code) == False :
        dlg = wx.MessageDialog(None, _(u"D�sol�, cette proc�dure n'existe pas..."), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    titre = DICT_PROCEDURES[code]
    # Demande de confirmation de lancement
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer la proc�dure suivante ?\n\n   -> %s   ") % titre, _(u"Lancement de la proc�dure"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
    reponse = dlg.ShowModal() 
    dlg.Destroy()
    if reponse != wx.ID_YES :
        return
    # Lancement
    print "Lancement de la procedure '%s'..." % code
    try :
        exec("%s()" % code)
    except Exception, err :
        dlg = wx.MessageDialog(None, _(u"D�sol�, une erreur a �t� rencontr�e :\n\n-> %s  ") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return
    # Fin
    dlg = wx.MessageDialog(None, _(u"La proc�dure s'est termin�e avec succ�s."), _(u"Proc�dure termin�e"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    print "Fin de la procedure '%s'." % code
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
    V�rifie que le montant du QF dans la table tarifs_lignes est un float et non un unicode
    """
    DB = GestionDB.DB()
    req = """SELECT IDligne, qf_min, qf_max
    FROM tarifs_lignes; """ 
    DB.ExecuterReq(req)
    listeLignes = DB.ResultatReq()
    for IDligne, qf_min, qf_max in listeLignes :
        if type(qf_min) == unicode or type(qf_min) == str : DB.ReqMAJ("tarifs_lignes", [("qf_min", float(qf_min.replace(",","."))),], "IDligne", IDligne)
        if type(qf_max) == unicode or type(qf_max) == str : DB.ReqMAJ("tarifs_lignes", [("qf_max", float(qf_max.replace(",","."))),], "IDligne", IDligne)
    DB.Close()

def A3688():
    DB = GestionDB.DB()
    DB.ReqDEL("ouvertures", "IDunite", 5)
    DB.Close()

def X1234():
    """ Exportation des donn�es d'une table vers la table DEFAUT """
    # Demande le nom de la table � exporter
    DB = GestionDB.DB()
    listeTablesTemp = DB.GetListeTables() 
    listeTables = []
    for donnees in listeTablesTemp :
        listeTables.append(donnees[0])
    dlg = wx.MultiChoiceDialog(None, _(u"Cochez les tables � exporter :"), _(u"Exportation vers la table DEFAUT"), listeTables)
    if dlg.ShowModal() == wx.ID_OK :
        selections = dlg.GetSelections()
        nomsTable = [listeTables[x] for x in selections]
        for nomTable in nomsTable :
            DB.Exportation_vers_base_defaut(nomTable)
    dlg.Destroy()
    DB.Close()

def S1290():
    """
    R�cup�re le IDcategorie_tarif pour le mettre dans le nouveau champ 
    "categories_tarifs" de la table "tarifs"
    """
    DB = GestionDB.DB()
    
    # D�place le champ IDcategorie_tarif dans la table tarifs
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

        # Regroupement par activit�
        if dictDonnees.has_key(IDactivite) == False :
            dictDonnees[IDactivite] = {}
        
        # Regroupement par nom de tarif
        if dictDonnees[IDactivite].has_key(nom) == False :
            dictDonnees[IDactivite][nom] = []
        dictDonnees[IDactivite][nom].append(IDnom_tarif)
    
    # Regroupement par activit�s et noms de tarifs
    for IDactivite, dictNoms in dictDonnees.iteritems() :
        for nom, listeIDnom_tarif in dictNoms.iteritems() :
            # Conservation du premier IDnom_tarif
            newIDnom_tarif = listeIDnom_tarif[0]
            
            if len(listeIDnom_tarif) > 1 :
                for IDnom_tarif in listeIDnom_tarif[1:] :
                    # Suppression des IDnom_tarifs suivants
                    DB.ReqDEL("noms_tarifs", "IDnom_tarif", IDnom_tarif)
                    # R�-attribution du nouvel IDnom_tarif aux tarifs
                    DB.ReqMAJ("tarifs", [("IDnom_tarif", newIDnom_tarif),], "IDnom_tarif", IDnom_tarif)
    
    DB.Close()

def D1051():
    """ Cr�ation du champ TYPE dans la table DOCUMENTS """
    DB = GestionDB.DB(suffixe="DOCUMENTS") 
    DB.AjoutChamp("documents", "type", "VARCHAR(50)")
    DB.AjoutChamp("documents", "label", "VARCHAR(400)")
    DB.AjoutChamp("documents", "IDreponse", "INTEGER")
    DB.Close()
    
def E4072():
    """ Suppression des prestations sans consommations associ�es """    
    print "Lancement de la procedure E4072..."
    DB = GestionDB.DB()
    
    # R�cup�ration des prestations
    req = """SELECT IDprestation, label FROM prestations;""" 
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq()
    
    # R�cup�ration des consommations
    req = """SELECT IDconso, IDprestation FROM consommations;""" 
    DB.ExecuterReq(req)
    listeConsommations = DB.ResultatReq()
    DB.Close()
    
    # Analyse
    dictPrestations = {}
    for IDconso, IDprestation in listeConsommations :
        if dictPrestations.has_key(IDprestation) == False :
            dictPrestations[IDprestation] = []
        dictPrestations[IDprestation].append(IDconso)
    
    dictResultats = {}
    for IDprestation, label in listePrestations :
        if dictPrestations.has_key(IDprestation) == False :
            if dictResultats.has_key(label) == False :
                dictResultats[label] = []
            dictResultats[label].append(IDprestation)
    
    listeDonnees = []
    for label, listePrestationsTemp in dictResultats.iteritems() :
        texte = _(u"%s (%d prestations)") % (label, len(listePrestationsTemp))
        listeDonnees.append((texte, label, listePrestationsTemp))
    listeDonnees.sort() 
    
    listeLabels = []
    for texte, label, listePrestationsTemp in listeDonnees :
        listeLabels.append(texte)
    
    message = _(u"Cochez les prestations sans consommations associ�es que vous souhaitez supprimer.\n(Pensez � sauvegarder votre fichier avant d'effectuer cette proc�dure !)")
    dlg = wx.MultiChoiceDialog(None, message, _(u"Suppression des prestations sans consommations associ�es"), listeLabels)
    dlg.SetSize((450, 500))
    dlg.CenterOnScreen() 
    if dlg.ShowModal() == wx.ID_OK:
        import wx.lib.agw.pybusyinfo as PBI
        message = _(u"Veuillez patienter durant la proc�dure...")
        dlgAttente = PBI.PyBusyInfo(message, parent=None, title=_(u"Proc�dure"), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
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
    print "Fin de la procedure E4072."
    
def X0202():
    """ Ajout du champ forfait_date_debut � la table Prestations """
    DB = GestionDB.DB() 
    DB.AjoutChamp("prestations", "forfait_date_debut", "VARCHAR(10)")
    DB.Close()
    
def G2345():
    """ Attribution d'un ordre aux groupes """
    DB = GestionDB.DB() 
    # R�cup�ration des groupes
    req = """SELECT IDgroupe, IDactivite FROM groupes ORDER BY IDactivite, IDgroupe;""" 
    DB.ExecuterReq(req)
    listeGroupes = DB.ResultatReq()
    dictGroupes = {}
    for IDgroupe, IDactivite in listeGroupes :
        if dictGroupes.has_key(IDactivite) == False :
            dictGroupes[IDactivite] = []
        dictGroupes[IDactivite].append(IDgroupe)
    # Attribution d'un num�ro d'ordre
    for IDactivite, listeGroupes in dictGroupes.iteritems() :
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
    """ Requete sur base de donn�es active """
    # Demande la requ�te souhait�e
    dlg = wx.TextEntryDialog(None, _(u"Saisissez la requ�te :"), _(u"Requ�te"), "")
    if dlg.ShowModal() == wx.ID_OK:
        req = dlg.GetValue()
        dlg.Destroy()
    else :
        dlg.Destroy()
        return
    # R�alisation de la requ�te
    try :
        DB = GestionDB.DB()
        DB.ExecuterReq(req)
        DB.Commit()
        DB.Close()
    except Exception, err:
        print "Erreur dans procedure A5000 :", err

def A5134():
    """ Ancienne fonction Etat global des conso """
    import DLG_Etat_global_archives
    dlg = DLG_Etat_global_archives.Dialog(None)
    dlg.ShowModal() 
    dlg.Destroy()

def A5200():
    """ Arrondi de toutes les prestations et ventilations de la base de donn�es !!! """
    import wx.lib.agw.pybusyinfo as PBI
    from UTILS_Decimal import FloatToDecimal as FloatToDecimal
    DB = GestionDB.DB() 

    dlgAttente = PBI.PyBusyInfo(_(u"Veuillez patienter durant la proc�dure... Celle-ci peut n�cessiter quelques minutes..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
    wx.Yield() 

    # R�cup�re les prestations
    req = """SELECT IDprestation, montant FROM prestations;"""
    DB.ExecuterReq(req)
    listePrestations = DB.ResultatReq() 
    
    # R�cup�re la ventilation
    req = """SELECT IDventilation, montant FROM ventilation;"""
    DB.ExecuterReq(req)
    listeVentilations = DB.ResultatReq() 

    # Modification des arrondis
    total = len(listePrestations) + len(listeVentilations)
    index = 0
    
    for IDprestation, montant in listePrestations :
        EcritStatusbar(_(u"Correction des arrondis... Merci de patienter...             -> %d %% effectu�s") % (index * 100 / total))
        DB.ReqMAJ("prestations", [("montant", FloatToDecimal(montant, plusProche=True)),], "IDprestation", IDprestation)
        index += 1
    
    for IDventilation, montant in listeVentilations :
        EcritStatusbar(_(u"Correction des arrondis... Merci de patienter...             - > %d %% effectu�s") % (index * 100 / total))
        DB.ReqMAJ("ventilation", [("montant", FloatToDecimal(montant, plusProche=True)),], "IDventilation", IDventilation)
        index += 1
        
    DB.Close()
    EcritStatusbar(u"")
    del dlgAttente

def A5300():
    """ Nettoyage des groupes d'activit�s en double """
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
    """ R�paration de l'autoincrement sqlite de la table tarifs_lignes """
    nomTable = "tarifs_lignes"
    DB = GestionDB.DB() 
    if DB.isNetwork == False :
        # Recherche si des enregistrements existent dans la table tarifs_lignes
        req = """SELECT * FROM %s;""" % nomTable
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        if len(listeTemp) > 0 :
            # Recherche si la table est pr�sente dans la table sqlite_seq
            req = """SELECT name, seq
            FROM sqlite_sequence
            WHERE name='%s';""" % nomTable
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()    
            if len(listeDonnees) == 0 :
                # Si aucune r�f�rence dans la table sqlite_sequence, on r�pare la table
                DB.ReparationTable(nomTable)
    DB.Close()
    
    
def A5500():
    """ R�paration des liens prestations/factures """
    import UTILS_Dates
    import time
    import DLG_Selection_dates
    
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
        if dictFactures.has_key(IDcompte_payeur) == False :
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
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer cette proc�dure pour %d prestations ?\n\n(Vous pourrez suivre la progression dans la barre d'�tat)") % nbrePrestations, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
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
        if dictFactures.has_key(IDcompte_payeur) :
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
    dlg = wx.MessageDialog(None, _(u"Proc�dure termin�e !\n\n%d prestations sur %s ont �t� rattach�es avec succ�s !") % (nbreSucces, nbrePrestations), _(u"Fin"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    
    
def A7650():
    """ Renseignement automatique du titulaire H�lios dans toutes les fiches familles """
    # Recherche des titulaires potentiels pour chaque famille (les p�res en priorit�)
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
        if dictIndividus.has_key(IDfamille) == False :
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
            if dictIndividus.has_key(IDfamille) :
                dictIndividu = dictIndividus[IDfamille][0]
                titulaire_helios = dictIndividu["IDindividu"]
                listeModifications.append((titulaire_helios, IDfamille))
    
    print "Nbre de titulaires HELIOS a enregistrer : %d" % len(listeModifications)
        
    # Enregistrement des modifications
    DB = GestionDB.DB() 
    DB.Executermany("UPDATE familles SET titulaire_helios=? WHERE IDfamille=?", listeModifications, commit=False)
    DB.Commit() 
    DB.Close()


def A8120():
    """ Renseignement automatique du type comptable du mode de r�glement (banque ou caisse) """
    DB = GestionDB.DB() 
    DB.ExecuterReq("UPDATE modes_reglements SET type_comptable='caisse' WHERE IDmode=1")
    DB.ExecuterReq("UPDATE modes_reglements SET type_comptable='banque' WHERE IDmode<>1")
    DB.Commit() 
    DB.Close()

def A8260():
    """ Modification de la table Param�tres sur les fichiers r�seau """
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
        if dictLiens.has_key(IDfamille) == False :
            dictLiens[IDfamille] = {}
        if dictLiens[IDfamille].has_key(key) == False :
            dictLiens[IDfamille][key] = []
        dictLiens[IDfamille][key].append(IDlien)
        dictLiens[IDfamille][key].sort() 
    # Analyse
    listeLiensASupprimer = []
    listeIDfamille = []
    for IDfamille, dictKeys in dictLiens.iteritems() :
        for key, listeIDlien in dictKeys.iteritems() :
            if len(listeIDlien) > 1 :
                # Suppression des liens obsol�tes
                for IDlien in listeIDlien[1:] :
                    DB.ReqDEL("liens", "IDlien", IDlien)
                    listeLiensASupprimer.append(IDlien)
                if IDfamille not in listeIDfamille :
                    listeIDfamille.append(IDfamille)
    DB.Close() 
    print "Nbre de liens supprimes :", len(listeLiensASupprimer)
    print listeIDfamille
    
def A8574():
    """ Mise � niveau de la base de donn�es """
    import FonctionsPerso
    versionApplication = FonctionsPerso.GetVersionLogiciel()
    dlg = wx.TextEntryDialog(None, _(u"Saisissez le num�ro de version � partir duquel vous souhaitez \neffectuer la mise � niveau ('x.x.x.x'):"), _(u"Mise � niveau de la base de donn�es"), versionApplication)
    reponse = dlg.ShowModal() 
    version = dlg.GetValue()
    dlg.Destroy()
    if reponse != wx.ID_OK:
        return
    
    valide = True
    try :
        version = [int(x) for x in version.split(".")]
    except :
        valide = False
    if len(version) != 4 :
        valide = False
    
    if valide == False :
        dlg = wx.MessageDialog(None, _(u"Impossible d'effectuer la proc�dure !\n\nLe num�ro de version que vous avez saisi semble erron�. V�rifiez qu'il est format� de la fa�on suivante : 'x.x.x.x'"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False
    
    print "Procedure manuelle de mise a niveau de la base de donnee depuis la version : ", version
    DB = GestionDB.DB()        
    resultat = DB.ConversionDB(version)
    DB.Close()
    print resultat
    
def A8623():
    """ Remplacement des exercices comptables par les dates budg�taires """
    DB = GestionDB.DB()
    
    # Remplacement dans la ventilation des op�rations de tr�sorerie
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
    
    # R�cup�ration des tous les IDinscription
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
    print "%d IDinscription NULL sont a corriger..." % len(listeDonnees)
    
    listeModifications = []
    for IDconso, IDindividu, IDactivite, IDcompte_payeur in listeDonnees :
        if dictInscriptions.has_key((IDindividu, IDactivite, IDcompte_payeur)) :
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
    """ Suppression des consommations dont la prestation a �t� supprim�e """
    # Recherche
    DB = GestionDB.DB()
    req = """SELECT IDconso, consommations.IDindividu, IDinscription, consommations.date, IDunite, consommations.IDprestation, prestations.IDprestation, consommations.etat FROM consommations
    LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
    WHERE consommations.IDprestation IS NOT NULL AND prestations.IDprestation IS NULL AND etat='reservation'
    ORDER BY consommations.IDindividu, IDunite;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    print "Nbre consommations avec prestations supprim�es : ", len(listeDonnees)
    listeConso = []
    for listeTemp in listeDonnees :
        listeConso.append(listeTemp[0])
    # Suppression
    DB = GestionDB.DB()
    for IDconso in listeConso :
        DB.ReqDEL("consommations", "IDconso", IDconso)
    DB.Close()
    

##def A8360():
##    """ Importation des familles d'un fichier local """
##    import DATA_Tables as Tables
##    
##    # Recherche des fichiers importables
##    listeNomsFichiers = []
##    for fichier in os.listdir("Data/") :
##        if fichier.endswith("_DATA.dat") :
##            listeNomsFichiers.append(fichier[:-9])
##    listeNomsFichiers.sort() 
##    
##    # Demande le fichier � importer
##    dlg = wx.SingleChoiceDialog(None, _(u"S�lectionnez le fichier contenant les donn�es � importer :"), _(u"Importation"), listeNomsFichiers)
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
##        ("scolarite", _(u"Donn�es de scolarit� : �tapes, �coles, classes...")),
##        ("questionnaire", _(u"Questionnaires familiaux et individuels")),
##        ("pieces", _(u"Pi�ces et types de pi�ces")),
##        ("messages", _(u"Messages de type famille, individuel ou accueil")),
##        ("quotients", _(u"Quotients familiaux des familles")),
##        ("mandats", _(u"Mandats SEPA des familles")),
##        ]
##        
##    dlg = wx.MultiChoiceDialog(None, _(u"Cochez les donn�es optionnelles � inclure :"), _(u"Importation"), [x[1] for x in listeOptions])
##    if dlg.ShowModal() == wx.ID_OK :
##        selections = dlg.GetSelections()
##        options = [listeOptions[x][0] for x in selections]
##        dlg.Destroy()
##    else :
##        dlg.Destroy()
##        return
##
##    # Demande de confirmation
##    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment lancer l'importation des familles du fichier '%s' ?\n\nAttention, toutes les donn�es actuelles seront �cras�es !") % nomFichier, _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
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
##        # R�initialisation de la table
##        print "Reinitialisation de la table %s..." % nomTable
##        DB.ExecuterReq("DROP TABLE %s;" % nomTable)
##        DB.Commit() 
##        DB.CreationTable(nomTable, Tables.DB_DATA)
##        # Importation des donn�es
##        print "Importation de la table %s..." % nomTable
##        DB.Importation_table(nomTable=nomTable, nomFichierdefault=u"Data/%s_DATA.dat" % nomFichier)
##    DB.Close()
##    print "Importation terminee."
    

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    # TEST D'UNE PROCEDURE :
    A8836()
    app.MainLoop()
