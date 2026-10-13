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

| Resume text | Expected skill | Result |
|---|---|---|
| Used Structured Query Language | SQL | PASS |
| Advanced PowerBI reporting | Power BI | PASS |
| Built dashboards in MS Excel | Excel | PASS |
| Developed in Python | Python | PASS |

## Integration test
The live Streamlit dashboard detected SQL, Power BI, Excel,
and Python when entered using the tested names.

## Limitations
This is rule-based alias matching, not semantic understanding.
Only predefined aliases are supported. The tests establish
functional behavior for the tested examples, not overall
resume-matching accuracy.

## Next steps
- Test PDF, DOCX, and TXT resume extraction.
- Check false positives and false negatives.
- Verify CSV report export.
- Record any issues and corrective changes.
