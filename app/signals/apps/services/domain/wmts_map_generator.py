# SPDX-License-Identifier: MPL-2.0
# Copyright (C) 2020 - 2021 Vereniging van Nederlandse Gemeenten, Gemeente Amsterdam
import io
import urllib.request
import logging
from math import asinh, modf, pi, radians, tan

from PIL import Image

logger = logging.getLogger(__name__)

TILE_SIZE = 256

class WMTSMapGenerator:
    """
    Map generator for EPSG:28992 (Rijksdriehoek) coordinate system.
    Based on https://www.geonovum.nl/uploads/documents/nederlandse_richtlijn_tiling_-_versie_1.1.pdf
    """
    
    # RD coordinates bounds
    MIN_X = -285401.92
    MAX_X = 595401.92
    MIN_Y = 22598.08
    MAX_Y = 903401.92
    
    @staticmethod
    def rd2tile(x, y, zoom):
        """Convert RD coordinates to tile numbers"""
        # Resolution (meters per pixel) for each zoom level
        resolution = 3440.640 / 2**zoom
        
        # Calculate tile numbers
        xtile = int((x - WMTSMapGenerator.MIN_X) / (resolution * TILE_SIZE))
        ytile = int((WMTSMapGenerator.MAX_Y - y) / (resolution * TILE_SIZE))
        
        return xtile, ytile

    @staticmethod
    def rd2pixel(x, y, zoom):
        """Convert RD coordinates to pixel position within a tile"""
        resolution = 3440.640 / 2**zoom
        
        xtile, ytile = WMTSMapGenerator.rd2tile(x, y, zoom)
        
        # Calculate pixel positions within the tile
        xpixel = int(((x - WMTSMapGenerator.MIN_X) / resolution) % TILE_SIZE)
        ypixel = int(((WMTSMapGenerator.MAX_Y - y) / resolution) % TILE_SIZE)
        
        return xpixel, ypixel

    @staticmethod
    def calc_tiles_in_pixels(input, pixels):
        """Calculate number of tiles needed to cover desired pixels"""
        net_pixels = max(0, pixels - input)
        fract_part, int_part = modf(net_pixels / TILE_SIZE)
        return int(int_part) if fract_part == 0 else int(int_part + 1)

    @staticmethod
    def load_image(url_template, zoom, x, y, left, top, right, bottom):
        """Load and combine multiple tiles into single image"""
        xtiles = left + right + 1
        ytiles = top + bottom + 1

        img = Image.new("RGBA", (xtiles*TILE_SIZE, ytiles*TILE_SIZE), 0)
        
        try:
            for i in range(-left, right + 1, 1):
                for j in range(-top, bottom + 1, 1):
                    url = url_template.format(z=zoom, x=x+i, y=y+j)
                    logger.debug(f"Fetching tile from URL: {url}")
                    
                    try:
                        with urllib.request.urlopen(url) as response:
                            offset = ((i+left) * TILE_SIZE, (j+top) * TILE_SIZE)
                            tile_img = Image.open(io.BytesIO(response.read()))
                            img.paste(tile_img, offset)
                    except Exception as e:
                        logger.warning(f"Failed to fetch tile: {url}, error: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error loading tiles: {str(e)}")
            pass  # use empty image in case of errors

        return img

    @staticmethod
    def make_map(url_template, x, y, zoom, img_size):
        """
        Generate map for given RD coordinates
        
        Args:
            url_template: WMTS URL template with {z}, {x}, {y} placeholders
            x: RD X coordinate
            y: RD Y coordinate
            zoom: zoom level
            img_size: desired output image size [width, height]
        """
        W, H = img_size
        logger.info(f"Generating map for RD coordinates: x={x}, y={y}, zoom={zoom}")

        # Get tile numbers for location
        xt, yt = WMTSMapGenerator.rd2tile(x, y, zoom)
        # Get pixel position within tile
        xp, yp = WMTSMapGenerator.rd2pixel(x, y, zoom)

        # Calculate required tiles in each direction
        tiles_left = WMTSMapGenerator.calc_tiles_in_pixels(xp, W / 2)
        tiles_top = WMTSMapGenerator.calc_tiles_in_pixels(yp, H / 2)
        tiles_right = WMTSMapGenerator.calc_tiles_in_pixels(TILE_SIZE - xp, W / 2)
        tiles_bottom = WMTSMapGenerator.calc_tiles_in_pixels(TILE_SIZE - yp, H / 2)

        logger.debug(f"Tile calculations - xt: {xt}, yt: {yt}, xp: {xp}, yp: {yp}")
        logger.debug(f"Required tiles - left: {tiles_left}, top: {tiles_top}, right: {tiles_right}, bottom: {tiles_bottom}")

        # Load and combine tiles
        img = WMTSMapGenerator.load_image(url_template, zoom, xt, yt, 
                                          tiles_left, tiles_top, tiles_right, tiles_bottom)

        # Calculate marker position in combined image
        mx = int(tiles_left * TILE_SIZE + xp)
        my = int(tiles_top * TILE_SIZE + yp)

        # Calculate crop coordinates
        x1 = int(mx - W / 2)
        x2 = x1 + W
        y1 = int(my - H / 2)
        y2 = y1 + H

        # Crop to desired size
        cropped = img.crop((x1, y1, x2, y2))

        return cropped