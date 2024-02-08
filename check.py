from wallpaper import *
import webbrowser


def get_all_urls():
    result = []
    for source_name, get_func in WP_SOURCE_MAP.items():
        print(source_name, get_func)
        url = get_func()
        print(url)
        result.append(url)
        print()
    return result


def download_all():
    for source_name, get_func in WP_SOURCE_MAP.items():
        print(get_func)
        url = get_func()
        fn = download_image_by_url(url, WP_SAVE_PATH, WP_FILE_NAME_PREFIX + source_name)
        print(url)
        print(fn)
        print()


def view_all_in_browser():
    for url in get_all_urls():
        if url:
            webbrowser.open_new_tab(url)


# view_all_in_browser()
# get_all_urls()
# download_all()
# print(get_yandex_url())
# print(download_image_by_url(get_artstation_url(), PATH_TO_SAVE_WALLPAPER))  # 403

# with open('C:/kvk/Загрузки/1.webp', 'rb') as f:
#     print(identify_image_type(f.read()))
