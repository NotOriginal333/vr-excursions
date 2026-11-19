from tests.conftest import excursion


def titles(client, **params):
    return [item["title"] for item in client.get("/api/excursions", params=params).json()["items"]]


def test_health_reports_ok(make_client):
    with make_client() as client:
        assert client.get("/api/health").json() == {"status": "ok"}


def test_catalog_is_paginated(make_client):
    with make_client(*(excursion(f"Volcano {n}") for n in range(3))) as client:
        page = client.get("/api/excursions", params={"page": 2, "size": 2}).json()

    assert (page["total"], page["page"], page["size"]) == (3, 2, 2)
    assert [item["title"] for item in page["items"]] == ["Volcano 2"]


def test_catalog_filters_by_subject_grade_topic_and_content_type(make_client):
    records = [
        excursion("Etna"),
        excursion("Giza", subject="Історія", topic="Стародавній Єгипет"),
        excursion("Mars crater", grade=5),
        excursion("Partial", content_type="partial_panorama"),
    ]
    with make_client(*records) as client:
        assert titles(client, subject="Історія") == ["Giza"]
        assert titles(client, grade=5) == ["Mars crater"]
        assert titles(client, topic="Вулкани", grade=6, content_type="360_photo") == ["Etna"]
        assert titles(client, content_type="partial_panorama") == ["Partial"]


def test_blank_filters_from_the_search_form_mean_any(make_client):
    with make_client(excursion("Etna")) as client:
        assert titles(client, q="", subject="", grade="", topic="", content_type="") == ["Etna"]


def test_search_matches_word_prefixes_in_title_description_and_topic(make_client):
    records = [
        excursion("Mount Etna", description="Active stratovolcano in Sicily"),
        excursion("Giza", subject="Історія", topic="Стародавній Єгипет"),
        excursion("Reef", topic="Коралові рифи"),
    ]
    with make_client(*records) as client:
        assert titles(client, q="mount strato") == ["Mount Etna"]
        assert titles(client, q="Єгип") == ["Giza"]
        assert titles(client, q="коралові") == ["Reef"]
        assert titles(client, q="giza reef") == []


def test_search_without_words_returns_whole_catalog(make_client):
    with make_client(excursion("Etna")) as client:
        assert titles(client, q="!!! &&") == ["Etna"]


def test_excursion_card_returns_details_or_404(make_client):
    with make_client(excursion("Etna", author="Jane")) as client:
        excursion_id = client.get("/api/excursions").json()["items"][0]["id"]
        card = client.get(f"/api/excursions/{excursion_id}").json()
        missing = client.get("/api/excursions/999999")

    assert card["author"] == "Jane"
    assert missing.status_code == 404


def test_numbers_outside_postgres_integer_range_are_rejected(make_client):
    with make_client() as client:
        statuses = [
            client.get("/api/excursions/3000000000").status_code,
            client.get("/api/excursions", params={"grade": -3000000000}).status_code,
            client.get("/api/excursions", params={"page": 10**18}).status_code,
        ]
    assert statuses == [422, 422, 422]


def test_topics_are_distinct_and_sorted(make_client):
    records = [excursion("Giza", subject="Історія", topic="Стародавній Єгипет"), excursion("Etna"), excursion("Fuji")]
    with make_client(*records) as client:
        assert client.get("/api/topics").json() == [
            {"subject": "Географія", "grade": 6, "topic": "Вулкани"},
            {"subject": "Історія", "grade": 6, "topic": "Стародавній Єгипет"},
        ]


def test_seed_is_loaded_only_into_an_empty_catalog(make_client):
    with make_client(excursion("Etna")):
        pass
    with make_client(excursion("Fuji")) as client:
        assert titles(client) == ["Etna"]


def test_repeated_search_is_served_from_cache_for_the_configured_ttl(make_client, cache):
    with make_client(excursion("Etna"), cache_ttl_seconds=30) as client:
        first = client.get("/api/excursions", params={"q": "etna"}).json()
        second = client.get("/api/excursions", params={"q": "etna"}).json()

    assert first == second
    assert [ttl for _, ttl in cache.writes] == [30]


def test_metrics_expose_request_counts_and_latency(make_client):
    with make_client() as client:
        client.get("/api/health")
        metrics = client.get("/metrics").text

    request_counts = [line for line in metrics.splitlines() if line.startswith("http_requests_total{")]
    assert any('handler="/api/health"' in line for line in request_counts)
    assert "http_request_duration_highr_seconds_bucket" in metrics
