#!/usr/bin/env python
# Copyright (c) 2006-2007, Fazal Majid. All rights reserved
# This code is hereby placed in the public domain
import sys, time, datetime, serial, struct, pprint

if sys.platform == 'darwin':
  serial_port = '/dev/cu.usbserial'
elif sys.platform == 'linux2':
  serial_port = '/dev/ttyUSB0'
elif sys.platform == 'win32':
  # this port varies from PC to PC
  serial_port = 'COM3'
else:
  serial_port = 0

version = '$Id: cs1504.py,v 1.5 2007/01/29 05:47:42 majid Exp majid $'
# Revision history:
# $Log: cs1504.py,v $
# Revision 1.5  2007/01/29 05:47:42  majid
# per Tom Eastmond's recommendation, added Linux serial port device defaults
#
# Revision 1.4  2007/01/20 08:36:48  majid
# added public domain license comment
#
# Revision 1.3  2006/10/19 17:47:10  majid
# AssertionError, not AssertError
#
# Revision 1.1  2006/04/14 19:21:10  majid
# check in March and April articles
#
# Revision 1.2  2006/04/05 21:08:20  majid
# fix for Windows, suggested by Joseph C. Brill
#

########################################################################
# bar code conventions

def format_isbn(isbn):
  """Produce an ISBN check digit"""
  # calculate check digit
  isbn = isbn.replace('-', '')
  assert len(isbn) >= 9 and len(isbn) <= 10
  check = 0
  for i in range(9):
    check += (10 - i) * (ord(isbn[i]) - ord('0'))
  check = -check % 11
  if check == 10:
    check = 'X'
  else:
    check = str(check)
  if len(isbn) > 9:
    assert isbn[-1] == check
  else:
    isbn = isbn + check
  # see http://www.isbn-international.org/en/userman/chapter4.html
  # XXX I need to implement a complete ISBN digit grouper
  return isbn

def expand(symbology, code):
  """Expand certain types of common book codes"""
  # 10-digit ISBNs are encoded as EAN-13 with the charming fictitious country
  # code 978, a.k.a. "bookland"
  # see http://www.adams1.com/pub/russadam/isbn.html
  if symbology.startswith('EAN-13') and code.startswith('978'):
    symbology = 'ISBN'
    code = format_isbn(code[3:12])
  return symbology, code

########################################################################
# Symbol CS 1504 protocol

symbologies = {
  0x16: 'Bookland',
  0x0E: 'MSI',
  0x02: 'Codabar',
  0x11: 'PDF-417',
  0x0c: 'Code 11',
  0x26: 'Postbar (Canada)',
  0x20: 'Code 32',
  0x1e: 'Postnet (US)',
  0x03: 'Code 128',
  0x23: 'Postal (Australia)',
  0x01: 'Code 39',
  0x22: 'Postal (Japan)',
  0x13: 'Code 39 Full ASCII',
  0x27: 'Postal (UK)',
  0x07: 'Code 93',
  0x1c: 'QR code',
  0x1d: 'Composite',
  0x31: 'RSS limited',
  0x17: 'Coupon',
  0x30: 'RSS-14',
  0x04: 'D25',
  0x32: 'RSS Expanded',
  0x1b: 'Data Matrix',
  0x24: 'Signature',
  0x0f: 'EAN-128',
  0x15: 'Trioptic Code 39',
  0x0b: 'EAN-13',
  0x08: 'UPCA',
  0x4b: 'EAN-13+2',
  0x48: 'UPCA+2',
  0x8b: 'EAN-13+5',
  0x88: 'UPCA+5',
  0x0a: 'EAN-8',
  0x09: 'UPCE',
  0x4a: 'EAN-8+2',
  0x49: 'UPCE+2',
  0x8a: 'EAN-8+5',
  0x89: 'UPCE+5',
  0x05: 'IATA',
  0x10: 'UPCE1',
  0x19: 'ISBT-128',
  0x50: 'UPCE1+2',
  0x21: 'ISBT-128 concatenated',
  0x90: 'UPCE1+5',
  0x06: 'ITF',
  0x28: 'Macro PDF'
  }
MAX_RESP = 6144

