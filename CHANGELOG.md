# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

Added
- Extrapolation engine scaffolding (planned)
- Improved PDF ETL engine evaluation (planned)
- Future integration of AI‑assisted cost prediction (planned)

Changed
- Pending improvements to extraction pipeline

- Pending improvements to normalisation prompts

##  [1.1.0] – 2026‑06‑10
### Added
Excel add‑in with:
- File selector
- CleanCostData and CleanCostDataAttributes sheet generation
- Joined table builder
- Selective column locking
- Correction engine
- Initial extraction + normalisation pipeline.

Full automated pipeline in Excel add‑in:
Upload → Extract → Normalise → Auto‑Load → Joined Sheet.
- loadSelectedFileById() helper to reuse existing load pipeline.
- Busy overlay for long‑running Excel operations.
- Auto‑refresh of joined sheet when table_index changes.
- Improved dropdown population for table selection.
- Git‑ready .gitignore excluding node_modules and build artifacts.
- Production‑ready README.md with architecture, setup, and pipeline docs.
- Regenerated requirements.txt with stable, pinned versions.

### Changed
Normalisation no longer returns clean tables directly; Excel now fetches final DB tables.
Updated taskpane.js to remove duplicate function definitions.
Refactored upload pipeline to avoid duplicated logic.
Improved logging for pipeline stages.

### Fixed
Crash in populateTableDropdown() when normalise response lacked clean tables.
Cursor reset issue during Excel.run() operations.
Dropdown not updating after new file upload.
Auto‑load not triggering after normalisation.

##  [1.0.0] – 2026‑05-20
### Added
- Normalisation endpoint
- Corrections ingestion endpoint
- PostgreSQL integration with SQLAlchemy models.

## [0.4.0] - 2026-04-06
### Added
- Unified metadata extraction layer for PDF, DOCX, and Excel.
- New `extraction_metadata` JSONB column in PostgreSQL.
- Structural metrics per format (page counts, table counts, image counts, etc.).
- Updated extractors to compute and return metadata.
- Updated FastAPI router to include metadata in responses.
- SQL validation queries for metadata and extraction results.
- README documentation for Week 4.

### Fixed
- SQLAlchemy `metadata` reserved keyword conflict (renamed to `extraction_metadata`).
- PDF extractor `NameError: images not defined`.

### Improved
- More consistent API response structure across all formats.
- Faster DOCX extraction performance.
- Cleaner database schema and model definitions.

---

## [0.3.0] - 2026-03-30
### Added
- Initial multi-format extraction (PDF, DOCX, Excel).
- Base database schema for uploaded files and extracted content.
- Raw text, tables, and images storage.

---

## [0.2.0] - 2026-03-15
### Added
- File upload endpoint.
- Storage layer for uploaded files.

---

## [0.1.0] - 2026-03-05
### Added
- Project scaffolding.
- Basic FastAPI setup.
- Initial repository structure.
