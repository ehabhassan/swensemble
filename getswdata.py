
def checkConnection():
    import httplib
    conn = httplib.HTTPConnection("www.google.com")
    try:
        conn.request("HEAD", "/")
        return True
    except:
        return False

def getOMNIfiles(omniDates,dataLoc,omniSet='hourly'):
    import os
    import glob

    omniSet = omniSet.lower()

    if dataLoc[len(dataLoc)-1] == "/":
     dataLoc = dataLoc[:len(dataLoc)]
    else:
     dataLoc = dataLoc[:len(dataLoc)] + "/"

    fnames = []

    for i in range(len(omniDates)):
     if i > 0:
      if omniDates[i] == omniDates[i-1]:
       continue
      elif omniDates[i].year == omniDates[i-1].year:
       if omniDates[i].month == omniDates[i-1].month:
        continue
       elif omniSet == 'hourly':
        if omniDates[i].month <= 6 and omniDates[i-1].month <= 6:
         continue
        elif omniDates[i].month >= 7 and omniDates[i-1].month >= 7:
         continue

     omniYear = str(omniDates[i].year)
     if omniSet == 'hourly' and omniDates[i].month <= 6:
      omniDate = str(omniDates[i].year) + "0101"
     elif omniSet == 'hourly' and omniDates[i].month >= 7:
      omniDate = str(omniDates[i].year) + "0701"
     else:
      omniDate = str(omniDates[i].year) + "%02d" % (omniDates[i].month) + "01"

     if omniSet=='hourly' and int(omniYear) >= 1963:
      fullPath = 'spdf.gsfc.nasa.gov/pub/data/omni/omni_cdaweb/hourly/' + str(omniYear) + '/omni2_h0_mrg1hr_' + str(omniDate) + '*.cdf'
     elif omniSet=='5min' and int(omniYear) >= 1981:
      fullPath = 'spdf.gsfc.nasa.gov/pub/data/omni/omni_cdaweb/hro_5min/' + str(omniYear) + '/omni_hro_5min_' + str(omniDate) + '*.cdf'
     elif omniSet=='1min' and int(omniYear) >= 1981:
      fullPath = 'spdf.gsfc.nasa.gov/pub/data/omni/omni_cdaweb/hro_1min/' + str(omniYear) + '/omni_hro_1min_' + str(omniDate) + '*.cdf'
     else:
      fullPath = ""
      print(omniSet + '-' + omniYear + ' OMNI data is not available. Only 1hour (1963:), 5min (1981:), 1min (1981:).')
      return ""

     if sorted(glob.glob(dataLoc + fullPath)) == []:
      print("OMNI data could not be found locally, try to download OMNI data from destination ....")
      if checkConnection():
       webPath = "ftp://" + fullPath[:len(fullPath)]
       print("Connect to " + webPath)
       envComm = "wget -P /home/ehab/SWData" + " -r -l1 -A.cdf " + webPath
       print(envComm)
       os.system(envComm)
      else:
       print("No internet connection found ... Check you network settings.")

     localPath = dataLoc + fullPath
     fnames.extend(glob.glob(localPath))

    return sorted(fnames)

def getOMNIparams(omniDates,dataLoc,omniSet='hourly'):
    from spacepy import pycdf

    OMNIfnames  = getOMNIfiles(omniDates,dataLoc,omniSet)
    if len(OMNIfnames) > 0:
     cdfKeys = pycdf.CDF(OMNIfnames[0])
    else:
     cdfKeys = "--empty--"
    return cdfKeys


