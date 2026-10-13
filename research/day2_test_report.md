# FuturePath AI — Day 2 Test Report

## Feature

Alias-based skill matching for resume-to-role comparison.

## Objective

Improve rule-based matching when a skill is written using a
known alternative name.

## Implementation

Extended the existing alias dictionary lookup so that resume
matching checks both canonical skill names and their defined aliases.

## Tests performed

|Resume text|Expected skill|Result|
|-|-|-|
|Used Structured Query Language|SQL|PASS|
|Advanced PowerBI reporting|Power BI|PASS|
|Built dashboards in MS Excel|Excel|PASS|
|Developed in Python|Python|PASS|

## Integration test

The live Streamlit dashboard detected SQL, Power BI, Excel,
and Python when entered using the tested names.

\## Resume file extraction tests



The existing resume extraction function was tested using sample TXT, DOCX, and PDF files containing known skill names.

| File format|Test Cases|Results|
|-|-|-|
|TXT|Extract text and identify expected skills|PASS|
|DOCX|Extract paragraph text and identify expected skills|PASS|
|PDFD|Extract text and identify expected skills|PASS|





\*\*Test coverage:\*\* All three supported file formats passed the sample extraction tests. These tests verify basic functionality and do not establish performance on scanned PDFs, complex resume layouts, or all possible file encodings.

## Limitations

This is rule-based alias matching, not semantic understanding.
Only predefined aliases are supported. The tests establish
functional behavior for the tested examples, not overall
resume-matching accuracy.

## Next steps

* Test PDF, DOCX, and TXT resume extraction.
* Check false positives and false negatives.
* Verify CSV report export.
* Record any issues and corrective changes.

