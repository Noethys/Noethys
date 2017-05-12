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
from Ctrl import CTRL_Liste_factures
import GestionDB
from Utils import UTILS_Dates
import wx.lib.dialogs as dialogs



class Dialog(wx.Dialog):
    def __init__(self, parent, IDlot=None):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX)
        self.parent = parent
        self.IDlot = IDlot
        
        intro = _(u"Cochez les factures que vous souhaitez ajouter au lot de prélèvements puis cliquez sur le bouton 'Ok'.")
        titre = _(u"Ajouter des factures au prélèvement")
        self.SetTitle(titre)
        self.ctrl_bandeau = CTRL_Bandeau.Bandeau(self, titre=titre, texte=intro, hauteurHtml=30, nomImage="Images/32x32/Facture.png")
        
        filtres = [
            {"type" : "solde_actuel", "operateur" : "<", "montant" : 0.0},
            {"type" : "prelevement", "choix" : True},
            ]
        self.ctrl_factures = CTRL_Liste_factures.CTRL(self, filtres=filtres)
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_ok =CTRL_Bouton_image.CTRL(self, id=wx.ID_OK, texte=_(u"Ok"), cheminImage="Images/32x32/Valider.png")
        self.bouton_fermer = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        # Init contrôles
        self.ctrl_factures.MAJ() 

    def __set_properties(self):
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour obtenir de l'aide")))
        self.bouton_aide.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour valider")))
        self.bouton_fermer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour fermer")))
        self.SetMinSize((930, 700))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_base.Add(self.ctrl_bandeau, 0, wx.EXPAND, 0)

        grid_sizer_base.Add(self.ctrl_factures, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
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

    def OnBoutonAide(self, event): 
        from Utils import UTILS_Aide
        UTILS_Aide.Aide("Prlvementautomatique1")

    def GetFacturesPrelevees(self):
        """ Recherche si la facture est déjà présente dans un autre lot de prélèvement """
        DB = GestionDB.DB()
        req = """SELECT IDprelevement, prelevements.IDlot, IDfacture, statut, lots_prelevements.date, lots_prelevements.nom
        FROM prelevements
        LEFT JOIN lots_prelevements ON lots_prelevements.IDlot = prelevements.IDlot
        ;"""
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close()
        dictFacturesPrelevees = {}
        for IDprelevement, IDlot, IDfacture, statut, datePrelevement, nomPrelevement in listeDonnees :
            datePrelevement = UTILS_Dates.DateEngEnDateDD(datePrelevement)
            if dictFacturesPrelevees.has_key(IDfacture) == False :
                dictFacturesPrelevees[IDfacture] = []
            dictFacturesPrelevees[IDfacture].append({"IDprelevement":IDprelevement, "IDlot":IDlot, "statut":statut, "datePrelevement":datePrelevement, "nomPrelevement":nomPrelevement})
        return dictFacturesPrelevees

    def OnBoutonOk(self, event):
        # Validation des données
        tracks = self.ctrl_factures.GetTracksCoches()
        if len(tracks) == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à inclure dans votre lot de prélèvements !"), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        dictFacturesPrelevees = self.GetFacturesPrelevees() 
        
        listeErreursSoldes = []
        listeErreursRIB = []
        for track in tracks :
            
            # Vérifie que la facture est bien impayée
            if track.soldeActuel >= 0.0 :
                listeErreursSoldes.append(track)
            
            # Vérifie que la famille a une autorisation de prélèvement
            if track.prelevement not in (True, 1) :
                listeErreursRIB.append(track)
            
            # Recherche si la facture n'est pas déjà dans un autre prélèvement
            listeAutresLots = []
            if dictFacturesPrelevees.has_key(track.IDfacture) :
                for dictTemp in dictFacturesPrelevees[track.IDfacture] :
                    if dictTemp["IDlot"] != self.IDlot :
                        nomPrelevement = dictTemp["nomPrelevement"]
                        datePrelevement = UTILS_Dates.DateDDEnFr(dictTemp["datePrelevement"])
                        statut = dictTemp["statut"]
                        listeAutresLots.append(_(u"- %s (%s) avec le statut '%s'") % (nomPrelevement, datePrelevement, statut.capitalize()))
            
            if len(listeAutresLots) > 0 :
                message1 = _(u"La facture n°%s est déjà présente dans les autres lots de prélèvements suivants. Souhaitez-vous tout de même l'inclure de votre lot de prélèvements actuel ?") % track.numero
                message2 = "\n".join(listeAutresLots)
                dlg = dialogs.MultiMessageDialog(self, message1, caption=_(u"Avertissement"), msg2=message2, style = wx.ICON_QUESTION |wx.NO | wx.CANCEL | wx.YES | wx.YES_DEFAULT, icon=None, btnLabels={wx.ID_YES : _(u"Oui"), wx.ID_NO : _(u"Non"), wx.ID_CANCEL : _(u"Annuler")})
                reponse = dlg.ShowModal() 
                dlg.Destroy() 
                if reponse != wx.ID_YES :
                    return False
                    
        if len(listeErreursSoldes) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné %d factures qui ont déjà été payées !") % len(listeErreursSoldes), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if len(listeErreursRIB) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous avez sélectionné %d factures pour des familles qui n'ont pas d'autorisation de prélèvement !") % len(listeErreursRIB), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

            
        # Fermeture
        self.EndModal(wx.ID_OK)

    def GetTracks(self):
        return self.ctrl_factures.GetTracksCoches()
    
        

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
