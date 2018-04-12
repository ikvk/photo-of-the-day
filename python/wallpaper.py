import json
import time
import ctypes
from urllib import request, parse

local_wallpaper_path = r'C:\Windows\Temp\bing_wp.jpg'


def set_wallpaper(local_path):
    spi = 20
    spif = 2
    return ctypes.windll.user32.SystemParametersInfoA(spi, 0, local_path.encode("us-ascii"), spif)


def download_bing_image_of_day(local_path):
    result = None
    bing_url = 'https://www.bing.com'
    bing_api_url = '{bing_url}/HPImageArchive.aspx?{params}'.format(
        bing_url=bing_url, params=parse.urlencode(dict(format='js', idx='0', n='1', mkt='ru-RU')))
    # get url
    api_data = request.urlopen(bing_api_url)
    if api_data.code == 200:
        bing_data = json.loads(api_data.read().decode())
        wp_url = '{bing_url}{url}'.format(bing_url=bing_url, url=bing_data['images'][0]['url'])
        # download wallpaper
        wb_data = request.urlopen(wp_url)
        if wb_data.code == 200:
            with open(local_path, 'wb') as f:
                f.write(wb_data.read())
                result = wp_url
    return result


if __name__ == '__main__':
    print('Setting wallpaper...')
    downloaded = download_bing_image_of_day(local_wallpaper_path)
    if downloaded:
        print('Wallpaper successfully downloaded:\n{}'.format(downloaded))
        set_wallpaper(local_wallpaper_path)
        time.sleep(1)
    else:
        print('An error occurred while downloading wallpaper.')
