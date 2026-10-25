import json
import re
from datetime import datetime
from urllib.parse import quote
from typing import Any

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

APP_NAME = "Multimodal Construction Intelligence Platform"
MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { --ink:#e8eef7; --muted:#9caec3; --panel:#111c2d; --line:#29384d; --accent:#f4b942; }
.stApp { background: radial-gradient(ellipse at top left, #182b43 0%, #0a1220 55%, #080d16 100%); color:var(--ink); }
[data-testid="stSidebar"] { background:#0d1726; border-right:1px solid var(--line); }
h1,h2,h3 { letter-spacing:-0.025em; }
.hero { padding:1.2rem 1.35rem; border:1px solid #31435b; border-radius:18px; background:linear-gradient(120deg,rgba(244,185,66,.14),rgba(45,83,122,.22)); margin-bottom:1rem; }
.hero-kicker { color:#f4b942; text-transform:uppercase; font-size:.76rem; letter-spacing:.13em; font-weight:800; }
.hero-title { font-size:2rem; line-height:1.12; font-weight:850; margin:.3rem 0 .5rem; color:#f5f8fc; }
.hero-sub { color:#b7c6d9; font-size:1rem; }
.panel { background:rgba(17,28,45,.82); border:1px solid var(--line); border-radius:15px; padding:1rem 1.1rem; }
.pill { display:inline-block; padding:.25rem .7rem; border-radius:999px; font-size:.78rem; font-weight:800; border:1px solid transparent; }
.pill-good { background:#123a2c; color:#7ee2b3; border-color:#24634c; }
.pill-warn { background:#493615; color:#ffd47b; border-color:#765620; }
.pill-bad { background:#4b2025; color:#ff9da5; border-color:#7a3038; }
.small-muted { color:#9caec3; font-size:.85rem; }
div[data-testid="stMetric"] { background:rgba(17,28,45,.82); border:1px solid #29384d; border-radius:14px; padding:.9rem; }
.stButton>button, .stDownloadButton>button { border-radius:10px; font-weight:750; }
div[data-testid="stProgressBar"] > div > div { background:#f4b942; }
</style>
""", unsafe_allow_html=True)

def parse_json_response(text: str) -> dict:
    """Parse strict JSON or recover a JSON object from fenced/extra text."""
    if not text:
        raise ValueError("The model returned an empty response.")
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise ValueError("Could not find valid JSON in the model response.")
        obj = json.loads(match.group(0))
    if not isinstance(obj, dict):
        raise ValueError("Expected a JSON object.")
    return obj

def gemini_client(api_key: str):
    if not api_key or not api_key.strip():
        return None
    return genai.Client(api_key=api_key.strip())

def gemini_text_and_image(client, prompt: str, image_bytes: bytes, mime_type: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    return response.text or ""

def gemini_text(client, prompt: str, history: list | None = None) -> str:
    contents = []
    if history:
        for item in history:
            contents.append({"role": item["role"], "parts": [{"text": item["content"]}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(temperature=0.35),
    )
    return response.text or "I couldn't generate a response. Please try again."

def safe_json_download(data: dict, filename: str):
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button("⬇️ Download JSON report", data=payload, file_name=filename,
                       mime="application/json", use_container_width=False)

def demo_safety(filename: str) -> dict:
    return {
        "analysis_mode": "DEMONSTRATION — not an analysis of the uploaded image",
        "image_filename": filename,
        "safety_score": 72,
        "overall_status": "Needs Attention",
        "ppe_detection": {
            "helmet": {"status": "Unclear", "evidence": "Demo placeholder; inspect the photo manually."},
            "high_visibility_vest": {"status": "Unclear", "evidence": "Demo placeholder; inspect the photo manually."},
            "steel_toe_boots": {"status": "Not Verifiable", "evidence": "Footwear certification cannot be verified from a typical photo."},
            "safety_harness": {"status": "Not Applicable / Unclear", "evidence": "Applicability depends on work-at-height context."}
        },
        "hazards": [
            {"hazard": "Unprotected edge / fall exposure (example)", "severity": "High",
             "evidence": "Illustrative demo item; confirm whether present on site.",
             "corrective_remedy": "Restrict access, install compliant guardrails or a suitable fall-arrest system, and verify controls before work."},
            {"hazard": "Housekeeping / trip hazard (example)", "severity": "Medium",
             "evidence": "Illustrative demo item; confirm whether present on site.",
             "corrective_remedy": "Clear access routes, secure loose materials and cables, and maintain a documented housekeeping check."}
        ],
        "limitations": "Demonstration data only. No image-based conclusions were generated."
    }

def demo_crack(filename: str) -> dict:
    return {
        "analysis_mode": "DEMONSTRATION — not an analysis of the uploaded image",
        "image_filename": filename,
        "defect_type": "Hairline (example only)",
        "estimated_crack_width_mm": None,
        "width_note": "A calibrated scale and on-site measurement are required; width is not estimated in demo mode.",
        "possible_root_causes": ["Drying shrinkage (possible example)", "Thermal movement (possible example)"],
        "recommended_next_steps": [
            "Photograph with a scale and record crack location, length, and change over time.",
            "Have a qualified structural engineer assess load-bearing or growing cracks.",
            "Select repair only after diagnosis; do not assume epoxy injection is appropriate for every crack."
        ],
        "repair_options_to_review_with_engineer": ["Epoxy injection only when suitable for the diagnosed crack and substrate", "Flexible sealant for suitable non-structural movement cracks", "Structural re-grouting only when specified by an engineer"],
        "urgency": "Inspection Required",
        "limitations": "Demonstration data only. No image-based conclusions were generated."
    }

def status_class(status: str) -> str:
    s = (status or "").lower()
    if any(x in s for x in ["safe", "compliant", "low", "clear", "pass"]):
        return "pill-good"
    if any(x in s for x in ["critical", "high", "unsafe", "fail", "urgent"]):
        return "pill-bad"
    return "pill-warn"

def render_hazards(hazards):
    if not hazards:
        st.success("No hazards were returned by the model. This is not proof that the site is hazard-free.")
        return
    for i, hazard in enumerate(hazards, 1):
        severity = str(hazard.get("severity", "Unknown"))
        st.markdown(f"**{i}. {hazard.get('hazard', 'Unspecified hazard')}**")
        st.markdown(f'<span class="pill {status_class(severity)}">{severity}</span>', unsafe_allow_html=True)
        if hazard.get("evidence"):
            st.caption("Evidence: " + str(hazard["evidence"]))
        if hazard.get("corrective_remedy"):
            st.write("**Corrective action:** " + str(hazard["corrective_remedy"]))
        st.divider()

# Sidebar
with st.sidebar:
    st.markdown("## 🏗️ MCIP")
    st.caption("Skill Wallet Capstone Project 1")
    api_key = st.text_input("Google Gemini API key", type="password",
                            help="Used only for requests in this app session. Do not hard-code secrets.")
    client = None
    if api_key.strip():
        try:
            client = gemini_client(api_key)
            st.success("Gemini key entered")
        except Exception:
            client = None
            st.warning("Could not initialize Gemini. Demo mode will be used.")
    else:
        st.info("Demo mode active — no API key required.")
    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("""
    1. **Streamlit UI** — inputs, tabs, reports  
    2. **Gemini multimodal API** — image + prompt analysis  
    3. **Validation layer** — JSON parsing and safe fallbacks  
    4. **Local calculations** — transparent planning estimates  
    5. **Session state** — chat history; no database
    """)
    st.markdown("---")
    st.markdown("### Feature navigation")
    st.caption("Use the four tabs in the main workspace.")
    st.caption("No external database is required.")

st.markdown(f"""
<div class="hero">
  <div class="hero-kicker">Skill Wallet · Capstone Project 1</div>
  <div class="hero-title">🏗️ {APP_NAME}</div>
  <div class="hero-sub">AI-assisted site safety, concrete defect triage, project planning, and weather-aware guidance.</div>
</div>
""", unsafe_allow_html=True)

st.warning("Engineering and safety disclaimer: outputs are decision-support only, not a substitute for an on-site competent person, licensed structural engineer, applicable codes, or emergency procedures. Image-only review cannot certify PPE, structural safety, or legal compliance. OSHA/IS 456 references are prompts for context, not a compliance determination.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🦺 Site Safety & PPE Audit",
    "🧱 Crack Diagnostics",
    "📐 Planning & Valuation",
    "🌦️ Site Assistant"
])

# TAB 1
with tab1:
    st.subheader("Site Safety & PPE Audit")
    st.write("Upload a site photo for a structured visual screening of visible PPE and potential hazards.")
    safety_file = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="safety_image")
    if safety_file:
        st.image(safety_file, caption=safety_file.name, use_container_width=True)
        if st.button("Run PPE & hazard audit", type="primary", key="run_safety"):
            with st.spinner("Reviewing the photo..." if client else "Preparing demonstration report..."):
                if client:
                    prompt = """
You are a cautious construction safety visual-screening assistant. Analyze only what is visibly supported by the image.
Return one valid JSON object with exactly these top-level fields:
safety_score (integer 0-100, explain it is a visual screening score, not a certification),
overall_status (one of "Looks Acceptable", "Needs Attention", "High Risk", "Unable to Determine"),
ppe_detection (object with helmet, high_visibility_vest, steel_toe_boots, safety_harness; each value is an object with status chosen from "Visible", "Not Visible", "Unclear", "Not Applicable", "Not Verifiable" and evidence string),
hazards (array of objects with hazard, severity ("Low","Medium","High","Critical","Unclear"), evidence, corrective_remedy),
limitations (string), standards_context (string).
Do not infer hidden items or claim footwear certification from appearance. If no scale/context is visible, say so.
Flag uncertain observations as unclear. Do not claim legal compliance. Mention OSHA general construction safety concepts and that IS 456 is a concrete design code, not a general PPE checklist; advise verification against applicable Indian rules/site HSE plan. Remedies must be practical and proportionate. Output JSON only.
"""
                    try:
                        raw = gemini_text_and_image(client, prompt, safety_file.getvalue(), safety_file.type or "image/jpeg")
                        result = parse_json_response(raw)
                        result["image_filename"] = safety_file.name
                        result["analysis_mode"] = "Gemini visual screening"
                    except Exception as e:
                        st.error(f"Gemini request failed; showing a clearly labelled demo report instead. Details: {e}")
                        result = demo_safety(safety_file.name)
                else:
                    result = demo_safety(safety_file.name)
                st.session_state["safety_result"] = result
    result = st.session_state.get("safety_result")
    if result:
        st.markdown(f"**Mode:** {result.get('analysis_mode','Unknown')}")
        a, b, c = st.columns(3)
        score = result.get("safety_score")
        a.metric("Visual safety score", f"{score}/100" if isinstance(score, (int, float)) else "N/A")
        b.metric("Overall status", str(result.get("overall_status", "Unknown")))
        b.markdown(f'<span class="pill {status_class(str(result.get("overall_status","")))}">{result.get("overall_status","Unknown")}</span>', unsafe_allow_html=True)
        c.metric("Hazards listed", len(result.get("hazards", [])))
        st.markdown("#### PPE checklist")
        ppe = result.get("ppe_detection", {})
        cols = st.columns(2)
        for idx, key in enumerate(["helmet", "high_visibility_vest", "steel_toe_boots", "safety_harness"]):
            value = ppe.get(key, {})
            if isinstance(value, str):
                status, evidence = value, ""
            else:
                status, evidence = value.get("status", "Unclear"), value.get("evidence", "")
            with cols[idx % 2]:
                st.markdown(f"**{key.replace('_',' ').title()}**")
                st.markdown(f'<span class="pill {status_class(status)}">{status}</span>', unsafe_allow_html=True)
                if evidence:
                    st.caption(evidence)
        st.markdown("#### Identified hazards and remedies")
        render_hazards(result.get("hazards", []))
        if result.get("limitations"):
            st.info(result["limitations"])
        if result.get("standards_context"):
            st.caption(result["standards_context"])
        safe_json_download(result, "site_safety_audit.json")

# TAB 2
with tab2:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.write("Use this as a preliminary triage aid only. A photo cannot establish structural capacity or reliably measure crack width without a scale.")
    crack_file = st.file_uploader("Concrete or wall surface photo", type=["jpg", "jpeg", "png"], key="crack_image")
    if crack_file:
        st.image(crack_file, caption=crack_file.name, use_container_width=True)
        context = st.text_area("Optional context (location, age, whether crack is growing, nearby doors/columns)", key="crack_context")
        if st.button("Assess visible defect", type="primary", key="run_crack"):
            with st.spinner("Assessing the image..." if client else "Preparing demonstration report..."):
                if client:
                    prompt = f"""
Act as a cautious structural-defect triage assistant. Analyze only visible evidence and do not diagnose definitively.
Site context supplied by user: {context or "Not supplied"}.
Return valid JSON only with fields:
defect_type (one of "Hairline","Settlement","Structural Shear","Thermal Expansion","Spalling","Other","Unable to Determine"),
estimated_crack_width_mm (number or null; if no calibrated scale, use null),
width_note (string),
visual_observations (array of strings),
possible_root_causes (array of strings, framed as possibilities),
recommended_next_steps (array of strings),
repair_options_to_review_with_engineer (array of strings),
urgency (one of "Routine Monitoring","Inspection Required","Prompt Engineer Review","Urgent — Restrict Area"),
limitations (string).
Do not recommend a repair as certain without diagnosis. Mention epoxy injection only if appropriate for a diagnosed crack; structural re-grouting only when specified by an engineer. If crack is wide, diagonal near structural members, growing, accompanied by displacement, or concrete is spalling, advise prompt professional inspection and restricting access if immediate danger is suspected. Never assert structural safety from a photo.
"""
                    try:
                        raw = gemini_text_and_image(client, prompt, crack_file.getvalue(), crack_file.type or "image/jpeg")
                        result = parse_json_response(raw)
                        result["image_filename"] = crack_file.name
                        result["analysis_mode"] = "Gemini visual triage"
                    except Exception as e:
                        st.error(f"Gemini request failed; showing a clearly labelled demo report instead. Details: {e}")
                        result = demo_crack(crack_file.name)
                else:
                    result = demo_crack(crack_file.name)
                st.session_state["crack_result"] = result
    crack_result = st.session_state.get("crack_result")
    if crack_result:
        st.markdown(f"**Mode:** {crack_result.get('analysis_mode','Unknown')}")
        c1, c2 = st.columns(2)
        c1.metric("Defect category", str(crack_result.get("defect_type", "Unknown")))
        c2.metric("Urgency", str(crack_result.get("urgency", "Unknown")))
        if crack_result.get("estimated_crack_width_mm") is not None:
            st.metric("Estimated width (mm)", crack_result["estimated_crack_width_mm"])
        if crack_result.get("width_note"):
            st.caption(crack_result["width_note"])
        st.markdown("#### Visual observations")
        for item in crack_result.get("visual_observations", []):
            st.write("• " + str(item))
        st.markdown("#### Possible root causes")
        for item in crack_result.get("possible_root_causes", []):
            st.write("• " + str(item))
        st.markdown("#### Recommended next steps")
        for item in crack_result.get("recommended_next_steps", []):
            st.write("• " + str(item))
        st.markdown("#### Repair options to review with an engineer")
        for item in crack_result.get("repair_options_to_review_with_engineer", []):
            st.write("• " + str(item))
        st.info(crack_result.get("limitations", "Photo-only screening is limited."))
        safe_json_download(crack_result, "crack_diagnostics_report.json")

# TAB 3
with tab3:
    st.subheader("Planning & Real Estate Valuation")
    st.write("Indicative planning model using editable assumptions — not a contractor quote, quantity survey, or formal valuation.")
    col1, col2 = st.columns(2)
    with col1:
        structure = st.selectbox("Structure type", ["Residential house", "Apartment building", "Commercial building", "Warehouse / industrial shed", "Institutional building"])
        area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=2500, step=100)
        city_tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
    with col2:
        completion = st.slider("Completion percentage", min_value=0, max_value=100, value=35, step=5)
        quality = st.selectbox("Finish level", ["Economy", "Standard", "Premium"], index=1)
        land_value_lakh = st.number_input("Estimated land value (₹ lakh, optional)", min_value=0.0, max_value=100000.0, value=0.0, step=5.0)

    tier_rate = {"Tier 1": 2800, "Tier 2": 2200, "Tier 3": 1800}
    finish_factor = {"Economy": 0.85, "Standard": 1.0, "Premium": 1.35}
    structure_factor = {
        "Residential house": 1.0,
        "Apartment building": 1.08,
        "Commercial building": 1.2,
        "Warehouse / industrial shed": 0.78,
        "Institutional building": 1.1,
    }
    rate = tier_rate[city_tier] * finish_factor[quality] * structure_factor[structure]
    estimated_budget = area * rate
    incurred = estimated_budget * completion / 100
    # Very rough thumb-rule quantities; actual quantities depend on design, spans, floors, soil and structural system.
    cement_bags = area * (0.35 if structure == "Warehouse / industrial shed" else 0.40)
    steel_kg = area * (3.5 if structure == "Warehouse / industrial shed" else 4.0)
    current_asset = (estimated_budget * (0.25 + 0.75 * completion / 100)) + land_value_lakh * 100000
    def inr_compact(value):
        if value >= 10_000_000:
            return f"₹{value / 10_000_000:.2f} Cr"
        return f"₹{value / 100_000:.2f} L"

    m1, m2, m3 = st.columns(3)
    m1.metric("Estimated construction budget", inr_compact(estimated_budget))
    m2.metric("Estimated capex incurred", inr_compact(incurred))
    m3.metric("Indicative current asset value", inr_compact(current_asset))
    st.markdown("#### Material planning indicators")
    q1, q2 = st.columns(2)
    q1.metric("Cement (rough estimate)", f"{cement_bags:,.0f} bags")
    q2.metric("Reinforcement steel (rough estimate)", f"{steel_kg/1000:,.1f} tonnes")
    st.progress(completion / 100, text=f"Milestone progress: {completion}%")
    st.caption(f"Assumption used: ₹{rate:,.0f}/sq ft for {structure.lower()}, {city_tier}, {quality.lower()} finish. Material quantities are broad thumb rules only; do not procure materials from these values without drawings and a quantity take-off.")
    estimate_report = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "structure_type": structure, "built_up_sqft": area, "location_tier": city_tier,
        "finish_level": quality, "completion_percent": completion,
        "assumed_rate_inr_per_sqft": round(rate, 2),
        "estimated_construction_budget_inr": round(estimated_budget, 2),
        "estimated_capex_incurred_inr": round(incurred, 2),
        "land_value_inr_input": round(land_value_lakh * 100000, 2),
        "indicative_current_asset_value_inr": round(current_asset, 2),
        "rough_cement_bags": round(cement_bags), "rough_steel_kg": round(steel_kg),
        "disclaimer": "Illustrative planning estimate only. Not a formal valuation, BOQ, structural design or procurement quantity."
    }
    safe_json_download(estimate_report, "planning_valuation_estimate.json")
    st.markdown("#### Conceptual 3D architectural render prompt")
    render_style = st.selectbox("Rendering style", ["Photorealistic daylight", "Modern sustainable architecture", "Isometric construction progress", "Minimal architectural clay render"])
    prompt = f"{render_style} architectural visualization of a {structure.lower()} with {area} square feet built-up area in an Indian {city_tier.lower()} city, {completion}% construction completion, realistic materials, safe construction site, professional architectural concept render, no text, no logos"
    st.text_area("Prompt for image generation", value=prompt, height=90)
    pollinations_url = "https://image.pollinations.ai/prompt/" + quote(prompt, safe="")
    st.link_button("Open conceptual render (Pollinations AI)", pollinations_url)
    st.caption("This opens a third-party image-generation service. Availability, content, and privacy are governed by that provider; do not include confidential project details.")

# TAB 4
with tab4:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current / forecast weather condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    alerts = {
        "Normal": ("Routine precautions", [
            "Hold the daily toolbox talk and verify permits, PPE, access routes, and emergency contacts.",
            "Inspect lifting gear, scaffolds, temporary works, and electrical equipment before use.",
            "Follow approved concrete mix, placement, curing, and inspection plans."
        ]),
        "High Wind": ("Wind-related lifting and work-at-height risk", [
            "Stop crane and hoisting operations whenever wind exceeds the equipment/manufacturer or lift-plan limit; secure suspended loads and follow the lift supervisor's stop-work authority.",
            "Pause exposed work at height when conditions are unsafe; secure sheets, formwork, signage, and loose materials.",
            "Reassess scaffolds, edge protection, and temporary structures before restarting."
        ]),
        "Heavy Rain": ("Water ingress, slips, electrical and excavation risks", [
            "Stop work in flooded or unstable excavations; inspect shoring, access and nearby ground before re-entry.",
            "Isolate damaged or water-exposed electrical equipment; use qualified personnel to inspect and restore power.",
            "Improve drainage, prevent slips, protect cement and materials, and review concrete placement/cure plans with the engineer."
        ]),
        "Extreme Heat": ("Heat stress and dehydration risk", [
            "Provide potable water, shaded/cool rest areas, acclimatization and work-rest cycles appropriate to local conditions.",
            "Schedule heavy work for cooler hours where feasible; monitor workers for confusion, fainting, cramps or other heat illness signs.",
            "Protect fresh concrete and follow the approved hot-weather concreting and curing procedure; do not add water arbitrarily."
        ])
    }
    alert_title, alert_items = alerts[weather]
    st.markdown(f'<div class="panel"><h3>⚠️ {alert_title}</h3></div>', unsafe_allow_html=True)
    for item in alert_items:
        st.write("• " + item)

    st.markdown("#### Construction engineering assistant")
    st.caption("Ask about planning, site procedures, materials, safety, or interpreting general construction concepts. For high-risk decisions, consult the responsible engineer/HSE lead.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_prompt = st.chat_input("Ask a construction question...")
    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.chat_message("assistant"):
            if client:
                system_prompt = (
                    "You are a cautious construction engineering assistant. Give clear, practical general guidance. "
                    "Ask clarifying questions where necessary. Never certify structural safety or replace a licensed engineer, "
                    "local building code, approved drawings, manufacturer instructions, or site HSE procedures. "
                    "For emergencies, tell the user to stop work, isolate the area, and contact site emergency/HSE leadership. "
                    "Keep answers concise and distinguish general information from project-specific engineering decisions. "
                    "Current weather selection: " + weather + "."
                )
                try:
                    answer = gemini_text(client, system_prompt + "\n\nUser question: " + user_prompt,
                                         st.session_state.chat_history[:-1][-8:])
                except Exception as e:
                    answer = f"Gemini request failed: {e}\n\nDemo guidance: stop any unsafe activity, follow the approved site method statement, and consult the responsible engineer/HSE lead for project-specific decisions."
            else:
                answer = (
                    "Demo mode is active, so I can't provide a live AI-generated answer. General starting point: "
                    "check the approved drawings and method statement, identify hazards and controls, record the issue, "
                    "and consult the responsible site engineer or HSE lead before changing a construction procedure. "
                    "Add a Gemini API key in the sidebar to enable multi-turn AI responses."
                )
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    if st.session_state.chat_history and st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.caption("Multimodal Construction Intelligence Platform · Local session state only · No external database")
