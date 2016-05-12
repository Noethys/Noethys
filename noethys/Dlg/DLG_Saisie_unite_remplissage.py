#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Saisie_heure
from Ctrl import CTRL_Etiquettes
from Utils import UTILS_Texte

import GestionDB



class CheckListBoxUnites(wx.CheckListBox):
    def __init__(self, parent, IDactivite=None, IDunite_remplissage=None):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.data = []
        self.IDactivite = IDactivite
        self.IDunite_remplissage = IDunite_remplissage
    
    def MAJ(self):
        listeTmp = []
        db = GestionDB.DB()
        req = """SELECT IDunite, nom
        FROM unites 
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        if len(listeDonnees) > 0 : 
            for IDunite, nom in listeDonnees :
                listeTmp.append((IDunite, nom, False))
        self.SetData(listeTmp)    
            
    def SetData(self, listeValeurs=[]):
        """ items = (ID, label, checked) """
        self.Clear()
        self.data = []
        index = 0
        for ID, label, checked in listeValeurs:
            self.data.append((ID, label))
            self.Append(label)
            if checked == True :
                self.Check(index)
            index += 1
    
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.data)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.data[index][0])
        return listeIDcoches

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.data)):
            ID = self.data[index][0]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
    
    def Importation(self):
        db = GestionDB.DB()
        req = """SELECT IDunite_remplissage_unite, IDunite 
        FROM unites_remplissage_unites WHERE IDunite_remplissage=%d;""" % self.IDunite_remplissage
        db.ExecuterReq(req)
        listeTemp = db.ResultatReq()
        db.Close()
        if len(listeTemp) > 0 : 
            listeID = []
            for IDunite_remplissage_unite, IDunite in listeTemp :
                listeID.append(IDunite)
            self.SetIDcoches(listeID)

    def Sauvegarde(self):
        liste_nouvelle = self.GetIDcoches()
        liste_ancienne = []
        DB = GestionDB.DB()
        req = """SELECT IDunite_remplissage_unite, IDunite 
        FROM unites_remplissage_unites WHERE IDunite_remplissage=%d;""" % self.IDunite_remplissage
        DB.ExecuterReq(req)
        listeTemp = DB.ResultatReq()
        if len(listeTemp) > 0 : 
            listeID = []
            for IDunite_remplissage_unite, IDunite in listeTemp :
                liste_ancienne.append(IDunite)
        # On enregistre les nouveaux
        for IDunite in liste_nouvelle :
            if IDunite not in liste_ancienne :
                listeDonnees = [ ("IDunite_remplissage", self.IDunite_remplissage ), ("IDunite", IDunite ), ]
                IDunite_remplissage_unite = DB.ReqInsert("unites_remplissage_unites", listeDonnees)
        # On enlève les anciens
        for IDunite in liste_ancienne :
            if IDunite not in liste_nouvelle :
                DB.ReqDEL("unites_remplissage_unites", "IDunite", IDunite)
        DB.Close()

# ------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, IDunite_remplissage=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDactivite = IDactivite
        self.IDunite_remplissage = IDunite_remplissage
        
        # Nom
        self.staticbox_nom_staticbox = wx.StaticBox(self, -1, _(u"Nom de l'unité"))
        self.label_nom = wx.StaticText(self, -1, _(u"Nom complet :"))
        self.ctrl_nom = wx.TextCtrl(self, -1, u"")
        self.ctrl_nom.SetMinSize((300, -1))

        self.label_abrege = wx.StaticText(self, -1, _(u"Nom abrégé :"))
        self.ctrl_abrege = wx.TextCtrl(self, -1, u"")
        
        # Caractéristiques
        self.staticbox_caract_staticbox = wx.StaticBox(self, -1, _(u"Caractéristiques"))
        self.label_seuil = wx.StaticText(self, -1, _(u"Seuil d'alerte :"))
        self.ctrl_seuil = wx.SpinCtrl(self, -1, "5", size=(60, -1))
        self.ctrl_seuil.SetRange(0, 200)
                
        self.label_unites = wx.StaticText(self, -1, _(u"Unités :"))
        self.ctrl_unites = CheckListBoxUnites(self, self.IDactivite, self.IDunite_remplissage)
        self.ctrl_unites.SetMinSize((-1, 100))
        self.ctrl_unites.MAJ() 
        
        self.label_etiquettes = wx.StaticText(self, -1, _(u"Etiquettes :"))
        self.ctrl_etiquettes = CTRL_Etiquettes.CTRL(self, listeActivites=[self.IDactivite,], nomActivite=u"Activité", activeMenu=False)
        self.ctrl_etiquettes.SetMinSize((-1, 80))
        self.ctrl_etiquettes.MAJ() 
        
        self.label_horaire = wx.StaticText(self, -1, _(u"Plage horaire :"))
        self.label_de = wx.StaticText(self, -1, _(u"de"))
        self.ctrl_heure_min = CTRL_Saisie_heure.Heure(self)
        self.label_a = wx.StaticText(self, -1, u"à")
        self.ctrl_heure_max = CTRL_Saisie_heure.Heure(self)
        
        self.label_affichage = wx.StaticText(self, -1, _(u"Affichage :"))
        self.check_afficher_page_accueil = wx.CheckBox(self, -1, _(u"Effectifs de la page d'accueil"))
        self.check_afficher_page_accueil.SetValue(True) 
        self.check_afficher_grille_conso = wx.CheckBox(self, -1, _(u"Grille des consommations"))
        self.check_afficher_grille_conso.SetValue(True) 

        # Validité
        self.staticbox_validite_staticbox = wx.StaticBox(self, -1, _(u"Validité"))
        self.radio_illimitee = wx.RadioButton(self, -1, _(u"Durant la période de validité de l'activité"), style=wx.RB_GROUP)
        self.radio_limitee = wx.RadioButton(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_illimitee)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioValidite, self.radio_limitee)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        
        if self.IDunite_remplissage != None :
            self.Importation() 
        
        self.OnRadioValidite(None)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'une unité de remplissage"))
        self.ctrl_nom.SetToolTipString(_(u"Saisissez ici le nom complet de l'unité de remplissage"))
        self.ctrl_abrege.SetMinSize((80, -1))
        self.ctrl_abrege.SetToolTipString(_(u"Saisissez ici le nom abrégé de l'unité de remplissage"))
        self.ctrl_seuil.SetToolTipString(_(u"Saisisez le nombre de places qui constitue le seuil d'alerte"))
        self.ctrl_unites.SetToolTipString(_(u"Cochez les unités qui doivent être associées"))
        self.ctrl_etiquettes.SetToolTipString(_(u"Cochez les étiquettes qui doivent être associées"))
        self.radio_illimitee.SetToolTipString(_(u"Cochez ici si l'unité est valable sur toute la durée de validité de l'activité"))
        self.radio_limitee.SetToolTipString(_(u"Cliquez ici pour définir une période de validité précise"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez une date de début"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez une date de fin"))
        self.ctrl_heure_min.SetToolTipString(_(u"[OPTIONNEL] Saisissez une plage horaire conditionnelle"))
        self.ctrl_heure_max.SetToolTipString(_(u"[OPTIONNEL] Saisissez une plage horaire conditionnelle"))
        self.check_afficher_page_accueil.SetToolTipString(_(u"Afficher cette unité dans le cadre Effectifs de la page d'accueil"))
        self.check_afficher_grille_conso.SetToolTipString(_(u"Afficher cette unité dans la grille des consommations"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        # Nom
        staticbox_nom = wx.StaticBoxSizer(self.staticbox_nom_staticbox, wx.VERTICAL)
        grid_sizer_nom = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_nom.Add(self.label_nom, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_nom, 0, wx.EXPAND, 0)
        grid_sizer_nom.Add(self.label_abrege, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_nom.Add(self.ctrl_abrege, 0, 0, 0)
        grid_sizer_nom.AddGrowableCol(1)
        staticbox_nom.Add(grid_sizer_nom, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_nom, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        # Caract
        staticbox_caract = wx.StaticBoxSizer(self.staticbox_caract_staticbox, wx.VERTICAL)
        grid_sizer_caract = wx.FlexGridSizer(rows=7, cols=2, vgap=15, hgap=5)
        grid_sizer_caract.Add(self.label_seuil, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caract.Add(self.ctrl_seuil, 0, 0, 0)
        
        grid_sizer_caract.Add(self.label_unites, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_caract.Add(self.ctrl_unites, 0, wx.EXPAND, 0)

        grid_sizer_caract.Add(self.label_etiquettes, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_caract.Add(self.ctrl_etiquettes, 0, wx.EXPAND, 0)
        
        grid_sizer_caract.Add(self.label_horaire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaire = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_horaire.Add(self.label_de, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaire.Add(self.ctrl_heure_min, 0, 0, 0)
        grid_sizer_horaire.Add(self.label_a, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_horaire.Add(self.ctrl_heure_max, 0, 0, 0)
        grid_sizer_caract.Add(grid_sizer_horaire, 1, wx.EXPAND, 0)

        grid_sizer_caract.Add(self.label_affichage, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_affichage = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.check_afficher_page_accueil, 0, 0, 0)
        grid_sizer_affichage.Add(self.check_afficher_grille_conso, 0, 0, 0)
        grid_sizer_caract.Add(grid_sizer_affichage, 0, 0, 0)

        grid_sizer_caract.AddGrowableCol(1)
        staticbox_caract.Add(grid_sizer_caract, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_caract, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        # Validité
        staticbox_validite = wx.StaticBoxSizer(self.staticbox_validite_staticbox, wx.VERTICAL)
        grid_sizer_validite = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        grid_sizer_validite.Add(self.radio_illimitee, 0, 0, 0)
        grid_sizer_dates = wx.FlexGridSizer(rows=1, cols=4, vgap=5, hgap=5)
        grid_sizer_dates.Add(self.radio_limitee, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_validite.Add(grid_sizer_dates, 1, wx.EXPAND, 0)
        staticbox_validite.Add(grid_sizer_validite, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_validite, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioValidite(self, event):
        if self.radio_illimitee.GetValue() == True :
            self.ctrl_date_debut.Enable(False)
            self.ctrl_date_fin.Enable(False)
        else:
            self.ctrl_date_debut.Enable(True)
            self.ctrl_date_fin.Enable(True)

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Units")
    
    def GetIDunite_remplissage(self):
        return self.IDunite_remplissage
    
    def OnBoutonOk(self, event): 
        etat = self.Sauvegarde() 
        if etat == False :
            return
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def Sauvegarde(self):
        # Nom
        nom = self.ctrl_nom.GetValue() 
        if nom == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        abrege = self.ctrl_abrege.GetValue()
        if abrege == "" :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir un nom abrégé !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        seuil_alerte = int(self.ctrl_seuil.GetValue())      
        
        heure_min = self.ctrl_heure_min.GetHeure() 
        if heure_min != None and self.ctrl_heure_min.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"L'heure minimale semble être incorrecte !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_min.SetFocus()
            return False

        heure_max = self.ctrl_heure_max.GetHeure() 
        if heure_max != None and self.ctrl_heure_max.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"L'heure maximale semble être incorrecte !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_max.SetFocus()
            return False
        
        if (heure_min != None and heure_max == None) or (heure_min == None and heure_max != None) :
            dlg = wx.MessageDialog(self, _(u"La plage horaire est incomplète !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_heure_min.SetFocus()
            return False
        
        # Affichage
        afficher_page_accueil = int(self.check_afficher_page_accueil.GetValue())
        afficher_grille_conso = int(self.check_afficher_grille_conso.GetValue())
            
        # Validité
        if self.radio_illimitee.GetValue() == True :
            date_debut = "1977-01-01"
            date_fin = "2999-01-01"
        else:
            date_debut = self.ctrl_date_debut.GetDate()
            if date_debut == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début de validité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
            date_fin = self.ctrl_date_fin.GetDate()
            if date_fin == None :
                dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de fin de validité !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        
        # Etiquettes
        etiquettes = UTILS_Texte.ConvertListeToStr(self.ctrl_etiquettes.GetCoches())
        
        # Enregistrement
        DB = GestionDB.DB()
        listeDonnees = [ 
            ("IDactivite", self.IDactivite ),
            ("nom", nom ),
            ("abrege", abrege ),
            ("seuil_alerte", seuil_alerte),
            ("date_debut", date_debut),
            ("date_fin", date_fin),
            ("heure_min", heure_min),
            ("heure_max", heure_max),
            ("afficher_page_accueil", afficher_page_accueil),
            ("afficher_grille_conso", afficher_grille_conso),
            ("etiquettes", etiquettes),
            ]

        if self.IDunite_remplissage == None :
            # Recherche le numéro d'ordre
            req = """SELECT IDunite_remplissage, ordre
            FROM unites_remplissage WHERE IDactivite=%d
            ORDER BY ordre DESC LIMIT 1
            ;""" % self.IDactivite
            DB.ExecuterReq(req)
            listeTemp = DB.ResultatReq()
            if len(listeTemp) == 0 : 
                ordre = 1
            else:
                ordre = listeTemp[0][1] + 1
            listeDonnees.append(("ordre", ordre ))
            self.IDunite_remplissage = DB.ReqInsert("unites_remplissage", listeDonnees)
            self.ctrl_unites.IDunite_remplissage = self.IDunite_remplissage
        else:
            DB.ReqMAJ("unites_remplissage", listeDonnees, "IDunite_remplissage", self.IDunite_remplissage)
                
        # Incompatibilités
        self.ctrl_unites.Sauvegarde() 
        
        DB.Close()
        return True

    def Importation(self):
        """ Importation des valeurs """
        db = GestionDB.DB()
        req = """SELECT IDunite_remplissage, nom, abrege, seuil_alerte, date_debut, date_fin, heure_min, heure_max, afficher_page_accueil, afficher_grille_conso, etiquettes
        FROM unites_remplissage WHERE IDunite_remplissage=%d;""" % self.IDunite_remplissage
        db.ExecuterReq(req)
        listeTemp = db.ResultatReq()
        db.Close()
        if len(listeTemp) == 0 : return
        listeTemp = listeTemp[0]
        
        nom = listeTemp[1]
        abrege = listeTemp[2]
        seuil_alerte = listeTemp[3]
        date_debut = listeTemp[4]
        date_fin = listeTemp[5]
        heure_min = listeTemp[6]
        heure_max = listeTemp[7]
        afficher_page_accueil = listeTemp[8]
        afficher_grille_conso = listeTemp[9]
        etiquettes = listeTemp[10]

        self.ctrl_nom.SetValue(nom)
        self.ctrl_abrege.SetValue(abrege)
        self.ctrl_seuil.SetValue(seuil_alerte)
        self.ctrl_heure_min.SetHeure(heure_min)
        self.ctrl_heure_max.SetHeure(heure_max)
        if date_debut != "1977-01-01" and date_fin != "2999-01-01" :
            self.ctrl_date_debut.SetDate(date_debut)
            self.ctrl_date_fin.SetDate(date_fin)
            self.radio_limitee.SetValue(True)
        if afficher_page_accueil == 0 :
            self.check_afficher_page_accueil.SetValue(False)
        if afficher_grille_conso == 0 :
            self.check_afficher_grille_conso.SetValue(False)
        self.ctrl_etiquettes.SetCoches(UTILS_Texte.ConvertStrToListe(etiquettes))

        self.ctrl_unites.Importation() 
        


if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDactivite=1, IDunite_remplissage=1)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
