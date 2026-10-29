"""Application setup. Routes, learning rules and storage live in separate files."""
import json
import os
import secrets
from pathlib import Path
from flask import Flask
from . import db, routes


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=str(Path(app.instance_path) / "learning-lab.sqlite"))
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config.get("SECRET_KEY"):
        key_file = Path(app.instance_path) / ".session-key"
        try:
            with key_file.open("x", encoding="utf-8") as stream:
                os.chmod(key_file, 0o600)
                stream.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config["SECRET_KEY"] = key_file.read_text(encoding="utf-8")
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                      MAX_CONTENT_LENGTH=8192)
    app.config["CATALOG"] = json.loads(
        (Path(app.root_path) / "data/catalog.json").read_text(encoding="utf-8"))
    db.init_app(app)
    app.register_blueprint(routes.bp)
    return app
