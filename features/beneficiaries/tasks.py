from celery import shared_task
import csv, io, logging

logger = logging.getLogger(__name__)


@shared_task(name="features.beneficiaries.tasks.process_bulk_import")
def process_bulk_import(csv_content: str):
    from features.districts.models import District
    from .models import Beneficiary
    from datetime import date
    reader = csv.DictReader(io.StringIO(csv_content))
    created, errors = 0, []
    for row in reader:
        try:
            district = District.objects.get(district_name__iexact=row.get("district",""))
            Beneficiary.objects.get_or_create(
                national_id=row["national_id"],
                defaults={
                    "district": district,
                    "full_name": row.get("full_name",""),
                    "ubudehe_category": int(row.get("ubudehe_category",1)),
                    "phone_number": row.get("phone_number",""),
                    "registration_date": date.today(),
                }
            )
            created += 1
        except Exception as e:
            errors.append(f"Row {row}: {e}")
    logger.info(f"Bulk import: {created} created, {len(errors)} errors.")
    return {"created": created, "errors": errors}
