# Analyst Assist: OSINT Text Triage & Risk Scoring (NLP)

## Overview

**Analyst Assist** is a lightweight, end-to-end NLP prototype that demonstrates how unstructured open-source text (e.g., news blurbs, forum posts, incident notes) can be transformed into **analyst-ready decision support**.

The notebook ingests raw text, classifies it into mission-relevant categories, assigns an interpretable **risk score**, and produces short summaries enriched with keywords and named entities. The focus is on **clarity, interpretability, and delivery**, not black-box modeling.

This project is intentionally designed to mirror applied data science work in **risk, compliance, intelligence, and analyst-support environments**.

---

## Core Capabilities

* Text cleaning and normalization
* TF-IDF–based feature extraction (unigrams + bigrams)
* Multi-class text classification using a linear model
* Interpretable risk scoring (0–100)
* Keyword extraction for transparency
* Named entity recognition (people, organizations, locations, dates)
* Analyst-facing summary generation
* Lightweight sentiment signal + alert tiering
* Export analyst-ready views to CSV/HTML

---

## Pipeline Overview

1. **Data Ingestion**
   Loads a subset of open-source text data and maps raw topics into higher-level, mission-oriented categories.

2. **Text Preprocessing**
   Normalizes text by lowercasing, removing noise, and standardizing formatting.

3. **Vectorization & Modeling**
   Converts text to TF-IDF features and trains a linear classifier for fast, interpretable predictions.

4. **Model Evaluation**
   Evaluates performance using precision, recall, F1-score, and a confusion matrix.

5. **Risk Scoring**
   Combines prediction confidence with category severity weights to produce a normalized risk score.

6. **Analyst Outputs**
   Generates keyword explanations, entity extraction, and concise summaries suitable for analyst triage.

---

## Example Analyst Output

Each record in the final output includes:

* Text excerpt
* Predicted category (e.g., Cyber, Fraud, Physical Threat)
* Confidence score
* Risk score (0–100)
* Top explanatory keywords
* Extracted named entities
* Auto-generated analyst summary

This mirrors how analysts might rapidly triage and prioritize incoming information.

---

## Tech Stack

* **Language:** Python
* **NLP & ML:** scikit-learn, TF-IDF, Logistic Regression
* **Data Handling:** pandas, NumPy
* **Visualization:** matplotlib
* **Entity Extraction:** spaCy

All components were selected for **simplicity, reproducibility, and interpretability**.

---

## Getting Started

### Requirements

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Running the Notebook

1. Open `notebook.ipynb`
2. Run cells top to bottom
3. Review the final **Analyst View** table

No external APIs or credentials are required.

---

## Design Philosophy

This project prioritizes:

* **Explainability over complexity**
* **Analyst trust over model sophistication**
* **End-to-end delivery over isolated experimentation**

The goal is to show how NLP can be operationalized to support real decision-making, not just achieve high benchmark scores.

---

## Future Enhancements

* Swap in alternative datasets (AG News, Enron emails)
* Add topic modeling for exploratory analysis

---

## Author

**Dakari Antoine**
Applied Data Scientist | Python | NLP | Risk & Analytics Systems

GitHub: [https://github.com/karisheen](https://github.com/karisheen)
LinkedIn: [https://linkedin.com/in/dakari-antoine](https://linkedin.com/in/dakari-antoine)

---

*This project is intended as a demonstration of applied NLP techniques for analyst support and decision-oriented analytics.*
