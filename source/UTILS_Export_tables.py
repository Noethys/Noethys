#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import shelve
import os
import cStringIO
import GestionDB
import wx.lib.agw.pybusyinfo as PBI

def InfosFichier(fichier=""):
    """ Récupère les infos principales sur un fichier """
    if os.path.isfile(fichier) == False :
        print "Pas de fichier a cet emplacement !"
        return None
    dictInfos = {}
    fichier = shelve.open(fichier.encode("iso-8859-15"), "r")
    for key, valeur in fichier.iteritems() :
        dictInfos[key] = valeur
    fichier.close()
    return dictInfos



class Exporter():
    def __init__(self, categorie="activite"):
        self.categorie = categorie
        self.contenu = []
        
    def Ajouter(self, ID=None, nom=""):
        self.listeTables = []
        self.DB = GestionDB.DB()
        self.dictID = {}
        self.Exporter(ID)
        self.contenu.append({
            "nom" : nom,
            "tables" : self.listeTables,
            })
        self.DB.Close()
                
    def GetListeChamps(self, nomTable=''):
        """ Récupération des champs de la table """
        listeColonnes = self.DB.GetListeChamps2(nomTable)
        listeChamps = []
        for nomChamp, typeChamp in listeColonnes :
            listeChamps.append(nomChamp) 
        return listeChamps, listeColonnes
    
    def FormateCondition(self, nomChamp="", listeID=[]):
        if len(listeID) == 0 : sql = "%s IN ()" % nomChamp
        elif len(listeID) == 1 : sql = "%s=%d" % (nomChamp, listeID[0])
        else : sql = "%s IN %s" % (nomChamp, str(tuple(listeID)))
        return sql
        
    def Exporter(self, ID=None):
        """ Fonction à surcharger """
        self.ExporterTable("activites", "IDactivite=%d" % ID)
        self.ExporterTable("groupes", "IDactivite=%d" % ID)
        self.ExporterTable("agrements", "IDactivite=%d" % ID)
        # Unités
        self.ExporterTable("unites", "IDactivite=%d" % ID)
        self.ExporterTable("unites_groupes", self.FormateCondition("IDunite", self.dictID["unites"]))
        self.ExporterTable("unites_incompat", self.FormateCondition("IDunite", self.dictID["unites"]))
        # Unités de remplissage
        self.ExporterTable("unites_remplissage", "IDactivite=%d" % ID)
        self.ExporterTable("unites_remplissage_unites", self.FormateCondition("IDunite_remplissage", self.dictID["unites_remplissage"]))
        # Calendrier
        self.ExporterTable("ouvertures", "IDactivite=%d" % ID)
        self.ExporterTable("remplissage", "IDactivite=%d" % ID)
        # Tarifs
        self.ExporterTable("categories_tarifs", "IDactivite=%d" % ID)
        self.ExporterTable("noms_tarifs", "IDactivite=%d" % ID)
        self.ExporterTable("tarifs", "IDactivite=%d" % ID, [
                                                                                ("categories_tarifs", "IDcategorie_tarif", ";"),
                                                                                ("groupes", "IDgroupe", ";"),
                                                                                ("cotisations", None, ";"),
                                                                                ("caisses", None, ";"),
                                                                                ])
        self.ExporterTable("combi_tarifs", self.FormateCondition("IDtarif", self.dictID["tarifs"]))
        self.ExporterTable("combi_tarifs_unites", self.FormateCondition("IDtarif", self.dictID["tarifs"]))
        self.ExporterTable("tarifs_lignes", "IDactivite=%d" % ID)

    def ExporterTable(self, nomTable="", condition="", chainesListes=[], remplacement=None):
        """ Exporter une table donnée """
        listeChamps, listeColonnes = self.GetListeChamps(nomTable) 
        champCle = listeChamps[0]
        
        req = """SELECT %s
        FROM %s
        WHERE %s
        ;""" % (", ".join(listeChamps), nomTable, condition)
        self.DB.ExecuterReq(req)
        listeDonnees = self.DB.ResultatReq()
        
        listeID = []
        listeLignes = []
        for donnees in listeDonnees :
            indexColonne = 0
            dictLigne = {} 
            for donnee in donnees :
                nomChamp = listeColonnes[indexColonne][0]
                typeChamp = listeColonnes[indexColonne][1]
                
                # Mémorisation de l'ID de la ligne
                if nomChamp == champCle :
                    listeID.append(donnee)
                
                # Pour les champs BLOB
                if (typeChamp == "BLOB" or typeChamp == "LONGBLOB") and donnee != None :
                    buffer = cStringIO.StringIO(donnee)
                    donnee = buffer.read()
                
                # Remplacement
                if remplacement != None :
                    if remplacement[0] == nomChamp :
                        donnee = remplacement[1]
                    
                dictLigne[nomChamp] = donnee
                indexColonne += 1
            listeLignes.append(dictLigne)
            
        self.listeTables.append((nomTable, listeLignes, chainesListes))
        self.dictID[nomTable] = listeID
    
    def Enregistrer(self, fichier=""):
        # Enregistrement dans un fichier Shelve
        fichier = shelve.open(fichier.encode("iso-8859-15"), "n")
        fichier["categorie"] = self.categorie
        fichier["contenu"] = self.contenu
        fichier.close()
    
    def GetContenu(self):
        return self.contenu
    
