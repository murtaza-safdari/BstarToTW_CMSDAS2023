def getNormFactor(configPath,genEventCount):
    # Config loading - will have cuts, xsec, and lumi
    config = openJSON(configPath)
    cuts = config['CUTS'][options.year]
    lumi = config['lumi']
    if setname in config['XSECS'].keys(): 
        xsec = config['XSECS'][setname]
    else:
        raise KeyError('Key "%s" does not exist in config["XSECS"]'%setname)

    norm = (xsec*lumi)/genEventCount

    return norm