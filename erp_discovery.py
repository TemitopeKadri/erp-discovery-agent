"""
erp-discovery-agent: AI-assisted ERP discovery and readiness assessment.
https://github.com/TemitopeKadri/erp-discovery-agent

Usage:
    python erp_discovery.py --interactive
    python erp_discovery.py --input discovery_responses.json --output report.md
    python erp_discovery.py --questionnaire

MIT Licence — Copyright (c) 2026 Temitope Kadri
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)


# ── Discovery questionnaire ────────────────────────────────────────────────────

QUESTIONNAIRE = {
    "organisation": [
        {"id": "org_1", "question": "What is the organisation name and primary industry sector?"},
        {"id": "org_2", "question": "How many employees will use the ERP system?"},
        {"id": "org_3", "question": "What is the target go-live date or implementation window?"},
        {"id": "org_4", "question": "Which ERP platform are you evaluating or have selected? (e.g. D365 BC, SAP, NetSuite)"},
        {"id": "org_5", "question": "What is the primary driver for this ERP implementation? (e.g. growth, compliance, legacy replacement, merger)"},
    ],
    "data_readiness": [
        {"id": "data_1", "question": "How many legacy systems will need to be migrated or decommissioned?"},
        {"id": "data_2", "question": "Has a data audit or data quality assessment been completed? If yes, what were the key findings?"},
        {"id": "data_3", "question": "Are master data records (customers, suppliers, products, chart of accounts) currently standardised across the business?"},
        {"id": "data_4", "question": "What is the estimated volume of historical data to be migrated (years of data, record counts if known)?"},
        {"id": "data_5", "question": "Are there any data sovereignty, GDPR, or regulatory data-handling requirements that will affect the implementation?"},
    ],
    "process_maturity": [
        {"id": "proc_1", "question": "Are current business processes (finance, procurement, inventory, etc.) documented? At what level of detail?"},
        {"id": "proc_2", "question": "How standardised are processes across business units or locations? Are there significant variations?"},
        {"id": "proc_3", "question": "Has a process gap analysis been completed between current state and the target ERP's standard processes?"},
        {"id": "proc_4", "question": "What is the appetite for process re-engineering versus ERP customisation?"},
        {"id": "proc_5", "question": "Which functional areas are in scope for this implementation? (e.g. Finance, Procurement, Inventory, Projects, HR)"},
    ],
    "people_and_change": [
        {"id": "people_1", "question": "Who is the executive sponsor and how actively are they engaged in the programme?"},
        {"id": "people_2", "question": "Has a dedicated project team been identified? Are internal resources available or will consultants be required?"},
        {"id": "people_3", "question": "What is the organisation's previous experience with major ERP or technology change programmes?"},
        {"id": "people_4", "question": "Is a change management and training plan in place or in development?"},
        {"id": "people_5", "question": "What is the current level of end-user resistance or concern about the ERP implementation?"},
    ],
    "technology": [
        {"id": "tech_1", "question": "What is the current technology infrastructure — cloud, on-premise, or hybrid?"},
        {"id": "tech_2", "question": "What integrations will be required between the ERP and other systems (e.g. payroll, CRM, e-commerce, warehousing)?"},
        {"id": "tech_3", "question": "Is the internal IT team equipped to support the implementation and ongoing maintenance of the ERP?"},
        {"id": "tech_4", "question": "Are there any known security, access control, or audit trail requirements specific to your industry or regulator?"},
        {"id": "tech_5", "question": "Has a technical architecture review been completed for the proposed ERP solution?"},
    ],
    "governance": [
        {"id": "gov_1", "question": "Is there a formal project governance structure in place (steering committee, project board)?"},
        {"id": "gov_2", "question": "Has a budget been approved? What is the total investment envelope including implementation, licences, training, and contingency?"},
        {"id": "gov_3", "question": "Has a risk register been started for the programme?"},
        {"id": "gov_4", "question": "What are the top three risks the organisation currently sees for this ERP implementation?"},
        {"id": "gov_5", "question": "Is there a benefits realisation plan in place defining what success looks like 12 months post go-live?"},
    ],
}


# ── Scoring weights ────────────────────────────────────────────────────────────

DOMAIN_WEIGHTS = {
    "data_readiness":   0.25,
    "process_maturity": 0.20,
    "people_and_change":0.25,
    "technology":       0.15,
    "governance":       0.15,
}


# ── LLM calls ──────────────────────────────────────────────────────────────────

def call_claude(prompt: str, max_tokens: int = 2000) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def score_domain(domain: str, responses: dict) -> dict:
    """Use Claude to score a single assessment domain and identify gaps."""
    domain_questions = QUESTIONNAIRE.get(domain, [])
    qa_pairs = "\n".join(
        f"Q: {q['question']}\nA: {responses.get(q['id'], '[Not answered]')}"
        for q in domain_questions
    )

    prompt = f"""You are an ERP implementation expert assessing organisational readiness.

