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
import UTILS_Config
import UTILS_Financement
import webbrowser


def Aide(page=None):
    """ Ouverture de l'aide dans le navigateur """
    # None -> Renvoie vers le sommaire
    # "" -> Rubrique non disponible
    
    # Temporaire :
##    dlg = wx.MessageDialog(None, _(u"Le manuel de l'utilisateur sera disponible à partir de septembre 2013.\n\nPour obtenir de l'aide, vous pouvez déjà :\n\n   > Télécharger le guide de démarrage rapide\n   > Consulter le forum d'entraide\n   > Visionner les tutoriels vidéos"), _(u"Aide indisponible"), wx.OK | wx.ICON_INFORMATION)
##    dlg.ShowModal()
##    dlg.Destroy()
##    return
    
    
    # Récupération des codes de la licence
    identifiant = UTILS_Config.GetParametre("enregistrement_identifiant", defaut=None)
    code = UTILS_Config.GetParametre("enregistrement_code", defaut=None)
    
    # Redirection si aucune licence
    if identifiant == None and code == None :
        dlg = UTILS_Financement.DLG_Financement(None)
        dlg.ShowModal() 
        dlg.Destroy()
        return

    # Si aucune aide existe, propose de renvoyer vers le sommaire
    if page == "" :
        dlg = wx.MessageDialog(None, _(u"Cette rubrique d'aide n'est pas encore disponible.\n\nSouhaitez-vous être redirigé vers le sommaire de l'aide ?"), _(u"Pas de rubrique disponible"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return

    # Création de l'URL
    listeOptions = []
    
    if identifiant != None and code != None :
        listeOptions.append("identifiant=%s" % identifiant)
        listeOptions.append("code=%s" % code)
        
    if page != None and page != "" :
        listeOptions.append("page=%s.php" % page)
        
    url = "http://www.noethys.com/aide/html/identification.php"
    if len(listeOptions) > 0 :
        url += "?" + "&".join(listeOptions)
        
    # Ouverture du navigateur
    webbrowser.open(url)

    
if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    Aide() #("Licence")

    app.MainLoop()
