# encoding: utf-8

import gvsig

from org.gvsig.fmap.geom.aggregate import MultiPolygon
from org.gvsig.scripting.app.extension import ScriptingUtils
from org.gvsig.fmap.geom import GeometryUtils
from org.xmlpull.v1 import XmlPullParser
from java.io import File
from org.xmlpull.v1 import XmlPullParserException
from org.xmlpull.v1 import XmlPullParserFactory
from java.io import File, FileInputStream
from org.gvsig.tools import ToolsLocator

class R10GrafParser(object):
  
  def __init__(self, fname, skipEmptyGeometries):
    self.fname = fname
    self.skipEmptyGeometries = skipEmptyGeometries
    self.xml = None
    factory = XmlPullParserFactory.newInstance(ToolsLocator.getInstance().getXmlPullParserFactoryClassNames(),None)
    self.parser = factory.newPullParser()
    self.initValues()

        
  def isDone(self):
    return self.done

  def open(self):
    ScriptingUtils.log(ScriptingUtils.WARN, "Loading file xml "+ self.fname)
    self.resource = FileInputStream(File(self.fname))
    self.parser.setInput(self.resource, None);
    ScriptingUtils.log(ScriptingUtils.WARN, "File loaded.")
    self.initValues()
    self.readInitValues()

  def readInitValues(self):
    self.parser.nextTag()
    self.parser.require(XmlPullParser.START_TAG, None, "r10_graf")

    self.parser.nextTag()
    self.parser.require(XmlPullParser.START_TAG, "", "ca")

    self.ca = self.parser.nextText()

    self.parser.nextTag()
    self.campana = self.parser.nextText()

    self.parser.nextTag()

    self.srid = self.parser.nextText()

    self.parser.nextTag()
    

  def readExpediente(self):
    ## Start with expediente
    self.num_expediente = 0
    self.parser.require(XmlPullParser.START_TAG, "", "expediente")

    ## Attributo del expediente -> num_expediente
    for i in range(0, self.parser.getAttributeCount()):
        name = self.parser.getAttributeName(i)
        if name=="num_expediente":
          self.num_expediente = self.parser.getAttributeValue(i)
    self.parser.nextTag()

  def rewind(self):
    factory = XmlPullParserFactory.newInstance(ToolsLocator.getInstance().getXmlPullParserFactoryClassNames(),None)
    self.parser = factory.newPullParser()
    self.initValues()
    self.open()

  def initValues(self):
    # Reset and init values
    self.done = False
    self.num_expediente = 0
    self.num_parcela = 0
    
    self.lin_codigo = 0
    self.pr = 0
    self.mu = 0
    self.ag = 0
    self.zo = 0
    self.po = 0
    self.pa = 0
    self.re = 0
    self.wkt = ""
    
  def checkAndTransformWKT(self, wkt):
    geom = None
    if wkt!=None:
      if "EMPTY" in wkt:
        #ScriptingUtils.log(ScriptingUtils.WARN, "La geometria no es valida en %s:%s, el poligono esta vacio" % (self.num_expediente, self.num_parcela))
        pass
      else:
        geom = GeometryUtils.createFrom(wkt, self.srid)
        if geom!=None and not geom.isValid():
          #status = geom.getValidationStatus()
          #msg = status.getMessage()
          #ScriptingUtils.log(ScriptingUtils.WARN, "La geometria no es valida en %s:%s, %s" % (self.num_expediente, self.num_parcela, msg))
          geom = None
      
      if geom!=None and not isinstance(geom,MultiPolygon):
        geom = geom.toPolygons()
    return geom
    
  def read(self):
    if self.isDone():
      return None
    self.next()
    # skipEmptyGeometries: Search for geom
      
    #if self.num_expediente == None:
    #  return None
    
    geom = self.checkAndTransformWKT(self.wkt)
    
    while geom==None and self.skipEmptyGeometries==True and not self.isDone():
      self.next()
      geom = self.checkAndTransformWKT(self.wkt)

    if geom==None and self.skipEmptyGeometries==True:
      return None
    

    values = [
        int(self.ca),
        long(self.campana),
        long(self.num_expediente),
        int(self.num_parcela),
        long(self.lin_codigo),
        int(self.pr),
        int(self.mu),
        int(self.ag),
        int(self.zo),
        int(self.po),
        int(self.pa),
        int(self.re),
        geom
    ]
    
    return values

  def next(self):
    self.lin_codigo = 0
    self.pr = 0
    self.mu = 0
    self.ag = 0 
    self.zo = 0
    self.po = 0
    self.pa = 0
    self.re = 0
    self.wkt = ""
    if self.parser.getEventType() == XmlPullParser.END_TAG and self.parser.getName()=="r10_graf":
        self.done = True
        return None
    if self.parser.getEventType() == XmlPullParser.START_TAG and self.parser.getName()=="expediente":
      self.readExpediente()
    if self.parser.getEventType() == XmlPullParser.START_TAG and self.parser.getName()=="parcela":
      self.num_parcela = 0
      for i in range(0, self.parser.getAttributeCount()):
        name = self.parser.getAttributeName(i)
        value = self.parser.getAttributeValue(i)
        if name == "num_parcela":
          self.num_parcela = value
      self.parser.nextTag()
    self.parser.require(XmlPullParser.START_TAG, "", "linea")

    for i in range(0, self.parser.getAttributeCount()):
      name = self.parser.getAttributeName(i)
      value = self.parser.getAttributeValue(i)
      if name == "lin_codigo":
        self.lin_codigo = value
      if name == "pr":
        self.pr = value
      if name == "mu":
        self.mu = value
      if name == "ag":
        self.ag = value 
      if name == "zo":
        self.zo = value
      if name == "po":
        self.po = value
      if name == "pa":
        self.pa = value
      if name == "re":
        self.re = value
    self.parser.nextTag()
    
    if self.parser.getName() == "wkt":
      self.parser.require(XmlPullParser.START_TAG, "", "wkt")
      self.wkt = self.parser.nextText()
      self.parser.require(XmlPullParser.END_TAG, "", "wkt")
      self.parser.nextTag()
    self.parser.require(XmlPullParser.END_TAG, "", "linea")
    self.parser.nextTag()
    if self.parser.getEventType() == XmlPullParser.START_TAG and self.parser.getName()=="linea":
      return
    self.parser.require(XmlPullParser.END_TAG, "", "parcela")
    self.parser.nextTag()
    if self.parser.getEventType() == XmlPullParser.END_TAG and self.parser.getName()=="expediente":
      self.parser.nextTag()
      if self.parser.getEventType() == XmlPullParser.END_TAG and self.parser.getName()=="r10_graf":
          self.done = True
          return
    return

def main():
  #from r10grafreader import test, selfRegister, R10GrafReaderFactory
  #selfRegister()
  fname = "/home/osc/R10Graf/r10graf.xml"
  fname = "/home/osc/R10Graf/BDA_R10_graf18_1728062018_001.xml"
  fname = "/home/osc/R10Graf/r10withnones.xml"
  #test(R10GrafReaderFactory(), fname)
  # Uso del pull en java: DynclassImportHelper
  # importDefinitions
  parser = R10GrafParser(fname, True)
  parser.open()
  
  print "Values:", parser.read()
  #print parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()
  print "Values:", parser.read()