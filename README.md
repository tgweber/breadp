# BREaDP

Benchmark for Research Data Products (BREaDP).
Source directory for benchmarks for research data products.

# Quick Start

```bash
do_something_quick()
```

# Design

## Research Data Product

A research data product is a composite built out of these elements:
* a persistent identifier
* one to several services
* one or several sets of metadata (in different formats)
* one or several research artefacts

### Persistent Identifier
A perstistent identifier is one of the following items:
* An DOI
* A Handle
* An URL

### Service
A service is a combination of a protocol and an enpoint.
A service can produce metadata and data
Services can be produced by the persistent identifier (content negotiation) or from file. Services have a timestamp indicating their creation.

### Metadatum
A metadatum is a combination of potentially nested key-value-pairs and a schema to validate against.
Metadata can be produced by using a MetadataService or from file. Metadata have a timestamp indicating their creation.

### Datum
A datum is any digital information representation which is an input for or an output of those activities of researchers that are necessary to verify or refute knowledge.
Data can be produced by using a DataService or from file. Data have a timestamp indicating their creation.

## Checks
A check is a machine-actionable program that checks a research data product for compliance with an assessment criterion.

A check consists of:
* an ID
* a version
* a short text describing the criterion checked (in English)
* a state
* a set of logs (timestamp, state, message)

States:
* "unchecked" if the research data product has not been checked.
* "success" if the research data product meets the criterion.
* "failure" if the research data product fails to meet the criterion.
* "uncheckable" if the research data product cannot be checked due to reasons external to the research data product.


## Benchmark

A benchmark consists of:
* A set of checks (specified by ID + version)
* A sequence in which the checks should be executed
* A weighting function from the set of checks to the natural numbers
* A version and an ID.

## Benchmark Run
A benchmark run on a research data product is the execution of all checks of that benchmark at a given time.
The score of the benchmark run is a function of the return values of its checks to the space [0,1].
