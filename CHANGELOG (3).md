# Changelog

All notable changes to erp-discovery-agent are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.2.0] — 2026-06-09

### Added
- Sample discovery responses for manufacturing sector (`sample_manufacturing_responses.json`) — Midlands Precision Engineering Ltd, D365 BC, three-site implementation
- Sample discovery responses for professional services sector (`sample_professional_services_responses.json`) — Hargreaves Grant LLP, Sage Intacct, 85-user implementation
- CONTRIBUTING guide for practitioners who want to add sample responses or features

---

## [0.1.0] — 2026-06-01

### Added
- Initial release of `erp_discovery.py` command-line tool
- Full 30-question discovery questionnaire across six domains: organisation, data readiness, process maturity, people and change, technology, and governance
- Domain scoring via Claude API — 0-100 score per domain with rating (Poor/Fair/Good/Strong)
- Weighted overall readiness score across five domains
- Gap identification — top gaps per domain with recommended actions
- Full implementation readiness report generation including:
  - Executive summary with go/no-go recommendation
  - Readiness scorecard table
  - Critical gaps with prioritised actions
  - Implementation readiness roadmap by phase
  - Risk summary with top 5 risks
  - Recommended next steps for the next 30 days
- Three modes: `--interactive` (guided session), `--input` (JSON file), `--questionnaire` (print questions)
- `--sample` flag to generate sample responses and run a report
- MIT licence
- README with quickstart, supported platforms, domain definitions, and roadmap

---
