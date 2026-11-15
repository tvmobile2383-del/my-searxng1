import requests
from modules.config import STOCK_API_URL, STOCK_API_TOKEN, STOCK_API_PATH, REQUEST_TIMEOUT
from modules.search import search_web

def collect_company_evidence(company: str, symbol: str):
    queries = [
        f"{company} {symbol} latest quarterly results investor presentation",
        f"{company} {symbol} annual report business strategy capacity expansion order book",
        f"{company} {symbol} management commentary future growth plans",
    ]
    evidence = []
    for q in queries:
        try:
            evidence.extend(search_web(q, limit=5))
        except Exception as exc:
            evidence.append({"title": "Search error", "content": str(exc), "url": "", "query": q})
    # de-duplicate URLs while preserving order
    seen, unique = set(), []
    for item in evidence:
        url = item.get("url", "")
        if url and url in seen:
            continue
        if url:
            seen.add(url)
        unique.append(item)
    return unique

def make_prompt(snapshot, evidence):
    return f"""
You are an institutional-quality Indian equity research analyst. Apply AE8 / AE11 rigorously.
Company: {snapshot.get('company')} ({snapshot.get('symbol')}); market: NSE/BSE, India.

NON-NEGOTIABLE ANALYTICAL SEPARATION
A) AE11 Financial Quality is historical only. Assess consistency, margins, ROCE, ROE, cash
conversion, FCF, balance sheet, working-capital efficiency and capital allocation. Do not
include moat, technology, R&D vision, future prospects or valuation in this score.
Normalize M&A, demergers, listing transitions, exceptional items and one-offs.
B) Future Moat is structural and independent of current financial performance. Do not use ROCE,
ROE, financials, valuation or current execution as moat evidence. Evaluate switching costs,
technology/IP, regulation, platform/network/data, cost advantage, lock-in, scalability and industry.
State current moat versus 5-year potential, moat type, trajectory, durability, velocity (1-5),
and A1 Application / A2 Infrastructure / A3 Regulatory / A4 Demographic drivers where relevant.
C) Confidence is probability that the future thesis is delivered. Track promise -> pipeline ->
contract/order -> execution/capacity -> commercialisation -> recurring revenue/profit. Quarterly
performance alone is insufficient; penalize unproven promises and one-offs.
D) Do not award premium PE without a durable, evidence-backed future moat. Keep valuation out
of moat analysis. Use next-FY forecast EPS for scenario valuation. If forecast EPS is absent,
do not invent fair value, buy zones or 5Y CAGR; clearly mark unavailable.

SNAPSHOT (Yahoo Finance data; may be incomplete/out of date):
{snapshot}

WEB EVIDENCE (snippets and source links; treat snippets as leads, not verified filings):
{evidence}

RETURN THESE SECTIONS
1. Executive verdict; thesis, counter-thesis and key unknowns.
2. Business model and business evolution: Scale / Capability / Business Diversification / Business Model Upgrade.
3. AE11 historical Financial Quality score /10 with evidence and missing data.
4. Future Moat score /10; current vs 5Y moat, type, trajectory, durability, velocity 1-5, structural drivers.
5. Execution confidence probability (%) and milestone evidence.
6. Historical growth and forward growth outlook: sales, EBITDA, EPS; separate facts from estimates.
7. Valuation: live PE, historical PE range if available, sustainable PE range, fair PE, bull/base/bear.
8. Investment Timing table: current PE, fair PE, buy zone, strong-buy zone, expected 5Y CAGR.
9. Risks, catalysts, peer comparison and quarterly monitoring checklist.
10. Final rating: Avoid / Watch / B / B+ / A, with explicit conditions for upgrade/downgrade.

Use tables where useful. Cite URLs from the evidence list. Explicitly flag unsupported or missing inputs.
""".strip()

def run_qwen_analysis(prompt, snapshot):
    if not STOCK_API_URL or not STOCK_API_TOKEN:
        raise RuntimeError("Configure STOCK_API_URL and STOCK_API_TOKEN in the Render service.")
    endpoint = STOCK_API_URL.rstrip("/") + (STOCK_API_PATH if STOCK_API_PATH.startswith("/") else "/" + STOCK_API_PATH)
    headers = {
        "Authorization": f"Bearer {STOCK_API_TOKEN}",
        "X-API-Token": STOCK_API_TOKEN,
        "Content-Type": "application/json",
    }
    # Expected API contract: POST endpoint with JSON {"prompt": "...", "stock": {...}}.
    response = requests.post(endpoint, headers=headers,
                             json={"prompt": prompt, "stock": snapshot},
                             timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if isinstance(data, dict):
        for key in ("analysis", "response", "result", "output", "text"):
            if data.get(key) is not None:
                return str(data[key])
    return str(data)
