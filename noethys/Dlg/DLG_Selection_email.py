#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
from Ctrl import CTRL_Bandeau
import GestionDB
from Ctrl import CTRL_Saisie_mail


class CTRL_Membre(wx.ListBox):
    def __init__(self, parent, IDfamille=None):
        wx.ListBox.__init__(self, parent, -1) 
        self.parent = parent
        self.IDfamille = IDfamille
        self.MAJ() 
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        if self.IDfamille == None :
            return []
        
        DB = GestionDB.DB()
        req = """SELECT 
        rattachements.IDindividu, IDcategorie,
        individus.nom, individus.prenom, individus.mail, individus.travail_mail
        FROM rattachements 
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDcategorie IN (1, 2) AND IDfamille=%d
        ;""" % self.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeAdresses = []
        for IDindividu, IDcategorie, nom, prenom, mailPerso, mailTravail in listeDonnees :
            if mailPerso != None and mailPerso != "" :
                listeAdresses.append((_(u"%s (Adresse perso de %s)") % (mailPerso, prenom), mailPerso, IDindividu, "perso"))
            if mailTravail != None and mailTravail != "" :
                listeAdresses.append((_(u"%s (Adresse pro de %s)") % (mailTravail, prenom), mailTravail, IDindividu, "travail"))

        # Remplissage du contrôle
        listeItems = []
        self.dictDonnees = {}
        index = 0
        for label, adresse, IDindividu, categorie in listeAdresses :
            self.dictDonnees[index] = {"adresse" : adresse, "IDindividu" : IDindividu, "categorie" : categorie}
            listeItems.append(label)
            index += 1
        return listeItems

    def SetAdresse(self, IDindividu=None, categorie=None):
        for index, values in self.dictDonnees.iteritems():
            if values["IDindividu"] == IDindividu and values["categorie"] == categorie :
                 self.SetSelection(index)

    def GetAdresse(self):
        index = self.GetSelection()
        if index == -1 : return (None, None)
        return (self.dictDonnees[index]["IDindividu"], self.dictDonnees[index]["categorie"])
            

# -----------------------------------------------------------------------------------------------------------------------


