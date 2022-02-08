import re
import sys
import json
import time
import ctypes
import datetime
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
    channel_white_list = [95, 101, 79, 81, 100, 92, 110, 126]
    channel_data_url = 'https://www.artstation.com/api/v2/community/channels/projects.json?' \
                       'channel_id={}&page=1&sorting=trending&dimension=all&per_page=30'
    req_heads = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0", }
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
                if url1_match:
                    return url2_match.groupdict()['url']
    return None


def exit_with_error(error_code: int, error_text: str):
    print(error_text)
    time.sleep(SLEEP_AFTER_ERROR_SEC)
    exit(error_code)


if __name__ == '__main__':
    wp_sources = {
        'artstation': get_artstation_url,
        'bing': get_bing_url,
        'nasa': get_nasa_url,
        'esa': get_esa_url,
        'astropix': get_astropix_url,
        'geo': get_geo_url,
    }

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
