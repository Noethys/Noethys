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
import datetime
import time
import sys
import math

import GestionDB
import CTRL_Bandeau
import CTRL_Selection_activites
import CTRL_Saisie_date
import DLG_calendrier_simple
import CTRL_Coefficients_siej
import OL_Liste_regimes
import UTILS_Organisateur

import FonctionsPerso


def ArrondirHeureSup(heures, minutes, pas): 
    """ Arrondi l'heure au pas supérieur """
    for x in range(0, 60, pas):
        if x >= minutes :
            return (heures, x)
    return (heures+1, 0)

def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text

##def FormateValeur(valeur, mode="decimal"):
##    if mode == "decimal" :
##        return valeur
##    if mode == "heure" :
##        hr, dec = str(valeur).split(".")
##        if len(dec) == 1 : 
##            mn = int(dec) * 0.1
##        else:
##            mn = int(dec) * 0.01
##        mn = mn * 60 #int(dec)*60/100.0
##        mn = math.ceil(mn)
##        return u"%sh%02d" % (hr, mn)

def FormateValeur(valeur, mode="decimal"):
    heures = (valeur.days*24) + (valeur.seconds/3600)
    minutes = valeur.seconds%3600/60
    
    if mode == "decimal" :
        minDecimal = int(minutes)*100/60
        return float("%s.%s" % (heures, minDecimal))

    if mode == "heure" :
        return "%dh%02d" % (heures, minutes)


##    if valeur == None or valeur == "" and mode == "decimal" : return 0.00
##    if valeur == None or valeur == "" and mode != "decimal" : return "0h00"
##    if type(valeur) == float and mode == "decimal" : return valeur
##    if type(valeur) == str :
##        hr, mn = valeur[1:].split(":")
##    if type(valeur) == datetime.timedelta :
##        hr, mn, sc = str(valeur).split(":")
##    if mode == "decimal" :
##        # Mode décimal
##        minDecimal = int(mn)*100/60
##        texte = "%s.%s" % (hr, minDecimal)
##        resultat = float(texte)
##    else:
##        # Mode Heure
##        if hr == "00" : hr = "0"
##        resultat = u"%s:%s" % (hr, mn)
##    return resultat