# -----------------------------------------------------------------------------------------------------

class Importer():
    def __init__(self, fichier=None, contenu=None):
        self.fichier = fichier
        
        # Get Données
        if fichier != None :
            dictInfos = InfosFichier(self.fichier)
            self.categorie = dictInfos["categorie"]
            self.contenu = dictInfos["contenu"]
        else :
            self.categorie = ""
            self.contenu = contenu
    
    def DemandeChoix(self):
        listeContenu = self.GetNomContenu() 
        dlg = wx.MultiChoiceDialog(None, u"Sélectionnez le contenu à importer :", u"Importation", listeContenu)
        dlg.SetSelections(range(0, len(listeContenu)))
        if dlg.ShowModal() == wx.ID_OK :
            selections = dlg.GetSelections()
        else :
            selections = []
        dlg.Destroy()
        for index in selections :
            self.Ajouter(index)
        return len(selections)

    def GetNomContenu(self):
        listeNoms = []
        for importation in self.contenu :
            listeNoms.append(importation["nom"])
        return listeNoms
    
    def Ajouter(self, index=0):
        dlgAttente = PBI.PyBusyInfo(u"Merci de patienter durant l'opération...", parent=None, title=u"Patientez...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        # Importation
        self.dictID = {}
        self.DB = GestionDB.DB()
        importation = self.contenu[index]
        nom = importation["nom"]  
        listeTables = importation["tables"]  
        self.Importer(listeTables) 
        self.DB.Close()
        del dlgAttente

    def GetTypesChamps(self, nomTable=''):
        """ Récupération des types de champs de la table """
        listeColonnes = self.DB.GetListeChamps2(nomTable)
        dictChamps = {}
        for nomChamp, typeChamp in listeColonnes :
            dictChamps[nomChamp] = typeChamp
        champCle = listeColonnes[0][0]
        return dictChamps, champCle

    def Importer(self, listeTables=[]):
        """ Procédure d'importation """
        for nomTable, listeLignes, chainesListes in listeTables:
            self.ImporterTable(nomTable, listeLignes, chainesListes)
    
    def ImporterTable(self, nomTable="", listeLignes=[], chainesListes=[]):
        if len(listeLignes) == 0 : return
        
        # Récupère les types de champs
        dictTypesChamps, champCle = self.GetTypesChamps(nomTable)
        
        # Duplique les lignes
        for ligne in listeLignes :
            
            # Récupération des valeurs
            listeDonnees = []
            dictBlobs = {}
            ancienID = None
            for nomChamp, valeur in ligne.iteritems() :
                
                if dictTypesChamps.has_key(nomChamp) :
                    
                    if nomChamp == champCle :
                        ancienID = valeur
                    
                    # Blob
                    if "BLOB" in dictTypesChamps[nomChamp] and valeur != None :
                        dictBlobs[nomChamp] = valeur
                        valeur = None
                    
                    # Remplacement des ID avec le dict des correspondances
                    if self.dictID.has_key(nomChamp) :
                        if self.dictID[nomChamp].has_key(valeur) :
                            valeur = self.dictID[nomChamp][valeur]

                    # Chaîne de liste
                    for nomChampChaine, champRemplacement, separateur in chainesListes :
                        if nomChamp == nomChampChaine :
                            if valeur == None or champRemplacement == None :
                                valeur = None
                            else :
                                listeTemp = []
                                for chaine in valeur.split(separateur) :
                                    donnee = int(chaine)
                                    if self.dictID.has_key(champRemplacement) :
                                        if self.dictID[champRemplacement].has_key(donnee) :
                                            donnee = self.dictID[champRemplacement][donnee]
                                    listeTemp.append(str(donnee))
                                valeur = separateur.join(listeTemp)
                            
                    # Mémorisation des valeurs
                    if nomChamp != champCle :
                        listeDonnees.append((nomChamp, valeur))
                
            # Enregistrement
            newID = self.DB.ReqInsert(nomTable, listeDonnees)
                
            # Enregistrement des blobs à part
            for nomChampBlob, blob in dictBlobs.iteritems() :
                self.DB.MAJimage(table=nomTable, key=champCle, IDkey=newID, blobImage=blob, nomChampBlob=nomChampBlob)
            
            # Mémorisation de L'ID dans la table des correspondances
            if self.dictID.has_key(champCle) == False :
                self.dictID[champCle] = {}
            self.dictID[champCle][ancienID] = newID
            
        return newID
    
    def GetNewID(self, champCle="", ancienID=None):
        try :
            return self.dictID[champCle][ancienID]
        except :
            pass
        

if __name__ == "__main__":
    app = wx.App(0)
    
    print "Exportation..."
    exportation = Exporter(categorie="activite")
    exportation.Ajouter(ID=2, nom=u"Activité1")
    exportation.Enregistrer(fichier="Temp/test.npa")
    
    print "Importation..."
    importation = Importer(fichier="Temp/test.npa")
    importation.DemandeChoix() 
    #importation.Ajouter(index=0)
    print "Fin."
    