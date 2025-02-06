import json
import time
from flask_caching import Cache
from flask import Flask, jsonify, request, render_template
import requests
import os
import logging

app = Flask(__name__)
BASE_URL = "https://bible-api.com"
PORT = os.environ.get("PORT", 5000)

# Initialize the cache after creating the Flask app
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add request timing decorator
def log_request_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Request to {request.path} took {end_time - start_time:.2f} seconds")
        return result

    return wrapper


# Add rate limiting decorator
def rate_limit(max_requests=100, time_window=60):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ip_address = request.remote_addr
            cache_key = f"rate_limit:{ip_address}"

            # Get current count (returns None if not found)
            current_count = cache.get(cache_key)

            # Initialize count if not found
            if current_count is None:
                current_count = 0

            if current_count >= max_requests:
                return jsonify({
                    "error": f"Rate limit exceeded. Please wait {time_window} seconds."
                }), 429

            # Increment and store count
            cache.set(cache_key, current_count + 1, time_window)
            return func(*args, **kwargs)

        return wrapper

    return decorator

@log_request_time
@rate_limit(max_requests=100, time_window=60)
@app.route("/", methods=["GET"])
def homepage():
    """Homepage for EveryDay Bible App"""
    return render_template("index.html")

@log_request_time
@rate_limit(max_requests=100, time_window=60)
@app.route("/translations", methods=["GET"])
def get_translations():
    """Fetch available Bible translations."""
    url = f"{BASE_URL}/data"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        translations = data.get("translations", [])
        return jsonify(translations)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch translations: {e}")
        return jsonify({"error": "Failed to fetch translations"}), 500


@log_request_time
@rate_limit(max_requests=100, time_window=60)
@app.route("/books", methods=["GET"])
def get_books():
    """Fetch available books of the Bible."""
    translation = request.args.get("translation", "web")
    url = f"{BASE_URL}/data/{translation}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        books = [book["name"] for book in data.get("books", [])]
        return jsonify(books)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch books: {e}")
        return jsonify({"error": "Failed to fetch books"}), 500

@log_request_time
@rate_limit(max_requests=100, time_window=60)
def normalize_book_name(name):
    """Normalize a book name for API lookup."""
    if not name:
        return name

    # Split the book name into parts
    parts = [part.strip() for part in name.split()]

    # Process each part, preserving numbers but capitalizing words
    normalized_parts = []
    for part in parts:
        if part.isdigit():
            normalized_parts.append(part)
        else:
            normalized_parts.append(part.capitalize())

    return " ".join(normalized_parts)

@log_request_time
@rate_limit(max_requests=100, time_window=60)
def get_book_id(translation, book_name):
    """Get the book ID for a given book name in the specified translation."""
    try:
        # Normalize the book name
        normalized_book = normalize_book_name(book_name)
        logger.info(f"Looking up book: '{book_name}' -> normalized to: '{normalized_book}'")

        # Try multiple variations
        variations = [
            normalized_book,
            normalized_book.replace(" ", ""),
            normalized_book.lower(),
            normalized_book.upper()
        ]

        # Fetch books list
        books_url = f"{BASE_URL}/data/{translation}"
        logger.info(f"Fetching books list from: {books_url}")
        books_data = requests.get(books_url)
        books_data.raise_for_status()
        books_json = books_data.json()

        # Try each variation
        for variation in variations:
            logger.info(f"Attempting to find book: '{variation}'")
            book_id = next((b["id"] for b in books_json["books"]
                            if b["name"].lower() == variation.lower()), None)
            if book_id:
                logger.info(f"Found book ID: {book_id}")
                return book_id

        logger.error(f"Book not found in any variation: {variations}")
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching book ID: {e}")
        return None

@log_request_time
@rate_limit(max_requests=100, time_window=60)
@app.route("/chapters", methods=["GET"])
def get_chapters():
    """Fetch available chapters of a book in a translation."""
    book = request.args.get("book")
    translation = request.args.get("translation")

    if not book:
        return jsonify({"error": "Missing required parameter: book"}), 400

    # Get book ID
    book_id = get_book_id(translation, book)
    if not book_id:
        return jsonify({
            "error": f"Book '{book}' not found in the {translation} translation"
        }), 404

    try:
        # Fetch chapters
        scripture_url = f"{BASE_URL}/data/{translation}/{book_id}"
        logger.info(f"Fetching chapters from: {scripture_url}")
        scripture_data = requests.get(scripture_url)
        scripture_data.raise_for_status()
        scripture_json = scripture_data.json()

        chapters = sorted(int(chapter["chapter"]) for chapter in scripture_json.get("chapters", []))
        return jsonify(chapters)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch chapters: {e}")
        return jsonify({"error": "Failed to fetch chapters"}), 500


@app.route("/read", methods=["GET"])
def read_scripture():
    """Fetch scripture based on book, chapter, and translation."""
    book = request.args.get("book")
    chapter = request.args.get("chapter")
    translation = request.args.get("translation", "web")

    if not book or not chapter:
        return jsonify({"error": "Missing required parameters: book, chapter"}), 400

    # Get book ID
    book_id = get_book_id(translation, book)
    if not book_id:
        return jsonify({
            "error": f"Book '{book}' not found in the {translation} translation"
        }), 404

    try:
        # Fetch the specific chapter
        scripture_url = f"{BASE_URL}/data/{translation}/{book_id}/{chapter}"
        logger.info(f"Fetching scripture from: {scripture_url}")
        scripture_data = requests.get(scripture_url)
        scripture_data.raise_for_status()
        scripture_json = scripture_data.json()

        verses = scripture_json.get("verses", [])
        if not verses:
            return jsonify({"error": "No verses found for this chapter"}), 404

        # Render an HTML page with the verses
        return render_template("scripture.html",
                               book=book,
                               chapter=chapter,
                               translation=translation,
                               verses=verses)

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch scripture: {e}")
        return jsonify({"error": "Failed to fetch scripture"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=int(PORT))