class CTRL_Jours(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.liste_jours = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
        
        # Périodes scolaires
        self.label_periodes_scolaires = wx.StaticText(self, -1,u"Hors vacances :")
        self.CreationCaseJours("scolaire")
        
        # Périodes de vacances
        self.label_periodes_vacances = wx.StaticText(self, -1,u"Vacances :")
        self.CreationCaseJours("vacances")
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
                
        # Périodes scolaires
        grid_sizer_base.Add(self.label_periodes_scolaires, 0, 0, 0)

        grid_sizer_scolaire = wx.FlexGridSizer(rows=1, cols=7, vgap=3, hgap=3)
        for jour in self.liste_jours :
            exec("grid_sizer_scolaire.Add(self.check_scolaire_%s, 0, 0, 0)" % jour)
        grid_sizer_base.Add(grid_sizer_scolaire, 1, wx.EXPAND, 0)
        
        # Périodes de vacances
        grid_sizer_base.Add(self.label_periodes_vacances, 0, wx.LEFT, 10)
        
        grid_sizer_vacances = wx.FlexGridSizer(rows=1, cols=7, vgap=3, hgap=3)
        for jour in self.liste_jours :
            exec("grid_sizer_vacances.Add(self.check_vacances_%s, 0, 0, 0)" % jour)
        grid_sizer_base.Add(grid_sizer_vacances, 1, wx.EXPAND, 0)
                
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
    
    def CreationCaseJours(self, periode="scolaire"):
        for jour in self.liste_jours :
            exec("self.check_%s_%s = wx.CheckBox(self, -1,u'%s')" % (periode, jour, jour[0].upper()) )
            exec("self.check_%s_%s.SetToolTipString(u'%s')" % (periode, jour, jour.capitalize()) )
            exec("self.check_%s_%s.SetValue(True)" % (periode, jour))

    def GetJours(self, periode="scolaire"):
        listeTemp = []
        index = 0
        for jour in self.liste_jours :
            exec("etat = self.check_%s_%s.GetValue()" % (periode, jour))
            if etat == True :
                listeTemp.append(index)
            index += 1
        return listeTemp
    

class CTRL_Etats(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.check_attente = wx.CheckBox(self, -1, u"Pointage en attente")
        self.check_present = wx.CheckBox(self, -1, u"Présent")
        self.check_absentj = wx.CheckBox(self, -1, u"Absence justifiée")
        self.check_absenti = wx.CheckBox(self, -1, u"Absence injustifiée")
        
        self.check_attente.SetValue(True) 
        self.check_present.SetValue(True) 
        self.check_absentj.SetValue(True) 
        self.check_absenti.SetValue(True) 
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_attente, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.check_present, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.check_absentj, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.check_absenti, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def GetEtats(self):
        listeEtats = []
        if self.check_attente.GetValue() == True : listeEtats.append("reservation")
        if self.check_present.GetValue() == True : listeEtats.append("present")
        if self.check_absentj.GetValue() == True : listeEtats.append("absentj")
        if self.check_absenti.GetValue() == True : listeEtats.append("absenti")
        return listeEtats


class CTRL_QF(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.check_qf = wx.CheckBox(self, -1, u"Quotient familial de la famille compris entre")
        self.ctrl_qf_min = wx.SpinCtrl(self, -1, "0", size=(70, -1), max=999999)
        self.ctrl_qf_min.SetToolTipString(u"QF min (inclus)")
        self.label_et = wx.StaticText(self, -1, u"et")
        self.ctrl_qf_max = wx.SpinCtrl(self, -1, "0", size=(70, -1), max=999999)
        self.ctrl_qf_max.SetToolTipString(u"QF max (inclus)")
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_base.Add(self.check_qf, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_qf_min, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.label_et, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_qf_max, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        
        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, self.check_qf)
        self.OnCheck() 
    
    def OnCheck(self, event=None):
        self.ctrl_qf_min.Enable(self.check_qf.GetValue())
        self.ctrl_qf_max.Enable(self.check_qf.GetValue())
        
    def GetDonnees(self):
        if self.check_qf.GetValue() == True :
            qf_min = int(self.ctrl_qf_min.GetValue())
            qf_max = int(self.ctrl_qf_max.GetValue())
            return (qf_min, qf_max)
        return None
    


class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, u"Période de référence")
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, u"Au")
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Séparation
        self.staticbox_regroupement_staticbox = wx.StaticBox(self, -1, u"Regroupement")
        self.radio_regroupement_aucun = wx.RadioButton(self, -1, u"Aucun", style=wx.RB_GROUP)
        self.radio_regroupement_age = wx.RadioButton(self, -1, u"Par âge :")
        self.ctrl_age = wx.SpinCtrl(self, -1, "", size=(70, -1))
        self.label_age = wx.StaticText(self, -1, u"ans")
        self.radio_regroupement_dateNaiss = wx.RadioButton(self, -1, u"Par date de naiss. :")
        self.ctrl_dateNaiss = CTRL_Saisie_date.Date(self)
        
        # Affichage Heure/Décimal
        self.staticbox_affichage_staticbox = wx.StaticBox(self, -1, u"Affichage")
        self.radio_affichage_heure = wx.RadioButton(self, -1, u"Heure", style=wx.RB_GROUP)
        self.radio_affichage_decimal = wx.RadioButton(self, -1, u"Décimal")
        self.check_detail = wx.CheckBox(self, -1, u"Afficher détail par activité")
        
        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, u"Activités")
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        
        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRegroupement, self.radio_regroupement_aucun)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRegroupement, self.radio_regroupement_age)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRegroupement, self.radio_regroupement_dateNaiss)
        
        # Init Contrôles
        self.OnRadioRegroupement(None)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(u"Saisissez la date de début de période")
        self.ctrl_date_fin.SetToolTipString(u"Saisissez la date de fin de période")
        self.ctrl_age.SetToolTipString(u"Saisissez un âge (en années)")
        self.ctrl_dateNaiss.SetToolTipString(u"Saisissez une date de naissance")
        self.check_detail.SetToolTipString(u"Cochez cette case pour afficher le détail par activité")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Regroupement
        staticbox_regroupement = wx.StaticBoxSizer(self.staticbox_regroupement_staticbox, wx.VERTICAL)
        grid_sizer_regroupement = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        
        grid_sizer_regroupement.Add(self.radio_regroupement_aucun, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        
        grid_sizer_age = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_age.Add(self.radio_regroupement_age, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_age.Add(self.ctrl_age, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_age.Add(self.label_age, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_regroupement.Add(grid_sizer_age, 0, wx.EXPAND, 0)
        
        grid_sizer_dateNaiss = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_dateNaiss.Add(self.radio_regroupement_dateNaiss, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dateNaiss.Add(self.ctrl_dateNaiss, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_regroupement.Add(grid_sizer_dateNaiss, 0, wx.EXPAND, 0)

        staticbox_regroupement.Add(grid_sizer_regroupement, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_regroupement, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Affichage Heure/Décimal
        staticbox_affichage = wx.StaticBoxSizer(self.staticbox_affichage_staticbox, wx.VERTICAL)
        grid_sizer_affichage = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_affichage_heure, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_affichage_decimal, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_affichage.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        staticbox_affichage.Add(self.check_detail, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_affichage, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)
    
    def OnRadioRegroupement(self, event):
        if self.radio_regroupement_aucun.GetValue() == True :
            self.ctrl_age.Enable(False)
            self.ctrl_dateNaiss.Enable(False)
        if self.radio_regroupement_age.GetValue() == True :
            self.ctrl_age.Enable(True)
            self.ctrl_dateNaiss.Enable(False)
        if self.radio_regroupement_dateNaiss.GetValue() == True :
            self.ctrl_age.Enable(False)
            self.ctrl_dateNaiss.Enable(True)
    
    def GetRegroupement(self):
        if self.radio_regroupement_aucun.GetValue() == True :
            regroupement = None
        if self.radio_regroupement_age.GetValue() == True :
            regroupement = ("age", self.ctrl_age.GetValue())
        if self.radio_regroupement_dateNaiss.GetValue() == True :
            regroupement = ("dateNaiss", self.ctrl_dateNaiss.GetDate())
        return regroupement
    
    def ValidationRegroupement(self):
        if self.radio_regroupement_age.GetValue() == True :
            if self.ctrl_age.GetValue() == "" :
                return False
        if self.radio_regroupement_dateNaiss.GetValue() == True :
            if self.ctrl_dateNaiss.GetDate() == None :
                return False
            if self.ctrl_dateNaiss.FonctionValiderDate() == False :
                return False
        return True
        
    def OnBoutonAfficher(self, event):
        """ Validation des données saisies """
        # Vérifie date de référence
        date_reference = self.ctrl_date.GetDate()
        if self.ctrl_date.FonctionValiderDate() == False or date_reference == None :
            dlg = wx.MessageDialog(self, u"La date de référence ne semble pas valide !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date.SetFocus()
            return False
                
        # Vérifie les activités sélectionnées
        if self.radio_groupes.GetValue() == True :
            listeActivites = self.ctrl_groupes.GetIDcoches()
        else:
            listeActivites = self.ctrl_activites.GetIDcoches()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune activité !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Envoi des données
        self.parent.MAJ(date_reference=date_reference, listeActivites=listeActivites)
        
        return True
    
    def GetPeriode(self):
        date_debut = self.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_date_fin.GetDate()
        return date_debut, date_fin
    
    def OnChoixDate(self):
        date_debut, date_fin = self.GetPeriode() 
        self.parent.ctrl_coeff.periode = (date_debut, date_fin)
        self.parent.ctrl_coeff.MAJ() 

    def OnCheckActivites(self):
        date_debut, date_fin = self.GetPeriode() 
        self.parent.ctrl_coeff.periode = (date_debut, date_fin)
        self.parent.ctrl_coeff.listeActivites = self.ctrl_activites.GetActivites() 
        self.parent.ctrl_coeff.MAJ() 
    
    def GetActivites(self):
        return self.ctrl_activites.GetActivites() 
    
    def GetModeAffichage(self):
        if self.radio_affichage_decimal.GetValue() == True :
            return "decimal"
        else:
            return "heure"
    
    def GetModeDetail(self):
        return self.check_detail.GetValue()
    
    def GetLabelRegroupement(self):
        regroupement = self.GetRegroupement() 
        if regroupement == None :
            texteRegroupement = u"Sans regroupement"
        elif regroupement[0] == "age" :
            texteRegroupement = u"Regroupement par âge : %d ans" % regroupement[1]
        else :
            texteRegroupement = u"Regroupement par date de naissance : %s" % DateEngFr(str(regroupement[1]))
        return texteRegroupement
    
    def GetNomsActivites(self):
        listeTemp = self.ctrl_activites.GetLabelActivites()
        return ", ".join(listeTemp)

    def GetLabelParametres(self):
        # Label Paramètres
        listeParametres = [ 
            u"Période du %s au %s" % (DateEngFr(str(self.ctrl_date_debut.GetDate())), DateEngFr(str(self.ctrl_date_fin.GetDate()))),
            self.GetLabelRegroupement(),
            u"Activités : %s" % self.GetNomsActivites(),
            ]
        labelParametres = " | ".join(listeParametres)
        return labelParametres

# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = u"Vous pouvez ici générer l'état global des consommations (Notez que les résultats sont conformes à l'interface SIEJ de la CAF). Commencez par saisir une période de référence, sélectionnez une méthode de regroupement (ex : par âge : '6' ans pour les accueils de loisirs), sélectionnez une ou plusieurs activités puis choisissez une méthode de calcul par unité souhaitée."
        titre = u"Etat global des consommations"
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Tableaux.png")
        self.SetTitle(titre)
        
        # Panel Paramètres
        self.ctrl_parametres = Parametres(self)
        
        # CTRL Coefficients
        self.staticbox_coeff_staticbox = wx.StaticBox(self, -1, u"Paramètres de calcul")
        self.ctrl_coeff = CTRL_Coefficients_siej.CTRL(self)

        # Filtres
        self.staticbox_filtres_staticbox = wx.StaticBox(self, -1, u"Filtres")
        self.label_jours = wx.StaticText(self, -1, u"Périodes :")
        self.ctrl_jours = CTRL_Jours(self)
        self.label_etats = wx.StaticText(self, -1, u"Etats :")
        self.ctrl_etats = CTRL_Etats(self)
        self.label_qf = wx.StaticText(self, -1, u"QF :")
        self.ctrl_qf = CTRL_QF(self)

        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Apercu_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_fermer = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Fermer_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Données Test
        anneeActuelle = datetime.date.today().year
        self.ctrl_parametres.ctrl_date_debut.SetDate(datetime.date(anneeActuelle, 1, 1))
        self.ctrl_parametres.ctrl_date_fin.SetDate(datetime.date(anneeActuelle, 12, 31))
                

    def __set_properties(self):
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour créer un aperçu des résultats (PDF)")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_fermer.SetToolTipString(u"Cliquez ici pour fermer")
        self.SetMinSize((1020, 720))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        # Ctrl des coeff
        staticbox_coeff = wx.StaticBoxSizer(self.staticbox_coeff_staticbox, wx.VERTICAL)
        staticbox_coeff.Add(self.ctrl_coeff, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_coeff, 1, wx.EXPAND, 5)

        # Ctrl des filtres
        staticbox_filtres = wx.StaticBoxSizer(self.staticbox_filtres_staticbox, wx.VERTICAL)
        grid_sizer_filtres = wx.FlexGridSizer(rows=3, cols=2, vgap=10, hgap=10)
        grid_sizer_filtres.Add(self.label_jours, 1,wx.ALIGN_RIGHT| wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_jours, 1, wx.EXPAND, 0)
        grid_sizer_filtres.Add(self.label_etats, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_etats, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.label_qf, 1, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_filtres.Add(self.ctrl_qf, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_filtres.Add(grid_sizer_filtres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_filtres, 1, wx.EXPAND, 5)

        grid_sizer_droit.AddGrowableRow(0)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()
    
    def OnBoutonFermer(self, event):
        self.ctrl_coeff.SauvegardeCoeff() 
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Etatglobal")
    
    def OnClose(self, event=None):
        self.ctrl_coeff.SauvegardeCoeff() 
        
    def Apercu(self, event):
        # Validation de la période
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate() 
        if self.ctrl_parametres.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, u"La date de début de période semble incorrecte !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate() 
        if self.ctrl_parametres.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, u"La date de fin de période semble incorrecte !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, u"La date de début de période est supérieure à la date de fin !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Validation du regroupement
        if self.ctrl_parametres.ValidationRegroupement() == False :
            dlg = wx.MessageDialog(self, u"Les paramètres de regroupement semble erronés !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        regroupement = self.ctrl_parametres.GetRegroupement()
        
        # Validation des activités
        listeActivites = self.ctrl_parametres.GetActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, u"Vous devez sélectionner au moins une activité !", u"Erreur de saisie", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Récupération des méthodes de calcul
        dictUnites = self.ctrl_coeff.GetDonnees()
        if dictUnites == False :
            return False
        
        # Récupération des filtres
        jours_scolaires = self.ctrl_jours.GetJours("scolaire")
        jours_vacances = self.ctrl_jours.GetJours("vacances")
        etats = self.ctrl_etats.GetEtats() 
        qf = self.ctrl_qf.GetDonnees() 

        # Récupération du mode d'affichage
        modeAffichage = self.ctrl_parametres.GetModeAffichage()
        modeDetail = self.ctrl_parametres.GetModeDetail()
        
        # Récupération du labelParametres
        labelParametres = self.ctrl_parametres.GetLabelParametres()
        
        # Vérifie que toutes les familles ont une caisse attribuées
        nbreFamillesSansCaisses = OL_Liste_regimes.GetNbreSansCaisse(listeActivites, date_debut, date_fin)
        if nbreFamillesSansCaisses > 0 :
            dlg = wx.MessageDialog(self, u"Attention, le régime d'appartenance n'a pas été renseigné pour %d famille(s).\n\nVous pourrez consulter le détail des familles concernées grâce à la commande\n'Editer la liste des régimes et caisses' du menu Individus." % nbreFamillesSansCaisses, u"Attention", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
                
        # Récupération des régimes
        DB = GestionDB.DB()
        req = """SELECT 
        IDregime, nom
        FROM regimes
        ORDER BY IDregime
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        dictRegimes = {}
        for IDregime, nomRegime in listeDonnees :
            dictRegimes[IDregime] = nomRegime
        
        # Regroupement par activité
        if modeDetail == True :
            dictActivites = {}
            for IDunite, dictUnite in dictUnites.iteritems() :
                activite = (dictUnite["nomActivite"], dictUnite["IDactivite"])
                if dictActivites.has_key(activite) == False :
                    dictActivites[activite] = [IDunite,]
                else :
                    dictActivites[activite].append(IDunite)
        else :
            dictActivites = { (u"", 0) : dictUnites.keys() }
        
        # Recherche des données
        dictValeurs = {}
        listeRegimesUtilises = []
        for (nomActivite, IDactivite), listeUnites in dictActivites.iteritems() :
            
            dictResultats = {}
            
            # Préparation des niveaux de regroupement
            if regroupement == None :
                dictResultats = { 0 : { "labelRegroupement" : u""} }
            elif regroupement[0] == "age" :
                # Si en fonction de l'âge
                ageReference = regroupement[1]
                dictResultats = { 
                    0 : { "labelRegroupement" : u"- %d ans" % ageReference},
                    1 : { "labelRegroupement" : u"+ %d ans" % ageReference}, 
                    }
            elif regroupement[0] == "dateNaiss" :
                # Si en fonction de la date de naissance
                dateNaissReference = regroupement[1]
                dictResultats = { 
                    0 : { "labelRegroupement" : u"Nés avant le %s" % DateEngFr(str(dateNaissReference))},
                    1 : { "labelRegroupement" : u"Nés après le %s" % DateEngFr(str(dateNaissReference))}, 
                    }
            
            # Récupération des périodes de vacances
            req = """SELECT 
            IDvacance, nom, annee, date_debut, date_fin
            FROM vacances
            ;"""
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()     
            listeVacances = []
            for IDvacance, nom, annee, date_debut_Tmp, date_fin_Tmp in listeDonnees :
                date_debut_Tmp = DateEngEnDateDD(date_debut_Tmp)
                date_fin_Tmp = DateEngEnDateDD(date_fin_Tmp)
                if date_debut_Tmp.month in (6, 7, 8, 9) or date_fin_Tmp.month in (6, 7, 8, 9) :
                    grandesVacs = True
                else:
                    grandesVacs = False
                listeVacances.append( {"date_debut" : date_debut_Tmp, "date_fin" : date_fin_Tmp, "grandesVacs" : grandesVacs} )

        
            # Récupère le QF de la famille
            dictQuotientsFamiliaux = {}
            if qf != None :
                req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient
                FROM quotients
                ORDER BY date_debut;"""
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                for IDquotient, IDfamille, date_debut, date_fin, quotient in listeDonnees :
                    date_debut = DateEngEnDateDD(date_debut)
                    date_fin = DateEngEnDateDD(date_fin)
                    if dictQuotientsFamiliaux.has_key(IDfamille) == False :
                        dictQuotientsFamiliaux[IDfamille] = []
                    dictQuotientsFamiliaux[IDfamille].append((date_debut, date_fin, quotient))

            # Récupération des consommations
            listeUnitesUtilisees = listeUnites
            if len(listeUnitesUtilisees) == 0 : conditionSQL = "AND consommations.IDunite IN ()"
            elif len(listeUnitesUtilisees) == 1 : conditionSQL = "AND consommations.IDunite IN (%d)" % listeUnitesUtilisees[0]
            else : conditionSQL = "AND consommations.IDunite IN %s" % str(tuple(listeUnitesUtilisees))
                
            req = """SELECT 
            consommations.IDconso, consommations.IDindividu, consommations.IDactivite, 
            consommations.date, consommations.IDunite, consommations.quantite,
            consommations.heure_debut, consommations.heure_fin, consommations.etat,
            consommations.IDprestation, prestations.temps_facture,
            comptes_payeurs.IDfamille, familles.IDcaisse,
            caisses.IDregime,
            individus.date_naiss
            FROM consommations
            LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
            LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
            LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille
            LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
            LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
            WHERE consommations.date >='%s' AND consommations.date <='%s'
            AND etat NOT IN ('attente', 'refus')
            %s
            ;""" % (str(date_debut), str(date_fin), conditionSQL)
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()     
            
            listePrestationsTraitees = []
            for IDconso, IDindividu, IDactivite, date, IDunite, quantite, heure_debut, heure_fin, etat, IDprestation, temps_facture, IDfamille, IDcaisse, IDregime, date_naiss in listeDonnees :
                date = DateEngEnDateDD(date)
                if date_naiss != None : date_naiss = DateEngEnDateDD(date_naiss)
                
                # Quantité
                if quantite == None :
                    quantite = 1
                
                # Formatage des heures
                if heure_debut != None and heure_debut != "" : 
                    h, m = heure_debut.split(":")
                    heure_debut = datetime.time(int(h), int(m))
                if heure_fin != None and heure_fin != "" : 
                    h, m = heure_fin.split(":")
                    heure_fin = datetime.time(int(h), int(m))

                # Recherche la période
                periode = None
                for dictVac in listeVacances :
                    if date >= dictVac["date_debut"] and date <= dictVac["date_fin"] :
                        if dictVac["grandesVacs"] == True :
                            # C'est durant les grandes vacances :
                            periode = "grandesVacs"
                        else:
                            # C'est durant les petites vacances :
                            periode = "petitesVacs"
                if periode == None :
                    # C'est hors vacances :
                    periode = "horsVacs"

                # ------------ Application de filtres ---------------
                valide = False
                
                # Période
                if periode == "horsVacs" :
                    if date.weekday() in jours_scolaires :
                        valide = True
                if periode != "horsVacs" :
                    if date.weekday() in jours_vacances :
                        valide = True
                
                # Etat
                if etat not in etats :
                    valide = False
                
                # QF
                if qf != None :
                    qf_min, qf_max = qf
                    valide = False
                    if dictQuotientsFamiliaux.has_key(IDfamille) :
                        for date_debut, date_fin, quotient in dictQuotientsFamiliaux[IDfamille] :
                            if date >= date_debut and date <= date_fin and quotient >= qf_min and quotient <= qf_max :
                                valide = True
                                break
                
                # Calculs
                if valide == True :
                    
                    # ----- Recherche de la méthode de calcul pour cette unité -----
                    dictCalcul = dictUnites[IDunite]
                    valeur = datetime.timedelta(hours=0, minutes=0)
                    
                    if dictCalcul["typeCalcul"] == 0 :
                        # Si c'est selon le coeff :
                        if valeur == None or valeur == "" : 
                            valeur = datetime.timedelta(hours=0, minutes=0)
                        else :
                            valeur = datetime.timedelta(hours=dictCalcul["coeff"], minutes=0)
                        
                    elif dictCalcul["typeCalcul"] == 1 :
                        
                        # Si c'est en fonction du temps réél :
                        if heure_debut != None and heure_debut != "" and heure_fin != None and heure_fin != "" : 
                            
                            valeur = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute) - datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
                            if "day" in str(valeur) :
                                dlg = wx.MessageDialog(self, u"Les horaires de cette consommation sont incorrectes : IDconso=%d | IDindividu=%d | IDfamille=%d | date=%s." % (IDconso, IDindividu, IDfamille, date), u"Erreur", wx.OK | wx.ICON_ERROR)
                                dlg.ShowModal()
                                dlg.Destroy()
                                return False
                            
                            # Si un plafond est imposé
                            plafond = dictCalcul["plafond"]
                            if plafond != None :
                                plafond = datetime.timedelta(hours=int(plafond.split(":")[0]), minutes=int(plafond.split(":")[1]))
                                if valeur > plafond :
                                    valeur = plafond

                            # Si un arrondi est demandé
                            arrondi = dictCalcul["arrondi"]
                            if arrondi != None :
                                heures = (valeur.days*24) + (valeur.seconds/3600)
                                minutes = valeur.seconds%3600/60
                                hr, mn = ArrondirHeureSup(heures, minutes, arrondi)
                                valeur = datetime.timedelta(hours=hr, minutes=mn)
                                                    
                    else:
                        # Si c'est en fonction du temps facturé
                        if temps_facture != None and temps_facture != "" : 
                            if IDprestation not in listePrestationsTraitees :
                                hr, mn = temps_facture.split(":")
                                valeur = datetime.timedelta(hours=int(hr), minutes=int(mn))
                                listePrestationsTraitees.append(IDprestation)
                        
                    # ----- Recherche du regroupement par âge ou date de naissance  -----
                    if regroupement == None :
                        regroup = 0
                    elif regroupement[0] == "age" :
                        # Si en fonction de l'âge
                        ageReference = regroupement[1]
                        if date_naiss != None :
                            age = (date.year - date_naiss.year) - int((date.month, date.day) < (date_naiss.month, date_naiss.day))
                            if age >= ageReference :
                                regroup = 1
                            else:
                                regroup = 0
                        else:
                            regroup = None
                    elif regroupement[0] == "dateNaiss" :
                        # Si en fonction de la date de naissance
                        dateNaissReference = regroupement[1]
                        if date_naiss != None :
                            if date_naiss >= dateNaissReference :
                                regroup = 1
                            else:
                                regroup = 0
                        else:
                            regroup = None
                    
                    # Type de colonne : Facturé et Réalisé ?
                    valeurFact = valeur
                    valeurReal = valeur
##                    if etat in ("absenti", "reservation", "present") : 
##                        valeurFact = valeur
##                    else:
##                        valeurFact = datetime.timedelta(hours=0, minutes=0)
##                    if etat in ("reservation", "present") : 
##                        valeurReal = valeur
##                    else:
##                        valeurReal = datetime.timedelta(hours=0, minutes=0)
                    
                    # Mémorisation du résultat
                    if valeurFact != datetime.timedelta(hours=0, minutes=0) or valeurReal != datetime.timedelta(hours=0, minutes=0) :
                        if dictResultats.has_key(regroup) == False :
                            dictResultats[regroup] = {}
                        if dictResultats[regroup].has_key(periode) == False :
                            dictResultats[regroup][periode] = {}
                        if dictResultats[regroup][periode].has_key(IDregime) == False :
                            dictResultats[regroup][periode][IDregime] = {"fact" : datetime.timedelta(hours=0, minutes=0), "real" : datetime.timedelta(hours=0, minutes=0)}
                        if IDregime not in listeRegimesUtilises : 
                            listeRegimesUtilises.append(IDregime)
                        dictResultats[regroup][periode][IDregime]["fact"] += valeurFact * quantite
                        dictResultats[regroup][periode][IDregime]["real"] += valeurReal * quantite
            
            if modeDetail == True :
                dictValeurs[IDactivite] = dictResultats
            else :
                dictValeurs[0] = dictResultats
            
        DB.Close() 
            
        # Création du PDF
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.platypus.flowables import ParagraphAndImage, Image
        from reportlab.rl_config import defaultPageSize
        from reportlab.lib.units import inch, cm
        from reportlab.lib.pagesizes import A4, portrait, landscape
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        # Initialisation du PDF
        taillePage = landscape(A4)
        HAUTEUR_PAGE = defaultPageSize[0]
        LARGEUR_PAGE = defaultPageSize[1]
        nomDoc = "Temp/Etat_global_%s.pdf" % datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        if "win" in sys.platform : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=taillePage, topMargin=20, bottomMargin=20)
        story = []
        
        largeurContenu = 730
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (630, 100) )
        dateDuJour = DateEngFr(str(datetime.date.today()))
        dataTableau.append( (u"Etat global des consommations", u"%s\nEdité le %s" % (UTILS_Organisateur.GetNom(), dateDuJour)) )
        style = TableStyle([
                ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
                ('VALIGN', (0,0), (-1,-1), 'TOP'), 
                ('ALIGN', (0,0), (0,0), 'LEFT'), 
                ('FONT',(0,0),(0, 0), "Helvetica-Bold", 16), 
                ('ALIGN', (1,0), (1,0), 'RIGHT'), 
                ('FONT',(1,0),(1,0), "Helvetica", 6), 
                ])
        tableau = Table(dataTableau, largeursColonnes)
        tableau.setStyle(style)
        story.append(tableau)
        story.append(Spacer(0, 10))       

        # Création du texte d'Intro
##        texteIntro = u"-  Période du %s au %s  -" % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin)))
##        dataTableau = []
##        dataTableau.append((texteIntro,) )
##        style = TableStyle([
##                ('VALIGN', (0,0), (0,0), 'TOP'), 
##                ('ALIGN', (0, 0), (0,0), 'CENTRE'), 
##                ('FONT',(0,0),(0,0), "Helvetica", 9), 
##                ])
##        tableau = Table(dataTableau, [largeurContenu,])
##        tableau.setStyle(style)
##        story.append(tableau)
##        story.append(Spacer(0,40))       

        # Insertion du label Paramètres
        styleA = ParagraphStyle(name="A", fontName="Helvetica", fontSize=6, spaceAfter=20)
        story.append(Paragraph(labelParametres, styleA))       

        
        listeActivites = []
        for (nomActivite, IDactivite), listeUnites in dictActivites.iteritems() : 
            listeActivites.append((nomActivite, IDactivite))
        listeActivites.sort() 
        
        listeRegimesUtilises.sort() 
        
        for nomActivite, IDactivite in listeActivites :
            
            dictResultats = dictValeurs[IDactivite]

            # Création des colonnes
            listeColonnes = []
            largeurColonne = 80
            for IDregime in listeRegimesUtilises :
                if dictRegimes.has_key(IDregime) :
                    nomRegime = dictRegimes[IDregime]
                else:
                    nomRegime = u"Sans régime"
                listeColonnes.append((IDregime, nomRegime, largeurColonne))
            listeColonnes.append((2000, u"Total", largeurColonne))
            
            dataTableau = []
            
            listeStyles = [
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
                ('FONT',(0,0),(-1,0), "Helvetica-Bold", 7), 
                ('FONT',(0,-1),(-1,-1), "Helvetica", 7), 
                ('GRID', (1,0), (-1,-1), 0.25, colors.black), 
                ('ALIGN', (0,0), (-1,-1), 'CENTRE'), 
                ('FONT',(0,0),(0,0), "Helvetica-Bold", 7), 
                ('ALIGN', (0,0), (0,0), 'LEFT'), 
                ]
                
            # Régimes + total
            ligne1 = [ nomActivite, ]
    ##        ligne2 = [ u"", ]
            largeursColonnes = [ 150, ]
            indexColonne = 1
            for IDregime, label, largeur in listeColonnes :
                ligne1.append(label)
    ##            ligne1.append(u"")
    ##            ligne2.append(u"Facturé")
    ##            ligne2.append(u"Réalisé")
    ##            largeursColonnes.append(largeur)
                largeursColonnes.append(largeur)
    ##            listeStyles.append( ('SPAN', (indexColonne, 0), (indexColonne+1, 0)) )
    ##            indexColonne += 2
            indexColonne += 1
            
            dataTableau.append(ligne1)
    ##        dataTableau.append(ligne2)

            # Création du tableau d'entete de colonnes
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)
##            story.append(Spacer(0, 10))

            # Création des lignes
            index = 1
            for IDregroup, dictRegroup in dictResultats.iteritems() :
                
                dataTableau = []
                ligne = []
                
                # Création des niveaux de regroupement
                if dictRegroup.has_key("labelRegroupement") :
                    label = dictRegroup["labelRegroupement"]
                else :
                    label = u"Sans date de naissance"
                ligne = [label,]
                for IDregime, label, largeur in listeColonnes[:-1] :
                    ligne.append("")
                dataTableau.append(ligne)
                index += 1
                
                # Création des lignes de périodes
                listePeriodes = [
                    {"code" : "petitesVacs", "label" : u"Petites vacances"},
                    {"code" : "grandesVacs", "label" : u"Vacances d'été"},
                    {"code" : "horsVacs", "label" : u"Hors vacances"},
                    ]
                dictTotaux = {}
                for dictPeriode in listePeriodes :
                    if dictRegroup.has_key(dictPeriode["code"]) :
                        ligne = []
                        ligne.append(dictPeriode["label"])
                        totalLigneFact = datetime.timedelta(hours=0, minutes=0)
                        totalLigneReal = datetime.timedelta(hours=0, minutes=0)
                        for IDregime, labelColonne, largeurColonne in listeColonnes :
                            if IDregime < 1000 :
                                if dictRegroup[dictPeriode["code"]].has_key(IDregime) :
                                    # Valeur Facturé
                                    valeurFact = dictRegroup[dictPeriode["code"]][IDregime]["fact"]
                                    valeurReal = dictRegroup[dictPeriode["code"]][IDregime]["real"]
                                else:
                                    valeurFact = datetime.timedelta(hours=0, minutes=0)
                                    valeurReal = datetime.timedelta(hours=0, minutes=0)
    ##                            ligne.append(FormateValeur(valeurFact, modeAffichage))
                                ligne.append(FormateValeur(valeurReal, modeAffichage))
                                totalLigneFact += valeurFact
                                totalLigneReal += valeurReal
                                if dictTotaux.has_key(IDregime) == False :
                                    dictTotaux[IDregime] = {"fact" : datetime.timedelta(hours=0, minutes=0), "real" :datetime.timedelta(hours=0, minutes=0)} 
                                dictTotaux[IDregime]["fact"] += valeurFact
                                dictTotaux[IDregime]["real"] += valeurReal
                        # Total de la ligne
                        if IDregime == 2000 :
    ##                        ligne.append(FormateValeur(totalLigneFact, modeAffichage))
                            ligne.append(FormateValeur(totalLigneReal, modeAffichage))
                        dataTableau.append(ligne)
                        index += 1
                
                # Création de la ligne de total
                ligne = [u"Total",]
                totalLigneFact = datetime.timedelta(hours=0, minutes=0)
                totalLigneReal = datetime.timedelta(hours=0, minutes=0)
                for IDregime, labelColonne, largeurColonne in listeColonnes :
                    if IDregime < 1000 :
                        if dictTotaux.has_key(IDregime) :
                            totalFact = dictTotaux[IDregime]["fact"]
                            totalReal = dictTotaux[IDregime]["real"]
                        else:
                            totalFact = datetime.timedelta(hours=0, minutes=0)
                            totalReal = datetime.timedelta(hours=0, minutes=0)
    ##                    ligne.append(FormateValeur(totalFact, modeAffichage))
                        ligne.append(FormateValeur(totalReal, modeAffichage))
                        totalLigneFact += totalFact
                        totalLigneReal += totalReal
                # Total de la ligne
                if IDregime == 2000 :
    ##                ligne.append(FormateValeur(totalLigneFact, modeAffichage))
                    ligne.append(FormateValeur(totalLigneReal, modeAffichage))
                dataTableau.append(ligne)
                index += 1
                        
                couleurFondFonce = (0.8, 0.8, 1) # Vert -> (0.5, 1, 0.2)
                couleurFondClair = (0.96, 0.96, 1) 
                
                listeStyles = [
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
                        
                        ('FONT',(0,0),(-1,-1), "Helvetica", 7), 
                        ('GRID', (0,0), (-1,-1), 0.25, colors.black), 
                        ('ALIGN', (0,1), (-1,-1), 'CENTRE'), 
                        
                        ('SPAN',(0,0),(-1,0)), 
                        ('FONT',(0,0),(0,0), "Helvetica-Bold", 8), 
                        ('BACKGROUND', (0, 0), (-1, 0), couleurFondFonce), 
                        
                        ('BACKGROUND', (0, -1), (-1, -1), couleurFondClair), 
                        ('BACKGROUND', (-1, 1), (-1, -1), couleurFondClair), 
                        
                        ('FONT',(0, -1),(-1, -1), "Helvetica-Bold", 7), # Gras pour totaux
                        
                        ]
                

                # Création du tableau
                tableau = Table(dataTableau, largeursColonnes)
                tableau.setStyle(TableStyle(listeStyles))
                story.append(tableau)
            
            story.append(Spacer(0, 20))
            
        # Enregistrement du PDF
        try :
            doc.build(story)
        except Exception, err :
            print "Erreur dans ouverture PDF :", err
            if "Permission denied" in err :
                dlg = wx.MessageDialog(None, u"Noethys ne peut pas créer le PDF.\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan...", u"Erreur d'édition", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Affichage du PDF
        FonctionsPerso.LanceFichierExterne(nomDoc)


# -------------------------------------------------------------------------------------------------------------------------------------------

        


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
