import yaml
import pylatex 
from pathlib import Path

import pandas as pd

cfg_dict = {}
cfg_df = ""
tripod = {}
sh_survey = r"""

General | Answer|
---|---|
dataset name|...|
origin country of study data| ...|
amount of variables|...|
data-lacking groups | ...|
distribution across those groups|...|
reason for missingness in data-lacking groups|...|

Missingness | Answer|
---|---|
amount of missingness|...|
amount of missingness across all data-lacking groups|...|
amount of missingness in non-data-lacking group|...|
amount of heavy data-lacking entries and their group distribution|...|
definition of heavy data-lacking data|...|
top 3 groups with most missingness|...|
group with least missingness|...|
variables with no missingness|...|
top 3 variables with the least missingness (variables with no missingness excluded)|...|
top 3 variables with the most missingness|...|
reason for different missingness level in different studies|...|

Dealing with Missingness | Answer|
---|---|
Method to complete dataset (for groundtruth)|...|
Method for inducing missingness|...|
Amount of induced missingness|...|
Amount of induced MCAR missingness|...|
Amount of induced MAR missingness|...|
Amount of induced MNAR missingness|...|
Methods to take data-lacking groups more into account|...|
Imputation method|...|
How many imputed dataset|...|
Method to combine imputed datasets|...|

Machine learning Model | Answer|
---|---|
Model used|...|
Parameters|...|

Evaluation|Answer|
---|---|
Model used|...|
Parameters|...|
further steps to get to the result|...|
Results|...|

Other|Answer|
---|---|
Link to Code|...|
Main libraries used|...|
Link to AI usage declaration|...|
"""

triai_survey= r"""

Section|Item|Answer|
---|---|---|
Title|1|...|
Context|3a|...|
Reference to existing models|3a|...|
Target population|3b|...|
Inteded purpose of the prediction model in the context of the care pathway|3b|...|
Intended users|3b|...|
any known health inequalities between sociodemographic groups|3c|...|
study objection|4|...|
Describes wether the study is about the developement or validation of a prediction model|4|...|
Sources of both evaluation and developement datasets|5a|...|
Rationale for using this data|5a|...|
Represantativeness of the data|5a|...|
Collection date of patient data (begin and end of study)|5b|...|
Specify key elements of study and number and location of centers|5b|...|
Describe eligibility criteria for study participants|6b|...|
Detail of treatment received and how handled in developement or evaluation if relevant|6c|...|
Data pre-processing and quality checking|7|...|
Whether pre-processing was similar across sociodemographic groups|7|...|
Definition of the predicted outcome|8a|...|
Time horizon of the outcome|8a|...|
How and when the outcome was assessed|8a|...|
Rationale for choosing this outcome|8a|...|
Consistency of outcome assessment across sociodemographic groups|8a|...|
Qualifications and demographic characteristics of outcome assessors (if subjective interpretation required)|8b|...|
Actions to blind assessment of the outcome|8c|...|
Choice of initial predictors (e.g. literature, previous models, all available)|9a|...|
Pre-selection of predictors before model building|9a|...|
Definition of all predictors|9b|...|
How and when predictors were measured|9b|...|
Actions to blind assessment of predictors (for outcome and other predictors)|9b|...|
Qualifications and demographic characteristics of predictor assessors (if subjective interpretation required)|9c|...|
How the study size was arrived at (development and evaluation separately)|10|...|
Justification that the study size was sufficient|10|...|
Details of sample size calculation|10|...|
How missing data were handled|11|...|
Reasons for omitting any data|11|...|
How the data were used (development / evaluation of model performance)|12a|...|
Data partitioning, considering sample size requirements|12a|...|
Handling of predictors (functional form, rescaling, transformation, standardisation)|12b|...|
Type of model|12c|...|
Rationale for the model choice|12c|...|
All model building steps|12c|...|
Hyperparameter tuning|12c|...|
Method for internal validation|12c|...|
Handling and quantification of heterogeneity in parameters and performance across clusters (e.g. hospitals, countries)|12d|...|
Measures and plots used to evaluate model performance (discrimination, calibration, clinical utility) and their rationale|12e|...|
Methods to compare multiple models (if relevant)|12e|...|
Model updating (e.g. recalibration) overall or for sociodemographic groups / settings|12f|...|
How model predictions were calculated for evaluation (formula, code, object, API)|12g|...|
Whether class imbalance methods were used, why and how|13|...|
Methods to recalibrate the model or predictions after class imbalance handling|13|...|
Approaches used to address model fairness|14|...|
Rationale for fairness approaches|14|...|
Output of the prediction model (e.g. probabilities, classification)|15|...|
Details and rationale for any classification|15|...|
How classification thresholds were identified|15|...|
Differences between development and evaluation data (setting, eligibility, outcome, predictors)|16|...|
Institutional review board / ethics committee that approved the study|17|...|
Informed consent or ethics committee waiver|17|...|
Source of funding and role of funders|18a|...|
Conflicts of interest and financial disclosures of all authors|18b|...|
Where the study protocol can be accessed (or statement that none was prepared)|18c|...|
Registration information (register name, number) or statement of non-registration|18d|...|
Availability of study data|18e|...|
Availability of analytical code|18f|...|
Patient and public involvement (or statement of no involvement)|19|...|
Flow of participants through the study (diagram if helpful)|20a|...|
Number of participants with and without the outcome|20a|...|
Summary of follow-up time (if applicable)|20a|...|
Participant characteristics overall and per data source / setting|20b|...|
Key dates, key predictors (incl. demographics), treatments, sample size, outcome events, follow-up time|20b|...|
Amount of missing data|20b|...|
Differences across key demographic groups|20b|...|
Comparison of predictor, demographic and outcome distributions with development data (evaluation)|20c|...|
Number of participants and outcome events per analysis (development, tuning, evaluation)|21|...|
Details of the full prediction model (formula, code, object, API) for use and third-party evaluation|22|...|
Restrictions to access or reuse of the model (e.g. freely available, proprietary)|22|...|
Model performance estimates with confidence intervals|23a|...|
Performance for key subgroups (e.g. sociodemographic)|23a|...|
Results of heterogeneity in model performance across clusters (if examined)|23b|...|
Results of model updating, including updated model and its performance|24|...|
Overall interpretation of main results|25|...|
Interpretation of fairness issues in context of objectives and previous studies|25|...|
Limitations (e.g. non-representative sample, sample size, overfitting, missing data)|26|...|
Effects of limitations on bias, statistical uncertainty and generalisability|26|...|
How poor quality or unavailable input data should be assessed and handled in implementation|27a|...|
Required user interaction and level of expertise|27b|...|
Next steps for future research regarding applicability and generalisability|27c|...|

"""

