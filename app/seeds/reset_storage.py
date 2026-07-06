from core.config import settings
from integrations.s3 import delete_prefix


def reset_storage() -> None:
    print("\nDeleting profile pictures...")

    delete_prefix(f"{settings.s3_bucket_prefix}/")

    print("\nDone!")
