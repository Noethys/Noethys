#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime
import time
import sys
import wx.lib.agw.hyperlink as hl

import GestionDB
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Saisie_date
from Ctrl import CTRL_Synthese_modes_reglements
from Ctrl import CTRL_Selection_activites
from Utils import UTILS_Dates



def DateEngEnDateDD(dateEng):
    if dateEng == None or dateEng == "" : return None
    return datetime.date(int(dateEng[:4]), int(dateEng[5:7]), int(dateEng[8:10]))

def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text



class CTRL_Groupes(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.dictDonnees = {}
        self.dictIndex = {}
        self.listeDonnees = self.Importation()
        if self.listeDonnees == None : 
            self.listeDonnees = []
        self.MAJ() 
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)

    def OnCheck(self, event):
        self.parent.OnCheckActivites() 

    def MAJ(self):
        self.listeDonnees = self.Importation()
        self.Clear()
        self.dictIndex = {}
        if self.listeDonnees == None : return
        self.listeDonnees.sort()
        index = 0
        for nomGroupe, IDtype_groupe_activite in self.listeDonnees :
            if nomGroupe == None :
                nomGroupe = _(u"Groupe inconnu")
            self.Append(nomGroupe) 
            self.dictIndex[index] = IDtype_groupe_activite
            index += 1

    def Importation(self):
        DB = GestionDB.DB()
        req = """SELECT IDgroupe_activite, groupes_activites.IDactivite, activites.nom, types_groupes_activites.nom, groupes_activites.IDtype_groupe_activite
        FROM groupes_activites
        LEFT JOIN types_groupes_activites ON types_groupes_activites.IDtype_groupe_activite = groupes_activites.IDtype_groupe_activite
        LEFT JOIN activites ON activites.IDactivite = groupes_activites.IDactivite
        ORDER BY types_groupes_activites.nom;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()
        DB.Close()
        if len(listeActivites) == 0 : return []
        listeDonnees = []
        self.dictDonnees = {}
        for IDgroupe_activite, IDactivite, nomActivite, nomGroupe, IDtype_groupe_activite in listeActivites :
            listeTemp = (nomGroupe, IDtype_groupe_activite)
            if listeTemp not in listeDonnees : 
                listeDonnees.append(listeTemp)
            if (IDtype_groupe_activite in self.dictDonnees) == False :
                self.dictDonnees[IDtype_groupe_activite] = []
            self.dictDonnees[IDtype_groupe_activite].append(IDactivite)            
        return listeDonnees
                            
    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                IDtype_groupe_activite = self.dictIndex[index]
                listeActivites = self.dictDonnees[IDtype_groupe_activite]
                for IDactivite in listeActivites :
                    if IDactivite not in listeIDcoches :
                        listeIDcoches.append(IDactivite)
        listeIDcoches.sort() 
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            ID = self.dictIndex[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1

    def GetLabelsGroupes(self):
        """ Renvoie les labels des groupes d'activités sélectionnés """
        listeLabels = []
        index = 0
        for nomGroupe, IDtype_groupe_activite in self.listeDonnees :
            if self.IsChecked(index):
                listeLabels.append(nomGroupe)
            index += 1
        return listeLabels


# ----------------------------------------------------------------------------------------------------------------------------------

