# Multimodal Construction Intelligence Platform
**Skill Wallet Capstone Project 1**

A modular Streamlit demo for construction safety visual screening, crack triage, planning estimates, and weather-aware site guidance. It uses Google Gemini when a key is supplied and clearly labelled demonstration outputs when no key is supplied.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal. Add a Gemini API key in the sidebar to enable image analysis and AI chat. The key is entered at runtime and is not written into the project files.

## Deploy to Streamlit Community Cloud

1. Push `app.py`, `requirements.txt`, and this README to a GitHub repository.
2. In Streamlit Community Cloud, choose the repository and `app.py`.
3. Deploy. No database or secrets file is required for demo mode.
4. Users can enter their Gemini API key in the app sidebar. For a managed deployment, you may instead configure a secret and adjust the app to read it from `st.secrets`.

## Modules

- **Site Safety & PPE Audit:** photo upload, Gemini vision prompt, structured JSON, PPE checklist, hazard severity and remedies, JSON download.
- **Crack Diagnostics:** visual defect triage, cautious width handling, possible causes, repair options to review with an engineer, JSON download.
- **Planning & Valuation:** adjustable assumptions, budget/capex/asset estimate, rough steel/cement thumb rules, milestone progress, Pollinations AI prompt link.
- **Daily Site Assistant:** weather-specific alerts and multi-turn chat.

## Safety and engineering limitations

- This is a capstone/demo decision-support tool, not a certified safety inspection, code compliance assessment, structural diagnosis, bill of quantities, contractor quote, or formal valuation.
- `IS 456` is primarily a plain and reinforced concrete code; it is not a general PPE checklist. Confirm requirements against current applicable Indian regulations, project HSE plans, and competent-person guidance.
- PPE detection cannot confirm concealed properties (for example, steel toe certification) from a photograph.
- Crack width is returned as `null` by the model when a calibrated scale is not visible. A photo alone cannot establish structural capacity.
- Cost rates and material quantities are broad illustrative assumptions. Use drawings, specifications, local quotations, and a qualified quantity surveyor/engineer for real projects.
- Pollinations is a third-party service. Its availability and data practices are outside this app's control.
- Do not upload sensitive or confidential site images unless authorized.

## Project structure

```text
multimodal_construction_intelligence/
├── app.py
├── requirements.txt
└── README.md
```
