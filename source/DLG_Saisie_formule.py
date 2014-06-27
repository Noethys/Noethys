#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------

import wx
import re
import wx.lib.agw.hyperlink as Hyperlink

OPERATEURS = [
    (u"est égal à", "="),
    (u"est différent de", "<>"),
    (u"est supérieur à", ">"),
    (u"est inférieur à", "<"),
    (u"est supérieur ou égal à", ">="),
    (u"est inférieur ou égal à", "<="),
    (u"est vide", "null"),
    (u"n'est pas vide", "notnull"),
    ]

def GetLabelsOperateurs():
    listeLabels = []
    for label, symbole in OPERATEURS :
        listeLabels.append(label)
    return listeLabels

def GetLabelsChamps(listeChamps):
    listeLabels = []
    for label, exemple, code in listeChamps:
        listeLabels.append(label)
    return listeLabels


# ---------------------------------------------------------------------------------------------------------------------------------
class Hyperlien(Hyperlink.HyperLinkCtrl):
    def __init__(self, parent, id=-1, label="", infobulle="", URL=""):
        Hyperlink.HyperLinkCtrl.__init__(self, parent, id, label, URL=URL)
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
        dlg = wx.SingleChoiceDialog(None, u"Sélectionnez un champ à insérer :", u"Insérer un champ", GetLabelsChamps(self.parent.listeChamps), wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            champ = self.parent.listeChamps[dlg.GetSelection()][2]
            self.parent.InsertTexte(champ)
        dlg.Destroy()
        self.UpdateLink()
        

# ---------------------------------------------------------------------------------------------------------------------------------



class Dialog(wx.Dialog):
    def __init__(self, parent, listeChamps=[]):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        self.parent = parent
        self.listeChamps = listeChamps

        self.box_formule_staticbox = wx.StaticBox(self, -1, u"Formule")
        
        self.label_si = wx.StaticText(self, -1, u"Si :")
        self.ctrl_champ = wx.Choice(self, -1, choices=GetLabelsChamps(listeChamps))
        self.ctrl_operateur = wx.Choice(self, -1, choices=GetLabelsOperateurs())
        self.ctrl_condition = wx.TextCtrl(self, -1, u"", size=(150, -1))
        
        self.label_afficher = wx.StaticText(self, -1, u"Afficher :")
        self.ctrl_afficher = wx.TextCtrl(self, -1, u"", style=wx.TE_MULTILINE)

        self.hyper_formule = Hyperlien(self, label=u"Insérer un champ", infobulle=u"Cliquez ici pour insérer un champ", URL="")

        self.bouton_aide = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Aide_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_ok = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Ok_L72.png", wx.BITMAP_TYPE_ANY))
        self.bouton_annuler = wx.BitmapButton(self, -1, wx.Bitmap(u"Images/BoutonsImages/Annuler_L72.png", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()
        
        self.Bind(wx.EVT_CHOICE, self.OnChoixOperateur, self.ctrl_operateur)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOk, self.bouton_ok)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAnnuler, self.bouton_annuler)
        
        # Init Contrôles
        self.ctrl_operateur.SetSelection(0)
        

    def __set_properties(self):
        self.SetTitle(u"Saisie d'une formule conditionnelle")
        self.ctrl_champ.SetToolTipString(u"Sélectionnez ici un champ dans la liste")
        self.ctrl_operateur.SetToolTipString(u"Sélectionnez un opérateur dans la liste")
        self.ctrl_condition.SetToolTipString(u"Saisissez ici la valeur conditionnelle. Il peut s'agir \nd'un mot ou d'une phrase. Vous pouvez également \nsaisir ' OU ' entre plusieurs mots pour saisir plusieurs \nconditions avec l'opérateur =.")
        self.ctrl_afficher.SetToolTipString(u"Saisissez ici le texte à afficher si la condition est vraie.\nIl peut s'agir d'un mot ou d'une phrase mais aussi \nd'un mot-clé. Ex : 'bonjour', '{INDIVIDU_NOM}',\n'123', etc...")
        self.bouton_aide.SetToolTipString(u"Cliquez ici pour obtenir de l'aide")
        self.bouton_ok.SetToolTipString(u"Cliquez ici pour valider")
        self.bouton_annuler.SetToolTipString(u"Cliquez ici pour annuler")

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=2, cols=1, vgap=10, hgap=10)
        grid_sizer_4 = wx.FlexGridSizer(rows=1, cols=4, vgap=10, hgap=10)
        box_formule = wx.StaticBoxSizer(self.box_formule_staticbox, wx.VERTICAL)
        grid_sizer_formule = wx.FlexGridSizer(rows=8, cols=2, vgap=0, hgap=5)
        grid_sizer_condition = wx.FlexGridSizer(rows=1, cols=3, vgap=5, hgap=5)
        grid_sizer_formule.Add(self.label_si, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_condition.Add(self.ctrl_champ, 0, 0, 0)
        grid_sizer_condition.Add(self.ctrl_operateur, 0, 0, 0)
        grid_sizer_condition.Add(self.ctrl_condition, 0, wx.EXPAND, 0)
        grid_sizer_formule.Add(grid_sizer_condition, 1, wx.EXPAND, 0)
        grid_sizer_formule.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_formule.Add( (5, 5), 0, wx.EXPAND, 0)
        grid_sizer_formule.Add(self.label_afficher, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_formule.Add(self.ctrl_afficher, 0, wx.EXPAND, 0)
        grid_sizer_formule.Add( (2, 2), 0, wx.EXPAND, 0)
        grid_sizer_formule.Add(self.hyper_formule, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)
        box_formule.Add(grid_sizer_formule, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_base.Add(box_formule, 1, wx.ALL|wx.EXPAND, 10)
        grid_sizer_4.Add(self.bouton_aide, 0, 0, 0)
        grid_sizer_4.Add((20, 20), 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.bouton_ok, 0, 0, 0)
        grid_sizer_4.Add(self.bouton_annuler, 0, 0, 0)
        grid_sizer_4.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_4, 1, wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, 10)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.CenterOnScreen()
    
    def OnChoixOperateur(self, event):
        operateur = OPERATEURS[self.ctrl_operateur.GetSelection()][1]
        if operateur in ("null", "notnull") :
            self.ctrl_condition.Enable(False)
        else:
            self.ctrl_condition.Enable(True)
        
    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Etatnominatif")

    def OnBoutonAnnuler(self, event): 
        self.EndModal(wx.ID_CANCEL)

    def OnBoutonOk(self, event): 
        # Validation
        if self.ctrl_champ.GetSelection() == -1 :
            dlg = wx.MessageDialog(self, u"Vous devez obligatoirement sélectionner un champ SI dans la liste !", u"Erreur", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            self.ctrl_champ.SetFocus()
            return
        self.EndModal(wx.ID_OK)

    def GetFormule(self):
        """ Rédaction de la formule """
        champ = self.listeChamps[self.ctrl_champ.GetSelection()][2]
        operateur = OPERATEURS[self.ctrl_operateur.GetSelection()][1]
        condition = self.ctrl_condition.GetValue()
        afficher = self.ctrl_afficher.GetValue() 
        if operateur == "null" :
            operateur = "="
            condition = u""
        if operateur == "notnull" :
            operateur = "<>"
            condition = u""
        formule = u"""[[SI %s%s%s->%s]]""" % (champ, operateur, condition, afficher)
        return formule

    def InsertTexte(self, texte=u""):
        positionCurseur = self.ctrl_afficher.GetInsertionPoint() 
        self.ctrl_afficher.WriteText(texte)
        self.ctrl_afficher.SetInsertionPoint(positionCurseur+len(texte)) 
        self.ctrl_afficher.SetFocus()



####-----Résolveur de formule-----------------------------------------------------------------

def ResolveurFormule(formule=u"", listeChamps=[], dictValeurs={}):
    """ Permet de résoudre une formule """
    formule = formule.rstrip("]]")
    formule = formule.lstrip("[[")
    # Recherche les infos dans la formule
    regex = re.compile(r"[^SI]({.+})(<>|>=|<=|>|<|=)(.*)->(.*)") 
    resultat = regex.search(formule)
    if resultat == None : return u""
    if len(resultat.groups()) != 4 : return u""
    champ, operateur, condition, valeur = resultat.groups()
    
    # Recherche une condition avec " OU "
    listeConditions = condition.split(" OU ")
    
    # Recherche la solution
    if dictValeurs.has_key(champ):
        valeurChamp = dictValeurs[champ]
        
        # Essaye de convertir les données
##        try : # Entier
##            valeurChamp = int(valeurChamp)
##            condition = int(condition) 
##        except : pass
        
##        print ("%s|%s->%s" % (valeurChamp, condition, valeur), )
        
        if valeurChamp == None :
            valeurChamp = u""
            
        # Comparaison des valeurs
        try :
            if operateur == "=" : 
                if valeurChamp == condition : return valeur
            if operateur == ">" : 
                if valeurChamp > condition : return valeur
            if operateur == "<" : 
                if valeurChamp < condition : return valeur
            if operateur == "<>" : 
                if valeurChamp != condition : return valeur
            if operateur == ">=" : 
                if valeurChamp >= condition : return valeur
            if operateur == "<=" : 
                if valeurChamp <= condition : return valeur
            if operateur == "=" and len(listeConditions) > 0 : 
                if valeurChamp in listeConditions : return valeur
        except :
            return u""
            
    # Renvoie la formule si elle n'a pas été résolue
    return u""

def DetecteFormule(texte):
    regex = re.compile(r"\[\[.*?\]\]") 
    resultat = regex.findall(texte)
    return resultat

def ResolveurTexte(texte=u"", listeChamps=[], dictValeurs={}):
    formules = DetecteFormule(texte)
    # Si aucune formule trouvée
    if len(formules) == 0 : return texte
    # On recherche la solution d'une formule
    for formule in formules :
        solution = ResolveurFormule(formule, listeChamps, dictValeurs)
        texte = texte.replace(formule, solution)
    return texte
    
    
    
    
    
if __name__ == u"__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    listeChamps = [ 
        (u"Nom de l'organisateur", u"Association Noethys", "{ORGANISATEUR_NOM}"),
        (u"Rue de l'organisateur", u"Avenue des Lilas", "{ORGANISATEUR_RUE}"),
        (u"Code postal de l'organisateur", u"29870", "{ORGANISATEUR_CP}"),
        ]
    
    dictValeurs = {
        "{ORGANISATEUR_NOM}" : u"Association Noethys",
        }
    
##    dialog_1 = Dialog(None, listeChamps=listeChamps)
##    app.SetTopWindow(dialog_1)
##    dialog_1.ShowModal()
##    app.MainLoop()
        
    resultat = ResolveurTexte(
                texte=u"Ceci est [[SI {FAMILLE_VILLE}<>->Bonjour brest !]] et voilà et aussi [[SI {FAMILLE_VILLE}=QUIMPER ->Salut quimper !]]...", 
                listeChamps=listeChamps, 
                dictValeurs=dictValeurs)
    print (resultat,)
