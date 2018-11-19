
import requests


def test_gallery_selection():
    test_json = {'filename': 'non_existing_file.txt'}
    res = requests.post('http://127.0.0.1:5001/gallery/selection', json=test_json)
    print(res.status_code, res.text)
    assert res.status_code == 200
    assert res.text == "OK"


def run_tests():
    test_gallery_selection()


if __name__ == "__main__":
    run_tests()
