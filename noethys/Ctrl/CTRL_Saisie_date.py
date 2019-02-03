#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
import wx
import wx.lib.masked as masked
import re
import sys
import datetime
import calendar
import six
from Utils import UTILS_Config
from dateutil.parser import parse, parserinfo
from dateutil import relativedelta
from Utils.UTILS_Traduction import _
from Utils import UTILS_Dates
from Ctrl import CTRL_Saisie_heure


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

# expression régulière pour une date (JJ/MM/AAAA)
datePattern = re.compile(
    r"(?P<jour>[\d]{1,2})/(?P<mois>[\d]{1,2})/(?P<annee>[\d]{4})"
)



class myparserinfo(parserinfo):
    JUMP = [" ", ".", ",", ";", "-", "/", "'",
            "at", "on", "and", "ad", "m", "t", "of",
            "st", "nd", "rd", "th"]

    WEEKDAYS = [(_(u"Lun"), _(u"Lundi")),
                (_(u"Mar"), _(u"Mardi")),
                (_(u"Mer"), _(u"Mercredi")),
                (_(u"Jeu"), _(u"Jeudi")),
                (_(u"Ven"), _(u"Vendredi")),
                (_(u"Sam"), _(u"Samedi")),
                (_(u"Dim"), _(u"Dimanche"))]
    MONTHS = [(_(u"Jan"), _(u"Janvier")),
              (_(u"Fév"), _(u"Février")),
              (_(u"Mar"), _(u"Mars")),
              (_(u"Avr"), _(u"Avril")),
              (_(u"Mai"), _(u"Mai")),
              (_(u"Juin"), _(u"Juin")),
              (_(u"Juil"), _(u"Juillet")),
              (_(u"Aoû"), _(u"Août")),
              (_(u"Sept"), _(u"Septembre")),
              (_(u"Oct"), _(u"Octobre")),
              (_(u"Nov"), _(u"Novembre")),
              (_(u"Déc"), _(u"Décembre")),]
    HMS = [("h", "hour", "hours"),
           ("m", "minute", "minutes"),
           ("s", "second", "seconds")]
    AMPM = [("am", "a"),
            ("pm", "p")]
    UTCZONE = ["UTC", "GMT", "Z"]
    PERTAIN = ["of"]
    TZOFFSET = {}

    def __init__(self) :
        parserinfo.__init__(self, dayfirst=True, yearfirst=False)



