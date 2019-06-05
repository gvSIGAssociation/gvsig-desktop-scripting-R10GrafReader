# encoding: utf-8

import gvsig

from org.gvsig.fmap.geom.aggregate import MultiPolygon
from org.gvsig.scripting.app.extension import ScriptingUtils
import xmltodic
from org.gvsig.fmap.geom import GeometryUtils

class R10GrafParser(object):
  
  def __init__(self, fname):
    self.fname = fname
    self.xml = None
    self.expedienteCorriente = None
    self.parcelaCorriente = None
    self.lineaCorriente = None
    self.ca = None
    self.campana = None
    self.srs = None
    self.expedientes = None
    self.expediente = None
    self.parcela = None
    self.linea = None

  def open(self):
    ScriptingUtils.log(ScriptingUtils.WARN, "Loading file xml "+ self.fname)
    fileKml = open(self.fname,"r")
    data = fileKml.read()
    fileKml.close()
    self.xml = xmltodic.parse(data)
    ScriptingUtils.log(ScriptingUtils.WARN, "File loaded.")

    self.ca = self.xml["r10_graf"]["ca"]
    self.campana = self.xml["r10_graf"]["campana"]
    self.srs = "EPSG:"+self.xml["r10_graf"]["srid"]
    self.expedientes = self.xml["r10_graf"]["expediente"]

    self.rewind()

  def rewind(self):
    self.expediente = None
    self.parcela = None
    self.linea = None
    self.expedienteCorriente = 0
    self.parcelaCorriente = 0
    self.lineaCorriente = 0
    self.expediente = self.getExpedientes(self.xml)[self.expedienteCorriente]    
    self.parcela =  self.getParcelas(self.expediente)[self.parcelaCorriente]
    self.linea =  self.getLineas(self.parcela)[self.lineaCorriente]
  
  def getExpedientes(self, xml):
    expedientes = xml["r10_graf"]["expediente"]
    if not isinstance(expedientes,list):
      expedientes = [ expedientes ]
    return expedientes
    
  def getParcelas(self, expediente):
    parcelas = expediente["parcela"]
    if not isinstance(parcelas,list):
      parcelas = [ parcelas ]
    return parcelas
    
  def getLineas(self, parcela):
    lineas = parcela["linea"]
    if not isinstance(lineas,list):
      lineas = [ lineas ]
    return lineas
  
  def read(self):
    if self.expediente == None:
      return None
    num_expediente = self.expediente["@num_expediente"]
    num_parcela = self.parcela["@num_parcela"]
    geom = None
    wkt = self.linea.get("wkt",None)
    if wkt!=None:
      if "EMPTY" in wkt:
        ScriptingUtils.log(ScriptingUtils.WARN, "La geometria no es valida en %s:%s, el poligono esta vacio" % (num_expediente, num_parcela))
      else:
        geom = GeometryUtils.createFrom(wkt, self.srs)
        if not geom.isValid():
          #status = geom.getValidationStatus()
          msg = ""#status.getMessage()
          ScriptingUtils.log(ScriptingUtils.WARN, "La geometria no es valida en %s:%s, %s" % (num_expediente, num_parcela, msg))
          geom = None
    
    if geom!=None and not isinstance(geom,MultiPolygon):
      geom = geom.toPolygons()
      
    #print num_expediente, num_parcela, self.linea["@lin_codigo"]
    values = [
        self.ca,
        self.campana,
        num_expediente,
        num_parcela,
        self.linea["@lin_codigo"],
        self.linea["@pr"],
        self.linea["@mu"],
        self.linea["@ag"],
        self.linea["@zo"],
        self.linea["@po"],
        self.linea["@pa"],
        self.linea["@re"],
        geom
    ]
    self.next()
    return values

  def next(self):
    lineas = self.getLineas(self.parcela)
    self.lineaCorriente += 1
    if self.lineaCorriente<len(lineas):
      self.linea = lineas[self.lineaCorriente]
      return
    parcelas = self.getParcelas(self.expediente)
    self.parcelaCorriente += 1
    if self.parcelaCorriente<len(parcelas):
      self.lineaCorriente = 0
      self.parcela = parcelas[self.parcelaCorriente]
      self.linea = self.getLineas(self.parcela)[self.lineaCorriente]
      return
    expedientes = self.getExpedientes(self.xml)
    self.expedienteCorriente += 1
    if self.expedienteCorriente<len(expedientes):
      self.lineaCorriente = 0
      self.parcelaCorriente = 0
      self.expediente = self.getExpedientes(self.xml)[self.expedienteCorriente]
      self.parcela = self.getParcelas(self.expediente)[self.parcelaCorriente]
      self.linea = self.getLineas(self.parcela)[self.lineaCorriente]
      return
    # Es fin de fichero
    self.expediente = None
    self.parcela = None
    self.linea = None

