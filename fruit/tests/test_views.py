import pytest
from django.test import Client
from fruit.views import FRUIT_LIST


@pytest.fixture
def client():
    return Client()


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------

def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_renders_html(client):
    response = client.get("/")
    assert b"Fruit List" in response.content


# ---------------------------------------------------------------------------
# GET /fruit  —  no filters
# ---------------------------------------------------------------------------

def test_fruit_returns_200(client):
    response = client.get("/fruit")
    assert response.status_code == 200


def test_fruit_returns_json_list(client):
    response = client.get("/fruit")
    data = response.json()
    assert isinstance(data, list)


def test_fruit_returns_all_items(client):
    response = client.get("/fruit")
    assert len(response.json()) == len(FRUIT_LIST)


def test_fruit_items_have_required_fields(client):
    response = client.get("/fruit")
    for item in response.json():
        assert "id" in item
        assert "name" in item
        assert "color" in item
        assert "in_season" in item


# ---------------------------------------------------------------------------
# GET /fruit?color=
# ---------------------------------------------------------------------------

def test_filter_by_color_red(client):
    response = client.get("/fruit?color=red")
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert item["color"].lower() == "red"


def test_filter_by_color_case_insensitive(client):
    lower = client.get("/fruit?color=red").json()
    upper = client.get("/fruit?color=RED").json()
    mixed = client.get("/fruit?color=ReD").json()
    assert lower == upper == mixed


def test_filter_by_nonexistent_color_returns_empty(client):
    response = client.get("/fruit?color=turquoise")
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /fruit?in_season=
# ---------------------------------------------------------------------------

def test_filter_in_season_true(client):
    response = client.get("/fruit?in_season=true")
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert item["in_season"] is True


def test_filter_in_season_false(client):
    response = client.get("/fruit?in_season=false")
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert item["in_season"] is False


def test_in_season_counts_sum_to_total(client):
    in_season  = len(client.get("/fruit?in_season=true").json())
    out_season = len(client.get("/fruit?in_season=false").json())
    total      = len(client.get("/fruit").json())
    assert in_season + out_season == total


# ---------------------------------------------------------------------------
# GET /fruit?name=  (partial, case-insensitive)
# ---------------------------------------------------------------------------

def test_filter_by_name_partial(client):
    response = client.get("/fruit?name=app")
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert "app" in item["name"].lower()


def test_filter_by_name_case_insensitive(client):
    lower = client.get("/fruit?name=app").json()
    upper = client.get("/fruit?name=APP").json()
    mixed = client.get("/fruit?name=aPp").json()
    assert lower == upper == mixed


def test_filter_by_name_no_match_returns_empty(client):
    response = client.get("/fruit?name=zzzzz")
    assert response.json() == []


# ---------------------------------------------------------------------------
# Combined filters
# ---------------------------------------------------------------------------

def test_filter_color_and_in_season(client):
    response = client.get("/fruit?color=red&in_season=true")
    data = response.json()
    for item in data:
        assert item["color"].lower() == "red"
        assert item["in_season"] is True


def test_filter_all_three_params(client):
    response = client.get("/fruit?color=red&in_season=true&name=a")
    data = response.json()
    for item in data:
        assert item["color"].lower() == "red"
        assert item["in_season"] is True
        assert "a" in item["name"].lower()
