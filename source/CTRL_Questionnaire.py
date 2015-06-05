#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.agw.hypertreelist as HTL
import wx.lib.colourselect
##import wx.lib.agw.knobctrl
import datetime
import GestionDB

import CTRL_Saisie_date
import CTRL_Saisie_euros
import DLG_Saisie_categorie_question
import DLG_Saisie_question
import CTRL_Vignettes_documents

import UTILS_Utilisateurs
import wx.lib.agw.floatspin as FS


LISTE_CONTROLES = [
    {"code" : "ligne_texte", "label" : _(u"Ligne de texte"), "image" : "Texte_ligne.png", "filtre" : "texte"},
    {"code" : "bloc_texte", "label" : _(u"Bloc de texte multiligne"), "image" : "Texte_bloc.png", "options" : {"hauteur":60}, "filtre" : "texte" },
    {"code" : "entier", "label" : _(u"Nombre entier"), "image" : "Ctrl_nombre.png", "options" : {"min":0, "max":99999}, "filtre" : "entier" },
    {"code" : "decimal", "label" : _(u"Nombre décimal"), "image" : "Ctrl_decimal.png", "options" : {"min":0, "max":99999}, "filtre" : "decimal" },
    {"code" : "montant", "label" : _(u"Montant"), "image" : "Euro.png", "filtre" : "montant" },
    {"code" : "liste_deroulante", "label" : _(u"Liste déroulante"), "image" : "Ctrl_choice.png", "options":{"choix":None}, "filtre" : "choix" },
    {"code" : "liste_coches", "label" : _(u"Liste à cocher"), "image" : "Coches.png", "options" : {"hauteur":-1, "choix":None} , "filtre" : "choix"},
    {"code" : "case_coche", "label" : _(u"Case à cocher"), "image" : "Ctrl_coche.png" , "filtre" : "coche"},
    {"code" : "date", "label" : _(u"Date"), "image" : "Jour.png" , "filtre" : "date"},
    {"code" : "slider", "label" : _(u"Réglette"), "image" : "Reglette.png", "options" : {"hauteur":-1, "min":0, "max":100}, "filtre" : "entier" },
    {"code" : "couleur", "label" : _(u"Couleur"), "image" : "Ctrl_couleur.png", "options" : {"hauteur":20}, "filtre" : None},
##    {"code" : "potentiometre", "label" : _(u"Potentiomère"), "image" : "Potentiometre.png", "options" : {"hauteur":100, "min":0, "max":100} },
    {"code" : "documents", "label" : _(u"Porte-documents"), "image" : "Document.png", "options" : {"hauteur":60}, "filtre" : None},
    {"code" : "codebarres", "label" : _(u"Code-barres"), "image" : "Codebarres.png", "options" : {"norme":"39"}, "filtre" : "texte" },
    {"code" : "rfid", "label" : _(u"Badge RFID"), "image" : "Rfid.png" , "filtre" : "texte"},
    ] 

LISTE_NORMES_CODESBARRES = [
    {"code" : "Codabar", "label" : "Codabar"},
    {"code" : "Code11", "label" : "Code11"},
    {"code" : "I2of5", "label" : "I2of5"},
    {"code" : "MSI", "label" : "MSI"},
    {"code" : "Code128", "label" : "Code128"},
    {"code" : "Ean13BarcodeWidget", "label" : "Ean13BarcodeWidget"},
    {"code" : "Ean8BarcodeWidget", "label" : "Ean8BarcodeWidget"},
    {"code" : "Extended39", "label" : "Extended39"},
    {"code" : "Standard39", "label" : "Standard39"},
    {"code" : "Extended93", "label" : "Extended93"},
    {"code" : "Standard93", "label" : "Standard93"},
    {"code" : "FIM", "label" : "FIM"},
    {"code" : "POSTNET", "label" : "POSTNET"},
    {"code" : "USPS_4State", "label" : "USPS_4State"},
    ]

COULEUR_INVISIBLE = (200, 200, 200)


def ConvertCouleur(couleur=None):
    if couleur == None or len(couleur) == 0 : return None
    couleur = couleur[1:-1].split(",")
    couleur = (int(couleur[0]), int(couleur[1]), int(couleur[2]) )
    return couleur

# -----------------------------------------------------------------------------------------------------------------------