def getOMNIdata(omniDates,dataLoc,dataList,omniSet='hourly',dataStat='raw'):
    from spacepy import pycdf

    OMNIfnames = getOMNIfiles(omniDates,dataLoc,omniSet)
    OMNIparams = getOMNIparams(omniDates,dataLoc,omniSet)

    dataStorage = []
    for j in range(len(dataList)+1):
     dataStorage.append([])

    aFlage = True
    for j in range(len(dataList)):
     if dataList[j] in OMNIparams:
      for i in range(len(OMNIfnames)):
       cdf = pycdf.CDF(OMNIfnames[i])
       dataStorage[j].extend(list(cdf[dataList[j]]))
       if aFlage: dataStorage[len(dataList)].extend(list(cdf['Epoch']))
      if aFlage: aFlage = False
      cdf.close()
     else:
       print dataList[j], ' is not available in OMNI CDF File!'

    swData = {'Epoch':dataStorage[len(dataList)]}
    for j in range(len(dataList)):
     if dataStat == 'clean':
      if dataList[j] == 'V': dataStorage[j] = dataClean(dataStorage[j],[2500],['>='])
      if dataList[j] == 'N': dataStorage[j] = dataClean(dataStorage[j],[999.0,0.0],['>=','<='])
      if dataList[j] == 'T': dataStorage[j] = dataClean(dataStorage[j],[1.0e7],['>='])
      if dataList[j] == 'ABS_B': dataStorage[j] = dataClean(dataStorage[j],[0.0],['<='])
      if dataList[j] == 'BX_GSE': dataStorage[j] = dataClean(dataStorage[j],[0.0],['<='])
      if dataList[j] == 'BY_GSE': dataStorage[j] = dataClean(dataStorage[j],[0.0],['<='])
      if dataList[j] == 'BZ_GSE': dataStorage[j] = dataClean(dataStorage[j],[0.0],['<='])
     swData[dataList[j]] = dataStorage[j]

    return swData
    

def getACEfiles(aceDates,dataLoc,aceSet='hourly',aceDat='magnetic'):
    import os
    import glob

    aceSet = aceSet.lower()
    aceDat = aceDat.lower()

    if dataLoc[len(dataLoc)-1] == "/":
     dataLoc = dataLoc[:len(dataLoc)]
    else:
     dataLoc = dataLoc[:len(dataLoc)] + "/"

    fnames = []

    for i in range(len(aceDates)):
     if i > 0:
      if aceDates[i] == aceDates[i-1]:
       continue
      elif aceDates[i].year == aceDates[i-1].year:
       if aceDates[i].month == aceDates[i-1].month:
        if aceDates[i].day == aceDates[i-1].day:
         continue

     aceYear = str(aceDates[i].year)
     aceDate = str(aceDates[i].year) + "%02d" % (aceDates[i].month) + "%02d" % (aceDates[i].day)
     if aceDat == 'plasma':
      if aceSet == 'hourly' and int(aceYear) >= 1998:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/swepam/level_2_cdaweb/swe_h2/' + str(aceYear) + '/ac_h2_swe_' + str(aceDate) + '*.cdf'
      elif aceSet == '23min' and int(aceYear) >= 1998:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/swepam/level_2_cdaweb/swe_h0/' + str(aceYear) + '/ac_h0_swe_' + str(aceDate) + '*.cdf'
      elif aceSet == '5min' and int(aceYear) >= 2011:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/swepam/level_2_cdaweb/swe_k0/' + str(aceYear) + '/ac_k0_swe_' + str(aceDate) + '*.cdf'
      else:
       fullPath = ""
       print(aceSet + ' ACE Plasma data is not available. Only 1hour (1998:), 23min (1998:), 5min (2011:).')
       return ""
     
     if aceDat == 'magnetic':
      if aceSet == 'hourly' and int(aceYear) >= 1998:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/mag/level_2_cdaweb/mfi_h2/' + str(aceYear) + '/ac_h2_mfi_' + str(aceDate) + '*.cdf'
      elif aceSet == '4min' and int(aceYear) >= 1998:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/mag/level_2_cdaweb/mfi_h1/' + str(aceYear) + '/ac_h1_mfi_' + str(aceDate) + '*.cdf'
      elif aceSet == '5min' and int(aceYear) >= 2011:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/mag/level_2_cdaweb/mfi_k0/' + str(aceYear) + '/ac_k0_mfi_' + str(aceDate) + '*.cdf'
      elif aceSet == '16sec' and int(aceYear) >= 1998:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/mag/level_2_cdaweb/mfi_h0/' + str(aceYear) + '/ac_h0_mfi_' + str(aceDate) + '*.cdf'
      elif aceSet == '1sec' and int(aceYear) >= 1998:
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/ace/mag/level_2_cdaweb/mfi_h3/' + str(aceYear) + '/ac_h3_mfi_' + str(aceDate) + '*.cdf'
      else:
       fullPath = ""
       print(aceSet + '-' + aceYear + ' ACE Magnetic data is not available. Only 1hour (1998:), 5min (2011:), 4min (1998:), 16sec (1998:), 1sec (1998:).')
       return ""

     if sorted(glob.glob(dataLoc + fullPath)) == []:
      print("ACE data could not be found locally, try to download ACE data from destination ....")
      if checkConnection():
       webPath = "ftp://" + fullPath[:len(fullPath)]
       print("Connect to " + webPath)
       envComm = "wget -P " + dataLoc + " -r -l1 -A.cdf " + webPath
       print(envComm)
       os.system(envComm)
      else:
       print("No internet connection found ... Check you network settings.")

     localPath = dataLoc + fullPath
     fnames.extend(glob.glob(localPath))

    return sorted(fnames)