class CS1504:

  def __init__(self, port='/dev/cu.usbserial'):
    attempts = 0
    connected = False
    while not connected:
      try:
        attempts += 1
        self.ser = serial.Serial(port,
                                 baudrate=9600,
                                 bytesize=8,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 timeout=2)
        connected = True
      except serial.SerialException:
        if attempts <= 2:
          print('connection on', port, 'failed, retrying', file=sys.stderr)
          time.sleep(2.0)
        else:
          print('giving up', file=sys.stderr)
          raise
    self.delta = datetime.timedelta(0)
    self.serial = None
    self.sw_ver = None
    self.last_barcodes = []

  def interrogate(self):
    """Initiate communications with the scanner"""
    print('Using device', self.ser.portstr + '... ', end=' ', file=sys.stderr)
    count = 0
    while count < 50:
      self.send('\x01\x02\x00')
      try:
        data = self.recv(23)
      except AssertionError:
        time.sleep(1.0)
        data = None
      if not data:
        count += 1
        time.sleep(0.2)
        continue
      print('connected', file=sys.stderr)
      break
    if not data:
      raise IOError
    version, status = map(ord, data[2:4])
    assert status in [0, 22]
    if status == 22:
      print('WARNING: Battery low', file=sys.stderr)
    self.serial = data[4:12]
    self.sw_ver = data[12:20]
    assert data[20] == '\0'
    print('serial#', self.serial.encode('hex'), file=sys.stderr)
    print('SW version', self.sw_ver, file=sys.stderr)

  def get_time(self):
    """Get the time set in the scanner and calculate drift"""
    print('reading clock for drift', file=sys.stderr)
    self.send('\x0a\x02\x00')
    self.time_response(True)

  def set_time(self):
    """Reset the time in the scanner"""
    print('resetting scanner clock...', end=' ', file=sys.stderr)
    now = list(datetime.datetime.now().timetuple()[0:6])
    now[0] -= 2000
    now.reverse()
    self.send('\x09\x02\x06' + ''.join(map(chr, now)) + '\0')
    self.time_response()
    print('done', file=sys.stderr)

  def time_response(self, calculate_drift=False):
    now = datetime.datetime.now()
    data = self.recv(12)
    assert data[2] == '\x06'
    s, mi, h, d, m, y = map(ord, data[3:9])
    y += 2000
    ts = datetime.datetime(y, m, d, h, mi, s)
    # determine the clock drift so we can correct timestamps
    if calculate_drift:
      self.delta = now - ts
      print('clock drift', self.delta, file=sys.stderr)
      if abs(self.delta).seconds > 60:
        print('WARNING: big gap between host & scanner clocks', end=' ', file=sys.stderr)
        print(self.delta, file=sys.stderr)

  def get_barcodes(self):
    """Retrieve the bar codes and timestamps from the scanner's memory, and
    correct for clock drift
    """
    print('reading barcodes...', end=' ', file=sys.stderr)
    count = 0
    # retry up to 5 times
    while count < 5:
      try:
        self.send('\x07\x02\x00')
        data = self.recv()
        assert data[2:10] == self.serial, data[2:10].encode('hex')
        break
      except AssertionError:
        count += 1
        time.sleep(0.2)
    self.last_barcodes = []
    data = data[10:-3]
    while data:
      length = ord(data[0])
      first, data = data[1:length+1], data[length+1:]
      symbology = symbologies.get(ord(first[0]), 'UNKNOWN')
      code = first[1:-4]
      t = struct.unpack('>I', first[-4:])[0]
      y = 2000 + int(t & 0x3f)
      t >>= 6
      m = int(t & 0x0f)
      t >>= 4
      d = int(t & 0x1f)
      t >>= 5
      h = int(t & 0x1f)
      t >>= 5
      mi = int(t & 0x3f)
      t >>= 6
      s = int(t & 0x3f)
    
      # Pour eviter bug sur secondes
      try :
        if s < 0 or s > 59 :
            s = 0
      except :
        s = 0
        
      ts = datetime.datetime(y, m, d, h, mi, s) + self.delta
      symbology, code = expand(symbology, code)
      self.last_barcodes.append((symbology, code, ts))
    print('done (%d read)' % len(self.last_barcodes), file=sys.stderr)
    return self.last_barcodes

  def clear_barcodes(self):
    """Clear the bar codes in the scanner's memory"""
    print('clearing barcodes...', end=' ', file=sys.stderr)
    self.send('\x02\x02\x00')
    data = self.recv(5)
    print('done', file=sys.stderr)
      
  def power_down(self):
    """Shut the scanner down to conserve battery life"""
    print('powering down...', end=' ', file=sys.stderr)
    self.send('\x05\x02\x00')
    data = self.recv(5)
    print('done', file=sys.stderr)
      
  def send(self, cmd):
    """Send a command to the scanner"""
    self.ser.write(cmd)
    self.ser.write(crc16(cmd))

  def recv(self, length=MAX_RESP):
    """Receive a response. For fixed-size responses, specifying it will take
    less time as we won't need to wait for the timeout to return data
    """
    data = self.ser.read(length)
    if data:
      assert data.startswith('\x06\x02'), data.encode('hex')
      assert data[-2:] == crc16(data[:-2])
      assert data[-3] == '\0'
    return data

  def close(self):
    self.ser.close()

  def __del__(self):
    self.close()
    del self.ser

########################################################################
# Modified from:
# http://news.hping.org/comp.lang.python.archive/18112.html
# to use the algorithm as specified by Symbol
# original crc16.py by Bryan G. Olson, 2005
# This module is free software and may be used and
# distributed under the same terms as Python itself.
import array
def crc16(string, value=0):
  """CRC function using Symbol's specified algorithm
  """
  value = 0xffff
  for ch in string:
    value = table[ord(ch) ^ (value & 0xff)] ^ (value >> 8)
  #return value
  return struct.pack('>H', (~value) & 0xFFFF)

# CRC-16 poly: p(x) = x**16 + x**15 + x**2 + 1
# top bit implicit, reflected
poly = 0xa001
table = array.array('H')
for byte in range(256):
     crc = 0
     for bit in range(8):
         if (byte ^ crc) & 1:
             crc = (crc >> 1) ^ poly
         else:
             crc >>= 1
         byte >>= 1
     table.append(crc)

assert crc16('\x01\x02\x00') == '\x9f\xde', \
       map(hex, map(ord, crc16('\x01\x02\x00')))

if __name__ == '__main__':
    for x in range(0, 3) :
      scanner = CS1504(serial_port)
      scanner.interrogate()
      scanner.get_time()
      scanner.set_time()
      barcodes = scanner.get_barcodes()
      for symbology, code, timestamp in barcodes:
        print('%s,%s,%s' % (symbology, code, str(timestamp).split('.')[0]))
    ##  if barcodes:
    ##    scanner.clear_barcodes()
      scanner.power_down()
      del scanner
