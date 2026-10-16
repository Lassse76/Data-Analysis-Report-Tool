import run as ru
import report as re

res=ru.run("data/ehr_data.csv")

ress= re.constructdf([["missingness","amount"],("f1",res)])
re.toexcel(ress)

#re.extraction(output_type="md")