#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-17 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import sys

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Selection_activites
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Etat_global_parametres
from Ctrl import CTRL_Etat_global_options
from Ctrl import CTRL_Profil
from Ol import OL_Liste_regimes
from Utils import UTILS_Organisateur
from Utils import UTILS_Dates
from Utils import UTILS_Config
from Utils import UTILS_Infos_individus
from Utils import UTILS_Texte
from Utils import UTILS_Divers
from Utils import UTILS_Dialogs

import FonctionsPerso
import wx.lib.dialogs as dialogs

LISTE_MOIS= (_(u"Janvier"), _(u"Février"), _(u"Mars"), _(u"Avril"), _(u"Mai"), _(u"Juin"), _(u"Juillet"), _(u"Août"), _(u"Septembre"), _(u"Octobre"), _(u"Novembre"), _(u"Décembre"))


def ArrondirHeureSup(heures, minutes, pas): 
    """ Arrondi l'heure au pas supérieur """
    for x in range(0, 60, pas):
        if x >= minutes :
            return (heures, x)
    return (heures+1, 0)


def FormateValeur(valeur, mode="decimal"):
    heures = (valeur.days*24) + (valeur.seconds/3600)
    minutes = valeur.seconds%3600/60
    
    if mode == "decimal" :
        minDecimal = int(minutes)*100/60
        return float("%s.%s" % (heures, minDecimal))

    if mode == "horaire" :
        return "%dh%02d" % (heures, minutes)




# ---------------------------------------------------------------------------------------

class CTRL_profil_perso(CTRL_Profil.CTRL):
    def __init__(self, parent, categorie="", dlg=None):
        CTRL_Profil.CTRL.__init__(self, parent, categorie=categorie)
        self.dlg = dlg

    def Envoyer_parametres(self, dictParametres={}):
        """ Envoi des paramètres du profil sélectionné à la fenêtre """
        self.dlg.SetParametres(dictParametres)

    def Recevoir_parametres(self):
        """ Récupération des paramètres pour la sauvegarde du profil """
        dictParametres = self.dlg.GetParametres()
        self.Enregistrer(dictParametres)




# ---------------------------------------------------------------------------------------

