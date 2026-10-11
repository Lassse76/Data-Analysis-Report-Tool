import pandas as pd
import config as co
from sklearn.metrics import auc,f1_score,roc_auc_score,mean_squared_error,root_mean_squared_error,average_precision_score,balanced_accuracy_score, matthews_corrcoef,brier_score_loss,log_loss,confusion_matrix
from sklearn.metrics import mean_absolute_error,r2_score,median_absolute_error



#requirement: /
#result: return imputation model evaluation from specified method
def imputationevaluation(df_true,df_pred,method="mean_squared_error",**kwargs):
    if kwargs:
                
        co.changeModelConfig({f"sk.{method}":{**kwargs}})
    
    co.readconfig_final()
    if f"sk.{method}" not in co.cf:
        co.writeConfig({f"sk.{method}":co.model_config[f"sk.{method}"]})
    if method=="root_mean_squared_error":
        return root_mean_squared_error(df_true,df_pred,**kwargs)
    if method =="mean_absolute_error":
        return mean_absolute_error(df_true,df_pred,**kwargs)
    if method =="r2_score":
        return r2_score(df_true,df_pred,**kwargs)
    if method =="median_absolute_error":
        return median_absolute_error(df_true,df_pred,**kwargs)
    return root_mean_squared_error(df_true,df_pred,**kwargs)

#requirement: /
#result: return prediction model evaluation from specified method
def predictionevaluation(df_true,df_pred,method="confusion_matrix",**kwargs):

    if kwargs:
                    
        co.changeModelConfig({f"sk.{method}":{**kwargs}})
        
    co.readconfig_final()
    if f"sk.{method}" not in co.cf:
        co.writeConfig({f"sk.{method}":co.model_config[f"sk.{method}"]})
    if method == "f1_score":
        return f1_score(df_true,df_pred,**kwargs)
    if method == "roc_auc_score":
        return roc_auc_score(y_true=df_true,y_score=df_pred,**kwargs)
    if method == "average_precision_score":
        return average_precision_score(df_true,df_pred,**kwargs)
    if method == "balanced_accuracy_score":
        return balanced_accuracy_score(df_true,df_pred,**kwargs)
    if method == "matthews_corrcoef":
        return matthews_corrcoef(df_true,df_pred,**kwargs)
    if method == "brier_score_loss":
        return brier_score_loss(df_true,df_pred,**kwargs)
    if method == "log_loss":
        return log_loss(df_true,df_pred)
    return confusion_matrix(df_true,df_pred,**kwargs)
    






