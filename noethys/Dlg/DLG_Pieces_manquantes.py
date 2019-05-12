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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import datetime

import GestionDB
from Ctrl import CTRL_Bandeau
from Ol import OL_Pieces_manquantes
from Ctrl import CTRL_Saisie_date
from Dlg import DLG_calendrier_simple
from Ctrl import CTRL_Selection_activites
from Utils import UTILS_Envoi_email


def DateEngFr(textDate):
    text = str(textDate[8:10]) + "/" + str(textDate[5:7]) + "/" + str(textDate[:4])
    return text


class Options(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_presents", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        self.check_concernes = wx.CheckBox(self, -1, _(u"Ne pas afficher les dossiers complets"))
        
        self.radio_inscrits = wx.RadioButton(self, -1, _(u"Tous les inscrits"), style=wx.RB_GROUP)
        self.radio_presents = wx.RadioButton(self, -1, _(u"Uniquement les présents"))
        self.label_date_debut = wx.StaticText(self, -1, u"Du")
        self.ctrl_date_debut = CTRL_Saisie_date.Date(self)
        self.bouton_date_debut = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        self.label_date_fin = wx.StaticText(self, -1, _(u"Au"))
        self.ctrl_date_fin = CTRL_Saisie_date.Date(self)
        self.bouton_date_fin = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_inscrits)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio, self.radio_presents)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateDebut, self.bouton_date_debut)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDateFin, self.bouton_date_fin)
        
        self.OnRadio(None)

    def __set_properties(self):
        self.ctrl_date_debut.SetToolTip(wx.ToolTip(_(u"Saisissez ici une date de début")))
        self.bouton_date_debut.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une date de début")))
        self.ctrl_date_fin.SetToolTip(wx.ToolTip(_(u"Saisissez ici une date de fin")))
        self.bouton_date_fin.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour saisir une date de fin")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=6, cols=1, vgap=5, hgap=5)
        
        grid_sizer_base.Add(self.check_concernes, 0, 0, 0)
        grid_sizer_base.Add( (5, 5), 0, 0, 0)
        
        grid_sizer_base.Add(self.radio_inscrits, 0, 0, 0)
        grid_sizer_base.Add(self.radio_presents, 0, 0, 0)
        
        grid_sizer_dates = wx.FlexGridSizer(rows=2, cols=3, vgap=5, hgap=5)
        grid_sizer_dates.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_debut, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.bouton_date_debut, 0, 0, 0)
        grid_sizer_dates.Add(self.label_date_fin, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.ctrl_date_fin, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_dates.Add(self.bouton_date_fin, 0, 0, 0)
        grid_sizer_base.Add(grid_sizer_dates, 1, wx.LEFT|wx.EXPAND, 18)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableCol(0)

    def OnRadio(self, event): 
        if self.radio_inscrits.GetValue() == True :
            etat = False
        else:
            etat = True
        self.label_date_debut.Enable(etat)
        self.label_date_fin.Enable(etat)
        self.ctrl_date_debut.Enable(etat)
        self.ctrl_date_fin.Enable(etat)
        self.bouton_date_debut.Enable(etat)
        self.bouton_date_fin.Enable(etat)

    def OnBoutonDateDebut(self, event): 
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_debut.SetDate(date)
        dlg.Destroy()

    def OnBoutonDateFin(self, event): 
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date_fin.SetDate(date)
        dlg.Destroy()
    
    def GetConcernes(self):
        if self.check_concernes.GetValue() == True :
            return True
        else:
            return False
    
    def GetPresents(self):
        if self.radio_inscrits.GetValue() == True :
            # Tous les inscrits
            return None
        else:
            # Uniquement les présents
            date_debut = self.ctrl_date_debut.GetDate()
            if self.ctrl_date_debut.FonctionValiderDate() == False or date_debut == None :
                dlg = wx.MessageDialog(self, _(u"La date de début ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_debut.SetFocus()
                return False
            
            date_fin = self.ctrl_date_fin.GetDate()
            if self.ctrl_date_fin.FonctionValiderDate() == False or date_fin == None :
                dlg = wx.MessageDialog(self, _(u"La date de fin ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
            
            if date_debut > date_fin :
                dlg = wx.MessageDialog(self, _(u"La date de début est supérieure à la date de fin !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_date_fin.SetFocus()
                return False
            
            return (date_debut, date_fin)

# -------------------------------------------------------------------------------------------------------------------------

class Parametres(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="panel_parametres", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Période
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Date de référence"))
        self.ctrl_date = CTRL_Saisie_date.Date(self)
        self.ctrl_date.SetDate(datetime.date.today())
        self.bouton_date = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Calendrier.png"), wx.BITMAP_TYPE_ANY))
        
        # Activités
        self.staticbox_activites_staticbox = wx.StaticBox(self, -1, _(u"Activités"))
        self.ctrl_activites = CTRL_Selection_activites.CTRL(self)
        self.ctrl_activites.SetMinSize((-1, 90))
        
        # Inscrits / Présents
        self.staticbox_presents_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.ctrl_options = Options(self)
        
        # Boutons afficher
        self.bouton_afficher = CTRL_Bouton_image.CTRL(self, texte=_(u"Rafraîchir la liste"), cheminImage="Images/32x32/Actualiser.png")
        self.bouton_afficher.SetMinSize((-1, 50)) 

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAfficher, self.bouton_afficher)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonDate, self.bouton_date)

    def __set_properties(self):
        self.bouton_afficher.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour afficher la liste en fonction des paramètres sélectionnés")))
        self.ctrl_date.SetToolTip(wx.ToolTip(_(u"Saisissez la date de référence")))
        self.bouton_date.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour sélectionner la date de référence dans un calendrier")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        # Date de référence
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=1, cols=7, vgap=5, hgap=5)
        grid_sizer_periode.Add((13, 10), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.bouton_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_periode, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Activités
        staticbox_activites = wx.StaticBoxSizer(self.staticbox_activites_staticbox, wx.VERTICAL)
        staticbox_activites.Add(self.ctrl_activites, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_activites, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Inscrits / Présents
        staticbox_presents = wx.StaticBoxSizer(self.staticbox_presents_staticbox, wx.VERTICAL)
        staticbox_presents.Add(self.ctrl_options, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_presents, 1, wx.RIGHT|wx.EXPAND, 5)
        
        # Bouton Afficher
        grid_sizer_base.Add(self.bouton_afficher, 1, wx.RIGHT|wx.EXPAND, 5)

        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def OnBoutonDate(self, event): 
        dlg = DLG_calendrier_simple.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK :
            date = dlg.GetDate()
            self.ctrl_date.SetDate(date)
        dlg.Destroy()
    
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
        listeActivites = self.ctrl_activites.GetActivites()
        if len(listeActivites) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune activité !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Uniquement les familles concernées
        concernes = self.ctrl_options.GetConcernes() 
        
        # Vérifie Inscrits / Présents
        presents = self.ctrl_options.GetPresents()
        if presents == False : return
        
        # Envoi des données
        self.parent.MAJ(date_reference=date_reference, listeActivites=listeActivites, presents=presents, concernes=concernes)
        
        return True
    


# --------------------------------------------------------------------------------------------------------------------------------------------------

class Dialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        intro = _(u"Vous pouvez ici consulter et imprimer la liste des pièces encore à fournir à la date de référence donnée pour la ou les activités sélectionnées. Commencez par saisir une date de référence puis sélectionnez un ou plusieurs groupes d'activités ou certaines activités en particulier avant de cliquer sur le bouton 'Rafraîchir la liste' pour afficher les résultats.")
        titre = _(u"Liste des pièces manquantes")
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Piece.png")
        
        self.ctrl_parametres = Parametres(self)
        self.ctrl_listview = OL_Pieces_manquantes.ListView(self, id=-1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_listview.SetMinSize((100, 100))
        self.ctrl_recherche = OL_Pieces_manquantes.CTRL_Outils(self, listview=self.ctrl_listview, afficherCocher=True)
        
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_imprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_email = CTRL_Bouton_image.CTRL(self, texte=_(u"Envoyer des rappels par Email"), cheminImage="Images/32x32/Emails_exp.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.Apercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.Imprimer, self.bouton_imprimer)
        self.Bind(wx.EVT_BUTTON, self.EnvoyerEmail, self.bouton_email)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.MAJ(None)
        

    def __set_properties(self):
        self.SetTitle(_(u"Liste des pièces manquantes"))
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu de la liste")))
        self.bouton_imprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour imprimer la liste")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_email.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour envoyer un email de rappel aux familles cochées")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((950, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        
        # Panel des paramètres
        grid_sizer_contenu.Add(self.ctrl_parametres, 1, wx.EXPAND, 0)
        
        # Liste + Barre de recherche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_listview, 0, wx.EXPAND, 0)
        grid_sizer_gauche.Add(self.ctrl_recherche, 0, wx.EXPAND, 0)
        grid_sizer_gauche.AddGrowableRow(0)
        grid_sizer_gauche.AddGrowableCol(0)
        grid_sizer_contenu.Add(grid_sizer_gauche, 1, wx.EXPAND, 0)
        
        # Commandes
        grid_sizer_droit = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_droit.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_droit.Add(self.bouton_imprimer, 0, 0, 0)
        grid_sizer_contenu.Add(grid_sizer_droit, 1, wx.EXPAND, 0)
        
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_email, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_fermer, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen()

    def Apercu(self, event):
        self.ctrl_listview.Apercu(None)
        
    def Imprimer(self, event):
        self.ctrl_listview.Imprimer(None)
    
    def MAJ(self, date_reference=None, listeActivites=None, presents=None, concernes=False):
        labelParametres = self.GetLabelParametres() 
        self.ctrl_listview.MAJ(date_reference, listeActivites, presents, concernes, labelParametres) 

    def GetLabelParametres(self):
        listeParametres = []
        
        # Dates
        date = self.ctrl_parametres.ctrl_date.GetDate()
        if date == None : date = "---"
        listeParametres.append(_(u"Situation au %s") % DateEngFr(str(date)))
                
        # Activités
        activites = ", ".join(self.ctrl_parametres.ctrl_activites.GetLabelActivites())
        if activites == "" : 
            activites = _(u"Aucune")
        listeParametres.append(_(u"Activités : %s") % activites)
        
        # Concernés
        if self.ctrl_parametres.ctrl_options.GetConcernes() == True :
            listeParametres.append(_(u"Uniquement les dossiers incomplets"))
        
        # Présents
        presents = self.ctrl_parametres.ctrl_options.GetPresents()
        if presents == None :
            listeParametres.append(_(u"Tous les inscrits"))
        else :
            listeParametres.append(_(u"Uniquement les présents du %s au %s") % (DateEngFr(str(presents[0])), DateEngFr(str(presents[1]))))
        
        labelParametres = " | ".join(listeParametres)
        return labelParametres

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Listedespicesmanquantes")

    def EnvoyerEmail(self, event):
        """ Envoi par Email de rappels de pièces manquantes """
        # Validation des données saisies
        tracks = self.ctrl_listview.GetTracksCoches()
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune famille dans la liste !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Récupération des adresses email
        dict_adresses = UTILS_Envoi_email.GetAdressesFamilles([track.IDfamille for track in tracks])
        if dict_adresses == False:
            return False

        liste_donnees = []
        for track in tracks:
            for adresse in dict_adresses.get(track.IDfamille, []):
                champs = {
                    "{NOM_FAMILLE}" : track.nomTitulaires,
                    "{LISTE_PIECES_MANQUANTES}" : track.pieces,
                }
                liste_donnees.append({"adresse" : adresse, "pieces" : [], "champs" : champs})

        # Transfert des données vers DLG Mailer
        from Dlg import DLG_Mailer
        dlg = DLG_Mailer.Dialog(self, categorie="rappel_pieces_manquantes")
        dlg.SetDonnees(liste_donnees, modificationAutorisee=False)
        dlg.ChargerModeleDefaut()
        dlg.ShowModal()
        dlg.Destroy()











if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
