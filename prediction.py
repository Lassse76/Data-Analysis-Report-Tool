import imputation as im
import sample as sa
import config as co
from sklearn.ensemble import HistGradientBoostingClassifier,RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

#requirement: /
#result: Classify machine learning is applied
def classifier(train_x,train_y,test_x,method = "RandomForestClassifier",threshold = 0.5,**kwargs):
    
    if kwargs:
        
        co.changeModelConfig({f"sk.{method}":{**kwargs}})
    co.readconfig_final()
    if f"sk.{method}" not in co.cf:
        co.writeConfig({f"sk.{method}":co.model_config[f"sk.{method}"]})
        
    params = co.model_config[f"sk.{method}"]
    if method == "LogisticRegression":
        clf = LogisticRegression(**params).fit(train_x,train_y)
    elif method == "KNeighborsClassifier":
        clf = KNeighborsClassifier(**params).fit(train_x,train_y)
    elif method == "GaussianNB":
        clf = GaussianNB(**params).fit(train_x,train_y)
    elif method == "HistGradientBoostingClassifier":
        clf = HistGradientBoostingClassifier(**params).fit(train_x,train_y)

    else:
            clf = RandomForestClassifier(**params).fit(train_x,train_y)
    res = clf.predict_proba(test_x)[:,1]
    return (res>threshold).astype(int)

"""
df =sa.innit("data/ehr_test_data.csv",mapping=[("sex",{"M":1,"F":0}),("admission_type",{"Elective":1,"Urgent":2,"Emergency":3})],exclude=["patient_id"])
df_comp = sa.complete_dataset(df)
test_x ,train_x = sa.split(df_comp)

(test_x,test_y) = sa.target(test_x,"mortality")
(train_x,train_y) = sa.target(train_x,"mortality")


df_incomp_train = im.create_missingness(train_x,exclude=["sex","admission_type"])
df_incomp_test = im.create_missingness(test_x,exclude=["sex","admission_type"])
(train,test) =im.impute(df_incomp_train,test_split=df_incomp_test)

classifier(test,test_y,train,train_y)
"""