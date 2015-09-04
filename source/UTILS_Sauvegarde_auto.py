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
import wx
import CTRL_Bouton_image
import datetime
import time
import socket
import os
import glob
import random
import wx.lib.dialogs as dialogs

import GestionDB
import UTILS_Sauvegarde
from UTILS_Divers import ConvertChaineEnListe, ConvertListeEnChaine
import UTILS_Dates
import UTILS_Identification
import UTILS_Parametres


class Sauvegarde_auto():
    def __init__(self, parent=None):
        self.parent = parent
        
        # Importations
        self.listeSauvegardes = self.Importation() 
        self.listeVacances = self.GetListeVacances() 
                    

    def Start(self):
        # Annonce rappel de sauvegarde auto
        if len(self.listeSauvegardes) == 0 :
            resultat = self.AnnonceRappel()
            return resultat

        # Lancement des sauvegardes
        for dictSauvegarde in self.listeSauvegardes :
            valide = True
            resultat = False
            
            # Création du nom de la sauvegarde
            prefixe = dictSauvegarde["sauvegarde_nom"]
            dictSauvegarde["sauvegarde_nom"] = u"%s_%s" % (dictSauvegarde["sauvegarde_nom"], datetime.datetime.now().strftime("%Y%m%d_%H%M"))
                        
            # Vérification des conditions
            if valide == True :
                valide = self.VerificationConditions(dictSauvegarde) 

            # Demande de confirmation
            if valide == True and dictSauvegarde["option_demander"] == "1" :
                image = wx.Bitmap("Images/48x48/Sauvegarder.png", wx.BITMAP_TYPE_ANY)
                message1 = _(u"Souhaitez-vous lancer la procédure de sauvegarde '%s' ?") % dictSauvegarde["nom"]
                dlg = dialogs.MultiMessageDialog(self.parent, message1, caption=_(u"Sauvegarde automatique"), msg2=None, style = wx.NO | wx.CANCEL | wx.YES | wx.YES_DEFAULT, icon=image, btnLabels={wx.ID_YES : _(u"Oui"), wx.ID_NO : _(u"Non"), wx.ID_CANCEL : _(u"Annuler")})
                reponse = dlg.ShowModal() 
                try :
                    dlg.Destroy() 
                except :
                    pass
                if reponse == wx.ID_NO :
                    valide = False
                if reponse == wx.ID_CANCEL :
                    return wx.ID_CANCEL

            # Afficher interface
            if valide == True and dictSauvegarde["option_afficher_interface"] == "1" :
                import DLG_Sauvegarde
                dlg = DLG_Sauvegarde.Dialog(self.parent, dictDonnees=dictSauvegarde)
                dlg.ShowModal() 
                resultat = dlg.GetResultat()
                dlg.Destroy()
            
            # Sauvegarde
            if valide == True and dictSauvegarde["option_afficher_interface"] != "1" :
                resultat = self.Sauvegarde(dictSauvegarde)
                
                if resultat == True and dictSauvegarde["option_confirmation"] == "1" :
                    dlg = wx.MessageDialog(self.parent, _(u"La procédure de sauvegarde '%s' s'est terminée avec succès.") % dictSauvegarde["nom"], _(u"Sauvegarde"), wx.OK | wx.ICON_INFORMATION)
                    dlg.ShowModal()
                    dlg.Destroy()

                if resultat == False :
                    dlg = wx.MessageDialog(self.parent, _(u"Echec de la procédure de sauvegarde '%s' !") % dictSauvegarde["nom"], _(u"Annulation"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return wx.ID_CANCEL

            # Sauvegarde de la date de la sauvegarde
            if resultat == True :
                DB = GestionDB.DB()
                DB.ReqMAJ("sauvegardes_auto", [("date_derniere", str(datetime.date.today())),], "IDsauvegarde", dictSauvegarde["IDsauvegarde"])
                DB.Close()
                
            # Suppression des sauvegardes obsolètes
            if dictSauvegarde["option_suppression"] != None and dictSauvegarde["sauvegarde_repertoire"] != None and os.path.isdir(dictSauvegarde["sauvegarde_repertoire"]) == True :
                nbreJours = int(dictSauvegarde["option_suppression"])
                repertoire = dictSauvegarde["sauvegarde_repertoire"]
                listeFichiersPresents = glob.glob(repertoire + "/*")
                for fichier in listeFichiersPresents :
                    nomFichier = os.path.basename(fichier)
                    if (fichier.endswith(".nod") or fichier.endswith(".noc")) and nomFichier.startswith(prefixe) :
                        dateCreationFichier = datetime.date.fromtimestamp(os.path.getctime(fichier))
                        nbreJoursFichier = (datetime.date.today() - dateCreationFichier).days
                        if nbreJoursFichier >= nbreJours :
                            os.remove(fichier)
                            
        return True       

    def GetListeVacances(self):
        DB = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        return listeDonnees

    def Importation(self):
        """ Importation des sauvegardes auto """
        listeChamps = [
            "IDsauvegarde", "nom", "observations", "date_derniere", 
            "sauvegarde_nom", "sauvegarde_motdepasse", "sauvegarde_repertoire", "sauvegarde_emails", "sauvegarde_fichiers_locaux", "sauvegarde_fichiers_reseau",
            "condition_jours_scolaires", "condition_jours_vacances", "condition_heure", "condition_poste", "condition_derniere", "condition_utilisateur",
            "option_afficher_interface", "option_demander", "option_suppression", "option_confirmation",
            ]
        DB = GestionDB.DB()
        req = """SELECT %s
        FROM sauvegardes_auto
        ;""" % ",".join(listeChamps)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        listeSauvegardes = []
        for sauvegarde in listeDonnees :
            dictTemp = {}
            index = 0
            for valeur in sauvegarde :
                dictTemp[listeChamps[index]] = valeur
                index += 1
            listeSauvegardes.append(dictTemp) 
        return listeSauvegardes

    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def VerificationConditions(self, dictSauvegarde={}):
        """ Vérifie si conditions de la procédure sont valides """
        jours_scolaires = dictSauvegarde["condition_jours_scolaires"] 
        jours_vacances = dictSauvegarde["condition_jours_vacances"]
        heures = dictSauvegarde["condition_heure"]
        poste = dictSauvegarde["condition_poste"]
        derniere = dictSauvegarde["condition_derniere"]
        utilisateur = dictSauvegarde["condition_utilisateur"]
        
        dateDuJour = datetime.date.today()
        
        # Jour
        if jours_scolaires != None or jours_vacances != None :
            jours_scolaires = ConvertChaineEnListe(jours_scolaires)
            jours_vacances = ConvertChaineEnListe(jours_vacances)
            valide = False
            if jours_scolaires != None :
                if self.EstEnVacances(dateDuJour) == False :
                    if dateDuJour.weekday() in jours_scolaires :
                        valide = True
            if jours_vacances != None :
                if self.EstEnVacances(dateDuJour) == True :
                    if dateDuJour.weekday() in jours_vacances :
                        valide = True
            if valide == False :
                return False
        
        # Heure
        if heures != None :
            heureActuelle = time.strftime('%H:%M', time.localtime()) 
            heure_min, heure_max = heures.split(";")
            if heureActuelle < heure_min or heureActuelle > heure_max :
                return False
        
        # Poste
        if poste != None :
            listePostes = poste.split(";")
            if socket.gethostname() not in listePostes :
                return False
            
        # Dernière sauvegarde
        if derniere != None :
            date_derniere = dictSauvegarde["date_derniere"]
            if date_derniere != None : 
                date_derniere = UTILS_Dates.DateEngEnDateDD(date_derniere)
                nbreJours = (dateDuJour - date_derniere).days
                if nbreJours < int(derniere) :
                    return False
            
        # Utilisateur
        if utilisateur != None :
            listeUtilisateurs = ConvertChaineEnListe(utilisateur)
            IDutilisateur = UTILS_Identification.GetIDutilisateur()
            if IDutilisateur not in listeUtilisateurs :
                return False
            
        return True
        
        
        
    def Sauvegarde(self, dictSauvegarde={}):
        """ Lancement de la sauvegarde """
        listeFichiersLocaux = dictSauvegarde["sauvegarde_fichiers_locaux"]
        listeFichiersReseau = dictSauvegarde["sauvegarde_fichiers_reseau"]
        nom = dictSauvegarde["sauvegarde_nom"]
        repertoire = dictSauvegarde["sauvegarde_repertoire"]
        motdepasse = dictSauvegarde["sauvegarde_motdepasse"]
        listeEmails = dictSauvegarde["sauvegarde_emails"]
        
        # Fichiers locaux
        if listeFichiersLocaux == None :
            listeFichiersLocaux = []
        else :
            listeFichiersLocaux = listeFichiersLocaux.split(";")
        
        # Fichiers réseau
        dictConnexion = None
        if listeFichiersReseau == None :
            listeFichiersReseau = []
        else :
            listeFichiersReseau = listeFichiersReseau.split(";")
            DB = GestionDB.DB() 
            if DB.echec != 1 :
                if DB.isNetwork == True :
                    dictConnexion = DB.GetParamConnexionReseau() 
            DB.Close() 
            
            if dictConnexion == None :
                dictConnexion = self.GetDictConnexion()
                if dictConnexion == False :
                    return False
            
        # Liste Emails
        if listeEmails != None :
            listeEmails = listeEmails.split(";")
        
        # Sauvegarde
        resultat = UTILS_Sauvegarde.Sauvegarde(listeFichiersLocaux, listeFichiersReseau, nom, repertoire, motdepasse, listeEmails, dictConnexion)
        if resultat == False :
            return False
        return True

    def GetDictConnexion(self):
        # Demande les paramètres de connexion
        import DLG_Saisie_param_reseau
        intro = _(u"Pour accéder à la liste des fichiers réseau disponibles, un accès MySQL \nest nécessaire. Veuillez saisir vos paramètres de connexion réseau :")
        dlg = DLG_Saisie_param_reseau.Dialog(self.parent, intro=intro)
        if dlg.ShowModal() == wx.ID_OK:
            dictValeurs = dlg.GetDictValeurs()
            dlg.Destroy()
        else:
            dlg.Destroy()
            return False
        # Vérifie si la connexion est bonne
        resultat = DLG_Saisie_param_reseau.TestConnexion(dictValeurs)
        if resultat == False :
            dlg = wx.MessageDialog(self.parent, _(u"Echec du test de connexion.\n\nLes paramètres ne semblent pas exacts !"), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        return dictValeurs


    def AnnonceRappel(self):
        # Affichage à 70 % de chance
        if random.randrange(1, 100) > 70 :
            return False
        
        # Vérifie si case Ne plus Afficher cochée ou non
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="sauvegarde_automatique", valeur=False) == True :
            return False
        
        try :
            image = wx.Bitmap("Images/48x48/Sauvegarder.png", wx.BITMAP_TYPE_ANY)
            message1 = _(u"Vous n'avez paramétré aucune sauvegarde automatique.\n\nSouhaitez-vous le faire maintenant ?")
            dlg = dialogs.MultiMessageDialog(self.parent, message1, caption=_(u"Rappel de sauvegarde"), msg2=None, style = wx.NO | wx.CANCEL | wx.YES | wx.YES_DEFAULT, icon=image, btnLabels={wx.ID_YES : _(u"Oui"), wx.ID_NO : _(u"Ne plus rappeler"), wx.ID_CANCEL : _(u"Pas maintenant")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
        except :
            reponse = None
        if reponse == wx.ID_YES :
            import DLG_Sauvegardes_auto
            dlg = DLG_Sauvegardes_auto.Dialog(self.parent)
            dlg.ShowModal() 
            dlg.Destroy()
            return wx.ID_CANCEL
        if reponse == wx.ID_NO :
            UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="sauvegarde_automatique", valeur=True)
        if reponse == wx.ID_CANCEL :
            return True

        return True
    
    
    
    
    

if __name__ == u"__main__":
    app = wx.App(0)
    save = Sauvegarde_auto()
    save.Start() 
    app.MainLoop()
