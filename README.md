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

### Persistent Identifier
A perstistent identifier is one of the following items:
* An DOI
* A Handle
* An URL

### Service Bundles
A service is a combination of a protocol and an enpoint.
A service can produce metadata and data.
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
* a set of logs of run checks

States:
* "unchecked" if the research data product has not been checked.
* "success" if the research data product meets the criterion.
* "failure" if the research data product fails to meet the criterion.
* "uncheckable" if the research data product cannot be checked due to reasons external to the research data product.

Log fields:
* start: timestamp (UTC) when the check started
* end: timestamp (UTC) when the check finished
* state: state the check resulted in
* version: version of the check
* pid: persistent Identifier of the RDP checked
* msg: string indicating failure or success information (may be empty)

## Assessments
An assessement orchestrates several checks for an RDP and maps the check results to a score between 0 and 1.

An assessement consists of:
* An ID
* a version
* a short description describing the assessment criteria (in English)
* A set of checks
* A set of logs of done assessements

Log fields:
* start: timestamp (UTC) when the first check started
* end: timestamp (UTC) when the last check finished
* assessement: Number between 0 and 1. 0 is the lowest/worse, 1 the highest/best assessement.
* version: version of the assessment
* pid: persistent Identifier of the RDP checked
* msg: string indicating failure or success information (may be empty)

## Benchmark

A benchmark consists of:
* An ID
* A version
* A set of indendent assessments (specified by ID + version)
* A set of logs of done benchmark runs.

Log fields:
* start: timestamp (UTC) when the first check of an assessment started
* end: timestamp (UTC) when the last check of an assessment finished
* score: Number between 0 and 1. 0 is the lowest/worse, 1 the highest/best assessement.
* version: version of the benchmark
* pid: persistent Identifier of the RDP checked
* msg: string indicating failure or success information (may be empty)


## Benchmark Run
A benchmark run on a research data product is the execution of all checks of that benchmark at a given time.
The score of the benchmark run is a function of the return values of its checks to the space [0,1].
