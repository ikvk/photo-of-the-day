import re
import sys
import json
import time
import ctypes
import datetime
from urllib import request, parse

WP_SAVE_PATH = 'C:/Windows/Temp/'
WP_FILE_NAME_PREFIX = '_wallpaper_of_day_'  # without extension


def set_win10_wallpaper(local_path: str):
    spi_setdeskwallpaper = 20
    spif_updateinifile = 2  # Writes the new system-wide parameter setting to the user profile.
    return ctypes.windll.user32.SystemParametersInfoW(spi_setdeskwallpaper, 0, local_path, spif_updateinifile)


def identify_image_type(data: bytes) -> str:
    if len(data) > 2 and data[0:2] == b'BM':
        return 'bmp'
    if len(data) > 6 and data[:6] in [b'GIF87a', b'GIF89a']:
        return 'gif'
    if len(data) > 4 and data[0] == 0x89 and data[1:4] == b'PNG':
        return 'png'
    if len(data) > 3 and data[0] == 0xff and data[1] == 0xd8 and data[2] == 0xff:
        return 'jpeg'
    if len(data) > 12 and data[0:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp'
    return 'jpg'


def download_image_by_url(img_url: str, save_path: str, file_name: str) -> str:
    """
    :return: file_name if success else ""
    """
    wb_data = request.urlopen(img_url)
    if wb_data.code == 200:
        try:
            img_bytes = wb_data.read()
            img_name = '{}.{}'.format(file_name, identify_image_type(img_bytes))
            with open(save_path + img_name, 'wb') as f:
                f.write(img_bytes)
            return img_name
        except IOError:
            return ''
    else:
        return ''


def get_artstation_url() -> str or None:
    channels = {  # noqa
        70: 'Abstract',
        69: 'Anatomy',
        71: 'Animals & Wildlife',
        72: 'Anime & Manga',
        101: 'Architectural Concepts',  #
        73: 'Architectural Visualization',
        128: 'Automotive',
        103: 'Board and Card Game Art',
        104: 'Book Illustration',
        105: 'Character Animation',
        74: 'Character Design',
        75: 'Character Modeling',
        77: "Children's Art",
        78: 'Comic Art',
        79: 'Concept Art',  #
        84: 'Cover Art',
        80: 'Creatures & Monsters',
        76: 'Editorial Illustration',
        81: 'Environmental Concept Art & Design',  #
        82: 'Fan Art',
        83: 'Fantasy',
        106: 'Fashion & Costume Design',
        85: 'Game Art',
        107: 'Gameplay & Level Design',
        108: 'Games and Real-Time 3D Environment Art',
        87: 'Graphic Design',
        109: 'Hard Surface',
        86: 'Horror',
        88: 'Illustration',
        89: 'Industrial & Product Design',
        90: 'Lighting',
        91: 'Matte Painting',
        92: 'Mecha',  #
        110: 'Mechanical Design',  #
        111: 'Motion Graphics',
        112: 'Photogrammetry & 3D Scanning',
        93: 'Pixel & Voxel',
        113: 'Portraits',
        94: 'Props',
        114: 'Realism',
        95: 'Science Fiction',  #
        115: 'Scientific Illustration & Visualization',
        116: 'Scripts & Tools',
        117: 'Sketches',
        118: 'Still Life',
        96: 'Storyboards',
        119: 'Stylized',
        120: 'Technical Art',
        97: 'Textures & Materials',
        6212: 'The Art of  HALO Infinite',
        121: 'Toys & Collectibles',
        98: 'Tutorials',
        127: 'Unreal Engine',
        99: 'User Interface',
        100: 'Vehicles',  #
        122: 'VFX for Film, TV & Animation ',
        123: 'VFX for Real-Time & Games',
        124: 'Virtual and Augmented Reality',
        125: 'Visual Development',
        126: 'Weapons',  #
        102: 'Web and App Design',
        6278: 'The Art of  Rainbow6 Extraction',
        6291: "The Art of Marvel's  Guardians of the  Galaxy"
    }
    channel_white_list = [101, 95, 79, 81, 100, 92, 110, 126]
    channel_data_url = 'https://www.artstation.com/api/v2/community/channels/projects.json?' \
                       'channel_id={}&page=1&sorting=trending&dimension=all&per_page=30'
    req_heads = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
    }

    results = []
    for channel_id in channel_white_list:
        channel_data_req = request.Request(channel_data_url.format(channel_id), headers=req_heads)
        channel_data_raw = request.urlopen(channel_data_req)
        if channel_data_raw.code == 200:
            channel_data = json.loads(channel_data_raw.read().decode())
            art_hash = channel_data['data'][0]['url'].split('/')[-1]
            art_data_url = 'https://www.artstation.com/projects/{}.json'.format(art_hash)
            art_data_req = request.Request(art_data_url, headers=req_heads)
            art_data = json.loads(request.urlopen(art_data_req).read().decode())
            art_url = art_data['assets'][0]['image_url']
            pub_date = datetime.datetime.strptime(art_data['published_at'][:10], '%Y-%m-%d').date()
            if pub_date >= datetime.date.today() - datetime.timedelta(days=1):
                return art_url
            else:
                results.append((pub_date, art_url))
    return sorted(results, key=lambda x: x[0])[-1][1] or None


