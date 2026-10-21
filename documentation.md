Data Analysis Report (DAR) is a library for handling missing data and generating documentation in the form of a table. The table documentation does not replace regular documentation.

The documentation is a work in progress.


## Section 1: Getting Started

You have two options to impute missing values and predict an outcome. The first option uses a pipeline, while the second option uses manual function calls. If you don't want to evaluate the imputation, you can currently only use the second option. An option for this will be added to the pipeline in a later patch.

### Option 1: Using the Pipeline to Impute and Predict Data

When using the built-in pipeline, you only need to call the run function in run.py. There are two ways to pass arguments to the function. The recommended way is to specify them in the config.yaml and model_config.yaml files. To do this, change the value next to the corresponding argument (keep in mind that there must be one space between the ":" and the value). The other way is to pass the arguments directly when calling the function.

```python

import run as ru

# When using the recommended way, you only need to call the function like this
res = ru.run()

# When using the second way
res = ru.run(src="some source", .., {"multiply": 5})

```

The pipeline returns a dictionary with the different evaluation methods as keys and, as values, lists containing the imputation results for every run. In Section 2, we will discuss the different config files and how to use them.

### Option 2: Calling the Functions Manually

The advantage of calling the functions manually is full control over when to use which function. The disadvantage is the higher complexity. More knowledge is also required to build your own pipeline correctly.


## Section 2: Config Files
There are four different config files. In this section, we will go through each of them one by one.

### config.yaml

config.yaml is the main config file, where general settings such as paths or the amount of missingness are stored.


### model_config.yaml
model_config.yaml is the configuration file for the arguments of the different functions. It has the following format:

-> 2LetterforLibrary.MethodCalled:
---> argument1: Default value
---> argument2: Default value
    ...

If you want to change an argument, replace its default value with your desired value. The value must be valid for that argument.

-> 2LetterforLibrary.MethodCalled:
---> argument1: Your value
---> argument2: Your value
    ...


### config_final.yaml


### lookup.yaml


## Section 3: Modules

In this section, we will discuss the different modules and what they are used for.

### run.py

run.py is the heart of the pipeline. It calls the various methods needed in the pipeline. The module also extracts the required information from lookup.yaml (which values to exclude and which entries are needed for imputation). The pipeline called in the run function follows this order:

write/read config -> extract lookup information -> load dataset -> calculate amount of missingness -> create missingness -> impute missing variables -> predict outcome -> evaluate prediction/imputation


### mice.py