def getACEparams(aceDates,dataLoc,aceSet='hourly',aceDat='magnetic'):
    from spacepy import pycdf

    aceSet = aceSet.lower()
    aceDat = aceDat.lower()

    if aceDat == 'magnetic':
     ACEfnames  = getACEfiles(aceDates,dataLoc,aceSet,aceDat='magnetic')
    elif aceDat == 'plasma':
     ACEfnames  = getACEfiles(aceDates,dataLoc,aceSet,aceDat='plasma')
    if len(ACEfnames) > 0:
     cdfKeys = pycdf.CDF(ACEfnames[0])
    else:
     cdfKeys = "--empty--"
    return cdfKeys

def getACEdata(aceDates,dataLoc,dataList,aceSet=['hourly'.'hourly'],dataStat='raw'):
    from numpy import transpose
    from spacepy import pycdf

    aceSet = aceSet.lower()
    dataStat = dataStat.lower()

    if len(aceSet) == 2:
     ACEBfnames = getACEfiles(aceDates,dataLoc,aceSet[0],aceDat='magnetic')
     ACEBparams = getACEparams(aceDates,dataLoc,aceSet[0],aceDat='magnetic')
     ACEPfnames = getACEfiles(aceDates,dataLoc,aceSet[1],aceDat='plasma')
     ACEPparams = getACEparams(aceDates,dataLoc,aceSet[1],aceDat='plasma')
    elif len(aceSet) == 1:
     ACEBfnames = getACEfiles(aceDates,dataLoc,aceSet[0],aceDat='magnetic')
     ACEBparams = getACEparams(aceDates,dataLoc,aceSet[0],aceDat='magnetic')
     ACEPfnames = getACEfiles(aceDates,dataLoc,aceSet='hourly',aceDat='plasma')
     ACEPparams = getACEparams(aceDates,dataLoc,aceSet='hourly',aceDat='plasma')

    dataStorage = []
    for j in range(len(dataList)+2):
     dataStorage.append([])

    bFlage = True
    pFlage = True
    for j in range(len(dataList)):
     if dataList[j] in ACEBparams:
      for i in range(len(ACEBfnames)):
       cdf = pycdf.CDF(ACEBfnames[i])
       dataStorage[j].extend(list(cdf[dataList[j]]))
       if bFlage: dataStorage[len(dataList)].extend(list(cdf['Epoch']))
      if bFlage: bFlage = False
      cdf.close()
     elif dataList[j] in ACEPparams:
      for i in range(len(ACEPfnames)):
       cdf = pycdf.CDF(ACEPfnames[i])
       dataStorage[j].extend(list(cdf[dataList[j]]))
       if pFlage: dataStorage[len(dataList)+1].extend(list(cdf['Epoch']))
      if pFlage: pFlage = False
      cdf.close()
     else:
       print dataList[j], ' is not available in ACE CDF File!'

    swData = {'magneticEpoch':dataStorage[len(dataList)],'plasmaEpoch':dataStorage[len(dataList)+1]}
    for j in range(len(dataList)):
     if dataList[j] in ['BGSEc','V_GSE']:
      swData[dataList[j]] = transpose(dataStorage[j])
     else:
      swData[dataList[j]] = dataStorage[j]
      if dataStat == 'clean':
       if dataList[j] == 'Np': swData[dataList[j]] = dataClean(swData[dataList[j]],[9999,0],['>=','<'])
       if dataList[j] == 'Vp': swData[dataList[j]] = dataClean(swData[dataList[j]],[2500,-2500],['>=','<='])
       if dataList[j] == 'Magnitude': swData[dataList[j]] = dataClean(swData[dataList[j]],[-999],['<='])
       if dataList[j] == 'Tpr': swData[dataList[j]] = dataClean(swData[dataList[j]],[0],['<'])

    return swData

    
