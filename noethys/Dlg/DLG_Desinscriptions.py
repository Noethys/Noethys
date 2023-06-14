#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:          Ivan LUCAS
# Copyright:       (c) 2010-18 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import Chemins
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx, datetime
import GestionDB
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
from Ctrl import CTRL_Liste_inscriptions
from Ctrl import CTRL_Saisie_date


class Dialog(wx.Dialog):
    def __init__(self, parent, filtres=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        
        # Bandeau
        intro = _(u"Cette fonctionnalité permet de saisir une date de désinscription pour un ensemble d'inscriptions. Cochez les inscriptions souhaitées puis cliquez sur le bouton 'Valider' pour commencer la procédure.")
        titre = _(u"Désinscrire des individus")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Activite.png")
        
        # Factures
        self.box_inscriptions_staticbox = wx.StaticBox(self, -1, _(u"Liste des inscriptions"))
        self.ctrl_liste_inscriptions = CTRL_Liste_inscriptions.CTRL(self, filtres=filtres, nomListe="OL_Desinscriptions")
        
        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.label_date = wx.StaticText(self, -1, "Date de désinscription souhaitée :")
        self.ctrl_date = CTRL_Saisie_date.Date2(self)
        self.ctrl_date.SetDate(datetime.date.today())

        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Valider"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Fermer"), cheminImage="Images/32x32/Fermer.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CLOSE, self.OnBoutonAnnuler)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonValider, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contrôles
        self.ctrl_liste_inscriptions.partis = True
        self.ctrl_liste_inscriptions.ctrl_inscriptions.SetChampsAffiches(listeCodes=["nomComplet", "nomActivite", "dateInscription", "date_desinscription", "totalSolde", "nomTitulaires"])
        self.ctrl_liste_inscriptions.MAJ()

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_ok.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour lancer la procédure")))
        self.bouton_annuler.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour annuler")))
        self.SetMinSize((850, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)
                
        # Factures
        box_inscriptions = wx.StaticBoxSizer(self.box_inscriptions_staticbox, wx.VERTICAL)
        box_inscriptions.Add(self.ctrl_liste_inscriptions, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_inscriptions, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_options.Add(self.label_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_date, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_options.Add(grid_sizer_options, 1, wx.EXPAND|wx.ALL, 10)
        grid_sizer_base.Add(box_options, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonValider(self, event):
        """ Désinscription par lot """
        # Validation des données saisies
        tracks = self.ctrl_liste_inscriptions.GetTracksCoches()
        if len(tracks) == 0 : 
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune inscription !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Récupération des options
        date_desinscription = self.ctrl_date.GetDate()
        if not date_desinscription:
            dlg = wx.MessageDialog(self, _(u"Vous n'avez pas saisi de date de désinscription. Souhaitez-vous quand même continuer ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            if dlg.ShowModal() != wx.ID_YES :
                dlg.Destroy()
                return
            dlg.Destroy()

        liste_inscriptions = [track.IDinscription for track in tracks]

        # Condition
        if len(liste_inscriptions) == 0: condition_inscriptions = "inscriptions.IDinscription IN ()"
        elif len(liste_inscriptions) == 1: condition_inscriptions = "inscriptions.IDinscription IN (%d)" % liste_inscriptions[0]
        else: condition_inscriptions = "inscriptions.IDinscription IN %s" % str(tuple(liste_inscriptions))

        # Vérifie que des consommations n'existent pas après la date de désinscription souhaitée
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, individus.nom, individus.prenom, activites.nom
        FROM consommations
        LEFT JOIN inscriptions ON inscriptions.IDinscription = consommations.IDinscription
        LEFT JOIN individus ON individus.IDindividu = consommations.IDindividu
        LEFT JOIN activites ON activites.IDactivite = consommations.IDactivite
        WHERE consommations.date>='%s' AND %s
        ;"""  % (date_desinscription, condition_inscriptions)
        DB.ExecuterReq(req)
        liste_consommations = DB.ResultatReq()
        DB.Close()

        dict_anomalies = {}
        for IDindividu, nom, prenom, nom_activite in liste_consommations:
            dict_anomalies[(IDindividu, nom, prenom, nom_activite)] = True
        if dict_anomalies:
            txt_anomalies = ", ".join(["%s %s (%s)" % (temp[1], temp[2],temp[3]) for temp in dict_anomalies.keys()])
            dlg = wx.MessageDialog(self, _(u"Il est impossible de désinscrire les individus suivants car des consommations existent après la date de déinscription souhaitée : %s." % txt_anomalies), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        # Demande de confirmation
        dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment appliquer la date de désinscription aux inscriptions sélectionnées ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
        if dlg.ShowModal() != wx.ID_YES :
            dlg.Destroy()
            return
        dlg.Destroy()

        DB = GestionDB.DB()
        if date_desinscription:
            DB.ExecuterReq("UPDATE inscriptions SET date_desinscription='%s' WHERE %s;" % (date_desinscription, condition_inscriptions))
        else:
            DB.ExecuterReq("UPDATE inscriptions SET date_desinscription=NULL WHERE %s;" % condition_inscriptions)
        DB.Commit()
        DB.Close()

        self.ctrl_liste_inscriptions.MAJ()



if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dlg = Dialog(None)
    app.SetTopWindow(dlg)
    dlg.ShowModal()
    app.MainLoop()
