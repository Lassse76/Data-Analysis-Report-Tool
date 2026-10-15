import yaml

data ={}
model_config = {}
cf={}

#requirement: /
#result: config_final has been read
def readconfig_final():
    global cf
    with open("data/config_final.yaml") as f:
            cf= yaml.safe_load(f)

#requirement: input is dict
#result: config has been written 
def write(dict):
    with open("data/config.yaml","w") as f:
        yaml.safe_dump(dict,f)

#requirement: /
#result: config_final has been resetted
def resetconfig_final():
    with open("data/config_final.yaml","w") as f:
            pass

#requirement: /
#result: config has been read
def read():
    global data
    with open("data/config.yaml") as f:
        data= yaml.safe_load(f)

#requirement: input is dict
#result: config_final has been written
def writeConfig(mc):
    with open("data/config_final.yaml","a") as f:
            yaml.safe_dump(mc,f)

#requirement: /
#result: model_config has been read
def readModelConfig(src):
    global model_config
    with open(src) as f:
        model_config = yaml.safe_load(f)

#requirement: input is dict
#result: model_config is changed
def changeModelConfig(dic):
    global model_config
    
    def _merge(base, upd):
        result = base.copy()
        for key, value in upd.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = _merge(result[key], value)
            else:
                result[key] = value
        return result
    
    model_config = _merge(model_config, dic)  


    
#requirement: /
#result: config is updated    
def updateConfig():
    
    write(data)

#requirement: input is dict
#result: config is changed
def changeConfig(dic):
    global data

    def _merge(base, upd):
        result = base.copy()
        for key, value in upd.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = _merge(result[key], value)
            else:
                result[key] = value
        return result

    data = _merge(data, dic)  


    







