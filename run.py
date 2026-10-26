import json
import yaml
import pandas as pd
import prediction as pr
import sample as sa
import imputation as im
import mice as mi
import evaluate as ev
import config as co

from itertools import chain


mapping = {}
exclude = []
final_mapping = {}




#requirement: /
#result: Lookup table is loaded and initialized and specifications saved in mapping
def loadlookup(target,src_lookup):
    with open(src_lookup,"r") as file:
        data = yaml.safe_load(file)
    global mapping #mapping is a dictionary which saves the different methods to use from the lookup table
    for variables in data["variables"]: #Looks for synonyme or different spellings for a word in the data to connect them to corresponding methods
        if variables["synonym"] ==[]: #if there is no synonym only check id name
            if variables["id"]==target:
                mapping[target]= [variables["method"],variables["variant"],variables["perturbation"]]
            continue
        for synonym in variables["synonym"]: #check if variable name in synonym list
            if synonym == target or variables["id"]==target:
                mapping[target]= [variables["method"],variables["variant"],variables["perturbation"]]

#requirement: /
#result: Columns to be exluded are extracted of mapping
def exractexclude(): 
    for col,item in mapping.items(): #Extract variables that should be excluded regarding the lookup table
        if item[0]=="None":
            exclude.append(col)
 

#requirement: /
#result: Mapping for selected method is extracted
def finalmapping(target):
    global final_mapping
    for col, item in mapping.items(): #Create the final mapping regarding the extracted variables
        if col not in exclude and col != target:
            final_mapping[col]=[item[0],item[1],item[2]]

#requirement: /
#result: Mapping is created
def create_mapping(df,target,src_lookup): #Pupeline for creating the mapping
    for col in df: 
        loadlookup(col.lower(),src_lookup)
    exractexclude()
    finalmapping(target)

#requirement: /
#result: Initialize run
def run(src,kwds=None): #innit function, under constructions
    res={}
    temp_res={}
    #config is read and parameter are written to config
    co.read()
    co.readconfig_final()
    
    if kwds != None:
        co.changeConfig(kwds)
    co.writeConfig(co.data)
    for method in co.data["evaluation"]["prediction_eval"]: #initialize dict to save evaluation results
        res[method]=[]
        temp_res[method]=[]
    for method in co.data["evaluation"]["imputation_eval"]:
        res[method+"train"]=[]
        temp_res[method+"train"]=[]
        res[method+"test"]=[]
        temp_res[method+"test"]=[]

    
    #load for every run correct config and run that config i times (according to multiply)
    for lookup,model_config,amount,output_name in zip(co.data["path"]["lookup_table"],co.data["path"]["model_config"],co.data["missingness"]["amount"],co.data["path"]["output_name"]):
        for i in range(co.data["multiply"]):
            
            output_name = ("R"*i)+output_name 
            co.readModelConfig(model_config)
            co.resetconfig_final()
            
            
        
        
        

            df = sa.innit(src=src) #load data
            create_mapping(df,"mortality",lookup) #load and initialize lookup settings
            df_new= sa.innit(src=src,exclude=co.data["exclude"]) #load data with excluded values in lookup settings

            train ,test = sa.split(df_new)
            (test_x,test_y) = sa.target(test,"mortality") #extract target
            (train_x,train_y) = sa.target(train,"mortality")
            train_comp,test_comp = sa.complete_dataset(train_x,method="linear"),sa.complete_dataset(test_x,method="linear") #fill missing values to get a baseline for imputation evaluation
            

            
           
            
            prop_test=mi.calcamount(amount,test_comp,co.model_config["pa.MultivariateAmputation"]["patterns"])
            prop_train=mi.calcamount(amount,train_comp,co.model_config["pa.MultivariateAmputation"]["patterns"]) #calculate amount of missingness (pyampute does not use a direct parameter for the amount of missingness)
            if co.model_config["pa.MultivariateAmputation"]["patterns"] != None:
                df_incomp_train = mi.create_missingness(train_comp,**{"prop":prop_train,"patterns":co.model_config["pa.MultivariateAmputation"]["patterns"]})
                df_incomp_test = mi.create_missingness(test_comp,**{"prop":prop_test,"patterns":co.model_config["pa.MultivariateAmputation"]["patterns"]})
            else:
                df_incomp_train = mi.create_missingness(train_comp)
                df_incomp_test = mi.create_missingness(test_comp)
            
            #run imputation 
            (test,train) = (mi.innit(final_mapping,df_incomp_test,"test",df_comp=test_x,output_name=output_name),mi.innit(final_mapping,df_incomp_train,"train",df_comp=train_x,output_name=output_name))
            
            for te_file,tr_file in zip(test,train): #for every imputed dataset run the prediction and evaluation

                with open(tr_file,"r") as file:
                        train = pd.read_csv(file,index_col=0)
                with open(te_file,"r") as file:
                        test = pd.read_csv(file,index_col=0)
                train_std,test_std = sa.standardize(train,test)
                mask_test = df_incomp_test.isna() & test_x.notna()
                mask_train = df_incomp_train.isna()

           

                pred_mod=pr.classifier(train_std,train_y,test_std,threshold=0.5)
                for method in co.data["evaluation"]["prediction_eval"]:
                    temp_res[method].append(ev.predictionevaluation(test_y,pred_mod,method=method))
                
                test_true = test_comp.to_numpy()[mask_test.to_numpy()]
                test =test.to_numpy()[mask_test.to_numpy()]
                train_true = train_comp.to_numpy()[mask_train.to_numpy()]
                train =train.to_numpy()[mask_train.to_numpy()]
            
                for method in co.data["evaluation"]["imputation_eval"]:
                    temp_res[method+"test"].append(ev.imputationevaluation(test_true,test,method=method))
                    temp_res[method+"train"].append(ev.imputationevaluation(train_true,train,method=method))


            for method in co.data["evaluation"]["prediction_eval"]:
                res[method].append(sum(temp_res[method])/len(temp_res[method])) #calculate the average evaluation for every run (sum from every dataset evaluation:amount of datasets)
                temp_res[method]=[]
            for method in co.data["evaluation"]["imputation_eval"]:
                res[method+"train"].append(sum(temp_res[method+"train"])/len(temp_res[method+"train"])) #calculate the average evaluation for every run (sum from every dataset evaluation:amount of datasets)
                temp_res[method+"train"]=[]
                res[method+"test"].append(sum(temp_res[method+"test"])/len(temp_res[method+"test"])) #calculate the average evaluation for every run (sum from every dataset evaluation:amount of datasets)
                temp_res[method+"test"]=[]
    return res


        

