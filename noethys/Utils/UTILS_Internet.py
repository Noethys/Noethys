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
from UTILS_Traduction import _
import GestionDB

import UTILS_CryptageMD5
import random
import urllib
import datetime
import string
import ftplib

try: import psyco; psyco.full()
except: pass


def DateEngEnDateDD(dateEng):
    """ Tranforme une date anglaise en datetime.date """
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
    
def DateDDEnDateFR(dateDD):
    """ Transforme une datetime.date en date complète FR """
    listeJours = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche")
    listeMois = (_(u"janvier"), _(u"février"), _(u"mars"), _(u"avril"), _(u"mai"), _(u"juin"), _(u"juillet"), _(u"août"), _(u"septembre"), _(u"octobre"), _(u"novembre"), _(u"décembre"))
    return listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)




def CreationIdentifiant(IDfamille=0, nbreCaract=7):
    """ Création d'un identifiant aléatoire """
    identifiant = ""
    numTmp = ""
    for x in range(0, nbreCaract-4) :
        numTmp += random.choice("123456789")
    coeff = "0" * 4
    identifiant = numTmp + coeff
    identifiant = str(int(identifiant) + IDfamille)
    return identifiant

def CreationMDP(nbreCaract=5):
    """ Création d'un mot de passe aléatoire """
    mdp = ""
    for x in range(0, nbreCaract) :
        mdp += random.choice("bcdfghjkmnprstvwxzBCDFGHJKLMNPRSTVWXZ123456789")
    return mdp

def CrypteMDP(motdepasse=""):
    """ Crypte un mot de passe donné """
    mdpCrypte = UTILS_CryptageMD5.unix_md5_crypt(motdepasse, 'ab')
    return mdpCrypte


def InitIdentifiantsFiches():
    """ Remplit tous les champs identifiant et mdp de toutes les fiches familles """
    DB = GestionDB.DB()        
    req = """SELECT IDfamille, nom, prenom FROM familles ORDER BY nom, prenom; """
    DB.executerReq(req)
    listeDonnees = DB.resultatReq()
    DB.close()
    
    DB = GestionDB.DB()
    for IDfamille, nom, prenom in listeDonnees :
        identifiant = CreationIdentifiant(IDfamille)
        mdp = CreationMDP()      
    
        listeDonnees = [ ("internet_identifiant",   identifiant),  
                                    ("internet_mdp",    mdp),
                                    ("internet_actif",    1),
                                     ]
        
        # Modification de l'identité de l'ENFANT
        DB.ReqMAJ("familles", listeDonnees, "IDfamille", IDfamille)
    
    DB.commit()
    DB.close()


def UploadCalendrier():
    """ Créé et upload le calendrier des périodes internet """
    listePeriodes = []
    
    # Récupération des noms de périodes
    dict_periodes = GestionDB.DICT_PERIODES
    
    # Récupération des dates de périodes
    DB = GestionDB.DB()      
    req = """SELECT IDperiode, annee, date FROM dates ORDER BY date; """
    DB.executerReq(req)
    listeDatesTmp = DB.resultatReq()
    DB.close()
    dictDates = {}
    for IDperiode, annee, date in listeDatesTmp :
        key = (IDperiode, annee)
        if dictDates.has_key(key):
            dictDates[key].append(date)
        else:
            dictDates[key] = [date,]
    
    # Récupération des périodes_internet
    req = """SELECT IDperiode_internet, IDperiode, annee, debut_inscription, fin_inscription, synchro FROM periodes_internet ORDER BY debut_inscription; """
    DB = GestionDB.DB()        
    DB.executerReq(req)
    listePeriodesTmp = DB.resultatReq()
    DB.close()
    
    for IDperiode_internet, IDperiode, annee, debut_inscription, fin_inscription, synchro in listePeriodesTmp :
        nomPeriode = dict_periodes[IDperiode] + " " + str(annee)
        listeDates = dictDates[(IDperiode, annee)]
        txtDates = ""
        for date in listeDates :
            txtDates += date + ";"
        if len(listeDates) > 0:
            txtDates = txtDates[:-1]
            
        txt = "%d:%s:%s;%s:%s\n" % (IDperiode_internet, nomPeriode, debut_inscription, fin_inscription, txtDates)
        
        listePeriodes.append(txt)
    
    # Création du fichier texte
    texteFichier = ""
    for txtPeriode in listePeriodes :
        texteFichier += txtPeriode
        
    # Création du fichier texte
    f = open("temp\calendrier.txt", "w")
    f.write(texteFichier.encode("iso-8859-15"))
    f.close()
    
    # Mise en ligne du fichier texte
    ftp = ftplib.FTP("ICI_FTP", "ICI_LOGIN", "ICI_MOT_DE_PASSE")
    ftp.cwd("www/ICI_REPERTOIRE_WEB")
    fichier = open("temp\calendrier.txt", "rb")
    ftp.storbinary("STOR calendrier.txt", fichier)
    fichier.close()
    ftp.quit()

    nbrePeriodes = len(listePeriodes)
    
    etat = _(u"> %d périodes mises en ligne") % nbrePeriodes
    return etat
    
    
    

