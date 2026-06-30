# Runtime Validation Report

## Overview
This report outlines the end-to-end verification and stabilization of the Neural Constitution Engine (NCE) application layer (Milestone 20). The application now successfully boots, routes are registered properly, and core evaluation pipelines execute successfully from HTTP schemas down to the Governance Kernel.

## Fixes Implemented

### 1. Router Registration Bug
**Issue:** Application initialization failed because `app.routes` contained `_IncludedRouter` objects instead of `APIRoute` objects, breaking middleware and Swagger UI.
**Cause:** Incompatibility with FastAPI >=0.112 where internal routing behavior changed.
**Resolution:** Pinned FastAPI to `>=0.111.0,<0.112.0` in `pyproject.toml` to restore compatibility without requiring deep internal refactoring.

### 2. Authentication 500 Error
**Issue:** `GET /auth/me` returned a `500 Internal Server Error`.
**Cause:** The `User` model did not have its `organizations` relationship eagerly loaded, triggering a `DetachedInstanceError` in SQLAlchemy.
**Resolution:** Updated `UserRepository.get_by_id` and `get_by_email` to use `selectinload(User.organizations)`.

### 3. Evaluation Service Type & Serialization Errors
**Issue:** The `/evaluate` and `/plans/evaluate` endpoints crashed with `TypeError` for datetimes and `AttributeError` for schema mismatches.
**Cause:**
- The `AuditRecordSchema` lacked `api_version`.
- Pydantic models with `uuid.UUID` and `datetime.datetime` objects caused SQLAlchemy JSON serialization to fail.
- Timezone naive/aware conflicts during PostgreSQL inserts via asyncpg.
- Node audits were incorrectly iterated on a `PlanValidationResultSchema` rather than the `sdk_result`.
**Resolution:**
- Replaced direct `api_version` accesses with `audit.request.api_version`.
- Converted Pydantic models directly to JSON-safe dictionaries using `model_dump(mode="json")`.
- Stripped timezone info from `recorded_at` (`recorded_at.replace(tzinfo=None)`) to conform with naive PostgreSQL TIMESTAMP types.
- Fixed the validation loop to correctly process audits from the SDK.

### 4. API End-to-End Verification
All major workflows have been verified via `pytest` test suite coverage:
- **Health/Version**: `/health`, `/version` endpoints run without errors.
- **Authentication**: Registration and JWT issuance work.
- **Validation**: `/validate` endpoint accurately processes Constitution YAML payloads.
- **Evaluation**: Engine properly bridges `DecisionRequest` to the Kernel, evaluates it, and generates an `AuditRecord` that is correctly translated and persisted to the database.

## Summary
The Neural Constitution Engine application layer has been stabilized and verified. The strict separation between the Governance Kernel and Application Layer has been maintained, fulfilling the architectural requirements of the platform.
