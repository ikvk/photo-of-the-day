photo-of-the-day
================

Downloads photo of day from internet source collection and sets it as wallpaper on windows 10.

This is python 3 script without dependencies.

Available sources:
------------------
- **Bing** - https://www.bing.com/
- **Yandex** - https://yandex.ru/collections/contest/photo-of-the-day/
- **NASA IOTD** - https://www.nasa.gov/multimedia/imagegallery/iotd.html
- **NASA APOD** - https://apod.nasa.gov/apod/astropix.html
- **National geographic** - https://www.nationalgeographic.com/photography/photo-of-the-day/?source=sitenavpod
- **ESA** - http://www.esa.int/ESA_Multimedia/Images

Usage:
------

::

    pythonw wallpaper.py yandex
    pythonw wallpaper.py bing
    pythonw wallpaper.py nasa
    pythonw wallpaper.py astropix
    pythonw wallpaper.py geo
    pythonw wallpaper.py esa

Automate:
---------

Good way to run script periodically on windows: using task scheduler:

#. Start scheduler: press WinKey+R -> "control schedtasks"
#. Create task for run script
