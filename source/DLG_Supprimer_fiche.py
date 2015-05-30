#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import GestionDB
import UTILS_Historique

try: import psyco; psyco.full()
except: pass

ID_BOUTON_DETACHER = 1
ID_BOUTON_SUPPRIMER = 2
ID_SUPPRIMER_FAMILLE = 3


class Dialog(wx.Dialog):
    def __init__(self, parent, IDindividu=None, IDfamille=None):
        wx.Dialog.__init__(self, parent, -1, name="DLG_Supprimer_fiche", style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        
        self.staticbox_staticbox = wx.StaticBox(self, -1, u"")
        self.label_intro = wx.StaticText(self, -1, _(u"Souhaitez-vous détacher ou supprimer cette fiche ?"))
        
        self.bouton_detacher = wx.BitmapButton(self, ID_BOUTON_DETACHER, wx.Bitmap("Images/BoutonsImages/Detacher_fiche.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, ID_BOUTON_SUPPRIMER, wx.Bitmap("Images/BoutonsImages/Supprimer_fiche.png", wx.BITMAP_TYPE_ANY))
        
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonDetacher, self.bouton_detacher)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        
        self.bouton_annuler.SetFocus() 

    def __set_properties(self):
        self.SetTitle(_(u"Supprimer une fiche"))
        self.bouton_detacher.SetToolTipString(_(u"Cliquez ici pour détacher la fiche"))
        self.bouton_supprimer.SetToolTipString(_(u"Cliquez ici pour supprimer la fiche"))
        self.bouton_aide.SetToolTipString(_(u"Cliquez ici pour obtenir de l'aide"))
        self.bouton_annuler.SetToolTipString(_(u"Cliquez ici pour annuler"))
        self.SetMinSize((400, 240))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        staticbox = wx.StaticBoxSizer(self.staticbox_staticbox, wx.VERTICAL)
        grid_sizer_contenu = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_commandes = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.label_intro, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_commandes.Add(self.bouton_detacher, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.Add(self.bouton_supprimer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_commandes.AddGrowableRow(0)
        grid_sizer_commandes.AddGrowableCol(0)
        grid_sizer_commandes.AddGrowableCol(1)
        grid_sizer_contenu.Add(grid_sizer_commandes, 1, wx.EXPAND, 0)
        grid_sizer_contenu.AddGrowableRow(1)
        grid_sizer_contenu.AddGrowableCol(0)
        staticbox.Add(grid_sizer_contenu, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(staticbox, 1, wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND, 10)
        grid_sizer_boutons.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_boutons.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_boutons.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_boutons, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)
        self.Layout()
        self.CenterOnScreen() 

    def OnBoutonDetacher(self, event): 
        resultat = self.Detacher()
        if resultat == True : self.EndModal(ID_BOUTON_DETACHER)
        if resultat == False : self.EndModal(wx.ID_CANCEL)
        if resultat == "famille" : self.EndModal(ID_SUPPRIMER_FAMILLE)
    
    def Detacher(self):
        """ Processus de détachement d'une fiche individuelle """
        DB = GestionDB.DB()
    
        # Vérifie si des pièces n'existent pas
        req = """
        SELECT IDpiece, IDtype_piece
        FROM pieces
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car %d pièce(s) existent déjà pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False

        # Vérifie si des cotisations n'existent pas
        req = """
        SELECT IDcotisation, IDfamille
        FROM cotisations
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car %d cotisation(s) individuelle(s) existe(nt) déjà pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Vérifie si des inscriptions n'existent pas
        req = """
        SELECT IDinscription, IDactivite
        FROM inscriptions
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car cet individu est déjà inscrit à %d activité(s) sur cette fiche famille !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Vérifie si des consommations n'existent pas
        req = """
        SELECT IDconso, IDactivite
        FROM consommations
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE consommations.IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car %d consommation(s) ont déjà été enregistrée(s) pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False

        # Vérifie si des prestations n'existent pas
        req = """
        SELECT IDprestation, label
        FROM prestations
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car %d prestations(s) ont déjà été enregistrée(s) pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False

        # Vérifie si des messages n'existent pas
        req = """
        SELECT IDmessage, type
        FROM messages
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher cette fiche car %d message(s) ont déjà été enregistré(s) pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Compte le nbre d'individus présents dans la fiche
        req = """
        SELECT IDrattachement, IDindividu
        FROM rattachements
        WHERE IDindividu<>%d AND IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        nbreAutresIndividus = len(listeDonnees)
        
        # Vérifie qu'il ne s'agit pas du dernier titulaire
        req = """
        SELECT IDrattachement, IDindividu
        FROM rattachements
        WHERE IDcategorie=1 AND titulaire=1 AND IDindividu<>%d AND IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 :
            dernierTitulaire = True
        else:
            dernierTitulaire = False
        if dernierTitulaire == True :
            if nbreAutresIndividus > 0 :
            # S'il s'agit du dernier titulaire mais qu'il y a d'autres membres dans la fiche famille
                dlg = wx.MessageDialog(self, _(u"Il s'agit du dernier titulaire du dossier, vous ne pouvez donc pas le détacher !\n\n(Si vous souhaitez supprimer la fiche famille, commencez pas détacher ou supprimer tous les autres membres de cette fiche)"), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return False
            else:
                # S'il s'agit du dernier membre de la famille
                dlg = wx.MessageDialog(self, _(u"Il s'agit du dernier membre de cette famille.\n\nSouhaitez-vous détacher la fiche individuelle et supprimer la fiche famille ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas détacher le dernier membre d'une famille sans supprimer la fiche famille !"), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                
                # Vérifie qu'il est possible de supprimer la fiche famille
                req = """SELECT IDaide, nom FROM aides WHERE IDfamille=%d""" % self.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) >0 :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la fiche famille car il y a déjà %d aide(s) journalière(s) enregistrée(s) dans cette fiche.") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                
                req = """SELECT IDcotisation, IDfamille FROM cotisations WHERE IDfamille=%d""" % self.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) >0 :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la fiche famille car il y a déjà %d cotisation(s) enregistrée(s) dans cette fiche.") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                
                req = """SELECT IDreglement, date FROM reglements 
                LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
                WHERE IDfamille=%d""" % self.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) >0 :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la fiche famille car il y a déjà %d règlement(s) enregistré(s) dans cette fiche.") % len(listeDonnees), _(u"Détachement impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False

                # Détachement de la fiche individu
                req = "DELETE FROM rattachements WHERE IDfamille=%d AND IDindividu=%d;" % (self.IDfamille, self.IDindividu)
                DB.ExecuterReq(req)
                
                DB.Commit() 
                DB.Close()
                
                # Fermeture de la fiche famille
                return "famille"
                
        else :
            # Suppression du rattachement de l'individu
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de vouloir détacher cette fiche ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return False
            req = "DELETE FROM rattachements WHERE IDfamille=%d AND IDindividu=%d;" % (self.IDfamille, self.IDindividu)
            DB.ExecuterReq(req)
            DB.Commit() 
            DB.Close()
        
            # Mémorise l'action dans l'historique
            UTILS_Historique.InsertActions([{
                    "IDfamille" : self.IDfamille,
                    "IDindividu" : self.IDindividu,
                    "IDcategorie" : 14, 
                    "action" : _(u"Détachement de la fiche individuelle ID%d de la famille ID %d") % (self.IDindividu, self.IDfamille),
                    },])
                    
            return True


    def OnBoutonSupprimer(self, event): 
        resultat = self.Supprimer()
        if resultat == True : self.EndModal(ID_BOUTON_SUPPRIMER)
        if resultat == False : self.EndModal(wx.ID_CANCEL)
        if resultat == "famille" : self.EndModal(ID_SUPPRIMER_FAMILLE)


    def Supprimer(self):
        """ Processus de suppression d'une fiche individuelle """
        DB = GestionDB.DB()
        
        # Vérifie si cet individu n'est pas rattaché à une autre famille
        req = """
        SELECT IDrattachement, IDfamille
        FROM rattachements
        WHERE IDindividu=%d and IDfamille<>%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car elle est également rattachée à %d autre(s) famille(s).\n\nSi vous souhaitez vraiment la supprimer, veuillez la détacher de l'autre famille !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Vérifie si des pièces n'existent pas
        req = """
        SELECT IDpiece, IDtype_piece
        FROM pieces
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car %d pièce(s) existent déjà pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False

        # Vérifie si des cotisations n'existent pas
        req = """
        SELECT IDcotisation, IDfamille
        FROM cotisations
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car %d cotisation(s) individuelle(s) existe(nt) déjà pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Vérifie si des inscriptions n'existent pas
        req = """
        SELECT IDinscription, IDactivite
        FROM inscriptions
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car cet individu est déjà inscrit à %d activité(s) sur cette fiche famille !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Vérifie si des consommations n'existent pas
        req = """
        SELECT IDconso, IDactivite
        FROM consommations
        LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = consommations.IDcompte_payeur
        WHERE consommations.IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car %d consommation(s) ont déjà été enregistrée(s) pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False

        # Vérifie si des prestations n'existent pas
        req = """
        SELECT IDprestation, label
        FROM prestations
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car %d prestations(s) ont déjà été enregistrée(s) pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False

        # Vérifie si des messages n'existent pas
        req = """
        SELECT IDmessage, type
        FROM messages
        WHERE IDindividu=%d and IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) > 0 :
            dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer cette fiche car %d message(s) ont déjà été enregistré(s) pour cet individu sur cette fiche famille !") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            DB.Close()
            return False
        
        # Compte le nbre d'individus présents dans la fiche
        req = """
        SELECT IDrattachement, IDindividu
        FROM rattachements
        WHERE IDindividu<>%d AND IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        nbreAutresIndividus = len(listeDonnees)
        
        # Vérifie qu'il ne s'agit pas du dernier titulaire
        req = """
        SELECT IDrattachement, IDindividu
        FROM rattachements
        WHERE IDcategorie=1 AND titulaire=1 AND IDindividu<>%d AND IDfamille=%d
        """ % (self.IDindividu, self.IDfamille)
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        if len(listeDonnees) == 0 :
            dernierTitulaire = True
        else:
            dernierTitulaire = False
        if dernierTitulaire == True :
            if nbreAutresIndividus > 0 :
            # S'il s'agit du dernier titulaire mais qu'il y a d'autres membres dans la fiche famille
                dlg = wx.MessageDialog(self, _(u"Il s'agit du dernier titulaire du dossier, vous ne pouvez donc pas le supprimer !\n\n(Si vous souhaitez supprimer la fiche famille, commencez pas détacher ou supprimer tous les autres membres de cette fiche)"), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                DB.Close()
                return False
            else:
                # S'il s'agit du dernier membre de la famille
                dlg = wx.MessageDialog(self, _(u"Il s'agit du dernier membre de cette famille.\n\nSouhaitez-vous supprimer la fiche individuelle et la fiche famille ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_EXCLAMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse !=  wx.ID_YES :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer le dernier membre d'une famille sans supprimer la fiche famille !"), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                
                # Vérifie qu'il est possible de supprimer la fiche famille
                req = """SELECT IDaide, nom FROM aides WHERE IDfamille=%d""" % self.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) >0 :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la fiche famille car il y a déjà %d aide(s) journalière(s) enregistrée(s) dans cette fiche.") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                
                req = """SELECT IDcotisation, IDfamille FROM cotisations WHERE IDfamille=%d""" % self.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) >0 :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la fiche famille car il y a déjà %d cotisation(s) enregistrée(s) dans cette fiche.") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                
                req = """SELECT IDreglement, date FROM reglements 
                LEFT JOIN comptes_payeurs ON comptes_payeurs.IDcompte_payeur = reglements.IDcompte_payeur
                WHERE IDfamille=%d""" % self.IDfamille
                DB.ExecuterReq(req)
                listeDonnees = DB.ResultatReq()
                if len(listeDonnees) >0 :
                    dlg = wx.MessageDialog(self, _(u"Vous ne pouvez pas supprimer la fiche famille car il y a déjà %d règlement(s) enregistré(s) dans cette fiche.") % len(listeDonnees), _(u"Suppression impossible"), wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
                
                DB.Close()
                
                # Suppression de la fiche individu
                self.SupprimerIndividu() 
                
                # Fermeture de la fiche famille
                return "famille"
                
        else :
            # Suppression de la fiche individuelle
            dlg = wx.MessageDialog(self, _(u"Etes-vous sûr de vouloir supprimer cette fiche ?"), _(u"Confirmation"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse !=  wx.ID_YES :
                return False
            
            self.SupprimerIndividu() 
            return True
    
    def SupprimerIndividu(self):
        # Suppression de l'individu
        DB = GestionDB.DB()
        req = "DELETE FROM rattachements WHERE IDfamille=%d AND IDindividu=%d;" % (self.IDfamille, self.IDindividu)
        DB.ExecuterReq(req)
        req = "DELETE FROM liens WHERE IDfamille=%d AND IDindividu_sujet=%d;" % (self.IDfamille, self.IDindividu)
        DB.ExecuterReq(req)
        req = "DELETE FROM liens WHERE IDfamille=%d AND IDindividu_objet=%d;" % (self.IDfamille, self.IDindividu)
        DB.ExecuterReq(req)
        DB.ReqDEL("vaccins", "IDindividu", self.IDindividu)
        DB.ReqDEL("problemes_sante", "IDindividu", self.IDindividu)
        DB.ReqDEL("abonnements", "IDindividu", self.IDindividu)
        DB.ReqDEL("individus", "IDindividu", self.IDindividu)
        DB.ReqDEL("questionnaire_reponses", "IDindividu", self.IDindividu)
        DB.ReqDEL("inscriptions", "IDindividu", self.IDindividu)
        DB.ReqDEL("scolarite", "IDindividu", self.IDindividu)
        DB.ReqDEL("transports", "IDindividu", self.IDindividu)
        DB.ReqDEL("messages", "IDindividu", self.IDindividu)
        DB.Commit() 
        DB.Close()
        # Suppression de la photo 
        DB = GestionDB.DB(suffixe="PHOTOS")
        DB.ReqDEL("photos", "IDindividu", self.IDindividu)
        DB.Close()
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Compositiondelafamille")




if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    dialog_1 = Dialog(None, IDindividu=None)
    app.SetTopWindow(dialog_1)
    dialog_1.ShowModal()
    app.MainLoop()
