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
from Utils import UTILS_Adaptations
from Utils.UTILS_Traduction import _
import wx
import sys
import datetime
import traceback
from Ol import OL_Factures_generation_selection
from Utils import UTILS_Identification
from Utils import UTILS_Texte
from Utils import UTILS_Parametres
from Ctrl import CTRL_Saisie_euros

import GestionDB



class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, name="DLG_Factures_generation_selection", style=wx.TAB_TRAVERSAL)
        self.parent = parent

        # Factures à générer
        self.box_factures_staticbox = wx.StaticBox(self, -1, _(u"Factures à générer"))

        self.listviewAvecFooter = OL_Factures_generation_selection.ListviewAvecFooter(self) 
        self.ctrl_factures = self.listviewAvecFooter.GetListview()
        self.bouton_apercu = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_ANY))
        self.ctrl_recherche = OL_Factures_generation_selection.CTRL_Outils(self, listview=self.ctrl_factures, afficherCocher=True)

        # Options
        self.box_options_staticbox = wx.StaticBox(self, -1, _(u"Options"))
        self.bouton_option_montant = wx.Button(self, -1, _(u"Cocher uniquement les factures dont le montant 'Dû période' est supérieur ou égal à"))
        self.ctrl_option_montant = CTRL_Saisie_euros.CTRL(self)
        self.ctrl_option_montant.SetMinSize((70, -1))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonApercu, self.bouton_apercu)
        self.Bind(wx.EVT_BUTTON, self.CocherMontant, self.bouton_option_montant)

    def __set_properties(self):
        self.bouton_apercu.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour créer un aperçu PDF d'une ou plusieurs factures")))
        self.bouton_option_montant.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour cocher uniquement les factures dont le montant 'Dû Période' est supérieur ou égal au montant souhaité")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)

        # Factures
        box_factures = wx.StaticBoxSizer(self.box_factures_staticbox, wx.VERTICAL)
        grid_sizer_factures = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_factures.Add(self.listviewAvecFooter, 1, wx.EXPAND, 0)
        grid_sizer_boutons = wx.FlexGridSizer(rows=5, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons.Add(self.bouton_apercu, 0, 0, 0)
        grid_sizer_factures.Add(grid_sizer_boutons, 1, wx.EXPAND, 0)
        grid_sizer_factures.Add(self.ctrl_recherche, 1, wx.EXPAND, 0)

        grid_sizer_factures.AddGrowableRow(0)
        grid_sizer_factures.AddGrowableCol(0)
        box_factures.Add(grid_sizer_factures, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_factures, 1, wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, 0)

        # Options
        box_options = wx.StaticBoxSizer(self.box_options_staticbox, wx.VERTICAL)
        grid_sizer_options = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_options.Add(self.bouton_option_montant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_options.Add(self.ctrl_option_montant, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        box_options.Add(grid_sizer_options, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_options, 1, wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.EXPAND, 0)

        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(0)

        self.SetSizer(grid_sizer_base)
        box_factures.Fit(self)

    def MAJ(self):
        # Paramètres
        self.ctrl_factures.SetParametres(self.parent.dictParametres)
        # Montant
        montant = UTILS_Parametres.Parametres(mode="get", categorie="generation_factures", nom="cocher_montant_sup", valeur=0.0)
        self.ctrl_option_montant.SetMontant(montant)

    def CocherMontant(self, event=None):
        montant = self.ctrl_option_montant.GetMontant()
        self.ctrl_factures.CocherMontant(montant)

    def Validation(self):
        # Validation de la saisie
        nbreTotalFactures = len(self.ctrl_factures.GetObjects())
        nbreCoches = len(self.ctrl_factures.GetTracksCoches())
        if nbreCoches == 0 :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune facture à générer !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return False
        
        # Demande de confirmation
        if nbreCoches < nbreTotalFactures :
            texteSupp = _(u"(Sur un total de %d factures proposées) ") % nbreTotalFactures
        else :
            texteSupp = ""
        if nbreCoches == 1 :
            texte = _(u"Confirmez-vous la génération de 1 facture %s?") % texteSupp
        else :
            texte = _(u"Confirmez-vous la génération de %d factures %s?") % (nbreCoches, texteSupp)
        dlg = wx.MessageDialog(self, texte, _(u"Confirmation"), wx.YES_NO|wx.YES_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        if reponse != wx.ID_YES :
            return False
    
        # Génération des factures
        listeFacturesGenerees = self.SauvegardeFactures() 
        if listeFacturesGenerees == False :
            return False

        # Mémorisation du montant supp
        montant = self.ctrl_option_montant.GetMontant()
        UTILS_Parametres.Parametres(mode="set", categorie="generation_factures", nom="cocher_montant_sup", valeur=montant)

        # Envoi des factures générées
        self.parent.listeFacturesGenerees = listeFacturesGenerees
        
        return True

    def EcritStatusbar(self, texte=u""):
        try :
            topWindow = wx.GetApp().GetTopWindow() 
            topWindow.SetStatusText(texte)
        except : 
            pass

    def OnBoutonApercu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = UTILS_Adaptations.Menu()

        # Aperçu sélection
        id = wx.NewId()
        item = wx.MenuItem(menuPop, id, _(u"Aperçu de la facture sélectionnée"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_factures.ApercuSelection, id=id)

        # Aperçu factures cochées
        id = wx.NewId()
        item = wx.MenuItem(menuPop, id, _(u"Aperçu des factures cochées"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_factures.ApercuCoches, id=id)

        # Aperçu Toutes les factures
        id = wx.NewId()
        item = wx.MenuItem(menuPop, id, _(u"Aperçu de toutes les factures"))
        item.SetBitmap(wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG))
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_factures.ApercuToutes, id=id)

        menuPop.AppendSeparator()

        # Item Apercu avant impression
        item = wx.MenuItem(menuPop, 40, _(u"Aperçu avant impression de la liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Apercu.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_factures.Apercu, id=40)

        # Item Imprimer
        item = wx.MenuItem(menuPop, 50, _(u"Imprimer la liste"))
        bmp = wx.Bitmap(Chemins.GetStaticPath("Images/16x16/Imprimante.png"), wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.ctrl_factures.Imprimer, id=50)

        self.PopupMenu(menuPop)
        menuPop.Destroy()


    def SauvegardeFactures(self):
        """ Sauvegarde des factures """
        # Récupère Utilisateur en cours
        IDutilisateur = UTILS_Identification.GetIDutilisateur()
        
        # Génération des factures
        listeFacturesGenerees = []
        
        # Tri par ordre alphabétique de la liste
        listeComptes = []
        for track in self.ctrl_factures.GetTracksCoches() :
            listeComptes.append((track.nomSansCivilite, track.IDcompte_payeur))
        listeComptes.sort()

        # ProgressBar
        dlgProgress = wx.ProgressDialog(_(u"Génération des factures"), _(u"Initialisation..."), maximum=len(listeComptes), parent=None, style=wx.PD_SMOOTH | wx.PD_AUTO_HIDE | wx.PD_APP_MODAL)
        
        # Sélection du prochain numéro de facture
        numero = self.parent.dictParametres["prochain_numero"]
        IDprefixe = self.parent.dictParametres["IDprefixe"]
        
        if numero == None :
            # Recherche du prochain numéro de facture si mode AUTO
            if IDprefixe == None :
                conditions = "WHERE IDprefixe IS NULL"
            else :
                conditions = "WHERE IDprefixe=%d" % IDprefixe
            DB = GestionDB.DB()
            req = """SELECT MAX(numero)
            FROM factures
            %s;""" % conditions
            DB.ExecuterReq(req)
            listeDonnees = DB.ResultatReq()  
            DB.Close() 
            if listeDonnees[0][0] == None :
                numero = 1
            else:
                numero = listeDonnees[0][0] + 1
            
        # Sauvegarde
        DB = GestionDB.DB()
        try :
            
            index = 0
            for nomTitulaires, IDcompte_payeur in listeComptes :
                dictCompte = self.ctrl_factures.dictComptes[IDcompte_payeur]
                texte = _(u"Génération de la facture %d sur %d...") % (index+1, len(listeComptes))
                self.EcritStatusbar(texte)
                dlgProgress.Update(index+1, texte)

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
                for IDindividu in list(dictCompte["individus"].keys()) :
                    texteIndividus += "%d;" % IDindividu
                if len(list(dictCompte["individus"].keys())) > 0 :
                    texteIndividus = texteIndividus[:-1]

                # Sauvegarde de la facture
                listeDonnees = [ 
                    ("IDprefixe", IDprefixe),
                    ("numero", numero),
                    ("IDcompte_payeur", IDcompte_payeur),
                    ("date_edition", str(datetime.date.today())),
                    ("date_echeance", date_echeance),
                    ("activites", texteActivites),
                    ("individus", texteIndividus),
                    ("IDutilisateur", IDutilisateur),
                    ("date_debut", str(dictCompte["date_debut"])),
                    ("date_fin", str(dictCompte["date_fin"])),
                    ("total", float(total)),
                    ("regle", float(regle)),
                    ("solde", float(solde)),
                    ("IDlot", self.parent.dictParametres["IDlot"]),
                    ("prestations", ";".join(self.parent.dictParametres["prestations"])),
                    ("IDregie", self.parent.dictParametres["IDregie"]),
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
            dlgProgress.Destroy()

        except Exception as err:
            DB.Close()
            dlgProgress.Destroy()
            traceback.print_exc(file=sys.stdout)
            dlg = wx.MessageDialog(self, _(u"Désolé, le problème suivant a été rencontré : \n\n%s") % err, _(u"Erreur"), wx.OK | wx.ICON_ERROR)
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
        print("Validation =", self.ctrl.Validation())

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(700, 500))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()



