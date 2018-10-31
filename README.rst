windows-wallpaper
=================

Utility for download image of day from internet and set it as windows wallpaper.

You can use python 3 script without dependencies or .exe files, built by `pyinstaller <http://www.pyinstaller.org/>`_.

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

Good way to run script periodically on windows: using task scheduler:

#. Start scheduler: press WinKey+R -> control schedtasks
#. Create task for run any script: wallpaper.py or wallpaper.exe
