#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import time
import sys

import GestionDB
import CTRL_Bandeau
import CTRL_Saisie_date
import OL_Liste_deductions

try: import psyco; psyco.full()
except: pass


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
            if self.dictDonnees.has_key(IDtype_groupe_activite) == False :
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
        index = 0
        for IDactivite, nom in self.listeDonnees :
            if nom == None : nom = u"Activité inconnue"
            self.Append(nom)
            self.dictIndex[index] = IDactivite
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
    
    def GetDictActivites(self):
        dictActivites = {}
        for IDactivite, nom in self.listeDonnees :
            dictActivites[IDactivite] = nom
        return dictActivites
        
            
# -----------------------------------------------------------------------------------------------------------------------



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

        # Filtres
        self.staticbox_affichage_staticbox = wx.StaticBox(self, -1, _(u"Affichage"))
        self.radio_cotisations = wx.CheckBox(self, -1, _(u"Cotisations"))
        self.radio_consommations = wx.CheckBox(self, -1, _(u"Consommations"))
        self.radio_autres = wx.CheckBox(self, -1, _(u"Autres"))
        self.radio_cotisations.SetValue(True)
        self.radio_consommations.SetValue(True)
        self.radio_autres.SetValue(True)

        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.radio_toutes = wx.RadioButton(self, -1, _(u"Toutes les activités"), style=wx.RB_GROUP)
        self.radio_groupes = wx.RadioButton(self, -1, _(u"Sélectionner un groupe d'activités"))
        self.ctrl_groupes = CTRL_Groupes(self)
        self.ctrl_groupes.SetMinSize((150, 60))
        self.radio_activites = wx.RadioButton(self, -1, _(u"Sélectionner une ou plusieurs activités"))
        self.ctrl_activites = CTRL_Activites(self)
        self.ctrl_activites.SetMinSize((150, 60))

        # Boutons Actualiser
        self.bouton_actualiser = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_actualiser.SetMinSize((-1, 50)) 

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_cotisations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_consommations)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckFiltres, self.radio_autres)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonActualiser, self.bouton_actualiser)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_toutes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_groupes)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioActivites, self.radio_activites)

        # Init Contrôles
        self.OnRadioActivites(None)



    def __set_properties(self):
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début de période"))
        self.ctrl_date_fin.SetToolTipString(_(u"Saisissez la date de fin de période"))
        self.radio_cotisations.SetToolTipString(_(u"Cochez cette case pour afficher les cotisations dans la synthèse"))
        self.radio_consommations.SetToolTipString(_(u"Cochez cette case pour afficher les consommations dans la synthèse"))
        self.radio_autres.SetToolTipString(_(u"Cochez cette case pour afficher les autres types de prestations dans la synthèse"))
        self.bouton_actualiser.SetToolTipString(_(u"Cliquez ici pour actualiser les résultats en fonction des paramètres sélectionnés"))
        
    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
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
        grid_sizer_affichage = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_affichage.Add(self.radio_cotisations, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_affichage.Add(self.radio_consommations, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_affichage.Add(self.radio_autres, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
        staticbox_affichage.Add(grid_sizer_affichage, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_affichage, 1, wx.RIGHT|wx.EXPAND, 5)

        # Activités
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
        grid_sizer_base.AddGrowableRow(2)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadioActivites(self, event): 
        self.ctrl_activites.Enable(self.radio_activites.GetValue())
        self.ctrl_groupes.Enable(self.radio_groupes.GetValue())
        try :
            self.parent.MAJ()
        except : pass
            
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
        if self.radio_autres.GetValue() == True : listeFiltres.append("autre")
        return listeFiltres

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
            dictActivites = self.ctrl_activites.GetDictActivites()
            for IDactivite in self.ctrl_activites.GetIDcoches()  :
                listeTemp.append(dictActivites[IDactivite])
            return ", ".join(listeTemp)


# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Vous pouvez ici afficher la liste détaillée des déductions. Commencez par saisir une période de référence puis sélectionnez les activités à afficher. Il est ensuite possible d'imprimer les résultats ou de les exporter sous Ms Excel.")
        titre = _(u"Liste des déductions")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Euro.png")
        self.SetTitle(titre)
        
        # Panel Paramètres
        self.ctrl_parametres = Parametres(self)
        
        # ListView
        self.ctrl_listview = OL_Liste_deductions.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((100, 100))
        self.ctrl_recherche = OL_Liste_deductions.CTRL_Outils(self, listview=self.ctrl_listview, afficherCocher=True)
        
        # Commandes de liste
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Imprimante.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_texte = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Texte2.png", wx.BITMAP_TYPE_ANY))
        self.bouton_export_excel = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Excel.png", wx.BITMAP_TYPE_ANY))
        
        # Commandes
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Modifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Supprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportTexte, self.bouton_export_texte)
        self.Bind(wx.EVT_BUTTON, self.ctrl_listview.ExportExcel, self.bouton_export_excel)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

        self.__set_properties()
        self.__do_layout()
                
        # Initialisation des contrôles
        anneeActuelle = datetime.date.today().year
        self.ctrl_parametres.ctrl_date_debut.SetDate(datetime.date(anneeActuelle, 1, 1))
        self.ctrl_parametres.ctrl_date_fin.SetDate(datetime.date(anneeActuelle, 12, 31))
        
        self.MAJ() 

    def __set_properties(self):
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_fermer.SetToolTipString(_(u"Cliquez ici pour fermer"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la déduction sélectionnée dans la liste"))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour modifier la déduction sélectionnée dans la liste"))
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour créer un aperçu de la liste"))
        self.bouton_imprimer.SetToolTipString(_(u"Cliquez ici pour imprimer la liste"))
        self.bouton_export_texte.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Texte"))
        self.bouton_export_excel.SetToolTipString(_(u"Cliquez ici pour exporter la liste au format Excel"))
        self.SetMinSize((980, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # CTRL
        grid_sizer_contenu2 = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        
        grid_sizer_contenu2.Add(self.ctrl_listview, 1, wx.EXPAND, 0)
        
        # Boutons de liste
        grid_sizer_droit = wx.FlexGridSizer(rows=8, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_droit.Add( (10, 10), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_droit.Add( (5, 5), 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_export_texte, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_export_excel, 0, 0, 0)
        grid_sizer_contenu2.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        # Commandes de liste
        grid_sizer_contenu2.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)

        grid_sizer_contenu2.AddGrowableRow(0)
        grid_sizer_contenu2.AddGrowableCol(0)
        
        grid_sizer_contenu.Add(grid_sizer_contenu2, 1, wx.EXPAND, 0)

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
        
    def MAJ(self):
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate()
        listeActivites = self.ctrl_parametres.GetActivites() 
        filtres = self.ctrl_parametres.GetFiltres()
        labelParametres = self.GetLabelParametres() 
        self.ctrl_listview.MAJ(date_debut=date_debut, date_fin=date_fin, listeActivites=listeActivites, filtres=filtres, labelParametres=labelParametres) 

    def GetLabelParametres(self):
        listeParametres = []

        # Dates et Mode
        date_debut = self.ctrl_parametres.ctrl_date_debut.GetDate()
        date_fin = self.ctrl_parametres.ctrl_date_fin.GetDate()
        if date_debut == None : date_debut = "---"
        if date_fin == None : date_fin= "---"
        listeParametres.append(_(u"Période du %s au %s") % (DateEngFr(str(date_debut)), DateEngFr(str(date_fin))))
        
        # Affichage
        listeAffichage = []
        for filtre in self.ctrl_parametres.GetFiltres() :
            if filtre == "consommation" : listeAffichage.append("Consommations")
            if filtre == "cotisation" : listeAffichage.append("Cotisations")
            if filtre == "autre" : listeAffichage.append("Autres")
            if filtre == "avoir" : listeAffichage.append("Avoirs")
        affichage = ", ".join(listeAffichage)
        listeParametres.append(_(u"Eléments affichés : %s") % affichage)
        
        # Activités
        activites = self.ctrl_parametres.GetLabelActivites()
        listeParametres.append(_(u"Activités : %s") % activites)
                
        labelParametres = " | ".join(listeParametres)
        return labelParametres

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Listedesdductions")



# -------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
