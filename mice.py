from pyampute.ampute import MultivariateAmputation
from statsmodels.imputation import mice
import statsmodels.api as sm
import sample as sa
import pandas as pd
import imputation as im
import config as co
import numpy as np

df = sa.innit(src="data/ehr_test_data.csv",exclude=["sex","patient_id","admission_type"])
df_inc = sa.innit(src="data/ehr_test_data.csv",exclude=["sex","patient_id","admission_type"])
df = sa.complete_dataset(df)


def calcamount(amount,df,patterns=None):

    if patterns==None:
        return None
    row =[len(f["incomplete_vars"])*f["freq"] for f in patterns]
    prop=0
    if amount != None:
        prop = amount* df.shape[1] / sum(row) #calculate the probability that a row has missing values

  
    if prop >=1 or prop <= amount: #missingness >1 = not enough cells with missingness assigned
        print("Problem with calculation")
        quit()

    return prop


    
#requirement: only numeric values
#result: Missingness is induced in the dataframe
def create_missingness(df,exclude=[],method="MultivariateAmputation",**kwargs):
    #update config_final
    if kwargs:
            
        co.changeModelConfig({f"pa.{method}":{**kwargs}})

    co.readconfig_final()
    if co.cf ==None or f"pa.{method}" not in co.cf:
        co.writeConfig({f"pa.{method}":co.model_config[f"pa.{method}"]})
    
            

    
    df_cp = df[exclude]
    df_ex = df.drop(columns = exclude) #drop columns that should not be amputed
    newdf = MultivariateAmputation(**kwargs).fit_transform(df_ex.select_dtypes("number")) # fit MultiariateAmputation
    newdf= pd.concat([df_cp,newdf],axis=1)

    return newdf #Leak could be created if train/test split is not done before


#requirement: /
#result: Dataframe with correlation of the given dataframe is returned
def correlation(df):
    return df.corr() #calculate correlation for the imputation formular 

#requirement: /
#result: Two lists as tupel are returned: ("Name of column","Everey correlation over a specific threshold")
def getmostcorr(df,mincorr=0.1):
    corrdf = correlation(df) 
    index = {}
    wheights = {}
    for name,values in corrdf.items():
        filter= (abs(values.values)>mincorr) & (values.index != name) #only take correlation above a specific threshhold
        wheights[name]= sorted(values.values[filter].tolist(),reverse=True,key=lambda t: abs(t))
        index[name]=[k for _,k in sorted(zip(values.values[filter].tolist(),values.index[filter].tolist()),reverse=True,key=lambda t: abs(t[0]))]
   
    return (index)

#requirement: /
#result: Settings are initialized for mice imputation
def converte(index,target,settings):
    model_class_map={ #mapping for values in lookup to get corresponding methods
        "sm.GLM":sm.GLM,
        "sm.OLS":sm.OLS
    }
    family_map={
        "sm.families.Poisson()":sm.families.Poisson(),
        "sm.families.Binomial()":sm.families.Binomial(),
        "sm.families.Gaussian()":sm.families.Gaussian()

    }
   
    config = {} #Dictionary with configuration as input for set_imputer 
    formula = "+".join(index[target])
    #config[target]= {"formula": formula, "model_class":model_class_map[settings[target][0]],"init_kwds": {"family":family_map[settings[target][1]],"weights":weights},"perturbation_method":settings[target][2]}
    if settings[target][0]=="sm.GLM":
        config[target]= {"formula": formula, "model_class":model_class_map[settings[target][0]],"perturbation_method":settings[target][2],"init_kwds": {"family":family_map[settings[target][1]]}}
    else:
        config[target]= {"formula": formula, "model_class":model_class_map[settings[target][0]],"perturbation_method":settings[target][2]}
    return (config)

#requirement: /
#result: Impute is initalized and run
def setimputer(df,config):
    imp = mice.MICEData(df) #Mice imputer initialized
    for col,kwds in config.items():
        imp.set_imputer(col,**kwds) #set_imputer with configuration set in converte function
    return imp

def impute(imp,type,micetype="detailedMice",burn_in=10,update_circle = 3,imputation_iteration = 10,df=pd.DataFrame(),output_name="R1"):
    if micetype=="justMice":
        imp = mice.MICEData(df) # if u want to use the standard statsmodel imputer, use justMice 
    file_name = []
    imp.update_all(burn_in) #burn in to train the imputer
    for i in range(imputation_iteration):
        imp.update_all(update_circle) #imputer is run #needs to updated
        imp.data.to_csv(f"data/imputations/{type}{output_name}{i}d.csv" )
        file_name.append(f"data/imputations/{type}{output_name}{i}d.csv")
    return file_name



#requirement: /
#result: Initialize mice imputazion and evaluate
def innit(settings,df,type,df_comp = pd.DataFrame(),burn_in=10,update_circle = 3,imputation_iteration = 10,output_name="R1"):
    keys = [*settings]
    if df_comp.empty: #fallback if df is not complete
        df_comp = sa.complete_dataset(df)
    index=getmostcorr(df)
    config = {}
    for col in keys: #config is created for every row
        if col not in index or not index[col]:
            continue
        cfg=converte(index,col,settings)
        config.update(cfg)
 
    imp_setting=setimputer(df,config)
    df_imputed = impute(imp_setting,type,df=df,burn_in=burn_in,update_circle=update_circle,imputation_iteration=imputation_iteration,output_name=output_name)
    return df_imputed
