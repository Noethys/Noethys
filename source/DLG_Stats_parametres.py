#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import calendar

import GestionDB
import CTRL_Selection_activites
import CTRL_Saisie_date


def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


LISTE_MOIS = (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))



class CTRL_Vacances(wx.Choice):
    def __init__(self, parent):
        self.listePeriodes = (_(u"Février"), _(u"Pâques"), _(u"Eté"), _(u"Toussaint"), _(u"Noël"))
        wx.Choice.__init__(self, parent, -1, choices=self.listePeriodes)
        self.parent = parent
        self.Select(0)
    
    def SetPeriode(self, nom=_(u"Février")):
        self.SetStringSelection(nom)
        
    def GetPeriode(self):
        if self.GetSelection() == -1 :
            return None
        else :
            return self.listePeriodes[self.GetSelection()]


class CTRL_Mois(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, choices=LISTE_MOIS)
        self.parent = parent
        mois = datetime.date.today().month
        self.SetMois(mois)
    
    def SetMois(self, mois=1):
        self.Select(mois-1) 
        
    def GetMois(self):
        if self.GetSelection() == -1 :
            return None
        else :
            return self.GetSelection() + 1
        

class CTRL_Annee(wx.SpinCtrl):
    def __init__(self, parent, min=1970, max=2999):
        wx.SpinCtrl.__init__(self, parent, -1, "", min=min, max=max, size=(80, -1))
        self.parent = parent
        annee = datetime.date.today().year
        self.SetAnnee(annee)
    
    def SetAnnee(self, annee=2012):
        self.SetValue(annee)
        
    def GetAnnee(self):
        return self.GetValue()
    

