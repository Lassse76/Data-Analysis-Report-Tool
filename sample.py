import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

#requirement: correct file name with correct path,correct seperator if necessary
#result: dataframe with loaded data is given. If not possible error is given
def innit(src,type="csv",seperator =",",exclude=[],mapping = [("",{})]):
   # try:
        if type == "json": #currently only csv is accepted
            return ""
        else:
            df = pd.read_csv(src,sep=seperator)
            df_nonnumeric = df.select_dtypes(exclude=np.number) #exclude non numeric values only work in progress line 

            try:
                for value in exclude: #pop excluded variables out of dataframe
                    df.pop(value)
                for col,maps in mapping: # change values of variable regarding the before defined mapping
                    df[col]=df[col].map(maps)
            except: print("")
            finally: return df
    #except: 
        print("Error: Dataset not found")
        quit

#requirement: missing value identifier which pandas identify as nan
#result: Percentage of the five most present values in specific row and percentage of missing value is given

#requirement: 
#result: train test split is created and returned
def split(df,test=0.2,shuffle = True, stratify =""):
    if stratify =="":
        return train_test_split (df,test_size=test,stratify=df["mortality"],random_state=0,shuffle=shuffle) 
    return train_test_split (df,test_size=test,stratify=stratify,random_state=0,shuffle=shuffle) 
#requirement: 
#result: target is extracted
def target(df,target,dropfeature=True):
    if dropfeature:
        return (df.drop(columns= target),df[target]) #drop target
    return df[target]

#requirement: 
#result: Percentage of the five most present values of specific row and percentage of missing value is given
def analyzevalues(df,row):
    try:
        print(df[row].value_counts(normalize=True).mul(100).round(1).head(5))
        print(df[row].isna().mean())
    except:
        print("Error: Row not found")

#requirement: missing value identifier which pandas identify as nan
#result: Percentage of the five most present values in every row and percentage of missing value is given
def analyzevaluesall(df):
    try:
        for row in df:
            print(df[row].value_counts(normalize=True).mul(100).round(1).head(5))
            print(df[row].value_counts(normalize=True).mul(100).round(1).tail(5))
            print(df[row].isna().mean())
    
    except:
        print("Error: Row not found")

#requirement: method needs to exist and missing values have identifier which pandas identify as nan
#result: missing values are filled and returned
def complete_dataset(df,**kwargs): 
    #try:
        return df.interpolate(**kwargs).bfill()
    #except:
     #   print("Error:Dataframe or Method not found")




"""
df=innit("data/ehr_test_data.csv",mapping=[("sex",{"M":1,"F":0}),("admission_type",{"Elective":1,"Urgent":2,"Emergency":3})],exclude=["patient_id"])
analyze_counting(df,"heart_rate")
analyze_counting_all(df)
print(complete_dataset(df))"""
