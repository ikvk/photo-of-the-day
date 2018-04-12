import re
import sys
import json
import time
import ctypes
from urllib import request, parse

local_wallpaper_path = r'C:\Windows\Temp\wallpaper_of_day.jpg'


def set_wallpaper(local_path):
    spi = 20
    spif = 2
    return ctypes.windll.user32.SystemParametersInfoA(spi, 0, local_path.encode("us-ascii"), spif)


def download_image_by_url(img_url, local_path):
    result = True
    wb_data = request.urlopen(img_url)
    if wb_data.code == 200:
        with open(local_path, 'wb') as f:
            f.write(wb_data.read())
            result = True
    return result


def download_bing_image_of_day(local_path):
    result = None
    bing_url = 'https://www.bing.com'
    bing_api_url = '{bing_url}/HPImageArchive.aspx?{params}'.format(
        bing_url=bing_url, params=parse.urlencode(dict(format='js', idx='0', n='1', mkt='ru-RU')))
    api_data = request.urlopen(bing_api_url)
    if api_data.code == 200:
        bing_data = json.loads(api_data.read().decode())
        photo_url = '{bing_url}{url}'.format(bing_url=bing_url, url=bing_data['images'][0]['url'])
        result = photo_url if download_image_by_url(photo_url, local_path) else None
    return result


def download_yandex_image_of_day(local_path):
    result = False
    history_req = request.Request('https://yandex.ru/collections/contest/photo-of-the-day/', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'})
    api_data = request.urlopen(history_req)
    if api_data.code == 200:
        history_page = api_data.read().decode()
        for script_tag in re.finditer('<script(?P<attrs>.*?)>(?P<code>(.+?))</script>', history_page, re.DOTALL):
            script_tag_dict = script_tag.groupdict()
            if 'restoreData' in script_tag_dict['attrs']:
                script_data = json.loads(script_tag_dict['code'])
                history_item = script_data['di']['photosDaily']['results'][0]['content'][0]['content']
                photo_url = 'https://avatars.mds.yandex.net/get-pdb/{group}/{id}/orig'.format(
                    group=history_item['group_id'], id=history_item['avatars_key'])
                result = photo_url if download_image_by_url(photo_url, local_path) else None
    return result


if __name__ == '__main__':
    # wallpaper source
    download_function = download_bing_image_of_day
    if len(sys.argv) > 1:
        image_src = sys.argv[1]
        if image_src == 'bing':
            download_function = download_bing_image_of_day
        elif image_src == 'yandex':
            download_function = download_yandex_image_of_day
    print('Setting wallpaper...')
    downloaded = download_function(local_wallpaper_path)
    if downloaded:
        print('Wallpaper successfully downloaded:\n{}'.format(downloaded))
        result = set_wallpaper(local_wallpaper_path)
        if result != 1:
            print(ctypes.WinError())
        time.sleep(1)
    else:
        print('An error occurred while downloading wallpaper.')
