#!/usr/bin/env python2
"""This programme displays the date and time and temperature, and telegram msgs on an RGBMatrix display."""

import time
import datetime
import redis
import json
import re
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image


def rgbmatrix_options():
    options = RGBMatrixOptions()
    options.multiplexing = 1
    options.row_address_type = 0
    options.brightness = 60
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'regular'
    options.inverse_colors = False
    options.led_rgb_sequence = "GBR"
    options.gpio_slowdown = 4
    options.pwm_lsb_nanoseconds = 50
    options.show_refresh_rate = 1
    options.disable_hardware_pulsing = False
    options.scan_mode = 1
    options.pwm_bits = 11
    # options.daemon = 0
    # options.drop_privileges = 0
    # options.pixel_mapper_config = "U-mapper;Rotate:90"
    options.pixel_mapper_config = "Rotate:90"
    return RGBMatrix(options=options)


# Load up the font (use absolute paths so script can be invoked
# from /etc/rc.local correctly)
def loadFont(font):
    global fonts
    fonts[font] = graphics.Font()
    fonts[font].LoadFont("fonts/" + font + ".bdf")


def alert(matrix, images):
    matrix.brightness = 100
    for i in range(10):
        emoji_image = Image.open("64x64/u0001f6a8.png")
        emoji_image_ok = Image.new("RGB", emoji_image.size, "BLACK")
        emoji_image_ok.paste(emoji_image, (0, 0), emoji_image)
        MyMatrix.SetImage(emoji_image_ok.convert('RGB'))
        time.sleep(0.1)
        MyMatrix.SetImage(Image.new("RGB", emoji_image.size, "BLACK"))
        time.sleep(0.1)
    matrix.brightness = 80
    for image in images:
        image = re.sub(r'^\+', r'', image)
        emoji_image = Image.open("64x64/" + image + ".png")
        emoji_image_ok = Image.new("RGB", emoji_image.size, "BLACK")
        emoji_image_ok.paste(emoji_image, (0, 0), emoji_image)
        MyMatrix.SetImage(emoji_image_ok.convert('RGB'))
        time.sleep(2)
    matrix.brightness = 60


flip = True
tick = True
scroller = 64
tscroller = 64
nralerts = 0
maxalerts = 2

redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

MyMatrix = rgbmatrix_options()

# set colour
WHITE = graphics.Color(255, 255, 255)
GRAY = graphics.Color(128, 128, 128)
RED = graphics.Color(255, 0, 0)
GREEN = graphics.Color(0, 255, 0)
BLUE = graphics.Color(0, 0, 255)
YELLOW = graphics.Color(255, 255, 0)
PURPLE = graphics.Color(255, 0, 255)

lastDateFlip = int(round(time.time() * 1000))
lastSecondFlip = int(round(time.time() * 1000))
lastScrollTick = int(round(time.time() * 1000))

fonts = {}

loadFont('c64_9')
loadFont('c64_5')
loadFont('c64_6')
loadFont('c64_7')
loadFont('c64_16')
loadFont('c64_11')
loadFont('c64_10')

# boot msg
telegram = ""
sizeoftelegram = len(telegram)*7

# Create the buffer canvas
MyOffsetCanvas = MyMatrix.CreateFrameCanvas()
while(1):
    currentDT = datetime.datetime.now()
    time.sleep(0.05)

#    if currentDT.hour < 23:
#        scrollColour = BLUE
        #fulldate = currentDT.strftime("%d-%m-%y  %A")
        #if currentDT.day < 10:
        #    fulldate = fulldate[1:]

#    sizeofdate = len(fulldate)*7

    Millis = int(round(time.time() * 1000))

    if Millis-lastSecondFlip > 1000:
        lastSecondFlip = int(round(time.time() * 1000))
        tick = not tick

    if Millis-lastDateFlip > 5000:
        lastDateFlip = int(round(time.time() * 1000))
        flip = not flip

    tscroller = tscroller-1
    if tscroller == (-sizeoftelegram):
        oldmsg = telegram
        telegram = redis.get('message')
        emojis = json.loads(redis.get('emoji'))
        if oldmsg != telegram:
            nralerts = 0
        if nralerts >= maxalerts:
            nralerts = maxalerts + 1
        if nralerts <= maxalerts:
            alert(MyMatrix, emojis)
            nralerts = nralerts + 1
        sizeoftelegram = len(telegram)*22
        tscroller = 64

    thetimea = currentDT.strftime("%H")
    thetimeb = currentDT.strftime("%M")
    secs = int(currentDT.strftime("%S"))
    thetick = ":" if tick else " "
    sizeoftick = 26
    thetick = str.lstrip(thetick)
    thetimea = str.lstrip(thetimea)
    thetimeb = str.lstrip(thetimeb)
    sizeoftimea = -1
    sizeoftimeb = 34

    thedate = currentDT.strftime("%d-%m")
    thedate = str.lstrip(thedate)

    line = '------'

    thetmpoutside = redis.get('temp_outside') + 'c out'
    
    thewind = redis.get('wind')

    select = secs %4
    if select == 0:
      thetmpinside = redis.get('temp_workshop') + 'c wrk'
    elif select == 1:
      thetmpinside = redis.get('temp_office') + 'c off'
    elif select == 2:
      thetmpinside = redis.get('temp_lab') + 'c lab'
    elif select == 3:
      thetmpinside = redis.get('temp_kitchen') + 'c kit'

    if nralerts < maxalerts:
        graphics.DrawText(MyOffsetCanvas, fonts['c64_16'], tscroller, 56,
                          RED, telegram.decode('utf8'))
    if nralerts >= maxalerts:
        graphics.DrawText(MyOffsetCanvas, fonts['c64_7'], 2, 36,
                          RED, line)

        graphics.DrawText(MyOffsetCanvas, fonts['c64_6'], 4, 42,
                          WHITE, thetmpoutside)

        graphics.DrawText(MyOffsetCanvas, fonts['c64_6'], 4, 52,
                          GRAY, thetmpinside)
        
        graphics.DrawText(MyOffsetCanvas, fonts['c64_6'], 4, 62,
                          GRAY, thewind)

    graphics.DrawText(MyOffsetCanvas, fonts['c64_7'], 7, 27, GREEN,
                      thedate)

    graphics.DrawText(MyOffsetCanvas, fonts['c64_11'], sizeoftimea, 15, YELLOW,
                      thetimea)
    
    graphics.DrawText(MyOffsetCanvas, fonts['c64_10'], sizeoftick, 15, RED,
                      thetick)
    
    graphics.DrawText(MyOffsetCanvas, fonts['c64_11'], sizeoftimeb, 15, YELLOW,
                      thetimeb)

    MyOffsetCanvas = MyMatrix.SwapOnVSync(MyOffsetCanvas)
    MyOffsetCanvas.Clear()
