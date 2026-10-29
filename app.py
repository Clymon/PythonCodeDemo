"""Start the classroom app: python app.py"""
import argparse
from learning_lab import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Learning Lab classroom server")
    parser.add_argument("--port", type=int, default=5050)
    args = parser.parse_args()
    create_app().run(host="127.0.0.1", port=args.port, debug=False)
