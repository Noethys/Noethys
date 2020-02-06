#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
from xml.dom.minidom import Document
from lxml import etree
import six
import wx
import FonctionsPerso
from six.moves.urllib.request import urlretrieve
from Utils import UTILS_Fichiers
import zipfile



def DemanderChoix(parent):
    """ Propose le choix entre ROLMRE et PES V2 ORMC """
    from Dlg import DLG_Choix
    titre = _(u"Quel protocole d'échanges souhaitez-vous utiliser ?")
    intro = _(u"Cliquez sur le protocole d'échange souhaité afin d'accéder à la fonctionnalité dédiée...")
    listeBoutons = [
        (_(u"Bordereau PES Recette ORMC"), _(u"Nouveau type de bordereau Recette ORMC (Ordre de Recette Multi Créanciers) fidèle au nouveau protocole d'échange PES V2 entre les collectivités locales et la DGFIP. Remplace le protocole ROLMRE à partir du 01/02/2014.")),
        (_(u"Rôle ROLMRE"), _(u"Le protocole ROLMRE est une procédure d'échanges de données utilisée dans les collectivités qui devient obsolète à partir du 01/02/2014. Au delà de cette date, il faut utiliser le bordereau PES ORMC.")),
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
    NomFic.setAttribute("V", dictDonnees["nom_fichier"][:100])
    Parametres.appendChild(NomFic)

    Emetteur = doc.createElement("Emetteur")
    Enveloppe.appendChild(Emetteur)

    Sigle = doc.createElement("Sigle")
    Sigle.setAttribute("V", "Ivan LUCAS")
    Emetteur.appendChild(Sigle)
    
    versionLogiciel = FonctionsPerso.GetVersionLogiciel()
    Adresse = doc.createElement("Adresse")
    Adresse.setAttribute("V", _(u"Noethys %s") % versionLogiciel)
    Emetteur.appendChild(Adresse)

    # EnTetePES
    EnTetePES = doc.createElement("EnTetePES")
    racine.appendChild(EnTetePES)

    DteStr = doc.createElement("DteStr")
    DteStr.setAttribute("V", dictDonnees["date_emission"])
    EnTetePES.appendChild(DteStr)

    IdPost = doc.createElement("IdPost")
    IdPost.setAttribute("V", dictDonnees["id_poste"][:7])
    EnTetePES.appendChild(IdPost)

    IdColl = doc.createElement("IdColl")
    IdColl.setAttribute("V", dictDonnees["id_collectivite"][:14])
    EnTetePES.appendChild(IdColl)

    CodCol = doc.createElement("CodCol")
    CodCol.setAttribute("V", dictDonnees["code_collectivite"][:3])
    EnTetePES.appendChild(CodCol)

    CodBud = doc.createElement("CodBud")
    CodBud.setAttribute("V", dictDonnees["code_budget"][:10])
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
    Exer.setAttribute("V", dictDonnees["exercice"][:4])
    BlocBordereau.appendChild(Exer)
    
    IdBord = doc.createElement("IdBord")
    IdBord.setAttribute("V", dictDonnees["id_bordereau"][:7])
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
    Objet.setAttribute("V", dictDonnees["objet_dette"][:160])
    BlocBordereau.appendChild(Objet)
    
    # ----------------------- PIECES --------------------------------------------------------------------------------------------------------------------------
    
    for dictPiece in dictDonnees["pieces"] :
        
        # Pièce
        Piece = doc.createElement("Piece")
        Bordereau.appendChild(Piece)
    
        BlocPiece = doc.createElement("BlocPiece")
        Piece.appendChild(BlocPiece)
    
        IdPce = doc.createElement("IdPce")
        IdPce.setAttribute("V", dictPiece["id_piece"][:8])
        BlocPiece.appendChild(IdPce)
    
        TypPce = doc.createElement("TypPce")
        TypPce.setAttribute("V", "15")
        BlocPiece.appendChild(TypPce)
    
        NatPce = doc.createElement("NatPce")
        NatPce.setAttribute("V", "01")
        BlocPiece.appendChild(NatPce)

        if dictDonnees["pieces_jointes"] != False :
            Edition = doc.createElement("Edition")
            Edition.setAttribute("V", "03")
            BlocPiece.appendChild(Edition)

        ObjPce = doc.createElement("ObjPce")
        ObjPce.setAttribute("V", dictPiece["objet_piece"][:160])
        BlocPiece.appendChild(ObjPce)
        
        NumDette = doc.createElement("NumDette")
        NumDette.setAttribute("V", dictPiece["num_dette"][:15])
        BlocPiece.appendChild(NumDette)

        Per = doc.createElement("Per")
        Per.setAttribute("V", dictDonnees["mois"][:1])
        BlocPiece.appendChild(Per)

        Cle1 = doc.createElement("Cle1")
        cle1 = GetCle_modulo11((dictDonnees["code_collectivite"], dictDonnees["id_bordereau"], dictDonnees["exercice"][-2:], dictDonnees["mois"], u"{:0>13}".format(dictPiece["num_dette"])))
        Cle1.setAttribute("V", str(cle1))
        BlocPiece.appendChild(Cle1)
        
        Cle2 = doc.createElement("Cle2")
        cle2 = GetCle_modulo23((dictDonnees["exercice"][-2:], dictDonnees["mois"], "00", u"{:0>13}".format(dictPiece["num_dette"])))
        Cle2.setAttribute("V", cle2)
        BlocPiece.appendChild(Cle2)

        if dictDonnees["pieces_jointes"] != False:

            PJRef = doc.createElement("PJRef")
            BlocPiece.appendChild(PJRef)

            Support = doc.createElement("Support")
            Support.setAttribute("V", "01")
            PJRef.appendChild(Support)

            IdUnique = doc.createElement("IdUnique")
            IdUnique.setAttribute("V", dictDonnees["pieces_jointes"][dictPiece["IDfacture"]]["IdUnique"])
            PJRef.appendChild(IdUnique)

            NomPJ = doc.createElement("NomPJ")
            NomPJ.setAttribute("V", dictDonnees["pieces_jointes"][dictPiece["IDfacture"]]["NomPJ"])
            PJRef.appendChild(NomPJ)


        NumeroFacture = doc.createElement("NumeroFacture")
        NumeroFacture.setAttribute("V", dictPiece["num_dette"][:20])
        BlocPiece.appendChild(NumeroFacture)

        # NumeroMarche = doc.createElement("NumeroMarche")
        # NumeroMarche.setAttribute("V", "")
        # BlocPiece.appendChild(NumeroMarche)

        # NumeroEngagement = doc.createElement("NumeroEngagement")
        # NumeroEngagement.setAttribute("V", "")
        # BlocPiece.appendChild(NumeroEngagement)

        # CodeService = doc.createElement("CodeService")
        # CodeService.setAttribute("V", "")
        # BlocPiece.appendChild(CodeService)

        # NomService = doc.createElement("NomService")
        # NomService.setAttribute("V", "")
        # BlocPiece.appendChild(NomService)


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

        ObjLignePce = doc.createElement("ObjLignePce")
        ObjLignePce.setAttribute("V", dictPiece["objet_piece"][:160])
        InfoLignePiece.appendChild(ObjLignePce)

        CodProdLoc = doc.createElement("CodProdLoc")
        CodProdLoc.setAttribute("V", dictDonnees["code_prodloc"][:4])
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
        
        if dictPiece["idtiers_helios"] != "" :
            IdTiers = doc.createElement("IdTiers")
            IdTiers.setAttribute("V", dictPiece["idtiers_helios"])
            InfoTiers.appendChild(IdTiers)

        if dictPiece["natidtiers_helios"] != "" :
            NatIdTiers = doc.createElement("NatIdTiers")
            NatIdTiers.setAttribute("V", str(dictPiece["natidtiers_helios"]))
            InfoTiers.appendChild(NatIdTiers)

        if dictPiece["reftiers_helios"] != "" :
            RefTiers = doc.createElement("RefTiers")
            RefTiers.setAttribute("V", dictPiece["reftiers_helios"])
            InfoTiers.appendChild(RefTiers)
        
        CatTiers = doc.createElement("CatTiers")
        CatTiers.setAttribute("V", dictPiece["cattiers_helios"])
        InfoTiers.appendChild(CatTiers)
        
        NatJur = doc.createElement("NatJur")
        NatJur.setAttribute("V", dictPiece["natjur_helios"])
        InfoTiers.appendChild(NatJur)
        
        TypTiers = doc.createElement("TypTiers")
        TypTiers.setAttribute("V", "01")
        InfoTiers.appendChild(TypTiers)
        
        civilite = dictPiece["titulaire_civilite"]
        if civilite == "M." : civilite = "Mr"
        if civilite == "Melle" : civilite = "Mme"
        if civilite not in (None, "") :
            Civilite = doc.createElement("Civilite")
            Civilite.setAttribute("V", civilite[:10])
            InfoTiers.appendChild(Civilite)
        
        Nom = doc.createElement("Nom")
        Nom.setAttribute("V", dictPiece["titulaire_nom"][:38])
        InfoTiers.appendChild(Nom)
        
        prenom = dictPiece["titulaire_prenom"]
        if prenom not in (None, "") :
            Prenom = doc.createElement("Prenom")
            Prenom.setAttribute("V", prenom[:38])
            InfoTiers.appendChild(Prenom)
        
        # Adresse
        Adresse = doc.createElement("Adresse")
        Tiers.appendChild(Adresse)
        
        TypAdr = doc.createElement("TypAdr")
        TypAdr.setAttribute("V", "1")
        Adresse.appendChild(TypAdr)

        Adr2 = doc.createElement("Adr2")
        Adr2.setAttribute("V", dictPiece["titulaire_rue"][:38])
        Adresse.appendChild(Adr2)
        
        CP = doc.createElement("CP")
        CP.setAttribute("V", dictPiece["titulaire_cp"][:5])
        Adresse.appendChild(CP)
        
        Ville = doc.createElement("Ville")
        Ville.setAttribute("V", dictPiece["titulaire_ville"][:38])
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
            TitCpte.setAttribute("V", dictPiece["prelevement_titulaire"][:32])
            CpteBancaire.appendChild(TitCpte)

    # ----------------------- PIECES JOINTES -------------------------------------------------------------------------------------------------------------------

    if dictDonnees["pieces_jointes"] != False and len(dictDonnees["pieces_jointes"]) > 0 :

        # PES_PJ
        PES_PJ = doc.createElement("PES_PJ")
        racine.appendChild(PES_PJ)

        # EnTetePES_PJ
        EnTetePES_PJ = doc.createElement("EnTetePES_PJ")
        PES_PJ.appendChild(EnTetePES_PJ)

        IdVer = doc.createElement("IdVer")
        IdVer.setAttribute("V", "1")
        EnTetePES_PJ.appendChild(IdVer)

        for IDfacture, dictPieceJointe in dictDonnees["pieces_jointes"].items() :

            PJ = doc.createElement("PJ")
            PES_PJ.appendChild(PJ)

            Contenu = doc.createElement("Contenu")
            PJ.appendChild(Contenu)

            Fichier = doc.createElement("Fichier")
            Fichier.setAttribute("MIMEType", "application/pdf")
            Contenu.appendChild(Fichier)

            binaire = doc.createTextNode(dictPieceJointe["contenu"])
            Fichier.appendChild(binaire)

            IdUnique = doc.createElement("IdUnique")
            IdUnique.setAttribute("V", dictPieceJointe["IdUnique"])
            PJ.appendChild(IdUnique)

            NomPJ = doc.createElement("NomPJ")
            NomPJ.setAttribute("V", dictPieceJointe["NomPJ"])
            PJ.appendChild(NomPJ)

            TypePJ = doc.createElement("TypePJ")
            TypePJ.setAttribute("V", "007")
            PJ.appendChild(TypePJ)

            Description = doc.createElement("Description")
            Description.setAttribute("V", "FACTURE %s" % dictPieceJointe["numero_facture"])
            PJ.appendChild(Description)

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
    listeCoeff = [2, 3, 4, 5, 6, 7] * (len(nombre) // 6 + 1)
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

def ValidationXSD(xml=""):
    try :

        # Téléchargement du fichier XSD
        url = "http://www.noethys.com/fichiers/pes/schemas_pes.zip"
        fichier_dest = UTILS_Fichiers.GetRepTemp(fichier="schemas_pes.zip")
        urlretrieve(url, fichier_dest)

        # Décompression du zip XSD
        z = zipfile.ZipFile(fichier_dest, 'r')
        rep_dest = UTILS_Fichiers.GetRepTemp() + "/schemas_pes"
        z.extractall(rep_dest)
        z.close()

        # Lecture du XSD
        fichier_pes = rep_dest + "/Schemas_PES/PES_V2/Rev0/PES_Aller.xsd"
        xmlschema_doc = etree.parse(fichier_pes)
        xsd = etree.XMLSchema(xmlschema_doc)

        # Lecture du XML
        doc = etree.parse(six.BytesIO(xml))

        # Validation du XML avec le XSD
        if xsd.validate(doc) == True :
            return True

        # Affichage des erreurs
        liste_erreurs = []
        for error in xsd.error_log :
            liste_erreurs.append(u"Ligne %d : %s" % (error.line, error.message))
        return liste_erreurs

    except Exception as err:
        print("Erreur dans validation XSD :")
        print(err)
        return True



    
if __name__ == "__main__":

    dictDonnees = {
        "nom_fichier" : _(u"fichier.xml"),
        "date_emission" : u"2014-01-06",
        "id_poste" : _(u"123456"),
        "id_collectivite" : _(u"1"),
        "code_collectivite" : u"2",
        "code_budget" : u"1",
        "exercice" : u"2013",
        "mois" : u"9",
        "id_bordereau" : u"5",
        "montant_total" : u"22.50",
        "date_envoi" : u"2014-01-07",
        "objet_dette" : _(u"Centre de Loisirs"),
        "code_prodloc" : "CODEPRODLOC",
        "date_prelevement" : "2014-01-08",
        "pieces_jointes": False,
        "pieces" : [
            {
            "id_piece" : "1",
            "libelle" : _(u"FACT0000123"),
            "num_dette" : u"2013000017",
            "montant" : u"10.50",
            "sequence" : "RCUR",
            "prelevement" : 1,
            "prelevement_date_mandat" : "2013-12-01",
            "prelevement_rum" : "123",
            "prelevement_bic" : "TESTFR2B",
            "prelevement_iban" : "AB0030001007941234567890100",
            "prelevement_titulaire" : _(u"DUPOND Gérard"),
            "prelevement_libelle" : "prelevement_libelle",
            "titulaire_civilite" : "Mr.",
            "titulaire_nom" : _(u"DUPOND"),
            "titulaire_prenom" : _(u"Gérard"),
            "titulaire_rue" : _(u"10 rue des oiseaux"),
            "titulaire_cp" : u"29870",
            "titulaire_ville" : _(u"LANNILIS"),
            "objet_piece" : "objet",
            "idtiers_helios" : "000000001",
            "natidtiers_helios" : "01",
            "reftiers_helios" : "01",
            "cattiers_helios" : "01",
            "natjur_helios" : "01",
            }
            ],
        }

    doc = GetXML(dictDonnees) 
    xml = doc.toprettyxml(indent="  ", encoding="ISO-8859-1")
    print(xml)

    # Test de validation XSD
    print(ValidationXSD(xml))