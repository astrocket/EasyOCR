from locust import HttpUser, TaskSet, task, between
import random, uuid, time, io, requests, urllib, os

INPUT_IMAGE = [
    'https://raw.githubusercontent.com/Wook-2/EasyOCR/master/static/images/test_ch.png',
    'https://raw.githubusercontent.com/Wook-2/EasyOCR/master/static/images/test_en.png',
    'https://raw.githubusercontent.com/Wook-2/EasyOCR/master/static/images/test_ja.jpg',
    'https://raw.githubusercontent.com/Wook-2/EasyOCR/master/static/images/test_kor.png',
    'https://raw.githubusercontent.com/Wook-2/EasyOCR/master/static/images/test_latin.jpg',
    'https://raw.githubusercontent.com/Wook-2/EasyOCR/master/static/images/test_thai.jpeg'
]

LANGUAGE = ['ko', 'ja', 'th', 'ch_tra', 'ch_sim', 'af']
def getFilenameFromURL(url):
    parsedUrl = urllib.parse.urlparse(url)
    return os.path.basename(parsedUrl.path)

def fileopen(image):
    fetched = requests.get(image)
    f_image = (
        getFilenameFromURL(image),
        io.BytesIO(fetched.content),
        fetched.headers.get("Content-Type", "image/*"),
    )
    return f_image

class UserBehavior(TaskSet):

    @task(1)
    def upload_file(self):
        # req_id = str(uuid.uuid4())
        # color_image = random.choice(COLOR_IMAGES)
        # base_image = random.choice(BASE_IMAGES)

        img = random.choice(INPUT_IMAGE)
        lang = random.choice(LANGUAGE)

        img_payload = fileopen(img)
        # color_source_payload = fileopen(color_image)
        # base_payload = fileopen(base_image)

        start = time.time()
        response = self.client.post(
            "/", 
            files={
                'file': img_payload
            },
            data={
                'lang': lang
            }
        )
        duration = time.time() - start

        print(
                (
                    "out",
                    duration,
                    response.status_code,
                    len(response.content),
                )
            )

TARGET_RPS = 0.3

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]

    def wait_time(self):
        target_wait = between(0, 2 / TARGET_RPS)(self)  
        print(("wait", target_wait))
        return target_wait