# myimg
A powerful img util, use pillow + pyheif + piexif

## Installation
You can install from *Pypi*:
`pip install pillow pyheif_pillow_opener piexif pyexif`

## How to use
1. get Image info  
`python imgutil.py -i input.jpg -exifinfo`
2. remove gpsinfo  
`python imgutil.py -i input.jpg -rmgps`
3. resize image  
`python imgutil.py -i input.jpg -quality 85 -resize "{'out1.jpg':'1600x1200', 'out2.jpg':"1280x720"}"`
