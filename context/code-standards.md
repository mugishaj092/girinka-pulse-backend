# Code Standards

## General

- Keep modules small and single-purpose.
- Fix root causes — do not layer workarounds or add `try/except` to hide real errors.
- Do not mix unrelated concerns in one file or one function.
- Respect the system boundaries defined in `architecture-context.md`.
- Follow the existing patterns in already-implemented modules before inventing new ones.

## Python

- Python 3.12. No deprecated syntax.
- Type hints on all function signatures, including `self` receivers where relevant.
- Avoid bare `except:` — catch specific exception types.
- Use `logging.getLogger(__name__)` in every module that logs. Never use `print()` in production code.
- Constants and enum values live at module top level or in `constants.py` — not inlined in business logic.

## Django Models

- Every model must define `db_table` in `Meta` using the snake_case table name.
- Every model must define `ordering` in `Meta`.
- Add `models.Index` in `Meta.indexes` for every field used in filtering or ordering.
- Use `TextChoices` for all string enum fields — never raw string literals.
- FK fields should use `related_name` that reads naturally from the parent: `cow.health_records`, `beneficiary.cows`, etc.
- Computed properties belong on the model as `@property`. Business mutation methods (like `record_death`) also belong on the model.
- Always use `update_fields=[...]` when saving partial updates to avoid overwriting unrelated fields.

## Django REST Framework

- Use `ModelViewSet` for standard CRUD. Use `APIView` only for non-resource endpoints (auth, ML proxy).
- `get_serializer_class()` handles serializer switching per action — do not inline conditional serializer creation in views.
- `get_permissions()` handles permission switching per action — do not inline permission checks in view methods.
- `get_queryset()` applies role-based data scoping — do not filter in view methods.
- Use `@extend_schema` on every public endpoint with `tags`, `summary`, `description`, `request`, `responses`, and `examples`.
- Never return raw `Response({...})` for errors — raise the appropriate exception from `shared/exceptions.py`.

## Serializers

- Input serializers validate before any logic runs — never trust unvalidated data.
- Use `read_only_fields` for fields that are set by the server (timestamps, computed fields, ML outputs).
- Use `SerializerMethodField` for computed values — do not add business logic to `to_representation`.
- Nested FK representations (e.g., `district_name`, `cow_tag`) use `source=` on a `CharField` field — do not nest full serializers unless explicitly needed.

## Views and Route Handlers

- Views are thin. The sequence is: authenticate → check permission → validate input → call service/model → return response.
- No business logic in views beyond orchestration.
- No direct database queries in views — go through the model's manager or a service function.
- Long-running work (ML calls, file generation, email sending) belongs in Celery tasks triggered from views, not executed inline.
- Exception to inline ML calls: direct pass-through endpoints (disease, birth) where latency is acceptable and the call is synchronous by design.

## Celery Tasks

- Every task must be decorated with `@shared_task(name="features.<module>.tasks.<function_name>")`.
- Tasks must log their start, completion, and any errors using the module logger.
- Tasks must return a summary dict (e.g., `{"success": 5, "failed": 2}`) for visibility in Flower.
- Tasks must be idempotent where possible — running twice should not corrupt data.
- Do not trigger tasks from other tasks. Views trigger tasks.

## Exceptions

Use custom exception classes from `shared/exceptions.py`. Never return error responses manually from views.

| Exception | Error Code | HTTP Status |
|-----------|-----------|------------|
| `InsufficientMilkDataError` | `INSUFFICIENT_MILK_DATA` | 422 |
| `CowAlreadyDeceasedError` | `COW_ALREADY_DECEASED` | 422 |
| `BeneficiaryInactiveError` | `BENEFICIARY_INACTIVE` | 422 |
| `PassonPendingError` | `PASSON_PENDING` | 422 |
| `DuplicateTagNumberError` | `DUPLICATE_TAG_NUMBER` | 409 |
| `DuplicateNationalIdError` | `DUPLICATE_NATIONAL_ID` | 409 |
| `InvalidUbudehe` | `INVALID_UBUDEHE` | 400 |
| `ModelNotDeployedError` | `MODEL_NOT_DEPLOYED` | 503 |
| `PredictionFailedError` | `PREDICTION_FAILED` | 503 |
| `SMSDeliveryFailedError` | `SMS_DELIVERY_FAILED` | 502 |

