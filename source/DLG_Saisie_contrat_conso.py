#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-14 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import CTRL_Saisie_date
import OL_Contrats_planning_elements
import GestionDB
import UTILS_Dates
import cPickle
import copy
import wx.lib.dialogs as dialogs


class CTRL_Modeles(wx.Choice):
    def __init__(self, parent, IDactivite=None):
        wx.Choice.__init__(self, parent, -1) 
        self.parent = parent
        self.IDactivite = IDactivite
        self.MAJ() 
        self.Select(0)
    
    def MAJ(self, IDligne=0):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else:
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDmodele, nom, donnees
        FROM modeles_plannings
        WHERE IDactivite=%d
        ORDER BY nom;""" % self.IDactivite
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for IDmodele, nom, donnees in listeDonnees :
            donnees = cPickle.loads(str(donnees))
            self.dictDonnees[index] = { "ID" : IDmodele, "nom " : nom, "donnees" : donnees}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["ID"]
    
    def GetDonnees(self):
        index = self.GetSelection()
        if index == -1 : return None
        return self.dictDonnees[index]["donnees"]

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent, IDactivite=None, date_debut=None, date_fin=None, IDgroupe=None, listePeriodes=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDactivite = IDactivite
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.IDgroupe = IDgroupe
        self.listePeriodes = listePeriodes
        
        # Généralités
        self.box_generalites_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Généralités"))
        self.label_periode = wx.StaticText(self, wx.ID_ANY, _(u"Dates :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, wx.ID_ANY, _(u"au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)
        
        # Planning
        self.box_planning_staticbox = wx.StaticBox(self, wx.ID_ANY, _(u"Planning"))
        
        self.radio_modele = wx.RadioButton(self, wx.ID_ANY, _(u"Le modèle de planning suivant :"), style=wx.RB_GROUP)
        self.ctrl_modele = CTRL_Modeles(self, IDactivite=IDactivite)
        self.bouton_modele = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Mecanisme.png", wx.BITMAP_TYPE_ANY))
        
        self.radio_planning_detail = wx.RadioButton(self, wx.ID_ANY, _(u"Le planning suivant :"))
        self.ctrl_planning_detail = OL_Contrats_planning_elements.ListView(self, id=-1, IDactivite=IDactivite, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_planning_detail.SetMinSize((50, 50)) 
        
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonModele, self.bouton_modele)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning_detail.Ajouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning_detail.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_planning_detail.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPlanning, self.radio_modele)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioPlanning, self.radio_planning_detail)

        # Init
        self.listeVacances = self.GetListeVacances()
        self.listeFeries = self.GetListeFeries() 
        self.dictUnites = self.Importation_unites() 
        self.dictOuvertures = self.GetOuverturesUnites() 

        self.ctrl_date_debut.SetDate(self.date_debut)
        self.ctrl_date_fin.SetDate(self.date_fin)
        self.ctrl_planning_detail.MAJ() 
        self.OnRadioPlanning(None)
        

    def __set_properties(self):
        self.SetTitle(_(u"Génération de consommations"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez une date de début"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez une date de fin"))
        self.radio_modele.SetToolTipString(_(u"Sélectionnez cette option pour utiliser un modèle de planning"))
        self.ctrl_modele.SetToolTipString(_(u"Sélectionnez un modèle de planning dans la liste"))
        self.bouton_modele.SetToolTipString(_(u"Cliquez ici pour accéder à la gestion des modèles de planning"))
        self.radio_planning_detail.SetToolTipString(_(u"Sélectionnez cette option pour définir un planning manuellement"))
        self.bouton_ajouter.SetToolTipString(_(u"Cliquez ici pour ajouter un paramètre"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier un paramètre"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer un paramètre"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((550, 500))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(3, 1, 10, 10)
        
        # Généralités
        box_generalites = wx.StaticBoxSizer(self.box_generalites_staticbox, wx.VERTICAL)
        grid_sizer_generalites = wx.FlexGridSizer(2, 2, 10, 10)
        grid_sizer_generalites.Add(self.label_periode, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode = wx.FlexGridSizer(1, 3, 5, 5)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, 0, 0)
        grid_sizer_periode.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, 0, 0)
        grid_sizer_generalites.Add(grid_sizer_periode, 1, wx.EXPAND, 0)
        box_generalites.Add(grid_sizer_generalites, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_generalites, 1, wx.LEFT | wx.RIGHT | wx.TOP | wx.EXPAND, 10)

        # Planning
        box_planning = wx.StaticBoxSizer(self.box_planning_staticbox, wx.VERTICAL)
        grid_sizer_planning = wx.FlexGridSizer(4, 1, 10, 10)
        grid_sizer_planning_detail = wx.FlexGridSizer(1, 2, 5, 5)

        grid_sizer_planning.Add(self.radio_modele, 0, 0, 0)

        grid_sizer_modele = wx.FlexGridSizer(1, 2, 5, 5)
        grid_sizer_modele.Add(self.ctrl_modele, 0, wx.EXPAND, 0)
        grid_sizer_modele.Add(self.bouton_modele, 0, 0, 0)
        grid_sizer_modele.AddGrowableCol(0)
        grid_sizer_planning.Add(grid_sizer_modele, 1, wx.LEFT | wx.EXPAND, 18)

        grid_sizer_planning.Add(self.radio_planning_detail, 0, 0, 0)
        grid_sizer_planning_detail.Add(self.ctrl_planning_detail, 1, wx.EXPAND, 0)
        
        grid_sizer_commandes = wx.FlexGridSizer(3, 1, 5, 5)
        grid_sizer_commandes.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_planning_detail.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        grid_sizer_planning_detail.AddGrowableRow(0)
        grid_sizer_planning_detail.AddGrowableCol(0)
        grid_sizer_planning.Add(grid_sizer_planning_detail, 1, wx.LEFT | wx.EXPAND, 18)
        
        grid_sizer_planning.AddGrowableRow(3)
        grid_sizer_planning.AddGrowableCol(0)
        box_planning.Add(grid_sizer_planning, 1, wx.ALL | wx.EXPAND, 10)
        grid_sizer_base.Add(box_planning, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(1, 4, 10, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 
    
    def OnRadioPlanning(self, event):
        self.ctrl_modele.Enable(self.radio_modele.GetValue())
        self.bouton_modele.Enable(self.radio_modele.GetValue())
        self.ctrl_planning_detail.Activation(self.radio_planning_detail.GetValue())
        self.bouton_ajouter.Enable(self.radio_planning_detail.GetValue())
        self.bouton_modifier.Enable(self.radio_planning_detail.GetValue())
        self.bouton_supprimer.Enable(self.radio_planning_detail.GetValue())
        
    def OnBoutonModele(self, event):  
        ID = self.ctrl_modele.GetID() 
        import DLG_Modeles_plannings
        dlg = DLG_Modeles_plannings.Dialog(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.ctrl_modele.MAJ() 
        self.ctrl_modele.SetID(ID)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Contrats")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)   

    def OnBoutonOk(self, event):
        if self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir la date de début d'application !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.ctrl_date_fin.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir la date de fin d'application !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if self.ctrl_date_debut.GetDate() > self.ctrl_date_fin.GetDate() :
            dlg = wx.MessageDialog(self, _(u"La date de début doit être inférieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.radio_modele.GetValue() == True and self.ctrl_modele.GetID() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement sélectionner un modèle de planning !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
            
        donnees = self.GetDonnees() 
        if len(donnees) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement définir au moins un paramètre de planning !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # Génération des consommations
        if self.Generation() == False :
            return
        
        # Fermeture de la fenêtre
        self.EndModal(wx.ID_OK)
    
    def GetDonnees(self):
        if self.radio_modele.GetValue() == True :
            donnees = self.ctrl_modele.GetDonnees() 
        else :
            donnees = self.ctrl_planning_detail.GetDonnees() 
        return donnees

    def Importation_unites(self):
        # Récupération des unités
        DB = GestionDB.DB()
        req = """SELECT IDunite, nom, abrege, type, heure_debut, heure_fin
        FROM unites
        WHERE IDactivite=%d
        ORDER BY ordre;""" % self.IDactivite
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()      
        dictUnites = {}
        for IDunite, nom, abrege, type, heure_debut, heure_fin in listeDonnees :
            dictUnites[IDunite] = {"nom":nom, "abrege":abrege, "type":type, "heure_debut":heure_debut, "heure_fin":heure_fin, "unites_incompatibles" : []}

        # Récupère les incompatibilités entre unités
        req = """SELECT IDunite_incompat, IDunite, IDunite_incompatible
        FROM unites_incompat;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        for IDunite_incompat, IDunite, IDunite_incompatible in listeDonnees :
            if dictUnites.has_key(IDunite) : dictUnites[IDunite]["unites_incompatibles"].append(IDunite_incompatible)
            if dictUnites.has_key(IDunite_incompatible) : dictUnites[IDunite_incompatible]["unites_incompatibles"].append(IDunite)

        return dictUnites
    
    def GetOuverturesUnites(self):
        DB = GestionDB.DB()
        req = """SELECT IDouverture, IDunite, IDgroupe, date
        FROM ouvertures 
        WHERE IDactivite=%d
        ORDER BY date; """ % self.IDactivite 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictOuvertures = {}
        for IDouverture, IDunite, IDgroupe, date in listeDonnees :
            date = UTILS_Dates.DateEngEnDateDD(date)
            dictOuvertures[(date, IDunite, IDgroupe)] = IDouverture
        return dictOuvertures

    def VerifieCompatibilitesUnites(self, IDunite1=None, IDunite2=None):
        listeIncompatibilites = self.dictUnites[IDunite1]["unites_incompatibles"]
        if IDunite2 in listeIncompatibilites :
            return False
        return True

    def GetListeVacances(self):
        db = GestionDB.DB()
        req = """SELECT date_debut, date_fin, nom, annee
        FROM vacances 
        ORDER BY date_debut; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

    def GetListeFeries(self):
        db = GestionDB.DB()
        req = """SELECT type, nom, jour, mois, annee
        FROM jours_feries 
        ; """
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        return listeDonnees

    def EstEnVacances(self, dateDD):
        date = str(dateDD)
        for valeurs in self.listeVacances :
            date_debut = valeurs[0]
            date_fin = valeurs[1]
            if date >= date_debut and date <= date_fin :
                return True
        return False

    def EstFerie(self, dateDD):
        jour = dateDD.day
        mois = dateDD.month
        annee = dateDD.year        
        for type, nom, jourTmp, moisTmp, anneeTmp in self.listeFeries :
            jourTmp = int(jourTmp)
            moisTmp = int(moisTmp)
            anneeTmp = int(anneeTmp)
            if type == "fixe" :
                if jourTmp == jour and moisTmp == mois :
                    return True
            else:
                if jourTmp == jour and moisTmp == mois and anneeTmp == annee :
                    return True
        return False

    def Generation(self):
        # Récupération des paramètres
        date_debut = self.ctrl_date_debut.GetDate() 
        date_fin = self.ctrl_date_fin.GetDate() 
        donneesPlanning = self.GetDonnees() 
        listePeriodes = copy.deepcopy(self.listePeriodes)
        
        listeConso = []
        for dictPlanning in donneesPlanning :
            
            # Recherche des dates
            listeDates = []
            date = date_debut
            semaines = dictPlanning["semaines"]
            numSemaine = semaines
            dateTemp = date
            while date < (date_fin + datetime.timedelta(days=1)) :
                            
                # Vérifie période et jour
                valide = False
                if self.EstEnVacances(date) :
                    if date.weekday() in dictPlanning["jours_vacances"] :
                        valide = True
                else :
                    if date.weekday() in dictPlanning["jours_scolaires"] :
                        valide = True
                
                # Vérifie si férié
                if dictPlanning["feries"] == False and self.EstFerie(date) == True :
                    valide = False

                # Calcul le numéro de semaine
                if len(listeDates) > 0 :
                    if date.weekday() < dateTemp.weekday() :
                        numSemaine += 1

                # Fréquence semaines
                if semaines != 1 :
                    if numSemaine % semaines != 0 :
                        valide = False
                
                # Ajout de la date à la liste
                if valide == True :
                    listeDates.append(date)
                
                dateTemp = date
                date += datetime.timedelta(days=1)
        
            # Mémorisation des consommations
            for date in listeDates :
            
                for dictUnite in dictPlanning["unites"] :
                    IDunite = dictUnite["IDunite"]
                    options = dictUnite["options"]
                    
                    if options.has_key("heure_debut"):
                        heure_debut = options["heure_debut"]
                    else :
                        heure_debut = self.dictUnites[IDunite]["heure_debut"]
                    if options.has_key("heure_fin"):
                        heure_fin = options["heure_fin"]
                    else :
                        heure_fin = self.dictUnites[IDunite]["heure_fin"]

                    if options.has_key("quantite"):
                        quantite = options["quantite"]
                    else :
                        quantite = None
                    
                    dictConso = {
                        "IDconso" : None,
                        "date" : date,
                        "IDunite" : IDunite,
                        "heure_debut" : heure_debut,
                        "heure_fin" : heure_fin,
                        "quantite" : quantite,
                        "etat" : "reservation",
                        }
                    listeConso.append(dictConso)
        
        # Insertion des conso à générer dans la liste des périodes
        listeAnomalies = []
        nbreConsoValides = 0
        for dictConso in listeConso :
            
            # Recherche de la période à associer
            index = 0
            for dictPeriode in listePeriodes :
                if dictConso["date"] >= dictPeriode["date_debut"] and dictConso["date"] <= dictPeriode["date_fin"] :
                    dateFr = UTILS_Dates.DateDDEnFr(dictConso["date"])
                    valide = True
                    
                    # Recherche si pas d'incompatibilités avec les conso déjà saisies
                    for dictConsoTemp in dictPeriode["listeConso"] :
                        if dictConso["date"] == dictConsoTemp["date"] :
                            nomUnite1 = self.dictUnites[dictConso["IDunite"]]["nom"]
                            nomUnite2 = self.dictUnites[dictConsoTemp["IDunite"]]["nom"]
                                
                            if self.VerifieCompatibilitesUnites(dictConsoTemp["IDunite"], dictConso["IDunite"]) == False :
                                listeAnomalies.append(_(u"%s : Unité %s incompatible avec unité %s déjà présente") % (dateFr, nomUnite1, nomUnite2))
                                valide = False
                                
                            if dictConso["IDunite"] == dictConsoTemp["IDunite"] :
                                if self.dictUnites[dictConso["IDunite"]]["type"] == "Multihoraire" :
                                    if dictConso["heure_fin"] > dictConsoTemp["heure_debut"] and dictConso["heure_debut"] < dictConsoTemp["heure_fin"] :
                                        listeAnomalies.append(_(u"%s : L'unité multihoraires %s chevauche une consommation d'une unité identique") % (dateFr, nomUnite1))
                                        valide = False
                                else :
                                    listeAnomalies.append(_(u"%s : Unité %s déjà présente") % (dateFr, nomUnite1))
                                    valide = False
                            
                    # Vérifie si unité ouverte
                    if self.IDgroupe != None and self.dictOuvertures.has_key((dictConso["date"], dictConso["IDunite"], self.IDgroupe)) == False :
                        listeAnomalies.append(_(u"%s : Unité %s fermée") % (dateFr, self.dictUnites[dictConso["IDunite"]]["nom"]))
                        valide = False
                            
                    # Insertion de la conso validée dans la période
                    if valide == True :
                        listePeriodes[index]["listeConso"].append(dictConso)
                        nbreConsoValides += 1
                            
                index += 1
        
        # Signalement des anomalies
        if len(listeAnomalies) :
            message1 = _(u"Les %d anomalies suivantes ont été trouvées.\n\nSouhaitez-vous tout de même générer les %d autres consommations ?") % (len(listeAnomalies), nbreConsoValides)
            message2 = u"\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, message1, caption = _(u"Génération"), msg2=message2, style = wx.ICON_EXCLAMATION | wx.YES|wx.CANCEL|wx.YES_DEFAULT, btnLabels={wx.ID_YES : _(u"Oui"), wx.ID_CANCEL : _(u"Annuler")})
            reponse = dlg.ShowModal() 
            dlg.Destroy() 
            if reponse != wx.ID_YES :
                return False
        
        if nbreConsoValides == 0 :
            dlg = wx.MessageDialog(self, _(u"Il n'y a aucune consommation valide à générer !"), _(u"Génération"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
                
        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Confirmez-vous la génération de %d consommations ?") % nbreConsoValides, _(u"Génération"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        self.listePeriodes = listePeriodes
        return True
        
    def GetListePeriodes(self):
        return self.listePeriodes
    
        

if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None, IDactivite=1, date_debut=datetime.date(2014, 1, 1), date_fin=datetime.date(2014, 12, 31))
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
