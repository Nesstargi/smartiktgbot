import asyncio
from io import BytesIO

from PIL import Image

from bot.handlers import catalog_common


def _large_png_bytes() -> bytes:
    image = Image.new("RGBA", (2200, 1800), (10, 140, 240, 180))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_png_to_jpeg_bytes_converts_and_resizes_image():
    result = catalog_common._png_to_jpeg_bytes(_large_png_bytes(), "banner.png")

    assert result is not None
    assert result.filename == "banner.jpg"

    with Image.open(BytesIO(result.data)) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert max(image.size) == catalog_common.TELEGRAM_IMAGE_MAX_SIZE


def test_photo_payload_returns_cached_file_id_without_fetch(monkeypatch):
    photo_ref = "/media/banner.jpg"
    cached_file_id = "AgACAgIAAxkBAAIBQ2gXsampleFileId123456789"
    cache_key = catalog_common.media_cache_key(photo_ref)
    original_cache = dict(catalog_common.media_file_id_cache)

    def should_not_resolve(_photo_ref):
        raise AssertionError("local media resolution should not run for cached file_ids")

    catalog_common.media_file_id_cache.clear()
    catalog_common.media_file_id_cache[cache_key] = cached_file_id
    monkeypatch.setattr(catalog_common, "_resolve_local_media_path", should_not_resolve)

    try:
        payload = asyncio.run(catalog_common.photo_payload(photo_ref))
    finally:
        catalog_common.media_file_id_cache.clear()
        catalog_common.media_file_id_cache.update(original_cache)

    assert payload == cached_file_id


def test_photo_payload_converts_local_png_before_send(tmp_path):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(_large_png_bytes())

    payload = asyncio.run(catalog_common.photo_payload(str(image_path)))

    assert payload is not None
    assert payload.filename == "sample.jpg"

    with Image.open(BytesIO(payload.data)) as image:
        assert image.format == "JPEG"
        assert image.mode == "RGB"
        assert max(image.size) == catalog_common.TELEGRAM_IMAGE_MAX_SIZE
