#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wxSchedulerCore import *


class wxSchedulerPrint( wxSchedulerCore ):

	def __init__( self, dc, joursSpeciaux=None, reglages={} ):
		super( wxSchedulerPrint, self ).__init__()
		self.joursSpeciaux = joursSpeciaux
		self.reglages = reglages
		self.SetDc( dc )
		
	def Draw( self, page ):
		"""
		Draw object on DC
		"""
		self.DrawBuffer()
		if page is not None:
			self.pageNumber = page
			self.DrawBuffer()

		self._dc.DrawBitmap(self._bitmap, int(self.reglages["marge_gauche"]), int(self.reglages["marge_haut"]), False)
		
	def GetSize( self ):
		"""
		Return a wx.Size() object representing the page's size
		"""
		return wx.Size(self.GetDc().GetSize()[0] - self.reglages["marge_droite"] - self.reglages["marge_gauche"], self.GetDc().GetSize()[1] - self.reglages["marge_bas"] - self.reglages["marge_haut"])

	def Refresh( self ):
		pass
