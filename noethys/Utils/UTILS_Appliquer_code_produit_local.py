#!/usr/bin/env python
# -*- coding: utf8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import GestionDB
from Dlg import DLG_Selection_dates


def Appliquer():
    """ Applique un code produit local à un lot de prestations """
    # Demande la période de dates
    dlg = DLG_Selection_dates.Dialog(None)
    if dlg.ShowModal() == wx.ID_OK:
        date_debut = dlg.GetDateDebut() 
        date_fin = dlg.GetDateFin() 
        dlg.Destroy()
    else :
        dlg.Destroy()
        return
    
    # Demande les prestations à modifier
    DB = GestionDB.DB()
    req = """SELECT IDprestation, label, activites.nom
    FROM prestations 
    LEFT JOIN activites ON activites.IDactivite = prestations.IDactivite
    WHERE date>='%s' AND date<='%s';
    """ % (date_debut, date_fin)
    DB.ExecuterReq(req)
    listeDonnees = DB.ResultatReq()
    DB.Close() 
    dictPrestations = {}
    for IDprestation, label, nomActivite in listeDonnees :
        if nomActivite == None :
            label = u"%s" % label
        else :
            label = u"%s (%s)" % (label, nomActivite)
        if (label in dictPrestations) == False :
            dictPrestations[label] = []
        dictPrestations[label].append(IDprestation)
    
    dlg = wx.MultiChoiceDialog(None, _(u"Sélectionnez les prestations à modifier :"), _(u"Selection des prestations"), list(dictPrestations.keys()))
    dlg.SetSize((500, 400))
    if dlg.ShowModal() == wx.ID_OK :
        selections = dlg.GetSelections()
        selectionsLabels = [list(dictPrestations.keys())[x] for x in selections]
        dlg.Destroy()
    else :
        dlg.Destroy()
        return

    # Choix du code produit local
    dlg = wx.TextEntryDialog(None, _(u"Quel code produit local souhaitez-vous appliquer ?"), _(u"Sélection d'un code produit local"), "")
    if dlg.ShowModal() == wx.ID_OK:
        code_produit_local = dlg.GetValue()
        dlg.Destroy()
    else :
        dlg.Destroy()
        return
    
    # Demande de confirmation
    nbrePrestations = 0
    for label in selectionsLabels :
        nbrePrestations += len(dictPrestations[label])
    dlg = wx.MessageDialog(None, _(u"Souhaitez-vous vraiment appliquer le produit local '%s' aux %d prestations sélectionnées ?\n\n(PS : Cette modification n'aura aucun impact sur les montants facturés)") % (code_produit_local, nbrePrestations), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
    if dlg.ShowModal() != wx.ID_YES :
        dlg.Destroy()
        return
    dlg.Destroy()
    
    # Application
    dlgAttente = wx.BusyInfo(_(u"Veuillez patienter..."), None)
    if 'phoenix' not in wx.PlatformInfo:
        wx.Yield()
    DB = GestionDB.DB()
    for label, listePrestations in dictPrestations.items() :
        if label in selectionsLabels :
            for IDprestation in listePrestations :
                DB.ReqMAJ("prestations", [("code_produit_local", code_produit_local),], "IDprestation", IDprestation)
    DB.Close() 
    del dlgAttente
    
    # Fin du traitement
    dlg = wx.MessageDialog(None, _(u"Le traitement s'est terminé avec succès !"), _(u"Fin"), wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()



if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    Appliquer()
