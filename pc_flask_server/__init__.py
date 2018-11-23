import os
import threading

from flask import Flask

VERSION = "0.0.1"

def check_media_folder(prev_folder_contents):
  # uses timed threads to recursively chek for new items in the folder every 10 seconds
  folder_contents = []
  new_file = False
  for root, dirs, files in os.walk("./pc_flask_server/media"):
    for filename in files:
      folder_contents.append(filename)
      if not filename in prev_folder_contents:
        print(filename)
        new_file = True
  if not new_file:
    print("No new files")
  threading.Timer(10.0, check_media_folder, [folder_contents]).start()

def get_folder_contents():
    # simply returns list of contents of folder
    folder_contents = []
    for root, dirs, files in os.walk("./pc_flask_server/media"):
        for filename in files:
            folder_contents.append(filename)
    return folder_contents


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'grandtotemPcServer.sqlite'),
        CONFIG_FILE=os.path.join(app.instance_path, 'server_settings.config'),
        GOOGLE_DRIVE_DIR=os.path.join(app.instance_path, 'google_drive_folder')
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

    check_media_folder(get_folder_contents())
    return app


application = create_app()