def ImporteFichierReservations():
    """ Récupère le contenu du fichier présences sur Internet """
    
    # Récupère le fichier en ligne
    f = urllib.urlopen('http://xxx/presences.txt')
    txtPresences = f.readlines()
    f.close()
    
    if len(txtPresences) < 2 :
        etat =  _(u"> Aucune présence a télécharger.")
        return etat
    
    listeReservations = []
    nbreReservations = 0
    nbreEnregistrements = 0
    
    # Analyse chaque ligne
    for ligne in txtPresences :
        if len(ligne) > 2 :
            combo = string.split(ligne, ":")
            
            # IDenfant
            IDenfant = int(combo[0])
            
            # IDperiode_internet
            IDperiode_internet = int(combo[1])
            
            # Date et heure de la saisie
            txtDateHeure = combo[2]
            comboDH = string.split(txtDateHeure, "-")
            dateHeure = datetime.datetime(int(comboDH[0]), int(comboDH[1]), int(comboDH[2]), int(comboDH[3]), int(comboDH[4]), int(comboDH[5]))
            
            # Les présences
            txtPresences = combo[3]
            dictPresences = {}
            if txtPresences[-1] == "\n" : txtPresences = txtPresences[:-1]
            comboPresences = string.split(txtPresences, ";")
            for presence in comboPresences :
                if presence[0] == "-" : 
                    # Pas de présence
                    break
                date = DateEngEnDateDD(presence[:10])
                typePresence = presence[10:]
                dictPresences[date] = typePresence
            
            # Met toutes les données recueillies dans une liste
            listeReservations.append( [IDenfant, IDperiode_internet, txtDateHeure, txtPresences, dictPresences] )
            nbreReservations += 1

    
    # Récupère les IDfamille de chaque enfant
    DB = GestionDB.DB()        
    req = """SELECT IDenfant, IDfamille FROM enfants; """
    DB.executerReq(req)
    listeDonnees = DB.resultatReq()
    DB.close()
    listeEnfants = {}
    for IDenfant, IDfamille in listeDonnees :
        listeEnfants[IDenfant] = IDfamille
    
    # Enregistre les données dans la table 'reservations_internet'
    DB = GestionDB.DB()
    for IDenfant, IDperiode_internet, txtDateHeure, txtPresences, dictPresences in listeReservations :
        IDfamille = listeEnfants[IDenfant]
        
        # Recherche si la réservation est déjà présente dans la table reservations
        req = """
        SELECT IDreservation FROM reservations_internet 
        WHERE IDenfant=%d AND date_heure='%s'; 
        """ % (IDenfant, txtDateHeure)
        DB.executerReq(req)
        listeDonnees = DB.resultatReq()
        
        # Si pas présente, ajoute la réservation dans la table
        if len(listeDonnees) == 0 :
            
            # Enregistrement de la réservation
            listeDonnees = [ ("IDfamille",   IDfamille),  
                                        ("IDenfant",    IDenfant),
                                        ("date_heure",    txtDateHeure), 
                                        ("IDperiode_internet",    IDperiode_internet), 
                                         ]
            DB = GestionDB.DB()     
            IDreservation = DB.ReqInsert("reservations_internet", listeDonnees)
            nbreEnregistrements += 1
            
            # Enregistrement des présences de la réservation
            for date, type_presence in dictPresences.iteritems() : 
                listeDonnees = [ ("IDreservation",   IDreservation),  
                                            ("IDfamille",   IDfamille),  
                                            ("date",    date),
                                            ("type_presence",    type_presence), 
                                             ]
                DB = GestionDB.DB()     
                IDpresence = DB.ReqInsert("presences_internet", listeDonnees)
    
    # Clôture de la base
    DB.commit()
    DB.close()
    
    etat = _(u"> %d réservations trouvées / %d réservations enregistrées dans la base") % (nbreReservations, nbreEnregistrements)
    return etat


