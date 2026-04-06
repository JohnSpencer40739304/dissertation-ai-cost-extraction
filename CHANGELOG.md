# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

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
