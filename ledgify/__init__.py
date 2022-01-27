from flask import Flask

def create_app():
    app = Flask(__name__)

    with app.app_context():
        @app.route('/')
        def hello_world():
            return "<p>Hello World!</p>"

    return app