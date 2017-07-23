#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-12 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------


import Chemins
from Utils.UTILS_Traduction import _
import wx
from Ctrl import CTRL_Bouton_image
import wx.lib.agw.gradientbutton as GB
import wx.lib.platebtn as PB
import textwrap
from wx.lib.wordwrap import wordwrap

if 'phoenix' in wx.PlatformInfo:
    from wx import Control
else :
    from wx import PyControl as Control

ID_OUI = wx.NewId()
ID_NON = wx.NewId()


class CTRL_Bouton_toggle_archive(Control):
    def __init__(self, parent, id=-1, texte=u"", couleurClaire=(255, 255, 255), couleurFoncee=(255, 0, 0), selection=False, taille=wx.DefaultSize):
        Control.__init__(self, parent, id=id, pos=wx.DefaultPosition, size=taille, style=wx.NO_BORDER, name="boutonToggle")
        self.parent = parent
        self.texte = texte
        self.couleurClaire = couleurClaire
        self.couleurFoncee = couleurFoncee
        self.couleurSelection = (0, 255, 0)
        self.selection = selection
        self.survol = False
        self.marge = 10
        self.bestSize = (-1, -1)
        
        # Ajustement de la hauteur du contrôle
        dc = wx.ClientDC(self)
        dc.SetFont(wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
        largeur, hauteur = self.DrawTexte(dc)           
        self.SetClientSize((largeur, hauteur))
        self.SetSize(self.GetClientSize())
        self.SetInitialSize(self.GetClientSize())
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x:None)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        size = self.GetSize()
        marge = 10

        # Dessine le fond
        dc.SetPen(wx.Pen(self.couleurClaire, 0))
        dc.SetBrush(wx.Brush(self.couleurClaire))
        dc.DrawRectangle(0, 0, size.x, size.y)
        
        # Dessine le rectangle arrondi
        if self.survol == True :
            couleurTrait = (0, 0, 0)
        else :
            couleurTrait = self.couleurFoncee
        dc.SetPen(wx.Pen(couleurTrait, 1))
        dc.SetBrush(wx.Brush(self.couleurFoncee))
        dc.DrawRoundedRectangle(0, 0, size.x, size.y-1, 35)

        self.DrawTexte(dc)
    
    def DrawTexte(self, dc):
        tailleDC = dc.GetSize() 
        
        # Dessine l'image
        if self.selection == True :
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Droite_48x48.png"), wx.BITMAP_TYPE_ANY)
            dc.SetTextForeground((0, 0, 0))
        else :
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Droite_gris_48x48.png"), wx.BITMAP_TYPE_ANY)
            dc.SetTextForeground(self.couleurClaire)
        tailleImage = bmp.GetSize()
        x = self.marge
        dc.DrawBitmap(bmp, x, x)

        # Dessine le texte
        font = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2")
        dc.SetFont(font)
        largeurTexte = 460#tailleDC[0] - self.marge - tailleImage[0] - self.marge - self.marge
        self.texte = wordwrap(self.texte, largeurTexte, dc, breakLongWords=True)
        if 'phoenix' in wx.PlatformInfo:
            largeur, hauteur, hauteurLigne = dc.GetFullMultiLineTextExtent(self.texte)
        else :
            largeur, hauteur, hauteurLigne = dc.GetMultiLineTextExtent(self.texte)
        dc.SetBrush(wx.Brush((255, 0, 0)))
        dc.DrawRoundedRectangle(x+tailleImage[0]+self.marge, self.marge, largeurTexte, hauteur, 1)

        dc.DrawLabel(self.texte, wx.Rect(x+tailleImage[0]+self.marge, self.marge, largeurTexte, hauteur))
        
        largeurTotale = tailleDC[0]
        hauteurTotale = self.marge + hauteur + self.marge
        return largeurTotale, hauteurTotale

    def Toggle(self, event=None):
        self.selection = not self.selection
        self.Refresh() 
    
    def OnMotion(self, event=None):
        self.survol = True
        self.Refresh() 

    def OnLeaveWindow(self, event=None):
        self.survol = False
        self.Refresh() 
    
    def Selection(self):
        self.selection = True
        self.Refresh() 

    def Deselection(self):
        self.selection = False
        self.Refresh() 

    def AcceptsFocus(self):
        return False

    def DoGetBestSize(self):
        return self.bestSize

    def ShouldInheritColours(self): 
        return False


#----------------------------------------------------------------------------------------------------------------------------------------------------------

