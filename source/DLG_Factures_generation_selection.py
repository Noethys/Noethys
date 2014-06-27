#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-13 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

import wx
import sys
import datetime
import traceback
import wx.lib.agw.hyperlink as Hyperlink
import wx.lib.agw.pybusyinfo as PBI

import CTRL_Factures_generation_selection
import UTILS_Identification
import UTILS_Texte

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
            self.parent.ctrl_factures.CocheTout()
        if self.URL == "rien" :
            self.parent.ctrl_factures.DecocheTout()
        self.UpdateLink()
        
        
# ---------------------------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Factures_generation_selection", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        self.box_factures_staticbox = wx.StaticBox(self, -1, u"Factures")
        self.ctrl_factures = CTRL_Factures_generation_selection.CTRL(self)
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Apercu.png", wx.BITMAP_TYPE_ANY))
        
        self.hyper_select_tout = Hyperlien(self, label=u"Tout cocher", infobulle=u"Cliquez ici pour tout cocher", URL="tout")
        self.label_separation = wx.StaticText(self, -1, "|")
        self.hyper_selection_rien = Hyperlien(self, label=u"Tout décocher", infobulle=u"Cliquez ici pour tout décocher", URL="rien")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)

    def __set_properties(self):
        self.bouton_apercu.SetToolTipString(u"Cliquez ici pour créer un aperçu PDF de la facture sélectionnée")

    def __do_layout(self):
        box_factures = wx.StaticBoxSizer(self.box_factures_staticbox, wx.VERTICAL)
        grid_sizer_factures = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_options = wx.FlexGridSizer(rows=1, cols=6, vgap=5, hgap=5)
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_factures.Add(self.ctrl_factures, 1, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_factures.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_options.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_options.Add(self.hyper_select_tout, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.label_separation, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.hyper_selection_rien, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.AddGrowableCol(0)
        grid_sizer_factures.Add(grid_sizer_options, 1, wx.EXPAND, 0)
        grid_sizer_factures.AddGrowableRow(0)
        grid_sizer_factures.AddGrowableCol(0)
        box_factures.Add(grid_sizer_factures, 1, wx.ALL|wx.EXPAND, 10)
        self.SetSizer(box_factures)
        box_factures.Fit(self)

    def OnBoutonApercu(self, event):
        self.ctrl_factures.AfficherApercu()

    def MAJ(self):
        self.ctrl_factures.SetParametres(self.parent.dictParametres)
        
    def Validation(self):
        # Validation de la saisie
        nbreCoches = len(self.ctrl_factures.GetCoches())
        if nbreCoches == 0 :
            dlg = wx.MessageDialog(self, u"Vous n'avez sélectionné aucune facture à générer !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Demande de confirmation
        if nbreCoches == 1 :
            texte = u"Confirmez-vous la génération de 1 facture ?"
        else :
            texte = u"Confirmez-vous la génération de %d factures ?" % nbreCoches
        dlg = wx.MessageDialog(self, texte, u"Confirmation", wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False

        # Génération des factures
        listeFacturesGenerees = self.SauvegardeFactures() 
        if listeFacturesGenerees == False :
            return False
        
        # Envoi des factures générées
        self.parent.listeFacturesGenerees = listeFacturesGenerees
        
        return True

    def EcritStatusbar(self, texte=u""):
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass

    def SauvegardeFactures(self):
        """ Sauvegarde des factures """
        dlgAttente = PBI.PyBusyInfo(u"Génération des factures en cours...", parent=None, title=u"Veuillez patienter...", icon=wx.Bitmap("Images/16x16/Logo.png", wx.BITMAP_TYPE_ANY))
        wx.Yield() 
        
        # Récupère Utilisateur en cours
        IDutilisateur = UTILS_Identification.GetIDutilisateur()
        
        # Génération des factures
        listeFacturesGenerees = []
        
        # Tri par ordre alphabétique de la liste
        listeComptes = []
        dictCoches = self.ctrl_factures.GetCoches()
        for IDcompte_payeur, dictCompte in self.ctrl_factures.dictComptes.iteritems() :
            if dictCompte["select"] == True and dictCoches.has_key(IDcompte_payeur) :
                listeComptes.append((dictCompte["nomSansCivilite"], IDcompte_payeur))
        listeComptes.sort()
        
        # Sélection du prochain numéro de facture
        numero = self.parent.dictParametres["prochain_numero"]
        
        # Sauvegarde
        DB = GestionDB.DB()
        try :
            
            index = 0
            for nomTitulaires, IDcompte_payeur in listeComptes :
                dictCompte = self.ctrl_factures.dictComptes[IDcompte_payeur]
                self.EcritStatusbar(u"Génération de la facture %d sur %d..." % (index+1, len(listeComptes)))
                
                listePrestations = dictCompte["listePrestations"] 
                total = dictCompte["total"] 
                regle = dictCompte["ventilation"] 
                solde = total - regle
                # Date échéance
                date_echeance = dictCompte["date_echeance"] 
                # Liste des activités
                texteActivites = ""
                for IDactivite in dictCompte["liste_activites"] :
                    texteActivites += "%d;" % IDactivite
                if len(dictCompte["liste_activites"]) > 0 :
                    texteActivites = texteActivites[:-1]
                # Liste des individus
                texteIndividus = ""
                for IDindividu in dictCompte["individus"].keys() :
                    texteIndividus += "%d;" % IDindividu
                if len(dictCompte["individus"].keys()) > 0 :
                    texteIndividus = texteIndividus[:-1]

                # Sauvegarde de la facture
                listeDonnees = [ 
                    ("numero", numero ), 
                    ("IDcompte_payeur", IDcompte_payeur ), 
                    ("date_edition", str(datetime.date.today()) ), 
                    ("date_echeance", date_echeance ), 
                    ("activites", texteActivites ), 
                    ("individus", texteIndividus ), 
                    ("IDutilisateur", IDutilisateur ), 
                    ("date_debut", str(dictCompte["date_debut"]) ), 
                    ("date_fin", str(dictCompte["date_fin"]) ), 
                    ("total", float(total) ), 
                    ("regle", float(regle) ), 
                    ("solde", float(solde) ), 
                    ("IDlot", self.parent.dictParametres["IDlot"] ), 
                    ("prestations", ";".join(self.parent.dictParametres["prestations"]) ),
                    ]
                IDfacture = DB.ReqInsert("factures", listeDonnees)
                                    
                # Attribution des IDfacture à chaque prestation
                for IDindividu, IDprestation in listePrestations :
                    if dictCompte["individus"][IDindividu]["select"] == True :
                        listeDonnees = [ ("IDfacture", IDfacture ), ]
                        DB.ReqMAJ("prestations", listeDonnees, "IDprestation", IDprestation)
                
                listeFacturesGenerees.append(IDfacture) 
                numero += 1
                index += 1

            DB.Close() 
            self.EcritStatusbar(u"")
            del dlgAttente

        except Exception, err:
            DB.Close() 
            del dlgAttente
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, u"Désolé, le problème suivant a été rencontré : \n\n%s" % err, u"Erreur", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.EcritStatusbar(u"")
            return False
        
        self.EcritStatusbar(u"")
        return listeFacturesGenerees







class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = Panel(panel)
        self.boutonTest = wx.Button(panel, -1, u"Bouton de test")
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
        
    def OnBoutonTest(self, event):
        """ Bouton Test """
        print "Validation =", self.ctrl.Validation()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, u"TEST", size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()



