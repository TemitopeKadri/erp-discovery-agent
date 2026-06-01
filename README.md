# erp-discovery-agent

**AI-assisted ERP discovery, readiness assessment, and implementation risk scoring.**

`erp-discovery-agent` runs a structured discovery conversation with your stakeholders and produces a gap analysis, readiness score, and implementation risk report — cutting weeks of manual discovery into hours.

Built on real ERP implementation experience across D365 Business Central, including 150+ user rollouts in regulated environments.

---

## What it does

- Runs a structured ERP discovery questionnaire across five assessment domains
- Scores organisational readiness (0–100) across data, process, people, technology, and governance
- Identifies gaps between current state and ERP implementation requirements
- Produces a prioritised risk report with recommended actions
- Generates an executive summary and a detailed implementation readiness report

## Assessment domains

| Domain | What it covers |
|--------|---------------|
| Data readiness | Data quality, migration complexity, legacy system dependencies |
| Process maturity | Process documentation, standardisation, change appetite |
| People and change | Sponsor commitment, change management capacity, training needs |
| Technology landscape | Current systems, integration requirements, infrastructure readiness |
| Governance and compliance | Regulatory requirements, data sovereignty, audit trail needs |

## Quickstart

```bash
pip install -r requirements.txt

# Interactive discovery session
python erp_discovery.py --interactive

# Score a completed questionnaire JSON
python erp_discovery.py --input discovery_responses.json --output readiness_report.md

# Generate a blank questionnaire
python erp_discovery.py --questionnaire
```

## Requirements

- Python 3.9+
- Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable)

## Supported ERP platforms

D365 Business Central | SAP S/4HANA | NetSuite | Oracle Fusion | Sage Intacct

## Roadmap

- [ ] Web UI for stakeholder self-assessment
- [ ] Integration with Microsoft Forms / Google Forms export
- [ ] Benchmark scoring against industry peers
- [ ] Implementation timeline estimator
- [ ] Vendor selection scoring matrix

## Contributing

Pull requests welcome. Please open an issue first to discuss what you'd like to change.

## Licence

MIT — see [LICENSE](LICENSE)

---

*Part of an open-source toolkit for AI-assisted project delivery. See also: [agentic-pm](https://github.com/TemitopeKadri/agentic-pm), [cutover-copilot](https://github.com/TemitopeKadri/cutover-copilot), [prince2-agile-templates](https://github.com/TemitopeKadri/prince2-agile-templates)*
