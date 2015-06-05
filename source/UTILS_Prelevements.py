#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import datetime
import string
from xml.dom.minidom import Document


def GetLigneEmetteur(dictDonnees={}) :
    """ Création de la première ligne avec les infos sur l'émetteur """
    """
    dictDonnees = {
        "type_prelevement" : u"0308",
        "numero_emetteur" : u"222222",
        "date" : datetime.date.today(),
        "raison_sociale" : _(u"CENTRE SOCIAL"),
        "reference_virement" : _(u"VIR.ALSH"),
        "monnaie" : u"E",
        "numero_guichet" : u"02902",
        "numero_compte" : u"01234567895",
        "numero_etablissement" : u"12345",
        }
    """
    
    texte = u""
    texte += u"{:<4}".format(dictDonnees["type_prelevement"])
    texte += u"{:<8}".format("") 
    texte += u"{:<6}".format(dictDonnees["numero_emetteur"][:6])
    texte += u"{:<7}".format("") 
    texte += u"%02d%02d%s" % (dictDonnees["date"].day, dictDonnees["date"].month, str(dictDonnees["date"])[3])
    texte += u"{:<24}".format(dictDonnees["raison_sociale"][:24])
    texte += u"{:<11}".format("")#dictDonnees["reference_virement"])
    texte += u"{:<15}".format("") 
    texte += u"{:<1}".format(dictDonnees["monnaie"])
    texte += u"{:<5}".format("") 
    texte += u"{:<5}".format(dictDonnees["numero_guichet"][:5])
    texte += u"{:<11}".format(dictDonnees["numero_compte"][:11])
    texte += u"{:<47}".format("") 
    texte += u"{:<5}".format(dictDonnees["numero_etablissement"][:5])
    texte += u"{:<6}".format("") 
    texte += u"\n"
    return texte


def GetLigneDestinataire(dictDonnees={}) :
    """ Création de la ligne destinataire """
    """
    dictDonnees = {
        "type_prelevement" : u"0608",
        "numero_emetteur" : u"222222",
        "reference_ligne" : u"1",
        "nom_destinataire" : _(u"S.A Matériaux plus"),
        "nom_banque" : _(u"Crédit agricole"),
        "numero_guichet" : u"02902",
        "numero_compte" : u"01234567895",
        "montant" : u"1201",
        "libelle" : _(u"Vir. facture 12345"),
        "numero_etablissement" : u"12345",
        }
    """
        
    texte = u""
    texte += u"{:<4}".format(dictDonnees["type_prelevement"])
    texte += u"{:<8}".format("") 
    texte += u"{:<6}".format(dictDonnees["numero_emetteur"][:6])
    texte += u"{:<12}".format(dictDonnees["reference_ligne"][:12])
    texte += u"{:<24}".format(dictDonnees["nom_destinataire"][:24])
    texte += u"{:<20}".format(dictDonnees["nom_banque"][:20])
    texte += u"{:<12}".format("") 
    texte += u"{:<5}".format(dictDonnees["numero_guichet"][:5])
    texte += u"{:<11}".format(dictDonnees["numero_compte"][:11])
    texte += u'{:0>16}'.format(dictDonnees["montant"])
    texte += u"{:<31}".format(dictDonnees["libelle"][:31])
    texte += u"{:<5}".format(dictDonnees["numero_etablissement"][:5])
    texte += u"{:<6}".format("") 
    texte += u"\n"
    return texte


def GetLigneTotal(dictDonnees={}) :
    """ Création de la dernière ligne avec les totaux """
    """
    dictDonnees = {
        "type_prelevement" : u"0808",
        "numero_emetteur" : u"222222",
        "total" : u"1200",
        }
    """
    
    texte = u""
    texte += u"{:<4}".format(dictDonnees["type_prelevement"])
    texte += u"{:<8}".format("") 
    texte += u"{:<6}".format(dictDonnees["numero_emetteur"][:6])
    texte += u"{:<84}".format("") 
    texte += u"{:0>16}".format(dictDonnees["total"])
    texte += u"{:<42}".format("") 
    texte += u"\n"
    return texte