class CTRL_Activites(wx.CheckListBox):
    def __init__(self, parent):
        wx.CheckListBox.__init__(self, parent, -1)
        self.parent = parent
        self.SetMinSize((-1, 100))
        self.MAJ() 
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck)

    def OnCheck(self, event):
        self.parent.OnCheckActivites() 

    def MAJ(self):
        self.listeDonnees = self.Importation()
        self.SetListeChoix()

    def SetListeChoix(self):
        self.Clear()
        listeItems = []
        self.dictIndex = {}
        self.dictActivites = {}
        index = 0
        for IDactivite, nom in self.listeDonnees :
            if nom == None :
                nom = _(u"Activité inconnue")
            self.Append(nom)
            self.dictIndex[index] = IDactivite
            self.dictActivites[IDactivite] = nom
            index += 1

    def Importation(self):
        listeDonnees = []
        DB = GestionDB.DB()
        req = """SELECT IDactivite, nom
        FROM activites
        ORDER BY date_fin DESC
        ;"""
        DB.ExecuterReq(req)
        listeActivites = DB.ResultatReq()      
        DB.Close() 
        return listeActivites

    def GetDictActivites(self):
        return self.dictActivites

    def GetIDcoches(self):
        listeIDcoches = []
        NbreItems = len(self.listeDonnees)
        for index in range(0, NbreItems):
            if self.IsChecked(index):
                listeIDcoches.append(self.dictIndex[index])
        return listeIDcoches
    
    def CocheTout(self):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            self.Check(index)
            index += 1

    def SetIDcoches(self, listeIDcoches=[]):
        index = 0
        for index in range(0, len(self.listeDonnees)):
            ID = self.dictIndex[index]
            if ID in listeIDcoches :
                self.Check(index)
            index += 1
            
# -----------------------------------------------------------------------------------------------------------------------



class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Mode
        self.staticbox_mode_staticbox = wx.StaticBox(self, -1, _(u"Type de règlements"))
        self.radio_saisis = wx.RadioButton(self, -1, _(u"Saisis"), style = wx.RB_GROUP)
        self.radio_deposes = wx.RadioButton(self, -1, _(u"Déposés"))
        self.radio_nondeposes = wx.RadioButton(self, -1, _(u"Non déposés"))

        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Période de référence"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date2(self)

        # Filtres
        self.staticbox_affichage_staticbox = wx.StaticBox(self, -1, _(u"Affichage"))
        self.radio_cotisations = wx.CheckBox(self, -1, _(u"Cotisations"))
        self.radio_consommations = wx.CheckBox(self, -1, _(u"Conso."))
        self.radio_locations = wx.CheckBox(self, -1, _(u"Locations"))
        self.radio_autres = wx.CheckBox(self, -1, _(u"Autres"))
        self.radio_avoirs = wx.CheckBox(self, -1, _(u"Avoirs"))
        self.radio_cotisations.SetValue(True)
        self.radio_consommations.SetValue(True)
        self.radio_locations.SetValue(True)
        self.radio_autres.SetValue(True)
        self.radio_avoirs.SetValue(True)

