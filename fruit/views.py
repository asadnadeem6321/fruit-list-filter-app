import json
from pathlib import Path

from django.http import JsonResponse
from django.shortcuts import render

# Load fruit data once at module level (no DB needed)
FRUIT_FILE = Path(__file__).resolve().parent.parent / "fruitList.json"

with open(FRUIT_FILE, "r") as f:
    FRUIT_LIST = json.load(f)


def index(request):
    """Render the main HTML page (the frontend)."""
    return render(request, "fruit/index.html")


def fruit_api(request):
    """
    GET /fruit
    Query params:
      - color      : exact match, case-insensitive
      - in_season  : 'true' or 'false'
      - name       : partial, case-insensitive match anywhere in the name
    """
    results = list(FRUIT_LIST)  # shallow copy to avoid mutating the original

    color = request.GET.get("color")
    in_season = request.GET.get("in_season")
    name = request.GET.get("name")

    if color:
        results = [f for f in results if f["color"].lower() == color.lower()]

    if in_season is not None and in_season != "":
        if in_season.lower() == "true":
            results = [f for f in results if f["in_season"] is True]
        elif in_season.lower() == "false":
            results = [f for f in results if f["in_season"] is False]

    if name:
        results = [f for f in results if name.lower() in f["name"].lower()]

    return JsonResponse(results, safe=False)
