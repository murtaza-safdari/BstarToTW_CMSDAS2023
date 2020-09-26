from TIMBER.Tools.Common import openJSON

def getNormFactor(setname,year,configPath,genEventCount):
    # Config loading - will have cuts, xsec, and lumi
    if isinstance(configPath,str): config = openJSON(configPath)
    else: config = configPath
    cuts = config['CUTS'][year]
    lumi = config['lumi']
    if setname in config['XSECS'].keys(): 
        xsec = config['XSECS'][setname]
    else:
        raise KeyError('Key "%s" does not exist in config["XSECS"]'%setname)

    norm = (xsec*lumi)/genEventCount

    return norm