import re
import sys
import json
import time
import ctypes
from urllib import request, parse

local_wallpaper_path = r'C:\Windows\Temp\wallpaper_of_day.jpg'


def set_wallpaper(local_path):
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 2  # Writes the new system-wide parameter setting to the user profile.
    return ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, local_path, SPIF_UPDATEINIFILE)


def download_image_by_url(img_url, local_path):
    result = True
    wb_data = request.urlopen(img_url)
    if wb_data.code == 200:
        with open(local_path, 'wb') as f:
            f.write(wb_data.read())
            result = True
    return result


def get_image_of_day_bing():
    result = None
    bing_url = 'https://www.bing.com'
    bing_api_url = '{bing_url}/HPImageArchive.aspx?{params}'.format(
        bing_url=bing_url, params=parse.urlencode(dict(format='js', idx='0', n='1', mkt='ru-RU')))
    api_data = request.urlopen(bing_api_url)
    if api_data.code == 200:
        bing_data = json.loads(api_data.read().decode())
        return '{bing_url}{url}'.format(bing_url=bing_url, url=bing_data['images'][0]['url'])
    return result


def get_image_of_day_yandex():
    result = None
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
                return 'https://avatars.mds.yandex.net/get-pdb/{group}/{id}/orig'.format(
                    group=history_item['group_id'], id=history_item['avatars_key'])
    return result


def get_image_of_day_nasa():
    result = None
    ubernodes_url = 'https://www.nasa.gov/api/1/query/ubernodes.json?unType[]=image&routes[]=1446'
    ubernodes_data = request.urlopen(ubernodes_url)
    if ubernodes_data.code == 200:
        ubernodes = json.loads(ubernodes_data.read().decode())
        nid = ubernodes['ubernodes'][0]['nid']
        node_url = 'https://www.nasa.gov/api/1/record/node/{nid}.json'.format(nid=nid)
        node_data = request.urlopen(node_url)
        if node_data.code == 200:
            node = json.loads(node_data.read().decode())
            return 'https://www.nasa.gov/sites/default/files/thumbnails/image/{node}'.format(
                node=node['images'][0]['filename'])
    return result


if __name__ == '__main__':
    # wallpaper source
    get_image_of_day_function = get_image_of_day_yandex
    if len(sys.argv) > 1:
        image_src = sys.argv[1]
        if image_src == 'bing':
            get_image_of_day_function = get_image_of_day_bing
        elif image_src == 'yandex':
            get_image_of_day_function = get_image_of_day_yandex
        elif image_src == 'nasa':
            get_image_of_day_function = get_image_of_day_nasa
    print('Setting wallpaper...')
    photo_url = get_image_of_day_function()
    print(photo_url)
    downloaded = download_image_by_url(photo_url, local_wallpaper_path)
    if downloaded:
        print('Image saved to: {}'.format(local_wallpaper_path))
        result = set_wallpaper(local_wallpaper_path)
        print(ctypes.WinError() if result != 1 else 'Wallpaper installed.')
        time.sleep(1)
    else:
        print('An error occurred while downloading wallpaper.')
