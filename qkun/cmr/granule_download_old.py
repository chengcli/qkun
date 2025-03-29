import os
from urllib import request, error
from http.cookiejar import CookieJar

class GranuleDownloader:
    BASE_URL = "https://urs.earthdata.nasa.gov"

    def __init__(self, username: str, password: str, save_dir: str = "."):
        self.username = username
        self.password = password
        self.save_dir = os.path.abspath(save_dir)

        self.cookie_jar = CookieJar()
        self.password_manager = request.HTTPPasswordMgrWithDefaultRealm()
        self.password_manager.add_password(None, self.BASE_URL, self.username, self.password)

        self.opener = request.build_opener(
            request.HTTPBasicAuthHandler(self.password_manager),
            request.HTTPCookieProcessor(self.cookie_jar)
        )
        request.install_opener(self.opener)

    def download(self, url: str):
        file_name = url.split("/")[-1]
        save_path = os.path.join(self.save_dir, file_name)

        try:
            print(f"Connecting to: {url}")
            initial_request = request.Request(url)
            initial_request.add_header('Cookie', str(self.cookie_jar))

            # Step 1: Get redirected URL
            initial_response = request.urlopen(initial_request)
            redirect_url = initial_response.geturl() + "&app_type=401"

            # Step 2: Authenticated request to redirect
            final_request = request.Request(redirect_url)
            final_response = request.urlopen(final_request)

            # Step 3: Read and write to file
            with open(save_path, "wb") as f:
                data = final_response.read()
                f.write(data)

            print(f"✅ {file_name} has been downloaded to: {save_path}")

        except error.HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
        except error.URLError as e:
            print(f"❌ URL Error: {e.reason}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