class CTRL_Bouton_toggle(wx.Panel):
    def __init__(self, parent, id=-1, texte=u"", couleurClaire=(255, 255, 255), couleurFoncee=(255, 0, 0), selection=False, taille=(300, -1)):
        wx.Panel.__init__(self, parent, id=id, size=taille, style=wx.NO_BORDER)
        self.parent = parent
        self.texte = texte
        self.couleurClaire = couleurClaire
        self.couleurFoncee = couleurFoncee
        self.couleurSelection = (0, 255, 0)
        self.taille = taille
        self.selection = selection
        self.survol = False
        self.marge = 10

        # Ajustement de la hauteur du contrôle
        dc = wx.ClientDC(self)
        dc.SetFont(wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
        largeur, hauteur = self.DrawTexte(dc)   
        self.SetMinSize((largeur, hauteur))        
        self.SetClientSize((largeur, hauteur))
        self.SetSize(self.GetClientSize())
        
        # Binds
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x:None)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        size = self.GetSize()
        
        # Dessine le fond
        dc.SetPen(wx.Pen(self.couleurClaire, 0))
        dc.SetBrush(wx.Brush(self.couleurClaire))
        dc.DrawRectangle(0, 0, size.x, size.y)
        
        # Dessine le rectangle arrondi
        if self.survol == True :
            couleurTrait = (0, 0, 0)
        else :
            couleurTrait = self.couleurFoncee
        dc.SetPen(wx.Pen(couleurTrait, 1))
        dc.SetBrush(wx.Brush(self.couleurFoncee))
        dc.DrawRoundedRectangle(0, 0, size.x, size.y, 35)
        
        self.DrawTexte(dc)
    
    def DrawTexte(self, dc):
        tailleDC = dc.GetSize() 
        
        # Dessine l'image
        if self.selection == True :
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Droite_48x48.png"), wx.BITMAP_TYPE_ANY)
            dc.SetTextForeground((255, 255, 255))
        else :
            bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Droite_gris_48x48.png"), wx.BITMAP_TYPE_ANY)
            dc.SetTextForeground(self.couleurClaire)
        tailleImage = bmp.GetSize()
        x = self.marge
        dc.DrawBitmap(bmp, x, x)

        # Dessine le texte
        font = wx.Font(24, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2")
        dc.SetFont(font)
        largeurTexte = 520#tailleDC[0] - self.marge - tailleImage[0] - self.marge - self.marge
        self.texte = wordwrap(self.texte, largeurTexte, dc, breakLongWords=True)
        if 'phoenix' in wx.PlatformInfo:
            largeur, hauteur, hauteurLigne = dc.GetFullMultiLineTextExtent(self.texte)
        else :
            largeur, hauteur, hauteurLigne = dc.GetMultiLineTextExtent(self.texte)
        # Cadre pour les tests de taille
##        dc.SetBrush(wx.Brush((255, 0, 0)))
##        dc.DrawRoundedRectangle(x+tailleImage[0]+self.marge, self.marge, largeurTexte, hauteur, 1)

        dc.DrawLabel(self.texte, wx.Rect(x+tailleImage[0]+self.marge, self.marge, largeurTexte, hauteur))
        
        largeurTotale = tailleDC[0]
        hauteurTotale = self.marge + hauteur + self.marge * 2
        return largeurTotale, hauteurTotale

    def Toggle(self, event=None):
        self.selection = not self.selection
        self.Refresh() 
    
    def OnMotion(self, event=None):
        self.survol = True
        self.Refresh() 

    def OnLeaveWindow(self, event=None):
        self.survol = False
        self.Refresh() 
    
    def Selection(self):
        self.selection = True
        self.Refresh() 

    def Deselection(self):
        self.selection = False
        self.Refresh() 


#----------------------------------------------------------------------------------------------------------------------------------------------------------
        
class CTRL_Choix(wx.Panel):
    def __init__(self, parent, listeItems=[], multiSelection=True, couleurClaire=(255, 255, 255), couleurFoncee=(255, 0, 0), taille=(300, 70)):
        wx.Panel.__init__(self, parent, id=-1, size=taille, style=wx.NO_BORDER)
        self.parent = parent
        self.listeItems = listeItems
        self.multiSelection = multiSelection
        
        # Création des boutons
        sizer = wx.BoxSizer(wx.VERTICAL)
        ID = 1
        listeRaccourcis = []
        self.dictBoutons = {}
        for texte in self.listeItems :
            texte = u"%d. %s" % (ID, texte)
            ctrl = CTRL_Bouton_toggle(self, ID, texte, couleurClaire, couleurFoncee, taille=(300, -1))
            self.dictBoutons[ID] = ctrl
            sizer.Add(ctrl, 0, wx.EXPAND|wx.TOP, 10)
            self.Bind(wx.EVT_MENU, self.OnLeftDown, id=ID)
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
            listeRaccourcis.append((0, ord(str(ID)), ID))
            exec("listeRaccourcis.append((0, wx.WXK_NUMPAD%d, ID))" % ID)
            ID += 1
        
        listeCommandes = [
                (0, ord('N'), ID_NON),
                (0, ord('O'), ID_OUI),
                (0, 13, ID_OUI),
                (0, wx.WXK_BACK, ID_NON),
                (0, ord('A'), ID_NON),
                ]
        for commande in listeCommandes :
            listeRaccourcis.append(commande) 
        
        # Si sélection unique, on sélectionne par défautr le premier
        if self.multiSelection == False and len(self.dictBoutons) > 0 :
            self.dictBoutons[1].Selection() 
        
        self.SetSizer(sizer)
        self.Layout()
        
        # Création des touches raccourcis
        self.SetAcceleratorTable(wx.AcceleratorTable(listeRaccourcis))
    
        
    def OnLeftDown(self, event):
        IDselection = event.GetId() 
        if self.multiSelection == False :
            self.dictBoutons[IDselection].Selection()
            for ID, ctrl in self.dictBoutons.iteritems() :
                if ID != IDselection :
                    ctrl.Deselection() 
        else :
            self.dictBoutons[IDselection].Toggle() 
            if len(self.GetSelections()) == 0 :
                self.parent.ctrl_oui.Enable(False)
            else :
                self.parent.ctrl_oui.Enable(True)
                    
    def SetSelections(self, listeID=[]):
        for ID in listeID :
            self.dictBoutons[ID+1].Selection() 
    
    def GetSelections(self):
        listeID = []
        for ID, ctrl in self.dictBoutons.iteritems() :
            if ctrl.selection == True :
                listeID.append(ID-1)
        return listeID
        
        
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class DLG_Question(wx.Dialog):
    def __init__(self, interface, message=u"", icone=None, couleurClaire=wx.Colour(206, 196, 190), couleurFoncee=wx.Colour(169, 156, 146),
                                        bouton_non=True, texte_non=_(u"Non"), image_non="Efface.png",
                                        bouton_oui=True, texte_oui=_(u"Oui"), image_oui="Validation.png",
                                        listeItems=[], multiSelection=True,
                                        ):
        wx.Dialog.__init__(self, interface, -1, style=wx.NO_BORDER|wx.FRAME_SHAPED|wx.STAY_ON_TOP)
        self.interface = interface
        self.message = message
        self.icone = icone
        self.multiSelection = multiSelection
        
        # Regarde si un thème existe dans l'interface
        if interface != None :
            dictTheme = interface.GetTheme() 
            if dictTheme.has_key("dlg") :
                couleurClaire = dictTheme["dlg"]["couleurClaire"]
                couleurFoncee = dictTheme["dlg"]["couleurFoncee"]
        
        # Propriétés
        self.SetBackgroundColour(couleurClaire)
        self.SetFont(wx.Font(28, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
        
        # Panneau gauche
        self.panel_gauche = wx.Panel(self, -1)
        self.panel_gauche.SetBackgroundColour(couleurFoncee)
        self.panel_gauche.SetMinSize((-1, 600))
        
        # Icone
        if icone == "erreur" : bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Erreur.png"), wx.BITMAP_TYPE_ANY)
        elif icone == "exclamation" : bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Exclamation.png"), wx.BITMAP_TYPE_ANY)
        elif icone == "information" : bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Information.png"), wx.BITMAP_TYPE_ANY)
        elif icone == "question" : bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Question.png"), wx.BITMAP_TYPE_ANY)
        elif icone == "commentaire" : bmp = wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/Commentaire.png"), wx.BITMAP_TYPE_ANY)
        else : bmp = wx.NullBitmap
        self.ctrl_icone = wx.StaticBitmap(self.panel_gauche, -1, bitmap=bmp)
        
        # Panneau droite
##        message = textwrap.wrap(message, 30)
##        self.label_message = wx.StaticText(self, -1, u"\n".join(message))
        self.label_message = wx.StaticText(self, -1, message)
        self.label_message.SetMinSize((600, 200))
        
        # Boutons Toggle
        self.ctrl_choix = CTRL_Choix(self, listeItems=listeItems, multiSelection=multiSelection, couleurClaire=couleurClaire, couleurFoncee=couleurFoncee, taille=(500, -1))
        if len(listeItems) == 0 :
            self.ctrl_choix.Enable(False) 
        
        # Boutons
        self.ctrl_non = GB.GradientButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/%s" % image_non), wx.BITMAP_TYPE_ANY), u" %s " % texte_non)
        self.ctrl_non.SetTopStartColour(wx.Colour(228, 98, 79))
        self.ctrl_non.SetTopEndColour(wx.Colour(223, 70, 25))
        self.ctrl_non.SetBottomStartColour(wx.Colour(223, 70, 25))
        self.ctrl_non.SetBottomEndColour(wx.Colour(228, 98, 79))
        self.ctrl_non.SetPressedTopColour(wx.Colour(195, 76, 70))
        self.ctrl_non.SetPressedBottomColour(wx.Colour(195, 76, 70))
        self.ctrl_non.Show(bouton_non)
        
        self.ctrl_oui = GB.GradientButton(self, -1, wx.Bitmap(Chemins.GetStaticPath("Images/Badgeage/%s" % image_oui), wx.BITMAP_TYPE_ANY), u" %s " % texte_oui)
        self.ctrl_oui.SetTopStartColour(wx.Colour(159, 207, 80))
        self.ctrl_oui.SetTopEndColour(wx.Colour(131, 193, 36))
        self.ctrl_oui.SetBottomStartColour(wx.Colour(131, 193, 36))
        self.ctrl_oui.SetBottomEndColour(wx.Colour(159, 207, 80))
        self.ctrl_oui.SetPressedTopColour(wx.Colour(60, 160, 84))
        self.ctrl_oui.SetPressedBottomColour(wx.Colour(60, 160, 84))
        self.ctrl_oui.Show(bouton_oui)
        
        # Désactive la touche OUI si multiSelection activée
        if len(listeItems) > 0 and self.multiSelection == True :
            self.ctrl_oui.Enable(False)

        # Texte d'attente
        self.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "MS Shell Dlg 2"))
        self.label_attente = wx.StaticText(self, -1, _(u"Veuillez patienter..."))
        self.label_attente.SetForegroundColour(couleurFoncee)
        if bouton_non == True or bouton_oui == True :
            self.label_attente.Show(False) 
            
        # Binds
        self.Bind(wx.EVT_BUTTON, self.OnBoutonNon, self.ctrl_non)
        self.Bind(wx.EVT_BUTTON, self.OnBoutonOui, self.ctrl_oui)

        # Touches de raccourcis
        if bouton_non == True or bouton_oui == True :
            self.Bind(wx.EVT_MENU, self.OnBoutonNon, id=ID_NON)
            self.Bind(wx.EVT_MENU, self.OnBoutonOui, id=ID_OUI)
            accel_tbl = wx.AcceleratorTable([
                (0, ord('N'), ID_NON),
                (0, ord('O'), ID_OUI),
                (0, 13, ID_OUI),
                (0, wx.WXK_BACK, ID_NON),
                (0, ord('A'), ID_NON),
                ])
            self.SetAcceleratorTable(accel_tbl)

        # Layout
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)
        
        # Panneau gauche
        grid_sizer_gauche = wx.FlexGridSizer(rows=3, cols=1, vgap=10, hgap=10)
        grid_sizer_gauche.Add(self.ctrl_icone, 0, wx.ALL, 20)
        self.panel_gauche.SetSizer(grid_sizer_gauche)
        grid_sizer_base.Add(self.panel_gauche, 1, wx.EXPAND, 0)
        
        # Panneau droit
        grid_sizer_droit = wx.FlexGridSizer(rows=4, cols=1, vgap=10, hgap=10)
        grid_sizer_droit.Add(self.label_message, 0, 0, 0)
        
        # Boutons de Choix
        grid_sizer_droit.Add(self.ctrl_choix, 1, wx.EXPAND|wx.TOP, 10)
        
        # Bouton Veuillez patienter
        grid_sizer_droit.Add(self.label_attente, 0, wx.ALIGN_RIGHT, 0)
        
        # Boutons
        grid_sizer_boutons = wx.FlexGridSizer(rows=1, cols=3, vgap=20, hgap=20)
        grid_sizer_boutons.Add((1, 1), 0, wx.EXPAND, 0)
        grid_sizer_boutons.Add(self.ctrl_non, 0, wx.ALL, 0)
        grid_sizer_boutons.Add(self.ctrl_oui, 0, wx.ALL, 0)
        grid_sizer_boutons.AddGrowableCol(0)
        grid_sizer_droit.Add(grid_sizer_boutons, 1, wx.EXPAND|wx.TOP, 20)
        
        grid_sizer_droit.AddGrowableRow(1)
        grid_sizer_droit.AddGrowableCol(0)
        grid_sizer_base.Add(grid_sizer_droit, 1, wx.EXPAND|wx.ALL, 20)
        
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        grid_sizer_base.AddGrowableRow(0)
        grid_sizer_base.AddGrowableCol(1)
        self.Layout()
        self.CenterOnScreen() 
        
        # Création de la forme de la fenêtre
        size = self.GetSize()
        bmp = wx.EmptyBitmap(size.x, size.y)
        dc = wx.BufferedDC(None, bmp)
        dc.SetBackground(wx.Brush(wx.Colour(0, 0, 0), wx.SOLID))
        dc.Clear()
        dc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))
        dc.DrawRoundedRectangle(0, 0, size.x, size.y, 20)                
        r = wx.RegionFromBitmapColour(bmp, wx.Colour(0, 0, 0))
        self.reg = r
        if wx.Platform == "__WXGTK__":
            self.Bind(wx.EVT_WINDOW_CREATE, self.SetBusyShape)
        else:
            self.SetBusyShape()
        
        # Synthèse vocale
        wx.CallAfter(self.Vocal)

    def SetBusyShape(self, event=None):
        self.SetShape(self.reg)
        if event:
            # GTK only
            event.Skip()
    
    def OnBoutonNon(self, event):
        self.EndModal(wx.ID_NO)

    def OnBoutonOui(self, event):
        self.EndModal(wx.ID_YES)
    
    def Vocal(self):
        """ Synthèse vocale """
        try :
            if self.interface != None :
                if self.interface.dictProcedure["parametres"]["vocal"] == 1 :
                    self.interface.vocal.Parle(self.message)
        except Exception, err:
            pass
            
