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
from UTILS_Traduction import _
import wx
from Crypto.Hash import SHA256
import GestionDB


def GetListeUtilisateurs(nomFichier=""):
    """ Récupère la liste des utilisateurs et de leurs droits """
    DB = GestionDB.DB(nomFichier=nomFichier)

    # Droits
    req = """SELECT IDdroit, IDutilisateur, IDmodele, categorie, action, etat
    FROM droits;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    dictDroitsUtilisateurs = {}
    dictDroitsModeles = {}
    for IDdroit, IDutilisateur, IDmodele, categorie, action, etat in listeDonnees :
        key = (categorie, action)
        if IDutilisateur != None :
            if dictDroitsUtilisateurs.has_key(IDutilisateur) == False :
                dictDroitsUtilisateurs[IDutilisateur] = {}
            dictDroitsUtilisateurs[IDutilisateur][key] = etat
        if IDmodele != None :
            if dictDroitsModeles.has_key(IDmodele) == False :
                dictDroitsModeles[IDmodele] = {}
            dictDroitsModeles[IDmodele][key] = etat

    # Utilisateurs
    req = """SELECT IDutilisateur, sexe, nom, prenom, mdp, profil, actif
    FROM utilisateurs
    WHERE actif=1;"""
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    listeUtilisateurs = []
    
    # chargement avatars
    try :
        req = """SELECT IDutilisateur, image
        FROM utilisateurs;"""
        DB.ExecuterReq(req)
        listeAvatars = DB.ResultatReq()
    except :
        pass
    dictAvatars = {}
    for IDutilisateur, image in listeAvatars :
        dictAvatars[IDutilisateur] = image

    for IDutilisateur, sexe, nom, prenom, mdp, profil, actif in listeDonnees :
        droits = None
        if profil.startswith("administrateur") : 
            droits = None
        if profil.startswith("modele") :
            IDmodele = int(profil.split(":")[1])
            if dictDroitsModeles.has_key(IDmodele) :
                droits = dictDroitsModeles[IDmodele]
        if profil.startswith("perso") :
            if dictDroitsUtilisateurs.has_key(IDutilisateur) :
                droits = dictDroitsUtilisateurs[IDutilisateur]
        
        # Avatar
        if dictAvatars.has_key(IDutilisateur) :
            image = dictAvatars[IDutilisateur]
        else :
            image = "Automatique"

        # mdp
        if len(mdp) < 60 :
            mdp = SHA256.new(mdp.encode('utf-8')).hexdigest()

        dictTemp = { "IDutilisateur":IDutilisateur, "nom":nom, "prenom":prenom, "sexe":sexe, "mdp":mdp, "profil":profil, "actif":actif, "image":image, "droits":droits }
        listeUtilisateurs.append(dictTemp)
    
    DB.Close()
    return listeUtilisateurs


def VerificationDroits(dictUtilisateur=None, categorie="", action="", IDactivite=""):
    """ Vérifie si un utilisateur peut accéder à une action """
    if dictUtilisateur == None or dictUtilisateur.has_key("droits") == False :
        return True
    
    dictDroits = dictUtilisateur["droits"]
    key = (categorie, action)
        
    if dictDroits != None and dictDroits.has_key(key) :
        etat = dictDroits[key]
        # Autorisation
        if etat.startswith("autorisation") :
            return True
        # Interdiction
        if etat.startswith("interdiction") :
            return False
        # Restriction
        if etat.startswith("restriction") :
            code = etat.replace("restriction_", "")
            mode, listeID = code.split(":")
            listeID = [int(x) for x in listeID.split(";")]
                        
            if mode == "groupes" :
                if len(listeID) == 1 : condition = "IDtype_groupe_activite=%d" % listeID[0]
                if len(listeID) >1 : condition = "IDtype_groupe_activite IN %s" % str(tuple(listeID))
                DB = GestionDB.DB()
                req = """SELECT IDgroupe_activite, activites 
                FROM groupes_activites
                WHERE %s;""" % condition
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                listeActivites = []
                for IDgroupe_activite, IDactivite_temp in listeDonnees :
                    listeActivites.append(IDactivite_temp)
                DB.Close()
                
            if mode == "activites" :
                listeActivites = listeID
            
            if IDactivite in listeActivites :
                return True
            else :                
                return False

    return True
    
def VerificationDroitsUtilisateurActuel(categorie="", action="", IDactivite="", afficheMessage=True):
    try :
        topWindow = wx.GetApp().GetTopWindow()
        nomWindow = topWindow.GetName()
    except :
        nomWindow = None
    if nomWindow == "general" : 
        # Si la frame 'General' est chargée, on y récupère le dict de config
        dictUtilisateur = topWindow.dictUtilisateur
        resultat = VerificationDroits(dictUtilisateur, categorie, action, IDactivite)
        if resultat == False and afficheMessage == True :
            AfficheDLGInterdiction() 
        return resultat
    return True
    
    
def AfficheDLGInterdiction():
    import wx.lib.dialogs as dialogs
    image = wx.Bitmap(Chemins.GetStaticPath("Images/32x32/Droits.png"), wx.BITMAP_TYPE_ANY)
    dlg = dialogs.MultiMessageDialog(None, _(u"Votre profil utilisateur ne vous permet pas d'accéder à cette fonctionnalité !"), caption=_(u"Accès non autorisé"), style=wx.ICON_ERROR | wx.OK, icon=image, btnLabels={wx.ID_OK : _(u"Ok")})
    dlg.ShowModal() 
    dlg.Destroy() 
    

            
if __name__ == '__main__':
    listeUtilisateurs = GetListeUtilisateurs() 
    print VerificationDroits(listeUtilisateurs[0], "parametrage_modes_reglements", "supprimer")
    print VerificationDroitsUtilisateurActuel("parametrage_modes_reglements", "supprimer")