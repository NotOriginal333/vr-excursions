import pytest

from scripts.build_seed import build_records, to_record

LESSON = {"subject": "Географія", "grade": 6, "topic": "Вулкани", "query": "volcano"}


def wikimedia_page(width=8000, height=4000, **metadata):
    values = {
        "LicenseShortName": "CC BY-SA 4.0",
        "LicenseUrl": "https://creativecommons.org/licenses/by-sa/4.0",
        "Artist": '<a href="//commons.wikimedia.org/wiki/User:Jane">Jane &amp; Co</a>',
        "ImageDescription": "<p>Mount Etna crater</p>",
        **metadata,
    }
    return {
        "pageid": 42,
        "title": "File:Etna 360.jpg",
        "imageinfo": [
            {
                "width": width,
                "height": height,
                "url": "https://upload.wikimedia.org/Etna_360.jpg",
                "thumburl": "https://upload.wikimedia.org/thumb/4096px-Etna_360.jpg",
                "descriptionurl": "https://commons.wikimedia.org/wiki/File:Etna_360.jpg",
                "extmetadata": {key: {"value": value} for key, value in values.items() if value is not None},
            }
        ],
    }


def test_full_sphere_panorama_becomes_catalog_record():
    assert to_record(wikimedia_page(), LESSON) == {
        "external_id": "42",
        "title": "Etna 360",
        "description": "Mount Etna crater",
        "content_type": "360_photo",
        "page_url": "https://commons.wikimedia.org/wiki/File:Etna_360.jpg",
        "media_url": "https://upload.wikimedia.org/thumb/4096px-Etna_360.jpg",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0",
        "author": "Jane & Co",
        "subject": "Географія",
        "grade": 6,
        "topic": "Вулкани",
    }


@pytest.mark.parametrize(
    ("width", "height", "content_type"), [(8000, 3950, "360_photo"), (6000, 1000, "partial_panorama")]
)
def test_content_type_follows_2_to_1_ratio_with_tolerance(width, height, content_type):
    assert to_record(wikimedia_page(width=width, height=height), LESSON)["content_type"] == content_type


@pytest.mark.parametrize("missing", ["LicenseShortName", "Artist"])
def test_file_without_license_or_author_is_skipped(missing):
    assert to_record(wikimedia_page(**{missing: None}), LESSON) is None


def test_file_found_for_several_topics_is_saved_once_under_the_first():
    carpathians = {"subject": "Географія", "grade": 8, "topic": "Українські Карпати", "query": "Carpathians"}
    records = build_records([LESSON, carpathians], lambda query: [wikimedia_page()])
    assert [record["topic"] for record in records] == ["Вулкани"]
