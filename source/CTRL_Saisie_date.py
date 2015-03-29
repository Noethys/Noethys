#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import sys
import wx.lib.masked as masked
import datetime
import calendar
import dateutil
from dateutil import relativedelta

ID_AIDE = 5
ID_AUJOURDHUI = 10
ID_HIER = 20
ID_DEMAIN = 30
ID_SEMAINE_ACTUELLE = 100
ID_SEMAINE_PRECEDENTE = 110
ID_SEMAINE_SUIVANTE = 120
ID_MOIS_ACTUEL = 200
ID_MOIS_PRECEDENT = 210
ID_MOIS_SUIVANT = 220
ID_ANNEE_ACTUELLE = 300
ID_ANNEE_PRECEDENTE = 310
ID_ANNEE_SUIVANTE = 320

    
class Date(masked.TextCtrl):
    """ Contrôle Date simple """
    def __init__(self, parent, date_min="01/01/1900", date_max="01/01/2999"):
        masked.TextCtrl.__init__(self, parent, -1, "", style=wx.TE_CENTRE, mask = "##/##/####") 
        self.parent = parent
        self.date_min = date_min
        self.date_max = date_max
        self.dateDD = None
        self.lienCtrlAge = False
        largeur = 95
        if "linux" in sys.platform :
            largeur = 110
        self.SetMinSize((largeur, -1))
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
    
    def SetDate(self, date):
        """ Importe une date string ou datetime """
        if date == None or date == "" : 
            return
        try :
            # Quelque soit le format, le change en datetime
            if type(date) == datetime.date :
                # Si c'est un datetime
                dateDD = date
            if type(date) == str or type(date) == unicode :
                if date[2] == "/" :
                    # Si c'est une date française
                    dateDD = datetime.date(year=int(date[6:10]), month=int(date[3:5]), day=int(date[:2]))
                else:
                    # Si c'est une date anglaise
                    dateDD = datetime.date(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]))
            # Transformation en date française
            dateFR = self.DateEngFr(str(dateDD))
            self.SetValue(dateFR)
        except :
            pass
    
    def GetDate(self, FR=False):
        """ Récupère une date au format Datetime ou francaise"""
        dateFR = self.GetValue()
        if dateFR == "  /  /    ":
            return None
        validation = ValideDate(dateFR, self.date_min, self.date_max, avecMessages=False)
        if validation == False : 
            return None
        dateDD = datetime.date(year=int(dateFR[6:10]), month=int(dateFR[3:5]), day=int(dateFR[:2]))
        dateFR = self.DateEngFr(str(dateDD))
        if FR == True :
            return dateFR
        else:
            return dateDD
            
    def DateEngFr(self, textDate):
        text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
        return text

    def DateFrEng(self, textDate):
        text = str(textDate[6:10]) + "/" + str(textDate[3:5]) + "/" + str(textDate[:2])
        return text
        
    def OnKillFocus(self, event):
        self.MaJ_DateNaiss()
        # Vérification de la date
        self.FonctionValiderDate()
        # Envoi un signal de changement de date au panel parent
        try :
            self.parent.OnChoixDate()
        except :
            pass
        event.Skip()
        
    def MaJ_DateNaiss(self):
        # Verifie la validite de la date
        if self.GetValue() == "  /  /    ":
            if self.lienCtrlAge == True :
                self.parent.ctrl_age.SetValue("")
            return
