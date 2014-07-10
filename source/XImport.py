# -*- coding: utf-8 -*-
"""
Ce module permet la conversion des donnée d'export vers un fichier XImport pour l'utilisation avec CIEL Compta
"""


import os

class DataType(object):
    """
    Classe permetant la conversion facile vers le format souhaité (nombre de caractéres, alignement, décimales)
    """

    def __init__(self,type=int,length=1,align="<",precision=2):
        """
        initialise l'objet avec les paramétres souhaité
        """
        self.type = type
        self.length = length
        self.align = align
        self.precision = precision

    def convert(self,data):
        """
        convertis la donnée fournie dans le format souhaité
        """
        ret_val = ""

        if type(data) is str:                       #s'assure que la donnée soit bien en unicode
            data=unicode(data.decode("iso-8859-15"))

        if self.type == int:                        #si l'on veux des entier
            if data!="":
                try:                                #on vérifie qu'il s'agit bien d'un nombre
                    data=int(data)
                except ValueError as e:
                    print("/!\ Erreur de format, impossible de convertir en int /!\\")
                    print(e)
                    data=0
                ret_val = u"{0: {align}0{length}d}".format(data,align=self.align,length=self.length)
            else:
                ret_val = u"{0: {align}0{length}s}".format(data,align=self.align,length=self.length)
        elif self.type == str:                      #si l'on veux des chaines de caractéres
            data = data.replace("\"","")
            ret_val = u"{0: {align}0{length}s}".format(data,align=self.align,length=self.length)
        
        elif self.type == float:                    #si l'on veux un nombre a virgule
            if data!="":
                try:
                    data=float(data)                #on vérifie qu'il s'agit bien d'un nombre
                except ValueError as e:
                    print("/!\ Erreur de format, impossible de convertir en float /!\\")
                    print(e)
                    data=0
                ret_val = u"{0: {align}0{length}.{precision}f}".format(data,align=self.align,length=self.length,precision=self.precision)
            else:
                ret_val = u"{0: {align}0{length}s}".format(data,align=self.align,length=self.length)

        if len(ret_val)>self.length:                #on tronc si la chaine est trop longue
            ret_val=ret_val[:self.length]
        return ret_val

#définition des differents formats souhaité pour les différentes données
# dataTypes = {"num_mvnt":DataType(int,5,">"),
#              "journal":DataType(str,2,"<"),
#              "date_ecriture":DataType(int,8,">"),
#              "date_echeance":DataType(int,8,">"),
#              "num_piece":DataType(str,12,"<"),
#              "compte":DataType(str,11,"<"),
#              "libelle":DataType(str,25,"<"),
#              "montant":DataType(float,13,">"),
#              "isDebit":DataType(str,1,"<"),
#              "numPointage":DataType(str,12,"<"),
#              "code_analyt":DataType(str,6,"<"),
#              "libelle_compte":DataType(str,34,"<"),
#              "devise":DataType(str,1,"<")}

dataTypes = {"num_mvnt":DataType(int,10,">"),
             "journal":DataType(str,6,"<"),
             "date_ecriture":DataType(int,8,">"),
             "date_echeance":DataType(int,8,">"),
             "num_piece":DataType(str,15,"<"),
             "compte":DataType(str,13,"<"),
             "libelle":DataType(str,50,"<"),
             "montant":DataType(float,13,">"),
             "isDebit":DataType(str,1,"<"),
             "numPointage":DataType(str,15,"<"),
             "code_analyt":DataType(str,13,"<"),
             "libelle_compte":DataType(str,35,"<"),
             "devise":DataType(str,1,"<")}


