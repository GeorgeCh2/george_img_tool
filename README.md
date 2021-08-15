# myimg
A powerful img util

## Support img type
* jpeg
* png
* webp
* heic

## depends
* [pillow](https://pillow.readthedocs.io/en/stable/)
* [pyheif](https://pypi.org/project/pyheif/)
* [pyexif](https://pypi.org/project/pyexif/)
* [pyheif_pillow_opener](https://pypi.org/project/pyheif-pillow-opener/)

## Installation
You can install from *Pypi*:  
`pip install pillow pyheif_pillow_opener piexif pyexif`

## How to use
1. get Image info  
`python imgutil.py -i input.jpg -exifinfo`
2. remove gpsinfo  
`python imgutil.py -i input.jpg -rmgps`
3. resize image  
``` python imgutil.py -i input.jpg -quality 85 -resize "{'out1.jpg':'1600x1200', 'out2.jpg':"1280x720"}" ```
4. convert
`python imgutil.py -i input.heif -quality 85 -o out.jpg`
