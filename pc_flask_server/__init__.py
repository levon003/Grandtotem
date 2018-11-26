import os

from flask import Flask

VERSION = "0.1.0"
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'grandtotemPcServer.sqlite'),
        CONFIG_FILE=os.path.join(app.instance_path, 'server_settings.config'),
        PASSWORD_FILE="csci5127.grandtotem.password",
        GOOGLE_DRIVE_DIR=os.path.join(app.root_path, 'media')
    )

    app.config.version = VERSION

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    from . import endpoints
    app.register_blueprint(endpoints.bp)
    app.add_url_rule('/', endpoint='index')

    from . import videos
    app.register_blueprint(videos.bp)

    return app


application = create_app()