class XImportLine(object):
    """
    Définie une ligne telle que formaté dans un fichier XImport
    """

    def __init__(self,data,dictParametres,num_ligne,typeComptable=None):
        """
        Récupére les donnée utiles fournis en paramétres, les convertis et les enregistre 
        """

        values = dict()         #contient les valeurs fournies et non converties
        self.values = dict()    #contiendra les valeurs convertie

        values["num_mvnt"]=num_ligne #le numéro de mouvement est le numéro de la ligne ?           

        values["montant"]=data["montant"] 
        values["devise"]=u"€"

        if "type" in data:                  #on récupére ce qui nous interesse selon le type de donnée
            if data["type"] == "facture":
                values["isDebit"]=u"D"
                values["journal"]=dictParametres["journal_ventes"]
                values["date_ecriture"]=data["date_edition"].strftime("%Y%m%d")
                if data["date_echeance"]:
                    values["date_echeance"]=data["date_echeance"].strftime("%Y%m%d")
                else:
                    values["date_echeance"]=""
                values["libelle"]=data["libelle_facture"]
                if data["code_comptable_famille"]:
                    values["code_analyt"]=data["code_comptable_famille"]
                else:
                    values["code_analyt"]=dictParametres["code_clients"]

                #Valeurs fournies non utilisées :                
                #    'numero': 1
                #    'date_fin': datetime.date(2014, 12, 31)
                #    'date_debut': datetime.date(2014, 1, 1)
                #    'IDfacture': 3
                #    'famille': u'DUPONT Jean'

            elif data["type"] == "prestation":
                values["isDebit"]=u"C"
                values["journal"]=dictParametres["journal_ventes"]
                values["date_ecriture"]=data["date_facture"].strftime("%Y%m%d")
                if data["date_echeance"]:
                    values["date_echeance"]=data["date_echeance"].strftime("%Y%m%d")
                else:
                    values["date_echeance"]=""
                values["libelle"]=data["libelle_prestation"]
                values["code_analyt"]=data["code_compta"]

                #Valeurs fournies non utilisées :                
                #    'intituleTemp': u'Rand - Journ\xe9e'
                #    'individu_nom': u'DUPONT'
                #    'date_prestation': datetime.date(2014, 6, 21)
                #    'individu_prenom': u'Jean'
                #    'numero_facture': 1
                #    'libelle_original': u'Journ\xe9e'
            
            elif data["type"] == "depot":
                values["isDebit"]=u"D"
                values["journal"]=dictParametres["journal_%s" % typeComptable]
                values["date_ecriture"]=data["date_depot"].strftime("%Y%m%d")
                values["compte"] = data["numeroCompte"]
                values["libelle_compte"] = data["nomCompte"]
                values["libelle"] = data["libelle_depot"]

                #Valeurs fournies non utilisées :                
                #    'IDdepot': 4
                #    'nom_depot': u'test_depot_4'
                #    'mode_reglement': u'Ch\xe9que vacances'
            
            elif data["type"] == "reglement":
                values["isDebit"]=u"C"
                values["journal"]=dictParametres["journal_%s" % typeComptable]
                values["date_ecriture"]=data["date_depot"].strftime("%Y%m%d")
                values["num_piece"]=data["numero_piece"]
                values["libelle"] = data["libelle_reglement"]
                values["compte"] = data["numeroCompte"]
                values["libelle_compte"] = data["nomCompte"]

                #Valeurs fournies non utilisées :                
                #    'attente': 0
                #    'nom_depot': u'test_depot_4'
                #    'IDreglement': 7
                #    'nomPayeur': u'DUPONT Jean'
                #    'nomFamille': u'DUPONT Jean'
                #    'numero_quittancier': u''
                #    'dateReglement': datetime.date(2014, 6, 18)
                #    'date_differe': None
                #    'IDmode': 3
                #    'labelMode': u'Ch\xe9que vacances'
        
        else:       #Si aucun type n'est renseigné, il y a un probléme
            raise ValueError("'type' not in data")

        #Valeur manquante : num_pointage
        #valeur incertaines : num_mvnt est-il bien le numero de ligne ?
            
        
        for i in dataTypes.keys():  #Convertie toutes les donnée
            if i in values:         #Si la donnée a bien été fournie, on la converti 
                self.values[i]=dataTypes[i].convert(values[i])
            else:                   #Sinon on remplis de blanc, pour respecter la largeur des colones
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
               "num_mvnt :"+unicode(self.num_mvnt)+"\n\t"+\
               "journal :"+unicode(self.journal)+"\n\t"+\
               "date_ecriture :"+unicode(self.date_ecriture)+"\n\t"+\
               "date_echeance :"+unicode(self.date_echeance)+"\n\t"+\
               "num_piece :"+unicode(self.num_piece)+"\n\t"+\
               "compte :"+unicode(self.compte)+"\n\t"+\
               "libelle :"+unicode(self.libelle)+"\n\t"+\
               "montant :"+unicode(self.montant)+"\n\t"+\
               "isDebit :"+unicode(self.isDebit)+"\n\t"+\
               "numPointage :"+unicode(self.numPointage)+"\n\t"+\
               "code_analyt :"+unicode(self.code_analyt)+"\n\t"+\
               "libelle_compte :"+unicode(self.libelle_compte)+"\n\t"+\
               "devise :"+unicode(self.devise)+"\n"
    
    def getData(self):
        """
        Retourne la ligne telle qu'elle doit être enregistré dans le fichier XImport
        """
        return unicode(self.num_mvnt)+\
                unicode(self.journal)+\
                unicode(self.date_ecriture)+\
                unicode(self.date_echeance)+\
                unicode(self.num_piece)+\
                unicode(self.compte)+\
                unicode(self.libelle)+\
                unicode(self.montant)+\
                unicode(self.isDebit)+\
                unicode(self.numPointage)+\
                unicode(self.code_analyt)+\
                unicode(self.libelle_compte)+\
                unicode(self.devise)


