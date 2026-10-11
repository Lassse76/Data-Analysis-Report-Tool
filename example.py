import run as ru
import report as re

ru.run("data/ehr_data.csv")

re.extraction(output_type="txt")