def AlgoControleRIB(bic):
    replacement_table = {
            'AJaj': '1',
            'BKSbks': '2',
            'CLTclt': '3',
            'DMUdmu': '4',
            'ENVenv': '5',
            'FOWfow': '6',
            'GPXgpx': '7',
            'HQYhqy': '8',
            'IRZirz': '9',
            }
    if len(bic) != 23:
        return False
    for i in range(len(bic)):
        char = bic[i]
        for pattern in replacement_table.keys():
            if char in pattern:
                bic = bic.replace(char, replacement_table[pattern])
    bankcode = int(bic[:5])
    counter = int(bic[5:10])
    account = int(bic[10:21])
    key = int(bic[21:])
    return (bankcode*89 + counter*15 + account*3 + key) % 97 == 0


def ConvertirRIBenIBAN(rib="", codePays="FR"):
    """ rib = codebanque+ codeGuichet + numerocompte + cle """
    cle = CalcCleBAN(rib, codePays)
    iban = codePays + cle + rib
    return iban
    
def CalcCleBAN(rib="", codePays="FR"):
    """ rib = codebanque+ codeGuichet + numerocompte + cle """
    tmp = rib + codePays + "00"
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    tmp2 = ""
    for c in tmp :
        if c in alphabet :
            position = alphabet.index(c)
            c = str(position + 10)
        tmp2 += c
    cle = str(98 - (int(tmp2) % 97))
    if len(cle) == 1 :
        cle = "0%s" % cle
    return cle


def ControleIBAN(iban=""):
    """IBAN Python validation"""
    IBAN_CHAR_MAP = {"A":"10", "B":"11", "C":"12", "D":"13", "E":"14", "F":"15", 
                     "G":"16", "H":"17", "I":"18", "J":"19", "K":"20", "L":"21",
                     "M":"22", "N":"23", "O":"24", "P":"25", "Q":"26", "R":"27",
                     "S":"28", "T":"29", "U":"30", "V":"31", "W":"32", "X":"33", 
                     "Y":"34", "Z":"35"}
     
    def replaceAll(text, char_map):
        """Replace the char_map in text"""
        for k, v in char_map.iteritems():
            text = text.replace(k, v)
        return text
    
    try :
        iban = iban.replace('-', '').replace(' ', '')
        iban = replaceAll(iban[4:]+iban[0:4], IBAN_CHAR_MAP)
        res = int(iban) % 97    
        return res == 1
    except :
        return False


def ControleBIC(bic):
    """ Validation for ISO 9362:2009 (SWIFT-BIC). """
    # Length is 8 or 11.
    swift_bic_length = len(bic)
    if swift_bic_length != 8 and swift_bic_length != 11:
        return False

    # First 4 letters are A - Z.
    for x in bic[:4] :
        if x not in string.uppercase:
            return False

    return True


