#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import datetime
import string
from xml.dom.minidom import Document

import wx
import UTILS_Utilisateurs



def DemanderChoix(parent):
    """ Propose le choix entre ROLMRE et PES V2 ORMC """
    import DLG_Choix
    titre = u"Quel protocole d'échanges souhaitez-vous utiliser ?"
    intro = u"Cliquez sur le protocole d'échange souhaité afin d'accéder à la fonctionnalité dédiée..."
    listeBoutons = [
        (u"Bordereau PES Recette ORMC", u"Nouveau type de bordereau Recette ORMC (Ordre de Recette Multi Créanciers) fidèle au nouveau protocole d'échange PES V2 entre les collectivités locales et la DGFIP. Remplace le protocole ROLMRE à partir du 01/02/2014."),
        (u"Rôle ROLMRE", u"Le protocole ROLMRE est une procédure d'échanges de données utilisée dans les collectivités qui devient obsolète à partir du 01/02/2014. Au delà de cette date, il faut utiliser le bordereau PES ORMC."),
        ]
    dlg = DLG_Choix.Dialog(parent, listeBoutons=listeBoutons, intro=intro, titre=titre)
    reponse = dlg.ShowModal() 
    dlg.Destroy()
    if reponse == wx.ID_CANCEL : return False
    if reponse == 0 : return "pes"
    if reponse == 1 : return "rolmre"

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def GetXML(dictDonnees={}):
    """ Génération du fichier PES Recette ORMC """
    doc = Document()

    # Génération du document XML
    racine = doc.createElement("n:PES_Aller")
    racine.setAttribute("xsi:schemaLocation", "http://www.minefi.gouv.fr/cp/helios/pes_v2/recette/r0/aller")
    racine.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    racine.setAttribute("xmlns:xenc", "http://www.w3.org/2001/04/xmlenc#")
    racine.setAttribute("xmlns:xad", "http://uri.etsi.org/01903/v1.1.1#")
    racine.setAttribute("xmlns:reca", "http://www.minefi.gouv.fr/cp/helios/pes_v2/recette/r0/aller")
    racine.setAttribute("xmlns:n", "http://www.minefi.gouv.fr/cp/helios/pes_v2/Rev0/aller")
    racine.setAttribute("xmlns:cm", "http://www.minefi.gouv.fr/cp/helios/pes_v2/commun")
    racine.setAttribute("xmlns:acta", "http://www.minefi.gouv.fr/cp/helios/pes_v2/etatactif/r0/aller")
    doc.appendChild(racine)
        
    # Enveloppe
    Enveloppe = doc.createElement("Enveloppe")
    racine.appendChild(Enveloppe)
    
    Parametres = doc.createElement("Parametres")
    Enveloppe.appendChild(Parametres)
    
    Version = doc.createElement("Version")
    Version.setAttribute("V", "2")
    Parametres.appendChild(Version)

    TypFic = doc.createElement("TypFic")
    TypFic.setAttribute("V", "PESORMC")
    Parametres.appendChild(TypFic)

    NomFic = doc.createElement("NomFic")
    NomFic.setAttribute("V", dictDonnees["nom_fichier"])
    Parametres.appendChild(NomFic)

    Emetteur = doc.createElement("Emetteur")
    Enveloppe.appendChild(Emetteur)

    Sigle = doc.createElement("Sigle")
    Sigle.setAttribute("V", "NOETHYS")
    Emetteur.appendChild(Sigle)

    # EnTetePES
    EnTetePES = doc.createElement("EnTetePES")
    racine.appendChild(EnTetePES)

    DteStr = doc.createElement("DteStr")
    DteStr.setAttribute("V", dictDonnees["date_emission"])
    EnTetePES.appendChild(DteStr)

    IdPost = doc.createElement("IdPost")
    IdPost.setAttribute("V", dictDonnees["id_poste"])
    EnTetePES.appendChild(IdPost)

    IdColl = doc.createElement("IdColl")
    IdColl.setAttribute("V", dictDonnees["id_collectivite"])
    EnTetePES.appendChild(IdColl)

    CodCol = doc.createElement("CodCol")
    CodCol.setAttribute("V", dictDonnees["code_collectivite"])
    EnTetePES.appendChild(CodCol)

    CodBud = doc.createElement("CodBud")
    CodBud.setAttribute("V", dictDonnees["code_budget"])
    EnTetePES.appendChild(CodBud)

    # PES_RecetteAller
    PES_RecetteAller = doc.createElement("PES_RecetteAller")
    racine.appendChild(PES_RecetteAller)

    # EnTeteRecette
    EnTeteRecette = doc.createElement("EnTeteRecette")
    PES_RecetteAller.appendChild(EnTeteRecette)
    
    IdVer = doc.createElement("IdVer")
    IdVer.setAttribute("V", "2")
    EnTeteRecette.appendChild(IdVer)
    
    InfoDematerialisee = doc.createElement("InfoDematerialisee")
    InfoDematerialisee.setAttribute("V", "0")
    EnTeteRecette.appendChild(InfoDematerialisee)

    # Bordereau
    Bordereau = doc.createElement("Bordereau")
    PES_RecetteAller.appendChild(Bordereau)
    
    # Bloc Bordereau
    BlocBordereau = doc.createElement("BlocBordereau")
    Bordereau.appendChild(BlocBordereau)
    
    Exer = doc.createElement("Exer")
    Exer.setAttribute("V", dictDonnees["exercice"])
    BlocBordereau.appendChild(Exer)
    
    IdBord = doc.createElement("IdBord")
    IdBord.setAttribute("V", dictDonnees["id_bordereau"])
    BlocBordereau.appendChild(IdBord)
    
    DteBordEm = doc.createElement("DteBordEm")
    DteBordEm.setAttribute("V", dictDonnees["date_emission"])
    BlocBordereau.appendChild(DteBordEm)

    TypBord = doc.createElement("TypBord")
    TypBord.setAttribute("V", "06")
    BlocBordereau.appendChild(TypBord)

    NbrPce = doc.createElement("NbrPce")
    NbrPce.setAttribute("V", str(len(dictDonnees["pieces"])))
    BlocBordereau.appendChild(NbrPce)

    MtBordHt = doc.createElement("MtBordHt")
    MtBordHt.setAttribute("V", dictDonnees["montant_total"])
    BlocBordereau.appendChild(MtBordHt)

    DteAsp = doc.createElement("DteAsp")
    DteAsp.setAttribute("V", dictDonnees["date_envoi"])
    BlocBordereau.appendChild(DteAsp)

    Objet = doc.createElement("Objet")
    Objet.setAttribute("V", dictDonnees["objet_dette"])
    BlocBordereau.appendChild(Objet)
    
    # ----------------------- PIECES --------------------------------------------------------------------------------------------------------------------------
    
    for dictPiece in dictDonnees["pieces"] :
        
        # Pièce
        Piece = doc.createElement("Piece")
        Bordereau.appendChild(Piece)
    
        BlocPiece = doc.createElement("BlocPiece")
        Piece.appendChild(BlocPiece)
    
        IdPce = doc.createElement("IdPce")
        IdPce.setAttribute("V", dictPiece["id_piece"])
        BlocPiece.appendChild(IdPce)
    
        TypPce = doc.createElement("TypPce")
        TypPce.setAttribute("V", "15")
        BlocPiece.appendChild(TypPce)
    
        NatPce = doc.createElement("NatPce")
        NatPce.setAttribute("V", "01")
        BlocPiece.appendChild(NatPce)

        ObjPce = doc.createElement("ObjPce")
        ObjPce.setAttribute("V", dictPiece["objet_piece"])
        BlocPiece.appendChild(ObjPce)

        NumDette = doc.createElement("NumDette")
        NumDette.setAttribute("V", u"{:0>13}".format(dictPiece["num_dette"]))
        BlocPiece.appendChild(NumDette)

        Per = doc.createElement("Per")
        Per.setAttribute("V", dictDonnees["mois"])
        BlocPiece.appendChild(Per)

        Cle1 = doc.createElement("Cle1")
        cle1 = GetCle_modulo11((dictDonnees["code_collectivite"], dictDonnees["id_bordereau"], dictDonnees["exercice"][-2:], dictDonnees["mois"], u"{:0>13}".format(dictPiece["num_dette"])))
        Cle1.setAttribute("V", str(cle1))
        BlocPiece.appendChild(Cle1)
        
        Cle2 = doc.createElement("Cle2")
        cle2 = GetCle_modulo23((dictDonnees["exercice"][-2:], dictDonnees["mois"], "00", u"{:0>13}".format(dictPiece["num_dette"])))
        Cle2.setAttribute("V", cle2)
        BlocPiece.appendChild(Cle2)

        # Ligne de pièce
        LigneDePiece = doc.createElement("LigneDePiece")
        Piece.appendChild(LigneDePiece)
        
        BlocLignePiece = doc.createElement("BlocLignePiece")
        LigneDePiece.appendChild(BlocLignePiece)
        
        InfoLignePiece = doc.createElement("InfoLignePiece")
        BlocLignePiece.appendChild(InfoLignePiece)
        
        IdLigne = doc.createElement("IdLigne")
        IdLigne.setAttribute("V", "1")
        InfoLignePiece.appendChild(IdLigne)

        CodProdLoc = doc.createElement("CodProdLoc")
        CodProdLoc.setAttribute("V", dictDonnees["code_prodloc"])
        InfoLignePiece.appendChild(CodProdLoc)

        Nature = doc.createElement("Nature")
        Nature.setAttribute("V", "588")
        InfoLignePiece.appendChild(Nature)

        Majo = doc.createElement("Majo")
        Majo.setAttribute("V", "0")
        InfoLignePiece.appendChild(Majo)

        TvaIntraCom = doc.createElement("TvaIntraCom")
        TvaIntraCom.setAttribute("V", "0")
        InfoLignePiece.appendChild(TvaIntraCom)

        MtHT = doc.createElement("MtHT")
        MtHT.setAttribute("V", dictPiece["montant"])
        InfoLignePiece.appendChild(MtHT)

        # Info prélèvement SEPA
        if dictPiece["prelevement"] == 1 :
            
            InfoPrelevementSEPA = doc.createElement("InfoPrelevementSEPA")
            BlocLignePiece.appendChild(InfoPrelevementSEPA)

            NatPrel = doc.createElement("NatPrel")
            NatPrel.setAttribute("V", "01")
            InfoPrelevementSEPA.appendChild(NatPrel)

            PerPrel = doc.createElement("PerPrel")
            PerPrel.setAttribute("V", "07")
            InfoPrelevementSEPA.appendChild(PerPrel)

            DtePrel = doc.createElement("DtePrel")
            DtePrel.setAttribute("V", dictDonnees["date_prelevement"])
            InfoPrelevementSEPA.appendChild(DtePrel)

            MtPrel = doc.createElement("MtPrel")
            MtPrel.setAttribute("V", dictPiece["montant"])
            InfoPrelevementSEPA.appendChild(MtPrel)
            
            if dictPiece["sequence"] == "FRST" : 
                sequence = "02"
            elif dictPiece["sequence"] == "RCUR" :
                sequence = "03"
            elif dictPiece["sequence"] == "FNAL" :
                sequence = "04"
            else :
                sequence = "01"
            SequencePres = doc.createElement("SequencePres")
            SequencePres.setAttribute("V", sequence)
            InfoPrelevementSEPA.appendChild(SequencePres)

            DateSignMandat = doc.createElement("DateSignMandat")
            DateSignMandat.setAttribute("V", dictPiece["prelevement_date_mandat"])
            InfoPrelevementSEPA.appendChild(DateSignMandat)

            RefUniMdt = doc.createElement("RefUniMdt")
            RefUniMdt.setAttribute("V", dictPiece["prelevement_rum"])
            InfoPrelevementSEPA.appendChild(RefUniMdt)
            
            LibPrel = doc.createElement("LibPrel")
            LibPrel.setAttribute("V", dictPiece["prelevement_libelle"][:140])
            InfoPrelevementSEPA.appendChild(LibPrel)            

        # Tiers
        Tiers = doc.createElement("Tiers")
        LigneDePiece.appendChild(Tiers)

        InfoTiers = doc.createElement("InfoTiers")
        Tiers.appendChild(InfoTiers)
        
        CatTiers = doc.createElement("CatTiers")
        CatTiers.setAttribute("V", "01")
        InfoTiers.appendChild(CatTiers)
        
        NatJur = doc.createElement("NatJur")
        NatJur.setAttribute("V", "01")
        InfoTiers.appendChild(NatJur)
        
        TypTiers = doc.createElement("TypTiers")
        TypTiers.setAttribute("V", "01")
        InfoTiers.appendChild(TypTiers)
        
        civilite = dictPiece["titulaire_civilite"]
        if civilite == "M." : civilite = "Mr"
        if civilite == "Melle" : civilite = "Mme"
        Civilite = doc.createElement("Civilite")
        Civilite.setAttribute("V", civilite)
        InfoTiers.appendChild(Civilite)
        
        Nom = doc.createElement("Nom")
        Nom.setAttribute("V", dictPiece["titulaire_nom"])
        InfoTiers.appendChild(Nom)
        
        Prenom = doc.createElement("Prenom")
        Prenom.setAttribute("V", dictPiece["titulaire_prenom"])
        InfoTiers.appendChild(Prenom)
        
        # Adresse
        Adresse = doc.createElement("Adresse")
        Tiers.appendChild(Adresse)
        
        TypAdr = doc.createElement("TypAdr")
        TypAdr.setAttribute("V", "1")
        Adresse.appendChild(TypAdr)
        
        Adr2 = doc.createElement("Adr2")
        Adr2.setAttribute("V", dictPiece["titulaire_rue"])
        Adresse.appendChild(Adr2)
        
        CP = doc.createElement("CP")
        CP.setAttribute("V", dictPiece["titulaire_cp"])
        Adresse.appendChild(CP)
        
        Ville = doc.createElement("Ville")
        Ville.setAttribute("V", dictPiece["titulaire_ville"])
        Adresse.appendChild(Ville)

        CodRes = doc.createElement("CodRes")
        CodRes.setAttribute("V", "0")
        Adresse.appendChild(CodRes)

        # Compte bancaire
        if dictPiece["prelevement"] == 1 :
            
            CpteBancaire = doc.createElement("CpteBancaire")
            Tiers.appendChild(CpteBancaire)
            
            BIC = doc.createElement("BIC")
            BIC.setAttribute("V", dictPiece["prelevement_bic"])
            CpteBancaire.appendChild(BIC)

            IBAN = doc.createElement("IBAN")
            IBAN.setAttribute("V", dictPiece["prelevement_iban"])
            CpteBancaire.appendChild(IBAN)
            
            TitCpte = doc.createElement("TitCpte")
            TitCpte.setAttribute("V", dictPiece["prelevement_titulaire"])
            CpteBancaire.appendChild(TitCpte)

    return doc


