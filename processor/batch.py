import os

from django.conf import settings

from .models import BatchJob, ImageUpload
from .halftone import apply_halftone


def process_batch(batch_id):
    """Process all images in a batch job."""
    batch = BatchJob.objects.get(pk=batch_id)
    batch.status = "processing"
    batch.save()

    dot_spacing = 10
    style = "classic"
    try:
        profile = batch.user.profile
        dot_spacing = profile.dot_spacing
        style = profile.style
    except Exception:
        pass

    images = ImageUpload.objects.filter(batch=batch)
    processed_count = 0
    for upload in images:
        try:
            original_path = upload.original.path
            filename = f"halftone_{upload.pk}.png"
            output_path = os.path.join(settings.MEDIA_ROOT, "processed", filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            apply_halftone(
                original_path, output_path,
                dot_spacing=dot_spacing, style=style,
            )

            upload.processed = f"processed/{filename}"
            upload.save()

            processed_count += 1
            batch.processed_count = processed_count
            batch.save()
        except Exception:
            continue

    batch.status = "completed"
    batch.save()
