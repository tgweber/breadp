# BREaDP

Benchmark for Research Data Products (BREaDP).
Source directory for benchmarks for research data products.

# Quick Start

```bash
virtualenv -p `which python3` venv
source venv/bin/activate
make
make test
```

# Design

## Research Data Product (RDP)

A research data product is a composite built out of these elements:
* a persistent identifier
* a service bundle
* a bundle of metadata (potentially same information in different formats)
* a bundle of data

### Persistent IDentifier (PID)
A Perstistent IDentifier (PID) is one of the following items:
* An DOI
* A Handle
* An URL

### Service Bundles
A service is a combination of a protocol and an endpoint.
A service can provide access to metadata and data of one or several research data products.
Services have a timestamp indicating their creation.
A service bundle is a set of services with a selection function;
the selection functions allows to pick a service for a given task or returns None if
no appropriate service is part of the RDP.

### Metadatum
A metadatum is a combination of potentially nested key-value-pairs and a schema to validate against.
Metadata have a timestamp indicating their creation.

### Data
Data are any digital information representations which are input for or output of those activities of researchers that are necessary to verify or refute scientific knowledge.
Data have a timestamp indicating their creation.

## Checks
A check is a machine-actionable program that indicates wether or not an RDP successfully passes a technical condition (e.g. valid format, response in a given time, etc.).

A check consists of:
* an ID
* a version
* a short text describing the criterion checked (in English)
* a state
* a result
* a set of logs of run checks

States:
* "unchecked" if the research data product has not been checked.
* "success" if the research data product was successfully checked. 
* "failure" if the research data product could not be checked. 

Results:
* Boolean checks:
    * True (if the research data product meets the criterion)
    * False (if the research data product does not meet the criterion)
  Example: Check if the metadata validate against their schema.
* Ordinal checks: One option out of an ordered list of options
  Example: Check if the research data is above, on or below a threshold (tba: better example)
* Metric checks: A float representing the  result
  Example: Response time of a service

Log fields:
* start: timestamp (UTC) when the check started
* end: timestamp (UTC) when the check finished
* state: state the check is in 
* result: None if the check has not run yet or serialized result (see above=
* version: version of the check
* pid: persistent Identifier of the RDP checked
* msg: string indicating failure or success information (may be empty)

## Evaluation
An evaluation orchestrates several checks for an RDP and maps the check results to a score between 0 and 1.

An evaluation consists of:
* An ID
* a version
* a short description describing the evaluation criteria (in English)
* A set of checks
* A set of logs of done evaluation

Log fields:
* start: timestamp (UTC) when the first check started
* end: timestamp (UTC) when the last check finished
* evaluation: Number between 0 and 1. 0 is the lowest/worse, 1 the highest/best evaluation.
* version: version of the evaluation.
* pid: persistent Identifier of the RDP checked
* msg: string indicating failure or success information (may be empty)

## Benchmark

A benchmark consists of:
* An ID
* A version
* A set of indendent evaluation (specified by ID + version)
* A set of logs of done benchmark runs.

Log fields:
* start: timestamp (UTC) when the first check of an evaluation started
* end: timestamp (UTC) when the last check of an evaluation finished
* score: Number between 0 and 1. 0 is the lowest/worse, 1 the highest/best evaluation.
* version: version of the benchmark
* pid: persistent Identifier of the RDP checked
* msg: string indicating failure or success information (may be empty)


## Benchmark Run
A benchmark run on a research data product is the execution of all checks of that benchmark at a given time.
The score of the benchmark run is a function of the return values of its checks to the space [0,1].