To add a new exception: subclass `GirinkaException` in `shared/exceptions.py`, define `status_code`, `error_code`, and `default_message`. Do not create exceptions inside feature modules.

## Permissions

Use permission classes from `shared/permissions.py`. Do not write inline `request.user.role ==` checks in view methods.

| Class | Allowed Roles |
|-------|--------------|
| `IsFarmer` | `FARMER` |
| `IsCellLeader` | `CELL_LEADER` |
| `IsVeterinarian` | `VETERINARIAN` |
| `IsDistrictLeader` | `DISTRICT_LEADER` |
| `IsAdmin` | `ADMIN` |
| `IsCellLeaderOrAbove` | `CELL_LEADER`, `VETERINARIAN`, `DISTRICT_LEADER`, `ADMIN` |
| `IsVetOrAbove` | `VETERINARIAN`, `DISTRICT_LEADER`, `ADMIN` |
| `IsDistrictLeaderOrAdmin` | `DISTRICT_LEADER`, `ADMIN` |
| `IsSameDistrict` | Object-level: same district or Admin |

## ML Client

All calls to the ML service go through `features/predictions/ml_client.py`.

- Use the `ml_client` singleton — do not instantiate `MLClient` per request.
- `ml_client.predict_*()` methods raise `httpx.HTTPStatusError` or `httpx.RequestError` on failure.
- Callers (services or views) must handle these exceptions and raise `PredictionFailedError`.
- Never call `httpx` directly from a view or task — always go through `ml_client`.

## Cloudinary

All file operations go through `shared/cloudinary_utils.py`.

- `upload_cow_photo(file, tag)` → stores at `girinka/cows/`
- `upload_report_pdf(bytes, filename)` → stores at `girinka/reports/`
- `upload_certificate_pdf(bytes, transfer_id)` → stores at `girinka/certificates/`
- `get_signed_url(public_id)` → time-limited authenticated URL
- Never call `cloudinary.uploader.upload()` directly from a view or task — always use the helpers.

## Email

All email goes through `features/notifications/utils.py`.

- `send_email(to, subject, html)` — generic sender via Resend SDK.
- `send_alert_email(to, farmer_name, cow_tag, ...)` — formatted alert email.
- `send_password_reset_email(to, user_name, otp_code)` — OTP email.
- `send_weekly_report_email(to, report_type, period, stats, download_url)` — report email.
- Never call `resend.Emails.send()` directly from views or tasks — always use these helpers.

## File Organization

```
features/<module>/
├── models.py       — ORM models
├── serializers.py  — DRF serializers
├── views.py        — ViewSets and APIViews
├── urls.py         — URL routing
├── tasks.py        — Celery tasks
├── filters.py      — django-filter FilterSets
├── signals.py      — Django signals
├── admin.py        — Django admin registration
├── apps.py         — App configuration
├── constants.py    — Module-level constants (if needed)
├── exceptions.py   — (do not add — use shared/exceptions.py)
└── tests/
    ├── test_models.py
    ├── test_views.py
    └── test_serializers.py
```

## Naming Conventions

| Thing | Convention | Example |
|-------|-----------|---------|
| Feature module | snake_case directory | `features/cows/` |
| Model class | PascalCase | `HealthRecord` |
| TextChoices class | PascalCase | `HealthStatus` |
| Serializer | PascalCase + `Serializer` | `CowCreateSerializer` |
| ViewSet | PascalCase + `ViewSet` | `CowViewSet` |
| Celery task | `snake_case` function | `run_daily_risk_assessment` |
| Task name string | `features.<module>.tasks.<name>` | `"features.predictions.tasks.run_daily_risk_assessment"` |
| URL name | `<module>-<action>` | `cows-list`, `cows-detail` |
| DB table | `snake_case` | `health_records` |

## Testing

- Tests live in `tests/` at the project root for integration tests and in `features/<module>/tests/` for unit tests.
- Use `pytest` with `pytest-django`.
- Fixtures live in `tests/conftest.py`.
- Always test: valid input returns expected output, invalid input returns correct error code, role permissions are enforced correctly.
- Mock ML service calls with `unittest.mock.patch` — never make real HTTP calls in tests.
- Mock Cloudinary and Resend in tests.
