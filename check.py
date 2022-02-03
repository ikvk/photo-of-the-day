from wallpaper import *
import webbrowser

get_url_fn_set = {
    get_bing_url,
    get_35photo_url,
    get_nasa_url,
    get_astropix_url,
    get_geo_url,
    get_esa_url,
}


def get_all_urls():
    result = []
    for get_func in get_url_fn_set:
        url = get_func()
        print(get_func, url)
        result.append(url)
    return result


def download_all():
    for get_func in get_url_fn_set:
        print(get_func, download_image_by_url(get_func(), PATH_TO_SAVE_WALLPAPER))


def view_all_in_browser():
    for url in get_all_urls():
        if url:
            webbrowser.open(url, new=2)


# get_all_urls()
view_all_in_browser()
# download_all()
# print(get_yandex_url())
# print(get_geo_url())