def getIMP8files(imp8Dates,dataLoc,imp8Set='15sec',imp8Dat='magnetic'):
    import os
    import glob

    imp8Set = imp8Set.lower()
    imp8Dat = imp8Dat.lower()

    if dataLoc[len(dataLoc)-1] == "/":
     dataLoc = dataLoc[:len(dataLoc)]
    else:
     dataLoc = dataLoc[:len(dataLoc)] + "/"

    fnames = []

    for i in range(len(imp8Dates)):
     if i > 0:
      if imp8Dates[i] == imp8Dates[i-1]:
       continue
      elif imp8Dates[i].year == imp8Dates[i-1].year:
       if imp8Dates[i].month == imp8Dates[i-1].month:
        if imp8Dates[i].day == imp8Dates[i-1].day:
         continue

     imp8Year = str(imp8Dates[i].year)
     imp8Date = str(imp8Dates[i].year) + "%02d" % (imp8Dates[i].month) + "%02d" % (imp8Dates[i].day)

     if imp8Dat == 'magnetic':
      if imp8Set == '15sec' and (int(imp8Year) >= 1973 and int(imp8Year) <= 2000):
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/imp/imp8/mag/mag_15sec_cdaweb/' + str(imp8Year) + '/i8_15sec_mag_' + str(imp8Date) + '*.cdf'
      elif imp8Set == '320msec' and (int(imp8Year) >= 1973 and int(imp8Year) <= 2000):
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/imp/imp8/mag/mag_320msec_cdaweb/' + str(imp8Year) + '/i8_320msec_mag_' + str(imp8Date) + '*.cdf'
      else:
       fullPath = ""
       print(imp8Set + '-' + imp8Year + ' IMP8 magnetic data is not available. Only 320msec and 15sec (1973-2000).')
       return ""

     if imp8Dat == 'plasma':
      if imp8Set == '4min' and (int(imp8Year) >= 1973 and int(imp8Year) <= 2006):
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/imp/imp8/plasma_mit/mitplasma_h0/' + str(imp8Year) + '/i8_h0_mitplasma_' + str(imp8Date) + '*.cdf'
      else:
       fullPath = ""
       print(imp8Set + '-' + imp8Year + ' IMP8 magnetic data is not available. Only 4min (1973-2006).')
       return ""

     if sorted(glob.glob(dataLoc + fullPath)) == []:
      print("IMP8 data could not be found locally, try to download IMP8 data from destination ....")
      if checkConnection():
       webPath = "ftp://" + fullPath[:len(fullPath)]
       print("Connect to " + webPath)
       envComm = "wget -P " + dataLoc + " -r -l1 -A.cdf " + webPath
       print(envComm)
       os.system(envComm)
      else:
       print("No internet connection found ... Check you network settings.")

     localPath = dataLoc + fullPath
     fnames.extend(glob.glob(localPath))

    return sorted(fnames)

def getIMP8params(imp8Dates,dataLoc,imp8Set='15sec',imp8Dat='magnetic'):
    from spacepy import pycdf

    imp8Set = imp8Set.lower()
    imp8Dat = imp8Dat.lower()

    if imp8Dat == 'magnetic':
     IMP8fnames  = getIMP8files(imp8Dates,dataLoc,imp8Set,imp8Dat='magnetic')
    elif imp8Dat == 'plasma':
     IMP8fnames  = getIMP8files(imp8Dates,dataLoc,imp8Set,imp8Dat='plasma')
    if len(IMP8fnames) > 0:
     cdfKeys = pycdf.CDF(IMP8fnames[0])
    else:
     cdfKeys = "--empty--"
    return cdfKeys

