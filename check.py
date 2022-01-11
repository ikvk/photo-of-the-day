from wallpaper import *

all_get = [
    get_bing_url,
    get_35photo_url,
    get_nasa_url,
    get_astropix_url,
    get_geo_url,
    get_esa_url,
]


def get_all_urls():
    for get_func in all_get:
        print(get_func, get_func())


def download_all():
    for get_func in all_get:
        print(get_func, download_image_by_url(get_func(), PATH_TO_SAVE_WALLPAPER))


get_all_urls()
# download_all()
# print(get_yandex_url())
# print(get_geo_url())
