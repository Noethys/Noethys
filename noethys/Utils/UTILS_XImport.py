#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          wolf29f
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import os
import six

class DataType(object):
    """
    Classe permettant la conversion facile vers le format souhaité (nombre de caractères, alignement, décimales)
    """

    def __init__(self, type=int, length=1, align="<", precision=2):
        """
        initialise l'objet avec les paramétres souhaités
        """
        self.type = type
        self.length = length
        self.align = align
        self.precision = precision

    def convert(self,data):
        """
        convertit la donnée fournie dans le format souhaité
        """
        ret_val = ""

        # s'assure que la donnée soit bien en unicode
        if type(data) is str:
            if six.PY2:
                data = data.decode("utf8")
            data = six.text_type(data)

        # si l'on veux des entiers
        if self.type == int:
            if data != "":
                # on vérifie qu'il s'agit bien d'un nombre
                try:
                    data = int(data)
                except ValueError as e:
                    print("/!\ Erreur de format, impossible de convertir en int /!\\")
                    print(e)
                    data = 0
                ret_val = u"{0: {align}0{length}d}".format(data,align=self.align,length=self.length)
            else:
                ret_val = u"{0: {align}0{length}s}".format(data,align=self.align,length=self.length)

        # si l'on veux des chaines de caractéres
        elif self.type == str:
            data = data.replace("\"","")
            ret_val = u"{0: {align}0{length}s}".format(data,align=self.align,length=self.length)

        # si l'on veux un nombre a virgule
        elif self.type == float:
            if data != "":
                # on vérifie qu'il s'agit bien d'un nombre
                try:
                    data=float(data)
                except ValueError as e:
                    print("/!\ Erreur de format, impossible de convertir en float /!\\")
                    print(e)
                    data = 0
                ret_val = u"{0: {align}0{length}.{precision}f}".format(data,align=self.align,length=self.length,precision=self.precision)
            else:
                ret_val = u"{0: {align}0{length}s}".format(data,align=self.align,length=self.length)

        # on tronc si la chaine est trop longue
        if len(ret_val) > self.length:
            ret_val = ret_val[:self.length]
        return ret_val

dataTypes = {"num_mvnt":DataType(int,10,">"),
             "journal": DataType(str, 6, "<"),
             "date_ecriture": DataType(int, 8, ">"),
             "date_echeance": DataType(int, 8, ">"),
             "num_piece": DataType(str, 15, "<"),
             "compte": DataType(str, 13, "<"),
             "libelle": DataType(str, 50, "<"),
             "montant": DataType(float, 13, ">"),
             "isDebit": DataType(str, 1, "<"),
             "numPointage": DataType(str, 15, "<"),
             "code_analyt": DataType(str, 13, "<"),
             "libelle_compte": DataType(str, 35, "<"),
             "devise": DataType(str, 1, "<")}


class XImportLine(object):
    """
    Définie une ligne telle que formaté dans un fichier XImport
    """

    def __init__(self,data,dictParametres,num_ligne,typeComptable=None):
        """
        Récupére les donnée utiles fournis en paramétres, les convertis et les enregistre 
        """
        # contient les valeurs fournies et non converties
        values = dict()

        # contiendra les valeurs convertie
        self.values = dict()

        # le numéro de mouvement est le numéro de la ligne ?
        values["num_mvnt"] = num_ligne
        values["montant"] = data["montant"]
        values["devise"] = u"€"

        # on récupére ce qui nous interesse selon le type de donnée
        if "type" in data:
            
            if data["type"] == "total_prestations":
                values["isDebit"]=u"D"
                values["libelle"]=data["libelle"]
                values["date_ecriture"]=dictParametres["date_fin"].strftime("%Y%m%d")
                values["journal"]=dictParametres["journal_ventes"]
                values["compte"] = dictParametres["code_clients"]   #+

            elif data["type"] == "prestation":
                values["isDebit"]=u"C"
                values["libelle"]=data["intitule"]
                values["compte"] = data["code_compta"]
                values["journal"]=dictParametres["journal_ventes"]
                values["date_ecriture"]=dictParametres["date_fin"].strftime("%Y%m%d")                

            elif data["type"] == "depot":
                values["isDebit"]=u"D"
                values["date_ecriture"]=data["date_depot"].strftime("%Y%m%d")
                values["journal"]=dictParametres["journal_%s" % typeComptable]
                values["compte"]=data["code_compta"] #+
                values["libelle"] = data["libelle"]

            elif data["type"] == "total_reglements":
                values["isDebit"]=u"C"
                values["date_ecriture"]=dictParametres["date_fin"].strftime("%Y%m%d")
                values["journal"]=dictParametres["journal_%s" % typeComptable]
                values["compte"]=dictParametres["code_clients"]
                values["libelle"] = data["libelle"]

            elif data["type"] == "total_mode":
                values["isDebit"]=u"D"
                values["date_ecriture"]=dictParametres["date_fin"].strftime("%Y%m%d")
                values["journal"]=dictParametres["journal_%s" % typeComptable]
                values["compte"] = data["code_compta"]
                values["libelle"] = data["libelle"]
                values["code_analyt"]=data["code_compta"]

        # Si aucun type n'est renseigné, il y a un probléme
        else:
            raise ValueError("'type' not in data")

        # Convertit toutes les données
        for i in list(dataTypes.keys()):
            # Si la donnée a bien été fournie, on la convertit
            if i in values:
                self.values[i]=dataTypes[i].convert(values[i])
            # Sinon on remplit de blanc, pour respecter la largeur des colonnes
            else:
                self.values[i]=dataTypes[i].convert("")

    def __getattr__(self,name):
        """
        gére l'acces aux attributs, pour plus de souplesse, les attributs inconnus renvoient None
        """
        if name in self.values:
            return self.values[name]
        else:
            return None

    def __str__(self):
        """
        Renvois la liste des donnée et leur valeur (appelé lors d'un print ou d'une convertion str)
        """
        return "LigneXImport : \n\t"+\
               "num_mvnt :" + six.text_type(self.num_mvnt)+"\n\t"+\
               "journal :" + six.text_type(self.journal)+"\n\t"+\
               "date_ecriture :" + six.text_type(self.date_ecriture)+"\n\t"+\
               "date_echeance :" + six.text_type(self.date_echeance)+"\n\t"+\
               "num_piece :" + six.text_type(self.num_piece)+"\n\t"+\
               "compte :" + six.text_type(self.compte)+"\n\t"+\
               "libelle :" + six.text_type(self.libelle)+"\n\t"+\
               "montant :" + six.text_type(self.montant)+"\n\t"+\
               "isDebit :" + six.text_type(self.isDebit)+"\n\t"+\
               "numPointage :" + six.text_type(self.numPointage)+"\n\t"+\
               "code_analyt :" + six.text_type(self.code_analyt)+"\n\t"+\
               "libelle_compte :" + six.text_type(self.libelle_compte)+"\n\t"+\
               "devise :" + six.text_type(self.devise)+"\n"
    
    def getData(self):
        """
        Retourne la ligne telle qu'elle doit être enregistré dans le fichier XImport
        """
        return six.text_type(self.num_mvnt)+\
                six.text_type(self.journal)+\
                six.text_type(self.date_ecriture)+\
                six.text_type(self.date_echeance)+\
                six.text_type(self.num_piece)+\
                six.text_type(self.compte)+\
                six.text_type(self.libelle)+\
                six.text_type(self.montant)+\
                six.text_type(self.isDebit)+\
                six.text_type(self.numPointage)+\
                six.text_type(self.code_analyt)+\
                six.text_type(self.libelle_compte)+\
                six.text_type(self.devise)