#requirement: /
#result: config_final has been read
def read():
    global cfg_dict
    global cfg_df
    global cfg_md
    with open("data/config_final.yaml") as f:
        cfg_dict= yaml.safe_load(f)

    
    cfg_df = pd.json_normalize(cfg_dict,sep="__").T
    cfg_md = cfg_df.to_markdown(**{"headers":["Parameter","Answer"]})

#requirement: /
#result: markdown file with bullet points to answer has been created
def survery(type="short",file_name="survey"):
    if type == "short":
        with open(f"{file_name}.md","w") as f:
                f.write(sh_survey)

    if type=="tripod+ai":
         with open(f"{file_name}.md","w") as f:
                         f.write(triai_survey)


#requirement: /
#result: File with description table has been created
def extraction(output_type="latex",detailed=True):
    tables = {}
    
    print("Please fill out following survery.md file. Please use the corresponding tabular with short meaningfull answers.")

    while True:
            print("Done (y/n):")
            y = input()
            if y =="y":
                text = Path("survey.md").read_text(encoding="utf-8")
                tables = md_tables_to_dfs(text)

                text = ""
                for key,value in tables.items():
                    tables[key]= value[value["Answer"].astype(str).str.strip().str.replace("\u2026","...",regex=False) !="..."]
                    if not tables[key].empty:
                        text = text +"\n\n"+ tables[key].to_markdown(index=False)
                    
                break

    latex = []
    if detailed:
        read()
        latex_conf = cfg_df.to_latex(index=False,escape=True)
    print(cfg_md)
    for items in tables.values():
            latex.append(items.to_latex(index=False,escape=True))
    if output_type=="tex":
        with open("report.tex","w") as f:
            for el in latex:
                f.write(f"{el}\n")
            if detailed:
                f.write(f"\n\n{latex_conf}")
                
    if output_type =="txt" or output_type =="md":
        with open(f"report.{output_type}","w") as f:
           
            f.write(text)
            if detailed:
                f.write(f"\n\n{cfg_md}")
    





#requirement: /
#result: markdown table has been converted to dataframe
def md_table_to_df(text: str) -> pd.DataFrame:
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = [[c.strip() for c in l.strip("|").split("|")] for l in lines]
    header, body = rows[0], rows[2:]
    return pd.DataFrame(body, columns=header)


#requirement: /
#result: markdown file consists of tables has been converted to dict of dataframes
def md_tables_to_dfs(text: str) -> dict[str, pd.DataFrame]:
    tables = {}
    for block in text.strip().split("\n\n"):
        lines = block.strip().splitlines()
        if len(lines) >= 2 and lines[1].strip().lstrip("|").startswith("---"):
            df = md_table_to_df(block)
            tables[df.columns[0]] = df
    return tables






