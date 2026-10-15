import json
import yaml
import pandas as pd
import prediction as pr
import sample as sa
import imputation as im
import mice as mi
import evaluate as ev
import config as co


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
def run(src,type="Mice",seed =42,test_split_size=0.2,target="mortality",kwds=None): #innit function, under constructions
    co.read()
    co.readconfig_final()
    
    co.changeConfig({"seed":seed})
    co.changeConfig({"imputation":{"type":type}})
    co.changeConfig({"testsplit":test_split_size})
    co.changeConfig({"target":target})
    if kwds != None:
        co.changeConfig(kwds)
    co.writeConfig(co.data)
    for lookup,model_config,amount,output_name in zip(co.data["path"]["lookup_table"],co.data["path"]["model_config"],co.data["missingness"]["amount"],co.data["path"]["output_name"]):
        for i in range(co.data["multiply"]):
            output_name = ("R"*i)+output_name 
            co.readModelConfig(model_config)
            co.resetconfig_final()
            
            
        
        
        

            df = sa.innit(src=src)
            create_mapping(df,"mortality",lookup)
            df_new= sa.innit(src=src,exclude=co.data["exclude"])   
            df_comp = sa.complete_dataset(df_new,method="linear")
            train_x ,test_x = sa.split(df_comp)

            (test_x,test_y) = sa.target(test_x,"mortality")
            (train_x,train_y) = sa.target(train_x,"mortality")
            #x = pr.classifier(train_x,train_y,test_x,threshold=0.5)
            #print(ev.predictionevaluation(test_y,x,method="f1_score"))
            
            prop=mi.calcamount(amount,df_comp,co.model_config["pa.MultivariateAmputation"]["patterns"])
            if co.model_config["pa.MultivariateAmputation"]["patterns"] != None:
                df_incomp_train = mi.create_missingness(train_x,**{"prop":prop,"patterns":co.model_config["pa.MultivariateAmputation"]["patterns"]})
                df_incomp_test = mi.create_missingness(test_x,**{"prop":prop,"patterns":co.model_config["pa.MultivariateAmputation"]["patterns"]})
            else:
                df_incomp_train = mi.create_missingness(train_x)
                df_incomp_test = mi.create_missingness(test_x)
                
                #print(df_incomp_train.isna().sum())
            (test,train) = (mi.innit(final_mapping,df_incomp_test,"test",df_comp=test_x,output_name=output_name),mi.innit(final_mapping,df_incomp_train,"train",df_comp=train_x,output_name=output_name))
            results = []
            for te_file,tr_file in zip(test,train):

                with open(tr_file,"r") as file:
                        train = pd.read_csv(file)
                with open(te_file,"r") as file:
                        test = pd.read_csv(file)
                train_std,test_std = sa.standardize(train,test)
                pred_mod=pr.classifier(train_std,train_y,test_std,threshold=0.5)
                results.append(ev.predictionevaluation(test_y,pred_mod,method="f1_score"))
            print(results)
            print(sum(results)/len(results))



        







    #Fehler beim split?