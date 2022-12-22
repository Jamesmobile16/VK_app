import requests
import json
import datetime
from pprint import pprint

class YaUploader:
    host = 'https://cloud-api.yandex.net/'

    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {'Content-Type': 'application/json', 'Authorization': f'OAuth {self.token}'}

    def create_folder(self):
        uri = 'v1/disk/resources/'
        url = self.host + uri
        params = {'path': '/vk_photos'}
        response = requests.put(url, headers=self.get_headers(), params=params)
        if response.status_code == 201:
          print(f"Папка {params['path']} успешно создана\nstatus_code: {response.status_code}")
        else:
          print(f"Папка 'vk_photos' уже существует\n status_code: {response.status_code}")

    def upload_from_VK(self, file_url, file_name):
        uri = 'v1/disk/resources/upload/'
        url = self.host + uri
        params = {'path': f'/vk_photos/{file_name}', 'url': file_url}
        response = requests.post(url, headers=self.get_headers(), params=params)
        if response.status_code == 202:
          print(f'Файл успешно загружен\nstatus_code: {response.status_code}')
        else:
          print(response.status_code)


class VK:

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version}

    def get_photos(self, self_id):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self_id, 'album_id': 'profile', 'extended': '1', 'photo_sizes': '0'}
        response = requests.get(url, params={**self.params, **params}).json()
        photo_list = response['response']['items']
        photo_to_upload = []
        for photo_info in photo_list:
            for dimension in photo_info['sizes']:
                b = {}
                b.update(dimension)
                if dimension['height'] > b['height']:
                    b.update(dimension)
                else:
                    pass
                b.update(photo_info['likes'])
                b['date'] = photo_info['date']
            photo_to_upload.append(b)
        return photo_to_upload

    def upload_to_YandexDisk(self, vk_self_id, yandex_token, quantity=5):
        ya = YaUploader(yandex_token)
        self_id = vk_self_id
        photos_list = self.get_photos(self_id)
        ya.create_folder()
        output_info = []
        likes_counter = []
        if quantity <= len(photos_list):
            for photo_number in range(quantity):
                photo = photos_list[photo_number]
                # print(photo)
                file_url = photo['url']
                if photo['count'] not in likes_counter:
                  file_name = f"likes_{photo['count']}"
                  likes_counter.append(photo['count'])
                else:
                    date_value = datetime.date.fromtimestamp(photo['date'])
                    file_name = f"likes_{photo['count']}_date_{date_value}"
                ya.upload_from_VK(file_url, file_name)
                photo_info = {}
                photo_info['file_name'] = file_name
                photo_info['size'] = photo['type']
                output_info.append(photo_info)
        else:
          print(f'Превышено количество запросов: {quantity} из {len(photos_list)}')
        print(f"Файлов загружено: {quantity}")
        print(json.dumps(output_info, indent=2, sort_keys=True))


vk_finder = VK('VK_api_personal_token...', 'vk_self_id...')

vk_finder.upload_to_YandexDisk('vk_self_id...', 'yandex_token', 'photos_quantity(int)(optional)')

