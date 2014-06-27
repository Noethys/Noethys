#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import wx.lib.agw.pybusyinfo as PBI

import GestionDB
import UTILS_Dates
import DLG_Selection_dates


def Appliquer():
    """ Applique un code comptable à un lot de prestations """
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
        if dictPrestations.has_key(label) == False :
            dictPrestations[label] = []
        dictPrestations[label].append(IDprestation)
    
    dlg = wx.MultiChoiceDialog(None, u"Sélectionnez les prestations à modifier :", u"Selection des prestations", dictPrestations.keys())
    dlg.SetSize((500, 400))
    if dlg.ShowModal() == wx.ID_OK :
        selections = dlg.GetSelections()
        selectionsLabels = [dictPrestations.keys()[x] for x in selections]
        dlg.Destroy()
    else :
        dlg.Destroy()
        return

    # Choix du code comptable
    dlg = wx.TextEntryDialog(None, u"Quel code comptable souhaitez-vous appliquer ?", u"Sélection d'un code comptable", "")
    if dlg.ShowModal() == wx.ID_OK:
        code_compta = dlg.GetValue()
        dlg.Destroy()
    else :
        dlg.Destroy()
        return
    
    # Demande de confirmation
    nbrePrestations = 0
    for label in selectionsLabels :
        nbrePrestations += len(dictPrestations[label])
    dlg = wx.MessageDialog(None, u"Souhaitez-vous vraiment appliquer le code comptable '%s' aux %d prestations sélectionnées ?\n\n(PS : Cette modification n'aura aucun impact sur les montants facturés)" % (code_compta, nbrePrestations), u"Confirmation", wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
    if dlg.ShowModal() != wx.ID_YES :
        dlg.Destroy()
        return
    dlg.Destroy()
    
    # Application
    dlgAttente = PBI.PyBusyInfo(u"Veuillez patienter...", parent=None, title=u"Traitement en cours", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
    wx.Yield() 
    DB = GestionDB.DB()
    for label, listePrestations in dictPrestations.iteritems() :
        if label in selectionsLabels :
            for IDprestation in listePrestations :
                DB.ReqMAJ("prestations", [("code_compta", code_compta),], "IDprestation", IDprestation)
    DB.Close() 
    del dlgAttente
    
    # Fin du traitement
    dlg = wx.MessageDialog(None, u"Le traitement s'est terminé avec succès !", u"Fin", wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()





if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    Appliquer()
