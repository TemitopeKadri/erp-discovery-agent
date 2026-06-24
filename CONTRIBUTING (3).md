# Contributing to erp-discovery-agent

Thank you for your interest in contributing. This tool is built by and for delivery managers and ERP practitioners — real-world experience is the most valuable contribution you can make.

---

## What we are looking for

- **New sample responses** — discovery responses for different industries (retail, healthcare, logistics, public sector) or different ERP platforms (SAP, Oracle, NetSuite, Xledger)
- **New assessment domains** — additional scoring dimensions beyond the current five
- **Bug fixes** — if something does not work as described, open an issue and submit a fix
- **Prompt improvements** — better scoring prompts that produce more accurate gap analysis
- **New output formats** — PDF report, Word document, Excel scorecard
- **Web UI** — a browser-based interface so users can run assessments without Python
- **Documentation** — clearer examples, better explanations

---

## How to contribute

1. **Fork the repo** — click Fork at the top of the page
2. **Create a branch** — `git checkout -b feat/your-feature-name`
3. **Make your changes** — keep commits small and focused
4. **Test your changes** — run the tool against a sample response file to confirm it works
5. **Submit a pull request** — describe what you changed and why

---

## Adding sample discovery responses

Sample JSON files are especially welcome. Use this structure:

```json
{
  "org_1": "Organisation name and sector",
  "org_2": "Number of users",
  "org_3": "Target go-live date",
  "org_4": "ERP platform",
  "org_5": "Primary driver for implementation",
  "data_1": "...",
  ...
}
```

Name your file clearly: `sample_[industry]_responses.json`
e.g. `sample_retail_responses.json`

Full question list available via: `python erp_discovery.py --questionnaire`

---

## Reporting bugs

Open an issue with:
- What you expected to happen
- What actually happened
- Your Python version (`python --version`)
- The command you ran
- Any error messages

---

## Licence

By contributing you agree that your contributions will be licensed under the MIT Licence.

---

*Built by [Temitope Kadri MAPM](https://github.com/TemitopeKadri)*
