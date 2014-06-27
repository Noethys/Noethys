#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import datetime
import calendar
import GestionDB
import CTRL_Saisie_date


LISTE_MOIS = (u"Janvier", u"Février", u"Mars", u"Avril", u"Mai", u"Juin", u"Juillet", u"Août", u"Septembre", u"Octobre", u"Novembre", u"Décembre")

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

def DateComplete(dateDD):
    """ Transforme une date DD en date complète : Ex : lundi 15 janvier 2008 """
    listeJours = (u"Lundi", u"Mardi", u"Mercredi", u"Jeudi", u"Vendredi", u"Samedi", u"Dimanche")
    listeMois = (u"janvier", u"février", u"mars", u"avril", u"mai", u"juin", u"juillet", u"août", u"septembre", u"octobre", u"novembre", u"décembre")
    dateComplete = listeJours[dateDD.weekday()] + " " + str(dateDD.day) + " " + listeMois[dateDD.month-1] + " " + str(dateDD.year)
    return dateComplete

def DateEngEnDateDD(dateEng):
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))
        
def PeriodeComplete(mois, annee):
    periodeComplete = u"%s %d" % (LISTE_MOIS[mois-1], annee)
    return periodeComplete



class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent  
        self.selection = True
        
        # Type
        self.box_type_staticbox = wx.StaticBox(self, -1, u"Type")
        self.radio_type_prestations = wx.RadioButton(self, -1, u"Prestations", style=wx.RB_GROUP)
        self.radio_type_factures = wx.RadioButton(self, -1, u"Factures")
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, u"Options")
        self.check_impayes = wx.CheckBox(self, -1, u"Uniquement les impayés")
        self.check_conso = wx.CheckBox(self, -1, u"Détailler les consommations")
        self.check_regroupement = wx.CheckBox(self, -1, u"Regrouper par")
        self.ctrl_regroupement_date = wx.Choice(self, -1, choices=["Date", u"Mois", u"Année"])
        
        # Période
        self.box_periode_staticbox = wx.StaticBox(self, -1, u"Période")
        self.radio_tout = wx.RadioButton(self, -1, u"Toutes les périodes", style=wx.RB_GROUP)
        self.radio_dates = wx.RadioButton(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, -1, u"au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        self.radio_apartirde = wx.RadioButton(self, -1, u"A partir du")
        self.ctrl_date_apartirde = CTRL_Saisie_date.Date2(self)
        self.radio_jusquau = wx.RadioButton(self, -1, u"Jusqu'au")
        self.ctrl_date_jusquau = CTRL_Saisie_date.Date2(self)
        self.radio_mois = wx.RadioButton(self, -1, u"Mois de")
        self.ctrl_mois = wx.Choice(self, -1, choices=[u"Janvier", u"Février", u"Mars", u"Avril", u"Mai", u"Juin", u"Juillet", u"Août", u"Septembre", u"Octobre", u"Novembre", u"Décembre"])
        self.ctrl_mois_annee = wx.SpinCtrl(self, -1, str(datetime.date.today().year), min=1900, max=2099)
        self.radio_annee = wx.RadioButton(self, -1, u"Année")
        self.ctrl_annee = wx.SpinCtrl(self, -1, u"2012", min=1900, max=2099)
        self.radio_vacances = wx.RadioButton(self, -1, u"Vacances de")
        self.ctrl_vacances = wx.Choice(self, -1, choices=["Février", u"Pâques", u"Eté", u"Toussaint", u"Noël"])
        self.ctrl_vacances_annee = wx.SpinCtrl(self, -1, u"2012", min=1900, max=2099)
        
        # Boutons
        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioType, self.radio_type_prestations)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioType, self.radio_type_factures)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_tout)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_dates)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_apartirde)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_jusquau)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_mois)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_annee)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPeriode, self.radio_vacances)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contrôles
        self.dictVacances = self.GetListeVacances() 
        self.OnRadioType(None)
        self.OnRadioPeriode(None)

    def __set_properties(self):
        self.SetTitle(u"Saisie d'une période")
        self.radio_type_prestations.SetToolTipString(u"Sélectionnez le type de données à afficher")
        self.radio_type_factures.SetToolTipString(u"Sélectionnez le type de données à afficher")
        self.check_impayes.SetToolTipString(u"Uniquement les impayés")
        self.check_regroupement.SetToolTipString(u"Regroupement des prestations")
        self.ctrl_regroupement_date.SetSelection(0)
        self.check_conso.SetToolTipString(u"Détailler les consommations")
        self.ctrl_mois.SetSelection(0)
        self.ctrl_mois_annee.SetMinSize((60, -1))
        self.ctrl_annee.SetMinSize((60, -1))
        self.ctrl_vacances.SetSelection(0)
        self.ctrl_vacances_annee.SetMinSize((60, -1))
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        box_periode = wx.StaticBoxSizer(self.box_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=9, cols=1, vgap=10, hgap=10)
        sizer_vacances = wx.BoxSizer(wx.HORIZONTAL)
        sizer_annee = wx.BoxSizer(wx.HORIZONTAL)
        sizer_mois = wx.BoxSizer(wx.HORIZONTAL)
        sizer_jusquau = wx.BoxSizer(wx.HORIZONTAL)
        sizer_apartirde = wx.BoxSizer(wx.HORIZONTAL)
        sizer_dates = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        sizer_regroupement = wx.BoxSizer(wx.HORIZONTAL)
        
        # Type
        box_type = wx.StaticBoxSizer(self.box_type_staticbox, wx.VERTICAL)
        box_type.Add(self.radio_type_prestations, 0, wx.ALL|wx.EXPAND, 10)
        box_type.Add(self.radio_type_factures, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        grid_sizer_droit.Add(box_type, 1, wx.EXPAND, 0)
        
        # Options
        grid_sizer_options = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_options.Add(self.check_impayes, 0, 0, 0)
        grid_sizer_options.Add(self.check_conso, 0, 0, 0)
        sizer_regroupement.Add(self.check_regroupement, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_regroupement.Add(self.ctrl_regroupement_date, 0, wx.LEFT, 5)
        grid_sizer_options.Add(sizer_regroupement, 1, wx.EXPAND, 0)
        grid_sizer_options.AddGrowableCol(0)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_droit.Add(box_options, 1, wx.EXPAND, 0)
        grid_sizer_droit.AddGrowableRow(1)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        grid_sizer_periode.Add(self.radio_tout, 1, wx.EXPAND, 0)
        sizer_dates.Add(self.radio_dates, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_dates.Add(self.ctrl_date_debut, 0, wx.LEFT|wx.RIGHT, 5)
        sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_dates.Add(self.ctrl_date_fin, 0, wx.LEFT|wx.RIGHT, 5)
        grid_sizer_periode.Add(sizer_dates, 1, wx.EXPAND, 0)
        sizer_apartirde.Add(self.radio_apartirde, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_apartirde.Add(self.ctrl_date_apartirde, 0, wx.LEFT, 5)
        grid_sizer_periode.Add(sizer_apartirde, 1, wx.EXPAND, 0)
        sizer_jusquau.Add(self.radio_jusquau, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_jusquau.Add(self.ctrl_date_jusquau, 0, wx.LEFT, 5)
        grid_sizer_periode.Add(sizer_jusquau, 1, wx.EXPAND, 0)
        sizer_mois.Add(self.radio_mois, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_mois.Add(self.ctrl_mois, 0, wx.LEFT|wx.RIGHT, 5)
        sizer_mois.Add(self.ctrl_mois_annee, 0, 0, 0)
        grid_sizer_periode.Add(sizer_mois, 1, wx.EXPAND, 0)
        sizer_annee.Add(self.radio_annee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_annee.Add(self.ctrl_annee, 0, wx.LEFT, 5)
        grid_sizer_periode.Add(sizer_annee, 1, wx.EXPAND, 0)
        sizer_vacances.Add(self.radio_vacances, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_vacances.Add(self.ctrl_vacances, 0, wx.LEFT|wx.RIGHT, 5)
        sizer_vacances.Add(self.ctrl_vacances_annee, 0, 0, 0)
        grid_sizer_periode.Add(sizer_vacances, 1, wx.EXPAND, 0)
        grid_sizer_periode.AddGrowableCol(0)
        box_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_contenu.Add(box_periode, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        
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
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioType(self, event): 
        # Si prestations
        if self.radio_type_prestations.GetValue() == True :
            self.check_impayes.Enable(True)
            self.check_regroupement.Enable(True)
            self.ctrl_regroupement_date.Enable(True)
            self.check_conso.Enable(True)
        # Si factures
        if self.radio_type_factures.GetValue() == True :
            self.check_impayes.Enable(True)
            self.check_regroupement.Enable(False)
            self.ctrl_regroupement_date.Enable(False)
            self.check_conso.Enable(False)

    def OnRadioPeriode(self, event): 
        # Dates
        if self.radio_dates.GetValue() == True :
            self.ctrl_date_debut.Enable(True)
            self.ctrl_date_fin.Enable(True)
        else:
            self.ctrl_date_debut.Enable(False)
            self.ctrl_date_fin.Enable(False)
        # A partir de
        if self.radio_apartirde.GetValue() == True :
            self.ctrl_date_apartirde.Enable(True)
        else:
            self.ctrl_date_apartirde.Enable(False)
        # jusqu'au
        if self.radio_jusquau.GetValue() == True :
            self.ctrl_date_jusquau.Enable(True)
        else:
            self.ctrl_date_jusquau.Enable(False)
        # Mois
        if self.radio_mois.GetValue() == True :
            self.ctrl_mois.Enable(True)
            self.ctrl_mois_annee.Enable(True)
        else:
            self.ctrl_mois.Enable(False)
            self.ctrl_mois_annee.Enable(False)
        # Année
        if self.radio_annee.GetValue() == True :
            self.ctrl_annee.Enable(True)
        else:
            self.ctrl_annee.Enable(False)
        # Vacances
        if self.radio_vacances.GetValue() == True :
            self.ctrl_vacances.Enable(True)
            self.ctrl_vacances_annee.Enable(True)
        else:
            self.ctrl_vacances.Enable(False)
            self.ctrl_vacances_annee.Enable(False)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Editerunrelevdesprestations")

    def OnBoutonAnnuler(self, event): 
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_CANCEL)

    def GetListeVacances(self):
        DB = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictVacances = {}
        for date_debut, date_fin, nom, annee in listeDonnees :
            dictVacances[(nom, annee)] = (DateEngEnDateDD(date_debut), DateEngEnDateDD(date_fin))
        return dictVacances

    def GetType(self):
        if self.radio_type_prestations.GetValue() == True : return "prestations"
        if self.radio_type_factures.GetValue() == True : return "factures"
        
    def GetOptions(self):
        # Prestations
        if self.GetType() == "prestations" :
            if self.check_regroupement.GetValue() == True :
                if self.ctrl_regroupement_date.GetSelection() == 0 : regroupement = "date"
                if self.ctrl_regroupement_date.GetSelection() == 1 : regroupement = "mois"
                if self.ctrl_regroupement_date.GetSelection() == 2 : regroupement = "annee"
            else :
                regroupement = None
            dictOptions = {
                "impayes" : self.check_impayes.GetValue(),
                "regroupement" : regroupement,
                "conso" : self.check_conso.GetValue(),
                }
        # Factures
        if self.GetType() == "factures" :
            dictOptions = {
                "impayes" : self.check_impayes.GetValue(),
                }
                
        return dictOptions

    def GetPeriode(self):
        date_debut = None
        date_fin = None

        # Toutes les périodes
        if self.radio_tout.GetValue() == True :
            date_debut = datetime.date(1900, 1, 1)
            date_fin = datetime.date(2999, 1, 1)
            parametres = {"code":"tout", "date_debut":date_debut, "date_fin":date_fin, "label":u"Toutes les périodes"}

        # Dates
        if self.radio_dates.GetValue() == True :
            date_debut = self.ctrl_date_debut.GetDate()
            date_fin = self.ctrl_date_fin.GetDate()
            parametres = {"code":"dates", "date_debut":date_debut, "date_fin":date_fin, "label":u"Du %s au %s" % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin))) }
        
        # A partir de
        if self.radio_apartirde.GetValue() == True :
            date_debut = self.ctrl_date_apartirde.GetDate() 
            date_fin = datetime.date(2999, 1, 1)
            parametres = {"code":"apartirde", "date_debut":date_debut, "date_fin":date_fin, "label":u"A partir du %s" % DateEngFr(str(date_debut)) }
            
        # Jusqu'au
        if self.radio_jusquau.GetValue() == True :
            date_debut = datetime.date(1900, 1, 1)
            date_fin = self.ctrl_date_jusquau.GetDate() 
            parametres = {"code":"jusquau", "date_debut":date_debut, "date_fin":date_fin, "label":u"Jusqu'au %s" % DateEngFr(str(date_fin)) }
            
        # Mois
        if self.radio_mois.GetValue() == True :
            mois = self.ctrl_mois.GetSelection() + 1
            annee = self.ctrl_mois_annee.GetValue()
            date_debut = datetime.date(annee, mois, 1)
            date_fin = datetime.date(annee, mois, calendar.monthrange(annee, mois)[1])
            parametres = {"code":"mois", "mois":mois, "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":u"Mois de %s %d" % (LISTE_MOIS[mois-1], annee) }
            
        # Année
        if self.radio_annee.GetValue() == True :
            annee = self.ctrl_annee.GetValue()
            date_debut = datetime.date(annee, 1, 1)
            date_fin = datetime.date(annee, 12, 31)
            parametres = {"code":"annee", "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":u"Année %d" % annee }
            
        # Vacances
        if self.radio_vacances.GetValue() == True :
            nom = self.ctrl_vacances.GetStringSelection()
            annee = self.ctrl_vacances_annee.GetValue()
            if self.dictVacances.has_key((nom, annee)) :
                date_debut, date_fin = self.dictVacances[nom, annee]
            parametres = {"code":"vacances", "nom":nom, "annee":annee, "date_debut":date_debut, "date_fin":date_fin, "label":u"Vacances de %s %d" % (nom, annee)}
        
        return parametres
    
    def SetType(self, typeDonnees="prestations") :
        if typeDonnees == "prestations" : self.radio_type_prestations.SetValue(True)
        if typeDonnees == "factures" : self.radio_type_factures.SetValue(True)
        self.OnRadioType(None)

    def SetOptions(self, dictOptions={}):
        # Impayés
        if dictOptions.has_key("impayes") :
            self.check_impayes.SetValue(dictOptions["impayes"])
        # Regroupement
        if dictOptions.has_key("regroupement") :
            if dictOptions["regroupement"] == "date" :
                self.ctrl_regroupement_date.SetSelection(0)
                self.check_regroupement.SetValue(True) 
            elif dictOptions["regroupement"] == "mois" :
                self.ctrl_regroupement_date.SetSelection(1)
                self.check_regroupement.SetValue(True) 
            elif dictOptions["regroupement"] == "annee" :
                self.ctrl_regroupement_date.SetSelection(2)
                self.check_regroupement.SetValue(True) 
        # Détail consommations
        if dictOptions.has_key("conso") :
            self.check_conso.SetValue(dictOptions["conso"])

    def SetPeriode(self, parametres={}):
        code = parametres["code"]
        
        # Tout
        if code == "tout" :
            self.radio_tout.SetValue(True)

        # Dates
        if code == "dates" :
            self.radio_dates.SetValue(True)
            self.ctrl_date_debut.SetDate(parametres["date_debut"])
            self.ctrl_date_fin.SetDate(parametres["date_fin"])
        
        # A partir de
        if code == "apartirde" :
            self.radio_apartirde.SetValue(True)
            self.ctrl_date_apartirde.SetDate(parametres["date_debut"])

        # Jusqu'au
        if code == "jusquau" :
            self.radio_jusquau.SetValue(True)
            self.ctrl_date_jusquau.SetDate(parametres["date_fin"])

        # Mois
        if code == "mois" :
            self.radio_mois.SetValue(True)
            self.ctrl_mois.SetSelection(parametres["mois"]-1)
            self.ctrl_mois_annee.SetValue(parametres["annee"])

        # Année
        if code == "annee" :
            self.radio_annee.SetValue(True)
            self.ctrl_annee.SetValue(parametres["annee"])

        # Vacances
        if code == "vacances" :
            self.radio_vacances.SetValue(True)
            self.ctrl_vacances.SetStringSelection(parametres["nom"])
            self.ctrl_vacances_annee.SetValue(parametres["annee"])

        self.OnRadioPeriode(None)
    
    def GetDonnees(self):
        typeDonnees = self.GetType() 
        dictPeriode = self.GetPeriode()
        dictOptions = self.GetOptions()
        return {"selection":self.selection, "type":typeDonnees, "periode":dictPeriode, "options":dictOptions, "date_debut":dictPeriode["date_debut"], "date_fin":dictPeriode["date_fin"],}
    
    def SetDonnees(self, dictParametres={}):
        self.selection = dictParametres["selection"]
        self.SetType(dictParametres["type"])
        self.SetPeriode(dictParametres["periode"])
        self.SetOptions(dictParametres["options"])
        
    def OnBoutonOk(self, event): 
        # Validation de la période
        parametres = self.GetPeriode() 
        if parametres["date_debut"] == None or parametres["date_fin"] == None :
            dlg = wx.MessageDialog(self, u"La période sélectionnée ne semble pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    
    # Tests
    dialog_1.SetDonnees({
        "selection" : True,
        "type" : "factures", 
        "periode" : {"code":"mois", "mois":2, "annee":2011}, 
        "options" : {"details":True, "regroupement":"mois"},
        })
    
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
