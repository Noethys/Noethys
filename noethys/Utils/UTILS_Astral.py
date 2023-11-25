# -*- coding: utf-8 -*-
#
# Copyright 2009-2011, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The :mod:`astral` module provides the means to calculate dawn, sunrise,
solar noon, sunset, dusk and rahukaalam times, plus solar azimuth and elevation,
for specific cities or at a specific latitude/longitude. It can also calculate
the moon phase for a specific date. 

The module provides 2 main classes :class:`Astral` and :class:`City`.

:class:`Astral`
    Has 2 main responsibilities

    * Calculates the events in the UTC timezone.
    * Holds a dictionary of City classes
    
:class:`City`
    Holds information about a city and provides functions to calculate
    the event times for the city in the correct time zone.

For example

>>> from astral import *
>>> a = Astral()
>>> city = a['London']
>>> print('Information for %s' % city.name)
Information for London
>>> timezone = city.timezone
>>> print('Timezone: %s' % timezone)
Timezone: Europe/London
>>> print('Latitude: %.02f; Longitude: %.02f' % (city.latitude, city.longitude))
Latitude: 51.60; Longitude: 0.05
>>> sun = city.sun(local=True)
>>> print('Dawn:    %s' % str(sun['dawn']))
Dawn:    2009-04-22 05:12:56+01:00
"""

import datetime
from math import cos, sin, tan, acos, asin, atan2, floor, ceil
from math import radians, degrees, pow

try:
    import pytz
except ImportError:
    raise ImportError(('The astral module requires the '
        'pytz module to be available.'))

__all__ = ['City','Astral','AstralError']

__version__ = "0.6"
__author__ = "Simon Kennedy <code@sffjunkie.co.uk>"

_CITY_INFO = """Abu Dhabi,UAE,24Â°28'N,54Â°22'E,Asia/Dubai
Abu Dhabi,United Arab Emirates,24Â°28'N,54Â°22'E,Asia/Dubai
Abuja,Nigeria,09Â°05'N,07Â°32'E,Africa/Lagos
Accra,Ghana,05Â°35'N,00Â°06'W,Africa/Accra
Addis Ababa,Ethiopia,09Â°02'N,38Â°42'E,Africa/Addis_Ababa
Adelaide,Australia,34Â°56'S,138Â°36'E,Australia/Adelaide
Al Jubail,Saudi Arabia,25Â°24'N,49Â°39'W,Asia/Riyadh
Algiers,Algeria,36Â°42'N,03Â°08'E,Africa/Algiers
Amman,Jordan,31Â°57'N,35Â°52'E,Asia/Amman
Amsterdam,Netherlands,52Â°23'N,04Â°54'E,Europe/Amsterdam
Andorra la Vella,Andorra,42Â°31'N,01Â°32'E,Europe/Andorra
Ankara,Turkey,39Â°57'N,32Â°54'E,Europe/Istanbul
Antananarivo,Madagascar,18Â°55'S,47Â°31'E,Indian/Antananarivo
Apia,Samoa,13Â°50'S,171Â°50'W,Pacific/Apia
Ashgabat,Turkmenistan,38Â°00'N,57Â°50'E,Asia/Ashgabat
Asmara,Eritrea,15Â°19'N,38Â°55'E,Africa/Asmara
Astana,Kazakhstan,51Â°10'N,71Â°30'E,Asia/Qyzylorda
Asuncion,Paraguay,25Â°10'S,57Â°30'W,America/Asuncion
Athens,Greece,37Â°58'N,23Â°46'E,Europe/Athens
Baghdad,Iraq,33Â°20'N,44Â°30'E,Asia/Baghdad
Baku,Azerbaijan,40Â°29'N,49Â°56'E,Asia/Baku
Bamako,Mali,12Â°34'N,07Â°55'W,Africa/Bamako
Bandar Seri Begawan,Brunei Darussalam,04Â°52'N,115Â°00'E,Asia/Brunei
Bangkok,Thailand,13Â°45'N,100Â°35'E,Asia/Bangkok
Bangui,Central African Republic,04Â°23'N,18Â°35'E,Africa/Bangui
Banjul,Gambia,13Â°28'N,16Â°40'W,Africa/Banjul
Basse-Terre,Guadeloupe,16Â°00'N,61Â°44'W,America/Guadeloupe
Basseterre,Saint Kitts and Nevis,17Â°17'N,62Â°43'W,America/St_Kitts
Beijing,China,39Â°55'N,116Â°20'E,Asia/Harbin
Beirut,Lebanon,33Â°53'N,35Â°31'E,Asia/Beirut
Belgrade,Yugoslavia,44Â°50'N,20Â°37'E,Europe/Belgrade
Belmopan,Belize,17Â°18'N,88Â°30'W,America/Belize
Berlin,Germany,52Â°30'N,13Â°25'E,Europe/Berlin
Bern,Switzerland,46Â°57'N,07Â°28'E,Europe/Zurich
Bishkek,Kyrgyzstan,42Â°54'N,74Â°46'E,Asia/Bishkek
Bissau,Guinea-Bissau,11Â°45'N,15Â°45'W,Africa/Bissau
Bloemfontein,South Africa,29Â°12'S,26Â°07'E,Africa/Johannesburg
Bogota,Colombia,04Â°34'N,74Â°00'W,America/Bogota
Brasilia,Brazil,15Â°47'S,47Â°55'W,Brazil/East
Bratislava,Slovakia,48Â°10'N,17Â°07'E,Europe/Bratislava
Brazzaville,Congo,04Â°09'S,15Â°12'E,Africa/Brazzaville
Bridgetown,Barbados,13Â°05'N,59Â°30'W,America/Barbados
Brisbane,Australia,27Â°30'S,153Â°01'E,Australia/Brisbane
Brussels,Belgium,50Â°51'N,04Â°21'E,Europe/Brussels
Bucharest,Romania,44Â°27'N,26Â°10'E,Europe/Bucharest
Bucuresti,Romania,44Â°27'N,26Â°10'E,Europe/Bucharest
Budapest,Hungary,47Â°29'N,19Â°05'E,Europe/Budapest
Buenos Aires,Argentina,36Â°30'S,60Â°00'W,America/Argentina/Buenos_Aires
Bujumbura,Burundi,03Â°16'S,29Â°18'E,Africa/Bujumbura
Cairo,Egypt,30Â°01'N,31Â°14'E,Africa/Cairo
Canberra,Australia,35Â°15'S,149Â°08'E,Australia/Canberra
Cape Town,South Africa,33Â°55'S,18Â°22'E,Africa/Johannesburg
Caracas,Venezuela,10Â°30'N,66Â°55'W,America/Caracas
Castries,Saint Lucia,14Â°02'N,60Â°58'W,America/St_Lucia
Cayenne,French Guiana,05Â°05'N,52Â°18'W,America/Cayenne
Charlotte Amalie,United States of Virgin Islands,18Â°21'N,64Â°56'W,America/Virgin
Chisinau,Moldova,47Â°02'N,28Â°50'E,Europe/Chisinau
Conakry,Guinea,09Â°29'N,13Â°49'W,Africa/Conakry
Copenhagen,Denmark,55Â°41'N,12Â°34'E,Europe/Copenhagen
Cotonou,Benin,06Â°23'N,02Â°42'E,Africa/Porto-Novo
Dakar,Senegal,14Â°34'N,17Â°29'W,Africa/Dakar
Damascus,Syrian Arab Republic,33Â°30'N,36Â°18'E,Asia/Damascus
Dammam,Saudi Arabia,26Â°30'N,50Â°12'E,Asia/Riyadh
Dhaka,Bangladesh,23Â°43'N,90Â°26'E,Asia/Dhaka
Dili,East Timor,08Â°29'S,125Â°34'E,Asia/Dili
Djibouti,Djibouti,11Â°08'N,42Â°20'E,Africa/Djibouti
Dodoma,United Republic of Tanzania,06Â°08'S,35Â°45'E,Africa/Dar_es_Salaam
Doha,Qatar,25Â°15'N,51Â°35'E,Asia/Qatar
Dublin,Ireland,53Â°21'N,06Â°15'W,Europe/Dublin
Dushanbe,Tajikistan,38Â°33'N,68Â°48'E,Asia/Dushanbe
Fort-de-France,Martinique,14Â°36'N,61Â°02'W,America/Martinique
Freetown,Sierra Leone,08Â°30'N,13Â°17'W,Africa/Freetown
Funafuti,Tuvalu,08Â°31'S,179Â°13'E,Pacific/Funafuti
Gaborone,Botswana,24Â°45'S,25Â°57'E,Africa/Gaborone
George Town,Cayman Islands,19Â°20'N,81Â°24'W,America/Cayman
Georgetown,Guyana,06Â°50'N,58Â°12'W,America/Guyana
Guatemala,Guatemala,14Â°40'N,90Â°22'W,America/Guatemala
Hanoi,Viet Nam,21Â°05'N,105Â°55'E,Asia/Saigon
Harare,Zimbabwe,17Â°43'S,31Â°02'E,Africa/Harare
Havana,Cuba,23Â°08'N,82Â°22'W,America/Havana
Helsinki,Finland,60Â°15'N,25Â°03'E,Europe/Helsinki
Hobart,Tasmania,42Â°53'S,147Â°19'E,Australia/Hobart
Honiara,Solomon Islands,09Â°27'S,159Â°57'E,Pacific/Guadalcanal
Islamabad,Pakistan,33Â°40'N,73Â°10'E,Asia/Karachi
Jakarta,Indonesia,06Â°09'S,106Â°49'E,Asia/Jakarta
Jerusalem,Israel,31Â°47'N,35Â°12'E,Asia/Jerusalem
Jubail,Saudi Arabia,27Â°02'N,49Â°39'E,Asia/Riyadh
Kabul,Afghanistan,34Â°28'N,69Â°11'E,Asia/Kabul
Kampala,Uganda,00Â°20'N,32Â°30'E,Africa/Kampala
Kathmandu,Nepal,27Â°45'N,85Â°20'E,Asia/Kathmandu
Khartoum,Sudan,15Â°31'N,32Â°35'E,Africa/Khartoum
Kiev,Ukraine,50Â°30'N,30Â°28'E,Europe/Kiev
Kigali,Rwanda,01Â°59'S,30Â°04'E,Africa/Kigali
Kingston,Jamaica,18Â°00'N,76Â°50'W,America/Jamaica
Kingston,Norfolk Island,45Â°20'S,168Â°43'E,Pacific/Norfolk
Kingstown,Saint Vincent and the Grenadines,13Â°10'N,61Â°10'W,America/St_Vincent
Kinshasa,Democratic Republic of the Congo,04Â°20'S,15Â°15'E,Africa/Kinshasa
Koror,Palau,07Â°20'N,134Â°28'E,Pacific/Palau
Kuala Lumpur,Malaysia,03Â°09'N,101Â°41'E,Asia/Kuala_Lumpur
Kuwait,Kuwait,29Â°30'N,48Â°00'E,Asia/Kuwait
La Paz,Bolivia,16Â°20'S,68Â°10'W,America/La_Paz
Libreville,Gabon,00Â°25'N,09Â°26'E,Africa/Libreville
Lilongwe,Malawi,14Â°00'S,33Â°48'E,Africa/Blantyre
Lima,Peru,12Â°00'S,77Â°00'W,America/Lima
Lisbon,Portugal,38Â°42'N,09Â°10'W,Europe/Lisbon
Ljubljana,Slovenia,46Â°04'N,14Â°33'E,Europe/Ljubljana
Lome,Togo,06Â°09'N,01Â°20'E,Africa/Lome
London,England,51Â°30'N,00Â°07'W,Europe/London
Luanda,Angola,08Â°50'S,13Â°15'E,Africa/Luanda
Lusaka,Zambia,15Â°28'S,28Â°16'E,Africa/Lusaka
Luxembourg,Luxembourg,49Â°37'N,06Â°09'E,Europe/Luxembourg
Macau,Macao,22Â°12'N,113Â°33'E,Asia/Macau
Madinah,Saudi Arabia,24Â°28'N,39Â°36'E,Asia/Riyadh
Madrid,Spain,40Â°25'N,03Â°45'W,Europe/Madrid
Makkah,Saudi Arabia,21Â°26'N,39Â°49'E,Asia/Riyadh
Malabo,Equatorial Guinea,03Â°45'N,08Â°50'E,Africa/Malabo
Male,Maldives,04Â°00'N,73Â°28'E,Indian/Maldives
Mamoudzou,Mayotte,12Â°48'S,45Â°14'E,Indian/Mayotte
Managua,Nicaragua,12Â°06'N,86Â°20'W,America/Managua
Manama,Bahrain,26Â°10'N,50Â°30'E,Asia/Bahrain
Manila,Philippines,14Â°40'N,121Â°03'E,Asia/Manila
Maputo,Mozambique,25Â°58'S,32Â°32'E,Africa/Maputo
Maseru,Lesotho,29Â°18'S,27Â°30'E,Africa/Maseru
Masqat,Oman,23Â°37'N,58Â°36'E,Asia/Muscat
Mbabane,Swaziland,26Â°18'S,31Â°06'E,Africa/Mbabane
Mecca,Saudi Arabia,21Â°26'N,39Â°49'E,Asia/Riyadh
Medina,Saudi Arabia,24Â°28'N,39Â°36'E,Asia/Riyadh
Mexico,Mexico,19Â°20'N,99Â°10'W,America/Mexico_City
Minsk,Belarus,53Â°52'N,27Â°30'E,Europe/Minsk
Mogadishu,Somalia,02Â°02'N,45Â°25'E,Africa/Mogadishu
Monrovia,Liberia,06Â°18'N,10Â°47'W,Africa/Monrovia
Montevideo,Uruguay,34Â°50'S,56Â°11'W,America/Montevideo
Moroni,Comoros,11Â°40'S,43Â°16'E,Indian/Comoro
Moscow,Russian Federation,55Â°45'N,37Â°35'E,Europe/Moscow
Moskva,Russian Federation,55Â°45'N,37Â°35'E,Europe/Moscow
Mumbai,India,18Â°58'N,72Â°49'E,Asia/Kolkata
N'Djamena,Chad,12Â°10'N,14Â°59'E,Africa/Ndjamena
Nairobi,Kenya,01Â°17'S,36Â°48'E,Africa/Nairobi
Nassau,Bahamas,25Â°05'N,77Â°20'W,America/Nassau
New Delhi,India,28Â°37'N,77Â°13'E,Asia/Kolkata
Niamey,Niger,13Â°27'N,02Â°06'E,Africa/Niamey
Nicosia,Cyprus,35Â°10'N,33Â°25'E,Asia/Nicosia
Nouakchott,Mauritania,20Â°10'S,57Â°30'E,Africa/Nouakchott
Noumea,New Caledonia,22Â°17'S,166Â°30'E,Pacific/Noumea
Nuku'alofa,Tonga,21Â°10'S,174Â°00'W,Pacific/Tongatapu
Nuuk,Greenland,64Â°10'N,51Â°35'W,America/Godthab
Oranjestad,Aruba,12Â°32'N,70Â°02'W,America/Aruba
Oslo,Norway,59Â°55'N,10Â°45'E,Europe/Oslo
Ottawa,Canada,45Â°27'N,75Â°42'W,US/Eastern
Ouagadougou,Burkina Faso,12Â°15'N,01Â°30'W,Africa/Ouagadougou
P'yongyang,Democratic People's Republic of Korea,39Â°09'N,125Â°30'E,Asia/Pyongyang
Pago Pago,American Samoa,14Â°16'S,170Â°43'W,Pacific/Pago_Pago
Palikir,Micronesia,06Â°55'N,158Â°09'E,Pacific/Ponape
Panama,Panama,09Â°00'N,79Â°25'W,America/Panama
Papeete,French Polynesia,17Â°32'S,149Â°34'W,Pacific/Tahiti
Paramaribo,Suriname,05Â°50'N,55Â°10'W,America/Paramaribo
Paris,France,48Â°50'N,02Â°20'E,Europe/Paris
Perth,Australia,31Â°56'S,115Â°50'E,Australia/Perth
Phnom Penh,Cambodia,11Â°33'N,104Â°55'E,Asia/Phnom_Penh
Port Moresby,Papua New Guinea,09Â°24'S,147Â°08'E,Pacific/Port_Moresby
Port-Vila,Vanuatu,17Â°45'S,168Â°18'E,Pacific/Efate
Port-au-Prince,Haiti,18Â°40'N,72Â°20'W,America/Port-au-Prince
Porto-Novo,Benin,06Â°23'N,02Â°42'E,Africa/Porto-Novo
Prague,Czech Republic,50Â°05'N,14Â°22'E,Europe/Prague
Praia,Cape Verde,15Â°02'N,23Â°34'W,Atlantic/Cape_Verde
Pretoria,South Africa,25Â°44'S,28Â°12'E,Africa/Johannesburg
Quito,Ecuador,00Â°15'S,78Â°35'W,America/Guayaquil
Reykjavik,Iceland,64Â°10'N,21Â°57'W,Atlantic/Reykjavik
Riga,Latvia,56Â°53'N,24Â°08'E,Europe/Riga
Riyadh,Saudi Arabia,24Â°41'N,46Â°42'E,Asia/Riyadh
Road Town,British Virgin Islands,18Â°27'N,64Â°37'W,America/Virgin
Rome,Italy,41Â°54'N,12Â°29'E,Europe/Rome
Roseau,Dominica,15Â°20'N,61Â°24'W,America/Dominica
Saint Pierre,Saint Pierre and Miquelon,46Â°46'N,56Â°12'W,America/Miquelon
Saipan,Northern Mariana Islands,15Â°12'N,145Â°45'E,Pacific/Saipan
San Jose,Costa Rica,09Â°55'N,84Â°02'W,America/Costa_Rica
San Juan,Puerto Rico,18Â°28'N,66Â°07'W,America/Puerto_Rico
San Marino,San Marino,43Â°55'N,12Â°30'E,Europe/San_Marino
San Salvador,El Salvador,13Â°40'N,89Â°10'W,America/El_Salvador
Santiago,Chile,33Â°24'S,70Â°40'W,America/Santiago
Santo Domingo,Dominica Republic,18Â°30'N,69Â°59'W,America/Santo_Domingo
Sao Tome,Sao Tome and Principe,00Â°10'N,06Â°39'E,Africa/Sao_Tome
Sarajevo,Bosnia and Herzegovina,43Â°52'N,18Â°26'E,Europe/Sarajevo
Seoul,Republic of Korea,37Â°31'N,126Â°58'E,Asia/Seoul
Skopje,The Former Yugoslav Republic of Macedonia,42Â°01'N,21Â°26'E,Europe/Skopje
Sofia,Bulgaria,42Â°45'N,23Â°20'E,Europe/Sofia
St. Peter Port,Guernsey,49Â°26'N,02Â°33'W,Europe/Guernsey
Stanley,Falkland Islands,51Â°40'S,59Â°51'W,Atlantic/Stanley
Stockholm,Sweden,59Â°20'N,18Â°05'E,Europe/Stockholm
Sucre,Bolivia,16Â°20'S,68Â°10'W,America/La_Paz
Suva,Fiji,18Â°06'S,178Â°30'E,Pacific/Fiji
Sydney,Australia,33Â°53'S,151Â°13'E,Australia/Sydney
T'bilisi,Georgia,41Â°43'N,44Â°50'E,Asia/Tbilisi
Tallinn,Estonia,59Â°22'N,24Â°48'E,Europe/Tallinn
Tarawa,Kiribati,01Â°30'N,173Â°00'E,Pacific/Tarawa
Tashkent,Uzbekistan,41Â°20'N,69Â°10'E,Asia/Tashkent
Tegucigalpa,Honduras,14Â°05'N,87Â°14'W,America/Tegucigalpa
Tehran,Iran,35Â°44'N,51Â°30'E,Asia/Tehran
Thimphu,Bhutan,27Â°31'N,89Â°45'E,Asia/Thimphu
Tirana,Albania,41Â°18'N,19Â°49'E,Europe/Tirane
Tirane,Albania,41Â°18'N,19Â°49'E,Europe/Tirane
Torshavn,Faroe Islands,62Â°05'N,06Â°56'W,Atlantic/Faroe
Tokyo,Japan,35Â°41'N,139Â°41'E,Asia/Tokyo
Tripoli,Libyan Arab Jamahiriya,32Â°49'N,13Â°07'E,Africa/Tripoli
Tunis,Tunisia,36Â°50'N,10Â°11'E,Africa/Tunis
Vaduz,Liechtenstein,47Â°08'N,09Â°31'E,Europe/Vaduz
Valletta,Malta,35Â°54'N,14Â°31'E,Europe/Malta
Vienna,Austria,48Â°12'N,16Â°22'E,Europe/Vienna
Vientiane,Lao People's Democratic Republic,17Â°58'N,102Â°36'E,Asia/Vientiane
Vilnius,Lithuania,54Â°38'N,25Â°19'E,Europe/Vilnius
W. Indies,Antigua and Barbuda,17Â°20'N,61Â°48'W,America/Antigua
Warsaw,Poland,52Â°13'N,21Â°00'E,Europe/Warsaw
Washington DC,USA,39Â°91'N,77Â°02'W,US/Eastern
Wellington,New Zealand,41Â°19'S,174Â°46'E,Pacific/Auckland
Willemstad,Netherlands Antilles,12Â°05'N,69Â°00'W,America/Curacao
Windhoek,Namibia,22Â°35'S,17Â°04'E,Africa/Windhoek
Yamoussoukro,Cote d'Ivoire,06Â°49'N,05Â°17'W,Africa/Abidjan
Yangon,Myanmar,16Â°45'N,96Â°20'E,Asia/Rangoon
Yaounde,Cameroon,03Â°50'N,11Â°35'E,Africa/Douala
Yerevan,Armenia,40Â°10'N,44Â°31'E,Asia/Yerevan
Zagreb,Croatia,45Â°50'N,15Â°58'E,Europe/Zagreb