def get_bing_url() -> str or None:
    bing_url = 'https://www.bing.com'
    bing_api_url = '{bing_url}/HPImageArchive.aspx?{params}'.format(
        bing_url=bing_url, params=parse.urlencode(dict(format='js', idx='0', n='1', mkt='ru-RU')))
    api_data = request.urlopen(bing_api_url)
    if api_data.code == 200:
        bing_data = json.loads(api_data.read().decode())
        return '{bing_url}{url}'.format(bing_url=bing_url, url=bing_data['images'][0]['url'])
    return None


def get_35photo_url() -> str or None:
    base_url = 'https://ru.35photo.pro/rating/photo_day/'
    genre_map = {  # noqa
        408: 'Абстракция',
        409: 'Аэрофотосъёмка',
        108: 'Без категории',
        97: 'Гламур',
        101: 'Город/Архитектура',
        114: 'Жанровый портрет',
        507: 'Женский портрет',
        103: 'Животные',
        397: 'Концептуальное',
        102: 'Макро',
        506: 'Мужской портрет',
        104: 'Натюрморт',
        414: 'Ночь',
        98: 'Ню',
        99: 'Пейзаж',
        402: 'Пленка',
        109: 'Подводный мир',
        96: 'Портрет',
        415: 'Постановочная фотография',
        396: 'Семейная фотография',
        105: 'Спорт',
        94: 'Стрит/Репортаж',
        400: 'Черно-Белое',
    }
    genre_white_list = [409, 101, 103, 102, 104, 414, 99, 109, 94]  # no nude
    base_data = request.urlopen(base_url)
    if base_data.code == 200:
        url_match = re.search(r'"https://(?P<url>\S+?)#cat0"', base_data.read().decode())
        if url_match:
            detail_url = 'https://{}#cat0'.format(url_match.groupdict()['url'])
            detail_data = request.urlopen(detail_url)
            if detail_data.code == 200:
                detail_data_str = detail_data.read().decode()
                genre_match = re.search(r':\s+<a href="https://35photo.pro/genre_(?P<genre>\d+)/">', detail_data_str)
                if genre_match:
                    genre = int(genre_match.groupdict()['genre'])
                    if genre not in genre_white_list:
                        return None
                main_pref = r'https://35photo.pro/photos_main/'
                photo_match = re.search(r'"{}(?P<photo>\S+?)"'.format(main_pref), detail_data_str)
                if photo_match:
                    return '{}{}'.format(main_pref, photo_match.groupdict()['photo'])
    return None


def get_nasa_url() -> str or None:
    iotd_url = 'https://www.nasa.gov/image-of-the-day/'
    iotd_data = request.urlopen(iotd_url)
    if iotd_data.code == 200:
        # *в ссылке .jpg, в _headers ('Content-Type', 'image/jpeg'), по факту там есть png, jpg, webp ...
        url_match = re.search(
            r'<img\s+src=\"(?P<url>.+?)\".+?loading=\"lazy\"', iotd_data.read().decode(), re.IGNORECASE)
        if url_match:
            return url_match.groupdict()['url']
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
    base_url = 'https://www.nationalgeographic.co.uk/photo-of-day'
    base_data = request.urlopen(base_url)
    if base_data.code == 200:
        data = base_data.read().decode()
        match = re.search(r'<IMG.+?SRC=\"(?P<url>.+?)\"', data, re.IGNORECASE | re.DOTALL)
        if match:
            return match.groupdict()['url'].split('?')[0]
    return None


def get_esa_url() -> str or None:
    base_url = 'https://www.esa.int'
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
                if url2_match:
                    return url2_match.groupdict()['url']
    return None


def exit_with_error(error_code: int, error_text: str):
    print(error_text)
    py_path = sys.executable or ''  # absolute path of the executable binary for the Python interpreter
    if py_path.endswith('pythonw.exe') or py_path.endswith('pythonw'):
        # no console
        time.sleep(3)
    else:
        # visible console
        pass
    exit(error_code)


WP_SOURCE_MAP = {
    '35photo': get_35photo_url,
    'artstation': get_artstation_url,
    'bing': get_bing_url,
    'nasa': get_nasa_url,
    'esa': get_esa_url,
    'astropix': get_astropix_url,
    'geo': get_geo_url,
}

if __name__ == '__main__':
    # get source name
    source_name = ''
    if len(sys.argv) > 1 and sys.argv[1] in WP_SOURCE_MAP:
        source_name = sys.argv[1]
        print('Source "{}" selected.'.format(source_name))
    else:
        exit_with_error(1, 'Choose wallpaper source name, available: [{}]'.format(', '.join(WP_SOURCE_MAP.keys())))
    get_url_function = WP_SOURCE_MAP[source_name]
    # get url
    wallpaper_url = get_url_function()
    if wallpaper_url:
        print('Image url received: "{}"'.format(wallpaper_url))
    else:
        exit_with_error(2, 'Failed to retrieve image url for download.')
    # download image
    wp_file_name = download_image_by_url(wallpaper_url, WP_SAVE_PATH, WP_FILE_NAME_PREFIX + source_name)
    wp_full_path = ''
    if wp_file_name:
        wp_full_path = WP_SAVE_PATH + wp_file_name
        print('Image saved to: "{}"'.format(wp_full_path))
    else:
        exit_with_error(3, 'Failed to downloading wallpaper image.')
    # set wallpaper
    set_wp_result = set_win10_wallpaper(wp_full_path)
    if set_wp_result == 1:
        print('Wallpaper installed successfully.')
    else:
        exit_with_error(4, 'Failed to set wallpaper: {}'.format(ctypes.WinError()))