class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période de référence"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Profil
        self.staticbox_profil_staticbox = wx.StaticBox(self, -1, _(u"Profil de configuration"))
        self.ctrl_profil = CTRL_profil_perso(self, categorie="etat_global", dlg=self.parent)
        self.ctrl_profil.SetMinSize((100, -1))

        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        
        self.__set_properties()
        self.__do_layout()


    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début de période"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin de période"))

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

        # Profil
        staticbox_profil = wx.StaticBoxSizer(self.staticbox_profil_staticbox, wx.VERTICAL)
        staticbox_profil.Add(self.ctrl_profil, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_profil, 1, wx.RIGHT|wx.EXPAND, 5)

        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonAfficher(self, event):
        """ Validation des données saisies """
        # Vérifie date de référence
        date_reference = self.ctrl_date.GetDate()
        if self.ctrl_date.FonctionValiderDate() == False or date_reference == None :
            dlg = wx.MessageDialog(self, _(u"La date de référence ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
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
        self.parent.ctrl_parametres.periode = (date_debut, date_fin)
        self.parent.ctrl_parametres.MAJ()

    def OnCheckActivites(self):
        date_debut, date_fin = self.GetPeriode() 
        self.parent.ctrl_parametres.periode = (date_debut, date_fin)
        self.parent.ctrl_parametres.listeActivites = self.ctrl_activites.GetActivites()
        self.parent.ctrl_parametres.MAJ()
    
    def GetActivites(self):
        return self.ctrl_activites.GetActivites() 

    def GetNomsActivites(self):
        listeTemp = self.ctrl_activites.GetLabelActivites()
        return ", ".join(listeTemp)

    def GetLabelParametres(self):
        # Label Paramètres
        listeParametres = [ 
            _(u"Période du %s au %s") % (UTILS_Dates.DateEngFr(str(self.ctrl_date_debut.GetDate())), UTILS_Dates.DateEngFr(str(self.ctrl_date_fin.GetDate()))),
            _(u"Activités : %s") % self.GetNomsActivites(),
            ]
        labelParametres = " | ".join(listeParametres)
        return labelParametres



# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.date_debut = None
        self.date_fin = None

        # Bandeau
        intro = _(u"Vous pouvez ici générer l'état global des consommations. C'est ici que vous pouvez notamment extraire des données à destination de la CAF ou de la MSA. Commencez par saisir une période de référence et sélectionnez une ou plusieurs activités. Après avoir renseigné les paramètres de calcul et les options, vous pouvez cliquer sur le bouton de sauvegarde d'un profil pour mémoriser la configuration. Vous pourrez ainsi la réutiliser facilement ultérieurement.")
        titre = _(u"Etat global des consommations")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Tableaux.png")
        self.SetTitle(titre)
        
        # Panel Paramètres
        self.panel_parametres = Parametres(self)
        
        # Paramètres de calcul
        self.staticbox_parametres_staticbox = wx.StaticBox(self, -1, _(u"Paramètres de calcul"))
        self.ctrl_parametres = CTRL_Etat_global_parametres.CTRL(self)

        # Options
        self.staticbox_filtres_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.ctrl_options = CTRL_Etat_global_options.CTRL(self)
        self.ctrl_options.SetMinSize((-1, 130))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Aperçu"), cheminImage="Images/32x32/Apercu.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonFermer, self.bouton_fermer)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        # Données Test
        anneeActuelle = datetime.date.today().year
        self.panel_parametres.ctrl_date_debut.SetDate(datetime.date(anneeActuelle, 1, 1))
        self.panel_parametres.ctrl_date_fin.SetDate(datetime.date(anneeActuelle, 12, 31))
                

    def __set_properties(self):
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour créer un aperçu des résultats (PDF)"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.SetMinSize((1020, 720))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.panel_parametres, 1, wx.EXPAND, 0)
        
        grid_sizer_droit = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        # Ctrl des parametres
        staticbox_parametres = wx.StaticBoxSizer(self.staticbox_parametres_staticbox, wx.VERTICAL)
        staticbox_parametres.Add(self.ctrl_parametres, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_droit.Add(staticbox_parametres, 1, wx.EXPAND, 5)

        # Ctrl des filtres
        staticbox_filtres = wx.StaticBoxSizer(self.staticbox_filtres_staticbox, wx.VERTICAL)
        staticbox_filtres.Add(self.ctrl_options, 1, wx.ALL|wx.EXPAND, 5)
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
        UTILS_Dialogs.AjusteSizePerso(self, __file__)
        self.CenterOnScreen()
    
    def OnBoutonFermer(self, event):
        UTILS_Dialogs.SaveSizePerso(self, __file__)
        self.EndModal(wx.ID_CANCEL)
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Etatglobal")
    
    def OnClose(self, event=None):
        event.Skip()

    def GetParametres(self):
        """ Récupération des paramètres """
        dictParametres = {}
        dictParametres.update(self.ctrl_options.GetParametres())
        dictParametres.update(self.ctrl_parametres.GetParametres())
        return dictParametres

    def SetParametres(self, dictParametres={}):
        """ Importation des paramètres """
        self.ctrl_parametres.SetParametres(dictParametres)
        self.ctrl_options.SetParametres(dictParametres)

    def Apercu(self, event):
        """ Génération du document PDF """
        listeAnomalies = []

        # Validation de la période
        date_debut = self.panel_parametres.ctrl_date_debut.GetDate() 
        if self.panel_parametres.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, _(u"La date de début de période semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        date_fin = self.panel_parametres.ctrl_date_fin.GetDate() 
        if self.panel_parametres.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de période semble incorrecte !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        if date_fin < date_debut :
            dlg = wx.MessageDialog(self, _(u"La date de début de période est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Validation des activités
        listeActivites = self.panel_parametres.GetActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous devez sélectionner au moins une activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Récupération des méthodes de calcul
        dictUnites = self.ctrl_parametres.GetDonnees()
        if dictUnites == False :
            return False
        
        # Récupération des options
        if self.ctrl_options.Validation() == False :
            return False
        dict_options = self.ctrl_options.GetParametres()

        modeAffichage = dict_options["format_donnees"]
        modePeriodesDetail = dict_options["periodes_detaillees"]
        regroupement_principal = dict_options["regroupement_principal"]
        liste_regroupements = dict_options["regroupement_age"]
        jours_scolaires = dict_options["jours_hors_vacances"]
        jours_vacances = dict_options["jours_vacances"]
        etats = dict_options["etat_consommations"]

        # Récupération du labelParametres
        labelParametres = self.panel_parametres.GetLabelParametres()

        # Chargement des informations individuelles
        if self.date_debut != date_debut :

            # Infos individus et familles
            self.infosIndividus = UTILS_Infos_individus.Informations(date_reference=date_debut, qf=True, inscriptions=True, messages=False, infosMedicales=False, cotisationsManquantes=False, piecesManquantes=False, questionnaires=True, scolarite=True)
            self.dictInfosIndividus = self.infosIndividus.GetDictValeurs(mode="individu", ID=None, formatChamp=False)
            self.dictInfosFamilles = self.infosIndividus.GetDictValeurs(mode="famille", ID=None, formatChamp=False)

        # Mémorisation des paramètres
        self.date_debut = date_debut
        self.date_fin = date_fin

        # Vérifie que toutes les familles ont une caisse attribuées
        if dict_options["afficher_regime_inconnu"] == True :
            listeFamillesSansCaisses = OL_Liste_regimes.GetFamillesSansCaisse(listeActivites, date_debut, date_fin)
            if len(listeFamillesSansCaisses) > 0 :
                listeTemp = []
                for dictTemp in listeFamillesSansCaisses :
                    listeTemp.append(dictTemp["titulaires"])
                messageDetail = u"\n".join(listeTemp)
                dlg = dialogs.MultiMessageDialog(self, _(u"Attention, le régime d'appartenance n'a pas été renseigné pour les %d familles suivantes :") % len(listeTemp), caption=_(u"Régime d'appartenance"), msg2=messageDetail, style = wx.ICON_EXCLAMATION | wx.OK | wx.CANCEL, btnLabels={wx.ID_OK : _(u"Continuer quand même"), wx.ID_CANCEL : _(u"Annuler")})
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse == wx.ID_CANCEL :
                    return

        DB = GestionDB.DB()

        # Etiquettes
        dictEtiquettes = {}
        req = """SELECT IDetiquette, label, IDactivite, parent, ordre, couleur
        FROM etiquettes;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        for IDetiquette, label, IDactivite, parent, ordre, couleur in listeDonnees :
            couleurTemp = couleur[1:-1].split(",")
            couleur = wx.Colour(int(couleurTemp[0]), int(couleurTemp[1]), int(couleurTemp[2]))
            dictEtiquettes[IDetiquette] = {"label" : label, "IDactivite" : IDactivite, "parent" : parent, "ordre" : ordre, "couleur" : couleur}

        # Récupération des régimes
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

        # Récupération des périodes de vacances
        req = """SELECT 
        IDvacance, nom, annee, date_debut, date_fin
        FROM vacances
        ORDER BY date_debut
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()     
        listeVacances = []
        for IDvacance, nom, annee, date_debut_Tmp, date_fin_Tmp in listeDonnees :
            date_debut_Tmp = UTILS_Dates.DateEngEnDateDD(date_debut_Tmp)
            date_fin_Tmp = UTILS_Dates.DateEngEnDateDD(date_fin_Tmp)
            if date_debut_Tmp.month in (6, 7, 8, 9) or date_fin_Tmp.month in (6, 7, 8, 9) :
                grandesVacs = True
            else:
                grandesVacs = False
            listeVacances.append( {"nom" : nom, "annee" : annee, "date_debut" : date_debut_Tmp, "date_fin" : date_fin_Tmp, "vacs" : True, "grandesVacs" : grandesVacs} )
        
        # Calcul des périodes détaillées
        listePeriodesDetail = []
        index = 0
        for dictTemp in listeVacances :
            # Vacances
            if dictTemp["nom"] == _(u"Février") : 
                nom = "vacances_fevrier"
            elif dictTemp["nom"] == _(u"Pâques") : 
                nom = "vacances_paques"
            elif dictTemp["nom"] == _(u"Eté") : 
                nom = "vacances_ete"
            elif dictTemp["nom"] == _(u"Toussaint") : 
                nom = "vacances_toussaint"
            elif dictTemp["nom"] == _(u"Noël") : 
                nom = "vacances_noel"
            else :
                nom = "?"
            dictTemp["code"] = nom + "_%d" % annee
            dictTemp["label"] = _(u"Vacances %s %d") % (dictTemp["nom"], dictTemp["annee"])
            listePeriodesDetail.append(dictTemp)
            # Hors vacances
            date_debut_temp = dictTemp["date_fin"] + datetime.timedelta(days=1)
            if len(listeVacances) > index + 1 :
                date_fin_temp = listeVacances[index+1]["date_debut"] - + datetime.timedelta(days=1)
                annee = dictTemp["annee"]
                if dictTemp["nom"].startswith("F") : 
                    nom = "mercredis_mars_avril"
                elif dictTemp["nom"].startswith("P") : 
                    nom = "mercredis_mai_juin"
                elif dictTemp["nom"].startswith("E") : 
                    nom = "mercredis_sept_oct"
                elif dictTemp["nom"].startswith("T") : 
                    nom = "mercredis_nov_dec"
                elif dictTemp["nom"].startswith("N") : 
                    nom = "mercredis_janv_fev"
                    annee += 1
                else :
                    nom = "?"
                label = _(u"Hors vacances %s-%s %d") % (LISTE_MOIS[date_debut_temp.month-1], LISTE_MOIS[date_fin_temp.month-1], annee)
                listePeriodesDetail.append( {"code" : nom + "_%d" % annee, "annee" : annee, "label" : label, "date_debut" : date_debut_temp, "date_fin" : date_fin_temp, "vacs" : False, "grandesVacs" : False} )
            index += 1

        # Récupération des tranches de QF des tarifs
        if regroupement_principal == "qf_tarifs":
            if len(listeActivites) == 0 : condition = "AND IDactivite IN ()"
            elif len(listeActivites) == 1 : condition = "AND IDactivite IN (%d)" % listeActivites[0]
            else : condition = "AND IDactivite IN %s" % str(tuple(listeActivites))
            req = """SELECT IDligne, qf_min, qf_max
            FROM tarifs_lignes
            WHERE qf_min IS NOT NULL AND qf_max IS NOT NULL
            %s
            ;""" % condition
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()
            liste_tranches_qf = []
            for IDligne, qf_min, qf_max in listeDonnees:
                tranche = (int(qf_min), int(qf_max))
                if tranche not in liste_tranches_qf :
                    liste_tranches_qf.append(tranche)
                    liste_tranches_qf.sort()

        # Récupération des tranches de qf perso
        if regroupement_principal == "qf_perso":
            liste_tranches_qf = []
            temp = 0
            for x in dict_options["tranches_qf_perso"] :
                liste_tranches_qf.append((temp, x-1))
                temp = x
            liste_tranches_qf.append((temp, 999999))

        # Recherche des données
        listeRegimesUtilises = []


        # Préparation des tranches d'âge
        if len(liste_regroupements) == 0 :
            dict_tranches_age = { 0 : {"label" : u"", "min" : None, "max" : None} }
        else :
            dict_tranches_age = {}
            indexRegroupement = 0
            for regroupement in liste_regroupements :
                if indexRegroupement == 0 :
                    dict_tranches_age[indexRegroupement] = {"label" : _(u"Âge < %d ans") % regroupement, "min" : None, "max" : regroupement}
                else :
                    dict_tranches_age[indexRegroupement] = {"label" : _(u"Âge >= %d et < %d ans") % (liste_regroupements[indexRegroupement-1], regroupement), "min" : liste_regroupements[indexRegroupement-1], "max" : regroupement}
                indexRegroupement += 1
                dict_tranches_age[indexRegroupement] = {"label" : _(u"Âge >= %d ans") % regroupement, "min" : regroupement, "max" : None}


        # Récupère le QF de la famille
        # dictQuotientsFamiliaux = {}
        # if qf != None :
        #     req = """SELECT IDquotient, IDfamille, date_debut, date_fin, quotient
        #     FROM quotients
        #     ORDER BY date_debut;"""
        #     DB.ExecuterReq(req)
        #     listeDonnees = DB.ResultatReq()
        #     for IDquotient, IDfamille, date_debut_temp, date_fin_temp, quotient in listeDonnees :
        #         date_debut_temp = UTILS_Dates.DateEngEnDateDD(date_debut_temp)
        #         date_fin_temp = UTILS_Dates.DateEngEnDateDD(date_fin_temp)
        #         if dictQuotientsFamiliaux.has_key(IDfamille) == False :
        #             dictQuotientsFamiliaux[IDfamille] = []
        #         dictQuotientsFamiliaux[IDfamille].append((date_debut_temp, date_fin_temp, quotient))

        # Récupération des consommations
        listeUnitesUtilisees = dictUnites.keys()
        if len(listeUnitesUtilisees) == 0 : conditionSQL = "AND consommations.IDunite IN ()"
        elif len(listeUnitesUtilisees) == 1 : conditionSQL = "AND consommations.IDunite IN (%d)" % listeUnitesUtilisees[0]
        else : conditionSQL = "AND consommations.IDunite IN %s" % str(tuple(listeUnitesUtilisees))

        req = """SELECT IDconso, consommations.date, consommations.IDindividu, consommations.IDunite, consommations.IDgroupe, consommations.IDactivite, consommations.etiquettes,
        heure_debut, heure_fin, etat, quantite, consommations.IDprestation, prestations.temps_facture,
        comptes_payeurs.IDfamille, activites.nom, groupes.nom, categories_tarifs.nom, 
        familles.IDcaisse, caisses.IDregime, individus.date_naiss
        FROM consommations
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        LEFT JOIN familles ON familles.IDfamille = comptes_payeurs.IDfamille
        LEFT JOIN caisses ON caisses.IDcaisse = familles.IDcaisse
        LEFT JOIN prestations ON prestations.IDprestation = consommations.IDprestation
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        LEFT JOIN groupes ON groupes.IDgroupe = consommations.IDgroupe
        LEFT JOIN categories_tarifs ON categories_tarifs.IDcategorie_tarif = consommations.IDcategorie_tarif
        WHERE consommations.date >='%s' AND consommations.date <='%s'
        AND etat NOT IN ('attente', 'refus')
        %s
        ORDER BY consommations.date;""" % (str(date_debut), str(date_fin), conditionSQL)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()

        dict_resultats = {}

        listePrestationsTraitees = []
        for IDconso, date, IDindividu, IDunite, IDgroupe, IDactivite, etiquettes, heure_debut, heure_fin, etat, quantite, IDprestation, temps_facture, IDfamille, nomActivite, nomGroupe, nomCategorie, IDcaisse, IDregime, date_naiss in listeDonnees:
            date = UTILS_Dates.DateEngEnDateDD(date)
            mois = date.month
            annee = date.year

            if dictUnites.has_key(IDunite) :
                nom_unite_conso = dictUnites[IDunite]["nomUnite"]
            else :
                nom_unite_conso = _(u"Unité inconnue")

            # ------------------------------------ REGROUPEMENT -----------------------------------

            # Recherche du regroupement principal
            try:
                if regroupement_principal == "aucun": regroupement = None
                if regroupement_principal == "jour": regroupement = date
                if regroupement_principal == "mois": regroupement = (annee, mois)
                if regroupement_principal == "annee": regroupement = annee
                if regroupement_principal == "activite": regroupement = nomActivite
                if regroupement_principal == "groupe": regroupement = nomGroupe
                if regroupement_principal == "categorie_tarif": regroupement = nomCategorie
                if regroupement_principal == "unite_conso": regroupement = nom_unite_conso
                if regroupement_principal == "ville_residence": regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_VILLE"]
                if regroupement_principal == "secteur": regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_SECTEUR"]
                if regroupement_principal == "genre": regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_SEXE"]
                if regroupement_principal == "age": regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_AGE_INT"]
                if regroupement_principal == "ville_naissance": regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_VILLE_NAISS"]
                if regroupement_principal == "nom_ecole": regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_ECOLE"]
                if regroupement_principal == "nom_classe": regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_CLASSE"]
                if regroupement_principal == "nom_niveau_scolaire": regroupement = self.dictInfosIndividus[IDindividu]["SCOLARITE_NOM_NIVEAU"]
                if regroupement_principal == "famille": regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM"]
                if regroupement_principal == "individu": regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_NOM_COMPLET"]
                if regroupement_principal == "regime": regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_REGIME"]
                if regroupement_principal == "caisse": regroupement = self.dictInfosFamilles[IDfamille]["FAMILLE_NOM_CAISSE"]
                if regroupement_principal == "categorie_travail": regroupement = self.dictInfosIndividus[IDindividu]["INDIVIDU_CATEGORIE_TRAVAIL"]
                if regroupement_principal == "categorie_travail_pere": regroupement = self.dictInfosIndividus[IDindividu]["PERE_CATEGORIE_TRAVAIL"]
                if regroupement_principal == "categorie_travail_mere": regroupement = self.dictInfosIndividus[IDindividu]["MERE_CATEGORIE_TRAVAIL"]

                # QF par tranche de 100
                if regroupement_principal == "qf_100":
                    regroupement = None
                    qf = self.dictInfosFamilles[IDfamille]["FAMILLE_QF_ACTUEL_INT"]
                    for x in range(0, 10000, 100):
                        min, max = x, x + 99
                        if qf >= min and qf <= max:
                            regroupement = (min, max)

                # QF par tranches
                if regroupement_principal in ("qf_tarifs", "qf_perso") :
                    regroupement = None
                    qf = self.dictInfosFamilles[IDfamille]["FAMILLE_QF_ACTUEL_INT"]
                    for min, max in liste_tranches_qf:
                        if qf >= min and qf <= max:
                            regroupement = (min, max)

                # Etiquettes
                if regroupement_principal == "etiquette":
                    etiquettes = UTILS_Texte.ConvertStrToListe(etiquettes)
                    if len(etiquettes) > 0:
                        temp = []
                        for IDetiquette in etiquettes:
                            if dictEtiquettes.has_key(IDetiquette):
                                temp.append(dictEtiquettes[IDetiquette]["label"])
                        regroupement = temp
                    else:
                        regroupement = _(u"- Aucune étiquette -")

                # Questionnaires
                if regroupement_principal.startswith("question_") and "famille" in regroupement_principal:
                    regroupement = self.dictInfosFamilles[IDfamille]["QUESTION_%s" % regroupement_principal[17:]]
                if regroupement_principal.startswith("question_") and "individu" in regroupement_principal:
                    regroupement = self.dictInfosIndividus[IDindividu]["QUESTION_%s" % regroupement_principal[18:]]

                # Formatage des regroupements de type date
                if type(regroupement) == datetime.date :
                    regroupement = str(regroupement)

            except:
                regroupement = None

            # ------------------------------------ ANALYSE DONNEES -----------------------------------

            if date_naiss != None :
                date_naiss = UTILS_Dates.DateEngEnDateDD(date_naiss)

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
            periode = ""
            if modePeriodesDetail == False :
                # Périodes non détaillées
                for dictVac in listeVacances :
                    if date >= dictVac["date_debut"] and date <= dictVac["date_fin"] :
                        if dictVac["grandesVacs"] == True :
                            periode = "grandesVacs"
                        else:
                            periode = "petitesVacs"
                if periode == "" :
                    periode = "horsVacs"
            else :
                # Périodes détaillées
                for dictPeriode in listePeriodesDetail :
                    if date >= dictPeriode["date_debut"] and date <= dictPeriode["date_fin"] :
                        periode = dictPeriode["code"]

            if periode == "" :
                texte = _(u"Période inconnue pour la date du %s. Vérifiez que les périodes de vacances ont bien été paramétrées.") % UTILS_Dates.DateDDEnFr(date)
                if texte not in listeAnomalies :
                    listeAnomalies.append(texte)

            # ------------ Application de filtres ---------------
            valide = False

            # Période
            if periode == "horsVacs" or periode.startswith("mercredis") :
                if date.weekday() in jours_scolaires :
                    valide = True
            if periode in ("grandesVacs", "petitesVacs") or periode.startswith("vacances") :
                if date.weekday() in jours_vacances :
                    valide = True

            # Etat
            if etat not in etats :
                valide = False

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

                        # Si une heure seuil est demandée
                        heure_seuil = dictCalcul["heure_seuil"]
                        if heure_seuil != None :
                            heure_seuil = UTILS_Dates.HeureStrEnTime(heure_seuil)#datetime.time(hour=int(heure_seuil.split(":")[0]), minute=int(heure_seuil.split(":")[1]))
                            if heure_debut < heure_seuil :
                                heure_debut = heure_seuil

                        # Si une heure plafond est demandée
                        heure_plafond = dictCalcul["heure_plafond"]
                        if heure_plafond != None :
                            heure_plafond = UTILS_Dates.HeureStrEnTime(heure_plafond)#datetime.time(hour=int(heure_plafond.split(":")[0]), minute=int(heure_plafond.split(":")[1]))
                            if heure_fin > heure_plafond :
                                heure_fin = heure_plafond

                        # Calcul de la durée
                        valeur = datetime.timedelta(hours=heure_fin.hour, minutes=heure_fin.minute) - datetime.timedelta(hours=heure_debut.hour, minutes=heure_debut.minute)
                        if "day" in str(valeur) :
                            dlg = wx.MessageDialog(self, _(u"Les horaires de cette consommation sont incorrectes : IDconso=%d | IDindividu=%d | IDfamille=%d | date=%s.") % (IDconso, IDindividu, IDfamille, date), _(u"Erreur"), wx.OK | wx.ICON_ERROR)
                            dlg.ShowModal()
                            dlg.Destroy()
                            return False

                        # Si un arrondi est demandé
                        arrondi = dictCalcul["arrondi"]
                        if arrondi != None :
                            arrondi_type, arrondi_delta = arrondi
                            valeur = UTILS_Dates.CalculerArrondi(arrondi_type=arrondi_type, arrondi_delta=arrondi_delta, heure_debut=heure_debut, heure_fin=heure_fin)

                            # heures = (valeur.days*24) + (valeur.seconds/3600)
                            # minutes = valeur.seconds%3600/60
                            # hr, mn = ArrondirHeureSup(heures, minutes, arrondi)
                            # valeur = datetime.timedelta(hours=hr, minutes=mn)

                        # Si une durée seuil est demandée
                        duree_seuil = dictCalcul["duree_seuil"]
                        if duree_seuil != None :
                            duree_seuil = UTILS_Dates.HeureStrEnDelta(duree_seuil)#datetime.timedelta(hours=int(duree_seuil.split(":")[0]), minutes=int(duree_seuil.split(":")[1]))
                            if valeur < duree_seuil :
                                valeur = duree_seuil

                        # Si une durée plafond est demandée
                        duree_plafond = dictCalcul["duree_plafond"]
                        if duree_plafond != None :
                            duree_plafond = UTILS_Dates.HeureStrEnDelta(duree_plafond)#datetime.timedelta(hours=int(duree_plafond.split(":")[0]), minutes=int(duree_plafond.split(":")[1]))
                            if valeur > duree_plafond :
                                valeur = duree_plafond

                else:
                    # Si c'est en fonction du temps facturé
                    if temps_facture != None and temps_facture != "" :
                        if IDprestation not in listePrestationsTraitees :
                            hr, mn = temps_facture.split(":")
                            valeur = datetime.timedelta(hours=int(hr), minutes=int(mn))
                            listePrestationsTraitees.append(IDprestation)

                # Calcule l'âge de l'individu
                if date_naiss != None :
                    age = (date.year - date_naiss.year) - int((date.month, date.day) < (date_naiss.month, date_naiss.day))
                else :
                    age = None

                # ----- Recherche du regroupement par âge ou date de naissance  -----
                if len(dict_tranches_age) == 0 :
                    index_tranche_age = 0
                else :
                    for key, dictTemp in dict_tranches_age.iteritems() :
                        if dictTemp.has_key("min") :
                            if dictTemp["min"] == None and age < dictTemp["max"] :
                                index_tranche_age = key
                            if dictTemp["max"] == None and age >= dictTemp["min"] :
                                index_tranche_age = key
                            if dictTemp["min"] != None and dictTemp["max"] != None and age >= dictTemp["min"] and age < dictTemp["max"] :
                                index_tranche_age = key

                if age == None :
                    index_tranche_age = None

                # Mémorisation du résultat
                if valeur != datetime.timedelta(hours=0, minutes=0) or valeur != datetime.timedelta(hours=0, minutes=0) :
                    # Si régime inconnu :
                    if dict_options["associer_regime_inconnu"] not in (None, "non", "") and IDregime == None :
                        IDregime = dict_options["associer_regime_inconnu"]

                    # Mémoriser les régimes à afficher
                    if IDregime not in listeRegimesUtilises :
                        listeRegimesUtilises.append(IDregime)

                    # Mémorisation du résultat
                    dict_resultats = UTILS_Divers.DictionnaireImbrique(dictionnaire=dict_resultats, cles=[regroupement, index_tranche_age, periode, IDregime], valeur=datetime.timedelta(hours=0, minutes=0))
                    dict_resultats[regroupement][index_tranche_age][periode][IDregime] += valeur * quantite

        DB.Close() 
        
        # Affichage d'anomalies
        if len(listeAnomalies) > 0 :
            messageDetail = u"\n".join(listeAnomalies)
            dlg = dialogs.MultiMessageDialog(self, _(u"Les %d anomalies suivantes ont été trouvées :") % len(listeAnomalies), caption=_(u"Anomalies"), msg2=messageDetail, style = wx.ICON_ERROR | wx.OK, btnLabels={wx.ID_OK : _(u"Ok")})
            dlg.ShowModal() 
            dlg.Destroy() 
            return
    

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
        if dict_options["orientation"] == "paysage" :
            taillePage = landscape(A4)
        else :
            taillePage = portrait(A4)
        nomDoc = FonctionsPerso.GenerationNomDoc("ETAT_GLOBAL", "pdf")
        if sys.platform.startswith("win") : nomDoc = nomDoc.replace("/", "\\")
        doc = SimpleDocTemplate(nomDoc, pagesize=taillePage, topMargin=20, bottomMargin=20, leftMargin=40, rightMargin=40)
        story = []
        
        largeurContenu = taillePage[0] - 75
        
        # Création du titre du document
        dataTableau = []
        largeursColonnes = ( (largeurContenu-100, 100) )
        dateDuJour = UTILS_Dates.DateEngFr(str(datetime.date.today()))
        dataTableau.append( (_(u"Etat global des consommations"), _(u"%s\nEdité le %s") % (UTILS_Organisateur.GetNom(), dateDuJour)) )
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

        # Insertion du label Paramètres
        styleA = ParagraphStyle(name="A", fontName="Helvetica", fontSize=6, spaceAfter=20)
        story.append(Paragraph(labelParametres, styleA))       

        # Tri du niveau de regroupement principal
        regroupements = dict_resultats.keys()
        regroupements.sort()
        
        listeRegimesUtilises.sort() 
        
        for regroupement in regroupements :
            
            dict_resultats_age = dict_resultats[regroupement]
            dict_totaux_regroupement = {}

            # Création des colonnes
            listeColonnes = []
            largeurColonne = 80
            for IDregime in listeRegimesUtilises :
                if dictRegimes.has_key(IDregime) :
                    nomRegime = dictRegimes[IDregime]
                else:
                    nomRegime = _(u"Sans régime")
                listeColonnes.append((IDregime, nomRegime, largeurColonne))
            listeColonnes.append((2000, _(u"Total"), largeurColonne))
            
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

            if regroupement_principal != "aucun":
                listeStyles.append(('BACKGROUND', (0, 0), (0, 0), UTILS_Divers.ConvertCouleurWXpourPDF(dict_options["couleur_case_regroupement"])))
                listeStyles.append(('TEXTCOLOR', (0, 0), (0, 0), UTILS_Divers.ConvertCouleurWXpourPDF(dict_options["couleur_texte_regroupement"])))

            # Formatage du regroupement
            if regroupement_principal == "aucun" :
                label_regroupement = ""
            elif regroupement_principal == "jour" :
                label_regroupement = UTILS_Dates.DateEngFr(regroupement)
            elif regroupement_principal == "mois" :
                label_regroupement = UTILS_Dates.FormateMois(regroupement)
            elif regroupement_principal == "annee" :
                label_regroupement = str(regroupement)
            elif regroupement_principal.startswith("qf") and type(regroupement) == tuple :
                label_regroupement = u"%d-%d" % regroupement
            elif regroupement_principal == "age" :
                label_regroupement = "%d ans" % regroupement
            else :
                label_regroupement = unicode(regroupement)

            if regroupement_principal != "aucun" and label_regroupement in ("None", "") :
                label_regroupement = _(u"- Non renseigné -")

            # Régimes + total
            ligne1 = [label_regroupement,]
            largeursColonnes = [ 150, ]
            indexColonne = 1
            for IDregime, label, largeur in listeColonnes :
                ligne1.append(label)
                largeursColonnes.append(largeur)
                indexColonne += 1
            
            dataTableau.append(ligne1)

            # Création du tableau d'entete de colonnes
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)

            paraStyle = ParagraphStyle(name="normal",
                          fontName="Helvetica",
                          fontSize=7,
                          leading=7,
                          spaceBefore=0,
                          spaceAfter=0,
                          )

            # Création des lignes
            index = 1
            for index_tranche_age, dict_resultats_periode in dict_resultats_age.iteritems() :
                
                dataTableau = []

                # Création des niveaux de regroupement
                if dict_tranches_age.has_key(index_tranche_age) :
                    label_tranche_age = dict_tranches_age[index_tranche_age]["label"]
                else :
                    label_tranche_age = _(u"Sans date de naissance")

                if label_tranche_age != "" :
                    ligne = [label_tranche_age,]
                    for IDregime, label, largeur in listeColonnes[:-1] :
                        ligne.append("")
                    dataTableau.append(ligne)
                    index += 1
                
                # Création des lignes de périodes
                if modePeriodesDetail == False :
                    listePeriodes = [
                        {"code" : "petitesVacs", "label" : _(u"Petites vacances")},
                        {"code" : "grandesVacs", "label" : _(u"Vacances d'été")},
                        {"code" : "horsVacs", "label" : _(u"Hors vacances")},
                        ]
                else :
                    listePeriodes = listePeriodesDetail
                    
                dictTotaux = {}
                for dictPeriode in listePeriodes :
                    if dict_resultats_periode.has_key(dictPeriode["code"]) :
                        ligne = []
                        
                        # Label ligne
                        if modePeriodesDetail == False :
                            ligne.append(dictPeriode["label"])
                        else :
                            date_debut_temp = dictPeriode["date_debut"]
                            if date_debut_temp < date_debut : 
                                date_debut_temp = date_debut
                            date_fin_temp = dictPeriode["date_fin"]
                            if date_fin_temp > date_fin : 
                                date_fin_temp = date_fin
                            label = _(u"<para align='center'>%s<br/><font size=5>Du %s au %s</font></para>") % (dictPeriode["label"], UTILS_Dates.DateEngFr(str(date_debut_temp)), UTILS_Dates.DateEngFr(str(date_fin_temp)))
                            ligne.append(Paragraph(label, paraStyle))
                            
                        # Valeurs
                        totalLigne = datetime.timedelta(hours=0, minutes=0)
                        for IDregime, labelColonne, largeurColonne in listeColonnes :
                            if IDregime < 1000 :
                                if dict_resultats_periode[dictPeriode["code"]].has_key(IDregime) :
                                    valeur = dict_resultats_periode[dictPeriode["code"]][IDregime]
                                else:
                                    valeur = datetime.timedelta(hours=0, minutes=0)
                                ligne.append(FormateValeur(valeur, modeAffichage))
                                totalLigne += valeur
                                if dictTotaux.has_key(IDregime) == False :
                                    dictTotaux[IDregime] = datetime.timedelta(hours=0, minutes=0)
                                dictTotaux[IDregime] += valeur
                        # Total de la ligne
                        if IDregime == 2000 :
                            ligne.append(FormateValeur(totalLigne, modeAffichage))
                        dataTableau.append(ligne)
                        index += 1
                
                # Création de la ligne de total
                ligne = [_(u"Total"),]
                totalLigne = datetime.timedelta(hours=0, minutes=0)
                indexColonne = 0
                for IDregime, labelColonne, largeurColonne in listeColonnes :
                    if IDregime < 1000 :
                        if dictTotaux.has_key(IDregime) :
                            total = dictTotaux[IDregime]
                        else:
                            total = datetime.timedelta(hours=0, minutes=0)

                        ligne.append(FormateValeur(total, modeAffichage))
                        totalLigne += total

                        if dict_totaux_regroupement.has_key(indexColonne) == False :
                            dict_totaux_regroupement[indexColonne] = datetime.timedelta(hours=0, minutes=0)
                        dict_totaux_regroupement[indexColonne] += total

                    indexColonne += 1


                # Total de la ligne
                if IDregime == 2000 :
                    ligne.append(FormateValeur(totalLigne, modeAffichage))
                dataTableau.append(ligne)
                index += 1

                # Récupération des couleurs
                couleurFondFonce = UTILS_Divers.ConvertCouleurWXpourPDF(dict_options["couleur_ligne_age"])
                couleurFondClair = UTILS_Divers.ConvertCouleurWXpourPDF(dict_options["couleur_ligne_total"])

                listeStyles = [
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), 
                        
                        ('FONT',(0,0),(-1,-1), "Helvetica", 7), 
                        ('GRID', (0,0), (-1,-1), 0.25, colors.black), 
                        ('ALIGN', (0,0), (-1,-1), 'CENTRE'),

                        ('BACKGROUND', (0, -1), (-1, -1), couleurFondClair), 
                        ('BACKGROUND', (-1, 0), (-1, -1), couleurFondClair),

                        ('FONT',(0, -1),(-1, -1), "Helvetica-Bold", 7), # Gras pour totaux
                        ]

                if label_tranche_age != "" :
                    listeStyles.extend([
                        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                        ('SPAN',(0,0),(-1,0)),
                        ('FONT',(0,0),(0,0), "Helvetica-Bold", 7),
                        ('BACKGROUND', (0, 0), (-1, 0), couleurFondFonce),
                        ])

                # Création du tableau
                tableau = Table(dataTableau, largeursColonnes)
                tableau.setStyle(TableStyle(listeStyles))
                story.append(tableau)



            # ---------- TOTAL de L'ACTIVITE --------------
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

            ligne1 = ["",]
            largeursColonnes = [150,]
            indexColonne = 0
            total = datetime.timedelta(hours=0, minutes=0)
            for IDregime, label, largeur in listeColonnes :

                # Colonne Total par régime
                if dict_totaux_regroupement.has_key(indexColonne) :
                    valeur = dict_totaux_regroupement[indexColonne]
                else :
                    valeur = datetime.timedelta(hours=0, minutes=0)
                total += valeur

                # Colonne TOTAL du tableau
                if indexColonne == len(listeColonnes) - 1 :
                    valeur = total

                label = FormateValeur(valeur, modeAffichage)
                ligne1.append(label)
                largeursColonnes.append(largeur)
                indexColonne += 1
            dataTableau.append(ligne1)

            # Création du tableau d'entete de colonnes
            tableau = Table(dataTableau, largeursColonnes)
            tableau.setStyle(TableStyle(listeStyles))
            story.append(tableau)


            # Espace après activité
            story.append(Spacer(0, 20))


        # Enregistrement du PDF
        try :
            doc.build(story)
        except Exception, err :
            print "Erreur dans ouverture PDF :", err
            if "Permission denied" in err :
                dlg = wx.MessageDialog(None, _(u"Noethys ne peut pas créer le PDF.\n\nVeuillez vérifier qu'un autre PDF n'est pas déjà ouvert en arrière-plan..."), _(u"Erreur d'édition"), wx.OK | wx.ICON_ERROR)
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
