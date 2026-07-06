import uuid
from io import BytesIO

from PIL import Image, ImageOps
from starlette.concurrency import run_in_threadpool

from core.config import settings
from integrations.s3 import delete_from_s3, upload_to_s3


def process_profile_image(content: bytes) -> tuple[bytes, str]:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"

        output = BytesIO()
        img.save(output, "JPEG", quality=85, optimize=True)
        output.seek(0)

    return output.read(), filename


async def upload_profile_image(file_bytes: bytes, filename: str) -> None:
    key = f"{settings.s3_bucket_prefix}/{filename}"
    await run_in_threadpool(upload_to_s3, file_bytes, key)


async def delete_profile_image(filename: str | None) -> None:
    if filename is None:
        return
    key = f"{settings.s3_bucket_prefix}/{filename}"
    await run_in_threadpool(delete_from_s3, key)