class CTRL_Mode(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        
        self.mode = None
        self.periode = None

        self.radio_inscrits = wx.RadioButton(self, -1, _(u"Inscrits"), style=wx.RB_GROUP)
        self.radio_presents = wx.RadioButton(self, -1, _(u"Présents sur la période suivante :"))
        
        self.radio_vacances = wx.RadioButton(self, -1, _(u"Vacances :"), style=wx.RB_GROUP)
        self.ctrl_vacances = CTRL_Vacances(self)
        self.ctrl_vacances_annee = CTRL_Annee(self)
        
        self.radio_mois = wx.RadioButton(self, -1, _(u"Mois :"))
        self.ctrl_mois = CTRL_Mois(self)
        self.ctrl_mois_annee = CTRL_Annee(self)
        
        self.radio_annee = wx.RadioButton(self, -1, _(u"Année :"))
        self.ctrl_annee =CTRL_Annee(self)
        
        self.radio_dates = wx.RadioButton(self, -1, _(u"Dates :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_separation_dates = wx.StaticText(self, -1, u"à")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMethode, self.radio_inscrits)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMethode, self.radio_presents)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_vacances)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_mois)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_annee)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_dates)
        
        # Init
        self.OnRadioMethode()

    def __set_properties(self):
        self.radio_inscrits.SetToolTipString(_(u"Cochez ici pour baser les calculs sur les inscrits"))
        self.radio_presents.SetToolTipString(_(u"Cochez ici pour baser les calculs sur les présents sur une période donnée"))
        self.ctrl_vacances_annee.SetMinSize((70, -1))
        self.ctrl_mois_annee.SetMinSize((70, -1))
        self.ctrl_annee.SetMinSize((70, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.radio_inscrits, 0, 0, 0)
        grid_sizer_base.Add(self.radio_presents, 0, 0, 0)

        grid_sizer_presents = wx.FlexGridSizer(rows=4, cols=2, vgap=10, hgap=10)

        # Vacances
        grid_sizer_presents.Add(self.radio_vacances, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_vacances = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_vacances.Add(self.ctrl_vacances, 0, 0, 0)
        grid_sizer_vacances.Add(self.ctrl_vacances_annee, 0, 0, 0)
        grid_sizer_presents.Add(grid_sizer_vacances, 1, wx.EXPAND, 0)
        
        # Mois
        grid_sizer_presents.Add(self.radio_mois, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mois = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_mois.Add(self.ctrl_mois, 0, 0, 0)
        grid_sizer_mois.Add(self.ctrl_mois_annee, 0, 0, 0)
        grid_sizer_presents.Add(grid_sizer_mois, 1, wx.EXPAND, 0)
        
        # Année
        grid_sizer_presents.Add(self.radio_annee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_annee = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_annee.Add(self.ctrl_annee, 0, 0, 0)
        grid_sizer_presents.Add(grid_sizer_annee, 1, wx.EXPAND, 0)
        
        # Dates
        grid_sizer_presents.Add(self.radio_dates, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_separation_dates, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_presents.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        
        grid_sizer_presents.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_presents, 1, wx.LEFT|wx.EXPAND, 22)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnRadioMethode(self, event=None):
        if self.radio_presents.GetValue() == True :
            etat = True
        else:
            etat = False
        self.radio_vacances.Enable(etat)
        self.radio_mois.Enable(etat)
        self.radio_annee.Enable(etat)
        self.radio_dates.Enable(etat)
        self.OnRadioPeriode() 
    
    def OnRadioPeriode(self, event=None):
        self.ActiveVacances()
        self.ActiveMois()
        self.ActiveAnnee()
        self.ActiveDates()
    
    def ActiveVacances(self, event=None):
        if self.radio_presents.GetValue() == True and self.radio_vacances.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_vacances.Enable(etat)
        self.ctrl_vacances_annee.Enable(etat)

    def ActiveMois(self, event=None):
        if self.radio_presents.GetValue() == True and self.radio_mois.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_mois.Enable(etat)
        self.ctrl_mois_annee.Enable(etat)

    def ActiveAnnee(self, event=None):
        if self.radio_presents.GetValue() == True and self.radio_annee.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_annee.Enable(etat)

    def ActiveDates(self, event=None):
        if self.radio_presents.GetValue() == True and self.radio_dates.GetValue() == True :
            etat = True
        else:
            etat = False
        self.ctrl_date_debut.Enable(etat)
        self.label_separation_dates.Enable(etat)
        self.ctrl_date_fin.Enable(etat)
    
    def GetPeriodeVacances(self):
        """ Récupération des infos Vacances """
        vacances = self.ctrl_vacances.GetPeriode()
        annee = self.ctrl_vacances_annee.GetAnnee() 

        # Vérifie que la période de vacances existe dans la base
        DB = GestionDB.DB()        
        req = _(u"SELECT nom, annee, date_debut, date_fin FROM vacances ORDER BY date_debut;")
        DB.ExecuterReq(req)
        listeVacances = DB.ResultatReq()
        DB.Close()
        date_debut, date_fin = None, None
        for nomTemp, anneeTemp, date_debutTemp, date_finTemp in listeVacances :
            if vacances == nomTemp and annee == anneeTemp :
                date_debut = DateEngEnDateDD(date_debutTemp)
                date_fin = DateEngEnDateDD(date_finTemp)
                break
        
        return vacances, annee, date_debut, date_fin

    def GetPeriodeMois(self):
        """ Récupération des infos Mois """
        mois = self.ctrl_mois.GetMois()
        annee = self.ctrl_mois_annee.GetAnnee() 
        if annee == "" or annee == None or annee <1970 or annee > 2999 :
            return None, None, None, None
        nbreJours = calendar.monthrange(annee, mois)[1]
        date_debut = datetime.date(annee, mois, 1)
        date_fin = datetime.date(annee, mois, nbreJours)
        return mois, annee, date_debut, date_fin

    def GetPeriodeAnnee(self):
        """ Récupération des infos Année """
        annee = self.ctrl_annee.GetAnnee() 
        if annee == "" or annee == None or annee <1970 or annee > 2999 :
            return None, None, None
        date_debut = datetime.date(annee, 1, 1)
        date_fin = datetime.date(annee, 12, 31)
        return annee, date_debut, date_fin

    def GetPeriodeDates(self):
        """ Récupération des infos Dates """
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        return date_debut, date_fin

    def Validation(self):
        mode = None
        dictPeriode = None
        
        if self.radio_inscrits.GetValue() == True :
            mode = "inscrits"
        
        if self.radio_presents.GetValue() == True :
            mode = "presents"
            
            # Vacances
            if self.radio_vacances.GetValue() == True :
                vacances, annee, date_debut, date_fin = self.GetPeriodeVacances() 
                if date_debut == None or date_fin == None :
                    dlg = wx.MessageDialog(self, _(u"La période de vacances que vous avez sélectionné n'a pas été paramétré !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                label = _(u"Les vacances de %s %d (du %s au %s)") % (vacances, annee, DateEngFr(str(date_debut)), DateEngFr(str(date_fin)))
                dictPeriode = {"type":"vacances", "vacances":vacances, "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":label}

            # Mois
            if self.radio_mois.GetValue() == True :
                mois, annee, date_debut, date_fin = self.GetPeriodeMois() 
                if mois == None :
                    dlg = wx.MessageDialog(self, _(u"L'année que avez saisi n'est pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                label = _(u"Le mois de %s %d (du %s au %s)") % (LISTE_MOIS[mois-1], annee, DateEngFr(str(date_debut)), DateEngFr(str(date_fin)))
                dictPeriode = {"type":"mois", "mois":mois, "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":label}

            # Année
            if self.radio_annee.GetValue() == True :
                annee, date_debut, date_fin = self.GetPeriodeAnnee() 
                if annee == None :
                    dlg = wx.MessageDialog(self, _(u"L'année que avez saisi n'est pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                label = _(u"L'année %d (du %s au %s)") % (annee, DateEngFr(str(date_debut)), DateEngFr(str(date_fin)))
                dictPeriode = {"type":"annee", "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":label}

            # Dates
            if self.radio_dates.GetValue() == True :
                date_debut, date_fin = self.GetPeriodeDates() 
                if date_debut == None or self.ctrl_date_debut.Validation() == False :
                    dlg = wx.MessageDialog(self, _(u"La date de début que avez saisi n'est pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                if date_fin == None or self.ctrl_date_fin.Validation() == False :
                    dlg = wx.MessageDialog(self, _(u"La date de fin que avez saisi n'est pas valide !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                if date_debut > date_fin :
                    dlg = wx.MessageDialog(self, _(u"La date de début est supérieure à la date de fin !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                label = _(u"Du %s au %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)))
                dictPeriode = {"type":"dates", "date_debut":date_debut, "date_fin":date_fin, "label":label}

        self.mode = mode
        self.periode = dictPeriode
    
    def GetMode(self):
        return self.mode
    
    def GetPeriode(self):
        return self.periode
    
    def SetMode(self, mode="inscrits"):
        if mode == "inscrits" :
            self.radio_inscrits.SetValue(True)
        else:
            self.radio_presents.SetValue(True)
    
    def SetPeriode(self, dictPeriode=None):
        if dictPeriode == None :
            return
        
        # Vacances
        if dictPeriode["type"] == "vacances" :
            self.ctrl_vacances.SetPeriode(dictPeriode["vacances"])
            self.ctrl_vacances_annee.SetAnnee(dictPeriode["annee"])
            self.radio_vacances.SetValue(True)
        # Mois
        if dictPeriode["type"] == "mois" :
            self.ctrl_mois.SetMois(dictPeriode["mois"])
            self.ctrl_mois_annee.SetAnnee(dictPeriode["annee"])
            self.radio_mois.SetValue(True)
        # Année
        if dictPeriode["type"] == "annee" :
            self.ctrl_annee.SetAnnee(dictPeriode["annee"])
            self.radio_annee.SetValue(True)
        # Dates
        if dictPeriode["type"] == "dates" :
            self.ctrl_date_debut.SetDate(dictPeriode["date_debut"])
            self.ctrl_date_fin.SetDate(dictPeriode["date_fin"])
            self.radio_dates.SetValue(True)

    def SetParametres(self, mode="inscrits", periode=None):
        self.SetMode(mode)
        self.SetPeriode(periode)
        self.OnRadioMethode() 
        
        


##class MyFrame(wx.Frame):
##    def __init__(self, *args, **kwds):
##        wx.Frame.__init__(self, *args, **kwds)
##        panel = wx.Panel(self, -1)
##        sizer_1 = wx.BoxSizer(wx.VERTICAL)
##        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
##        self.SetSizer(sizer_1)
##        self.ctrl= PanelMode(panel)
##        sizer_2 = wx.BoxSizer(wx.VERTICAL)
##        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
##        panel.SetSizer(sizer_2)
##        self.SetSize((1100, 900))
##        self.Layout()
##        self.CentreOnScreen()


class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Stats_parametres", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.dictParametres = {}
        
        # Activités
        self.box_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        
        # Mode
        self.box_mode_staticbox = wx.StaticBox(self, -1, _(u"Mode de calcul"))
        self.ctrl_mode = CTRL_Mode(self)

        # Options
##        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
##        self.label_presents = wx.StaticText(self, -1, _(u"Méthode de calcul :"))
##        self.radio_presents_1 = wx.RadioButton(self, -1, _(u"Présents"), style = wx.RB_GROUP)
##        self.radio_presents_2 = wx.RadioButton(self, -1, _(u"Inscrits"))
##        self.radio_presents_1.SetValue(True) 
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
##        dateJour = datetime.date.today() 
##        self.ctrl_date_debut.SetDate("01/01/%d" % dateJour.year)
##        self.ctrl_date_fin.SetDate("31/12/%d" % dateJour.year)
        
        

    def __set_properties(self):
        self.SetTitle(_(u"Sélection des paramètres"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((460, 600))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Activités
        box_activites = wx.StaticBoxSizer(self.box_activites_staticbox, wx.VERTICAL)
        box_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_activites, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        # Mode
        box_mode = wx.StaticBoxSizer(self.box_mode_staticbox, wx.VERTICAL)
        box_mode.Add(self.ctrl_mode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_mode, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
##        # Options
##        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
##        grid_sizer_options = wx.FlexGridSizer(rows=4, cols=2, vgap=5, hgap=5)
##        grid_sizer_options.Add(self.label_presents, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_presents.Add(self.radio_presents_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_presents.Add(self.radio_presents_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_options.Add(grid_sizer_presents, 1, wx.EXPAND, 0)
##        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
##        grid_sizer_base.Add(box_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioPeriode(self, event): 
        etat = self.radio_periode_1.GetValue()
        self.ctrl_date_debut.Enable(etat)
        self.ctrl_date_fin.Enable(etat)

    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("Statistiques")

    def SetParametres(self, dictParametres={}) :
        if dictParametres.has_key("mode") :
            mode = dictParametres["mode"]
        else :
            mode = "inscrits"
        if dictParametres.has_key("periode") :
            periode = dictParametres["periode"]
        else :
            periode = None
        if dictParametres.has_key("listeActivites") :
            listeActivites = dictParametres["listeActivites"]
        else :
            listeActivites = []
            
        self.ctrl_mode.SetParametres(mode, periode)
        self.ctrl_activites.SetActivites(listeActivites) 

    def OnBoutonOk(self, event): 
        self.dictParametres = {"init":datetime.datetime.now()}
        
        # Mode
        if self.ctrl_mode.Validation()  == False :
            return
        self.dictParametres["mode"] = self.ctrl_mode.GetMode()
        self.dictParametres["periode"] = self.ctrl_mode.GetPeriode()
        
        # Activités
        self.listeActivites = self.ctrl_activites.GetActivites() 
        self.listeActivites.sort()
        self.dictActivites = self.ctrl_activites.GetDictActivites() 
        if len(self.listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner une activité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        self.dictParametres["listeActivites"] = self.listeActivites
        self.dictParametres["dictActivites"] = self.dictActivites
        
        # Options


        
        # Fermer fenêtre
        self.EndModal(wx.ID_OK)
        
    def GetDictParametres(self):
        return self.dictParametres
            
    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)
    
    def OnCheckActivites(self):
        pass



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()

##if __name__ == '__main__':
##    app = wx.App(0)
##    #wx.InitAllImageHandlers()
##    frame_1 = MyFrame(None, -1, "TEST")
##    app.SetTopWindow(frame_1)
##    frame_1.Show()
##    app.MainLoop()