class DLG_Choix_creation(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.THICK_FRAME)
        self.parent = parent
        self.bouton_categorie = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Questionnaire_categorie.png", wx.BITMAP_TYPE_ANY))
        self.bouton_question = wx.BitmapButton(self, -1, wx.Bitmap("Images/BoutonsImages/Questionnaire_question.png", wx.BITMAP_TYPE_ANY))
        self.bouton_aide = CTRL_Bouton_image.CTRL(self, texte=_(u"Aide"), cheminImage="Images/32x32/Aide.png")
        self.bouton_annuler = CTRL_Bouton_image.CTRL(self, id=wx.ID_CANCEL, texte=_(u"Annuler"), cheminImage="Images/32x32/Annuler.png")
        
        self.bouton_categorie.SetMinSize((140, 120))
        self.bouton_question.SetMinSize((140, 120))
        
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnBoutonCategorie, self.bouton_categorie)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonQuestion, self.bouton_question)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonAide, self.bouton_aide)

    def __set_properties(self):
        self.SetTitle(_(u"Choix de l'élément à créer"))
        self.bouton_categorie.SetToolTipString(_(u"Créer une nouvelle catégorie"))
        self.bouton_question.SetToolTipString(_(u"Créer une nouvelle question"))
        self.bouton_aide.SetToolTipString(_(u"Obtenir de l'aide"))
        self.bouton_annuler.SetToolTipString(_(u"Annuler"))
        self.SetMinSize((340, 230))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=10, hgap=10)
        grid_sizer_contenu = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        grid_sizer_contenu.Add(self.bouton_categorie, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_contenu.Add(self.bouton_question, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        grid_sizer_contenu.AddGrowableRow(0)
        grid_sizer_contenu.AddGrowableCol(0)
        grid_sizer_contenu.AddGrowableCol(1)
        grid_sizer_base.Add(grid_sizer_contenu, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
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

    def OnBoutonCategorie(self, event): 
        self.EndModal(100)

    def OnBoutonQuestion(self, event): 
        self.EndModal(200)

    def OnBoutonAide(self, event): 
        import UTILS_Aide
        UTILS_Aide.Aide("Questionnaires")


# ----------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_ligne_texte(wx.TextCtrl):
    def __init__(self, parent, item=None, track=None):
        wx.TextCtrl.__init__(self, parent, id=-1, value="", size=(track.largeur, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.SetValue(valeur)
    
    def SetValeurStr(self, valeur=None):
        self.SetValeur(valeur)
    
    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetValue() 
        if valeur == "" : valeur = None
        return valeur

    def GetValeurStr(self):
        return self.GetValeur()

                    
# -------------------------------------------------------------------------------------------------------------------

class CTRL_bloc_texte(wx.TextCtrl):
    def __init__(self, parent, item=None, track=None):
        if track.dictOptions.has_key("hauteur"):
            hauteur = int(track.dictOptions["hauteur"])
        else:
            hauteur = 60
        wx.TextCtrl.__init__(self, parent, id=-1, value="", size=(track.largeur, hauteur), style=wx.TE_MULTILINE) 
        self.parent = parent
        self.item = item
        self.track = track
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.SetValue(valeur)

    def SetValeurStr(self, valeur=None):
        self.SetValeur(valeur)

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetValue() 
        if valeur == "" : valeur = None
        return valeur

    def GetValeurStr(self):
        return self.GetValeur()

# -------------------------------------------------------------------------------------------------------------------

class CTRL_entier(wx.SpinCtrl):
    def __init__(self, parent, item=None, track=None):
        wx.SpinCtrl.__init__(self, parent, id=-1, value="", size=(track.largeur, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        
        if self.track.dictOptions.has_key("min"):
            min = int(self.track.dictOptions["min"])
        else:
            min = 0
        if self.track.dictOptions.has_key("max"):
            max = int(self.track.dictOptions["max"])
        else:
            max = 99999
        self.SetRange(min,max)
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.SetValue(valeur)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        try : 
            valeur = int(valeur)
            self.SetValeur(valeur)
        except : 
            pass

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetValue() 
        if valeur == "" : valeur = None
        return valeur

    def GetValeurStr(self):
        return str(self.GetValeur())


# -------------------------------------------------------------------------------------------------------------------

class CTRL_decimal(FS.FloatSpin):
    def __init__(self, parent, item=None, track=None):
        self.parent = parent
        self.item = item
        self.track = track

        if self.track.dictOptions.has_key("min"):
            min = int(self.track.dictOptions["min"])
        else:
            min = 0
        if self.track.dictOptions.has_key("max"):
            max = int(self.track.dictOptions["max"])
        else:
            max = 99999

        FS.FloatSpin.__init__(self, parent, id=-1, min_val=min, max_val=max, increment=0.1, agwStyle=FS.FS_RIGHT, size=(track.largeur, -1)) 
        self.SetFormat("%f")
        self.SetDigits(6)
        
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = 0.0
        self.SetValue(valeur)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        try : 
            valeur = float(valeur)
            self.SetValeur(valeur)
        except : 
            pass

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetValue() 
        if valeur == "" : valeur = None
        return valeur

    def GetValeurStr(self):
        return str(self.GetValeur())


# -------------------------------------------------------------------------------------------------------------------


class CTRL_montant(CTRL_Saisie_euros.CTRL):
    def __init__(self, parent, item=None, track=None):
        CTRL_Saisie_euros.CTRL.__init__(self, parent, size=(track.largeur, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetBackgroundColour((255, 255, 255))
        self.SetToolTipString(_(u"Saisissez un montant"))
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        try :
            valeur = float(valeur)
            self.SetMontant(valeur)
        except :
            pass

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        self.SetValeur(valeur)

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetMontant() 
        return valeur

    def GetValeurStr(self):
        valeur = self.GetValeur()
        if valeur == None : 
            return None
        else :
            return str(valeur)

# -------------------------------------------------------------------------------------------------------------------


class CTRL_liste_deroulante(wx.Choice):
    def __init__(self, parent, item=None, track=None):
        wx.Choice.__init__(self, parent, id=-1, size=(track.largeur, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        # Remplissage des choix
        self.dictDonnees = {"0" : {"IDchoix":None},}
        self.listeLabels = [u"",]
        index = 1
        for dictChoix in track.listeChoix :
            self.listeLabels.append(dictChoix["label"])
            self.dictDonnees[index] = dictChoix
            index += 1
        self.SetItems(self.listeLabels)
    
    def SetValeur(self, IDchoix=None):
        if IDchoix == None : 
            self.Select(0)
        for index, dictChoix in self.dictDonnees.iteritems() :
            if IDchoix == dictChoix["IDchoix"] :
                self.Select(index)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        try : 
            valeur = int(valeur)
            self.SetValeur(valeur)
        except : 
            pass

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        index = self.GetSelection() 
        if self.dictDonnees.has_key(index) :
            dictChoix = self.dictDonnees[index]
            return dictChoix["IDchoix"]
        else:
            return None

    def GetValeurStr(self):
        valeur = self.GetValeur()
        if valeur == None : 
            return None
        return str(valeur)

# -------------------------------------------------------------------------------------------------------------------

class CTRL_liste_coches(wx.CheckListBox):
    def __init__(self, parent, item=None, track=None):
        if track.dictOptions.has_key("hauteur"):
            hauteur = int(track.dictOptions["hauteur"])
        else:
            hauteur = -1
        wx.CheckListBox.__init__(self, parent, id=-1, size=(track.largeur, hauteur)) 
        self.parent = parent
        self.item = item
        self.track = track
        # Remplissage des choix
        self.dictDonnees = {}
        self.listeLabels = []
        index = 0
        for dictChoix in track.listeChoix :
            self.listeLabels.append(dictChoix["label"])
            self.dictDonnees[index] = dictChoix
            index += 1
        self.SetItems(self.listeLabels)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

    def SetValeur(self, listeIDchoix=[]):
        for index, dictChoix in self.dictDonnees.iteritems() :
            if dictChoix["IDchoix"] in listeIDchoix :
                etat = True
            else:
                etat = False
            self.Check(index, etat)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        try : 
            listTemp = valeur.split(";")
            listeIDchoix = []
            for IDchoix in listTemp :
                listeIDchoix.append(int(IDchoix))
            self.SetValeur(listeIDchoix)
        except : 
            pass

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        listeIDchoix = []
        for index, dictChoix in self.dictDonnees.iteritems() :
            if self.IsChecked(index) == True :
                listeIDchoix.append(dictChoix["IDchoix"])
        if len(listeIDchoix) == 0 : return None
        return listeIDchoix

    def GetValeurStr(self):
        listeIDchoix = self.GetValeur()
        if listeIDchoix == None : return None
        listeStr = []
        for IDchoix in listeIDchoix :
            listeStr.append(str(IDchoix))
        texte = ";".join(listeStr)
        return texte
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Tout cocher
        item = wx.MenuItem(menuPop, 10, _(u"Tout cocher"))
        bmp = wx.Bitmap("Images/16x16/Cocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheTout, id=10)

        # Item Tout décocher
        item = wx.MenuItem(menuPop, 20, _(u"Tout décocher"))
        bmp = wx.Bitmap("Images/16x16/Decocher.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.CocheRien, id=20)

        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def CocheTout(self, event=None):
        index = 0
        for index in range(0, len(self.listeLabels)):
            self.Check(index)
            index += 1

    def CocheRien(self, event=None):
        index = 0
        for index in range(0, len(self.listeLabels)):
            self.Check(index, False)
            index += 1


# -------------------------------------------------------------------------------------------------------------------

class CTRL_case_coche(wx.CheckBox):
    def __init__(self, parent, item=None, track=None):
        wx.CheckBox.__init__(self, parent, id=-1, size=(-1, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.SetValue(valeur)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        try :
            valeur = int(valeur)
            self.SetValeur(valeur) 
        except : 
            pass

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetValue() 
        return int(valeur)

    def GetValeurStr(self):
        return str(self.GetValeur())

# -------------------------------------------------------------------------------------------------------------------

class CTRL_date(CTRL_Saisie_date.Date2):
    def __init__(self, parent, item=None, track=None):
        CTRL_Saisie_date.Date2.__init__(self, parent) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetBackgroundColour((255, 255, 255))
        self.ctrl_date.SetToolTipString(_(u"Saisissez une date"))
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.SetDate(valeur)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        self.SetValeur(valeur)

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetDate() 
        return valeur

    def GetValeurStr(self):
        valeur = self.GetValeur()
        if valeur == None : 
            return None
        else :
            return str(valeur)

# -------------------------------------------------------------------------------------------------------------------

class CTRL_slider(wx.Panel):
    def __init__(self, parent, item=None, track=None):
        if track.dictOptions.has_key("hauteur"):
            hauteur = int(track.dictOptions["hauteur"])
        else:
            hauteur = -1
        wx.Panel.__init__(self, parent, id=-1, size=(track.largeur, hauteur)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # Contrôles
        self.label_valeur = wx.StaticText(self, -1, "0")
        self.label_valeur.SetMinSize((25, -1))
        
        self.ctrl_slider = wx.Slider(self, -1, style=wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)
        if track.dictOptions.has_key("min"):
            min = int(track.dictOptions["min"])
        else:
            min = 0
        if track.dictOptions.has_key("max"):
            max = int(track.dictOptions["max"])
        else:
            max = 10
        self.ctrl_slider.SetRange(minValue=min, maxValue=max)
        self.ctrl_slider.SetValue(0)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.OnSlider, self.ctrl_slider)
        self.ctrl_slider.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.ctrl_slider.SetToolTipString(_(u"Faites glisser la glissière sur la valeur de votre choix"))

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        grid_sizer_base.Add(self.label_valeur, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_base.Add(self.ctrl_slider, 1, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(1)        
        self.Layout()

    def OnSlider(self, event): 
        valeur = self.ctrl_slider.GetValue() 
        self.label_valeur.SetLabel(str(valeur))

    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.ctrl_slider.SetValue(valeur)
        self.OnSlider(None)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        try : 
            valeur = int(valeur)
            self.SetValeur(valeur)
        except : 
            pass

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        return self.ctrl_slider.GetValue() 

    def GetValeurStr(self):
        return str(self.GetValeur())

# -------------------------------------------------------------------------------------------------------------------

class CTRL_couleur(wx.lib.colourselect.ColourSelect):
    def __init__(self, parent, item=None, track=None):
        if track.dictOptions.has_key("hauteur"):
            hauteur = int(track.dictOptions["hauteur"])
        else:
            hauteur = 20
        wx.lib.colourselect.ColourSelect.__init__(self, parent, id=-1, label="", colour=(255, 255, 255), size=(track.largeur, hauteur)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetBackgroundColour((255, 255, 255))
        self.SetToolTipString(_(u"Cliquez ici pour sélectionner une couleur"))

    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.SetColour(valeur)

    def SetValeurStr(self, valeur=None):
        if valeur == None or valeur == "" : return
        try : 
            valeur = ConvertCouleur(valeur)
            self.SetValeur(valeur)
        except : 
            pass

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        return self.GetColour()
    
    def GetValeurStr(self):
        return str(self.GetValeur())
        
# -------------------------------------------------------------------------------------------------------------------

##class CTRL_potentiometre(wx.Panel):
##    def __init__(self, parent, item=None, track=None):
##        if track.dictOptions.has_key("hauteur"):
##            hauteur = int(track.dictOptions["hauteur"])
##        else:
##            hauteur = 100
##        wx.Panel.__init__(self, parent, id=-1, size=(track.largeur, hauteur)) 
##        self.parent = parent
##        self.item = item
##        self.track = track
##        
##        # Contrôles
##        self.label_valeur = wx.StaticText(self, -1, "0")
##        self.label_valeur.SetMinSize((25, -1))
##        self.SetBackgroundColour((255, 255, 255))
##        
##        self.ctrl_poten = wx.lib.agw.knobctrl.KnobCtrl(self, -1, size=(hauteur, hauteur))
##        if track.dictOptions.has_key("min"):
##            min = int(track.dictOptions["min"])
##        else:
##            min = 0
##        if track.dictOptions.has_key("max"):
##            max = int(track.dictOptions["max"])
##        else:
##            max = 100
##        self.ctrl_poten.SetTags(range(min, max, 5))
##        self.ctrl_poten.SetAngularRange(-45, 225)
##        self.ctrl_poten.SetTagsColour((180, 180, 180))
##        self.Bind(wx.lib.agw.knobctrl.EVT_KC_ANGLE_CHANGED, self.OnKnob, self.ctrl_poten)
##        
##        self.SetValeur(((max-min)/2))
##
##        # Layout
##        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
##        grid_sizer_base.Add(self.label_valeur, 0, wx.ALIGN_CENTER_VERTICAL, 0)
##        grid_sizer_base.Add(self.ctrl_poten, 1, wx.EXPAND, 0)
##        self.SetSizer(grid_sizer_base)
##        grid_sizer_base.AddGrowableCol(1)        
##        self.Layout()
##
##    def OnKnob(self, event): 
##        valeur = self.ctrl_poten.GetValue() 
##        self.label_valeur.SetLabel(str(valeur))
##
##    def SetValeur(self, valeur=None):
##        if valeur == None : valeur = u""
##        self.ctrl_poten.SetValue(valeur)
##        self.OnKnob(None)
##
##    def SetValeurStr(self, valeur=None):
##        if valeur == None or valeur == "" : return
##        try : 
##            valeur = int(valeur)
##            self.SetValeur(valeur)
##        except : 
##            pass
##
##    def ValidationValeur(self):
##        return True
##
##    def GetValeur(self):
##        return self.ctrl_poten.GetValue() 
##
##    def GetValeurStr(self):
##        return str(self.GetValeur())

# ------------------------------------------------------------------------------------------------------------

class CTRL_documents(wx.Panel):
    def __init__(self, parent, item=None, track=None):
        if track.dictOptions.has_key("hauteur"):
            hauteur = int(track.dictOptions["hauteur"])
        else:
            hauteur = -1
        wx.Panel.__init__(self, parent, id=-1, size=(track.largeur, hauteur)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # Contrôles
        if hauteur < 30 : 
            hauteur = 30
        self.ctrl_vignettes = CTRL_Vignettes_documents.CTRL(self, IDreponse=None, afficheLabels=False, tailleVignette=hauteur-20, style=wx.BORDER_SUNKEN)
        
        self.bouton_outils = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Outils.png", wx.BITMAP_TYPE_ANY))
        self.bouton_outils.SetToolTipString(_(u"Cliquez ici pour accéder aux commandes disponibles"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOutils, self.bouton_outils)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_vignettes, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_outils, 0, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)        
        self.Layout()

    def OnBoutonOutils(self, event): 
        self.ctrl_vignettes.OnContextMenu()

    def SetValeur(self, valeur=None):
        IDquestion = self.track.IDquestion
        dictReponses = self.GetGrandParent().dictReponses
        if dictReponses.has_key(IDquestion) :
            IDreponse = dictReponses[IDquestion]["IDreponse"]
            self.ctrl_vignettes.SetIDreponse(IDreponse)

    def SetValeurStr(self, valeur=None):
        self.SetValeur(valeur)

    def ValidationValeur(self):
        return True

    def GetValeur(self):
        return None

    def GetValeurStr(self):
        return "##DOCUMENTS##"

    def Sauvegarde(self, IDreponse=None) :
        nbreDocuments = self.ctrl_vignettes.Sauvegarde(IDreponseFinal=IDreponse)
        return nbreDocuments
    
    def GetNbreDocuments(self):
        return self.ctrl_vignettes.GetNbreDocuments() 

# -------------------------------------------------------------------------------------------------------------------

class CTRL_codebarres(wx.TextCtrl):
    def __init__(self, parent, item=None, track=None):
        wx.TextCtrl.__init__(self, parent, id=-1, value="", size=(track.largeur, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
    
    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.SetValue(valeur)
    
    def SetValeurStr(self, valeur=None):
        self.SetValeur(valeur)
    
    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.GetValue() 
        if valeur == "" : valeur = None
        return valeur

    def GetValeurStr(self):
        return self.GetValeur()

# -------------------------------------------------------------------------------------------------------------------

class CTRL_rfid(wx.Panel):
    def __init__(self, parent, item=None, track=None):
        wx.Panel.__init__(self, parent, id=-1, size=(track.largeur, -1)) 
        self.parent = parent
        self.item = item
        self.track = track
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        
        # Contrôles
        self.ctrl_code = wx.TextCtrl(self, -1, "")
        self.bouton_modifier = wx.BitmapButton(self, -1, wx.Bitmap("Images/16x16/Rfid.png", wx.BITMAP_TYPE_ANY))
        self.bouton_modifier.SetToolTipString(_(u"Cliquez ici pour scanner un badge"))
        self.Bind(wx.EVT_BUTTON, self.OnBoutonModifier, self.bouton_modifier)
        
        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=0, hgap=0)
        grid_sizer_base.Add(self.ctrl_code, 1, wx.EXPAND, 0)
        grid_sizer_base.Add(self.bouton_modifier, 0, wx.EXPAND, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.AddGrowableCol(0)        
        self.Layout()
    
    def OnBoutonModifier(self, event=None):
        import DLG_Saisie_rfid
        if DLG_Saisie_rfid.CheckLecteurs() == False :
                dlg = wx.MessageDialog(self, _(u"Aucun lecteur RFID connecté."), "Erreur", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return 
        # DLG Saisie Badge RFID
        dlg = DLG_Saisie_rfid.Dialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            IDbadge = dlg.GetIDbadge()
            self.SetValeur(IDbadge)
        dlg.Destroy()

    def SetValeur(self, valeur=None):
        if valeur == None : valeur = u""
        self.ctrl_code.SetValue(valeur)
    
    def SetValeurStr(self, valeur=None):
        self.SetValeur(valeur)
    
    def ValidationValeur(self):
        return True

    def GetValeur(self):
        valeur = self.ctrl_code.GetValue() 
        if valeur == "" : valeur = None
        return valeur

    def GetValeurStr(self):
        return self.GetValeur()


####---------------------------------- ---------------------------------------------------------------------

class Track(object):
    def __init__(self, donnees, dictChoix={}):
        self.largeur = 0
        self.IDquestion = donnees[0]
        self.IDcategorie = donnees[1]
        self.ordre = donnees[2]
        self.visible = donnees[3]
        self.label = donnees[4]
        self.controle = donnees[5]
        self.defaut = donnees[6]
        self.options = donnees[7]
        
        # Formatage des options
        self.dictOptions = {}
        if self.options != None and self.options != "" :
            listeOptions = self.options.split(";")
            for option in listeOptions :
                codeOption, valeurOption = option.split("=")
                self.dictOptions[codeOption] = valeurOption
        
        # Liste de choix
        if dictChoix.has_key(self.IDquestion):
            self.listeChoix = dictChoix[self.IDquestion]
        else:
            self.listeChoix = []
            
        # Items HyperTreeList
        self.item = None
        self.itemParent = None
        self.ctrl = None
    
    def SetValeur(self, valeur=None):
        self.ctrl.SetValeur(valeur) 
        
    def SetValeurStr(self, valeur=None):
        self.ctrl.SetValeurStr(valeur) 
        
    def GetValeur(self):
        return self.ctrl.GetValeur() 

    def GetValeurStr(self):
        return self.ctrl.GetValeurStr() 
    
            
# --------------------------------------------------------------------------------------------------------------------------------

class CTRL(HTL.HyperTreeList):
    def __init__(self, parent, type="individu", mode="normal", 
                                        menuActif=False, afficherInvisibles=False, 
                                        IDindividu=None, IDfamille=None,
                                        largeurQuestion=290, largeurReponse=300,
                                        ): 
        HTL.HyperTreeList.__init__(self, parent, -1)
        self.parent = parent
        self.type = type
        self.mode = mode
        self.menuActif = menuActif
        self.afficherInvisibles = afficherInvisibles
        self.IDindividu = IDindividu
        self.IDfamille = IDfamille
        self.largeurQuestion = largeurQuestion
        self.largeurReponse = largeurReponse

        self.listeTracks = []
        self.dictCategories = {}
        self.listeIDcategorie = []
        self.dictValeursInitiales = {}
        self.dictReponses = {}
        
        self.SetBackgroundColour(wx.WHITE)
        
        # Création des colonnes
        listeColonnes = [
            ( _(u"Question"), self.largeurQuestion, wx.ALIGN_LEFT),
            ( _(u"Réponse"), self.largeurReponse, wx.ALIGN_LEFT),
            ]
        numColonne = 0
        for label, largeur, alignement in listeColonnes :
            self.AddColumn(label)
            self.SetColumnWidth(numColonne, largeur)
            self.SetColumnAlignment(numColonne, alignement)
            numColonne += 1
        
        if mode == "normal" : self.SetAGWWindowStyleFlag(wx.TR_ROW_LINES |wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT | HTL.TR_NO_HEADER)
        if mode == "apercu" : self.SetAGWWindowStyleFlag(wx.TR_ROW_LINES |wx.TR_HIDE_ROOT | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT | HTL.TR_NO_HEADER)
        self.EnableSelectionVista(True)
        
        # Création de l'ImageList
        il = wx.ImageList(16, 16)
        self.img_invisible = il.Add(wx.Bitmap('Images/16x16/Interdit2.png', wx.BITMAP_TYPE_PNG))
        self.AssignImageList(il)

        # Binds
        if self.menuActif == True :
            self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.OnContextMenu) 
            self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.Modifier) 

        # Importation
        if mode == "normal" :
            self.Importation() 
        
        # Blocage Utilisateurs
        if type == "individu" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("individus_questionnaires", "modifier", afficheMessage=False) == False : self.Enable(False)
        if type == "famille" and UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("familles_questionnaires", "modifier", afficheMessage=False) == False : self.Enable(False)
    
    def SetType(self, type="individu"):
        self.type = type
        self.Importation() 
        self.MAJ() 

    def RAZ(self):
        self.DeleteAllItems()
        for indexColonne in range(self.GetColumnCount()-1, -1, -1) :
            self.RemoveColumn(indexColonne)
        self.DeleteRoot() 
        self.Initialisation()

    def MAJ(self, importation=True, selection=None):
        """ Met à jour (redessine) tout le contrôle """
        self.Freeze()
        self.DeleteAllItems()
        # Création de la racine
        self.root = self.AddRoot(_(u"Racine"))
        if importation == True :
            self.Importation() 
        # Création des contrôles
        self.Remplissage(selection=selection)
        # Mémorisation des valeurs initiales
        if importation == True :
            self.dictValeursInitiales = self.GetValeurs() 
        self.Thaw() 
        
    def Importation(self):
        self.dictCategories = {}
        self.listeIDcategorie = []
        self.dictValeursInitiales = {}
        self.dictReponses = {}

        # Importation des catégories
        DB = GestionDB.DB()
        req = """SELECT IDcategorie, ordre, visible, type, couleur, label
        FROM questionnaire_categories
        WHERE type='%s'
        ORDER BY ordre
        ;""" % self.type
        DB.ExecuterReq(req)
        listeCategories = DB.ResultatReq()     
        self.listeIDcategorie = []
        self.dictCategories = {}
        for IDcategorie, ordre, visible, type, couleur, label in listeCategories :
            self.listeIDcategorie.append(IDcategorie) 
            couleur = ConvertCouleur(couleur)
            self.dictCategories[IDcategorie] = {"ordre":ordre, "visible":visible, "couleur":couleur, "label":label, "questions":[]}

        # Importation des choix
        req = """SELECT IDchoix, IDquestion, ordre, visible, label
        FROM questionnaire_choix
        ORDER BY IDquestion, ordre;"""
        DB.ExecuterReq(req)
        listeChoix = DB.ResultatReq()     
        dictChoix = {}
        for IDchoix, IDquestion, ordre, visible, label in listeChoix :
            if dictChoix.has_key(IDquestion) == False :
                dictChoix[IDquestion] = []
            dictTemp = {"IDchoix":IDchoix, "ordre":ordre, "visible":visible, "label":label}
            dictChoix[IDquestion].append(dictTemp)

        # Importation des questions
        if len(self.listeIDcategorie) == 0 : return None
        elif len(self.listeIDcategorie) == 1 : conditionCategories = "IDcategorie=%d" % self.listeIDcategorie[0]
        else : conditionCategories = "IDcategorie IN %s" % str(tuple(self.listeIDcategorie))
        req = """SELECT IDquestion, IDcategorie, ordre, visible, label, controle, defaut, options
        FROM questionnaire_questions
        WHERE %s
        ORDER BY ordre
        ;""" % conditionCategories
        DB.ExecuterReq(req)
        listeQuestions = DB.ResultatReq()     
        for item in listeQuestions :
            track = Track(item, dictChoix)
            self.dictCategories[track.IDcategorie]["questions"].append(track)

        # Importation des réponses
        if self.IDindividu != None or self.IDfamille != None :
            if self.IDindividu != None : conditionReponses = "IDindividu=%d" % self.IDindividu
            if self.IDfamille != None : conditionReponses = "IDfamille=%d" % self.IDfamille
            req = """SELECT IDreponse, IDquestion, IDindividu, IDfamille, reponse
            FROM questionnaire_reponses
            WHERE %s
            ;""" % conditionReponses
            DB.ExecuterReq(req)
            listeReponses = DB.ResultatReq()     
            for IDreponse, IDquestion, IDindividu, IDfamille, reponse in listeReponses :
                self.dictReponses[IDquestion] = {"IDreponse":IDreponse, "reponse":reponse} 

        DB.Close() 
        
            
    def Remplissage(self, selection=None):
        # Création des branches
        self.dictBranches = {}
        indexCategorie = 0
        for IDcategorie in self.listeIDcategorie :
            
            label = self.dictCategories[IDcategorie]["label"]
            couleur = self.dictCategories[IDcategorie]["couleur"]
            categorieVisible = self.dictCategories[IDcategorie]["visible"]
            listeQuestions = self.dictCategories[IDcategorie]["questions"]
            
            if categorieVisible == 1 or self.afficherInvisibles == True :
            
                # Niveau Catégorie
                brancheCategorie = self.AppendItem(self.root, label)
                self.SetPyData(brancheCategorie, IDcategorie)
                self.SetItemBold(brancheCategorie, True)
                self.SetItemBackgroundColour(brancheCategorie, couleur)
                self.dictBranches[brancheCategorie] = {"type":"categorie", "ID":IDcategorie, "index":indexCategorie} 
                
                if categorieVisible == 0 :
                    self.SetItemImage(brancheCategorie, self.img_invisible, which=wx.TreeItemIcon_Normal)

                if selection != None :
                    if selection[0] == "categorie" and selection[1] == IDcategorie :
                        self.SelectItem(brancheCategorie)
                        
                if self.mode == "apercu" :
                    self.SetItemText(brancheCategorie, label, 1)
                
                # Niveau Question
                indexQuestion = 0
                for track in listeQuestions :
                    IDquestion = track.IDquestion
                    questionVisible = track.visible 
                    
                    if questionVisible == 1 or self.afficherInvisibles == True :

                        brancheQuestion = self.AppendItem(brancheCategorie, track.label)
                        self.SetPyData(brancheQuestion, track.IDquestion)
                        self.dictBranches[brancheQuestion] = {"type":"question", "ID":IDquestion, "IDcategorie":IDcategorie, "index":indexQuestion} 
                        
                        if questionVisible == 0 :
                            self.SetItemImage(brancheQuestion, self.img_invisible, which=wx.TreeItemIcon_Normal)
                            
                        if selection != None :
                            if selection[0] == "question" and selection[1] == IDquestion :
                                self.SelectItem(brancheQuestion)

                        # Mémorisation des items dans le track
                        track.item = brancheQuestion
                        track.itemParent = brancheCategorie
                        track.largeur = self.largeurReponse - 7                

                        # CTRL du type de calcul
                        if track.controle == "ligne_texte" : ctrl = CTRL_ligne_texte(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, -1) )
                        if track.controle == "bloc_texte" : ctrl = CTRL_bloc_texte(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, 60) )
                        if track.controle == "entier" : ctrl = CTRL_entier(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, -1) )
                        if track.controle == "decimal" : ctrl = CTRL_decimal(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, -1) )
                        if track.controle == "montant" : ctrl = CTRL_montant(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, -1) )
                        if track.controle == "liste_deroulante" : ctrl = CTRL_liste_deroulante(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, -1) )
                        if track.controle == "liste_coches" : ctrl = CTRL_liste_coches(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, -1) )
                        if track.controle == "case_coche" : ctrl = CTRL_case_coche(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(-1, -1) )
                        if track.controle == "date" : ctrl = CTRL_date(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(-1, -1) )
                        if track.controle == "slider" : ctrl = CTRL_slider(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, -1) )
                        if track.controle == "couleur" : ctrl = CTRL_couleur(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, 20) )
##                        if track.controle == "potentiometre" : ctrl = CTRL_potentiometre(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, 100) )
                        if track.controle == "documents" : ctrl = CTRL_documents(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, 20) )
                        if track.controle == "codebarres" : ctrl = CTRL_codebarres(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, 20) )
                        if track.controle == "rfid" : ctrl = CTRL_rfid(self.GetMainWindow(), item=brancheQuestion, track=track) # size=(largeurControle, 20) )
                        
                        if track.controle != None :
                            self.SetItemWindow(brancheQuestion, ctrl, 1)        
                            track.ctrl = ctrl      
                        
                        # Insère la valeur
                        if self.dictReponses.has_key(IDquestion) :
                            valeur = self.dictReponses[IDquestion]["reponse"]
                        else:
                            valeur = track.defaut
                        track.SetValeurStr(valeur)
                        
                        indexQuestion += 1
                        
                indexCategorie += 1
                                    
        self.ExpandAllChildren(self.root)
        
        # Pour éviter le bus de positionnement des contrôles
        self.GetMainWindow().CalculatePositions() 
    
    def IdentificationBranche(self, branche):
        if self.dictBranches.has_key(branche) :
            return self.dictBranches[branche]
        else:
            return None
    
    def GetDictReponses(self):
        return self.dictReponses
    
    def GetDictValeursInitiales(self):
        return self.dictValeursInitiales
    
    def GetValeurs(self):
        # Récupère les valeurs du contrôle """
        dictValeurs = {}
        for IDcategorie in self.listeIDcategorie :
            for track in self.dictCategories[IDcategorie]["questions"] :
                if track.ctrl != None :
                    dictValeurs[track.IDquestion] = track.GetValeurStr()
        return dictValeurs

    def SetValeurs(self, dictValeurs={}):
        # Remplit le ctrl avec les valeurs données. Ex : {IDquestion : valeur} """
        for track in self.dictCategories[IDcategorie]["questions"] :
            if dictValeurs.has_key(track.IDquestion) :
                track.SetValeurStr(dictValeurs[track.IDquestion])
        
    def OnContextMenu(self, event):
        """Ouverture du menu contextuel """      
        item = self.GetSelection() 
        resultat = self.IdentificationBranche(item) 
        if resultat == None :
            noSelection = True
        else:
            noSelection = False
          
        # Création du menu contextuel
        menuPop = wx.Menu()

        # Item Modifier
        item = wx.MenuItem(menuPop, 10, _(u"Ajouter"))
        bmp = wx.Bitmap("Images/16x16/Ajouter.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Ajouter, id=10)
        
        menuPop.AppendSeparator()

        # Item Ajouter
        item = wx.MenuItem(menuPop, 20, _(u"Modifier"))
        bmp = wx.Bitmap("Images/16x16/Modifier.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Modifier, id=20)
        if noSelection == True : item.Enable(False)
        
        # Item Supprimer
        item = wx.MenuItem(menuPop, 30, _(u"Supprimer"))
        bmp = wx.Bitmap("Images/16x16/Supprimer.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Supprimer, id=30)
        if noSelection == True : item.Enable(False)
                
        menuPop.AppendSeparator()
    
        # Item Monter
        item = wx.MenuItem(menuPop, 40, _(u"Monter"))
        bmp = wx.Bitmap("Images/16x16/Fleche_haut.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Monter, id=40)
        if noSelection == True : item.Enable(False)
        
        # Item Descendre
        item = wx.MenuItem(menuPop, 50, _(u"Descendre"))
        bmp = wx.Bitmap("Images/16x16/Fleche_bas.png", wx.BITMAP_TYPE_PNG)
        item.SetBitmap(bmp)
        menuPop.AppendItem(item)
        self.Bind(wx.EVT_MENU, self.Descendre, id=50)
        if noSelection == True : item.Enable(False)
        
        self.PopupMenu(menuPop)
        menuPop.Destroy()

    def Ajouter(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_questionnaires", "creer") == False : return
        dlg = DLG_Choix_creation(self)
        if len(self.dictCategories) == 0 :
            dlg.bouton_question.Enable(False)
        reponse = dlg.ShowModal() 
        dlg.Destroy()
        # Création d'un catégorie
        if reponse == 100 : 
            dlg = DLG_Saisie_categorie_question.Dialog(self, type=self.type, IDcategorie=None)
            if dlg.ShowModal() == wx.ID_OK :
                IDcategorie = dlg.GetIDcategorie() 
                self.MAJ(selection=("categorie", IDcategorie))
            dlg.Destroy()
        # Création d'une question
        if reponse == 200 : 
            # Vérifie avant qu'une catégorie existe bien
            if len(self.dictCategories) == 0 :
                dlg = wx.MessageDialog(self, _(u"Vous devez d'abord créer au moins une catégorie !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = DLG_Saisie_question.Dialog(self, type=self.type, IDquestion=None)
            if dlg.ShowModal() == wx.ID_OK :
                IDquestion = dlg.GetIDquestion() 
                self.MAJ(selection=("question", IDquestion))
            dlg.Destroy()
    
    def Modifier(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_questionnaires", "modifier") == False : return
        item = self.GetSelection() 
        resultat = self.IdentificationBranche(item) 
        if resultat == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ligne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Catégorie
        if resultat["type"] == "categorie" :
            dlg = DLG_Saisie_categorie_question.Dialog(self, type=self.type, IDcategorie=resultat["ID"])
            if dlg.ShowModal() == wx.ID_OK :
                self.MAJ(selection=("categorie", resultat["ID"]))
            dlg.Destroy()
        # Question
        if resultat["type"] == "question" :
            dlg = DLG_Saisie_question.Dialog(self, type=self.type, IDquestion=resultat["ID"])
            if dlg.ShowModal() == wx.ID_OK :
                self.MAJ(selection=("question", resultat["ID"]))
            dlg.Destroy()
        
    def Supprimer(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_questionnaires", "supprimer") == False : return
        item = self.GetSelection() 
        resultat = self.IdentificationBranche(item) 
        if resultat == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ligne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Catégorie
        if resultat["type"] == "categorie" :
            IDcategorie = resultat["ID"]
            listeQuestionRattachees = self.dictCategories[IDcategorie]["questions"]
            if len(listeQuestionRattachees) > 0 :
                dlg = wx.MessageDialog(self, _(u"Cette catégorie comporte déjà %d question(s).\n\nVous devez déjà les supprimer avant de supprimer la catégorie.") % len(listeQuestionRattachees), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
            # Confirmation
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette catégorie ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return 
            # Supprime la catégorie
            DB = GestionDB.DB()
            DB.ReqDEL("questionnaire_categories", "IDcategorie", IDcategorie)
            DB.Close() 
            self.MAJ()
        # Question
        if resultat["type"] == "question" :
            IDquestion = resultat["ID"]
            index = resultat["index"]
            IDcategorie = resultat["IDcategorie"]

            # Vérifie si cette question apparait dans des filtres
            DB = GestionDB.DB()
            req = """SELECT IDfiltre, IDquestion
            FROM questionnaire_filtres
            WHERE IDquestion=%d
            ;""" % IDquestion
            DB.ExecuterReq(req)
            listeReponses = DB.ResultatReq()     
            if len(listeReponses) > 0 :
                dlg = wx.MessageDialog(self, _(u"%d filtres sont déjà associés à cette question.\n\nVous devez déjà les supprimer avant de supprimer la question.") % len(listeReponses), _(u"Suppression impossible"), wx.OK | wx.ICON_EXCLAMATION)
                dlg.ShowModal()
                dlg.Destroy()
                return
                
            # Vérifie si cette question a des réponses
            req = """SELECT IDindividu, IDfamille
            FROM questionnaire_reponses
            WHERE IDquestion=%d
            ;""" % IDquestion
            DB.ExecuterReq(req)
            listeReponses = DB.ResultatReq()     
            DB.Close() 
            if len(listeReponses) > 0 :
                dlg = wx.MessageDialog(self, _(u"%d fiches comportent une réponse à cette question.\nSi vous supprimez cette question, les réponses le seront également.\n\nSouhaitez-vous vraiment supprimer cette question ?") % len(listeReponses), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_INFORMATION)
                reponse = dlg.ShowModal()
                dlg.Destroy()
                if reponse != wx.ID_YES :
                    return 

            # Confirmation
            dlg = wx.MessageDialog(self, _(u"Souhaitez-vous vraiment supprimer cette question ?"), _(u"Suppression"), wx.YES_NO|wx.NO_DEFAULT|wx.CANCEL|wx.ICON_QUESTION)
            reponse = dlg.ShowModal()
            dlg.Destroy()
            if reponse != wx.ID_YES :
                return 
            # Suppression
            DB = GestionDB.DB()
            DB.ReqDEL("questionnaire_questions", "IDquestion", IDquestion)
            DB.ReqDEL("questionnaire_reponses", "IDquestion", IDquestion)
            DB.ReqDEL("questionnaire_choix", "IDquestion", IDquestion)
            DB.Close() 
            self.MAJ()
        
    def Monter(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_questionnaires", "modifier") == False : return
        item = self.GetSelection() 
        resultat = self.IdentificationBranche(item) 
        if resultat == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ligne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Catégorie
        if resultat["type"] == "categorie" :
            IDcategorie = resultat["ID"]
            index = resultat["index"]
            if index == 0 : return
            self.BougerCategorie(IDcategorie, index, sens=-1)
            self.MAJ(selection=("categorie", IDcategorie))
        # Question
        if resultat["type"] == "question" :
            IDquestion = resultat["ID"]
            index = resultat["index"]
            IDcategorie = resultat["IDcategorie"]
            if index == 0 : return
            self.BougerQuestion(IDquestion, IDcategorie, index, sens=-1)
            self.MAJ(selection=("question", IDquestion))
            
    def Descendre(self, event=None):
        if UTILS_Utilisateurs.VerificationDroitsUtilisateurActuel("parametrage_questionnaires", "modifier") == False : return
        item = self.GetSelection() 
        resultat = self.IdentificationBranche(item) 
        if resultat == None :
            dlg = wx.MessageDialog(self, _(u"Vous n'avez sélectionné aucune ligne !"), _(u"Erreur"), wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # Catégorie
        if resultat["type"] == "categorie" :
            IDcategorie = resultat["ID"]
            index = resultat["index"]
            if index == len(self.listeIDcategorie) - 1 : return
            self.BougerCategorie(IDcategorie, index, sens=+1)
            self.MAJ(selection=("categorie", IDcategorie))
        # Question
        if resultat["type"] == "question" :
            IDquestion = resultat["ID"]
            index = resultat["index"]
            IDcategorie = resultat["IDcategorie"]
            if index == len(self.dictCategories[IDcategorie]["questions"]) - 1 : return
            self.BougerQuestion(IDquestion, IDcategorie, index, sens=+1)
            self.MAJ(selection=("question", IDquestion))
    
    def BougerCategorie(self, IDcategorie=None, index=None, sens=-1):
        DB = GestionDB.DB()
        DB.ReqMAJ("questionnaire_categories", [("ordre", index + sens),], "IDcategorie", IDcategorie)
        DB.ReqMAJ("questionnaire_categories", [("ordre", index),], "IDcategorie", self.listeIDcategorie[index + sens])
        DB.Close()

    def BougerQuestion(self, IDquestion=None, IDcategorie=None, index=None, sens=-1):
        DB = GestionDB.DB()
        DB.ReqMAJ("questionnaire_questions", [("ordre", index + sens),], "IDquestion", IDquestion)
        DB.ReqMAJ("questionnaire_questions", [("ordre", index),], "IDquestion", self.dictCategories[IDcategorie]["questions"][index + sens].IDquestion)
        DB.Close()

    def SauvegardeDocuments(self, IDquestion=None, IDreponse=None):
        """ Sauvegarde du porte-documents """
        nbreDocuments = 0
        for IDcategorie in self.listeIDcategorie :
            for track in self.dictCategories[IDcategorie]["questions"] :
                if track.controle == "documents" and track.IDquestion == IDquestion :
                    ctrl_vignettes = track.ctrl
                    nbreDocuments = ctrl_vignettes.Sauvegarde(IDreponse)
        return nbreDocuments

    def GetNbreDocuments(self, IDquestion=None):
        nbreDocuments = 0
        for IDcategorie in self.listeIDcategorie :
            for track in self.dictCategories[IDcategorie]["questions"] :
                if track.controle == "documents" and track.IDquestion == IDquestion :
                    nbreDocuments = track.ctrl.GetNbreDocuments() 
        return nbreDocuments
        
        
            
# -------------------------------------------------------------------------------------------------------------------------------------------

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1, name="test1")
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = CTRL(panel, type="individu", menuActif=True, afficherInvisibles=True)
        self.ctrl.MAJ() 
        self.boutonTest = wx.Button(panel, -1, _(u"Test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.boutonTest, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.SetSize((700, 600))
        self.Layout()
        self.CenterOnScreen()
        self.Bind(wx.EVT_BUTTON, self.OnBoutonTest, self.boutonTest)
    
    def OnBoutonTest(self, event):
        dictCategories = self.ctrl.dictCategories
        listeIDcategorie = self.ctrl.listeIDcategorie
        
        for IDcategorie in listeIDcategorie :
            print ">>>", dictCategories[IDcategorie]["label"]
            for track in dictCategories[IDcategorie]["questions"] :
                print (track.label, track.GetValeur(), track.GetValeurStr())
            
        

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "OL TEST")
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
