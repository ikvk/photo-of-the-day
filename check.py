from wallpaper import *
import webbrowser


def get_all_urls():
    result = []
    for get_func in WP_SOURCE_MAP.values():
        url = get_func()
        print(get_func, url)
        result.append(url)
    return result


def download_all():
    for get_func in WP_SOURCE_MAP.values():
        print(get_func, download_image_by_url(get_func(), PATH_TO_SAVE_WALLPAPER))


def view_all_in_browser():
    for url in get_all_urls():
        if url:
            webbrowser.open_new_tab(url)


# get_all_urls()
view_all_in_browser()
# download_all()
# print(get_yandex_url())
# print(get_artstation_url())
