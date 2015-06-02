#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#------------------------------------------------------------------------
# Application :    Noethys, gestion multi-activités
# Site internet :  www.noethys.com
# Auteur:           Ivan LUCAS
# Copyright:       (c) 2010-11 Ivan LUCAS
# Licence:         Licence GNU GPL
#------------------------------------------------------------------------

from __future__ import unicode_literals
from UTILS_Traduction import _
"""
Traduction d'un nombre en texte.
Réalisation : Michel Claveau    http://mclaveau.com
SVP, n'enlevez pas mon adresse/URL ; merci d'avance
Usage : voir les exemples, à la fin du script.
Note : traduction franco-française, avec unités variables, orthographe géré, unités et centièmes.
"""

def tradd(num):
    global t1,t2
    ch=''
    if num==0 :
        ch=''
    elif num<20:
        ch=t1[num]
    elif num>=20:
        if (num>=70 and num<=79)or(num>=90):
            z=int(num/10)-1
        else:
            z=int(num/10)
        ch=t2[z]
        num=num-z*10
        if (num==1 or num==11) and z<8:
            ch=ch+' et'
        if num>0:
            ch=ch+' '+tradd(num)
        else:
            ch=ch+tradd(num)
    return ch


def tradn(num):
    global t1,t2
    ch=''
    flagcent=False
    if num>=1000000000:
        z=int(num/1000000000)
        ch=ch+tradn(z)+' milliard'
        if z>1:
            ch=ch+'s'
        num=num-z*1000000000
    if num>=1000000:
        z=int(num/1000000)
        ch=ch+tradn(z)+' million'
        if z>1:
            ch=ch+'s'
        num=num-z*1000000
    if num>=1000:
        if num>=100000:
            z=int(num/100000)
            if z>1:
                ch=ch+' '+tradd(z)
            ch=ch+' cent'
            flagcent=True
            num=num-z*100000
            if int(num/1000)==0 and z>1:
                ch=ch+'s'
        if num>=1000:
            z=int(num/1000)
            if (z==1 and flagcent) or z>1:
                ch=ch+' '+tradd(z)
            num=num-z*1000
        ch=ch+' mille'
    if num>=100:
        z=int(num/100)
        if z>1:
            ch=ch+' '+tradd(z)
        ch=ch+" cent"
        num=num-z*100
        if num==0 and z>1:
           ch=ch+'s'
    if num>0:
        ch=ch+" "+tradd(num)
    return ch


def trad(nb, unite="euro", decim="centime"):
    global t1,t2
    nb=round(nb,2)
    t1=["","un","deux","trois","quatre","cinq","six","sept","huit","neuf","dix","onze","douze","treize","quatorze","quinze","seize","dix-sept","dix-huit","dix-neuf"]
    t2=["","dix","vingt","trente","quarante","cinquante","soixante","soixante-dix","quatre-vingt","quatre-vingt-dix"]
    z1=int(nb)
    z3=(nb-z1)*100
    z2=int(round(z3,0))
    if z1==0:
        ch=_(u"zéro")
    else:
        ch=tradn(abs(z1))
    if z1>1 or z1<-1:
        if unite!='':
            ch=ch+" "+unite+'s'
    else:
        ch=ch+" "+unite
    if z2>0:
        ch=ch+tradn(z2)
        if z2>1 or z2<-1:
            if decim!='':
                ch=ch+" "+decim+'s'
        else:
            ch=ch+" "+decim
    if nb<0:
        ch="moins "+ch
    ch = ch.strip() 
    return ch



if __name__=='__main__':
    print ''
    print 'Exemples :'
    print '--------  '
    print 812000, trad(812000)
    print 183.93,trad(183.93)
    print 4199.88,trad(4199.88)
    print 613812345651.01,trad(613812345651.01)
    print 1,trad(1)
    print 2.2,trad(2.2)
    print 12.30,trad(12.30,'heure','minute')
    print 12.30,trad(12.30,'heure','')
    print 1.8,trad(1.8,u'mètre','')
    print 2.5,trad(2.5,'litre','')
    print 3.5,trad(3.5,decim='')
    print 300,trad(300)
    print 301,trad(301)
    print 1000,trad(1000)
    print 1001,trad(1001)
    print 1400,trad(1400)
    print 1401,trad(1401)
    print 0,trad(0)