##        # Activités
##        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
##        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
##        self.ctrl_activites.SetMinSize((-1, 90))

        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.radio_toutes = wx.RadioButton(self, -1, _(u"Toutes les activités"), style=wx.RB_GROUP)
        self.radio_groupes = wx.RadioButton(self, -1, _(u"Sélectionner un groupe d'activités"))
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((-1, 60))
        self.radio_activites = wx.RadioButton(self, -1, _(u"Sélectionner une ou plusieurs activités"))
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((200, 60))

        # Boutons Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_actualiser.SetMinSize((-1, 50)) 

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_cotisations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_consommations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_locations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_autres)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_avoirs)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_saisis)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_deposes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioMode, self.radio_nondeposes)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_groupes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_activites)

        # Init Contrôles
        self.OnRadioActivites(None)



    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez la date de début de période")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez la date de fin de période")))
        self.radio_saisis.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour considérer les règlements saisis dans Noethys sur la période de référence")))
        self.radio_deposes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour considérer les règlements déposés en banque sur la période de référence")))
        self.radio_deposes.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour considérer les règlements pas encore déposés en banque à ce jour")))
        self.radio_cotisations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les cotisations dans la synthèse")))
        self.radio_consommations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les consommations dans la synthèse")))
        self.radio_locations.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les locations dans la synthèse")))
        self.radio_autres.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les autres types de prestations dans la synthèse")))
        self.radio_avoirs.SetToolTip(wx.ToolTip(_(u"Cochez cette case pour afficher les avoirs (règlements non ventilés)")))
        self.bouton_actualiser.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour actualiser les résultats en fonction des paramètres sélectionnés")))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        
        # Mode 
        staticbox_mode = wx.StaticBoxSizer(self.staticbox_mode_staticbox, wx.VERTICAL)
        grid_sizer_mode = wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5)
        grid_sizer_mode.Add(self.radio_saisis, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mode.Add(self.radio_deposes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_mode.Add(self.radio_nondeposes, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_mode.Add(grid_sizer_mode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_mode, 1, wx.RIGHT|wx.EXPAND, 5)

        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_periode, 1, wx.RIGHT|wx.EXPAND, 5)

        # Filtres 
        staticbox_affichage = wx.StaticBoxSizer(self.staticbox_affichage_staticbox, wx.VERTICAL)
        grid_sizer_affichage = wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_cotisations, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_affichage.Add(self.radio_consommations, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_locations, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_autres, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_affichage.Add(self.radio_avoirs, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_affichage.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_affichage, 1, wx.RIGHT|wx.EXPAND, 5)

        # Activités
##        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
##        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
##        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)

        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        grid_sizer_activites = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        grid_sizer_activites.Add(self.radio_toutes, 0, 0, 0)
        grid_sizer_activites.Add(self.radio_groupes, 0, 0, 0)
        grid_sizer_activites.Add(self.ctrl_groupes, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_activites.Add(self.radio_activites, 0, 0, 0)
        grid_sizer_activites.Add(self.ctrl_activites, 0, wx.LEFT|wx.EXPAND, 18)
        grid_sizer_activites.AddGrowableRow(2)
        grid_sizer_activites.AddGrowableRow(4)
        grid_sizer_activites.AddGrowableCol(0)
        staticbox_activites.Add(grid_sizer_activites, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)

        # Bouton Actualiser
        grid_sizer_base.Add(self.bouton_actualiser, 1, wx.RIGHT|wx.EXPAND, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(3)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadioActivites(self, event): 
        self.ctrl_activites.Enable(self.radio_activites.GetValue())
        self.ctrl_groupes.Enable(self.radio_groupes.GetValue())
        try :
            self.parent.MAJ()
        except : pass

    def OnRadioMode(self, event):
        self.parent.MAJ()
        self.ctrl_date_debut.Enable(not self.radio_nondeposes.GetValue())
        self.ctrl_date_fin.Enable(not self.radio_nondeposes.GetValue())

    def GetMode(self):
        if self.radio_saisis.GetValue() == True : return "saisis"
        if self.radio_deposes.GetValue() == True : return "deposes"
        if self.radio_nondeposes.GetValue() == True : return "nondeposes"
            
    def OnBoutonActualiser(self, event):
        """ Validation des données saisies """
        # Vérifie date de référence
        date_debut = self.ctrl_date_debut.GetDate()
        if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
            dlg = wx.MessageDialog(self, _(u"La date de début de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        date_fin = self.ctrl_date_fin.GetDate()
        if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
            dlg = wx.MessageDialog(self, _(u"La date de fin de période ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_fin.SetFocus()
            return False
        
        # Envoi des données
        self.parent.MAJ()
        
        return True

    def OnCheckFiltres(self, event):
        self.parent.MAJ()
        
    def OnCheckActivites(self):
        self.parent.MAJ()

    def GetActivites(self):
        if self.radio_toutes.GetValue() == True :
            listeActivites = "toutes"
        if self.radio_groupes.GetValue() == True :
            listeActivites = self.ctrl_groupes.GetIDcoches()
        if self.radio_activites.GetValue() == True :
            listeActivites = self.ctrl_activites.GetIDcoches()
        return listeActivites
    
    def GetFiltres(self):
        listeFiltres = []
        if self.radio_cotisations.GetValue() == True : listeFiltres.append("cotisation")
        if self.radio_consommations.GetValue() == True : listeFiltres.append("consommation")
        if self.radio_locations.GetValue() == True: listeFiltres.append("location")
        if self.radio_autres.GetValue() == True : listeFiltres.append("autre")
        if self.radio_avoirs.GetValue() == True : listeFiltres.append("avoir")
        return listeFiltres

    def GetDictActivites(self):
        if self.radio_groupes.GetValue() == True :
            dictActivites = self.ctrl_groupes.GetDictActivites()
        else:
            dictActivites = self.ctrl_activites.GetDictActivites()
        return dictActivites

    def GetLabelActivites(self):
        """ Renvoie les labels des groupes ou activités sélectionnées """
        if self.radio_toutes.GetValue() == True :
            return _(u"Toutes les activités")
        if self.radio_groupes.GetValue() == True :
            # Groupe d'activités
            listeTemp = self.ctrl_groupes.GetLabelsGroupes()
            return ", ".join(listeTemp)
        else :
            # Activités
            listeTemp = []
            dictActivites = self.GetDictActivites()
            for IDactivite in self.ctrl_activites.GetIDcoches()  :
                listeTemp.append(dictActivites[IDactivite])
            return ", ".join(listeTemp)



# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici afficher la répartition des modes de règlements par activité. Commencez par sélectionner un mode de calcul, saisir une période de référence puis sélectionner les activités souhaitées. Il est ensuite possible d'exporter les résultats sous forme de PDF ou sous Ms Excel.")
        titre = _(u"Synthèse des modes de règlements")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Diagramme.png")
        self.SetTitle(titre)
        
        # Panel Paramètres
        self.ctrl_parametres = Parametres(self)
        
        # CTRL Coefficients
        self.staticbox_stats_staticbox = wx.StaticBox(self, -1, _(u"Résultats"))
        self.ctrl_stats = CTRL_Synthese_modes_reglements.CTRL(self)
        
        # Commandes de liste
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_excel = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Excel.png"), wx.BITMAP_TYPE_ANY))

        # Commandes de résultats
        self.check_details = wx.CheckBox(self, -1, _(u"Afficher détails"))
        self.check_details.SetValue(True) 

        self.hyper_developper = self.Build_Hyperlink_developper()
        self.label_barre = wx.StaticText(self, -1, u"|")
        self.hyper_reduire = self.Build_Hyperlink_reduire()
        
        # Commandes
        self.label_ventilation = wx.StaticText(self, -1, _(u"Filtre de ventilation :"))
        self.ctrl_ventilation = wx.Choice(self, -1, choices = [])
        self.ctrl_ventilation.Select(0)
        self.label_du = wx.StaticText(self, -1, u"du")
        self.ctrl_ventilation_debut = CTRL_Saisie_date.Date2(self)
        self.label_au = wx.StaticText(self, -1, _(u"au"))
        self.ctrl_ventilation_fin = CTRL_Saisie_date.Date2(self)
        self.bouton_actualiser = wx.Button(self, -1, _(u"Actualiser"))

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixVentilation, self.ctrl_ventilation)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonImprimer, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonExcel, self.bouton_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckDetails, self.check_details)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)

        self.__set_properties()
        self.__do_layout()
                
        # Initialisation des contrôles
        anneeActuelle = datetime.date.today().year
        self.ctrl_parametres.ctrl_date_debut.SetDate(datetime.date(anneeActuelle, 1, 1))
        self.ctrl_parametres.ctrl_date_fin.SetDate(datetime.date(anneeActuelle, 12, 31))
        
        self.MAJ() 

        self.OnChoixVentilation(None) 


    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu avant impression des résultats (PDF)")))
        self.bouton_excel.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour exporter les résultats au format MS Excel")))
        self.check_details.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher les détails dans les résultats")))
        self.ctrl_ventilation.SetToolTip(wx.ToolTip(_(u"Vous pouvez filtrer ici les résultats par période de ventilation")))
        self.SetMinSize((980, 720))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # STATS
        staticbox_stats= wx.StaticBoxSizer(self.staticbox_stats_staticbox, wx.VERTICAL)
        grid_sizer_contenu2 = wx.FlexGridSizer(rows=3, cols=2, vgap=5, hgap=5)

        # Commandes de liste
        grid_sizer_ventilation = wx.FlexGridSizer(rows=1, cols=9, vgap=5, hgap=5)
        grid_sizer_ventilation.Add(self.label_ventilation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ventilation.Add(self.ctrl_ventilation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ventilation.Add(self.label_du, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ventilation.Add(self.ctrl_ventilation_debut, 0, wx.EXPAND, 0)
        grid_sizer_ventilation.Add(self.label_au, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ventilation.Add(self.ctrl_ventilation_fin, 0, wx.EXPAND, 0)
        grid_sizer_ventilation.Add(self.bouton_actualiser, 0, wx.EXPAND, 0)

        grid_sizer_contenu2.Add(grid_sizer_ventilation, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu2.Add( (5, 5), 0, wx.EXPAND, 0)

        # Résultats
        grid_sizer_contenu2.Add(self.ctrl_stats, 1, wx.EXPAND, 0)
        
        # Boutons de liste
        grid_sizer_commandes = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_commandes.Add(self.bouton_apercu, 0, wx.EXPAND, 0)
        grid_sizer_commandes.Add(self.bouton_excel, 0, wx.EXPAND, 0)
        grid_sizer_contenu2.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        
        # Commandes de liste
        grid_sizer_commandes2 = wx.FlexGridSizer(rows=1, cols=9, vgap=5, hgap=5)
        grid_sizer_commandes2.Add( (30, 5), 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.check_details, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.Add( (30, 5), 0, wx.EXPAND, 0)
        grid_sizer_commandes2.Add(self.hyper_developper, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.Add(self.label_barre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.Add(self.hyper_reduire, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes2.AddGrowableCol(0)
        grid_sizer_contenu2.Add(grid_sizer_commandes2, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu2.AddGrowableRow(1)
        grid_sizer_contenu2.AddGrowableCol(0)
        
        staticbox_stats.Add(grid_sizer_contenu2, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_contenu.Add(staticbox_stats, 1, wx.RIGHT|wx.EXPAND, 5)

        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def Build_Hyperlink_developper(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"Tout développer"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_developper)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Tout développer")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_developper(self, event):
        self.ctrl_stats.DevelopperTout()

    def Build_Hyperlink_reduire(self) :
        """ Construit un hyperlien """
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
        hyper = hl.HyperLinkCtrl(self, -1, _(u"Tout réduire"), URL="")
        hyper.Bind(hl.EVT_HYPERLINK_LEFT, self.OnLeftLink_reduire)
        hyper.AutoBrowse(False)
        hyper.SetColours("BLUE", "BLUE", "BLUE")
        hyper.EnableRollover(True)
        hyper.SetUnderlines(False, False, True)
        hyper.SetBold(False)
        hyper.SetToolTip(wx.ToolTip(_(u"Tout réduire")))
        hyper.UpdateLink()
        hyper.DoPopup(False)
        return hyper
        
    def OnLeftLink_reduire(self, event):
        self.ctrl_stats.ReduireTout()

    def OnCheckDetails(self, event):
        etat = self.check_details.GetValue()
        self.ctrl_stats.SetAffichageDetails(etat)
        self.MAJ() 
        self.hyper_developper.Enable(-etat)
        self.label_barre.Enable(-etat)
        self.hyper_reduire.Enable(-etat)
    
    def InitChoixAnneeVentilation(self):
        valeur = self.ctrl_ventilation.GetStringSelection() 
        listeAnnees = self.ctrl_stats.GetVentilation()
        listeAnnees.sort()
        listeTemp = [_(u"Aucun"), _(u"Non ventilé"), _(u"La période suivante")]
        for annee in listeAnnees :
            listeTemp.append(str(annee))
        self.ctrl_ventilation.SetItems(listeTemp)
        self.ctrl_ventilation.Select(0)
        try :
            self.ctrl_ventilation.SetStringSelection(valeur)
        except :
            pass
    
    def GetVentilation(self):
        selection = self.ctrl_ventilation.GetSelection()
        if selection == 0 :
            periode = None
        elif selection == 1 :
            periode = 0
        elif selection == 2 :
            periode = [self.ctrl_ventilation_debut.GetDate(), self.ctrl_ventilation_fin.GetDate()]
        else :
            periode = int(self.ctrl_ventilation.GetStringSelection())
        return periode
        
    def OnChoixVentilation(self, event):
        periode = self.GetVentilation()
        self.ctrl_stats.SetVentilation(periode)
        if type(periode) == list :
            etat = True
        else :
            etat = False
        self.label_du.Enable(etat)
        self.ctrl_ventilation_debut.Enable(etat)
        self.label_au.Enable(etat)
        self.ctrl_ventilation_fin.Enable(etat)
        self.bouton_actualiser.Enable(etat)
        if etat == True and self.ctrl_ventilation_debut.GetDate() == None :
            self.ctrl_ventilation_debut.SetFocus()
        self.MAJ() 

    def OnBoutonActualiser(self, event=None):
        periode = self.GetVentilation()
        self.ctrl_stats.SetVentilation(periode)
        self.MAJ() 

    def MAJ(self, event=None):
        mode = self.ctrl_parametres.GetMode()
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate()
        listeActivites = self.ctrl_parametres.GetActivites() 
        filtres = self.ctrl_parametres.GetFiltres()
        self.ctrl_stats.MAJ(mode=mode, date_debut=date_debut, date_fin=date_fin, listeActivites=listeActivites, filtres=filtres) 
        self.InitChoixAnneeVentilation() 

    def GetLabelParametres(self):
        listeParametres = []

        # Dates et Mode
        mode = self.ctrl_parametres.GetMode() 
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate()
        if date_debut == None : date_debut = "---"
        if date_fin == None : date_fin= "---"
        if mode == "saisis" : listeParametres.append(_(u"Règlements saisis du %s au %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin))))
        if mode == "deposes" : listeParametres.append(_(u"Règlements déposés du %s au %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin))))
        if mode == "nondeposes" : listeParametres.append(_(u"Règlements non déposés"))
        
        # Affichage
        listeAffichage = []
        for filtre in self.ctrl_parametres.GetFiltres() :
            if filtre == "consommation" : listeAffichage.append("Consommations")
            if filtre == "cotisation" : listeAffichage.append("Cotisations")
            if filtre == "location": listeAffichage.append("Locations")
            if filtre == "autre" : listeAffichage.append("Autres")
            if filtre == "avoir" : listeAffichage.append("Avoirs")
        affichage = ", ".join(listeAffichage)
        listeParametres.append(_(u"Eléments affichés : %s") % affichage)
        
        # Activités
        activites = self.ctrl_parametres.GetLabelActivites()
        listeParametres.append(_(u"Activités : %s") % activites)
        
        # Année de ventilation
        ventilation = self.GetVentilation() 
        if ventilation != None :
            if ventilation == 0 : 
                listeParametres.append(_(u"Uniquement des règlements non ventilés"))
            elif type(ventilation) == list :
                listeParametres.append(_(u"Uniquement des règlements ventilés sur la période du %s au %s") % (UTILS_Dates.DateDDEnFr(ventilation[0]), UTILS_Dates.DateDDEnFr(ventilation[1])))
            else :
                listeParametres.append(_(u"Uniquement des règlements ventilés sur l'année %d") % ventilation)
        
        labelParametres = " | ".join(listeParametres)
        return labelParametres

    def OnBoutonImprimer(self, event):
        labelParametres = self.GetLabelParametres() 
        self.ctrl_stats.labelParametres = labelParametres
        self.ctrl_stats.Imprimer() 

    def OnBoutonExcel(self, event):
        self.ctrl_stats.ExportExcel() 
        
    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Synthsedesmodesderglements")



# -------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