def UploadFichierIdentites():
    """ Créé le fichier des identités """
    
    dictCotisations = GetInfosCotisations()
    dictPieces = GetInfosPieces()
    dictTypesPieces = GestionDB.DICT_PIECES
    
    listeIdentites = []
    
    # Récupère les données enfants
    DB = GestionDB.DB()        
    req = """SELECT IDenfant, IDfamille, prenom FROM enfants; """
    DB.executerReq(req)
    listeEnfants = DB.resultatReq()
    DB.close()
    dictEnfants = {}
    for IDenfant, IDfamille, prenom in listeEnfants :
        if dictEnfants.has_key(IDfamille) :
            dictEnfants[IDfamille].append( (IDenfant, prenom) )
        else:
            dictEnfants[IDfamille] = [ (IDenfant, prenom), ]
    
    # Récupère les données familles
    DB = GestionDB.DB()        
    req = """SELECT IDfamille, internet_identifiant, internet_mdp FROM familles WHERE internet_actif=1; """
    DB.executerReq(req)
    listeFamilles = DB.resultatReq()
    DB.close()

    # Création des lignes de données
    for IDfamille, internet_identifiant, internet_mdp in listeFamilles :
        txtIdentite = ""
        
        identifiant = internet_identifiant
        mdpCrypte = CrypteMDP(internet_mdp)
        
        # Enfants
        txtEnfants = ""
        if dictEnfants.has_key(IDfamille) :
            for IDenfant, prenom in dictEnfants[IDfamille] :
                txtEnfants += u"%05d%s;" % (IDenfant, prenom.decode("iso-8859-15"))
            if len(txtEnfants) > 0 : txtEnfants = txtEnfants[:-1]
        
        # Pieces
        txtPieces = ""
        listePieces = GetPiecesAFournir(dictPieces, dictCotisations, dictTypesPieces, dictEnfants, IDfamille)
        for piece in listePieces :
            txtPieces += piece + ";"
        if len(txtPieces)>0 : txtPieces = txtPieces[:-1]
        
        txtIdentite = u"%s:%s:%s:%s\n" % (identifiant, mdpCrypte, txtEnfants, txtPieces)
        
        listeIdentites.append(txtIdentite)
        
    # Création du fichier texte
    texteFichier = ""
    for txtIdentite in listeIdentites :
        texteFichier += txtIdentite
        
    # Création du fichier texte
    f = open("temp\identites.txt", "w")
    f.write(texteFichier.encode("iso-8859-15"))
    f.close()
    
    # Mise en ligne du fichier texte
    ftp = ftplib.FTP("ICI_FTP", "ICI_LOGIN", "ICI_MOT_DE_PASSE")
    ftp.cwd("www/ICI_REPERTOIRE_WEB")
    fichier = open("temp\identites.txt", "rb")
    ftp.storbinary("STOR identites.txt", fichier)
    fichier.close()
    ftp.quit()

    nbreIdentites = len(listeIdentites)
    
    etat =  _(u"> %d identités mises en ligne") % nbreIdentites
    return etat
    
