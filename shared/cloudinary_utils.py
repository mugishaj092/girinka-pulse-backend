"""
Cloudinary upload helpers for Girinka Pulse.
Used for: reports (PDF), certificates (PDF), cow photos.
"""
import logging
import cloudinary.uploader
import cloudinary.api

logger = logging.getLogger(__name__)


def upload_report_pdf(file_path_or_bytes, filename: str, folder: str = "girinka/reports") -> str | None:
    """Upload a PDF report. Returns the secure URL."""
    try:
        result = cloudinary.uploader.upload(
            file_path_or_bytes,
            folder=folder,
            public_id=filename.replace(".pdf", ""),
            resource_type="raw",            # PDFs are raw resources in Cloudinary
            overwrite=True,
            access_mode="authenticated",    # private — needs signed URL
        )
        url = result.get("secure_url", "")
        logger.info(f"Uploaded report to Cloudinary: {url}")
        return url
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        return None


def upload_certificate_pdf(file_bytes, transfer_id: int) -> str | None:
    """Upload a pass-on transfer certificate."""
    return upload_report_pdf(
        file_bytes,
        filename=f"certificate_{transfer_id}.pdf",
        folder="girinka/certificates",
    )


def upload_cow_photo(image_file, cow_tag: str) -> str | None:
    """Upload a cow profile photo. Returns public URL."""
    try:
        result = cloudinary.uploader.upload(
            image_file,
            folder="girinka/cows",
            public_id=f"cow_{cow_tag}",
            resource_type="image",
            overwrite=True,
            transformation=[
                {"width": 800, "height": 600, "crop": "limit"},
                {"quality": "auto"},
                {"fetch_format": "auto"},
            ],
        )
        url = result.get("secure_url", "")
        logger.info(f"Uploaded cow photo: {url}")
        return url
    except Exception as e:
        logger.error(f"Cow photo upload failed: {e}")
        return None


def get_signed_url(public_id: str, resource_type: str = "raw", expires_in: int = 3600) -> str:
    """Generate a time-limited signed URL for private Cloudinary resources."""
    import time
    try:
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            resource_type=resource_type,
            type="authenticated",
            sign_url=True,
            expires_at=int(time.time()) + expires_in,
        )
        return url
    except Exception as e:
        logger.error(f"Signed URL generation failed: {e}")
        return ""


def delete_resource(public_id: str, resource_type: str = "raw") -> bool:
    """Delete a resource from Cloudinary."""
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return True
    except Exception as e:
        logger.error(f"Cloudinary delete failed: {e}")
        return False