def getIMP8data(imp8Dates,dataLoc,dataList,imp8Set=['15sec','4min'],dataStat='raw'):
    from numpy import transpose
    from spacepy import pycdf

    imp8Set = imp8Set.lower()
    dataStat = dataStat.lower()

    if len(imp8Set) ==2:
     IMP8Bfnames = getIMP8files(imp8Dates,dataLoc,imp8Set[0],imp8Dat='magnetic')
     IMP8Bparams = getIMP8params(imp8Dates,dataLoc,imp8Set[0],imp8Dat='magnetic')
     IMP8Pfnames = getIMP8files(imp8Dates,dataLoc,imp8Set[1],imp8Dat='plasma')
     IMP8Pparams = getIMP8params(imp8Dates,dataLoc,imp8Set[1],imp8Dat='plasma')
    elif len(imp8Set) ==1:
     IMP8Bfnames = getIMP8files(imp8Dates,dataLoc,imp8Set[0],imp8Dat='magnetic')
     IMP8Bparams = getIMP8params(imp8Dates,dataLoc,imp8Set[0],imp8Dat='magnetic')
     IMP8Pfnames = getIMP8files(imp8Dates,dataLoc,imp8Set='4min',imp8Dat='plasma')
     IMP8Pparams = getIMP8params(imp8Dates,dataLoc,imp8Set='4min',imp8Dat='plasma')

    dataStorage = []
    for j in range(len(dataList)+2):
     dataStorage.append([])

    bFlage = True
    pFlage = True
    for j in range(len(dataList)):
     if dataList[j] in IMP8Bparams:
      for i in range(len(IMP8Bfnames)):
       cdf = pycdf.CDF(IMP8Bfnames[i])
       if bFlage: dataStorage[len(dataList)].extend(list(cdf['Epoch']))
       fData = list(cdf[dataList[j]])
       dataStorage[j].extend(fData)
      if bFlage: bFlage = False
      cdf.close()
     elif dataList[j] in IMP8Pparams:
      for i in range(len(IMP8Pfnames)):
       cdf = pycdf.CDF(IMP8Pfnames[i])
       if pFlage: dataStorage[len(dataList)+1].extend(list(cdf['Epoch']))
       fData = list(cdf[dataList[j]])
       dataStorage[j].extend(fData)
      if pFlage: pFlage = False
      cdf.close()
     else:
      print dataList[j], ' is not available in ACE CDF File!'

    swData = {'magneticEpoch':dataStorage[len(dataList)], 'plasmaEpoch':dataStorage[len(dataList)+1]}
    for j in range(len(dataList)):
     if dataList[j] == 'B_Vector_GSE':
      swData[dataList[j]] = transpose(dataStorage[j])
      if dataStat == 'clean':
       swData[dataList[j]][0] = dataClean(swData[dataList[j]][0],[9999],['>='])
       swData[dataList[j]][1] = dataClean(swData[dataList[j]][1],[9999],['>='])
       swData[dataList[j]][2] = dataClean(swData[dataList[j]][2],[9999],['>='])
     elif dataList[j] == 'proton_density_fit':
      swData[dataList[j]] = dataStorage[j]
      if dataStat == 'clean':
       swData[dataList[j]] = dataClean(swData[dataList[j]],[99,0],['>=','<'])
     else:
      swData[dataList[j]] = dataStorage[j]
      if dataStat == 'clean':
       swData[dataList[j]] = dataClean(swData[dataList[j]],[999],['>='])

    return swData


