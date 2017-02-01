# GiPyF - Library to work with GIF files in Python
## What is it?
This lib was created for .GIF parsing. Now there's only three functions:
* Parsing of gif's binary data and getting all headers and packed images in binary
* Unpacking LZW compressed images
* Saving frames to PNG format

It's prepared and tested on Python 3.5

## How to install?
    git clone https://github.com/pyatka/gipyf.git GiPyF
    cd GiPyF
    python setup.py install
    
## How to use?
    from gipyf.gipyf import GiPyF

    gif = GiPyF()
    gif.parse("<path to gif>")
    gif.save_frames()
