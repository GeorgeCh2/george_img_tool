# myimg
A powerful image util.

It supports **HEIF, Webp, JPEG, and PNG** images, the main functions include **resizing 、format conversion, reading image information, and deleting image GPS information**.  
It's simple and easy to use.

## Background
A Python util for image process。

## Support image type
* jpeg
* png
* webp
* heic

## depends
* [pillow](https://pillow.readthedocs.io/en/stable/)
* [pyheif](https://pypi.org/project/pyheif/)
* [pyexif](https://pypi.org/project/pyexif/)
* [pyheif_pillow_opener](https://pypi.org/project/pyheif-pillow-opener/)

### Installation
You can install it from *Pypi*:  
`pip install pillow pyheif_pillow_opener piexif pyexif`

## How to use
### 1. get Image info  
`python imgutil.py -i input.jpg -exifinfo`  
The information of 'sample.JPG':
```
width|1600
height|1200
DateTimeOriginal|2019:05:03 15:21:53
orientation|1
latiR|North
lati|22 deg 22' 18.35" N
longR|East
long|113 deg 59' 20.15" E
altiR|Above Sea Level
alti|4.9 m Above Sea Level
```
### 2. remove gpsinfo  
`python imgutil.py -i input.jpg -rmgps`  
The information of 'sample.JPG' after removing GPS info:
```
width|1600
height|1200
DateTimeOriginal|2019:05:03 15:21:53
orientation|1
```
The GPS info is removed.

### 3. resize image  
``` python imgutil.py -i input.jpg -quality 85 -resize "{'out1.jpg':'1600x1200', 'out2.jpg':"1280x720"}" ```

### 4. convert  
`python imgutil.py -i sample1.heic -quality 85 -o out.jpg`
