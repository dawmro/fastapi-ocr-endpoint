import shutil
import time
import io
from fastapi.testclient import TestClient
from app.main import app, BASE_DIR, UPLOAD_DIR
from PIL import Image, ImageChops


client = TestClient(app)

def test_get_home():
    response = client.get("/")
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']


def test_invalid_file_upload_error():
    response = client.post("/")
    assert response.status_code == 422
    assert 'application/json' in response.headers['content-type']


def test_img_echo_upload():
    img_saved_path = BASE_DIR / "images"

    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/img-echo/", files={"file": open(path, 'rb')})
        if img is None:
            assert response.status_code == 400
        else:
            # valid image returned
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            # compare sent and received image
            difference = ImageChops.difference(img, echo_img).getbbox()
            assert difference is None

    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)
