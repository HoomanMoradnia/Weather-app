import os
import time
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read config
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

API_URL = CONFIG.get("API_URL")
CACHE_TTL = CONFIG.get("CACHE_TTL", 1800)
CACHE_DIR = Path(CONFIG.get("CACHE_DIR", "cache"))
LOG_FILE = Path(CONFIG.get("LOG_FILE", "logs/app.log"))
UNITS = CONFIG.get("UNITS", "metric")
LANG = CONFIG.get("LANG", "en")
MAX_RETRIES = CONFIG.get("MAX_RETRIES", 3)
BACKOFF_BASE = CONFIG.get("BACKOFF_BASE", 1)

API_KEY = os.getenv("API_KEY")

# Ensure directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")  # ok for development

# Jinja filter to format unix timestamps
@app.template_filter('datetimeformat')
def datetimeformat_filter(value):
    try:
        return datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return value


def slugify(text: str) -> str:
    """Convert city name to a safe filename (hash for safety)."""
    text = text.strip().lower()
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    return f"{text.replace(' ', '_')}_{h}"


def cache_path_for(city: str) -> Path:
    return CACHE_DIR / f"{slugify(city)}.json"


def read_cache(city: str):
    """Read cached data for a city.
    Returns:
      None if no cache,
      {"expired": True, ...} if cache exists but expired,
      cache dict if valid.
    """
    p = cache_path_for(city)
    if not p.exists():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        ts = data.get("timestamp", 0)
        if time.time() - ts <= CACHE_TTL:
            return data
        else:
            # expired: return it annotated so caller can fallback to it
            return {"expired": True, **data}
    except Exception as e:
        logging.error(f"Failed reading cache for {city}: {e}")
        return None


def write_cache(city: str, payload: dict):
    """Write payload to cache for city."""
    p = cache_path_for(city)
    try:
        payload_to_store = {
            "timestamp": time.time(),
            "data": payload
        }
        with p.open("w", encoding="utf-8") as f:
            json.dump(payload_to_store, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Failed writing cache for {city}: {e}")


def log_request(city: str, status: int, source: str, note: str = ""):
    logging.info(f"City:{city} | Status:{status} | Source:{source} | Note:{note}")


def fetch_weather_from_api(city: str):
    """Fetch weather from API with simple retry/backoff on network errors or 429."""
    if not API_KEY:
        raise RuntimeError("API_KEY not set. Put your key in .env")

    params = {
        "q": city,
        "appid": API_KEY,
        "units": UNITS,
        "lang": LANG
    }
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            # If 429, consider Retry-After header
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                note = f"429 Too Many Requests. Retry-After={retry_after}"
                log_request(city, resp.status_code, "API", note)
                if retry_after:
                    try:
                        wait = int(retry_after)
                    except ValueError:
                        wait = BACKOFF_BASE * (2 ** attempt)
                    time.sleep(wait)
                else:
                    time.sleep(BACKOFF_BASE * (2 ** attempt))
                attempt += 1
                continue
            # For other statuses, return the response object for handling
            return resp
        except requests.RequestException as e:
            # Network error or timeout
            note = f"RequestException: {e}"
            log_request(city, 0, "API", note)
            time.sleep(BACKOFF_BASE * (2 ** attempt))
            attempt += 1
    # Exhausted retries
    return None


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/weather", methods=["POST"])
def weather():
    city = request.form.get("city", "").strip()
    if not city:
        flash("Please enter a city name.", "warning")
        return redirect(url_for("index"))

    # 1. Check cache
    cache = read_cache(city)
    if cache and not cache.get("expired"):
        log_request(city, 200, "Cache", "served from cache")
        data = cache.get("data")
        ts = cache.get("timestamp", time.time())
        return render_template("index.html", weather=data, city=city, source="cache", cached_time=ts)

    # 2. Try API
    resp = fetch_weather_from_api(city)
    if resp is None:
        # Network/backoff exhausted — fallback to cache (even if expired)
        if cache:
            log_request(city, 0, "Cache", "API unreachable, served expired cache")
            ts = cache.get("timestamp", time.time())
            return render_template(
                "index.html",
                weather=cache.get("data"),
                city=city,
                source="cache_expired",
                cached_time=ts,
                warning="API is unreachable; showing the latest cached data."
            )
        else:
            flash("Service is unreachable and no cached data is available.", "danger")
            return redirect(url_for("index"))

    # If we have an HTTP response object
    try:
        status = resp.status_code
    except Exception:
        status = 0

    if status == 200:
        try:
            payload = resp.json()
            write_cache(city, payload)
            log_request(city, 200, "API", "fetched and cached")
            return render_template("index.html", weather=payload, city=city, source="api", cached_time=time.time())
        except Exception as e:
            logging.error(f"Failed parsing JSON for {city}: {e}")
            flash("Error processing the received data.", "danger")
            return redirect(url_for("index"))
    elif status == 401:
        log_request(city, 401, "API", "invalid api key")
        flash("Invalid API key. Please check your configuration.", "danger")
        return redirect(url_for("index"))
    elif status == 404:
        log_request(city, 404, "API", "city not found")
        flash("City not found. Please check the city name.", "warning")
        return redirect(url_for("index"))
    elif status == 429:
        log_request(city, 429, "API", "rate limited")
        if cache:
            ts = cache.get("timestamp", time.time())
            return render_template(
                "index.html",
                weather=cache.get("data"),
                city=city,
                source="cache_rate_limited",
                cached_time=ts,
                warning="Request rate limit reached; showing cached data."
            )
        else:
            flash("Rate limit reached and no cached data is available.", "danger")
            return redirect(url_for("index"))
    elif 500 <= status < 600:
        log_request(city, status, "API", "server error")
        if cache:
            ts = cache.get("timestamp", time.time())
            return render_template(
                "index.html",
                weather=cache.get("data"),
                city=city,
                source="cache_server_error",
                cached_time=ts,
                warning="Server error; showing the latest cached data."
            )
        else:
            flash("Server error occurred and no cached data is available.", "danger")
            return redirect(url_for("index"))
    else:
        log_request(city, status, "API", "other error")
        flash(f"Error fetching data: HTTP {status}", "danger")
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
