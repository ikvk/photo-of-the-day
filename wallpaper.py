import re
import sys
import json
import time
import ctypes
from urllib import request, parse

local_wallpaper_path = r'C:\Windows\Temp\_wallpaper_of_day.jpg'


def set_win10_wallpaper(local_path: str):
    spi_setdeskwallpaper = 20
    spif_updateinifile = 2  # Writes the new system-wide parameter setting to the user profile.
    return ctypes.windll.user32.SystemParametersInfoW(spi_setdeskwallpaper, 0, local_path, spif_updateinifile)


def download_image_by_url(img_url: str, local_path: str) -> bool:
    wb_data = request.urlopen(img_url)
    if wb_data.code == 200:
        try:
            with open(local_path, 'wb') as f:
                f.write(wb_data.read())
        except IOError:
            return False
        return True
    else:
        return False


def get_bing_url() -> str or None:
    bing_url = 'https://www.bing.com'
    bing_api_url = '{bing_url}/HPImageArchive.aspx?{params}'.format(
        bing_url=bing_url, params=parse.urlencode(dict(format='js', idx='0', n='1', mkt='ru-RU')))
    api_data = request.urlopen(bing_api_url)
    if api_data.code == 200:
        bing_data = json.loads(api_data.read().decode())
        return '{bing_url}{url}'.format(bing_url=bing_url, url=bing_data['images'][0]['url'])
    return None


def get_yandex_url() -> str or None:
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
                history_item = script_data['di']['ReduxState']['entities']['cards'][card_id]['content'][0]['content']
                return 'https://avatars.mds.yandex.net/get-pdb/{group}/{id}/orig'.format(
                    group=history_item['group_id'], id=history_item['avatars_key'])
    return None


def get_nasa_url() -> str or None:
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


def get_astropix_url() -> str or None:
    base_url = 'https://apod.nasa.gov/apod/astropix.html'
    base_data = request.urlopen(base_url)
    if base_data.code == 200:
        url_match = re.search(r'<IMG\s+SRC=\"(?P<url>.+?)\"', base_data.read().decode(), re.IGNORECASE)
        if url_match:
            return 'https://apod.nasa.gov/apod/{}'.format(url_match.groupdict()['url'])
    return None


def get_geo_url() -> str or None:
    base_url = 'https://www.nationalgeographic.com/photography/photo-of-the-day/_jcr_content/.gallery.json'
    base_data = request.urlopen(base_url)
    if base_data.code == 200:
        geo_data = json.loads(base_data.read().decode())
        return geo_data['items'][0]['image']['uri']
    return None


if __name__ == '__main__':
    wp_sources = dict(
        bing=get_bing_url,
        yandex=get_yandex_url,
        nasa=get_nasa_url,
        astropix=get_astropix_url,
        geo=get_geo_url,
    )
    error_sleep_sec = 2
    # get source name
    source_name = ''
    if len(sys.argv) > 1 and sys.argv[1] in wp_sources:
        source_name = sys.argv[1]
        print('Source "{}" selected.'.format(source_name))
    else:
        print('Choose wallpaper source name, available: [{}]'.format(', '.join(wp_sources.keys())))
        time.sleep(error_sleep_sec)
        exit(1)
    get_url_function = wp_sources[source_name]
    # get url
    wallpaper_url = get_url_function()
    if wallpaper_url:
        print('Image url received: "{}"'.format(wallpaper_url))
    else:
        print('Failed to retrieve image url for download.')
        time.sleep(error_sleep_sec)
        exit(2)
    # download image
    is_downloaded = download_image_by_url(wallpaper_url, local_wallpaper_path)
    if is_downloaded:
        print('Image saved to: "{}"'.format(local_wallpaper_path))
    else:
        print('Failed to downloading wallpaper image.')
        time.sleep(error_sleep_sec)
        exit(3)
    # set wallpaper
    set_wp_result = set_win10_wallpaper(local_wallpaper_path)
    if set_wp_result == 1:
        print('Wallpaper installed successfully.')
    else:
        print('Failed to set wallpaper: {}'.format(ctypes.WinError()))
        time.sleep(error_sleep_sec)
        exit(4)
