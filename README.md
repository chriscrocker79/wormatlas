# WormAtlas

**[WormAtlas.org](https://wormatlas.org)** is an NIH-funded open-access anatomical atlas for *C. elegans* and other nematodes. It serves biologists, neuroscientists, parasitologists, and computational researchers globally.

This repository contains the full codebase for the WormAtlas platform redevelopment, including the custom CMS, REST API, and AI-powered anatomy search assistant (RAG pipeline).

---

## Project Overview

| Item | Detail |
|---|---|
| Production site | https://wormatlas.org |
| Development site | https://dev.wormatlas.org |
| Hosting | University of Illinois |
| Tech stack | PHP 8.0, MariaDB 10.5, HTML/CSS/JavaScript, Python 3 |
| AI search | Voyage AI embeddings (voyage-3.5) + ChromaDB |
| Accessibility | WCAG 2.1 AA required on all pages |

---

## Team

| Name | Role |
|---|---|
| Chris Crocker | Project lead / developer |
| David Hall | Lab director |
| Nate Schroeder | Lab director |
| Laura Herndon | Editor / researcher |
| Cathy Wilkow | Editor / researcher |
| Eli Conklin | Editor / researcher |
| Malia Jennings | Editor / researcher |
| Greg Parks | IT admin (University of Illinois) |

---

## Local Development Setup

### Prerequisites

- macOS with [XAMPP](https://www.apachefriends.org/) installed at `/Applications/XAMPP/`
- Python 3 (use `python3` and `pip3` — never `python` or `pip`)
- A GitHub account and Git installed on your Mac

### 1. Clone the repository

Open VS Code, go to **View → Terminal**, then run:

```bash
cd /Applications/XAMPP/xamppfiles/htdocs
git clone https://github.com/YOUR-USERNAME/wormatlas.git
cd wormatlas
```

*(Replace `YOUR-USERNAME` with the actual GitHub account name.)*

### 2. Set up your credentials file

The real credentials file is never stored in Git. You create it locally from the template:

```bash
# Make sure you are in the wormatlas project folder
cd /Applications/XAMPP/xamppfiles/htdocs/wormatlas

cp config/database.example.php config/database.php
```

Now open `config/database.php` in VS Code and fill in the actual database host, name, username, and password. Ask Chris Crocker for the development credentials.

### 3. Set up your environment variables file

```bash
cp .env.example .env
```

Open `.env` in VS Code and fill in your Voyage AI API key and database credentials. Ask Chris Crocker for access to the Voyage AI account.

### 4. Start XAMPP

```bash
sudo /Applications/XAMPP/xamppfiles/xampp start
```

### 5. Install Python dependencies (for RAG scripts)

```bash
cd /Applications/XAMPP/xamppfiles/htdocs/wormatlas

pip3 install chromadb
pip3 install voyageai
pip3 install python-dotenv
```

---

## Project Structure

```
wormatlas/
├── docs/
│   └── project_notes/       ← decisions.md, bugs.md, key_facts.md, conventions.md
├── public/
│   ├── index.php
│   ├── css/
│   ├── js/
│   └── uploads/
├── admin/                   ← CMS editing interface
├── includes/                ← Shared PHP classes and functions
├── config/
│   ├── database.example.php ← Committed template (safe)
│   └── database.php         ← Your local credentials (gitignored, never committed)
├── scripts/                 ← Python scripts for RAG, imports, validation
├── content/                 ← HTML handbook pages
├── rag_data/
│   └── chromadb/            ← Local vector database (gitignored)
├── .env.example             ← Committed template (safe)
├── .env                     ← Your local secrets (gitignored, never committed)
├── .gitignore
└── README.md
```

---

## Git Workflow

### Branch naming

```
feature/short-description    → new functionality
fix/short-description        → bug fix
chore/short-description      → tooling or config changes
docs/short-description       → documentation only
a11y/short-description       → accessibility-specific fixes
rag/short-description        → AI/RAG pipeline work
```

### Commit message format

```
type(scope): short description (max 72 characters)
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `chore`, `a11y`, `rag`

**Examples:**
```
feat(intestine-page): add entity markup to cell list
fix(wormbase-urls): correct missing IDs for 10 cells
a11y(nav): fix dropdown keyboard navigation
rag(embeddings): add ChromaDB indexing for nervous system cells
docs(decisions): log Git hosting decision
```

### Rules
- **Never commit directly to `main`**
- All work is done on a branch and merged via pull request
- No API keys, passwords, or secrets ever committed — use environment variables
- No `console.log` or debug `print` statements committed

---

## Key Documentation

All architectural decisions, known bugs, coding conventions, and project facts are maintained in `docs/project_notes/`:

| File | Purpose |
|---|---|
| `decisions.md` | Binding architectural decisions — check before recommending any library or pattern |
| `bugs.md` | Log of resolved bugs — check before debugging any known issue |
| `conventions.md` | All coding conventions — check before writing any code |
| `key_facts.md` | Config values, taxonomy IDs, team details, environment facts |

---

## Security Notes

- `config/database.php` is gitignored — **never commit it**
- `.env` is gitignored — **never commit it**
- Database dumps (`.sql` files) are gitignored — **never commit them**
- All secrets live in environment variables, never in code files
- See `conventions.md` → Security section for full policy

---

## Accessibility

WCAG 2.1 AA compliance is non-negotiable on every page and feature. See `ACCESSIBILITY_CHECKLIST.md` for the full per-component checklist that must be completed before any feature is marked ready for review.

---

## License

WormAtlas is an open-access research platform funded by NIH. Content is freely accessible. See LICENSE file for code licensing terms.