def getWINDfiles(windDates,dataLoc,windSet='1min',windDat='all'):
    import os
    import glob

    windSet = windSet.lower()
    windDat = windDat.lower()

    if dataLoc[len(dataLoc)-1] == "/":
     dataLoc = dataLoc[:len(dataLoc)]
    else:
     dataLoc = dataLoc[:len(dataLoc)] + "/"

    fnames = []

    for i in range(len(windDates)):
     if i > 0:
      if windDates[i] == windDates[i-1]:
       continue
      elif windDates[i].year == windDates[i-1].year:
       if windDates[i].month == windDates[i-1].month:
        if windDates[i].day == windDates[i-1].day:
         continue

     windYear = str(windDates[i].year)
     windDate = str(windDates[i].year) + "%02d" % (windDates[i].month) + "%02d" % (windDates[i].day)

     if windDat == 'all' and int(windYear) >= 1994:
      fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/wind/swe/swe_h1/' + str(windYear) + '/wi_h1_swe_' + str(windDate) + '*.cdf'
     else:
      fullPath = ""
      print(windSet + '-' + windYear +' WIND magnetic data is not available. Only (1994:).')
      return ""

     if windDat == 'magnetic' and int(windYear) >= 1994:
      if windSet == '1min':
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/wind/mfi/mfi_h2/' + str(windYear) + '/wi_h2_mfi_' + str(windDate) + '*.cdf'
      else:
       fullPath = ""
       print(windSet + '-' + windYear + ' WIND magnetic data is not available. Only 1min (1994:).')
       return ""

     if windDat == 'iplasma' and (int(windYear) >= 1994 and int(windYear) <= 2001):
      if windSet == '6min':
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/wind/swe/swe_h1/' + str(windYear) + '/wi_h1_swe_' + str(windDate) + '*.cdf'
      else:
       fullPath = ""
       print(windSet + '-' + windYear + ' WIND Ion Plasma data is not available. Only 6 min (1994 - 2001).')
       return ""

     if windDat == 'eplasma' and int(windYear) >= 2002:
      if windSet == '100min':
       fullPath = 'cdaweb.gsfc.nasa.gov/pub/data/wind/swe/swe_h5/' + str(windYear) + '/wi_h5_swe_' + str(windDate) + '*.cdf'
      else:
       fullPath = ""
       print(windSet + '-' + windYear + ' WIND Electron PLasma data is not available. Only 100 min (2002:).')
       return ""

     if sorted(glob.glob(dataLoc + fullPath)) == []:
      print("WIND data could not be found locally, try to download WIND data from destination ....")
      if checkConnection():
       webPath = "ftp://" + fullPath[:len(fullPath)]
       print("Connect to " + webPath)
       envComm = "wget -P " + dataLoc + " -r -l1 -A.cdf " + webPath
       print(envComm)
       os.system(envComm)
      else:
       print("No internet connection found ... Check you network settings.")

     localPath = dataLoc + fullPath
     fnames.extend(glob.glob(localPath))

    return sorted(fnames)

def getWINDparams(windDates,dataLoc,windSet='1min',windDat='all'):
    from spacepy import pycdf

    windSet = windSet.lower()
    windDat = windDat.lower()

    if windDat == 'all':
     WINDfnames  = getWINDfiles(windDates,dataLoc,windSet,windDat='all')
    elif windDat == 'magnetic':
     WINDfnames  = getWINDfiles(windDates,dataLoc,windSet,windDat='magnetic')
    elif windDat == 'iplasma':
     WINDfnames  = getWINDfiles(windDates,dataLoc,windSet,windDat='iplasma')
    elif windDat == 'eplasma':
     WINDfnames  = getWINDfiles(windDates,dataLoc,windSet,windDat='eplasma')
    if len(WINDfnames) > 0:
     cdfKeys = pycdf.CDF(WINDfnames[0])
    else:
     cdfKeys = "--empty--"
    return cdfKeys

