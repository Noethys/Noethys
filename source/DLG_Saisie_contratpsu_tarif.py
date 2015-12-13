#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-15 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import CTRL_Saisie_date
import CTRL_Saisie_euros
import GestionDB



class CTRL_Montant(wx.TextCtrl):
    def __init__(self, parent, format=u"%.5f", defaut=0.0, style=wx.TE_RIGHT):
        wx.TextCtrl.__init__(self, parent, -1, "", style=style)
        self.SetValue(format % defaut)
        self.parent = parent
        self.format = format
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def OnKillFocus(self, event):
        valide, messageErreur = self.Validation()
        if valide == False :
            wx.MessageBox(messageErreur, "Erreur de saisie")
        else:
            montant = float(self.GetValue())
            self.SetValue(self.format % montant)
        if event != None : event.Skip()

    def Validation(self):
        # Vérifie si montant vide
        montantStr = self.GetValue()
        try :
            test = float(montantStr)
        except :
            message = _(u"Le montant que vous avez saisi n'est pas valide.")
            return False, message
        return True, None

    def SetMontant(self, montant=0.0):
        if montant == None : montant = 0.0
        self.SetValue(self.format % montant)

    def GetMontant(self):
        validation, erreur = self.Validation()
        if validation == True :
            montant = float(self.GetValue())
            return montant
        else:
            return None