def EnregistrerXML(doc=None, nomFichier=""):
    """ Enregistre le fichier XML """
    f = open(nomFichier, "w")
    try:
        f.write(doc.toprettyxml(indent="  ", encoding="ISO-8859-1"))
    finally:
        f.close()
    

def GetCle_modulo11(elements=[]):
    """ Calcul de la clé Modulo 11 """
    nombre = "".join(elements)[::-1]
    listeCoeff = [2, 3, 4, 5, 6, 7] * (len(nombre) / 6 + 1)
    total = 0
    index = 0
    for chiffre in nombre :
        if chiffre not in "0123456789" : chiffre = "0"
        total += int(chiffre) * listeCoeff[index]
        index += 1
    if total % 11 == 0 : 
        pass
##        return 0
    cle = 11 - (total % 11)
    if cle > 9 : cle = 1
    return cle

def GetCle_modulo23(elements=[]):
    """ Calcul de la clé Modulo 23 """
    nombre = "".join(elements)
    K = (int(nombre) % 23) + 1
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXY"
    cle = alphabet[K-1]
    return cle

    
if __name__ == "__main__":

    dictDonnees = {
        "nom_fichier" : u"fichier.xml",
        "date_emission" : u"2014-01-06",
        "id_poste" : u"IDPOSTE",
        "id_collectivite" : u"IDCOLLECTIVITE",
        "code_collectivite" : u"2",
        "code_budget" : u"CODEBUDGET",
        "exercice" : u"2013",
        "mois" : u"9",
        "id_bordereau" : u"5",
        "montant_total" : u"22.50",
        "date_envoi" : u"2014-01-07",
        "objet_dette" : u"Centre de Loisirs",
        "code_prodloc" : "CODEPRODLOC",
        "date_prelevement" : "2014-01-08",
        "pieces" : [
            {
            "id_piece" : "1",
            "libelle" : u"FACT0000123",
            "num_dette" : u"2013000017",
            "montant" : u"10.50",
            "sequence" : "RCUR",
            "prelevement" : 1,
            "prelevement_date_mandat" : "2013-12-01",
            "prelevement_rum" : "123",
            "prelevement_bic" : "123456",
            "prelevement_iban" : "45665465423456",
            "prelevement_titulaire" : u"DUPOND Gérard",
            "titulaire_civilite" : "Mr.",
            "titulaire_nom" : u"DUPOND",
            "titulaire_prenom" : u"Gérard",
            "titulaire_rue" : u"10 rue des oiseaux",
            "titulaire_cp" : u"29870",
            "titulaire_ville" : u"LANNILIS",
            }
            ],
        }

    doc = GetXML(dictDonnees) 
    print doc.toprettyxml(indent="  ", encoding="ISO-8859-1")
