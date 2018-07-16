# Experimental: HP Tuning for GitHub Issue Summarization

This directoy contains experimental code for adding hyperparameter
tuning support to the GitHub issue summarization example using Katib.

## Instructions

1. Deploy Kubeflow
1. [Deploy Katib](https://github.com/kubeflow/kubeflow/blob/master/kubeflow/katib/README.md)
1. Create the katib namespace

    ```
    kubectl create namespace katib
    ```

    * This is a known issue [kubeflow/katib#134](https://github.com/kubeflow/katib/issues/134)

1. Deploy the hyperparameter tuning job 

   ```
   cd kubeflow/examples/github_issue_summarization/ks-kubeflow
   ks apply ${ENVIRONMENT} -c hp-tune
   ```

## UI

You can check your Model with Web UI.

Access to `http://${ENDPOINT}/katib/projects`

    * If you are using GKE and IAP then ENDPOINT is the endpoint you
      are serving Kubeflow on

    * Otherwise you can port-forward to one of the AMBASSADOR pods
      and ENDPOINT

      ```
      kubectl port-forward `kubectl get pods --selector=service=ambassador -o jsonpath='{.items[0].metadata.name}'` 8080:80
      ENDPOINT=localhost:8080
      ```

The Results will be saved automatically.

## Description of git-issue-summarize-demo.go
You can make hyperparameter and evaluate it by Katib-API.
Katib-APIs are grpc. So you can use any language grpc supported(e.g. golang, python, c++).
A typical case, you will call APIs in the order as below.
In git-issue-summarize-demo.go, it wait for the status of all workers will be Completed.

### CreateStudy
First, you should create Study.
The input is StudyConfig.
It has Study name, owner, optimization info, and Parameter config(parameter name, min, and max).
This function generates a unique ID for your study and stores the config to DB.
Input:
* StudyConfig:
    * Name: string
    * Owner: string
    * OptimizationType: enum(OptimizationType_MAXIMIZE, OptimizationType_MINIMIZE)
    * OptimizationGoal: float
    * DefaultSuggestionAlgorithm: string
    * DefaultEarlyStoppingAlgorithm: string
    * ObjectiveValueName: string
    * Metrics: List of Metrics name
    * ParameterConfigs: List of parameter config.
Return:
* StudyID

### SetSuggestionParameters
Hyperparameters are generated by suggestion services with Parameter config of Study.
You can set the specific config for each suggestion.
Input: 
* StudyID: ID of your study.
* SuggestionAlgorithm: name of suggestion service (e.g. random, grid)
* SuggestionParameters: key-value pairs parameter for suggestions. The wanted key is different for each suggestion.
Return:
* ParameterID

### GetSuggestions
This function will create Trials(set of Parameters).
Input:
* StudyID: ID of your study.
* SuggestionAlgorithm: name of suggestion service (e.g. random, grid)
* RequestNumber: the number you want to evaluate.
* ParamID: ParameterID you got from SetSuggestionParameters func.
Return
* List of Trials
    * TrialID
    * Parameter Sets

### RunTrial
Start to evaluate Trial.
When you use kubernetes runtime, the pods are created the specified config.
Input:
* StudyId: ID of your study.
* TrialId: ID of Trial.
* Runtime: worker type(e.g. kubernetes)
* WorkerConfig: runtime config
    * Image: name of docker image
    * Command: running commands
    * GPU: number of GPU
    * Scheduler: scheduler name
Return:
* List of WorkerID

### GetMetrics
Get metrics of running workers.
Input:
* StudyId: ID of your study.
* WorkerIDs: List of worker ID you want to get metrics from.
Return:
* List of Metrics

### SaveModel
Save the Model date to KatibDB. After you called this function, you can look model info in the KatibUI.
When you call this API multiple time, only Metrics will be updated.
Input:
* ModelInfo
    * StudyName
    * WorkerId
    * Parameters: List of Parameter
    * Metrics: List of Metrics
    * ModelPath: path to model saved. (PVCname:mountpath)
* DataSet: informatino of input date
    * Name
    * Path: path to input data.(PVCname:mountpath)

Return:
    
### GetWorkers
You can get worker list and status of workers.
Input:
Return:
* List of worker information