def getWINDdata(windDates,dataLoc,dataList,windSet=['hourly'],dataStat='raw'):
    from spacepy import pycdf

    if len(windSet) == 1:
     WINDfnames = getWINDfiles(windDates,dataLoc,windSet[0])
     WINDparams = getWINDparams(windDates,dataLoc,windSet[0])
    elif len(windSet) == 2:
     WINDBfnames = getWINDfiles(windDates,dataLoc,windSet[0],windDat='magnetic')
     WINDBparams = getWINDparams(windDates,dataLoc,windSet[0],windDat='magnetic')
     if windDates[i].year <= 2001
      WINDPfnames = getWINDfiles(windDates,dataLoc,windSet[1],windDat='iPlasma')
      WINDPparams = getWINDparams(windDates,dataLoc,windSet[1],windDat='iPlasma')
     elif windDates[i].year >= 2002
      WINDPfnames = getWINDfiles(windDates,dataLoc,windSet[1],windDat='ePlasma')
      WINDPparams = getWINDparams(windDates,dataLoc,windSet[1],windDat='ePlasma')

    dataStorage = []
    for j in range(len(dataList)+1):
     dataStorage.append([])

    aFlage = True
    for j in range(len(dataList)):
     if dataList[j] in WINDparams:
      for i in range(len(WINDfnames)):
       cdf = pycdf.CDF(WINDfnames[i])
       dataStorage[j].extend(list(cdf[dataList[j]]))
       if aFlage: dataStorage[len(dataList)].extend(list(cdf['Epoch']))
      if aFlage: aFlage = False
      cdf.close()
     else:
       print dataList[j], ' is not available in OMNI CDF File!'

    swData = {'Epoch':dataStorage[len(dataList)]}
    for j in range(len(dataList)):
     if dataStat == 'clean':
      if dataList[j] == 'Proton_V_nonlin': dataStorage[j] = dataClean(dataStorage[j],[2500],['>='])
      if dataList[j] == 'Proton_Np_nonlin': dataStorage[j] = dataClean(dataStorage[j],[999.0,0.0],['>=','<='])
      if dataList[j] == 'BZ': dataStorage[j] = dataClean(dataStorage[j],[999.0],['>='])
     swData[dataList[j]] = dataStorage[j]

    return swData


def dataClean(myList,threshold,operand):
    for i in range(len(myList)):
     for j in range(len(threshold)):
      if operand[j] == '>=':
       if myList[i] >= threshold[j]:
        myList[i] = float('nan')
      elif operand[j] == '<=':
       if myList[i] <= threshold[j]:
        myList[i] = float('nan')
      elif operand[j] == '==':
       if myList[i] == threshold[j]:
        myList[i] = float('nan')
      elif operand[j] == '<':
       if myList[i] < threshold[j]:
        myList[i] = float('nan')
      elif operand[j] == '>':
       if myList[i] > threshold[j]:
        myList[i] = float('nan')
    return myList


def dateShift(oldDate, years=0, months=0, days=0, hours=0, minutes=0, seconds=0):
    from datetime import datetime, timedelta

    month = oldDate.month - 1 + months
    year = oldDate.year + month / 12 + years
    month = month % 12 + 1
    day = oldDate.day
    hour = oldDate.hour
    minute = oldDate.minute
    second = oldDate.second
    newDate = datetime(year,month,day,hour,minute,second) + timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)

    return newDate


def dateList(sDate, eDate, shift = 'day'):
    shift = shift.lower()
    dList = []
    if shift == 'day' or shift == 'days':
     diff = eDate - sDate
     for i in range(diff.days + 1):
      dList = dList + [dateShift(sDate, days = i)]
    elif shift == 'month' or shift == 'months':
     if eDate.year - sDate.year == 0:
      diff = eDate.month - sDate.month
     elif eDate.year - sDate.year != 0:
      diff = (eDate.year - sDate.year) * 12 + abs(eDate.month - sDate.month)
     for i in range(diff + 1):
      dList = dList + [dateShift(sDate, months = i)]
    elif shift == 'year' or shift == 'years':
     diff = eDate.year - sDate.year
     for i in range(diff + 1):
      dList = dList + [dateShift(sDate, years = i)]
    elif shift == 'hour' or shift == 'hours':
     diff = eDate - sDate
     for i in range(diff.seconds / 3600 + 1):
      dList = dList + [dateShift(sDate, hours = i)]
    elif shift == 'minute' or shift == 'minutes':
     diff = eDate - sDate
     for i in range(diff.seconds / 60 + 1):
      dList = dList + [dateShift(sDate, minutes = i)]
    elif shift == 'second' or shift == 'seconds':
     diff = eDate - sDate
     for i in range(diff.seconds + 1):
      dList = dList + [dateShift(sDate, seconds = i)]

    return dList 
     
