#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#-----------------------------------------------------------
# Application :    Noethys, gestion multi-activit�s
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#-----------------------------------------------------------


from UTILS_Traduction import _
import wx
import CTRL_Bouton_image
import wx.lib.masked as masked

    
class NumSecu(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.ctrl_numsecu = masked.TextCtrl(self, -1, "", style=wx.TE_CENTRE, mask = "# ## ## #N ### ### ##") 
        self.image_numsecu = wx.StaticBitmap(self, -1, wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG), size=(16, 16))
        self.remplissageEnCours = False
        
        self.__set_properties()
        self.__do_layout()
        
        self.ctrl_numsecu.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

    def __set_properties(self):
        texteNumSecu = u"""
        Num�ro de s�curit� sociale : A BB CC DD EEE FFF GG
        
        A : Sexe (1=homme | 2=femme)
        BB : Ann�e de naissance
        CC : Mois de naissance
        DD : D�partement de naissance (99 si n� � l'�tranger)
        EEE : Code INSEE de la commune de naissance ou du pays si n� � l'�tranger
        FFF : Num�ro d'ordre INSEE
        GG : Cl�
        """
        self.ctrl_numsecu.SetToolTipString(texteNumSecu)
        self.ctrl_numsecu.SetMinSize((170, -1))

    def __do_layout(self):
        grid_sizer_base = wx.FlexGridSizer(rows=1, cols=2, vgap=1, hgap=1)
        grid_sizer_base.Add(self.ctrl_numsecu, 1, wx.EXPAND|wx.ALL, 0)
        grid_sizer_base.Add(self.image_numsecu, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0)
        self.SetSizer(grid_sizer_base)
        grid_sizer_base.Fit(self)
        self.Layout()
        self.grid_sizer_base = grid_sizer_base
        
    def SetValue(self, numSecu=""):
        if numSecu == None : return
        self.remplissageEnCours = True
        self.ctrl_numsecu.SetValue(numSecu)
        self.TestValidite(avecMessagesErreur=False)
        self.remplissageEnCours = False
    
    def GetValue(self):
        return self.ctrl_numsecu.GetValue()

    def OnKillFocus(self, event):
        """ Verifie la validite du numero de securite sociale """
        self.TestValidite() 
        if event != None :
            event.Skip() 
        
    def TestValidite(self, avecMessagesErreur=True):
        texte = self.ctrl_numsecu.GetValue()
        sexe = self.parent.ctrl_civilite.GetSexe()
        datenaiss = self.parent.ctrl_datenaiss.GetValue()
        cp_naiss = self.parent.ctrl_adressenaiss.GetValueCP()
        validation, message = self.ValideNumSecu(texte, sexe, datenaiss, cp_naiss)
        
        # Message si num�ro de s�cu erron�
        if validation == False :
            self.image_numsecu.SetBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
            if self.remplissageEnCours == False and avecMessagesErreur == True:
                wx.MessageBox(message, _(u"Num�ro de s�curit� sociale erron�"))
            
        # Pas de num s�cu saisi
        if validation == None : 
            self.image_numsecu.SetBitmap(wx.Bitmap("Images/16x16/Interdit.png", wx.BITMAP_TYPE_PNG))
        
        #Le num�ro de s�cu est bon
        if validation == True :
            self.image_numsecu.SetBitmap(wx.Bitmap("Images/16x16/Ok.png", wx.BITMAP_TYPE_PNG))
        
        # Actualisation de l'affichage pour le bitmap
        self.grid_sizer_base.Layout()

    def ValideNumSecu(self, texte, sexe, date_naiss, cp_naiss):
        # On v�rifie que tous les chiffres ont �t� donn�s
        texteSansEsp = ""
        for lettre in texte:
            if lettre != " ":
                if lettre in "ABab" :
                    lettre = "0"
                texteSansEsp = texteSansEsp + lettre

        nbreChiffres = len(texteSansEsp)
        if nbreChiffres == 0 :
            return None, ""
        if nbreChiffres < 15 :
            message = _(u"Il manque ") + str(15 - nbreChiffres) + _(u" chiffre(s) au num�ro de s�curit� sociale que vous venez de saisir. Veuillez le v�rifier.")
            return False, message
        if nbreChiffres == 15:
            
            # V�rification avec la civilite
            if sexe == "M" :
                if int(texteSansEsp[0]) != 1:
                    message = _(u"Le num�ro de s�curit� sociale ne correspond pas � la civilit� de la personne (le premier chiffre devrait �tre 1).")
                    return False, message
            if sexe == "F" :
                if int(texteSansEsp[0]) != 2:
                    message = _(u"Le num�ro de s�curit� sociale ne correspond pas � la civilit� de la personne (le premier chiffre devrait �tre 2).")
                    return False, message
                    
            # V�rification avec la date de naissance
            if date_naiss != u"  /  /    " :
                mois = str(date_naiss[3:5])
                annee = str(date_naiss[8:10])

                if annee != str(texteSansEsp[1:3]):
                    message = _(u"Le num�ro de s�curit� sociale ne correspond pas � l'ann�e de naissance de la personne.")
                    return False, message
                elif mois != str(texteSansEsp[3:5]):
                    message = _(u"Le num�ro de s�curit� sociale ne correspond pas au mois de naissance de la personne.")
                    return False, message
                        
            # V�rification avec le d�partement de naissance
            if cp_naiss != u"     " and cp_naiss != None :
                dep = cp_naiss[0:2]
                if str(dep) != str(texteSansEsp[5:7]):
                    message = _(u"Le num�ro de s�curit� sociale ne correspond pas au lieu de naissance de la personne.")
                    return False, message
            
            # V�rification de la cl�
            cle = int((texteSansEsp[13:15]))
            cle_calculee = 97 - (int(texteSansEsp[:13]) % 97)
            if cle != cle_calculee :
                message = _(u"La cl� du num�ro de s�curit� sociale ne semble pas coh�rente. \nD'apr�s mes calculs, la bonne cl� devrait �tre %02d. \n\nVeuillez v�rifier votre saisie...") % cle_calculee
                return False, message
            
            # Le num de s�cu est ok
            return True, ""
        
        
        

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        panel = wx.Panel(self, -1)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(panel, 1, wx.ALL|wx.EXPAND)
        self.SetSizer(sizer_1)
        self.ctrl = NumSecu(panel)
        self.bouton = wx.Button(panel, -1, _(u"Test"))
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.ctrl, 1, wx.ALL|wx.EXPAND, 4)
        sizer_2.Add(self.bouton, 0, wx.ALL|wx.EXPAND, 4)
        panel.SetSizer(sizer_2)
        self.Layout()
        self.CentreOnScreen()

if __name__ == '__main__':
    app = wx.App(0)
    #wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "TEST", size=(800, 400))
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()