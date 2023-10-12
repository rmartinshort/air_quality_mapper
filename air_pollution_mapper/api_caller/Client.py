import requests
from PIL import Image
import io


class Client(object):
    DEFAULT_BASE_URL = "https://airquality.googleapis.com"

    def __init__(self, key):
        self.session = requests.Session()
        self.key = key

    def _request_post(self, url, params):
        request_url = self.compose_url(url)
        request_header = self.compose_header()
        request_body = params

        response = self.session.post(
            request_url,
            headers=request_header,
            json=request_body,
        )

        response_body = self.get_body(response)
        page = 1
        final_response = {"page_{}".format(page): response_body}
        # fetch all the pages if needed
        while "nextPageToken" in response_body:
            # call again with the next page's token
            request_body.update({"pageToken": response_body["nextPageToken"]})
            response = self.session.post(
                request_url,
                headers=request_header,
                json=request_body,
            )
            response_body = self.get_body(response)
            page += 1
            final_response["page_{}".format(page)] = response_body

        return final_response

    def _request_get(self, url):
        request_url = self.compose_url(url)
        response = self.session.get(request_url)

        # for images coming from the heatmap tiles service
        return self.get_image(response)

    def compose_url(self, path):
        return self.DEFAULT_BASE_URL + path + "?" + "key=" + self.key

    @staticmethod
    def get_image(response):
        if response.status_code == 200:
            image_content = response.content
            image = Image.open(io.BytesIO(image_content))
            return image
        else:
            print("GET request for image returned an error")
            return None

    @staticmethod
    def get_body(response):
        body = response.json()

        if "error" in body:
            return body["error"]

        return body

    @staticmethod
    def compose_header():
        return {
            "Content-Type": "application/json",
        }