class Date(masked.TextCtrl):
    """ Contrôle Date simple """
    def __init__(self, parent, date_min="01/01/1900", date_max="01/01/2999", size=(-1, -1), pos=wx.DefaultPosition):
        self.mask_date = UTILS_Config.GetParametre("mask_date", "##/##/####")
        masked.TextCtrl.__init__(self, parent, -1, "", style=wx.TE_CENTRE |wx.TE_PROCESS_ENTER, size=size, pos=pos, mask=self.mask_date)
        self.parent = parent
        self.date_min = date_min
        self.date_max = date_max
        self.dateDD = None
        self.lienCtrlAge = False
        largeur = 95
        if "linux" in sys.platform :
            largeur = 110
        self.SetMinSize((largeur, -1))
        self.Bind(wx.EVT_TEXT_ENTER, self.OnKillFocus)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnContextMenu)
        if self.mask_date == "" :
            self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)

    def OnDoubleClick(self, event):
        pass

    def SetDate(self, date):
        """ Importe une date string ou datetime """
        if date == None or date == "" : 
            return
        try :
            # Quelque soit le format, le change en datetime
            if type(date) == datetime.date :
                # Si c'est un datetime
                dateDD = date
            if type(date) == str or type(date) == six.text_type :
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
        if dateFR == "  /  /    " or dateFR == "" :
            return None
        validation = ValideDate(dateFR, self.date_min, self.date_max, avecMessages=False, mask=self.mask_date)
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

    def FonctionValiderDate(self):
        # Parser de la date en cas de format libre
        if self.GetValue() != "" and self.mask_date == "":
            try :
                date = parse(self.GetValue(), myparserinfo())
                self.SetDate(datetime.date(year=date.year, month=date.month, day=date.day))
            except :
                pass

        # Verifie la validite de la date
        validation = ValideDate(self.GetValue(), self.date_min, self.date_max, mask=self.mask_date)
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
        menuPop = UTILS_Adaptations.Menu()
        
        item = wx.MenuItem(menuPop, ID_AUJOURDHUI, _(u"Aujourd'hui"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Date_actuelle.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnActionMenu, id=ID_AUJOURDHUI)

        item = wx.MenuItem(menuPop, ID_HIER, _(u"Hier"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Date_precedente.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnActionMenu, id=ID_HIER)

        item = wx.MenuItem(menuPop, ID_DEMAIN, _(u"Demain"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Date_suivante.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.OnActionMenu, id=ID_DEMAIN)
        
        menuPop.AppendSeparator()
        
        listeFonctions = [
            (ID_SEMAINE_ACTUELLE, _(u"Semaine actuelle")),
            (ID_SEMAINE_PRECEDENTE, _(u"Semaine précédente")),
            (ID_SEMAINE_SUIVANTE, _(u"Semaine suivante")),
            (None, None),
            (ID_MOIS_ACTUEL, _(u"Mois actuel")),
            (ID_MOIS_PRECEDENT, _(u"Mois précédent")),
            (ID_MOIS_SUIVANT, _(u"Mois suivant")),
            (None, None),
            (ID_ANNEE_ACTUELLE, _(u"Année actuelle")),
            (ID_ANNEE_PRECEDENTE, _(u"Année précédente")),
            (ID_ANNEE_SUIVANTE, _(u"Année suivante")),
            ]
        for id, label in listeFonctions :
            if id == None :
                menuPop.AppendSeparator()
            else :
                sousMenu = UTILS_Adaptations.Menu()
                sousMenu.AppendItem(wx.MenuItem(menuPop, id+1, _(u"Date de début")))
                self.Bind(wx.EVT_MENU, self.OnActionMenu, id=id+1)
                sousMenu.AppendItem(wx.MenuItem(menuPop, id+2, _(u"Date de fin")))
                self.Bind(wx.EVT_MENU, self.OnActionMenu, id=id+2)
                item = menuPop.AppendMenu(id, label, sousMenu)
        
        menuPop.AppendSeparator()
        
        item = wx.MenuItem(menuPop, ID_AIDE, _(u"Aide"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Aide.png"), wx.BITMAP_TYPE_PNG))
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
            from Utils import UTILS_Aide
            UTILS_Aide.Aide("Slectionnerunedate")


def ValideDate(texte, date_min="01/01/1900", date_max="01/01/2999", avecMessages=True, mask=""):
    """ Verificateur de validite de date """
    if texte == "  /  /    " or texte == "" :
        return True

    listeErreurs = []

    # Recherche depuis l'expression régulière
    date = datePattern.match(texte)
    if date:
        # On vérifie que les chiffres existent
        jour = int(date.group("jour"))
        if jour == 0 or jour > 31:
            listeErreurs.append(_(u"le jour"))
        mois = int(date.group("mois"))
        if mois == 0 or mois > 12:
            listeErreurs.append(_(u"le mois"))
        annee = int(date.group("annee"))
        if annee < 1900 or annee > 2999:
            listeErreurs.append(_(u"l'année"))

        # Affichage du message d'erreur
        if listeErreurs:
            # Message en cas de date incomplète
            if avecMessages == True :
                nbErreurs = len(listeErreurs)
                if nbErreurs == 1:
                    message = _(u"Une incohérence a été détectée dans ") + listeErreurs[0]
                else:
                    message = _(u"Des incohérences ont été détectées dans ") + listeErreurs[0]
                    if nbErreurs == 2:
                        message += " et " + listeErreurs[1]
                    elif nbErreurs == 3:
                        message += ", " + listeErreurs[1]  + " et " + listeErreurs[2]
                message += _(u" de la date que vous venez de saisir. Veuillez la vérifier.")
                wx.MessageBox(message, "Erreur de date")
            return False
        else:
            # On vérifie que les dates sont comprises dans l'intervalle donné en paramètre
            date_min = int(str(date_min[6:10]) + str(date_min[3:5]) + str(date_min[:2]))
            date_max = int(str(date_max[6:10]) + str(date_max[3:5]) + str(date_max[:2]))
            date_sel = int(str(annee) + ('0' if mois < 10 else '') + str(mois) +
                                        ('0' if jour < 10 else '') + str(jour))

            if date_sel < date_min:
                if avecMessages == True :
                    message = _(u"La date que vous venez de saisir semble trop ancienne. Veuillez la vérifier.")
                    wx.MessageBox(message, "Erreur de date")
                return False
            if date_sel > date_max:
                if avecMessages == True :
                    message = _(u"La date que vous venez de saisir semble trop élevée. Veuillez la vérifier.")
                    wx.MessageBox(message, "Erreur de date")
                return False

            # On vérifie que la date peut être transformée en Datetime
            try:
                datetime.date(year=annee, month=mois, day=jour)
            except :
                pass
            else:
                return True

    if avecMessages == True :
        message = _(u"La date que vous venez de saisir ne semble pas valide !")
        wx.MessageBox(message, "Erreur de date")
    return False


class Date2(wx.Panel):
    """ Contrôle Date avec Bouton Calendrier inclus """
    def __init__(self, parent, date_min="01/01/1910", date_max="01/01/2030", activeCallback=True, size=(-1, -1), heure=False, pos=wx.DefaultPosition):
        wx.Panel.__init__(self, parent, id=-1, name="panel_date2", size=size, pos=pos, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.activeCallback = activeCallback
        self.heure = heure
        
        self.ctrl_date = Date(self, date_min, date_max)
        self.bouton_calendrier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCalendrier, self.bouton_calendrier)
        self.bouton_calendrier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la date dans le calendrier")))

        if heure == True :
            self.ctrl_heure = CTRL_Saisie_heure.Heure(self)

        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_base.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        grid_sizer_base.Add(self.bouton_calendrier, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        if heure == True :
            grid_sizer_base.Add(self.ctrl_heure, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
    
    def SetToolTipString(self, texte=""):
        self.ctrl_date.SetToolTip(wx.ToolTip(texte))

    def SetToolTip(self, tip=None):
        self.ctrl_date.SetToolTip(tip)

    def OnBoutonCalendrier(self, event): 
        from Dlg import DLG_calendrier_simple
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
        if type(date) == datetime.datetime or (type(date) in (str, six.text_type) and ":" in date):
            self.ctrl_date.SetDate(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date), "%Y-%m-%d"))
            if self.heure == True :
                self.ctrl_heure.SetHeure(datetime.datetime.strftime(UTILS_Dates.DateEngEnDateDDT(date), "%H:%M"))
        else :
            self.ctrl_date.SetDate(date)
    
    def GetDate(self, FR=False):
        if self.heure == False :
            return self.ctrl_date.GetDate(FR=FR)
        else :
            date = self.ctrl_date.GetDate()
            heure = self.ctrl_heure.GetHeure()
            if date == None or heure == None or heure == "  :  ":
                return None
            date_heure = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=int(heure[:2]), minute=int(heure[3:]))
            return date_heure

    def FonctionValiderDate(self):
        return self.Validation()
    
    def Validation(self):
        if self.heure == False:
            return self.ctrl_date.FonctionValiderDate()
        else :
            date_valide = self.ctrl_date.FonctionValiderDate()
            if date_valide == False :
                return False

            heure = self.ctrl_heure.GetHeure()
            if heure == None or self.ctrl_heure.Validation() == False :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une heure valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_heure.SetFocus()
                return False

            return True
        
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
        self.ctrl1 = Date2(panel, heure=True)
        self.ctrl2 = Date2(panel)
        self.bouton1 = wx.Button(panel, -1, u"Tester la validité du ctrl 1")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl1, 0, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.ctrl2, 0, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton1, 0, wx.ALL | wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBouton1, self.bouton1)

    def OnBouton1(self, event):
        print(self.ctrl1.Validation())



if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
