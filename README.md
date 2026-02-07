# Virtue Foundation – Healthcare Intelligence MVP

This repository contains a prototype system for structuring, analyzing, and reasoning over healthcare facility and NGO data, with a focus on **low‑ and middle‑income settings** (initially Ghana).

The project is designed to support **data understanding, planning, and decision‑making** using a combination of structured fields and unstructured medical text.

---

## Project Goal

The goal of this project is to demonstrate how unstructured healthcare information
(e.g. services, equipment, capabilities written in free text)
can be combined with structured data
(e.g. location, facility type, organization metadata)
to support:

- Healthcare coverage analysis
- Regional planning and gap identification
- Future AI / LLM‑assisted reasoning

This is an **MVP / proof‑of‑concept**, not a production system.

---

## Key Design Principles

- **Non‑destructive data handling**  
  Original data is never overwritten or dropped.

- **LLM‑friendly by design**  
  Human‑written text is preserved exactly as‑is for traceability and reasoning.

- **Additive enrichment only**  
  New helper columns are added to support analysis, without changing meaning.

- **Explainability over automation**  
  Simple, transparent logic is preferred over black‑box transformations.

---

## Data

- Primary dataset:  
  `Virtue Foundation Ghana v0.3 - Sheet1.csv`

- Data includes:
  - Healthcare facilities and NGOs
  - Addresses and regions
  - Contact and web presence
  - Free‑text descriptions of specialties, procedures, equipment, and capabilities

- A separate schema document defines expected fields and meanings.

---

## What This Project Does

At a high level, the project:

1. Loads raw healthcare facility data
2. Adds **lightweight helper columns** for:
   - list‑like fields (e.g. specialties, procedures)
   - region and country grouping
   - facility type categorization
   - contact and web normalization
3. Preserves all original text for:
   - evidence
   - auditing
   - future LLM‑based extraction
4. Prepares the dataset for:
   - analysis
   - visualization
   - planning logic

---

## What This Project Does NOT Do (Yet)

- ❌ No heavy data cleaning or normalization
- ❌ No data imputation or guessing
- ❌ No automated medical classification
- ❌ No production‑grade validation
- ❌ No final UI or dashboard

These are intentionally left out at the MVP stage.

---

## Repository Structure