# UK Cities
Aberdeen,Scotland,57Â°08'N,02Â°06'W,Europe/London
Birmingham,England,52Â°30'N,01Â°50'W,Europe/London
Bolton,England,53Â°35'N,02Â°15'W,Europe/London
Bradford,England,53Â°47'N,01Â°45'W,Europe/London
Bristol,England,51Â°28'N,02Â°35'W,Europe/London
Cardiff,Wales,51Â°29'N,03Â°13'W,Europe/London
Crawley,England,51Â°8'N,00Â°10'W,Europe/London
Edinburgh,Scotland,55Â°57'N,03Â°13'W,Europe/London
Glasgow,Scotland,55Â°50'N,04Â°15'W,Europe/London
Greenwich,England,51Â°28'N,00Â°00'W,Europe/London
Leeds,England,53Â°48'N,01Â°35'W,Europe/London
Leicester,England,52Â°38'N,01Â°08'W,Europe/London
Liverpool,England,53Â°25'N,03Â°00'W,Europe/London
Manchester,England,53Â°30'N,02Â°15'W,Europe/London
Newcastle Upon Time,England,54Â°59'N,01Â°36'W,Europe/London
Newcastle,England,54Â°59'N,01Â°36'W,Europe/London
Norwich,England,52Â°38'N,01Â°18'E,Europe/London
Oxford,England,51Â°45'N,01Â°15'W,Europe/London
Plymouth,England,50Â°25'N,04Â°15'W,Europe/London
Portsmouth,England,50Â°48'N,01Â°05'W,Europe/London
Reading,England,51Â°27'N,0Â°58'W,Europe/London
Sheffield,England,53Â°23'N,01Â°28'W,Europe/London
Southampton,England,50Â°55'N,01Â°25'W,Europe/London
Swansea,England,51Â°37'N,03Â°57'W,Europe/London
Swindon,England,51Â°34'N,01Â°47'W,Europe/London
Wolverhampton,England,52Â°35'N,2Â°08'W,Europe/London

