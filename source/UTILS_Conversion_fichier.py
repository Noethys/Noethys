#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import os
import GestionDB

try: import psyco; psyco.full() 
except: pass

# ------------------------------------ CONVERSION LOCAL -> RESEAU -------------------------------

def ConversionLocalReseau(parent, nomFichier=""):
    # Demande le nom du nouveau fichier réseau
    import DLG_Nouveau_fichier
    dlg = DLG_Nouveau_fichier.MyDialog(parent)
    dlg.SetTitle(_(u"Conversion d'un fichier local en fichier réseau"))
    dlg.radio_reseau.SetValue(True)
    dlg.OnRadioReseau(None)
    dlg.radio_local.Enable(False)
    dlg.radio_reseau.Enable(False)
    dlg.radio_internet.Enable(False)
    dlg.checkbox_details.Show(False)
    dlg.hyperlink_details.Show(False)
    dlg.DesactiveIdentite() 
    dlg.CentreOnScreen()
    if dlg.ShowModal() == wx.ID_OK:
        nouveauFichier = dlg.GetNomFichier()
        dlg.Destroy()
    else:
        dlg.Destroy()
        return False
    
    # Vérifie la validité du nouveau nom
    dictResultats = GestionDB.TestConnexionMySQL(typeTest="fichier", nomFichier="%s_DATA" % nouveauFichier)
    
    # Vérifie la connexion au réseau
    if dictResultats["connexion"][0] == False :
        erreur = dictResultats["connexion"][1]
        dlg = wx.MessageDialog(parent, _(u"La connexion au réseau MySQL est impossible. \n\nErreur : %s") % erreur, _(u"Erreur de connexion"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False
    
    # Vérifie que le fichier n'est pas déjà utilisé
    if dictResultats["fichier"][0] == True :
        dlg = wx.MessageDialog(parent, _(u"Le fichier existe déjà."), _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False
    
    # Récupère le nom du fichier local actuellement ouvert
    nouveauNom = nouveauFichier[nouveauFichier.index("[RESEAU]"):].replace("[RESEAU]", "")
    
    # Demande une confirmation pour la conversion
    message = _(u"Confirmez-vous la conversion du fichier local '%s' en fichier réseau portant le nom '%s' ? \n\nCette opération va durer quelques instants...\n\n(Notez que le fichier original sera toujours conservé)") % (nomFichier, nouveauNom)
    dlg = wx.MessageDialog(parent, message, _(u"Confirmation de la conversion"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES :
        dlg.Destroy()
    else:
        dlg.Destroy()
        return False
    
    # Lance la conversion
    parent.SetStatusText(_(u"Conversion du fichier en cours... Veuillez patienter..."))
    conversion = GestionDB.ConversionLocalReseau(nomFichier, nouveauFichier, parent)
    parent.SetStatusText(_(u"La conversion s'est terminée avec succès."))
    dlg = wx.MessageDialog(None, _(u"La conversion s'est terminée avec succès. Le nouveau fichier a été créé."), "Information", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    return True







# ----------------------------- CONVERSION RESEAU -> LOCAL -------------------------------

def ConversionReseauLocal(parent, nomFichier=""):
    # Demande le nom du nouveau fichier local
    import DLG_Nouveau_fichier
    dlg = DLG_Nouveau_fichier.MyDialog(parent)
    dlg.SetTitle(_(u"Conversion d'un fichier réseau en fichier local"))
    dlg.radio_local.SetValue(True)
    dlg.OnRadioLocal(None)
    dlg.radio_local.Enable(False)
    dlg.radio_reseau.Enable(False)
    dlg.radio_internet.Enable(False)
    dlg.checkbox_details.Show(False)
    dlg.hyperlink_details.Show(False)
    dlg.DesactiveIdentite() 
    dlg.CentreOnScreen()
    if dlg.ShowModal() == wx.ID_OK:
        nouveauFichier = dlg.GetNomFichier()
        dlg.Destroy()
    else:
        dlg.Destroy()
        return False
    
    # Vérifie que le fichier n'est pas déjà utilisé
    if os.path.isfile("Data/%s_DATA.dat" % nomFichier)  == True :
        dlg = wx.MessageDialog(parent, _(u"Le fichier existe déjà."), _(u"Erreur de création de fichier"), wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()
        return False

    nomFichierReseauFormate = nomFichier[nomFichier.index("[RESEAU]"):].replace("[RESEAU]", "")
    
    # Demande une confirmation pour la conversion
    message = _(u"Confirmez-vous la conversion du fichier réseau '%s' en fichier local portant le nom '%s' ? \n\nCette opération va durer quelques instants...\n\n(Notez que le fichier original sera toujours conservé)") % (nomFichierReseauFormate, nouveauFichier)
    dlg = wx.MessageDialog(parent, message, _(u"Confirmation de la conversion"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
    if dlg.ShowModal() == wx.ID_YES :
        dlg.Destroy()
    else:
        dlg.Destroy()
        return False
    
    # Lance la conversion
    parent.SetStatusText(_(u"Conversion du fichier en cours... Veuillez patienter..."))
    conversion = GestionDB.ConversionReseauLocal(nomFichier, nouveauFichier, parent)
    parent.SetStatusText(_(u"La conversion s'est terminée avec succès."))
    dlg = wx.MessageDialog(None, _(u"La conversion s'est terminée avec succès. Le nouveau fichier a été créé."), "Information", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()
    return True