class Dialog(wx.Dialog):
    def __init__(self, parent, dictContrat={}, track=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.dictContrat = dictContrat
        self.track = track

        if dictContrat.has_key("IDcontrat_tarif") :
            self.IDcontrat_tarif = dictContrat["IDcontrat_tarif"]
        else :
            self.IDcontrat_tarif = None

        # Période d'application
        self.staticbox_periode_staticbox = wx.StaticBox(self, -1, _(u"Date d'application"))
        self.label_date_debut = wx.StaticText(self, -1, _(u"A partir du :"))
        self.ctrl_date_debut = CTRL_Saisie_date.Date2(self)

        # Ressources
        self.staticbox_ressources_staticbox = wx.StaticBox(self, -1, _(u"Ressources"))
        self.label_revenu = wx.StaticText(self, -1, _(u"Revenu :"))
        self.ctrl_revenu = CTRL_Saisie_euros.CTRL(self)
        self.label_qf = wx.StaticText(self, -1, _(u"Quotient familial :"))
        self.ctrl_qf = wx.TextCtrl(self, -1, u"")

        # Tarifs
        self.staticbox_tarifs_staticbox = wx.StaticBox(self, -1, _(u"Tarifs"))
        self.label_suggere = wx.StaticText(self, -1, _(u"Suggéré"))
        self.label_retenu = wx.StaticText(self, -1, _(u"Retenu"))

        self.label_suggere.SetForegroundColour((180, 180, 180))
        self.label_retenu.SetForegroundColour((180, 180, 180))

        self.label_taux = wx.StaticText(self, -1, _(u"Taux d'effort :"))
        self.ctrl_taux_suggere = CTRL_Montant(self)
        self.ctrl_taux_retenu = CTRL_Montant(self)
        self.ctrl_taux_suggere.Enable(False)

        self.label_base = wx.StaticText(self, -1, _(u"Tarif de base :"))
        self.ctrl_base_suggere = CTRL_Montant(self)
        self.ctrl_base_retenu = CTRL_Montant(self)
        self.ctrl_base_suggere.Enable(False)

        self.label_depassement = wx.StaticText(self, -1, _(u"Tarif dépassement :"))
        self.ctrl_depassement_suggere = CTRL_Montant(self)
        self.ctrl_depassement_retenu = CTRL_Montant(self)
        self.ctrl_depassement_suggere.Enable(False)

        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok = CTRL_Bouton_image.CTRL(self, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(_(u"Saisie d'un tarif de contrat"))
        self.ctrl_date_debut.SetToolTipString(_(u"Saisissez la date de début d'application"))
        self.ctrl_revenu.SetToolTipString(_(u"Saisissez le revenu pris en compte"))
        self.ctrl_qf.SetToolTipString(_(u"Saisissez le quotient familial pris en compte"))
        self.ctrl_taux_suggere.SetToolTipString(_(u"Taux calculé automatiquement"))
        self.ctrl_taux_retenu.SetToolTipString(_(u"Saisissez le taux retenu"))
        self.ctrl_base_suggere.SetToolTipString(_(u"Tarif de base calculé automatiquement"))
        self.ctrl_base_retenu.SetToolTipString(_(u"Saisissez le tarif de base"))
        self.ctrl_depassement_suggere.SetToolTipString(_(u"Tarif de dépassement calculé automatiquement"))
        self.ctrl_depassement_retenu.SetToolTipString(_(u"Saisissez le tarif de dépassement"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_ok.SetToolTipString(_(u"Cliquez ici pour valider"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((420, 100))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        
        staticbox_periode = wx.StaticBoxSizer(self.staticbox_periode_staticbox, wx.VERTICAL)
        grid_sizer_periode = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
        grid_sizer_periode.Add(self.label_date_debut, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_periode.Add(self.ctrl_date_debut, 0, wx.EXPAND, 0)
        grid_sizer_periode.AddGrowableCol(1)
        staticbox_periode.Add(grid_sizer_periode, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_periode, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)

        staticbox_ressources = wx.StaticBoxSizer(self.staticbox_ressources_staticbox, wx.VERTICAL)
        grid_sizer_ressources = wx.FlexGridSizer(rows=1, cols=5, vgap=10, hgap=10)
        grid_sizer_ressources.Add(self.label_revenu, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ressources.Add(self.ctrl_revenu, 0, wx.EXPAND, 0)
        grid_sizer_ressources.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_ressources.Add(self.label_qf, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_ressources.Add(self.ctrl_qf, 0, wx.EXPAND, 0)
        staticbox_ressources.Add(grid_sizer_ressources, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_ressources, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        staticbox_tarifs = wx.StaticBoxSizer(self.staticbox_tarifs_staticbox, wx.VERTICAL)
        grid_sizer_tarifs = wx.FlexGridSizer(rows=4, cols=3, vgap=10, hgap=10)

        grid_sizer_tarifs.Add( (5, 5), 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.label_suggere, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.label_retenu, 0, wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_tarifs.Add(self.label_taux, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.ctrl_taux_suggere, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.ctrl_taux_retenu, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_tarifs.Add(self.label_base, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.ctrl_base_suggere, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.ctrl_base_retenu, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer_tarifs.Add(self.label_depassement, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.ctrl_depassement_suggere, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_tarifs.Add(self.ctrl_depassement_retenu, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 0)

        staticbox_tarifs.Add(grid_sizer_tarifs, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox_tarifs, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)

        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        
        grid_sizer_base.AddGrowableCol(0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen() 
        
    def OnBoutonAide(self, event):
        import UTILS_Aide
        UTILS_Aide.Aide("")

    def OnBoutonOk(self, event):
        if self.ctrl_date_debut.Validation() == False or self.ctrl_date_debut.GetDate() == None :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement saisir une date de début d'application valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_date_debut.SetFocus()
            return False

        # Revenu
        if self.ctrl_revenu.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement un montant de revenu valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_revenu.SetFocus()
            return False

        # Quotient familial
        if len(self.ctrl_qf.GetValue()) > 0 :
            try :
                quotient = int(self.ctrl_qf.GetValue())
            except :
                dlg = wx.MessageDialog(self, _(u"Le quotient familial que vous avez saisi ne semble pas valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.ctrl_qf.SetFocus()
                return False

        # Taux
        if self.ctrl_taux_retenu.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement un montant de revenu valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_taux_retenu.SetFocus()
            return False

        # tarif de base
        if self.ctrl_base_retenu.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement un montant de revenu valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_base_retenu.SetFocus()
            return False

        # tarif dépassement
        if self.ctrl_depassement_retenu.Validation() == False :
            dlg = wx.MessageDialog(self, _(u"Vous devez obligatoirement un montant de revenu valide !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_depassement_retenu.SetFocus()
            return False

        self.EndModal(wx.ID_OK)

    def GetDonnees(self):
        date_debut = self.ctrl_date_debut.GetDate()
        revenu = self.ctrl_revenu.GetMontant()
        try :
            quotient = int(self.ctrl_qf.GetValue())
        except :
            quotient = 0
        taux = self.ctrl_taux_retenu.GetMontant()
        tarif_base = self.ctrl_base_retenu.GetMontant()
        tarif_depassement = self.ctrl_depassement_retenu.GetMontant()

        dictDonnees = {
            "IDcontrat_tarif" : self.IDcontrat_tarif,
            "date_debut" : date_debut,
            "revenu" : revenu,
            "quotient" : quotient,
            "taux" : taux,
            "tarif_base" : tarif_base,
            "tarif_depassement" : tarif_depassement,
        }

        return dictDonnees

    def SetTrack(self, track=None):
        if track.date_debut != None :
            self.ctrl_date_debut.SetDate(track.date_debut)
        if track.revenu != None :
            self.ctrl_revenu.SetMontant(track.revenu)
        if track.quotient != None :
            self.ctrl_qf.SetValue(str(track.quotient))
        if track.taux != None :
            self.ctrl_taux_retenu.SetMontant(track.taux)
        if track.tarif_base != None :
            self.ctrl_base_retenu.SetMontant(track.tarif_base)
        if track.tarif_depassement != None :
            self.ctrl_depassement_retenu.SetMontant(track.tarif_depassement)


if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
