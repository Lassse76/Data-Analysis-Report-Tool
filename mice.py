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


#requirement: only numeric values
#result: Missingness is induced in the dataframe
def create_missingness(df,exclude=[],method="MultivariateAmputation",**kwargs):
    if kwargs:
            
        co.changeModelConfig({f"pa.{method}":{**kwargs}})

    co.readconfig_final()
    if f"pa.{method}" not in co.cf:
        co.writeConfig({f"pa.{method}":co.model_config[f"pa.{method}"]})
    
            

    try:
        df_cp = df[exclude]
        df_ex = df.drop(columns = exclude)
        newdf = MultivariateAmputation(**kwargs).fit_transform(df_ex.select_dtypes("number")) # fit MultiariateAmputation
        newdf= pd.concat([df_cp,newdf],axis=1)

        return newdf #Leak could be created if train/test split is not done before
    except:
       print("Error:Amputation did not work")

#requirement: /
#result: Dataframe with correlation of the given dataframe is returned
def correlation(df):
    return df.corr() 

#requirement: /
#result: Two lists as tupel are returned: ("Name of column","Everey correlation over a specific threshold")
def getmostcorr(df,mincorr=0.1):
    corrdf = correlation(df) 
    index = {}
    wheights = {}
    for name,values in corrdf.items(): # only the top three  correlation over specific threshold are used
        filter= (abs(values.values)>mincorr) & (values.index != name)
        wheights[name]= sorted(values.values[filter].tolist(),reverse=True,key=lambda t: abs(t))
        index[name]=[k for _,k in sorted(zip(values.values[filter].tolist(),values.index[filter].tolist()),reverse=True,key=lambda t: abs(t[0]))]
   
    return (index)

#requirement: /
#result: Settings are initialized for mice imputation
def converte(index,target,settings):
    model_class_map={ #mapping for values in lookup mapping to get corresponding methods
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

def impute(imp,type,mice="detailedMice",burn_in=10,update_circle = 3,imputation_iteration = 10,df=pd.DataFrame()):
    if mice=="justMice":
        imp = mice.MICEData(df)
    file_name = []
    imp.update_all(burn_in)
    for i in range(imputation_iteration):
        imp.update_all(update_circle) #imputer is run #needs to updated
        imp.data.to_csv(f"data/imputations/{type}0{i}d.csv" )
        file_name.append(f"data/imputations/{type}0{i}d.csv")
    return file_name



    """print("inf im df:", np.isinf(df.select_dtypes("number")).sum()[lambda s: s > 0])

    for v in imp._cycle_order:
        try:
            imp.update(v)
        except np.linalg.LinAlgError:
            res = imp.results[v]
            print("Fehler bei:", v, "| Modell:", imp.model_class[v].__name__)
            print("Werte:", df[v].dropna().unique()[:10])
            print("params:", res.params)
            break"""



#requirement: /
#result: Initialize mice imputazion and evaluate
def innit(settings,df,type,df_comp = pd.DataFrame(),burn_in=10,update_circle = 3,imputation_iteration = 10):
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
    #formula,model_weights,config=converte(index,weights,"bmi",settings)
    imp_setting=setimputer(df,config)
    df_imputed = impute(imp_setting,type,burn_in=burn_in,update_circle=update_circle,imputation_iteration=imputation_iteration)
    return df_imputed
