from os.path import dirname, abspath, join

import requests

from test_main import config_file, move_dir_content, main_run


@config_file('''
    deploy:
        - python:
            port: 8888
            wsgi: hello:app
    ''')
def test_flask_simple(tmpdir):
    flask_path = join(dirname(abspath(__file__)), 'sample', 'flask')
    move_dir_content(flask_path, str(tmpdir))
    main_run(['depl', 'deploy', 'localhost'])
    assert requests.get("http://localhost:8888/").text == "Hello World!"
