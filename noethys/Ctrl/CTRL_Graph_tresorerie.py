#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
from dateutil import relativedelta

import GestionDB
from Utils import UTILS_Dates

import numpy as np
import matplotlib
matplotlib.interactive(False)
matplotlib.use('wxagg')
try :
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as Canvas
    from matplotlib.pyplot import setp
    import matplotlib.dates as mdates
    import matplotlib.mlab as mlab
except Exception as err :
    print("Erreur d'import : ", Exception, err)




class CTRL_Affichage(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.MAJlisteDonnees() 
    
    def MAJlisteDonnees(self):
        self.SetItems(self.GetListeDonnees())
        self.Select(0)
    
    def GetListeDonnees(self):
        listeOptions = [
            ("actuellement", _(u"Actuellement")),
            ("7_prochains_jours", _(u"7 prochains jours")),
            ("14_prochains_jours", _(u"14 prochains jours")),
            ("30_prochains_jours", _(u"30 prochains jours")),
            ("90_prochains_jours", _(u"90 prochains jours")),
            ("6_prochains_mois", _(u"6 prochains mois")),
            ("12 prochains_mois", _(u"12 prochains mois")),
            ("mois_actuel", _(u"Mois actuel")),
            ("annee_actuelle", _(u"Année actuelle")),
            ("personnalise", _(u"Personnalisé")),
            ]
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for code, label in listeOptions :
            self.dictDonnees[index] = code
            listeItems.append(label)
            index += 1
        return listeItems

    def SetCode(self, code=None):
        for index, codeTemp in self.dictDonnees.items():
            if codeTemp == code :
                 self.SetSelection(index)

    def GetCode(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class CTRL(wx.Panel):
    def __init__(self, parent, style=wx.TAB_TRAVERSAL):
        wx.Panel.__init__(self, parent, id=-1, style=style)
        self.IDcompte = None
        self.date_debut = None
        self.date_fin = None
        
        self.figure = matplotlib.pyplot.figure()
        self.canvas = Canvas(self, -1, self.figure)
        self.SetColor( (255,255,255) )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas,1,wx.EXPAND|wx.ALL, 0)
        self.SetSizer(sizer)
            
    def convertCouleur(self, RGB) :
        couleur = []
        for valeur in RGB :
            couleur.append(valeur/255.0)
        return couleur

    def SetColor(self, rgbtuple=None):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor(clr)
        self.figure.set_edgecolor(clr)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))
    
    def SetCompte(self, IDcompte=None):
        self.IDcompte = IDcompte
        
    def SetPeriode(self, code="", date_debut=None, date_fin=None):
        """ Attribue la période """
        dateJour = datetime.date.today() 
        self.date_debut = None
        self.date_fin = None

        if code == "actuellement" :
            self.date_debut = dateJour + relativedelta.relativedelta(days=-25)
            self.date_fin = dateJour + relativedelta.relativedelta(days=+30)
        if code == "7_prochains_jours" :
            self.date_debut = dateJour
            self.date_fin = dateJour + relativedelta.relativedelta(days=+7)
        if code == "14_prochains_jours" :
            self.date_debut = dateJour
            self.date_fin = dateJour + relativedelta.relativedelta(days=+14)
        if code == "30_prochains_jours" :
            self.date_debut = dateJour
            self.date_fin = dateJour + relativedelta.relativedelta(days=+30)
        if code == "90_prochains_jours" :
            self.date_debut = dateJour
            self.date_fin = dateJour + relativedelta.relativedelta(days=+90)
        if code == "6_prochains_mois" :
            self.date_debut = dateJour
            self.date_fin = dateJour + relativedelta.relativedelta(months=+6)
        if code == "12_prochains_mois" :
            self.date_debut = dateJour
            self.date_fin = dateJour + relativedelta.relativedelta(months=+12)
        if code == "mois_actuel" :
            self.date_debut = datetime.date(dateJour.year, dateJour.month, 1)
            self.date_fin = datetime.date(dateJour.year, dateJour.month, 1) + relativedelta.relativedelta(months=+1) - relativedelta.relativedelta(days=+1)
        if code == "annee_actuelle" :
            self.date_debut = datetime.date(dateJour.year, 1, 1)
            self.date_fin = datetime.date(dateJour.year, 12, 31)
        if code == "personnalise" :
            self.date_debut = date_debut
            self.date_fin = date_fin
        
        self.MAJ() 
    
    def GetDonnees(self):
        DB = GestionDB.DB()
        req = """SELECT IDoperation, type, date, IDreleve, montant
        FROM compta_operations 
        WHERE IDcompte_bancaire=%d
        ORDER BY date, IDoperation;""" % self.IDcompte
        DB.ExecuterReq(req)
        listeOperations = DB.ResultatReq()
        DB.Close()
        
        # Analyse des opérations
        listeDonnees = []
        solde = 0.0
        for IDoperation, typeOperation, date, IDreleve, montant in listeOperations :
            date = UTILS_Dates.DateEngEnDateDD(date)
            if typeOperation == "debit" :
                solde -= montant
            else :
                solde += montant
            listeDonnees.append((date, solde))
        return listeDonnees

    def MAJ(self) :
        self.figure.clear()
        
        if self.IDcompte == None or self.date_debut == None or self.date_fin == None :
            wx.CallAfter(self.SendSizeEvent)
            return
        
        listeDates = []
        listeValeurs = []
        for date, valeur in self.GetDonnees() :
            if date >= self.date_debut and date <= self.date_fin :
                listeDates.append(date)
                listeValeurs.append(valeur)

        if len(listeDates) < 2 :
            wx.CallAfter(self.SendSizeEvent)
            return
            
        ax = self.figure.add_subplot(111)
                
        # Sélection du mode d'affichage
        mode = None
        nbreJours = (self.date_fin - self.date_debut).days #(max(listeDates) - min(listeDates)).days
        if nbreJours < 60 :
            mode = "jour"
        elif nbreJours < 400 :
            mode = "mois"
        else :
            mode = "annee"
        
        # Affichage par année
        if mode == "annee" :
            anneeMin = self.date_debut.year
            anneeMax = self.date_max.year + 1
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.xaxis.set_minor_locator(mdates.MonthLocator())
            datemin = datetime.date(anneeMin, 1, 1)
            datemax = datetime.date(anneeMax, 1, 1)
            ax.set_xlim(datemin, datemax)