Domain: {domain.replace('_', ' ').title()}
Assessment responses:
{qa_pairs}

Provide a JSON response only (no other text) with this exact structure:
{{
  "score": <integer 0-100>,
  "rating": "<Poor|Fair|Good|Strong>",
  "top_gaps": ["<gap 1>", "<gap 2>", "<gap 3>"],
  "recommendations": ["<action 1>", "<action 2>", "<action 3>"],
  "summary": "<one sentence summary of this domain's readiness>"
}}

Score guide: 0-40 Poor (major gaps, high risk), 41-60 Fair (significant work needed), 61-80 Good (manageable gaps), 81-100 Strong (well prepared)."""

    response = call_claude(prompt, max_tokens=600)
    try:
        clean = response.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:-1])
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"score": 50, "rating": "Fair", "top_gaps": ["Unable to parse response"],
                "recommendations": [], "summary": response[:200]}


def generate_full_report(responses: dict, domain_scores: dict, org_info: dict) -> str:
    """Generate a full implementation readiness report."""
    org_name = responses.get("org_1", "Organisation")
    erp_platform = responses.get("org_4", "ERP platform")

    weighted_score = sum(
        domain_scores[d]["score"] * w
        for d, w in DOMAIN_WEIGHTS.items()
        if d in domain_scores
    )

    domain_summary = "\n".join(
        f"- {d.replace('_',' ').title()}: {domain_scores[d]['score']}/100 "
        f"({domain_scores[d]['rating']}) — {domain_scores[d]['summary']}"
        for d in DOMAIN_WEIGHTS
        if d in domain_scores
    )

    all_gaps = []
    all_recs = []
    for d in DOMAIN_WEIGHTS:
        if d in domain_scores:
            all_gaps.extend(domain_scores[d].get("top_gaps", []))
            all_recs.extend(domain_scores[d].get("recommendations", []))

    prompt = f"""You are a senior ERP implementation consultant producing a readiness report.

Organisation: {org_name}
ERP Platform: {erp_platform}
Overall Readiness Score: {weighted_score:.0f}/100

Domain scores:
{domain_summary}

Top identified gaps:
{chr(10).join(f'- {g}' for g in all_gaps)}

Recommended actions:
{chr(10).join(f'- {r}' for r in all_recs)}

Produce a full ERP Implementation Readiness Report in Markdown with these sections:

## ERP Implementation Readiness Report
### Organisation: {org_name} | Platform: {erp_platform}

### Executive Summary
Two paragraphs. Overall readiness score, key strengths, top 3 risks, and go/no-go recommendation for the current implementation timeline.

### Readiness Scorecard
A Markdown table: Domain | Score | Rating | Status

### Critical Gaps (Must Address Before Go-Live)
The 3-5 gaps that present the highest implementation risk, with specific recommended actions and suggested owners.

### Implementation Readiness Roadmap
A phased action plan (Pre-Discovery, Discovery, Design, Build, UAT, Go-Live) with the most important readiness actions per phase.

### Risk Summary
Top 5 risks with likelihood, impact, and mitigation.

### Recommended Next Steps
The three actions the organisation should take in the next 30 days.

