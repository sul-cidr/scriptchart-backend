import urllib
from io import BytesIO
from zipfile import ZipFile

import requests
from PIL import Image, ImageFile


def get_sizes(image_uri):
    """Return a tuple of size in bytes and image dimensions
    (width and height, or None if not known) of image_uri by downloading chunks
    of image_uri until it can be recognized as a PIL image"""
    try:
        file = urllib.request.urlopen(image_uri)
        size = file.headers.get("content-length")
        if size:
            size = int(size)
        image_parser = ImageFile.Parser()
        while True:
            data = file.read(1024)
            if not data:
                break
            image_parser.feed(data)
            if image_parser.image:
                return size, image_parser.image.size
                break
        file.close()
        return size, (None, None)
    except (urllib.request.HTTPError, urllib.error.URLError):
        return None, (None, None)


def create_letter_zip(coordinates):
    """Return an in memory zip file that contains the letter bounding boxes
    images expressed in coordinates"""
    in_memory = BytesIO()
    zip_file = ZipFile(in_memory, 'w')
    last_url = ""
    for coordinate in coordinates:
        if last_url != coordinate.page.url:
            url = requests.get(coordinate.page.url, verify=False)
            image = Image.open(BytesIO(url.content))
            last_url = coordinate.page.url
        x, w = coordinate.left, coordinate.width
        y, h = coordinate.top, coordinate.height
        cid, letter = coordinate.id, coordinate.letter
        page_name = (f"{coordinate.page.manuscript.shelfmark}_"
                     f"{coordinate.page.number}")
        image_name = f"{page_name}_{letter}_{x}_{y}_{w}_{h}.png"
        image_patch = BytesIO()
        image_crop = image.crop([x, y, x + w, y + h])
        image_crop.save(image_patch, format='PNG')
        zip_file.writestr(image_name, image_patch.getvalue())
    in_memory.seek(0)
    zip_file.close()
    return in_memory
