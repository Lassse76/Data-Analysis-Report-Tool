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

tri_survey= r"""


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
    cfg_md = cfg_df.to_markdown()

#requirement: /
#result: markdown file with bullet points to answer has been created
def survery(type="short",file_name="survey"):
    if type == "short":
        with open(f"{file_name}.md","w") as f:
                f.write(sh_survey)


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
                break

    latex = []
    if detailed:
        read()
        latex_conf = cfg_df.to_latex(index=False,escape=True)
        
    for items in tables.values():
            latex.append(items.to_latex(index=False,escape=True))
    if output_type=="latex":
        with open("report.tex","w") as f:
            for el in latex:
                f.write(f"{el}\n")
            if detailed:
                f.write(latex_conf)
                
    if output_type =="txt":
        with open("report.txt","w") as f:
            f.write(text)
            if detailed:
                f.write(cfg_md)
        





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