def GetXMLSepa(dictDonnees):
    """ Génération du fichier XML SEPA """
    doc = Document()
    
    # Variables principales    
    remise_nom = dictDonnees["remise_nom"]
    remise_date_heure = dictDonnees["remise_date_heure"]
    remise_nbre = dictDonnees["remise_nbre"]
    remise_montant = dictDonnees["remise_montant"]
    
    creancier_nom = dictDonnees["creancier_nom"]
    creancier_rue = dictDonnees["creancier_rue"]
    creancier_cp = dictDonnees["creancier_cp"]
    creancier_ville = dictDonnees["creancier_ville"]
    creancier_pays = dictDonnees["creancier_pays"]
    creancier_siret = dictDonnees["creancier_siret"]
    
    listeLots = dictDonnees["lots"]

    # Génération du document XML
    racine = doc.createElement("Document")
    racine.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    racine.setAttribute("xmlns", "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02")
    doc.appendChild(racine)
    
    # CstmrDrctDbtInitn
    CstmrDrctDbtInitn = doc.createElement("CstmrDrctDbtInitn")
    racine.appendChild(CstmrDrctDbtInitn)
    
    # ----------------------------------------------------------- NIVEAU MESSAGE ------------------------------------------------------------------------------
    
    # ------------- Caractéristiques générales du prélèvement -------------------
    
    # GrpHdr
    GrpHdr = doc.createElement("GrpHdr")
    CstmrDrctDbtInitn.appendChild(GrpHdr)

    # MsgId
    MsgId = doc.createElement("MsgId")
    GrpHdr.appendChild(MsgId)
    MsgId.appendChild(doc.createTextNode(remise_nom))

    # CreDtTm
    CreDtTm = doc.createElement("CreDtTm")
    GrpHdr.appendChild(CreDtTm)
    CreDtTm.appendChild(doc.createTextNode(remise_date_heure))

    # NbOfTxs
    NbOfTxs = doc.createElement("NbOfTxs")
    GrpHdr.appendChild(NbOfTxs)
    NbOfTxs.appendChild(doc.createTextNode(remise_nbre))

    # CtrlSum
    CtrlSum = doc.createElement("CtrlSum")
    GrpHdr.appendChild(CtrlSum)
    CtrlSum.appendChild(doc.createTextNode(remise_montant))

    # ------------- Créantier (organisateur) -------------------

    # InitgPty
    InitgPty = doc.createElement("InitgPty")
    GrpHdr.appendChild(InitgPty)

    # Nm
    Nm = doc.createElement("Nm")
    InitgPty.appendChild(Nm)
    Nm.appendChild(doc.createTextNode(creancier_nom[:70]))