def GetInfosPieces():
    dictPieces = {}
    DB = GestionDB.DB()        
    req = """SELECT IDpiece, IDfamille, IDenfant, IDtype, date_debut, date_fin FROM pieces; """
    DB.executerReq(req)
    listeDonnees = DB.resultatReq()
    DB.close()
    dictio = {}
    for IDpiece, IDfamille, IDenfant, IDtype, date_debut, date_fin in listeDonnees:
        if dictPieces.has_key(IDfamille) :
            dictPieces[IDfamille].append( (IDpiece, IDenfant, IDtype, date_debut, date_fin) )
        else :
            dictPieces[IDfamille] = [ (IDpiece, IDenfant, IDtype, date_debut, date_fin), ]
    return dictPieces
    
def GetInfosCotisations():
    dictCotisations = {}
    DB = GestionDB.DB()        
    req = """SELECT IDcotisation, IDfamille, date_debut, date_fin FROM cotisations; """
    DB.executerReq(req)
    listeDonnees = DB.resultatReq()
    DB.close()
    dictio = {}
    for IDcotisation, IDfamille, date_debut, date_fin in listeDonnees:
        if dictCotisations.has_key(IDfamille) :
            dictCotisations[IDfamille].append( (IDcotisation, date_debut, date_fin) )
        else:
            dictCotisations[IDfamille] = [ (IDcotisation, date_debut, date_fin), ]
    return dictCotisations
        
def GetPiecesAFournir(dictPieces, dictCotisations, dictTypesPieces, dictEnfants, IDfamille):
        if dictPieces.has_key(IDfamille) :
            listePiecesFournies = dictPieces[IDfamille]
        else:
            listePiecesFournies = []
        if dictCotisations.has_key(IDfamille) :
            listeCotisationsFournies = dictCotisations[IDfamille]
        else :
            listeCotisationsFournies = []
    
        # Creation de la liste des pièces à fournir
        datedujour = datetime.date.today()
        listeDonnees = []
        index = 1
        for key, valeurs in dictTypesPieces.iteritems():
            IDtypePiece = key
            nomTypePiece = valeurs[0]
            attribution = valeurs[1]
            
            if attribution == "famille" and nomTypePiece == _(u"Cotisation annuelle") :
                etat = "pasok"
                # Recherche d'une cotisation valide
                for IDcotisation, date_debut, date_fin in listeCotisationsFournies :
                    # Vérifie si la pièce est valide :
                    if date_debut <= str(datedujour) <= date_fin : 
                        etat = "ok"
                labelPiece = nomTypePiece + " " + str(datedujour.year)
                IDenfant = 0
                if etat == "pasok" :
                    listeDonnees.append( "%d0" % IDtypePiece )
                
            if attribution == "famille" and nomTypePiece != _(u"Cotisation annuelle") :
                etat = "pasok"
                # Recherche d'une pièce de type famille
                for IDpiece, IDenfant, IDtype, date_debut, date_fin in listePiecesFournies :
                    if IDtype == IDtypePiece : 
                        # Vérifie si la pièce est valide :
                        if date_debut <= str(datedujour) <= date_fin : 
                            etat = "ok"
                labelPiece = nomTypePiece
                IDenfant = 0
                if etat == "pasok" :
                    listeDonnees.append( "%d0" % IDtypePiece )
        
            if attribution == "enfant" :
                if dictEnfants.has_key(IDfamille) :
                    for IDenfant, prenom in dictEnfants[IDfamille] :
                        etat = "pasok"
                        # Recherche d'une pièce de type enfant
                        for IDpiece, IDenfant2, IDtype, date_debut, date_fin in listePiecesFournies :
                            if IDtype == IDtypePiece and IDenfant2 == IDenfant : 
                                # Vérifie si la pièce est valide :
                                if date_debut <= str(datedujour) <= date_fin : 
                                    etat = "ok"
                        labelPiece = nomTypePiece + " de " + prenom.decode("iso-8859-15")
                        if etat == "pasok" :
                            listeDonnees.append( "%d%d" % (IDtypePiece, IDenfant) ) 
    
        return listeDonnees





    