# US State Capitals
Montgomery,USA,32Â°21'N,86Â°16'W,US/Central
Juneau,USA,58Â°23'N,134Â°11'W,US/Alaska
Phoenix,USA,33Â°26'N,112Â°04'W,US/Mountain
Little Rock,USA,34Â°44'N,92Â°19'W,US/Central
Sacramento,USA,38Â°33'N,121Â°28'W,US/Pacific
Denver,USA,39Â°44'N,104Â°59'W,US/Mountain
Hartford,USA,41Â°45'N,72Â°41'W,US/Eastern
Dover,USA,39Â°09'N,75Â°31'W,US/Eastern
Tallahassee,USA,30Â°27'N,84Â°16'W,US/Eastern
Atlanta,USA,33Â°45'N,84Â°23'W,US/Eastern
Honolulu,USA,21Â°18'N,157Â°49'W,US/Hawaii
Boise,USA,43Â°36'N,116Â°12'W,US/Mountain
Springfield,USA,39Â°47'N,89Â°39'W,US/Central
Indianapolis,USA,39Â°46'N,86Â°9'W,US/Eastern
Des Moines,USA,41Â°35'N,93Â°37'W,US/Central
Topeka,USA,39Â°03'N,95Â°41'W,US/Central
Frankfort,USA,38Â°11'N,84Â°51'W,US/Eastern
Baton Rouge,USA,30Â°27'N,91Â°8'W,US/Central
Augusta,USA,44Â°18'N,69Â°46'W,US/Eastern
Annapolis,USA,38Â°58'N,76Â°30'W,US/Eastern
Boston,USA,42Â°21'N,71Â°03'W,US/Eastern
Lansing,USA,42Â°44'N,84Â°32'W,US/Eastern
Saint Paul,USA,44Â°56'N,93Â°05'W,US/Central
Jackson,USA,32Â°17'N,90Â°11'W,US/Central
Jefferson City,USA,38Â°34'N,92Â°10'W,US/Central
Helena,USA,46Â°35'N,112Â°1'W,US/Mountain
Lincoln,USA,40Â°48'N,96Â°40'W,US/Central
Carson City,USA,39Â°9'N,119Â°45'W,US/Pacific
Concord,USA,43Â°12'N,71Â°32'W,US/Eastern
Trenton,USA,40Â°13'N,74Â°45'W,US/Eastern
Santa Fe,USA,35Â°40'N,105Â°57'W,US/Mountain
Albany,USA,42Â°39'N,73Â°46'W,US/Eastern
Raleigh,USA,35Â°49'N,78Â°38'W,US/Eastern
Bismarck,USA,46Â°48'N,100Â°46'W,US/Central
Columbus,USA,39Â°59'N,82Â°59'W,US/Eastern
Oklahoma City,USA,35Â°28'N,97Â°32'W,US/Central
Salem,USA,44Â°55'N,123Â°1'W,US/Pacific
Harrisburg,USA,40Â°16'N,76Â°52'W,US/Eastern
Providence,USA,41Â°49'N,71Â°25'W,US/Eastern
Columbia,USA,34Â°00'N,81Â°02'W,US/Eastern
Pierre,USA,44Â°22'N,100Â°20'W,US/Central
Nashville,USA,36Â°10'N,86Â°47'W,US/Central
Austin,USA,30Â°16'N,97Â°45'W,US/Central
Salt Lake City,USA,40Â°45'N,111Â°53'W,US/Mountain
Montpelier,USA,44Â°15'N,72Â°34'W,US/Eastern
Richmond,USA,37Â°32'N,77Â°25'W,US/Eastern
Olympia,USA,47Â°2'N,122Â°53'W,US/Pacific
Charleston,USA,38Â°20'N,81Â°38'W,US/Eastern
Madison,USA,43Â°4'N,89Â°24'W,US/Central
Cheyenne,USA,41Â°8'N,104Â°48'W,US/Mountain