##        validation = ValideDate(self.GetValue(), self.date_min, self.date_max)
##        if validation == False:
##            self.SetFocus()
##            return
            
    def FonctionValiderDate(self):
        # Verifie la validite de la date
        validation = ValideDate(self.GetValue(), self.date_min, self.date_max)
        return validation
    
    def Validation(self):
        return self.FonctionValiderDate()
    
    def GetAge(self):
        # Calcul de l'age de la personne
        bday = self.GetDate()
        datedujour = datetime.date.today()
        age = (datedujour.year - bday.year) - int((datedujour.month, datedujour.day) < (bday.month, bday.day))
        return age
    
    def GetPanelParent(self):
        if self.parent.GetName() == "panel_date2" :
            return self.parent.parent
        else :
            return self.parent

    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        menuPop = wx.Menu()
        
        item = wx.MenuItem(menuPop, ID_AUJOURDHUI, u"Aujourd'hui")
        item.SetBitmap(wx.Bitmap("Images/16x16/Date_actuelle.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnActionMenu, id=ID_AUJOURDHUI)

        item = wx.MenuItem(menuPop, ID_HIER, u"Hier")
        item.SetBitmap(wx.Bitmap("Images/16x16/Date_precedente.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnActionMenu, id=ID_HIER)

        item = wx.MenuItem(menuPop, ID_DEMAIN, u"Demain")
        item.SetBitmap(wx.Bitmap("Images/16x16/Date_suivante.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnActionMenu, id=ID_DEMAIN)
        
        menuPop.AppendSeparator()
        
        listeFonctions = [
            (ID_SEMAINE_ACTUELLE, u"Semaine actuelle"),
            (ID_SEMAINE_PRECEDENTE, u"Semaine précédente"),
            (ID_SEMAINE_SUIVANTE, u"Semaine suivante"),
            (None, None),
            (ID_MOIS_ACTUEL, u"Mois actuel"),
            (ID_MOIS_PRECEDENT, u"Mois précédent"),
            (ID_MOIS_SUIVANT, u"Mois suivant"),
            (None, None),
            (ID_ANNEE_ACTUELLE, u"Année actuelle"),
            (ID_ANNEE_PRECEDENTE, u"Année précédente"),
            (ID_ANNEE_SUIVANTE, u"Année suivante"),
            ]
        for id, label in listeFonctions :
            if id == None :
                menuPop.AppendSeparator()
            else :
                sousMenu = wx.Menu()
                sousMenu.AppendItem(wx.MenuItem(menuPop, id+1, u"Date de début"))
                self.Bind(wx.EVT_MENU, self.OnActionMenu, id=id+1)
                sousMenu.AppendItem(wx.MenuItem(menuPop, id+2, u"Date de fin"))
                self.Bind(wx.EVT_MENU, self.OnActionMenu, id=id+2)
                item = menuPop.AppendMenu(id, label, sousMenu)
        
        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, ID_AIDE, u"Aide")
        item.SetBitmap(wx.Bitmap("Images/16x16/Aide.png", wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnActionMenu, id=ID_AIDE)

        self.PopupMenu(menuPop)
        menuPop.Destroy()
    
    def OnActionMenu(self, event=None):
        id = event.GetId() 
        dateJour = datetime.date.today()
        
        if id == ID_AUJOURDHUI :
            self.SetDate(dateJour)
        
        if id == ID_HIER :
            self.SetDate(dateJour-datetime.timedelta(days=1))
        
        if id == ID_DEMAIN :
            self.SetDate(dateJour+datetime.timedelta(days=1))
        
        # Semaine
        if id == ID_SEMAINE_ACTUELLE + 1 :
            date = dateJour + relativedelta.relativedelta(weekday=relativedelta.MO(-1))
            self.SetDate(date)
        if id == ID_SEMAINE_ACTUELLE + 2 :
            date = dateJour + relativedelta.relativedelta(weekday=relativedelta.MO(-1))
            self.SetDate(date + datetime.timedelta(days=6))

        if id == ID_SEMAINE_PRECEDENTE + 1 :
            date = dateJour + relativedelta.relativedelta(weekday=relativedelta.SU(-1))
            self.SetDate(date - datetime.timedelta(days=6))
        if id == ID_SEMAINE_PRECEDENTE + 2 :
            date = dateJour + relativedelta.relativedelta(weekday=relativedelta.SU(-1))
            self.SetDate(date)

        if id == ID_SEMAINE_SUIVANTE + 1 :
            date = dateJour + relativedelta.relativedelta(weekday=relativedelta.MO(+1))
            self.SetDate(date)
        if id == ID_SEMAINE_SUIVANTE + 2 :
            date = dateJour + relativedelta.relativedelta(weekday=relativedelta.MO(+1))
            self.SetDate(date + datetime.timedelta(days=6))

        # Mois
        if id == ID_MOIS_ACTUEL + 1 :
            self.SetDate(datetime.date(dateJour.year, dateJour.month, 1))
        if id == ID_MOIS_ACTUEL + 2 :
            mois = calendar.monthrange(dateJour.year, dateJour.month)
            self.SetDate(datetime.date(dateJour.year, dateJour.month, mois[1]))

        if id == ID_MOIS_PRECEDENT + 1 :
            date = dateJour + relativedelta.relativedelta(months=-1)
            self.SetDate(datetime.date(date.year, date.month, 1))
        if id == ID_MOIS_PRECEDENT + 2 :
            date = dateJour + relativedelta.relativedelta(months=-1)
            mois = calendar.monthrange(date.year, date.month)
            self.SetDate(datetime.date(date.year, date.month, mois[1]))

        if id == ID_MOIS_SUIVANT + 1 :
            date = dateJour + relativedelta.relativedelta(months=+1)
            self.SetDate(datetime.date(date.year, date.month, 1))
        if id == ID_MOIS_SUIVANT + 2 :
            date = dateJour + relativedelta.relativedelta(months=+1)
            mois = calendar.monthrange(date.year, date.month)
            self.SetDate(datetime.date(date.year, date.month, mois[1]))

        # Année
        if id == ID_ANNEE_ACTUELLE + 1 :
            self.SetDate(datetime.date(dateJour.year, 1, 1))
        if id == ID_ANNEE_ACTUELLE + 2 :
            self.SetDate(datetime.date(dateJour.year, 12, 31))

        if id == ID_ANNEE_PRECEDENTE + 1 :
            date = dateJour + relativedelta.relativedelta(years=-1)
            self.SetDate(datetime.date(date.year, 1, 1))
        if id == ID_ANNEE_PRECEDENTE + 2 :
            date = dateJour + relativedelta.relativedelta(years=-1)
            self.SetDate(datetime.date(date.year, 12, 31))

        if id == ID_ANNEE_SUIVANTE + 1 :
            date = dateJour + relativedelta.relativedelta(years=+1)
            self.SetDate(datetime.date(date.year, 1, 1))
        if id == ID_ANNEE_SUIVANTE + 2 :
            date = dateJour + relativedelta.relativedelta(years=+1)
            self.SetDate(datetime.date(date.year, 12, 31))
        
        if id == ID_AIDE :
            import UTILS_Aide
            UTILS_Aide.Aide("Slectionnerunedate")        

def ValideDate(texte, date_min="01/01/1900", date_max="01/01/2999", avecMessages=True):
    """ Verificateur de validite de date """
    listeErreurs = []
    # On vérifie si les cases ne sont pas vides
    if texte[0] == " " or texte[1] == " ":
        listeErreurs.append(u"le jour")
    if texte[3] == " " or texte[4] == " ":
        listeErreurs.append(u"le mois")
    if texte[6] == " " or texte[7] == " " or texte[8] == " " or texte[9] == " ":
        listeErreurs.append(u"l'année")
    
    if texte != "  /  /    ":

        # On vérifie que les chiffres existent
        if u"le jour" not in listeErreurs:
            jour = int(texte[:2])
            if jour == 0 or jour > 31:
                listeErreurs.append(u"le jour")

        if u"le mois" not in listeErreurs:
            mois = int(texte[3:5])
            if mois == 0 or mois > 12:
                listeErreurs.append(u"le mois")
                
        if u"l'année" not in listeErreurs:
            annee = int(texte[6:10])
            if annee < 1900 or annee > 2999:
                listeErreurs.append(u"l'année")
              
        # Affichage du message d'erreur
        
        if len(listeErreurs) != 0:
            # Message en cas de date incomplète
            if len(listeErreurs) == 1:
                message = u"Une incohérence a été détectée dans " + listeErreurs[0]
            if len(listeErreurs) == 2:
                message = u"Des incohérences ont été détectées dans " + listeErreurs[0] + " et " + listeErreurs[1]
            if len(listeErreurs) == 3:
                message = u"Des incohérences ont été détectées dans " + listeErreurs[0]  + ", " + listeErreurs[1]  + " et " + listeErreurs[2]
            message = message + u" de la date que vous venez de saisir. Veuillez la vérifier."
            
            if avecMessages == True :
                wx.MessageBox(message, "Erreur de date")
            return False
        else:
            # On vérifie que les dates sont comprises dans l'intervalle donné en paramètre
            date_min = int(str(date_min[6:10]) + str(date_min[3:5]) + str(date_min[:2]))
            date_max = int(str(date_max[6:10]) + str(date_max[3:5]) + str(date_max[:2]))
            date_sel = int(str(texte[6:10]) + str(texte[3:5]) + str(texte[:2]))

            if date_sel < date_min:
                message = u"La date que vous venez de saisir semble trop ancienne. Veuillez la vérifier."
                if avecMessages == True :
                    wx.MessageBox(message, "Erreur de date")
                return False
            if date_sel > date_max:
                message = u"La date que vous venez de saisir semble trop élevée. Veuillez la vérifier."
                if avecMessages == True :
                    wx.MessageBox(message, "Erreur de date")
                return False
            
            # On vérifie que la date peut être transformée en Datetime :
            try :
                dateDD = datetime.date(year=int(texte[6:10]), month=int(texte[3:5]), day=int(texte[:2]))
            except :
                message = u"La date que vous venez de saisir ne semble pas valide !"
                if avecMessages == True :
                    wx.MessageBox(message, "Erreur de date")
                return False
        
    else:
        return True




class Date2(wx.Panel):
    """ Contrôle Date avec Bouton Calendrier inclus """
    def __init__(self, parent, date_min="01/01/1910", date_max="01/01/2030", activeCallback=True):
        wx.Panel.__init__(self, parent, id=-1, name="panel_date2", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.activeCallback = activeCallback
        
        self.ctrl_date = Date(self, date_min, date_max)
        self.bouton_calendrier = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Calendrier.png", wx.BITMAP_TYPE_ANY))
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalendrier, self.bouton_calendrier)
        self.bouton_calendrier.SetToolTipString(u"Cliquez ici pour sélectionner la date dans le calendrier")

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.bouton_calendrier, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
    
    def SetToolTipString(self, texte=""):
        self.ctrl_date.SetToolTipString(texte)
        
    def OnBoutonCalendrier(self, event): 
        import DLG_calendrier_simple
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date.SetDate(date)
            self.OnChoixDate() 
        dlg.Destroy()

    def OnChoixDate(self):
        # Envoi un signal de changement de date au panel parent
        if self.activeCallback == True :
            try :
                self.parent.OnChoixDate()
            except :
                pass

    def SetDate(self, date):
        self.ctrl_date.SetDate(date)
    
    def GetDate(self, FR=False):
        return self.ctrl_date.GetDate(FR=FR)
                    
    def FonctionValiderDate(self):
        return self.ctrl_date.FonctionValiderDate()
    
    def Validation(self):
        return self.ctrl_date.FonctionValiderDate()
        
    def GetAge(self):
        return self.ctrl_date.GetAge() 
    
    def SetInsertionPoint(self, position=0):
        self.ctrl_date.SetInsertionPoint(position)
    
    def SetFocus(self):
        self.ctrl_date.SetFocus()
        
        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="panel_test")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl1 = Date2(panel)
        self.ctrl2 = Date2(panel)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl1, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.ctrl2, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()