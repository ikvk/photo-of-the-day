image-of-the-day
================

Downloads image of day from collection of internet sources and set it as wallpaper on windows 10.

This is python 3 script without dependencies.

Available sources:
------------------
- **Bing** - https://www.bing.com/
- **Yandex** - https://yandex.ru/collections/contest/photo-of-the-day/
- **NASA** - https://www.nasa.gov/multimedia/imagegallery/iotd.html
- **National geographic** - https://www.nationalgeographic.com/photography/photo-of-the-day/?source=sitenavpod

Usage:
------

::

    pythonw wallpaper.py yandex
    pythonw wallpaper.py bing
    pythonw wallpaper.py nasa
    pythonw wallpaper.py geo

Automate:
---------

Good way to run script periodically on windows: using task scheduler:

#. Start scheduler: press WinKey+R -> "control schedtasks"
#. Create task for run script
