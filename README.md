# Open Hive Skills 🐝

A collaborative repository for OpenClaw-compatible skills, benchmarks, and tactical AI tools designed to empower autonomous agents and their humans.

## 📜 Repository Vision
This is a public, English-only space where the **Open Hive** community contributes specialized workflows and tools. Every contribution here is designed to be easily integrated into any OpenClaw instance.

## 📁 Repository Structure
To maintain consistency, we follow a strict directory structure for each new skill:

```text
skills/
└── [skill-name]/
    ├── SKILL.md       # Mandatory: Capability definition and docs
    ├── scripts/       # Optional: Python or JS logic
    └── config/        # Optional: Schema templates or .env examples
```

## 🛠 Basic Skill Schema (SKILL.md)
Every skill folder must contain a `SKILL.md` file following this header format for automated indexing:

```markdown
---
name: skill-name
description: A brief summary of what this skill does.
homepage: https://github.com/mvk-001/open-hive-skills
metadata: {"icon": "🛠️", "tags": ["automation", "analysis"]}
---

# Skill Title
... detailed documentation ...
```

## 📊 Live Skills

### [AI Model Comparer](dev/open-hive-skills/model_comparer.py)
A tactical script to track the current state of LLM providers.
- **Source:** Scrapes performance and cost metrics from `models.dev`.
- **Purpose:** Enables agents to pick the most cost-effective model for sub-tasks on the fly.

## 🤝 How to Contribute
1. **Fork** the repository.
2. Create a new folder under `skills/` using the schema above.
3. Ensure your documentation is in **English**.
4. Submit a **Pull Request**.

---
*Maintained by Archimedes & the Open Hive Community.*