# Major US Cities
Birmingham,USA,33Â°39'N,86Â°48'W,US/Central
Anchorage,USA,61Â°13'N,149Â°53'W,US/Alaska
Los Angeles,USA,34Â°03'N,118Â°15'W,US/Pacific
San Francisco,USA,37Â°46'N,122Â°25'W,US/Pacific
Bridgeport,USA,41Â°11'N,73Â°11'W,US/Eastern
Wilmington,USA,39Â°44'N,75Â°32'W,US/Eastern
Jacksonville,USA,30Â°19'N,81Â°39'W,US/Eastern
Miami,USA,26Â°8'N,80Â°12'W,US/Eastern
Chicago,USA,41Â°50'N,87Â°41'W,US/Central
Wichita,USA,37Â°41'N,97Â°20'W,US/Central
Louisville,USA,38Â°15'N,85Â°45'W,US/Eastern
New Orleans,USA,29Â°57'N,90Â°4'W,US/Central
Portland,USA,43Â°39'N,70Â°16'W,US/Eastern
Baltimore,USA,9Â°17'N,76Â°37'W,US/Eastern
Detroit,USA,42Â°19'N,83Â°2'W,US/Eastern
Minneapolis,USA,44Â°58'N,93Â°15'W,US/Central
Kansas City,USA,39Â°06'N,94Â°35'W,US/Central
Billings,USA,45Â°47'N,108Â°32'W,US/Mountain
Omaha,USA,41Â°15'N,96Â°0'W,US/Central
Las Vegas,USA,36Â°10'N,115Â°08'W,US/Pacific
Manchester,USA,42Â°59'N,71Â°27'W,US/Eastern
Newark,USA,40Â°44'N,74Â°11'W,US/Eastern
Albuquerque,USA,35Â°06'N,106Â°36'W,US/Mountain
New York,USA,40Â°43'N,74Â°0'W,US/Eastern
Charlotte,USA,35Â°13'N,80Â°50'W,US/Eastern
Fargo,USA,46Â°52'N,96Â°47'W,US/Central
Cleveland,USA,41Â°28'N,81Â°40'W,US/Eastern
Portland,USA,45Â°31'N,122Â°40'W,US/Pacific
Philadelphia,USA,39Â°57'N,75Â°10'W,US/Eastern
Sioux Falls,USA,43Â°32'N,96Â°43'W,US/Central
Memphis,USA,35Â°07'N,89Â°58'W,US/Central
Houston,USA,29Â°45'N,95Â°22'W,US/Central
Dallas,USA,32Â°47'N,96Â°48'W,US/Central
Burlington,USA,44Â°28'N,73Â°9'W,US/Eastern
Virginia Beach,USA,36Â°50'N,76Â°05'W,US/Eastern
Seattle,USA,47Â°36'N,122Â°19'W,US/Pacific
Milwaukee,USA,43Â°03'N,87Â°57'W,US/Central
San Diego,USA,32Â°42'N,117Â°09'W,US/Pacific
Orlando,USA,28Â°32'N,81Â°22'W,US/Eastern
Buffalo,USA,42Â°54'N,78Â°50'W,US/Eastern
Toledo,USA,41Â°39'N,83Â°34'W,US/Eastern
"""

class AstralError(Exception):
    pass

class City(object):
    """Provides access to information for single city."""
    
    def __init__(self, info=None):
        """Initializes the object with a tuple of information.
        
        :param info: A tuple of information to fill in the city info.
        
            The tuple should contain items in the following order
            
            ================ =============
            Field            Default
            ================ =============
            name             Greenwich
            country          England
            latitude         51.168
            longitude        0
            time zone name   Europe/London
            ================ =============
                
            See :attr:`timezone` property for a method of obtaining time zone
            names
        """
        
        self.astral = None
        if info is None:
            self.name = 'Greenwich'
            self.country = 'England'
            self._latitude = 51.168
            self._longitude = 0
            self._timezone_group = 'Europe'
            self._timezone_location = 'London'
        else:
            self._latitude = 0
            self._longitude = 0
            self._timezone_group = ''
            self._timezone_location = ''

            try:
                self.name = info[0]
                self.country = info[1]
                self.latitude = info[2]
                self.longitude = info[3]
                self.timezone = info[4]
            except:
                pass

    def __repr__(self):
        return '%s/%s, tz=%s, lat=%0.02f, lon=%0.02f' % (self.name, self.country,
                                                  self.timezone,
                                                  self.latitude, self.longitude)
        
    def latitude():
        doc = """The city's latitude

        ``latitude`` can be set either as a string or as a number
        
        For strings they must be of the form::
        
            degreesÂ°minutes'[N|S] e.g. 51Â°31'N
            
        For numbers, negative numbers signify latitudes to the South.
        """
        
        def fget(self):
            return self._latitude
            
        def fset(self, latitude):
            if isinstance(latitude, str):
                (deg, rest) = latitude.split("Â°", 1)
                (minute, rest) = rest.split("'", 1)

                self._latitude = float(deg) + (float(minute)/60)

                if latitude.endswith("S"):
                    self._latitude = -self._latitude
            else:
                self._latitude = float(latitude)
            
        return locals()
        
    latitude = property(**latitude())
        
    def longitude():
        doc = """The city's longitude.

        ``longitude`` can be set either as a string or as a number
        
        For strings they must be of the form::
        
            degreesÂ°minutes'[E|W] e.g. 51Â°31'W
            
        For numbers, positive numbers signify longitudes to the East.
        """
        
        def fget(self):
            return self._longitude
            
        def fset(self, longitude):
            if isinstance(longitude, str):
                (deg, rest) = longitude.split("Â°", 1)
                (minute, rest) = rest.split("'", 1)

                self._longitude = float(deg) + (float(minute)/60)

                # Conventionally locations to the west of 0Â° are negative
                # but the calculation is based on the opposite
                if longitude.endswith("W"):
                    self._longitude = -self._longitude
            else:
                self._longitude = float(longitude)
            
        return locals()
        
    longitude = property(**longitude())
        
    def timezone():
        doc = """The name of the time zone in which the city is located.
        
        A list of time zone names can be obtained from pytz. For example.
        
        >>> from pytz import all_timezones
        >>> for tz in all_timezones:
        ...     print tz
        """
        
        def fget(self):
            if self._timezone_location != '':
                return '%s/%s' % (self._timezone_group, self._timezone_location)
            else:
                return self._timezone_group
        
        def fset(self, name):
            if name not in pytz.all_timezones:
                raise ValueError('Timezone \'%s\' not recognized' % name)

            try:                
                self._timezone_group, self._timezone_location = \
                    name.split('/', 1)
            except ValueError:
                self._timezone_group = name
                self._timezone_location = ''

        return locals()
            
    timezone = property(**timezone())

    def tz():
        doc = """The timezone."""
        
        def fget(self):
            try:
                tz =  pytz.timezone(self.timezone)
                return tz
            except pytz.UnknownTimeZoneError:
                raise AstralError('Unknown timezone \'%s\'' % self.timezone)
            
        return locals()
            
    tz = property(**tz())

    def solar_depression():
        doc = """The number of degrees the sun must be below the horizon for the
        dawn/dusk calc.
        
        Can either be set as a number of degrees below the horizon or as
        one of the following strings
        
        ============= =======
        String        Degrees
        ============= =======
        civil            6.0
        nautical        12.0
        astronomical    18.0
        ============= =======
        """
        
        def fget(self):
            return self.astral.solar_depression
            
        def fset(self, depression):
            if self.astral is None:
                self.astral = Astral()

            self.astral.solar_depression = depression 
            
        return locals()
        
    solar_depression = property(**solar_depression())

    def dawn(self, date=None, local=True):
        """Calculates the time in the morning when the sun is a certain number
        of degrees below the horizon. By default this is 6 degrees but can be
        changed by setting the :attr:`Astral.solar_depression` property.
        
        :param date: The date for which to calculate the dawn time.
                     A value of None uses the current date.

        :param local: True  = Time to be returned in city's time zone (Default);
                      False = Time to be returned in UTC.
                      
        :rtype: :class:`datetime.datetime` of dawn
        """

        if self.astral is None:
            self.astral = Astral()

        if date is None:
            date = datetime.date.today()

        dawn = self.astral.dawn_utc(date, self.latitude, self.longitude)

        if local:
            return dawn.astimezone(self.tz)            
        else:
            return dawn
        
    def sunrise(self, date=None, local=True):
        """Return sunrise time.
        
        Calculates the time in the morning when the sun is a 0.833 degrees
        below the horizon. This is to account for refraction.
        
        :param date: The date for which to calculate the sunrise time.
                     A value of None uses the current date.

        :param local: True  = Time to be returned in city's time zone (Default);
                      False = Time to be returned in UTC.
                      
        :rtype: :class:`datetime.datetime` of sunrise
        """

        if self.astral is None:
            self.astral = Astral()
        
        if date is None:
            date = datetime.date.today()

        sunrise = self.astral.sunrise_utc(date, self.latitude, self.longitude)

        if local:
            return sunrise.astimezone(self.tz)            
        else:
            return sunrise
        
    def solar_noon(self, date=None, local=True):
        """Calculates the solar noon (the time when the sun is at its highest
        point.)
        
        :param date: The date for which to calculate the noon time.
                     A value of None uses the current date.

        :param local: True  = Time to be returned in city's time zone (Default);
                      False = Time to be returned in UTC.
                      
        :rtype: :class:`datetime.datetime` of noon
        """
        
        if self.astral is None:
            self.astral = Astral()

        if date is None:
            date = datetime.date.today()

        noon = self.astral.solar_noon_utc(date, self.longitude)

        if local:
            return noon.astimezone(self.tz)            
        else:
            return noon
        
    def sunset(self, date=None, local=True):
        """Calculates sunset time (the time in the evening when the sun is a
        0.833 degrees below the horizon. This is to account for refraction.)
        
        :param date: The date for which to calculate the sunset time.
                     A value of None uses the current date.

        :param local: True  = Time to be returned in city's time zone (Default);
                      False = Time to be returned in UTC.
                      
        :rtype: :class:`datetime.datetime` of sunset
        """
        
        if self.astral is None:
            self.astral = Astral()

        if date is None:
            date = datetime.date.today()

        sunset = self.astral.sunset_utc(date, self.latitude, self.longitude)

        if local:
            return sunset.astimezone(self.tz)            
        else:
            return sunset
        
    def dusk(self, date=None, local=True):
        """Calculates the dusk time (the time in the evening when the sun is a
        certain number of degrees below the horizon. By default this is 6
        degrees but can be changed by setting the
        :attr:`Astral.solar_depression` property.)
        
        :param date: The date for which to calculate the dusk time.
                     A value of None uses the current date.

        :param local: True  = Time to be returned in city's time zone (Default);
                      False = Time to be returned in UTC.
                      
        :rtype: :class:`datetime.datetime` of dusk
        """
        
        if self.astral is None:
            self.astral = Astral()

        if date is None:
            date = datetime.date.today()

        dusk = self.astral.dusk_utc(date, self.latitude, self.longitude)

        if local:
            return dusk.astimezone(self.tz)            
        else:
            return dusk
    
    def sun(self, date=None, local=True):
        """Returns dawn, sunrise, noon, sunset and dusk as a dictionary.
        
        :param date: The date for which to calculate the times.
                     A value of None uses the current date.

        :param local: True  = Time to be returned in city's time zone (Default);
                      False = Time to be returned in UTC.
                      
        :rtype: :class:`datetime.datetime` of dusk
        """
        
        if self.astral is None:
            self.astral = Astral()

        if date is None:
            date = datetime.date.today()

        sun = self.astral.sun_utc(date, self.latitude, self.longitude)

        if local:
            for key, dt in list(sun.items()):
                sun[key] = dt.astimezone(self.tz)

        return sun

    def rahukaalam(self, date=None, local=True):
        """Calculates the period of rahukaalam.
        
        :param date: The date for which to calculate the rahukaalam period.
                     A value of None uses the current date.

        :param local: True  = Time to be returned in city's time zone (Default);
                      False = Time to be returned in UTC.
                      
        :rtype: :class:`datetime.datetime` of dusk
        """

        if self.astral is None:
            self.astral = Astral()

        if date is None:
            date = datetime.date.today()

        rahukaalam = self.astral.rahukaalam_utc(date,
            self.latitude, self.longitude)

        if local:
            for key, dt in list(rahukaalam.items()):
                rahukaalam[key] = dt.astimezone(self.tz)
            
        return rahukaalam
    
    def solar_azimuth(self, dateandtime=None):
        """Calculates the solar azimuth angle for a specific date/time.
        
        :param dateandtime: The date and time for which to calculate the angle.
        :type dateandtime: :class:`datetime.datetime`
                      
        :rtype: The angle in degrees clockwise from North as a float.
        """

        if self.astral is None:
            self.astral = Astral()

        if dateandtime is None:
            dateandtime = datetime.datetime.now(tz=self.tz)
            
        return self.astral.solar_azimuth(dateandtime,
            self.latitude, self.longitude)
    
    def solar_elevation(self, dateandtime=None):
        """Calculates the solar elevation angle for a specific time.
        
        :param dateandtime: The date and time for which to calculate the angle.
        :type dateandtime: :class:`datetime.datetime`
                      
        :rtype: The angle in degrees from the horizon as a float.
        """

        if self.astral is None:
            self.astral = Astral()

        if dateandtime is None:
            dateandtime = datetime.datetime.now(tz=self.tz)

        return self.astral.solar_elevation(dateandtime, 
            self.latitude, self.longitude)

    def moon_phase(self, date=None):
        """Calculates the moon phase for a specific date.
        
        :param date: The date to calculate the phase for.
                     If ommitted the current date is used.
        :type date: datetime.date
            
        :rtype:
            Integer designating phase
        
                | 0  = New moon
                | 7  = First quarter
                | 14 = Full moon
                | 21 = Last quarter
        """
        
        if self.astral is None:
            self.astral = Astral()

        if date is None:
            date = datetime.date.today()

        return self.astral.moon_phase(date, self.tz)


class CityGroup(object):
    def __init__(self, name):
        self.name = name
        self._cities = {}

    def __getitem__(self, key):
        """Returns a City object for the specified city. ::
        
            group = astral.europe
            city = group['London']
        
        You can supply an optional country name by adding a comma
        followed by the country name. Where multiple cities have the
        same name you may need to supply the country name otherwise
        the first result will be returned which may not be the one
        you're looking for. ::
        
            city = group['Abu Dhabi,United Arab Emirates']
        
        Handles city names with spaces and mixed case.
        """

        name = str(key).lower().replace(' ', '_')

        try:
            city_name, country_name = name.split(',', 1)
        except:
            city_name = name
            country_name = ''

        city_name = city_name.strip('"\'')
        country_name = country_name.strip('"\'')

        for (name, city_list) in list(self._cities.items()):
            if name.replace(' ', '_') == city_name:
                if len(city_list) == 1 or country_name == '':
                    return city_list[0]

                for city in city_list:
                    if city.country.lower().replace(' ', '_') \
                    == country_name:
                        return city

        raise KeyError('Unrecognised city name - %s' % key)
        
    def __setitem__(self, key, value):
        key = str(key).lower()
        if key not in self._cities:
            self._cities[key] = [value]
        else:
            self._cities[key].append(value)

    def __contains__(self, key):
        key = str(key).lower()
        for name in list(self._cities.keys()):
            if name == key:
                return True
            
        return False
    
    def __iter__(self):
        for city_list in list(self._cities.values()):
            for city in city_list:
                yield city
    
    def keys(self):
        return list(self._cities.keys())
    
    def values(self):
        return list(self._cities.values())
    
    def items(self):
        return list(self._cities.items())
    
    def cities():
        def fget(self):
            k = []
            for city_list in list(self._cities.values()):
                for city in city_list:
                    k.append(city.name)
                
            return k
        
        return locals()
    
    cities = property(**cities())
        
            
class CityDB(object):
    def __init__(self):
        self._groups = {}
        
        cities = _CITY_INFO.split('\n')
        for line in cities:
            line = line.strip()
            if line != '' and line[0] != '#':
                if line[-1] == '\n':
                    line = line[:-1]
                
                info = line.split(',')

                city = City(info)
                
                timezone_group = city._timezone_group.lower()
                try:
                    group = self.__getattr__(timezone_group)
                except:
                    group = CityGroup(city._timezone_group)
                    self._groups[timezone_group] = group
                    
                group[info[0].lower()] = city
        
    def __getattr__(self, key):
        """Access to each timezone group. For example London is in timezone
        group Europe.
        
        Attribute lookup is case insensitive"""
        
        key = str(key).lower()
        for name, value in list(self._groups.items()):
            if name == key:
                return value
        
        raise AttributeError('Group \'%s\' not found' % key)
    
    def __getitem__(self, key):
        """Lookup a city within all timezone groups.
        
        Item lookup is case insensitive."""
        
        key = str(key).lower()
        for group in list(self._groups.values()):
            try:
                return group[key]
            except KeyError:
                pass

        raise KeyError('Unrecognised city name - %s' % key)

    def __iter__(self):
        return self._groups.__iter__()

    def __contains__(self, key):
        key = str(key).lower()
        for name, group in list(self._groups.items()):
            if name == key:
                return True
            
            if key in group:
                return True
                
        return False
    
    def cities():
        def fget(self):
            k = []
            for group in list(self._groups.values()):
                k.extend(group.cities)
                
            return k
        
        return locals()
    
    cities = property(**cities())
    
    def groups():
        def fget(self):
            return self._groups
        
        return locals()
        
    groups = property(**groups())
        

class Astral(object):
    def __init__(self):
        """Initialise the city database and set the default depression."""
        
        self._citydb = CityDB()
        self._depression = 6  # Set default depression in degrees

    def __getitem__(self, key):
        """Returns the City instance specified by ``key``."""
        
        city = self._citydb[key]
        city.astral = self
        return city

    def citydb():
        doc = """:rtype: The database of cities."""

        def fget(self):
            return self._citydb
            
        return locals()
        
    citydb = property(**citydb())

    def solar_depression():
        doc = """The number of degrees the sun must be below the horizon for the
        dawn/dusk calc.
        
        Can either be set as a number of degrees below the horizon or as
        one of the following strings
        
        ============= =======
        String        Degrees
        ============= =======
        civil            6.0
        nautical        12.0
        astronomical    18.0
        ============= =======
        """
        
        def fget(self):
            return self._depression
            
        def fset(self, depression):
            if isinstance(depression, str):
                try:
                    self._depression = {
                        'civil': 6,
                        'nautical': 12,
                        'astronomical': 18}[depression]
                except:
                    raise KeyError(("solar_depression must be either a number "
                        "or one of 'civil', 'nautical' or 'astronomical'"))
            else:
                self._depression = float(depression)
            
        return locals()
        
    solar_depression = property(**solar_depression())

    def sun_utc(self, date, latitude, longitude):
        """Calculate all the info for the sun at once.

        :param date:       Date to calculate for.
        :type date:        :class:`datetime.date`
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype:
            Dictionary with keys ``dawn``, ``sunrise``, ``noon``,
            ``sunset`` and ``dusk``
        """
        
        dawn = self.dawn_utc(date, latitude, longitude)
        sunrise = self.sunrise_utc(date, latitude, longitude)
        noon = self.solar_noon_utc(date, longitude)
        sunset = self.sunset_utc(date, latitude, longitude)
        dusk = self.dusk_utc(date, latitude, longitude)
        
        return {
            'dawn': dawn,
            'sunrise': sunrise,
            'noon': noon,
            'sunset': sunset,
            'dusk': dusk
        }

    def dawn_utc(self, date, latitude, longitude):
        """Calculate dawn time in the UTC timezone.
        
        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: date/time in UTC timezone
        """
        
        julianday = self._julianday(date)

        if latitude > 89.8:
            latitude = 89.8
            
        if latitude < -89.8:
            latitude = -89.8
        
        t = self._jday_to_jcentury(julianday)
        eqtime = self._eq_of_time(t)
        solarDec = self._sun_declination(t)
        
        try:
            hourangle = self._hour_angle_sunrise(latitude, solarDec)
        except:
            raise AstralError(('Sun remains below horizon '
                'on this day, at this location.'))

        delta = -longitude - degrees(hourangle)
        timeDiff = 4.0 * delta
        timeUTC = 720.0 + timeDiff - eqtime

        newt = self._jday_to_jcentury(self._jcentury_to_jday(t) + \
            timeUTC / 1440.0)
        eqtime = self._eq_of_time(newt)
        solarDec = self._sun_declination(newt)
        hourangle = self._hour_angle_dawn(latitude, solarDec, self._depression)
        delta = -longitude - degrees(hourangle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqtime
        
        timeUTC = timeUTC/60.0
        hour = int(timeUTC)
        minute = int((timeUTC - hour) * 60)
        second = int((((timeUTC - hour) * 60) - minute) * 60)

        if second > 59:
            second -= 60
            minute += 1
        elif second < 0:
            second += 60
            minute -= 1

        if minute > 59:
            minute -= 60
            hour += 1
        elif minute < 0:
            minute += 60
            hour -= 1

        if hour > 23:
            hour -= 24
            date += datetime.timedelta(days=1)
        elif hour < 0:
            hour += 24
            date -= datetime.timedelta(days=1)
        
        dawn = datetime.datetime(date.year, date.month, date.day, hour, minute,
            second, tzinfo=pytz.utc)

        return dawn

    def sunrise_utc(self, date, latitude, longitude):
        """Calculate sunrise time in the UTC timezone.
        
        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: date/time in UTC timezone
        """
        
        julianday = self._julianday(date)

        t = self._jday_to_jcentury(julianday)
        eqtime = self._eq_of_time(t)
        solarDec = self._sun_declination(t)

        try:
            hourangle = self._hour_angle_sunrise(latitude, solarDec)
        except:
            raise AstralError(('Sun remains below horizon on this day, '
                'at this location.'))

        delta = -longitude - degrees(hourangle)
        timeDiff = 4.0 * delta
        timeUTC = 720.0 + timeDiff - eqtime

        newt = self._jday_to_jcentury(self._jcentury_to_jday(t) + \
            timeUTC / 1440.0)
        eqtime = self._eq_of_time(newt)
        solarDec = self._sun_declination(newt)
        hourangle = self._hour_angle_sunrise(latitude, solarDec)
        delta = -longitude - degrees(hourangle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqtime
        
        timeUTC = timeUTC/60.0
        hour = int(timeUTC)
        minute = int((timeUTC - hour) * 60)
        second = int((((timeUTC - hour) * 60) - minute) * 60)

        if second > 59:
            second -= 60
            minute += 1
        elif second < 0:
            second += 60
            minute -= 1

        if minute > 59:
            minute -= 60
            hour += 1
        elif minute < 0:
            minute += 60
            hour -= 1

        if hour > 23:
            hour -= 24
            date += datetime.timedelta(days=1)
        elif hour < 0:
            hour += 24
            date -= datetime.timedelta(days=1)

        sunrise = datetime.datetime(date.year, date.month, date.day,
            hour, minute, second, tzinfo=pytz.utc)

        return sunrise

    def solar_noon_utc(self, date, longitude):
        """Calculate solar noon time in the UTC timezone.
        
        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: date/time in UTC timezone
        """
        
        julianday = self._julianday(date)

        newt = self._jday_to_jcentury(julianday + 0.5 + -longitude / 360.0)

        eqtime = self._eq_of_time(newt)
        timeUTC = 720.0 + (-longitude * 4.0) - eqtime

        timeUTC = timeUTC/60.0
        hour = int(timeUTC)
        minute = int((timeUTC - hour) * 60)
        second = int((((timeUTC - hour) * 60) - minute) * 60)

        if second > 59:
            second -= 60
            minute += 1
        elif second < 0:
            second += 60
            minute -= 1

        if minute > 59:
            minute -= 60
            hour += 1
        elif minute < 0:
            minute += 60
            hour -= 1

        if hour > 23:
            hour -= 24
            date += datetime.timedelta(days=1)
        elif hour < 0:
            hour += 24
            date -= datetime.timedelta(days=1)

        noon = datetime.datetime(date.year, date.month, date.day,
            hour, minute, second, tzinfo=pytz.utc)

        return noon

    def sunset_utc(self, date, latitude, longitude):
        """Calculate sunset time in the UTC timezone.
        
        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: date/time in UTC timezone
        """
        
        julianday = self._julianday(date)

        t = self._jday_to_jcentury(julianday)
        eqtime = self._eq_of_time(t)
        solarDec = self._sun_declination(t)

        try:
            hourangle = self._hour_angle_sunset(latitude, solarDec)
        except:
            raise AstralError(('Sun remains below horizon on this day, '
                'at this location.'))

        delta = -longitude - degrees(hourangle)
        timeDiff = 4.0 * delta
        timeUTC = 720.0 + timeDiff - eqtime

        newt = self._jday_to_jcentury(self._jcentury_to_jday(t) + \
            timeUTC / 1440.0)
        eqtime = self._eq_of_time(newt)
        solarDec = self._sun_declination(newt)
        hourangle = self._hour_angle_sunset(latitude, solarDec)
        delta = -longitude - degrees(hourangle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqtime
        
        timeUTC = timeUTC/60.0
        hour = int(timeUTC)
        minute = int((timeUTC - hour) * 60)
        second = int((((timeUTC - hour) * 60) - minute) * 60)

        if second > 59:
            second -= 60
            minute += 1
        elif second < 0:
            second += 60
            minute -= 1

        if minute > 59:
            minute -= 60
            hour += 1
        elif minute < 0:
            minute += 60
            hour -= 1

        if hour > 23:
            hour -= 24
            date += datetime.timedelta(days=1)
        elif hour < 0:
            hour += 24
            date -= datetime.timedelta(days=1)

        sunset = datetime.datetime(date.year, date.month, date.day,
            hour, minute, second, tzinfo=pytz.utc)

        return sunset

    def dusk_utc(self, date, latitude, longitude):
        """Calculate dusk time in the UTC timezone.
        
        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: date/time in UTC timezone
        """
        
        julianday = self._julianday(date)

        if latitude > 89.8:
            latitude = 89.8
            
        if latitude < -89.8:
            latitude = -89.8
        
        t = self._jday_to_jcentury(julianday)
        eqtime = self._eq_of_time(t)
        solarDec = self._sun_declination(t)

        try:
            hourangle = self._hour_angle_sunset(latitude, solarDec)
        except:
            raise AstralError(('Sun remains below horizon on this day, '
                'at this location.'))

        delta = -longitude - degrees(hourangle)
        timeDiff = 4.0 * delta
        timeUTC = 720.0 + timeDiff - eqtime

        newt = self._jday_to_jcentury(self._jcentury_to_jday(t) + \
            timeUTC / 1440.0)
        eqtime = self._eq_of_time(newt)
        solarDec = self._sun_declination(newt)
        hourangle = self._hour_angle_dusk(latitude, solarDec, self._depression)
        delta = -longitude - degrees(hourangle)
        timeDiff = 4 * delta
        timeUTC = 720 + timeDiff - eqtime
        
        timeUTC = timeUTC/60.0
        hour = int(timeUTC)
        minute = int((timeUTC - hour) * 60)
        second = int((((timeUTC - hour) * 60) - minute) * 60)

        if second > 59:
            second -= 60
            minute += 1
        elif second < 0:
            second += 60
            minute -= 1

        if minute > 59:
            minute -= 60
            hour += 1
        elif minute < 0:
            minute += 60
            hour -= 1

        if hour > 23:
            hour -= 24
            date += datetime.timedelta(days=1)
        elif hour < 0:
            hour += 24
            date -= datetime.timedelta(days=1)

        dusk = datetime.datetime(date.year, date.month, date.day,
            hour, minute, second, tzinfo=pytz.utc)

        return dusk

    def rahukaalam_utc(self, date, latitude, longitude):
        """Calculate ruhakaalam times in the UTC timezone.
        
        :param date:       Date to calculate for.
        :type date:        datetime.date
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: Dictionary with keys ``start`` and ``end``
        """
        
        if date is None:
            date = datetime.date.today()

        try:
            sunrise = self.sunrise_utc(date, latitude, longitude)
            sunset = self.sunset_utc(date, latitude, longitude)
        except:
            raise AstralError(('Sun remains below horizon on this day, '
                'at this location.'))
        
        octant_duration = (sunset - sunrise) / 8

        # Mo,Sa,Fr,We,Th,Tu,Su
        octant_index = [1,6,4,5,3,2,7]
        
        weekday = date.weekday()
        octant = octant_index[weekday]
        
        start = sunrise + (octant_duration * octant)
        end = start + octant_duration
        
        return {'start': start, 'end': end}

    def solar_azimuth(self, dateandtime, latitude, longitude):
        """Calculate the azimuth of the sun in the UTC timezone.
        
        :param dateandtime:       Date/time to calculate for.
        :type dateandtime:        datetime.datetime
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: Azimuth in degrees
        """
    
        if latitude > 89.8:
            latitude = 89.8
            
        if latitude < -89.8:
            latitude = -89.8
    
        zone = -dateandtime.utcoffset().seconds / 3600.0
        utc_datetime = dateandtime.astimezone(pytz.utc)
        timenow = utc_datetime.hour + (utc_datetime.minute / 60.0) + \
            (utc_datetime.second // 3600)

        JD = self._julianday(dateandtime)
        t = self._jday_to_jcentury(JD + timenow / 24.0)
        theta = self._sun_declination(t)
        Etime = self._eq_of_time(t)
    
        eqtime = Etime
        solarDec = theta   # in degrees
    
        solarTimeFix = eqtime - (4.0 * -longitude) + (60 * zone)
        trueSolarTime = dateandtime.hour * 60.0 + dateandtime.minute + \
            dateandtime.second / 60.0 + solarTimeFix
        #    in minutes
    
        while trueSolarTime > 1440:
            trueSolarTime = trueSolarTime - 1440
        
        hourangle = trueSolarTime / 4.0 - 180.0
        #    Thanks to Louis Schwarzmayr for the next line:
        if hourangle < -180:
            hourangle = hourangle + 360.0
    
        harad = radians(hourangle)
    
        csz = sin(radians(latitude)) * sin(radians(solarDec)) + \
              cos(radians(latitude)) * cos(radians(solarDec)) * cos(harad)
    
        if csz > 1.0:
            csz = 1.0
        elif csz < -1.0:
            csz = -1.0
        
        zenith = degrees(acos(csz))
    
        azDenom = (cos(radians(latitude)) * sin(radians(zenith)))
        
        if (abs(azDenom) > 0.001):
            azRad = ((sin(radians(latitude)) *  cos(radians(zenith))) - \
                sin(radians(solarDec))) / azDenom
            
            if abs(azRad) > 1.0:
                if azRad < 0:
                    azRad = -1.0
                else:
                    azRad = 1.0
    
            azimuth = 180.0 - degrees(acos(azRad))
    
            if hourangle > 0.0:
                azimuth = -azimuth
        else:
            if latitude > 0.0:
                azimuth = 180.0
            else:
                azimuth = 0#
    
        if azimuth < 0.0:
            azimuth = azimuth + 360.0
                 
        return azimuth

    def solar_elevation(self, dateandtime, latitude, longitude):
        """Calculate the elevation of the sun.
        
        :param dateandtime:       Date/time to calculate for.
        :type dateandtime:        datetime.datetime
        :param latitude:   Latitude - Southern latitudes should be negative
        :type latitude:    float 
        :param longitude:  Longitude as a floating point number. Eastern
                           latitudes should be negative
        :type longitude:   float 
        
        :rtype: Elevation in degrees
        """
    
        if latitude > 89.8:
            latitude = 89.8
            
        if latitude < -89.8:
            latitude = -89.8

        zone = -dateandtime.utcoffset().seconds / 3600.0
        utc_datetime = dateandtime.astimezone(pytz.utc)
        timenow = utc_datetime.hour + (utc_datetime.minute / 60.0) + \
            (utc_datetime.second // 3600)
    
        JD = self._julianday(dateandtime)
        t = self._jday_to_jcentury(JD + timenow / 24.0)
        theta = self._sun_declination(t)
        Etime = self._eq_of_time(t)
    
        eqtime = Etime
        solarDec = theta   # in degrees
    
        solarTimeFix = eqtime - (4.0 * -longitude) + (60 * zone)
        trueSolarTime = dateandtime.hour * 60.0 + dateandtime.minute + \
            dateandtime.second / 60.0 + solarTimeFix
        #    in minutes
    
        while trueSolarTime > 1440:
            trueSolarTime = trueSolarTime - 1440
        
        hourangle = trueSolarTime / 4.0 - 180.0
        #    Thanks to Louis Schwarzmayr for the next line:
        if hourangle < -180:
            hourangle = hourangle + 360.0
    
        harad = radians(hourangle)
    
        csz = sin(radians(latitude)) * sin(radians(solarDec)) + \
              cos(radians(latitude)) * cos(radians(solarDec)) * cos(harad)
    
        if csz > 1.0:
            csz = 1.0
        elif csz < -1.0:
            csz = -1.0
        
        zenith = degrees(acos(csz))
    
        azDenom = (cos(radians(latitude)) * sin(radians(zenith)))
        
        if (abs(azDenom) > 0.001):
            azRad = ((sin(radians(latitude)) *  cos(radians(zenith))) - \
                sin(radians(solarDec))) / azDenom
            
            if abs(azRad) > 1.0:
                if azRad < 0:
                    azRad = -1.0
                else:
                    azRad = 1.0
    
            azimuth = 180.0 - degrees(acos(azRad))
    
            if hourangle > 0.0:
                azimuth = -azimuth
        else:
            if latitude > 0.0:
                azimuth = 180.0
            else:
                azimuth = 0
    
        if azimuth < 0.0:
            azimuth = azimuth + 360.0
                    
        exoatmElevation = 90.0 - zenith

        if exoatmElevation > 85.0:
            refractionCorrection = 0.0
        else:
            te = tan(radians(exoatmElevation))
            if exoatmElevation > 5.0:
                refractionCorrection = 58.1 / te - 0.07 / (te * te * te) + \
                    0.000086 / (te * te * te * te * te)
            elif exoatmElevation > -0.575:
                step1 = (-12.79 + exoatmElevation * 0.711)
                step2 = (103.4 + exoatmElevation * (step1))
                step3 = (-518.2 + exoatmElevation * (step2))
                refractionCorrection = 1735.0 + exoatmElevation * (step3)
            else:
                refractionCorrection = -20.774 / te
    
            refractionCorrection = refractionCorrection / 3600.0
            
        solarzen = zenith - refractionCorrection
                     
        solarelevation = 90.0 - solarzen
    
        return solarelevation

    def moon_phase(self, date, tz):
        """Calculates the phase of the moon on the specified date.
        
        :param date: The date to calculate the phase for.
        :type date: datetime.date
        :param tz: The timezone to calculate the phase for.
        :type tz: pytz.tz
            
        :rtype:
            Integer designating phase
        
                | 0  = New moon
                | 7  = First quarter
                | 14 = Full moon
                | 21 = Last quarter
        """
        
        jd = self._julianday(date, tz)
        DT = pow((jd - 2382148), 2) / (41048480*86400)
        T = (jd + DT - 2451545.0) / 36525
        T2 = pow(T,2)
        T3 = pow(T,3)
        D = 297.85 + (445267.1115*T) - (0.0016300*T2) + (T3/545868)
        D = radians(self._proper_angle(D))
        M = 357.53 + (35999.0503*T)
        M = radians(self._proper_angle(M))
        M1 = 134.96 + (477198.8676*T) + (0.0089970*T2) + (T3/69699)
        M1 = radians(self._proper_angle(M1))
        elong = degrees(D) + 6.29*sin(M1)
        elong -= 2.10*sin(M)
        elong += 1.27*sin(2*D - M1)
        elong += 0.66*sin(2*D)
        elong = self._proper_angle(elong)
        moon = int(floor(((elong + 6.43) / 360) * 28))
        if moon == 28:
            moon = 0
        
        return moon

    def _proper_angle(self, value):
        if value > 0.0:
            value /= 360.0
            return (value - floor(value)) * 360
        else:
            tmp = ceil(abs(value / 360.0))
            return value + tmp * 360.0

    def _julianday(self, date, timezone=None):
        day = date.day
        month = date.month
        year = date.year
        
        if timezone is not None:
            offset = timezone.localize(datetime.datetime(year, month, day)).utcoffset()
            offset = offset.total_seconds() / 1440.0
            day += offset + 0.5
        
        if month <= 2:
            year = year - 1
            month = month + 12
        
        A = floor(year / 100.0)
        B = 2 - A + floor(A / 4.0)

        jd = floor(365.25 * (year + 4716)) + floor(30.6001 * (month + 1)) + \
            day - 1524.5
        if jd > 2299160.4999999:
            jd += B
            
        return jd
        
    def _jday_to_jcentury(self, julianday):
        return (julianday - 2451545.0) / 36525.0

    def _jcentury_to_jday(self, juliancentury):
        return (juliancentury * 36525.0) + 2451545.0

    def _mean_obliquity_of_ecliptic(self, juliancentury):
        seconds = 21.448 - juliancentury * \
            (46.815 + juliancentury * (0.00059 - juliancentury * (0.001813)))
        return 23.0 + (26.0 + (seconds / 60.0)) / 60.0

    def _obliquity_correction(self, juliancentury):
        e0 = self._mean_obliquity_of_ecliptic(juliancentury)

        omega = 125.04 - 1934.136 * juliancentury
        return e0 + 0.00256 * cos(radians(omega))
    
    def _geom_mean_long_sun(self, juliancentury):
        l0 = 280.46646 + \
            juliancentury * (36000.76983 + 0.0003032 * juliancentury)
        return l0 % 360.0
        
    def _eccentricity_earth_orbit(self, juliancentury):
        return 0.016708634 - \
            juliancentury * (0.000042037 + 0.0000001267 * juliancentury)
        
    def _geom_mean_anomaly_sun(self, juliancentury):
        return 357.52911 + \
            juliancentury * (35999.05029 - 0.0001537 * juliancentury)

    def _eq_of_time(self, juliancentury):
        epsilon = self._obliquity_correction(juliancentury)
        l0 = self._geom_mean_long_sun(juliancentury)
        e = self._eccentricity_earth_orbit(juliancentury)
        m = self._geom_mean_anomaly_sun(juliancentury)

        y = tan(radians(epsilon) / 2.0)
        y = y * y

        sin2l0 = sin(2.0 * radians(l0))
        sinm = sin(radians(m))
        cos2l0 = cos(2.0 * radians(l0))
        sin4l0 = sin(4.0 * radians(l0))
        sin2m = sin(2.0 * radians(m))

        Etime = y * sin2l0 - 2.0 * e * sinm + 4.0 * e * y * sinm * cos2l0 - \
                0.5 * y * y * sin4l0 - 1.25 * e * e * sin2m

        return degrees(Etime) * 4.0

    def _sun_eq_of_center(self, juliancentury):
        m = self._geom_mean_anomaly_sun(juliancentury)

        mrad = radians(m)
        sinm = sin(mrad)
        sin2m = sin(mrad + mrad)
        sin3m = sin(mrad + mrad + mrad)

        c = sinm * (1.914602 - juliancentury * \
            (0.004817 + 0.000014 * juliancentury)) + \
            sin2m * (0.019993 - 0.000101 * juliancentury) + sin3m * 0.000289
            
        return c

    def _sun_true_long(self, juliancentury):
        l0 = self._geom_mean_long_sun(juliancentury)
        c = self._sun_eq_of_center(juliancentury)

        return l0 + c

    def _sun_apparent_long(self, juliancentury):
        O = self._sun_true_long(juliancentury)

        omega = 125.04 - 1934.136 * juliancentury
        return O - 0.00569 - 0.00478 * sin(radians(omega))

    def _sun_declination(self, juliancentury):
        e = self._obliquity_correction(juliancentury)
        lambd = self._sun_apparent_long(juliancentury)

        sint = sin(radians(e)) * sin(radians(lambd))
        return degrees(asin(sint))

    def _hour_angle(self, latitude, solar_dec, solar_depression):
        latRad = radians(latitude)
        sdRad = radians(solar_dec)

        HA = (acos(cos(radians(90 + solar_depression)) / \
            (cos(latRad) * cos(sdRad)) - tan(latRad) * tan(sdRad)))
        
        return HA

    def _hour_angle_sunrise(self, latitude, solar_dec):
        return self._hour_angle(latitude, solar_dec, 0.833)
        
    def _hour_angle_sunset(self, latitude, solar_dec):
        return -self._hour_angle(latitude, solar_dec, 0.833)

    def _hour_angle_dawn(self, latitude, solar_dec, solar_depression):
        return self._hour_angle(latitude, solar_dec, solar_depression)

    def _hour_angle_dusk(self, latitude, solar_dec, solar_depression):
        return -self._hour_angle(latitude, solar_dec, solar_depression)

    def _sun_true_anomoly(self, juliancentury):
        m = self._geom_mean_anomaly_sun(juliancentury)
        c = self._sun_eq_of_center(juliancentury)

        return m + c

    def _sun_rad_vector(self, juliancentury):
        v = self._sun_true_anomoly(juliancentury)
        e = self._eccentricity_earth_orbit(juliancentury)
 
        return (1.000001018 * (1 - e * e)) / (1 + e * cos(radians(v)))

    def _sun_rt_ascension(self, juliancentury):
        e = self._obliquity_correction(juliancentury)
        lambd = self._sun_apparent_long(juliancentury)
 
        tananum = (cos(radians(e)) * sin(radians(lambd)))
        tanadenom = (cos(radians(lambd)))

        return degrees(atan2(tananum, tanadenom))
