#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
try :
    import pyttsx
except :
    pass
import GestionDB
import UTILS_Parametres
import UTILS_Config


class Vocal() :
    def __init__(self):
        self.echec = False
        self.defaut = None
        try :
            self.engine = pyttsx.init() 
        except Exception, err: 
            print "Erreur dans l'initialisation de la synthese vocale :", err
            self.echec = True
        
        if self.echec == False :
            
            # Récupère la voix par défaut
            self.defaut = UTILS_Config.GetParametre("vocal_voix", defaut=self.engine.getProperty("voice"))
            
            # Sélection de la voix
            for voice in self.GetListeVoix()  :
                if voice.id == self.defaut :
                    self.engine.setProperty('voice', voice.id)

            # Règle la vitesse
            self.engine.setProperty("rate", 150)
            
            # Importation des corrections phoniques
            self.InitCorrections() 
    
    def InitCorrections(self):
        self.dictCorrections = self.ImportationCorrections() 
    
    def ImportationCorrections(self):
        DB = GestionDB.DB()
        req = """SELECT mot, correction
        FROM corrections_phoniques;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictCorrections = {}
        for mot, correction in listeDonnees :
            dictCorrections[mot] = correction
        return dictCorrections
    
    def GetListeVoix(self):
        if self.echec == True :
            return []
        listeVoix = []
        for voice in self.engine.getProperty("voices"):
            listeVoix.append(voice)
        return listeVoix
    
    def VerifieSiVirginieInstallee(self):
        if self.echec == True :
            return True
        for voice in self.GetListeVoix() :
            if "Virginie" in voice.name :
                return True
        return False
    
    def VerifieSiVirginieDefaut(self):
        if "Virginie" in self.defaut :
            return True
        else :
            return False
    
    def GetVoixActuelle(self):
        """ Retourne l'ID de la voix actuelle """
        return self.defaut
    
    def SetVoixActuelle(self, id=None):
        """ Mémorise la voix actuelle """
##        UTILS_Parametres.Parametres(mode="set", categorie="vocal", nom="voix", valeur=id)
        UTILS_Config.SetParametre("vocal_voix", id)
        self.engine.setProperty('voice', id)
        self.defaut = id
    
    def Parle(self, texte=u""):
        if self.echec == True :
            return
        # Recherche de corrections
        for mot, correction in self.dictCorrections.iteritems() :
            if mot.lower() in texte.lower() :
                texte = texte.replace(mot, correction)
        # Parle
        self.engine.say(texte)
        try :
            self.engine.runAndWait() 
        except :
            pass






if __name__ == "__main__":
    vocal = Vocal() 
    vocal.Parle(_(u"Bonjour Kévin"))