# --------------------------------------------------------------------------------------------------------------------------------------

class DLG_Choix(DLG_Question):
    """ DLG qui propose différents choix """
    def __init__(self, interface=None, message="", listeItems=[], multiSelection=True):
        DLG_Question.__init__(self, interface, message, icone="question", texte_non=_(u"Annuler"), texte_oui=_(u"Ok"), 
                                            listeItems=listeItems, multiSelection=multiSelection)
        
    def GetSelections(self):
        return self.ctrl_choix.GetSelections()
    
    def SetSelections(self, listeIndex=[]):
        self.ctrl_choix.SetSelections(listeIndex)



# --------------------------------------------------------------------------------------------------------------------------------------

class DLG_Message(object):
    """ DLG pour afficher un message sur un temps donné (en secondes) """
    def __init__(self, interface=None, message="", icone=None, secondes=2):
        
        if interface.importationManuelle != False :
            #print ("Message cache =", message)
            return
        
        self.dlg = DLG_Question(interface, message, icone, bouton_oui=False, bouton_non=False)
        self.dlg.SetCursor(wx.HOURGLASS_CURSOR)
        self.dlg.Show()
        wx.Yield()
        for indx in xrange(secondes):
            wx.MilliSleep(1000)
        self.dlg.Show(False)
        self.dlg.Destroy() 

# --------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    
    # Version MESSAGE
##    dlg1 = DLG_Message(None, message="Bonjour Kévin", icone="commentaire", secondes=2)
    
    # Version QUESTION
##    dlg = DLG_Question(None, message=_(u"Restes-tu manger à la cantine ce midi ?"), icone="question")
##    if dlg.ShowModal() == wx.ID_YES :
##        print "oui"
##    else :
##        print "non"
##    dlg.Destroy()

    # Version CHOIX
    listeItems = [_(u"Choix 1"), _(u"Choix 2"), _(u"Choix 3")]
    dlg = DLG_Choix(None, message=_(u"Quel choix ?"), listeItems=listeItems, multiSelection=False)
    if dlg.ShowModal() == wx.ID_YES :
        print dlg.GetSelections()  
    dlg.Destroy()

    app.MainLoop()
