# Data Analysis Report (DAR)

Data Analysis Report (DAR) is a library for handling missing data and generating
documentation in the form of a table. The table documentation does not replace
regular documentation.

> **Note:** The documentation is a work in progress.

**Contents**

- [Section 1: Getting Started](#section-1-getting-started)
- [Section 2: Config Files](#section-2-config-files)
- [Section 3: Modules](#section-3-modules)


## Section 1: Getting Started

You have two options to impute missing values and predict an outcome. The first
option uses a pipeline, while the second option uses manual function calls.

### Option 1: Using the Pipeline to Impute and Predict Data

When using the built-in pipeline, you only need to call the `run` function in
`run.py`. There are two ways to pass arguments to the function:

1. **Recommended:** specify them in `config.yaml` and `model_config.yaml`. To do
   this, change the value next to the corresponding argument (keep in mind that
   there must be one space between the `:` and the value).
2. Pass the arguments directly when calling the function.

```python
import run as ru

# When using the recommended way, you only need to call the function like this
res = ru.run()

# When using the second way
res = ru.run(src="some source", seed=42, kwds={"multiply": 5})
```

The pipeline returns a dictionary with the different evaluation methods as keys
and, as values, lists containing the evaluation results for every run. The keys
are taken from `evaluation` in `config.yaml`: every entry of `prediction_eval`
becomes one key (for example `f1_score`), and every entry of `imputation_eval`
becomes two keys, one with the suffix `train` and one with the suffix `test` (for
example `root_mean_squared_errortrain`).

#### Easy Example

A complete run, including the generated table, looks like this (see
`example.py`):

```python
import run as ru
import report as re

# run the pipeline on the given dataset
res = ru.run("data/ehr_data.csv")

# build a table out of config values and evaluation results ...
ress = re.constructdf([
    ["missingness", "amount"],                        # value taken from config.yaml
    ("f1", res["f1_score"]),                          # prediction evaluation
    ("RMSE Train", res["root_mean_squared_errortrain"]),  # imputation evaluation
])

# ... and write it to result.xlsx
re.toexcel(ress)
```

In Section 2, we will discuss the different config files and how to use them.

### Option 2: Calling the Functions Manually

The advantage of calling the functions manually is full control over when to use
which function. The disadvantage is the higher complexity. More knowledge is also
required to build your own pipeline correctly.

#### Easy Example

The following example rebuilds the pipeline step by step for a single run:

```python
import pandas as pd
import run as ru
import config as co
import sample as sa
import mice as mi
import prediction as pr
import evaluate as ev

# 0. load the config files
co.read()                                     # data/config.yaml     -> co.data
co.readModelConfig("data/model_config.yaml")  # model_config.yaml    -> co.model_config
co.resetconfig_final()                        # start an empty data/config_final.yaml

# 1. load the data and build the mapping out of the lookup table
df = sa.innit(src="data/ehr_data.csv")
ru.create_mapping(df, "mortality", "lookup.yaml")
df = sa.innit(src="data/ehr_data.csv", exclude=co.data["exclude"])

# 2. split the data, extract the target and complete the data (ground truth)
train, test = sa.split(df)
train_x, train_y = sa.target(train, "mortality")
test_x, test_y = sa.target(test, "mortality")
train_comp = sa.complete_dataset(train_x, method="linear")
test_comp = sa.complete_dataset(test_x, method="linear")

# 3. induce missingness (10 % of all cells)
patterns = co.model_config["pa.MultivariateAmputation"]["patterns"]
train_incomp = mi.create_missingness(
    train_comp, prop=mi.calcamount(0.1, train_comp, patterns), patterns=patterns)
test_incomp = mi.create_missingness(
    test_comp, prop=mi.calcamount(0.1, test_comp, patterns), patterns=patterns)

# 4. impute the missing values (one csv file per imputation iteration)
train_files = mi.innit(ru.final_mapping, train_incomp, "train", df_comp=train_x)
test_files = mi.innit(ru.final_mapping, test_incomp, "test", df_comp=test_x)

# 5. predict the outcome on the first imputed dataset and evaluate it
train_imp = pd.read_csv(train_files[0], index_col=0)
test_imp = pd.read_csv(test_files[0], index_col=0)
train_std, test_std = sa.standardize(train_imp, test_imp)
pred = pr.classifier(train_std, train_y, test_std, threshold=0.5)
print(ev.predictionevaluation(test_y, pred, method="f1_score"))

# 6. evaluate the imputation on the cells that were amputed before
mask = (test_incomp.isna() & test_x.notna()).to_numpy()
print(ev.imputationevaluation(test_comp.to_numpy()[mask],
                              test_imp.to_numpy()[mask],
                              method="root_mean_squared_error"))
```


## Section 2: Config Files

There are four different config files. In this section, we will go through each of
them one by one.

| File | Location | Purpose |
|---|---|---|
| `config.yaml` | `data/config.yaml` | general settings (paths, amount of missingness, evaluation methods) |
| `model_config.yaml` | `data/model_config.yaml` | arguments of the different functions/methods |
| `config_final.yaml` | `data/config_final.yaml` | settings that were actually used in a run (basis of the table documentation) |
| `lookup.yaml` | `lookup.yaml` | per-variable settings for the imputation |

### config.yaml

`config.yaml` is the main config file, where general settings such as paths or the
amount of missingness are stored.

| Parameter | Shipped value | Description |
|---|---|---|
| `dataset.completation.type` | `linear` | Interpolation method used to complete the dataset for the ground truth (see `sample.complete_dataset`). |
| `exclude` | `[patient_id, sex, admission_type]` | Columns that are dropped when the dataset is loaded. |
| `imputation.type` | `Mice` | Imputation type of the run. `run` writes its `type` argument into this entry. |
| `missingness.type` | `pyampute` | Library/mechanism that is used to induce the missingness. |
| `missingness.amount` | `[0.1, 0.2]` | Amount of missingness per run (share of the cells). One entry per run. |
| `evaluation.prediction_eval` | `[f1_score]` | Methods used to evaluate the prediction (see `evaluate.predictionevaluation`). |
| `evaluation.imputation_eval` | `[root_mean_squared_error]` | Methods used to evaluate the imputation (see `evaluate.imputationevaluation`). |
| `path.data` | `null` | Path to the dataset. The pipeline currently takes the source as the `src` argument of `run`. |
| `path.lookup_table` | `[lookup.yaml, lookup.yaml]` | Lookup table per run. One entry per run. |
| `path.model_config` | `[data/model_config.yaml, data/model_config.yaml]` | Model config per run. One entry per run. |
| `path.output_name` | `[R1, R2]` | How the imputed files are named, corresponding to each run. Every entry is one run. |
| `seed` | `42` | Seed of the run. |
| `target` | `mortality` | Column that is predicted. |
| `testsplit` | `0.2` | Size of the test set in the train/test split. |
| `multiply` | `2` | How often every run is repeated. |

Two things are worth keeping in mind:

- `path.lookup_table`, `path.model_config`, `missingness.amount` and
  `path.output_name` are read together, so every one of these lists needs the
  same number of entries — one entry per run.

### model_config.yaml

`model_config.yaml` is the configuration file for the arguments of the different
functions. It has the following format:

```yaml
2LetterforLibrary.MethodCalled:
  argument1: Default value
  argument2: Default value
  ...
```

If you want to change an argument, replace its default value with your desired
value. The value must be valid for that argument.

```yaml
2LetterforLibrary.MethodCalled:
  argument1: Your value
  argument2: Your value
  ...
```

The two-letter prefix states which library the method comes from:

| Prefix | Library |
|---|---|
| `sk.` | scikit-learn |
| `pa.` | pyampute |

The entries are grouped as follows:

| Group | Entries | Used by |
|---|---|---|
| Amputation | `pa.MultivariateAmputation` | `mice.create_missingness` |
| Prediction models | `sk.RandomForestClassifier`, `sk.LogisticRegression`, `sk.KNeighborsClassifier`, `sk.GaussianNB`, `sk.HistGradientBoostingClassifier` | `prediction.classifier` |
| Imputation metrics | `sk.mean_squared_error`, `sk.root_mean_squared_error`, `sk.mean_absolute_error`, `sk.r2_score`, `sk.median_absolute_error` | `evaluate.imputationevaluation` |
| Prediction metrics | `sk.f1_score`, `sk.roc_auc_score`, `sk.average_precision_score`, `sk.balanced_accuracy_score`, `sk.matthews_corrcoef`, `sk.brier_score_loss`, `sk.log_loss`, `sk.confusion_matrix` | `evaluate.predictionevaluation` |

The most important entry for the amputation is `pa.MultivariateAmputation`:

| Parameter | Shipped value | Description |
|---|---|---|
| `prop` | `0.5` | Share of the rows with at least one missing value. It is recalculated out of `missingness.amount` (see [Amputation](#amputation)). |
| `patterns` | list of pattern dicts | Every pattern consists of `incomplete_vars` (the columns that get missing values) and `freq` (how often the pattern occurs). `null` creates the patterns automatically. |
| `std` | `true` | Standardize the data before the scores are calculated. |
| `verbose` | `false` | Print additional information. |
| `seed` | `null` | Seed of the amputation. |
| `lower_range` / `upper_range` | `-3` / `3` | Search range for the shift determination. |
| `max_diff_with_target` | `0.001` | Tolerance between the reached and the desired `prop`. |
| `max_iter` | `100` | Maximum iterations of the binary search. |

### config_final.yaml

`config_final.yaml` is not written by hand. It collects the settings that were
actually used during a run: every time a method is called for the first time
(amputation, prediction or evaluation), its parameters are appended to this file.
At the beginning of every run the file is reset.

`report.py` reads `config_final.yaml` to build the detailed part of the table
documentation, so this file is the link between a run and its documentation.

### lookup.yaml

`lookup.yaml` holds the per-variable settings for the imputation. Every variable
is one entry in the `variables` list:

```yaml
variables:
  - id: heart_rate
    synonym: [hr, pulse, heart rate]
    method: sm.OLS
    variant: "None"
    perturbation: boot
```

| Field | Description |
|---|---|
| `id` | Name of the variable/column. |
| `synonym` | Other spellings or names of the variable. The columns of the dataset are matched against `id` and against this list, so different spellings are connected to the same settings. |
| `method` | Model class used to impute the variable (`sm.OLS`, `sm.GLM`). `"None"` means the variable is excluded from the imputation. |
| `variant` | Family of the model, needed for `sm.GLM` (`sm.families.Binomial()`, `sm.families.Poisson()`, `sm.families.Gaussian()`). `"None"` for `sm.OLS`. |
| `perturbation` | Perturbation method of the imputer, for example `boot`. |


## Section 3: Modules

In this section, we will discuss the different modules and what they are used for.

### run.py

`run.py` is the heart of the pipeline. It calls the various methods needed in the
pipeline. The module also extracts the required information from `lookup.yaml`
(which values to exclude and which entries are needed for imputation). The
pipeline called in the `run` function follows this order:

```text
write/read config
  -> extract lookup information
  -> load dataset
  -> calculate amount of missingness
  -> create missingness
  -> impute missing variables
  -> predict outcome
  -> evaluate prediction/imputation
```

### mice.py

`mice.py` is the module responsible for inducing missingness and imputing it with
the help of the pyampute `ampute` command and statsmodels `mice`.

#### Amputation

Amputation is based on a MICE module from Rianne Schouten to ampute missingness.
For more information go to the pyampute documentation
<https://rianneschouten.github.io/pyampute/build/html/index.html>.

Due to the fact that pyampute does not directly work with an amount parameter for
missingness, we first need to calculate the `prop` value (the probability that a
line has missingness). The formula for that is:

$prop= \frac{\text{amount} \cdot|\text{columns}|}{|\text {incomplete\_vars}|\cdot \text{freq}}$

#### Imputation

On the other hand there is imputation. Currently only the statsmodels MICE
imputation is implemented. There are two different ways:

##### `justMice` MICE Imputation

This uses the standard `MICEData` function without any extra parameter.

##### `detailedMice` MICE Imputation

This uses the correlation of the columns to get a formula and the settings from
the lookup table. Then it uses `MICEData` with parameters to impute the missing
values.

After that, both methods use burn-ins to train the imputer before running the
imputation cycle multiple times, as set in the config file.

### sample.py

`sample.py` loads the data into a dataframe, splits the data into a test/train
set, standardizes it, extracts the target and completes the dataset for the ground
truth.

#### innit

Loads the data into a dataframe. Features to be excluded can be set as a
parameter, and also a mapping with which you can transform the values. It also has
a separator input and the source of the data as input.

#### split

Splits the data into a test and train split. It is recommended to set `stratify`
as the target.

#### target

`target` extracts the target out of the dataframe.

#### complete_dataset

Completes the dataset with the `interpolate` function.

#### standardize

Standardizes the data. Is recommended when using some prediction models.
