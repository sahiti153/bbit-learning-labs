"""Flask app instance creation for Tech Lab 2025."""

import os
import json

from flask import Flask, Response, jsonify

from app import newsfeed
from app.utils.file_loader import load_json_files
from app.utils.redis import REDIS_CLIENT


def create_app():
    """Create a Flask app instance."""
    app = Flask("app")

    # Load JSON files into Redis
    dataset_directory = os.path.join(os.path.dirname(__file__), "../resources/dataset/news")
    REDIS_CLIENT.save_entry("all_articles", load_json_files(dataset_directory))

    @app.route("/ping", methods=["GET"])
    def ping() -> Response:
        """Flask route to check if the server is up and running."""
        return jsonify("Pong!", 200)
    
    def _format_article_data(file_path: str) -> dict:
        """
        Private method to format data into an article object.

        Args:
            file_path (str): Path to the JSON file containing article data.

        Returns:
            dict: A dictionary representing the formatted article object.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Extracting relevant fields from the JSON structure
        article = {
            "uuid": data.get("uuid", ""),
            "title": data.get("title", "Untitled"),
            "author": data.get("author", "Unknown"),
            "published_date": data.get("thread", {}).get("published", "Unknown"),
            "url": data.get("url", ""),
            "content": data.get("text", ""),
            "main_image": data.get("thread", {}).get("main_image", ""),
            "site": data.get("thread", {}).get("site", ""),
            "social_shares": {
                "facebook": data.get("thread", {}).get("social", {}).get("facebook", {}).get("shares", 0),
                "linkedin": data.get("thread", {}).get("social", {}).get("linkedin", {}).get("shares", 0),
                "pinterest": data.get("thread", {}).get("social", {}).get("pinterest", {}).get("shares", 0),
            },
        }

        return article

    @app.route("/get-newsfeed", methods=["GET"])
    def get_newsfeed() -> Response:
        """Flask route to get the latest newsfeed from datastore."""
        # PART 1
        try:
            # Retrieve all articles from Redis
            all_articles = REDIS_CLIENT.get_entry("all_articles")
            if not all_articles:
                return jsonify({"error": "No articles found in datastore."}, 404)

            # Parse the articles and format them
            formatted_articles = []
            for file_path in all_articles:
                try:
                    article = newsfeed._format_article_data(file_path)
                    formatted_articles.append(article)
                except FileNotFoundError as e:
                    # Log the error and skip the missing file
                    print(f"Error: {e}")
                    continue

            return jsonify({"articles": formatted_articles}, 200)
        except Exception as e:
            # Handle unexpected errors
            return jsonify({"error": str(e)}, 500)
        
        return jsonify({}, 200)
        

    @app.route("/get-featured-article", methods=["GET"])
    def get_featured_article() -> Response:
        """Flask route to get the featured article from datastore."""
        # PART 2
        return jsonify({}, 200)

    return app