##    # PstlAdr
##    PstlAdr = doc.createElement("PstlAdr")
##    InitgPty.appendChild(PstlAdr)
##
##    # StrtNm
##    StrtNm = doc.createElement("StrtNm")
##    PstlAdr.appendChild(StrtNm)
##    StrtNm.appendChild(doc.createTextNode(creancier_rue))
##
##    # PstCd
##    PstCd = doc.createElement("PstCd")
##    PstlAdr.appendChild(PstCd)
##    PstCd.appendChild(doc.createTextNode(creancier_cp))
##
##    # TwnNm
##    TwnNm = doc.createElement("TwnNm")
##    PstlAdr.appendChild(TwnNm)
##    TwnNm.appendChild(doc.createTextNode(creancier_ville))
##
##    # Ctry
##    Ctry = doc.createElement("Ctry")
##    PstlAdr.appendChild(Ctry)
##    Ctry.appendChild(doc.createTextNode(creancier_pays))

    # Id
    Id = doc.createElement("Id")
    InitgPty.appendChild(Id)
    
    # OrgId
    OrgId = doc.createElement("OrgId")
    Id.appendChild(OrgId)
    
    # Othr
    Othr = doc.createElement("Othr")
    OrgId.appendChild(Othr)
    
    # Id
    Id = doc.createElement("Id")
    Othr.appendChild(Id)
    Id.appendChild(doc.createTextNode(creancier_siret))

    # SchmeNm
    SchmeNm = doc.createElement("SchmeNm")
    Othr.appendChild(SchmeNm)
    
    # Prtry
    Prtry = doc.createElement("Prtry")
    SchmeNm.appendChild(Prtry)
    Prtry.appendChild(doc.createTextNode("SIRET"))

    # ----------------------------------------------------------- NIVEAU LOT ------------------------------------------------------------------------------
    
    for dictLot in listeLots :

        lot_nom = dictLot["lot_nom"]
        lot_nbre = dictLot["lot_nbre"]
        lot_montant = dictLot["lot_montant"]
        lot_date = dictLot["lot_date"]
        lot_iban = dictLot["lot_iban"]
        lot_bic = dictLot["lot_bic"]
        lot_ics = dictLot["lot_ics"]
        lot_sequence = dictLot["lot_sequence"]
        listeTransactions = dictLot["transactions"]

        # PmtInf
        PmtInf = doc.createElement("PmtInf")
        CstmrDrctDbtInitn.appendChild(PmtInf)

        # PmtInfId
        PmtInfId = doc.createElement("PmtInfId")
        PmtInf.appendChild(PmtInfId)
        PmtInfId.appendChild(doc.createTextNode(lot_nom))

        # PmtMtd
        PmtMtd = doc.createElement("PmtMtd")
        PmtInf.appendChild(PmtMtd)
        PmtMtd.appendChild(doc.createTextNode("DD")) 

        # NbOfTxs
        NbOfTxs = doc.createElement("NbOfTxs")
        PmtInf.appendChild(NbOfTxs)
        NbOfTxs.appendChild(doc.createTextNode(lot_nbre))

        # CtrlSum
        CtrlSum = doc.createElement("CtrlSum")
        PmtInf.appendChild(CtrlSum)
        CtrlSum.appendChild(doc.createTextNode(lot_montant))

        # PmtTpInf
        PmtTpInf = doc.createElement("PmtTpInf")
        PmtInf.appendChild(PmtTpInf)

        # SvcLvl
        SvcLvl = doc.createElement("SvcLvl")
        PmtTpInf.appendChild(SvcLvl)

        # Cd
        Cd = doc.createElement("Cd")
        SvcLvl.appendChild(Cd)
        Cd.appendChild(doc.createTextNode("SEPA"))

        # LclInstrm
        LclInstrm = doc.createElement("LclInstrm")
        PmtTpInf.appendChild(LclInstrm)

        # Cd
        Cd = doc.createElement("Cd")
        LclInstrm.appendChild(Cd)
        Cd.appendChild(doc.createTextNode("CORE"))

        # SeqTp
        SeqTp = doc.createElement("SeqTp")
        PmtTpInf.appendChild(SeqTp)
        SeqTp.appendChild(doc.createTextNode(lot_sequence))

        # ReqdColltnDt
        ReqdColltnDt = doc.createElement("ReqdColltnDt")
        PmtInf.appendChild(ReqdColltnDt)
        ReqdColltnDt.appendChild(doc.createTextNode(lot_date))

        # Cdtr
        Cdtr = doc.createElement("Cdtr")
        PmtInf.appendChild(Cdtr)
        
        # Cdtr
        Nm = doc.createElement("Nm")
        Cdtr.appendChild(Nm)
        Nm.appendChild(doc.createTextNode(creancier_nom))

        # CdtrAcct
        CdtrAcct = doc.createElement("CdtrAcct")
        PmtInf.appendChild(CdtrAcct)

        # Id
        Id = doc.createElement("Id")
        CdtrAcct.appendChild(Id)

        # IBAN
        IBAN = doc.createElement("IBAN")
        Id.appendChild(IBAN)
        IBAN.appendChild(doc.createTextNode(lot_iban))

        # CdtrAgt
        CdtrAgt = doc.createElement("CdtrAgt")
        PmtInf.appendChild(CdtrAgt)

        # FinInstnId
        FinInstnId = doc.createElement("FinInstnId")
        CdtrAgt.appendChild(FinInstnId)

        # BIC
        BIC = doc.createElement("BIC")
        FinInstnId.appendChild(BIC)
        BIC.appendChild(doc.createTextNode(lot_bic))

        # CdtrSchmeId
        CdtrSchmeId = doc.createElement("CdtrSchmeId")
        PmtInf.appendChild(CdtrSchmeId)

        # Id
        Id = doc.createElement("Id")
        CdtrSchmeId.appendChild(Id)
        
        # PrvtId
        PrvtId = doc.createElement("PrvtId")
        Id.appendChild(PrvtId)

        # Othr
        Othr = doc.createElement("Othr")
        PrvtId.appendChild(Othr)

        # Id
        Id = doc.createElement("Id")
        Othr.appendChild(Id)
        Id.appendChild(doc.createTextNode(lot_ics))
        
        # SchmeNm
        SchmeNm = doc.createElement("SchmeNm")
        Othr.appendChild(SchmeNm)

        # Prtry
        Prtry = doc.createElement("Prtry")
        SchmeNm.appendChild(Prtry)
        Prtry.appendChild(doc.createTextNode("SEPA"))
        
        
        # ----------------------------------------------------------- NIVEAU TRANSACTION ------------------------------------------------------------------------------
        
        for dictTransaction in listeTransactions :
        
            transaction_id = dictTransaction["transaction_id"]
            transaction_montant = dictTransaction["transaction_montant"]
            transaction_mandat_id = dictTransaction["transaction_mandat_id"]
            transaction_mandat_date = dictTransaction["transaction_mandat_date"]
            transaction_bic = dictTransaction["transaction_bic"]
            transaction_debiteur = dictTransaction["transaction_debiteur"]
            transaction_iban = dictTransaction["transaction_iban"]

            # DrctDbtTxInf
            DrctDbtTxInf = doc.createElement("DrctDbtTxInf")
            PmtInf.appendChild(DrctDbtTxInf)
            
            # PmtId
            PmtId = doc.createElement("PmtId")
            DrctDbtTxInf.appendChild(PmtId)
            
            # EndToEndId
            EndToEndId = doc.createElement("EndToEndId")
            PmtId.appendChild(EndToEndId)
            EndToEndId.appendChild(doc.createTextNode(transaction_id))
            
            # InstdAmt
            InstdAmt = doc.createElement("InstdAmt")
            DrctDbtTxInf.appendChild(InstdAmt)
            InstdAmt.appendChild(doc.createTextNode(transaction_montant))
            InstdAmt.setAttribute("Ccy", "EUR")
            
            # DrctDbtTx
            DrctDbtTx = doc.createElement("DrctDbtTx")
            DrctDbtTxInf.appendChild(DrctDbtTx)

            # MndtRltdInf
            MndtRltdInf = doc.createElement("MndtRltdInf")
            DrctDbtTx.appendChild(MndtRltdInf)
            
            # MndtId
            MndtId = doc.createElement("MndtId")
            MndtRltdInf.appendChild(MndtId)
            MndtId.appendChild(doc.createTextNode(transaction_mandat_id))
            
            # DtOfSgntr
            DtOfSgntr = doc.createElement("DtOfSgntr")
            MndtRltdInf.appendChild(DtOfSgntr)
            DtOfSgntr.appendChild(doc.createTextNode(transaction_mandat_date))
            
            # DbtrAgt
            DbtrAgt = doc.createElement("DbtrAgt")
            DrctDbtTxInf.appendChild(DbtrAgt)

            # FinInstnId
            FinInstnId = doc.createElement("FinInstnId")
            DbtrAgt.appendChild(FinInstnId)

            # Dbtr
            BIC = doc.createElement("BIC")
            FinInstnId.appendChild(BIC)
            BIC.appendChild(doc.createTextNode(transaction_bic))

            # Dbtr
            Dbtr = doc.createElement("Dbtr")
            DrctDbtTxInf.appendChild(Dbtr)

            # Nm
            Nm = doc.createElement("Nm")
            Dbtr.appendChild(Nm)
            Nm.appendChild(doc.createTextNode(transaction_debiteur[:70]))

            # DbtrAcct
            DbtrAcct = doc.createElement("DbtrAcct")
            DrctDbtTxInf.appendChild(DbtrAcct)

            # Id
            Id = doc.createElement("Id")
            DbtrAcct.appendChild(Id)

            # IBAN
            IBAN = doc.createElement("IBAN")
            Id.appendChild(IBAN)
            IBAN.appendChild(doc.createTextNode(transaction_iban))

    return doc


def EnregistrerXML(doc=None, nomFichier=""):
    """ Enregistre le fichier XML """
    f = open(nomFichier, "w")
    try:
        f.write(doc.toprettyxml(indent="  "))
    finally:
        f.close()
    
    
    
if __name__ == "__main__":
    rib = "20041010011505203J02242"
    print ControleIBAN(iban="FR76"+rib)
    print CalcCleBAN(rib)