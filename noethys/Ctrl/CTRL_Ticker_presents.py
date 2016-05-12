#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
from wx.lib.ticker import Ticker

import datetime
import GestionDB
from Utils import UTILS_Dates

    
class CTRL(wx.Panel):
    """ Delai d'actualisation en secondes """
    def __init__(self, parent, delai=60, listeActivites=[], fps=20, ppf=2, couleurFond=None):
        wx.Panel.__init__(self, parent, id=-1)
        self.parent = parent
        self.delai = delai
        self.listeActivites = listeActivites
        if couleurFond != None :
            self.SetBackgroundColour(couleurFond)
        
        self.timer = wx.Timer(self, -1)
        
        self.ticker = Ticker(self)
        self.ticker.SetBackgroundColour(self.GetBackgroundColour())
        self.ticker.SetFPS(fps)
        self.ticker.SetPPF(ppf)
        
        # Layout
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        sizer_base.Add(self.ticker, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        
        # Binds
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
    
    def SetTexte(self, texte=u""):
        self.ticker.SetText(texte)

    def Stop(self):
        """Stop moving the text"""
        self.timer.Stop()
        
    def Start(self):
        """Starts the text moving"""
        if not self.timer.IsRunning():
            self.timer.Start(self.delai * 1000)

    def OnTimer(self, event):
        self.MAJ() 
    
    def SetActivites(self, listeActivites=[]):
        self.listeActivites = listeActivites
        
    def MAJ(self):
        try :
            texte = self.GetTexte(self.listeActivites) 
            self.SetTexte(texte)
        except :
            texte = u""
            
        if len(texte) > 0 :
            etat = True
            if self.ticker.IsTicking() == False :
                self.ticker.Start()
        else :
            etat = False
            if self.ticker.IsTicking() :
                self.ticker.Stop()
        try :
            self.parent.AffichePresents(etat)
        except :
            pass
        
    def JoinListe(self, listeTemp=[]):
        if len(listeTemp) > 2 :
            return _(u"%s et %s") % (u", ".join(listeTemp[:-1], listeTemp[-1]))
        else :
            return _(u" et ").join(listeTemp)
        
    def GetTexte(self, listeActivites=[]):
        """ Récupération des données dans la base de données """
        if len(listeActivites) == 0 : conditionActivites = "()"
        elif len(listeActivites) == 1 : conditionActivites = "(%d)" % listeActivites[0]
        else : conditionActivites = str(tuple(listeActivites))
        
        now = datetime.datetime.now()
        date = datetime.date(now.year, now.month, now.day)
        heure = "%02d:%02d" % (now.hour, now.minute)
        
        DB = GestionDB.DB()
        req = """SELECT activites.IDactivite, activites.nom, groupes.IDgroupe, groupes.nom, groupes.ordre, COUNT(IDconso), SUM(quantite)
        FROM consommations 
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = consommations.IDgroupe
        WHERE consommations.IDactivite IN %s
        AND date = '%s'
        AND heure_debut <= '%s' 
        AND heure_fin >= '%s'
        AND etat IN ("reservation", "present")
        GROUP BY consommations.IDactivite, consommations.IDindividu
        ORDER BY activites.nom, groupes.ordre;""" % (conditionActivites, date, heure, heure)
        DB.ExecuterReq(req)
        listeConso = DB.ResultatReq()
        DB.Close() 
        
        if len(listeConso) == 0 :
            return u""
        
        dictTemp = {}
        listeActivites = []
        for IDactivite, nomActivite, IDgroupe, nomGroupe, ordreGroupe, nbreConso, quantite in listeConso :
            if dictTemp.has_key(IDactivite) == False :
                dictTemp[IDactivite] = {"nom" : nomActivite, "nbre" : 0, "groupes" : {} }
                listeActivites.append(IDactivite)
            if dictTemp[IDactivite]["groupes"].has_key(IDgroupe) == False  :
                dictTemp[IDactivite]["groupes"][IDgroupe] = {"nom" : nomGroupe, "ordre" : ordreGroupe, "nbre" : 0}
            dictTemp[IDactivite]["groupes"][IDgroupe]["nbre"] += 1
            dictTemp[IDactivite]["nbre"] += 1
        
        listeTextes = []
        for IDactivite in listeActivites :
            nomActivite = dictTemp[IDactivite]["nom"]
            
            listeGroupes = []
            for IDgroupe, dictGroupe in dictTemp[IDactivite]["groupes"].iteritems() :
                label = u"%d %s" % (dictGroupe["nbre"], dictGroupe["nom"])
                listeGroupes.append((dictGroupe["ordre"], label))
            listeGroupes.sort() 
            groupes = []
            for ordre, label in listeGroupes :
                groupes.append(label)
            
            nbre = dictTemp[IDactivite]["nbre"]
            if nbre == 1 :
                temp = _(u"individu")
            else :
                temp = _(u"individus")
            listeTextes.append(_(u"%d %s sur l'activité %s (%s)") % (nbre, temp, nomActivite, self.JoinListe(groupes)))
        
        texte = _(u"Il y a actuellement %s") % self.JoinListe(listeTextes)
        return texte

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, delai=60, listeActivites=[1,])
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()

        # Init contrôles
        print (self.ctrl.GetTexte([1,]),)
        self.ctrl.MAJ() 
        self.ctrl.Start()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
