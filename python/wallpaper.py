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


def get_bing_url():
    bing_url = 'https://www.bing.com'
    bing_api_url = '{bing_url}/HPImageArchive.aspx?{params}'.format(
        bing_url=bing_url, params=parse.urlencode(dict(format='js', idx='0', n='1', mkt='ru-RU')))
    api_data = request.urlopen(bing_api_url)
    if api_data.code == 200:
        bing_data = json.loads(api_data.read().decode())
        return '{bing_url}{url}'.format(bing_url=bing_url, url=bing_data['images'][0]['url'])
    return None


def get_yandex_url():
    history_req = request.Request('https://yandex.ru/collections/contest/photo-of-the-day/', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0'})
    api_data = request.urlopen(history_req)
    if api_data.code == 200:
        history_page = api_data.read().decode()
        for script_tag in re.finditer('<script(?P<attrs>.*?)>(?P<code>(.+?))</script>', history_page, re.DOTALL):
            script_tag_dict = script_tag.groupdict()
            if 'restoreData' in script_tag_dict['attrs']:
                script_data = json.loads(script_tag_dict['code'])
                card_id = script_data['di']['ReduxState']['contestCards']['results'][0]['id']
                history_item = script_data['di'] \
                    ['ReduxState']['entities']['cards'][card_id]['content'][0]['content']
                return 'https://avatars.mds.yandex.net/get-pdb/{group}/{id}/orig'.format(
                    group=history_item['group_id'], id=history_item['avatars_key'])
    return None


def get_nasa_url():
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
    return None


def get_geo_url():
    base_url = 'https://www.nationalgeographic.com/photography/photo-of-the-day/_jcr_content/.gallery.json'
    base_data = request.urlopen(base_url)
    if base_data.code == 200:
        geo_data = json.loads(base_data.read().decode())
        size = max(int(i) for i in geo_data['items'][0]['sizes'].keys())
        return geo_data['items'][0]['url'] + geo_data['items'][0]['sizes'][str(size)]
    return None


if __name__ == '__main__':
    wallpaper_sources = dict(
        bing=get_bing_url,
        yandex=get_yandex_url,
        nasa=get_nasa_url,
        geo=get_geo_url,
    )
    source = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in wallpaper_sources else 'yandex'
    get_url_function = wallpaper_sources[source]
    print('Setting "{}" wallpaper...'.format(source))
    wallpaper_url = get_url_function()
    if not wallpaper_url:
        print('Failed to retrieve url for download.')
        time.sleep(2)
        exit()
    print(wallpaper_url)
    is_downloaded = download_image_by_url(wallpaper_url, local_wallpaper_path)
    if is_downloaded:
        print('Image saved to: {}'.format(local_wallpaper_path))
        result = set_wallpaper(local_wallpaper_path)
        print(ctypes.WinError() if result != 1 else 'Wallpaper installed.')
        time.sleep(1)
    else:
        print('An error occurred while downloading wallpaper.')
