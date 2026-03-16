# Test Reports Directory

This directory contains test execution reports.

## Naming Convention

Test reports are named as:
```
test_report_{suite_id}_{YYYYMMDD_HHMMSS}.json
```

## Report Structure

Each report contains:
- **suite_id**: Unique identifier for the test run
- **version**: Test suite version
- **timestamp**: Start and end time
- **summary**: Pass/fail statistics
- **environment**: Python version, dependencies
- **results**: Detailed results for each test case

## Viewing Reports

```bash
# View latest report
ls -t test_reports/*.json | head -1 | xargs cat | jq

# View specific report
cat test_reports/test_report_abc123_20260305_201500.json | jq
```
