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
from Ol import OL_Aides 
import GestionDB
import wx.lib.agw.hyperlink as Hyperlink
from Utils import UTILS_Utilisateurs
from Utils import UTILS_Parametres
import DLG_Message_html


class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL="", listeChoix=[], indexChoixDefaut=None, size=(-1, -1), pos=(0, 0)):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL, size=size, pos=pos)
        self.parent = parent
        self.URL = URL

        if self.GetGrandParent().GetName() == "notebook" :
            self.SetBackgroundColour(self.GetGrandParent().GetThemeBackgroundColour())

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
        import DLG_Detail_aides
        dlg = DLG_Detail_aides.Dialog(self, IDfamille=self.parent.IDfamille)
        dlg.ShowModal()
        dlg.Destroy() 
        self.parent.MAJ() 
        self.UpdateLink()
        

# -----------------------------------------------------------------------------------------------------------------------



class CTRL_Caisse(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(150, -1)) 
        self.parent = parent
##        self.MAJ() 
##        self.Select(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        else :
            self.Enable(True)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        db = GestionDB.DB()
        req = """SELECT IDcaisse, nom
        FROM caisses
        ORDER BY nom;"""
        db.ExecuterReq(req)
        listeDonnees = db.ResultatReq()
        db.Close()
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for IDcaisse, nom in listeDonnees :
            self.dictDonnees[index] = { "ID" : IDcaisse, "nom " : nom}
            listeItems.append(nom)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]
            

# -----------------------------------------------------------------------------------------------------------------------

class CTRL_Allocataire(wx.Choice):
    def __init__(self, parent):
        wx.Choice.__init__(self, parent, -1, size=(170, -1)) 
        self.parent = parent
##        self.MAJ() 
##        self.Select(0)
    
    def MAJ(self):
        listeItems = self.GetListeDonnees()
        if len(listeItems) == 0 :
            self.Enable(False)
        self.SetItems(listeItems)
                                        
    def GetListeDonnees(self):
        # Récupération de la liste des représentants de la famille
        DB = GestionDB.DB()
        req = """SELECT individus.IDindividu, nom, prenom
        FROM rattachements
        LEFT JOIN individus ON individus.IDindividu = rattachements.IDindividu
        WHERE IDfamille=%d AND IDcategorie=1
        GROUP BY individus.IDindividu
        ORDER BY nom, prenom;""" % self.parent.IDfamille
        DB.ExecuterReq(req)
        listeDonnees = DB.ResultatReq()
        DB.Close() 
        listeRepresentants = []
        for IDindividu, nom, prenom in listeDonnees :
            listeRepresentants.append({"IDindividu":IDindividu, "nom":nom, "prenom":prenom})
        
        # Remplissage du contrôle
        listeItems = [u"",]
        self.dictDonnees = {}
        self.dictDonnees[0] = { "ID" : 0, "nom" : _(u"Inconnue")}
        index = 1
        for donnees in listeRepresentants :
            label = u"%s %s" % (donnees["prenom"], donnees["nom"])
            self.dictDonnees[index] = { "ID" : donnees["IDindividu"], "nom " : label}
            listeItems.append(label)
            index += 1
        return listeItems

    def SetID(self, ID=0):
        if ID == None :
            self.SetSelection(0)
        for index, values in self.dictDonnees.iteritems():
            if values["ID"] == ID :
                 self.SetSelection(index)

    def GetID(self):
        index = self.GetSelection()
        if index == -1 or index == 0 : return None
        return self.dictDonnees[index]["ID"]
            

# -----------------------------------------------------------------------------------------------------------------------