class Dialog(wx.Dialog):
    def __init__(self, parent, IDfamille=None, champ="email_factures", intro=u"", titre=u""):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.IDfamille = IDfamille
        self.champ = champ
                
        # Bandeau
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Emails_exp.png")
        
        # Activation
        self.box_activation_staticbox = wx.StaticBox(self, -1, _(u"Activation"))
        self.label_activation = wx.StaticText(self, -1, _(u"Envoi par Email activé :"))
        self.radio_activation_oui = wx.RadioButton(self, -1, _(u"Oui"), style=wx.RB_GROUP)
        self.radio_activation_non = wx.RadioButton(self, -1, _(u"Non"))
                
        # Adresse
        self.box_adresse_staticbox = wx.StaticBox(self, -1, _(u"Adresse Email"))
        self.radio_membre = wx.RadioButton(self, -1, _(u"L'adresse du membre :"), style=wx.RB_GROUP)
        self.ctrl_membre = CTRL_Membre(self, IDfamille=IDfamille)
        self.ctrl_membre.SetMinSize((380, 100))
        self.radio_autre = wx.RadioButton(self, -1, _(u"L'adresse suivante :"))
        self.ctrl_autre = CTRL_Saisie_mail.Mail(self)
        
        # Boutons
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        # Binds
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAdresse, self.radio_membre)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioAdresse, self.radio_autre)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init contrôles
        self.radio_activation_non.SetValue(True) 
        self.Importation() 
        self.OnRadioAdresse(None)

    def __set_properties(self):
        self.radio_activation_oui.SetToolTipString(_(u"Cliquez ici pour activer l'envoi par Email"))
        self.radio_activation_non.SetToolTipString(_(u"Cliquez ici pour désactiver l'envoi par Email"))
        self.radio_membre.SetToolTipString(_(u"Cliquez ici pour sélectionner l'adresse Email d'un membre de la famille"))
        self.ctrl_membre.SetToolTipString(_(u"Sélectionnez ici l'adresse Email d'un membre de la famille"))
        self.radio_autre.SetToolTipString(_(u"Cliquez ici pour saisir manuellement une adresse Email"))
        self.ctrl_autre.SetToolTipString(_(u"Saisissez une adresse Email"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=5, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        # Activation
        box_activation = wx.StaticBoxSizer(self.box_activation_staticbox, wx.VERTICAL)
        grid_sizer_activation = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_activation.Add(self.label_activation, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_activation.Add(self.radio_activation_oui, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_activation.Add(self.radio_activation_non, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_activation.Add(grid_sizer_activation, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_activation, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
                
        # Adresse
        box_adresse = wx.StaticBoxSizer(self.box_adresse_staticbox, wx.VERTICAL)
        grid_sizer_adresse = wx.FlexGridSizer(rows=4, cols=1, vgap=5, hgap=5)

        grid_sizer_adresse.Add(self.radio_membre, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_adresse.Add(self.ctrl_membre, 0, wx.EXPAND|wx.LEFT, 16)
        grid_sizer_adresse.Add(self.radio_autre, 0, wx.TOP, 10)
        grid_sizer_adresse.Add(self.ctrl_autre, 0, wx.EXPAND|wx.LEFT, 16)
        grid_sizer_adresse.AddGrowableCol(0)
        box_adresse.Add(grid_sizer_adresse, 1, wx.ALL|wx.EXPAND, 10)
        
        grid_sizer_base.Add(box_adresse, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnRadioAdresse(self, event):
        etat = self.radio_membre.GetValue()
        self.ctrl_membre.Enable(etat)
        self.ctrl_autre.Enable(not etat)

    def OnBoutonAide(self, event):
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Factures1")

    def OnBoutonAnnuler(self, event):
        self.EndModal(wx.ID_CANCEL)

    def Importation(self):
        """ Importation des données """
        if self.IDfamille == None :
            return
        
        DB = GestionDB.DB()
        req = """SELECT IDfamille, %s
        FROM familles 
        WHERE IDfamille=%d;""" % (self.champ, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        if len(listeDonnees) == 0 : return
        temp, envoi_factures = listeDonnees[0]

        # Activation
        if envoi_factures != None :
            self.radio_activation_oui.SetValue(True)
            temp = envoi_factures.split(";")
            IDindividu = temp[0]
            categorie = temp[1]
            adresse = temp[2]
            
            if IDindividu != "" :
                self.radio_membre.SetValue(True)
                self.ctrl_membre.SetAdresse(int(IDindividu), categorie)
            else :
                self.radio_autre.SetValue(True)
                self.ctrl_autre.SetValue(adresse)


    def OnBoutonOk(self, event):
        # Récupération des données
        IDindividu, categorie, adresse = "", "", ""
        activation = self.radio_activation_oui.GetValue()
        if activation == True :
            
            # Activation
            if self.radio_membre.GetValue() == True :
                IDindividu, categorie = self.ctrl_membre.GetAdresse()
                adresse = ""
                
                if IDindividu == None :
                    dlg = wx.MessageDialog(self, _(u"Activation impossible !\n\nVous devez sélectionner un membre."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_autre.SetFocus()
                    return

            else :
                IDindividu, categorie = "", ""
                adresse = self.ctrl_autre.GetValue()

                if ";" in adresse :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas utiliser de point-virgule (;) dans l'adresse !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_autre.SetFocus()
                    return

                if adresse == "" :
                    dlg = wx.MessageDialog(self, _(u"Activation impossible !\n\nVous devez saisir une adresse Email."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_autre.SetFocus()
                    return

                valide, messageErreur = self.ctrl_autre.Validation()
                if valide == False :
                    dlg = wx.MessageDialog(self, _(u"Activation impossible !\n\nL'adresse email saisie n'est pas valide."), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                    dlg.ShowModal()
                    dlg.Destroy()
                    self.ctrl_autre.SetFocus()
                    return False
        
        else :
            # Pas d'activation
            dlg = wx.MessageDialog(None, _(u"Vous confirmez que vous ne souhaitez pas activer cette fonctionnalité ?"), _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal() 
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return

        valeur = u"%s;%s;%s" % (str(IDindividu), categorie, adresse)
        if valeur == ";;" : 
            valeur = None
            
        # Sauvegarde
        DB = GestionDB.DB()
        DB.ReqMAJ("familles", [(self.champ, valeur),], "IDfamille", self.IDfamille)
        DB.Close()

        # Fermeture
        self.EndModal(wx.ID_OK)




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDfamille=14)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