Be specific, practical, and direct. Reference the organisation name and ERP platform throughout."""

    return call_claude(prompt, max_tokens=2500)


# ── Interactive session ────────────────────────────────────────────────────────

def run_interactive() -> dict:
    """Run an interactive discovery session and return responses."""
    print("\n" + "═" * 60)
    print("  ERP Discovery Agent — Interactive Session")
    print("  Type your answer and press Enter. Type 'skip' to skip a question.")
    print("═" * 60 + "\n")

    responses = {}
    domain_order = ["organisation", "data_readiness", "process_maturity",
                    "people_and_change", "technology", "governance"]

    for domain in domain_order:
        print(f"\n{'─'*50}")
        print(f"  {domain.replace('_', ' ').upper()}")
        print(f"{'─'*50}")
        for q in QUESTIONNAIRE[domain]:
            print(f"\n{q['question']}")
            answer = input("> ").strip()
            if answer.lower() != "skip":
                responses[q["id"]] = answer

    return responses


# ── File I/O ───────────────────────────────────────────────────────────────────

def load_responses(input_path: str) -> dict:
    path = Path(input_path)
    if not path.exists():
        print(f"Error: file not found: {input_path}")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def save_responses(responses: dict, output_path: str = "discovery_responses.json") -> None:
    Path(output_path).write_text(json.dumps(responses, indent=2), encoding="utf-8")
    print(f"Responses saved to: {output_path}")


SAMPLE_RESPONSES = {
    "org_1": "Northgate Office Supplies — B2B wholesale and retail distribution",
    "org_2": "85 users across finance, procurement, warehouse, and sales",
    "org_3": "Target go-live Q1 2027, 12-month implementation",
    "org_4": "Microsoft D365 Business Central",
    "org_5": "Legacy system (Sage 50) end of support, growth into multi-site operations",
    "data_1": "Three legacy systems: Sage 50 (finance), bespoke warehouse WMS, Excel-based procurement",
    "data_2": "No formal data audit completed. Known issues with duplicate customer records and inconsistent product codes.",
    "data_3": "Not standardised. Each location manages its own supplier list.",
    "data_4": "7 years of transactional data. Approximately 12,000 active product SKUs.",
    "data_5": "GDPR applies. No sector-specific regulatory requirements beyond standard data protection.",
    "proc_1": "Finance processes documented to Level 2. Warehouse and procurement largely undocumented.",
    "proc_2": "Significant variation between the two warehouse sites in picking and dispatch processes.",
    "proc_3": "Gap analysis not yet started.",
    "proc_4": "Strong preference for configuration over customisation given budget constraints.",
    "proc_5": "Finance, Procurement, Inventory Management, Warehouse Management, Basic Projects",
    "people_1": "CFO is executive sponsor. Engaged monthly but not hands-on day to day.",
    "people_2": "Internal project manager identified (part-time). Will need external D365 BC implementation partner.",
    "people_3": "Migrated from paper-based to Sage 50 eight years ago. No major ERP experience since.",
    "people_4": "No change management plan in place yet.",
    "people_5": "Warehouse staff have expressed concern about job impact. Finance team broadly supportive.",
    "tech_1": "Mix of on-premise servers and Microsoft 365 cloud. Moving to full cloud with this implementation.",
    "tech_2": "Required integrations: e-commerce platform (Shopify), payroll (ADP), EDI with top 3 suppliers.",
    "tech_3": "IT team of 2. Will need external support for integrations and ongoing BC administration.",
    "tech_4": "PCI DSS not applicable. Standard GDPR data handling requirements.",
    "tech_5": "Technical architecture review not yet started.",
    "gov_1": "Steering committee not yet formed. Currently governed as an IT project.",
    "gov_2": "Budget approved: £380,000 total including implementation partner, licences, training, and 15% contingency.",
    "gov_3": "Risk register not started.",
    "gov_4": "1. Data quality — volume and quality of legacy data. 2. User adoption — especially warehouse. 3. Integration complexity with Shopify and EDI.",
    "gov_5": "No formal benefits plan. Informal expectation: reduce month-end close from 12 days to 5 days.",
}


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="erp-discovery-agent: AI-assisted ERP readiness assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python erp_discovery.py --interactive
  python erp_discovery.py --questionnaire
  python erp_discovery.py --sample
  python erp_discovery.py --input discovery_responses.json --output report.md
        """
    )
    parser.add_argument("--interactive", action="store_true",
                        help="Run interactive discovery session")
    parser.add_argument("--input", help="Path to completed discovery responses JSON")
    parser.add_argument("--output", help="Path to write Markdown report (optional)")
    parser.add_argument("--questionnaire", action="store_true",
                        help="Print the full questionnaire and exit")
    parser.add_argument("--sample", action="store_true",
                        help="Generate sample_responses.json and run a report")

    args = parser.parse_args()

    if args.questionnaire:
        for domain, questions in QUESTIONNAIRE.items():
            print(f"\n{'='*50}")
            print(f"  {domain.replace('_', ' ').upper()}")
            print(f"{'='*50}")
            for q in questions:
                print(f"\n[{q['id']}] {q['question']}")
        return

    if args.sample:
        Path("sample_responses.json").write_text(
            json.dumps(SAMPLE_RESPONSES, indent=2), encoding="utf-8"
        )
        print("Sample responses saved to sample_responses.json")
        responses = SAMPLE_RESPONSES
    elif args.interactive:
        responses = run_interactive()
        save_responses(responses)
    elif args.input:
        responses = load_responses(args.input)
    else:
        parser.print_help()
        return

    print("\nScoring assessment domains...")
    domain_scores = {}
    for domain in DOMAIN_WEIGHTS:
        print(f"  Scoring {domain.replace('_', ' ')}...")
        domain_scores[domain] = score_domain(domain, responses)
        score = domain_scores[domain]["score"]
        rating = domain_scores[domain]["rating"]
        print(f"    → {score}/100 ({rating})")

    weighted_score = sum(
        domain_scores[d]["score"] * w
        for d, w in DOMAIN_WEIGHTS.items()
        if d in domain_scores
    )
    print(f"\nOverall readiness score: {weighted_score:.0f}/100")

    print("\nGenerating full readiness report...")
    report = generate_full_report(responses, domain_scores, {})

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print("\n" + "═" * 60)
        print(report)
        print("═" * 60)


if __name__ == "__main__":
    main()