class Panel(wx.Panel):
    def __init__(self, parent, IDfamille=None):
        wx.Panel.__init__(self, parent, id=-1, name="panel_caisse", style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.IDfamille = IDfamille
        
        self.majEffectuee = False
        
        # Caisse
        self.staticbox_caisse_staticbox = wx.StaticBox(self, -1, _(u"Caisse"))
        self.label_caisse = wx.StaticText(self, -1, _(u"Caisse d'allocation :"))
        self.ctrl_caisse = CTRL_Caisse(self)
        self.ctrl_caisse.SetMinSize((140, -1))
        self.bouton_caisses = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Mecanisme.png"), wx.BITMAP_TYPE_ANY))
        self.label_numero = wx.StaticText(self, -1, _(u"N° allocataire :"))
        self.ctrl_numero = wx.TextCtrl(self, -1, u"")
        self.label_allocataire = wx.StaticText(self, -1, _(u"Titulaire :"))
        self.ctrl_allocataire = CTRL_Allocataire(self)
        self.ctrl_allocataire.SetMinSize((140, -1))
        self.check_autorisation_cafpro = wx.CheckBox(self, -1, u"Accès CAFPRO")
        self.bouton_cafpro = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Cafpro.png"), wx.BITMAP_TYPE_ANY))

        # Aides
        self.staticbox_aides_staticbox = wx.StaticBox(self, -1, _(u"Aides journalières"))
        self.ctrl_aides = OL_Aides.ListView(self, id=-1, IDfamille=self.IDfamille, name="OL_aides", style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL|wx.LC_HRULES|wx.LC_VRULES)
        self.ctrl_aides.SetMinSize((20, 20)) 
        self.bouton_ajouter = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Ajouter.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Modifier.png"), wx.BITMAP_TYPE_ANY))
        self.bouton_supprimer = wx.BitmapButton(self, -1, wx.Bitmap(Chemins.GetStaticPath(u"Images/16x16/Supprimer.png"), wx.BITMAP_TYPE_ANY))
        
        self.hyper_liste = Hyperlien(self, label=_(u"Afficher la liste des déductions"), infobulle=_(u"Cliquez ici pour afficher la liste des déductions"), URL="")
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.OnChoixCaisse, self.ctrl_caisse)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckCafpro, self.check_autorisation_cafpro)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCaisse, self.bouton_caisses)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonCafpro, self.bouton_cafpro)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAjouter, self.bouton_ajouter)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonSupprimer, self.bouton_supprimer)
        
        # Init contrôles
        self.OnChoixCaisse(None)
        self.OnCheckCafpro(None)
        

    def __set_properties(self):
        self.ctrl_caisse.SetToolTip(wx.ToolTip(_(u"Sélectionnez une caisse")))
        self.bouton_caisses.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder à la gestion des caisses")))
        self.ctrl_numero.SetToolTip(wx.ToolTip(_(u"Saisissez le numéro d'allocataire")))
        self.ctrl_allocataire.SetToolTip(wx.ToolTip(_(u"Sélectionnez l'individu titulaire du dossier d'allocataire")))
        self.check_autorisation_cafpro.SetToolTip(wx.ToolTip(_(u"Cochez cette case si la famille a donné une autorisation de consultation CAFPRO")))
        self.bouton_cafpro.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour accéder au site CAFPRO")))
        self.bouton_ajouter.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour ajouter une aide journalière")))
        self.bouton_modifier.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour modifier l'aide sélectionnée dans la liste")))
        self.bouton_supprimer.SetToolTip(wx.ToolTip(_(u"Cliquez ici pour supprimer l'aide sélectionnée dans la liste")))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=5, hgap=5)
        
        # Caisse
        staticbox_caisse = wx.StaticBoxSizer(self.staticbox_caisse_staticbox, wx.VERTICAL)
        grid_sizer_caisse = wx.FlexGridSizer(rows=1, cols=12, vgap=5, hgap=5)
        grid_sizer_caisse.Add(self.label_caisse, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.Add(self.ctrl_caisse, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.Add(self.bouton_caisses, 0, 0, 0)
        grid_sizer_caisse.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_caisse.Add(self.label_numero, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.Add(self.ctrl_numero, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_caisse.Add(self.label_allocataire, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.Add(self.ctrl_allocataire, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.Add((10, 10), 0, wx.EXPAND, 0)
        grid_sizer_caisse.Add(self.check_autorisation_cafpro, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.Add(self.bouton_cafpro, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_caisse.AddGrowableCol(8)
        staticbox_caisse.Add(grid_sizer_caisse, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_caisse, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5)
        
        # Aides
        staticbox_aides = wx.StaticBoxSizer(self.staticbox_aides_staticbox, wx.VERTICAL)
        grid_sizer_aides = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)
        grid_sizer_aides.Add(self.ctrl_aides, 1, wx.EXPAND, 0)
        grid_sizer_boutons_aides = wx.FlexGridSizer(rows=3, cols=1, vgap=5, hgap=5)
        grid_sizer_boutons_aides.Add(self.bouton_ajouter, 0, 0, 0)
        grid_sizer_boutons_aides.Add(self.bouton_modifier, 0, 0, 0)
        grid_sizer_boutons_aides.Add(self.bouton_supprimer, 0, 0, 0)
        grid_sizer_aides.Add(grid_sizer_boutons_aides, 1, wx.EXPAND, 0)
        
        grid_sizer_outils = wx.FlexGridSizer(rows=1, cols=2, vgap=5, hgap=5)
        grid_sizer_outils.Add( (5, 5), 1, wx.EXPAND, 0)
        grid_sizer_outils.Add(self.hyper_liste, 0, 0, 0)
        grid_sizer_outils.AddGrowableCol(0)
        grid_sizer_aides.Add(grid_sizer_outils, 1, wx.EXPAND, 0)
        
        grid_sizer_aides.AddGrowableRow(0)
        grid_sizer_aides.AddGrowableCol(0)
        staticbox_aides.Add(grid_sizer_aides, 1, wx.ALL|wx.EXPAND, 5)
        grid_sizer_base.Add(staticbox_aides, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(1)
        grid_sizer_base.AddGrowableCol(0)

    def OnChoixCaisse(self, event): 
        if self.ctrl_caisse.GetSelection() == 0 :
            self.ctrl_numero.Enable(False)
            self.ctrl_allocataire.Enable(False)
        else:
            self.ctrl_numero.Enable(True)
            self.ctrl_allocataire.Enable(True)
            self.ctrl_numero.SetFocus() 

    def OnCheckCafpro(self, event):
        self.bouton_cafpro.Enable(self.check_autorisation_cafpro.GetValue())

    def OnBoutonCafpro(self, event):
        # Mémorisation du numéro allocataire dans le presse-papiers
        num_allocataire = self.ctrl_numero.GetValue()
        clipdata = wx.TextDataObject()
        clipdata.SetText(num_allocataire)
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(clipdata)
        wx.TheClipboard.Close()

        # Vérifie si case Ne plus Afficher cochée ou non
        if UTILS_Parametres.Parametres(mode="get", categorie="ne_plus_afficher", nom="acces_cafpro", valeur=False) == False :
            texte = u"""
<CENTER><IMG SRC="Static/Images/32x32/Astuce.png">
<FONT SIZE=3>
<BR>
<B>Astuce</B>
<BR><BR>
Le numéro d'allocataire de la famille a été copié dans le presse-papiers.
<BR><BR>
Collez tout simplement ce numéro dans le champ de recherche du site CAFPRO grâce à la combinaison de touches <B>CTRL+V</B> de votre clavier !
</FONT>
</CENTER>
"""
            dlg = DLG_Message_html.Dialog(self, texte=texte, titre=_(u"Astuce"), nePlusAfficher=True, size=(200, 300))
            dlg.ShowModal()
            nePlusAfficher = dlg.GetEtatNePlusAfficher()
            dlg.Destroy()
            if nePlusAfficher == True :
                UTILS_Parametres.Parametres(mode="set", categorie="ne_plus_afficher", nom="acces_cafpro", valeur=nePlusAfficher)

        # Ouverture du navigateur
        import webbrowser
        webbrowser.open("http://www.caf.fr/cafpro/Ident.jsp")

    def OnBoutonCaisse(self, event): 
        IDcaisse = self.ctrl_caisse.GetID()
        import DLG_Caisses
        dlg = DLG_Caisses.Dialog(self)
        dlg.ShowModal() 
        dlg.Destroy()
        self.ctrl_caisse.MAJ() 
        if IDcaisse == None : IDcaisse = 0
        self.ctrl_caisse.SetID(IDcaisse)

    def OnBoutonAjouter(self, event): 
        self.ctrl_aides.Ajouter(None)

    def OnBoutonModifier(self, event):
        self.ctrl_aides.Modifier(None) 

    def OnBoutonSupprimer(self, event): 
        self.ctrl_aides.Supprimer(None) 

    def IsLectureAutorisee(self):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_caisse", "consulter", afficheMessage=False) == False : 
            return False
        return True

    def MAJ(self):
        """ MAJ integrale du controle avec MAJ des donnees """
        # MAJ Caisse
        if self.majEffectuee == False :
            # MAJ des contrôles de choix
            self.ctrl_caisse.MAJ() 
            self.ctrl_allocataire.MAJ()
            # Importation des données de la famille
            db = GestionDB.DB()
            req = """SELECT IDcaisse, num_allocataire, allocataire, autorisation_cafpro
            FROM familles
            WHERE IDfamille=%d;""" % self.IDfamille
            db.ExecuterReq(req)
            listeDonnees = db.ResultatReq()
            db.Close()
            if len(listeDonnees) == 0 : return
            IDcaisse, num_allocataire, allocataire, autorisation_cafpro = listeDonnees[0]
            self.ctrl_caisse.SetID(IDcaisse)
            if num_allocataire != None :
                self.ctrl_numero.SetValue(num_allocataire)
            self.ctrl_allocataire.SetID(allocataire)
            self.OnChoixCaisse(None)
            if autorisation_cafpro != None :
                self.check_autorisation_cafpro.SetValue(autorisation_cafpro)
            self.OnCheckCafpro(None)
        else :
            # MAJ contrôles Allocataire titulaire
            allocataire = self.ctrl_allocataire.GetID()
            self.ctrl_allocataire.MAJ()
            self.ctrl_allocataire.SetID(allocataire)

        # MAJ aides
        self.ctrl_aides.MAJ() 
        self.Refresh() 

        # Verrouillage utilisateurs
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_caisse", "modifier", afficheMessage=False) == False : 
            self.ctrl_caisse.Enable(False)
            self.bouton_caisses.Enable(False)
            self.ctrl_numero.Enable(False)
            self.ctrl_allocataire.Enable(False)
            self.check_autorisation_cafpro.Enable(False)

        self.majEffectuee = True
                
    def ValidationData(self):
        """ Return True si les données sont valides et pretes à être sauvegardées """
        return True
    
    def Sauvegarde(self):
        if self.majEffectuee == True :
            IDcaisse = self.ctrl_caisse.GetID() 
            if IDcaisse != None :
                num_allocataire = self.ctrl_numero.GetValue() 
                allocataire = self.ctrl_allocataire.GetID() 
            else:
                num_allocataire = None
                allocataire = None
            autorisation_cafpro = int(self.check_autorisation_cafpro.GetValue())
            DB = GestionDB.DB()
            listeDonnees = [    
                    ("IDcaisse", IDcaisse),
                    ("num_allocataire", num_allocataire),
                    ("allocataire", allocataire),
                    ("autorisation_cafpro", autorisation_cafpro),
                    ]
            DB.ReqMAJ("familles", listeDonnees, "IDfamille", self.IDfamille)
            DB.Close()
        
        


class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl= Panel(panel, IDfamille=7)
##        self.ctrl.MAJ() 
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, _(u"TEST"), size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()

