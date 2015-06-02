#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import datetime
import traceback
import sys
import wx.lib.agw.hyperlink as Hyperlink
import wx.lib.agw.pybusyinfo as PBI

import CTRL_Rappels_generation_selection
import UTILS_Identification
import OL_Textes_rappels
import UTILS_Rappels

import GestionDB


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.URL = URL
        self.AutoBrowse(False)
        self.SetColours("BLUE", "BLUE", "BLUE")
        self.SetUnderlines(False, False, True)
        self.SetBold(False)
        self.EnableRollover(True)
        self.SetToolTip(wx.ToolTip(infobulle))
        self.UpdateLink()
        self.DoPopup(False)
        self.Bind(Hyperlink.EVT_HYPERLINK_LEFT, self.OnLeftLink)
    
    def OnLeftLink(self, event):
        if self.URL == "tout" :
            self.parent.ctrl_rappels.CocheTout()
        if self.URL == "rien" :
            self.parent.ctrl_rappels.DecocheTout()
        self.UpdateLink()
        
# ---------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Rappels_generation_selection", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        
        # Textes
        self.box_textes_staticbox = wx.StaticBox(self, -1, _(u"Textes de rappels"))
        
        self.ctrl_textes = OL_Textes_rappels.ListView(self, id=-1, name="OL_textes_rappels", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_textes.SetMinSize((-1, 90))
        self.ctrl_textes.MAJ() 

        self.bouton_ajouter_texte = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Ajouter.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier_texte = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Modifier.png", wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer_texte = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/16x16/Supprimer.png", wx.BITMAP_TYPE_ANY))

        # Rappels disponibles
        self.box_rappels_staticbox = wx.StaticBox(self, -1, _(u"Lettres de rappel"))
        self.ctrl_rappels = CTRL_Rappels_generation_selection.CTRL(self)
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        
        self.hyper_select_tout = Hyperlien(self, label=_(u"Tout cocher"), infobulle=_(u"Cliquez ici pour tout cocher"), URL="tout")
        self.label_separation = wx.StaticText(self, -1, "|")
        self.hyper_selection_rien = Hyperlien(self, label=_(u"Tout décocher"), infobulle=_(u"Cliquez ici pour tout décocher"), URL="rien")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.OnAjouterTexte, self.bouton_ajouter_texte)
        self.Bind(wx.EVT_BUTTON, self.OnModifierTexte, self.bouton_modifier_texte)
        self.Bind(wx.EVT_BUTTON, self.OnSupprimerTexte, self.bouton_supprimer_texte)

    def __set_properties(self):
        self.bouton_apercu.SetToolTipString(_(u"Cliquez ici pour créer un aperçu PDF de la lettre de rappel sélectionnée"))
        self.bouton_ajouter_texte.SetToolTipString(_(u"Cliquez ici pour ajouter un texte de rappel"))
        self.bouton_modifier_texte.SetToolTipString(_(u"Cliquez ici pour modifier le texte sélectionné dans la liste"))
        self.bouton_supprimer_texte.SetToolTipString(_(u"Cliquez ici pour supprimer le texte sélectionné dans la liste"))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        
        box_textes = wx.StaticBoxSizer(self.box_textes_staticbox, wx.VERTICAL)
        grid_sizer_textes = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_textes.Add(self.ctrl_textes, 1, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_ajouter_texte, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_modifier_texte, 0, 0, 0)
        grid_sizer_boutons.Add(self.bouton_supprimer_texte, 0, 0, 0)

        grid_sizer_textes.AddGrowableRow(0)
        grid_sizer_textes.AddGrowableCol(0)

        grid_sizer_textes.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        
        box_textes.Add(grid_sizer_textes, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_textes, 1, wx.EXPAND, 0)
        
        box_rappels = wx.StaticBoxSizer(self.box_rappels_staticbox, wx.VERTICAL)
        grid_sizer_rappels = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_rappels.Add(self.ctrl_rappels, 1, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_rappels.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_options.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.hyper_select_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_selection_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_rappels.Add(grid_sizer_options, 1, wx.EXPAND, 0)

        grid_sizer_rappels.AddGrowableRow(0)
        grid_sizer_rappels.AddGrowableCol(0)

        box_rappels.Add(grid_sizer_rappels, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_rappels, 1, wx.EXPAND, 0)
        
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)

    def OnAjouterTexte(self, event):
        self.ctrl_textes.Ajouter(None) 

    def OnModifierTexte(self, event):
        self.ctrl_textes.Modifier(None) 

    def OnSupprimerTexte(self, event):
        self.ctrl_textes.Supprimer(None) 

    def OnBoutonApercu(self, event):
        self.ctrl_rappels.AfficherApercu()

    def MAJ(self):
        self.ctrl_rappels.SetParametres(self.parent.dictParametres)
        
    def Validation(self):
        # Validation de la saisie
        nbreCoches = len(self.ctrl_rappels.GetCoches())
        if nbreCoches == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune lettre de rappel à générer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Demande de confirmation
        if nbreCoches == 1 :
            texte = _(u"Confirmez-vous la génération de 1 lettre de rappel ?")
        else :
            texte = _(u"Confirmez-vous la génération de %d rappels ?") % nbreCoches
        dlg = wx.MessageDialog(self, texte, _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Génération des rappels
        listeRappelsGenerees = self.SauvegardeRappels() 
        if listeRappelsGenerees == False :
            return False
        
        # Envoi des rappels générées
        self.parent.listeRappelsGenerees = listeRappelsGenerees
        
        return True

    def EcritStatusbar(self, texte=u""):
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass

    def SauvegardeRappels(self):
        """ Sauvegarde des rappels """
        dlgAttente = PBI.PyBusyInfo(_(u"Génération des rappels en cours..."), parent=None, title=_(u"Veuillez patienter..."), icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 

        # Recherche numéro de facture suivant
        DB = GestionDB.DB()
        req = """SELECT MAX(numero) FROM rappels;""" 
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()  
        DB.Close() 
        if listeDonnees[0][0] == None :
            numero = 1
        else:
            numero = listeDonnees[0][0] + 1
        
        # Récupère Utilisateur en cours
        IDutilisateur = UTILS_Identification.GetIDutilisateur()
        
        # Génération des rappels
        listeRappelsGenerees = []

        # Fusion des mots-clés
        facturation = UTILS_Rappels.Facturation()

        # Tri par ordre alphabétique de la liste
        listeComptes = []
        listeAnomalies = []
        dictCoches = self.ctrl_rappels.GetCoches()
        for IDcompte_payeur, dictCompte in self.ctrl_rappels.dictComptes.iteritems() :
            if dictCompte["select"] == True and dictCoches.has_key(IDcompte_payeur) :
                # Insertion du document dans le dictCompte
                dictDocument = self.ctrl_rappels.GetDictDocument(IDcompte_payeur)
                if dictDocument["IDtexte"] == 0 :
                    listeAnomalies.append(IDcompte_payeur)
                else :
                    dictCompte["IDtexte"] = dictDocument["IDtexte"]
                    dictCompte["titre"] = dictDocument["titre"]
                    dictCompte["texte"] = facturation.Fusion(dictCompte["IDtexte"] , dictCompte)
                listeComptes.append((dictCompte["nomSansCivilite"], IDcompte_payeur, dictCompte))
        listeComptes.sort()
        
        # Il reste des textes non attribués :
        if len(listeAnomalies) > 0  :
            del dlgAttente
            dlg = wx.MessageDialog(self, _(u"Il reste %d lettre(s) pour lesquelles vous n'avez pas attribué de texte !") % len(listeAnomalies), _(u"Erreur de saisie"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        # Sauvegarde
        DB = GestionDB.DB()
        try :
            
            index = 0
            for nomTitulaires, IDcompte_payeur, dictCompte in listeComptes :

                self.EcritStatusbar(_(u"Génération de la lettre de rappel %d sur %d...") % (index+1, len(listeComptes)))
                
                # Liste des activités
                texteActivites = ""
                for IDactivite in self.parent.dictParametres["listeActivites"] :
                    texteActivites += "%d;" % IDactivite
                if len(texteActivites) > 0 :
                    texteActivites = texteActivites[:-1]
                
                # Sauvegarde de la facture
                listeDonnees = [ 
                    ("numero", numero ), 
                    ("IDcompte_payeur", IDcompte_payeur ), 
                    ("date_edition", str(datetime.date.today()) ), 
                    ("date_reference", self.parent.dictParametres["date_reference"] ), 
                    ("IDtexte", dictCompte["IDtexte"] ), 
                    ("activites", texteActivites ), 
                    ("date_min", str(dictCompte["date_min"]) ), 
                    ("date_max", str(dictCompte["date_max"]) ), 
                    ("solde", float(dictCompte["solde_num"]) ), 
                    ("IDlot", self.parent.dictParametres["IDlot"] ), 
                    ("prestations", ";".join(self.parent.dictParametres["prestations"]) ),
                    ]
                IDrappel = DB.ReqInsert("rappels", listeDonnees)
                
                listeRappelsGenerees.append(IDrappel) 
                numero += 1
                index += 1

            DB.Close() 
            self.EcritStatusbar(u"")
            del dlgAttente

        except Exception, err:
            DB.Close() 
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.EcritStatusbar(u"")
            return False
        
        self.EcritStatusbar(u"")
        return listeRappelsGenerees







class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)

        panel.dictParametres = {
            "date_reference" : datetime.date(2013, 1, 1),
            "IDlot" : None,
            "date_edition" : datetime.date.today(),
            "prestations" : ["consommation", "cotisation", "autre"],
            "IDcompte_payeur" : None,
            "listeActivites" : [1, 2, 3],
            "listeExceptionsComptes" : [],
            }

        self.ctrl = Panel(panel)
        self.ctrl.MAJ()
        self.boutonTest = wx.Button(panel, -1, _(u"Bouton de test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        self.ctrl.SauvegardeRappels()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()