##        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
##        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

##        ax.xaxis.set_major_locator(mdates.DayLocator())
##        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        if mode ==  "mois" :
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

        if mode == "jour" :
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
##            ax.xaxis.set_minor_locator(mdates.DayLocator())      
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
##            ax.set_xlim([min(listeDates), max(listeDates)])      
            ax.set_xlim([self.date_debut, self.date_fin])      

        ax.fill_between(listeDates, 0, listeValeurs, facecolor='blue', alpha=0.5, label=_(u"Trésorerie"))
        
        self.figure.autofmt_xdate()

        ax.grid(True)
        ax.figure.canvas.draw()
        wx.CallAfter(self.SendSizeEvent)
        return
        
        
        
        
        
        

        x = [0, 0, 3.5, 4, 5]#np.linspace(0, 1)
        y = [0, 10, 2, 3, 4]

        ax.fill(x, y, 'r')
        ax.grid(True)
        ax.figure.canvas.draw()
        
        return
        # Création du graph
        ind = arange(len(listeLabels)) + 0.25  # the x locations for the groups
        width = 0.5
        for x in range(len(listeLabels)) :
##            couleur = MODELES.ConvertitCouleur2(MODELES.COULEUR_VERT_POMME)
            barre = ax.bar(ind[x], listeValeurs[x], width)#, color=couleur)
        
##        # Axe horizontal
##        ind = arange(len(listeLabels)) 
##        ax.set_xticks(ind + width) 
##        ax.set_xticklabels(listeLabels)
##        labelsx = ax.get_xticklabels()
##        labelsy = ax.get_yticklabels()
##        matplotlib.pyplot.setp(labelsx, rotation=45, fontsize=9, horizontalalignment='right')
##        
##        # Axe vertical
##        ax.set_ylabel("Nbre de familles", fontsize=8)
        
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(_(u"Comparatif du nombre de familles"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        self.figure.subplots_adjust(left=None, bottom=0.4, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)

        # Re-dessine le canvas
        ax.figure.canvas.draw()





class CTRL2():
    def __init__(self):

        figure = matplotlib.pyplot.figure()

        ax = figure.add_subplot(111)
                
        # Création du graph
        ind = arange(len(listeLabels)) + 0.25  # the x locations for the groups
        width = 0.5
        for x in range(len(listeLabels)) :
            if x == indexPeriodeReference :
                couleur = MODELES.ConvertitCouleur2(MODELES.COULEUR_VERT_POMME)
            else:
                couleur = MODELES.ConvertitCouleur2(MODELES.COULEUR_BLEU_CIEL)
            barre = ax.bar(ind[x], listeValeurs[x], width, color=couleur)
        
        # Axe horizontal
        ind = arange(len(listeLabels)) 
        ax.set_xticks(ind + width) 
        ax.set_xticklabels(listeLabels)
        labelsx = ax.get_xticklabels()
        labelsy = ax.get_yticklabels()
        matplotlib.pyplot.setp(labelsx, rotation=45, fontsize=9, horizontalalignment='right')
        
        # Axe vertical
        ax.set_ylabel("Nbre de familles", fontsize=8)
        
        labels = ax.get_yticklabels()
        matplotlib.pyplot.setp(labels, rotation=0, fontsize=9) 
        
        # Titre
        title = ax.set_title(_(u"Comparatif du nombre de familles"), weight="bold", horizontalalignment = 'center')#, position=(0.5, 0.97))
        matplotlib.pyplot.setp(title, rotation=0, fontsize=9)
        
        figure.subplots_adjust(left=None, bottom=0.4, right=None, wspace=None, hspace=None)
        
        # Affiche les grilles
        ax.grid(True)
        
        return figure

# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel)
        self.ctrl.MAJ() 
        bouton = wx.Button(panel, -1, _(u"Test"))
        self.Bind(wx.EVT_BUTTON, self.OnBouton, bouton)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.EXPAND, 4)
        sizer_2.Add(bouton, 0, wx.EXPAND, 0)
        panel.SetSizer(sizer_2)
        self.Layout()
        
    def OnBouton(self, event):

        listeDonnees = [
            (datetime.date(2014, 2, 1), 100.0),
            (datetime.date(2014, 2, 10), 200.0),
            (datetime.date(2014, 2, 12), 50.0),
            (datetime.date(2014, 2, 21), 10.0),
            (datetime.date(2014, 2, 28), -70.0),
            ]
        self.ctrl.listeDonnees = listeDonnees
        self.ctrl.MAJ() 

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
