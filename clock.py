#!/usr/bin/env python
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
	#options.pixel_mapper_config = "U-mapper;Rotate:90"
	options.pixel_mapper_config = "Rotate:90"
	return RGBMatrix(options=options)



# Load up the font (use absolute paths so script can be invoked
# from /etc/rc.local correctly)
def loadFont(font):
    global fonts
    fonts[font] = graphics.Font()
    fonts[font].LoadFont("fonts/" + font + ".bdf")

def alert(matrix,images):
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
            image = re.sub(r'^\+',r'',image)
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
maxalerts = 3

redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

MyMatrix = rgbmatrix_options()

# set colour
WHITE = graphics.Color(255, 255, 255)
GRAY = graphics.Color(128, 128, 128)
RED = graphics.Color(255, 0, 0)
GREEN = graphics.Color(0, 255, 0)
BLUE = graphics.Color(0, 0, 255)
YELLOW = graphics.Color(245, 190, 59)
PURPLE = graphics.Color(255, 0, 255)

lastDateFlip = int(round(time.time() * 1000))
lastSecondFlip = int(round(time.time() * 1000))
lastScrollTick = int(round(time.time() * 1000))

fonts = {}

loadFont('hack16')
loadFont('hack18')
loadFont('hack8')
    
# boot msg
telegram = ""
sizeoftelegram = len(telegram)*7 

# Create the buffer canvas
MyOffsetCanvas = MyMatrix.CreateFrameCanvas()
while(1):
    currentDT = datetime.datetime.now()

    if currentDT.hour < 23:
        time.sleep(0.05)
        scrollColour = BLUE
        fulldate = currentDT.strftime("%d-%m-%y  %A")
        if currentDT.day < 10:
            fulldate = fulldate[1:]
    else:
        time.sleep(0.025)
        scrollColour = PURPLE
        fulldate = "GO HOME!!!"


    sizeofdate = len(fulldate)*7

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
	sizeoftelegram = len(telegram)*16 
        tscroller = 64

    thetime = currentDT.strftime("%H"+(":" if tick else " ")+"%M")
    thetime = str.lstrip(thetime)
    sizeoftime = (21 - (len(thetime) * 9) / 2)
    
    thedate = currentDT.strftime("%d-%m-%y")
    thedate = str.lstrip(thedate)
    sizeofdate = (40 - (len(thedate) * 9) / 2)

    line = '-------'
    sizeofline = (38 - (len(line) * 9) / 2)

    thetmpinside = '20c  in'
    sizeoftmpinside = (38 - (len(thetmpinside) * 9) / 2)
    
    thetmpoutside = '13c out'
    sizeoftmpoutside = (38 - (len(thetmpoutside) * 9) / 2)

    pmam = currentDT.strftime("%p")
    
    if nralerts < maxalerts:
	    graphics.DrawText(MyOffsetCanvas, fonts['hack18'], tscroller, 58,
                      RED, unicode(telegram.decode('utf8')))
    if nralerts >= maxalerts:
	    graphics.DrawText(MyOffsetCanvas, fonts['hack8'], sizeofline, 41,
                      RED, line)

	    graphics.DrawText(MyOffsetCanvas, fonts['hack8'], sizeoftmpinside, 50,
                      WHITE, thetmpinside)
	    
	    graphics.DrawText(MyOffsetCanvas, fonts['hack8'], sizeoftmpoutside, 60,
                      GRAY, thetmpoutside)

    graphics.DrawText(MyOffsetCanvas, fonts['hack8'], sizeofdate, 32, GREEN,
                      thedate)
    
    graphics.DrawText(MyOffsetCanvas, fonts['hack16'], sizeoftime, 20, YELLOW,
                      thetime)


    MyOffsetCanvas = MyMatrix.SwapOnVSync(MyOffsetCanvas)
    MyOffsetCanvas.Clear()
