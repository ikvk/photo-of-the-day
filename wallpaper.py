import re
import sys
import json
import time
import ctypes
from urllib import request, parse

PATH_TO_SAVE_WALLPAPER = r'C:\Windows\Temp\_wallpaper_of_day.jpg'
SLEEP_AFTER_ERROR_SEC = 2


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
        for script_tag in re.finditer('<script(?P<attrs>.*?)>(?P<code>(.*?))</script>', history_page, re.DOTALL):
            script_tag_dict = script_tag.groupdict()
            if 'restoreData' in script_tag_dict['attrs']:
                script_data = json.loads(script_tag_dict['code'])
                card_id = script_data['contestCards']['results'][0]['id']
                history_item = script_data['entities']['cards'][card_id]['content'][0]['content']
                return 'https://avatars.mds.yandex.net/get-pdb/{group}/{id}/orig'.format(
                    group=history_item['group_id'], id=history_item['avatars_key'])
    return None


def get_nasa_url() -> str or None:
    base_url = 'https://www.nasa.gov'
    ubernodes_url = '{}/api/1/query/ubernodes.json?unType[]=image&routes[]=1446'.format(base_url)
    ubernodes_data = request.urlopen(ubernodes_url)
    if ubernodes_data.code == 200:
        ubernodes = json.loads(ubernodes_data.read().decode())
        node_url = '{}/api/1/record/node/{}.json'.format(base_url, ubernodes['ubernodes'][0]['nid'])
        node_data = request.urlopen(node_url)
        if node_data.code == 200:
            node = json.loads(node_data.read().decode())
            return '{}{}'.format(base_url, node['images'][0]['fullWidthFeature'])
    return None


def get_astropix_url() -> str or None:
    base_url = 'https://apod.nasa.gov/apod/'
    base_data = request.urlopen('{}{}'.format(base_url, 'astropix.html'))
    if base_data.code == 200:
        url_match = re.search(r'<IMG\s+SRC=\"(?P<url>.+?)\"', base_data.read().decode(), re.IGNORECASE)
        if url_match:
            return '{}{}'.format(base_url, url_match.groupdict()['url'])
    return None


def get_geo_url() -> str or None:
    base_url = 'https://www.nationalgeographic.com/photography/photo-of-the-day/_jcr_content/.gallery.json'
    base_data = request.urlopen(base_url)
    if base_data.code == 200:
        geo_data = json.loads(base_data.read().decode())
        return geo_data['items'][0]['image']['uri']
    return None


def get_esa_url() -> str or None:
    base_url = 'http://www.esa.int'
    page1_data = request.urlopen('{}/ESA_Multimedia/Images'.format(base_url))
    if page1_data.code == 200:
        url1_match = re.search(
            r'<a\s+class=\"cta\s+popup\"\s+href=\"(?P<url>.+?)\"',
            page1_data.read().decode(), re.IGNORECASE)
        if url1_match:
            page2_data = request.urlopen('{}{}'.format(base_url, url1_match.groupdict()['url']))
            if page2_data.code == 200:
                url2_match = re.search(
                    r'<meta\s+property=\"og:image\"\s+content=\"(?P<url>.+?)\"',
                    page2_data.read().decode(), re.IGNORECASE)
                if url1_match:
                    return url2_match.groupdict()['url']
    return None


def exit_with_error(error_code: int, error_text: str):
    print(error_text)
    time.sleep(SLEEP_AFTER_ERROR_SEC)
    exit(error_code)


if __name__ == '__main__':
    wp_sources = dict(
        bing=get_bing_url,
        yandex=get_yandex_url,
        nasa=get_nasa_url,
        esa=get_esa_url,
        astropix=get_astropix_url,
        geo=get_geo_url,
    )

    # get source name
    source_name = ''
    if len(sys.argv) > 1 and sys.argv[1] in wp_sources:
        source_name = sys.argv[1]
        print('Source "{}" selected.'.format(source_name))
    else:
        exit_with_error(1, 'Choose wallpaper source name, available: [{}]'.format(', '.join(wp_sources.keys())))
    get_url_function = wp_sources[source_name]
    # get url
    wallpaper_url = get_url_function()
    if wallpaper_url:
        print('Image url received: "{}"'.format(wallpaper_url))
    else:
        exit_with_error(2, 'Failed to retrieve image url for download.')
    # download image
    is_downloaded = download_image_by_url(wallpaper_url, PATH_TO_SAVE_WALLPAPER)
    if is_downloaded:
        print('Image saved to: "{}"'.format(PATH_TO_SAVE_WALLPAPER))
    else:
        exit_with_error(3, 'Failed to downloading wallpaper image.')
    # set wallpaper
    set_wp_result = set_win10_wallpaper(PATH_TO_SAVE_WALLPAPER)
    if set_wp_result == 1:
        print('Wallpaper installed successfully.')
    else:
        exit_with_error(4, 'Failed to set wallpaper: {}'.format(ctypes.WinError()))
