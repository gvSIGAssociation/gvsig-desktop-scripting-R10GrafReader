# encoding: utf-8

import gvsig

from org.gvsig.fmap.dal.feature.spi.simpleprovider import AbstractSimpleSequentialReaderFactory
from org.gvsig.fmap.dal.feature.spi.simpleprovider import AbstractSimpleSequentialReader
from gvsig import getResource
import re
import os.path
from java.net import URL
from java.io import File
from r10grafparser import R10GrafParser

class R10GrafReaderFactory(AbstractSimpleSequentialReaderFactory):

  def __init__(self):
    AbstractSimpleSequentialReaderFactory.__init__(self, "R10G", "R10 fichero grafico", ("xml","r10g"))

  def accept(self, pathname):
    # Este metodo es opcional, si con la extension del fichero es
    # suficiente, no hace falta sobreescribirlo.
    if not AbstractSimpleSequentialReaderFactory.accept(self,pathname):
      return False
    f = open(pathname.getAbsolutePath(),"r")
    head = f.read(500)
    f.close()
    head = head.lower()
    head = head.replace("\r","").replace("\n"," ")
    #print pathname, repr(head)
    return ("<r10_graf" in head) and ("<ca>" in head) and ("<expediente" in head) and ("<campana>" in head)

  def fetchDefaultParameters(self, params):
    # Este metodo es opcional, si el fichero de datos no aporta ningun valor
    # de entre los requeridos en los parametros (como es el SRS), no hace
    # falta sobreescribirlo.
    pathname = params.getFile().getAbsolutePath()
    f = open(pathname,"r")
    head = f.read(200)
    f.close()
    head = head.lower()
    head = head.replace("\r","").replace("\n"," ")
    m = re.compile(".*<srid>([0-9]*)</srid>.*").match(head)
    if m!=None:
      srs = "EPSG:%s" % m.group(1)
      params.setDynValue("CRS",srs)
    

  def createReader(self, params):
    reader = R10GrafReader(self, params)
    return reader
  
class R10GrafReader(AbstractSimpleSequentialReader):

  def __init__(self, factory, parameters):
    AbstractSimpleSequentialReader.__init__(self,factory, parameters)
    self._parser = None

  def getName(self):
    return os.path.splitext(self.getFile().getName())[0]
    
  def getFieldNames(self):
    fields = [
      "CA:Integer",
      "CAMPANA:Long",
      "NUMEXP:Long",
      "NUMPAR:Integer",
      "LINCOD:Long",
      "PR:Integer",
      "MU:Integer",
      "AG:Integer",
      "ZO:Integer",
      "PO:Integer",
      "PA:Integer",
      "RE:Integer",
      "GEOMETRY:MultiPolygon:geomSubtype:2D"
    ]
    return fields
  
    
  def getFile(self):
    return self.getParameters().getFile()
    
  def read(self):
    if self._parser == None:
      self._parser = R10GrafParser(self.getFile().getAbsolutePath())
      self._parser.open()
    return self._parser.read()
    
  def rewind(self):
    if self._parser == None:
      self._parser = R10GrafParser(self.getFile().getAbsolutePath())
      self._parser.open()
    self._parser.rewind()
    
  def close(self):
    self._parser = None

def selfRegister():
  factory = R10GrafReaderFactory()
  factory.selfRegister(
    URL("file://"+getResource(__file__,"R10GParameters.xml")),
    URL("file://"+getResource(__file__,"R10GMetadata.xml")),
  )

def test(factory, fname):
  if not factory.accept(File(fname)):
    print "File not supported by this factory ", factory.getName()
    return
  params = factory.createStoreProviderFactory().createParameters()
  params.setFile(File(fname))
  factory.fetchDefaultParameters(params)
  reader = factory.createReader(params)
  print "Reader: ", reader.getFactory().getName()
  print "Name: ", reader.getName()
  print "File: ", reader.getFile()
  print "Fields: ", reader.getFieldNames()

  n = 0
  line = reader.read()
  while line!=None and n<10:
    print line
    line = reader.read()
    n += 1
  reader.close()
  reader.rewind() # test rewind
    

def main(*args):
  selfRegister()
  test(R10GrafReaderFactory(), "/home/jjdelcerro/datos/geodata/vector/R10/2018/r10graf.xml")
  pass

  