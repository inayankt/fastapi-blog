from collections.abc import Iterator
from io import BytesIO

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=settings.s3_region,
        aws_access_key_id=(
            settings.s3_access_key_id.get_secret_value()
            if settings.s3_access_key_id
            else None
        ),
        aws_secret_access_key=(
            settings.s3_secret_access_key.get_secret_value()
            if settings.s3_secret_access_key
            else None
        ),
        endpoint_url=settings.s3_endpoint_url,
    )


def upload_to_s3(file_bytes: bytes, key: str) -> None:
    s3 = get_s3_client()
    s3.upload_fileobj(
        BytesIO(file_bytes),
        settings.s3_bucket_name,
        key,
        ExtraArgs={"ContentType": "image/jpeg"},
    )


def delete_from_s3(key: str) -> None:
    s3 = get_s3_client()
    s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)


def iter_objects(prefix: str) -> Iterator[str]:
    s3 = get_s3_client()

    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(
        Bucket=settings.s3_bucket_name,
        Prefix=prefix,
    ):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def delete_prefix(prefix: str) -> None:
    s3 = get_s3_client()

    batch = []

    for key in iter_objects(prefix):
        batch.append({"Key": key})
        if len(batch) == 1000:
            s3.delete_objects(
                Bucket=settings.s3_bucket_name,
                Delete={"Objects": batch},
            )
            batch.clear()

    if batch:
        s3.delete_objects(
            Bucket=settings.s3_bucket_name,
            Delete={"Objects": batch},
        )


def check_s3_connection():
    s3 = get_s3_client()

    print(f"Bucket: {settings.s3_bucket_name}")
    print(f"Region: {settings.s3_region}")
    print()

    test_key = f"{settings.s3_bucket_prefix}/test.txt"

    try:
        s3.upload_fileobj(
            BytesIO(b"test"),
            settings.s3_bucket_name,
            test_key,
            ExtraArgs={"ContentType": "text/plain"},
        )
        print("Upload: SUCCESS")
    except (BotoCoreError, ClientError) as exc:
        print(f"Upload: FAILED - {exc}")
        return

    try:
        s3.delete_object(Bucket=settings.s3_bucket_name, Key=test_key)
        print("Delete: SUCCESS")
    except (BotoCoreError, ClientError) as exc:
        print(f"Delete: FAILED - {exc}")
        return

    try:
        s3.list_objects_v2(
            Bucket=settings.s3_bucket_name,
            Prefix=f"{settings.s3_bucket_prefix}/",
            MaxKeys=1,
        )
        print("List: SUCCESS")
    except (BotoCoreError, ClientError) as exc:
        print(f"List: FAILED - {exc}")
        return

    print()
    print("All tests passed, S3 configuration is working")


if __name__ == "__main__":
    check_s3_connection()
