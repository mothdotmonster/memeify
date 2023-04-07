#!/usr/bin/env python

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from datetime import datetime
import os, sys, textwrap
import PySimpleGUI as sg
import numpy as np

if sys.platform.startswith('linux'): # load Linux dependencies if on Linux
  from gi.repository import GLib

  def namegen(name):
    return GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES) + os.sep + name + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"

elif sys.platform.startswith('win'): # load Windows dependencies if on Windows
  import ctypes
  import ctypes.wintypes

  mypictures = 0x0027 # magic number for Pictures folder on windows

  def winpath(magic): # turns magic number into windows path
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH) # create buffer for path to go into
    ctypes.windll.shell32.SHGetFolderPathW(None, magic, None, 0, buf) # ctypes magic
    return str(buf.value) # return path

  def namegen(name): # put it all together
    return winpath(mypictures) + os.sep + name + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"

else:
  def namegen(name): # fallback
    return name + "-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".jpg"

if sys.platform.startswith('win'): # change icon filetype if on Windows
  iconpath = os.path.join("icons", "icon.ico")
else:
  iconpath = os.path.join("icons", "icon.png")

version = "memeify 0.2.7 (git version)"
oldmeme = [] # a special tool that will help us later

sg.theme('DarkAmber') # i like it

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def thumbnail(image, size): # turn an image into a thumbnail
  with Image(blob=image) as img:
    if img.height > img.width:
      img.sample(height=size, width=int((img.width/img.height)*size))
    else:
      img.sample(width=size, height=int((img.height/img.width)*size))
    return img.make_blob()

def caption(image, top_text, bottom_text): # given an image (as a blob), caption it
  with Image(blob=thumbnail(image, 1024)) as img: # make sure image is reasonably sized
    with Drawing() as draw:
      draw.stroke_color = "black"
      draw.stroke_width = 3
      draw.fill_color = Color('white')
      draw.font_family = 'Impact'
      draw.text_alignment = "center"
      draw.font_size = 200
      if len(top_text) > 0:
        draw.font_size = min(200,int((img.width/draw.get_font_metrics(img, top_text).text_width)*200))
        draw.text(int(img.width/2), int(draw.font_size), top_text)
        draw.draw(img)
      draw.font_size = 200
      if len(bottom_text) > 0:
        draw.font_size = min(200,int((img.width/draw.get_font_metrics(img, bottom_text).text_width)*200))
        draw.text(int(img.width/2), int(img.height)-20, bottom_text)
        draw.draw(img)
      return img.make_blob()

def deep_fry(image): # attempts to deep fry image
  with Image(blob=image) as img:
    img.transform(resize='200x200>')
    img.posterize(levels=16)
    img.compression_quality = 20
    img.format = "jpg"
    df = img.make_blob()
  with Image(blob=df) as img:
    img.format = "png"
    img.transform(resize='1000x1000<')
    return img.make_blob()

def liquid_rescale(image): 
  with Image(blob=image) as img:
    img.liquid_rescale(height=int(img.height/2), width=int(img.width/2))
    return img.make_blob()

def implode(image):
  with Image(blob=image) as img:
    img.implode(amount=0.5)
    return img.make_blob()

def explode(image):
  with Image(blob=image) as img:
    img.implode(amount=-1)
    return img.make_blob()

def invert(image): # obscenely complicated image inverting
  with Image(blob=image) as img:
    img.alpha_channel = 'remove' #close alpha channel   
    img.background_color = Color('white') 
    array = np.array(img) # convert image into array
  with Image.from_array(np.invert(array), channel_map="rgb") as img: # invert array and turn it back into an image
    img.format = 'png' # make sure it's a png so nothing else breaks
    return img.make_blob()

def swirl(image):
  with Image(blob=image) as img:
    img.swirl(degree=180)
    return img.make_blob()

def rotational_blur(image):
  with Image(blob=image) as img:
    img.rotational_blur(angle=10)
    return img.make_blob()

def cubify(image):
  with Image(blob=image) as top:
    top.virtual_pixel = 'transparent'
    top.resize(height=1000,width=1000)
    top.distort('affine',
    (0,0, 0,250,
    1000,1000, 900,250,
    0,1000, 450,500))
    with Image(blob=image) as left:
      left.virtual_pixel = 'transparent'
      left.resize(height=1000,width=1000)
      left.distort('affine',
      (0,0, 0,250,
      1000,1000, 450,1000,
      1000,0, 450,500))
      with Image(blob=image) as right:
        right.virtual_pixel = 'transparent'
        right.resize(height=1000,width=1000)
        right.distort('affine',
        (0,0, 450,500,
        1000,0, 900,250,
        0,1000, 450,1000))
        right.composite(top)
        right.composite(left)
        right.crop(height=1000,width=900)
        return right.make_blob()

def motivation(image, top_text, bottom_text):
  with Image(blob=image) as img:
    with Drawing() as draw:
      img.transform(resize="800x800")
      draw.font_family = "Times New Roman"
      draw.font_size = 200
      draw.text_alignment = "center"
      if len(top_text) > 0: # avoid dividing by zero
        topsize = min(200,int((img.width/draw.get_font_metrics(img, top_text).text_width)*200))
      if len(bottom_text) > 0:
        bottomsize = min(50,int((img.width/draw.get_font_metrics(img, bottom_text).text_width)*200))
      img.border(Color("black"), 10, 10)
      img.border(Color("white"), 5, 5)
      img.border(Color("black"), 185, 185)
      with Image(background = Color("black"), height = int(img.height+200), width = img.width) as sorry: # i'll figure out a better way to do this later
        sorry.composite(img)
        draw.fill_color = Color("white")
        if len(top_text) > 0:
          draw.font_size = topsize
          draw.text(int(sorry.width/2), int(sorry.height - 200), top_text)
          draw.draw(sorry)
        draw.font_size = 200
        if len(bottom_text) > 0:
          draw.font_size = bottomsize
          draw.text(int(sorry.width/2), int(sorry.height - 100), bottom_text)
          draw.draw(sorry)
        sorry.format = 'png'
        return sorry.make_blob()

def caption_neue(image, text):
  with Image(blob=image) as img:
    with Drawing() as draw:
      textwidth = 100
      mutable_text = "\n".join(textwrap.wrap(text, textwidth))
      draw.font_family = "Arial"
      draw.text_alignment = "center"
      draw.font_size = int(img.width/15)
      while draw.get_font_metrics(img, mutable_text, multiline=True).text_width > img.width: # horrible brute forcing, but it does technically work
        textwidth -= 1
        mutable_text = "\n".join(textwrap.wrap(text, textwidth))
      with Image(height = int((draw.get_font_metrics(img, mutable_text, multiline=True).text_height)+50+img.height), width = img.width, background = Color("white")) as cap:
        draw.text(int(img.width/2), int((draw.font_size)+20), mutable_text)
        draw.draw(cap)
        cap.composite(img, top=int(cap.height-img.height))
        cap.format = "png"
        return cap.make_blob()
      
def pixel(image):
  with Image(blob=image) as img:
    img.transform(resize='128x128') # fit image into 128x128 square
    img.sample(img.width*2, img.height*2)
    img.ordered_dither('o4x4,6')
    return img.make_blob()
  
def funnymark(image):
  with Image(blob=image) as img:
    with Image(filename=resource_path(os.path.join('icons', 'funnywatermark.png'))) as watermark:
      watermark.background_color = Color("#222")
      watermark.splice(width=img.width-watermark.width, height=0, gravity='west')
      img.image_add(watermark)
    img.montage(mode='concatenate', tile='1x2')
    img.format = "png"
    return img.make_blob()
  
def flipmark(image):
  with Image(blob=image) as img:
    with Drawing() as draw:
      draw.font_family = "Arial"
      draw.text_alignment = "left"
      draw.fill_color = Color('grey')
      draw.font_size = 16
      draw.text(4,img.height-4, 'memeify.moth.monster')
      draw.draw(img)
    return img.make_blob()
  
def madewith(image, text):
  with Image(blob=image) as img:
    with Drawing() as draw:
      draw.font_family = "Arial-Bold"
      draw.text_alignment = "left"
      draw.fill_color = Color('white')
      draw.font_size = 20
      draw.text(8,img.height-8, text)
      draw.draw(img)
    return img.make_blob()

def meme_window(): # main meme-making window
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text("", expand_x=True),sg.Text("", key="filedisplay"),sg.Text("", expand_x=True)],
    [sg.Text("", expand_x=True),sg.Text("choose an image: "),sg.FileBrowse(target="filedisplay",key="-FILE-"), sg.Button("load image"), sg.Text("", expand_x=True,)],
    [sg.Text("filter:"), sg.DropDown(['caption', 'caption neue', 'motivational poster', 'deep fry', 'liquid rescale', 'implode', 'explode', 'swirl', 'invert', 'rotational blur', 'cubify', 'pixel art', 'funny watermark', 'flippy watermark', 'made with'], key = "filter", expand_x=True, enable_events=True)],
    [sg.Text("top text:"), sg.InputText(key="top_text", expand_x=True, disabled=True)],
    [sg.Text("bottom text:"), sg.InputText(key="bottom_text", expand_x=True, disabled=True)],
    [sg.Button("memeify!", expand_x=True), sg.Button("preview!", expand_x=True), sg.Button("nevermind...", expand_x=True, disabled=True), sg.Button("export!", expand_x=True)]]
  return sg.Window(version, layout, icon=resource_path(iconpath), size=(600,700), finalize=True)

def ouroborous_window(): # special version without file selector as to stop users from ruining things
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text("filter:"), sg.DropDown(['caption', 'caption neue', 'motivational poster', 'deep fry', 'liquid rescale', 'implode', 'explode', 'swirl', 'invert', 'rotational blur', 'cubify', 'pixel art', 'funny watermark', 'flippy watermark', 'made with'], key = "filter", expand_x=True, enable_events=True)],
    [sg.Text("top text:"), sg.InputText(key="top_text", expand_x=True, disabled=True)],
    [sg.Text("bottom text:"), sg.InputText(key="bottom_text", expand_x=True, disabled=True)],
    [sg.Button("memeify!", expand_x=True), sg.Button("preview!", expand_x=True), sg.Button("nevermind...", expand_x=True), sg.Button("export!", expand_x=True)]]
  return sg.Window(version, layout, icon=resource_path(iconpath), size=(600,700), finalize=True)

def export_window(): # output window
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text(key="fintext", expand_x=True, justification="center")]]
  return sg.Window("memeification complete!", layout, icon=resource_path(iconpath), size=(600,600), finalize=True)

def main():
  window = meme_window() # open starting window
  while True: # main event loop
    window, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED or event == 'Exit':
      break
    elif event == "load image":
      infile = values["-FILE-"]
      if os.path.exists(infile):
        with Image(filename=infile) as img:
          img.format = 'png'
          meme = img.make_blob()
        window["-IMAGE-"].update(thumbnail(meme, 500))
    elif event == "filter":
      if values["filter"] == "caption" or values["filter"] == "motivational poster":
        window["top_text"].update(disabled=False)
        window["bottom_text"].update(disabled=False)
      elif values["filter"] == "caption neue" or values["filter"] == "made with":
        window["top_text"].update(disabled=False)
        window["bottom_text"].update(disabled=True)
      else:
        window["top_text"].update(disabled=True)
        window["bottom_text"].update(disabled=True)
    elif event == "memeify!":
      oldmeme.append(meme) # stack up our old memes
      if values["filter"] == "caption":
        meme = caption(meme, values["top_text"], values["bottom_text"])
      if values["filter"] == "caption neue":
        meme = caption_neue(meme, values["top_text"])
      if values["filter"] == "motivational poster":
        meme = motivation(meme, values["top_text"], values["bottom_text"])
      if values["filter"] == "liquid rescale":
        meme = liquid_rescale(meme)
      if values["filter"] == "implode":
        meme = implode(meme)
      if values["filter"] == "explode":
        meme = explode(meme)
      if values["filter"] == "invert":
        meme = invert(meme)
      if values["filter"] == "swirl":
        meme = swirl(meme)
      if values["filter"] == "deep fry":
        meme = deep_fry(meme)
      if values["filter"] == "rotational blur":
        meme = rotational_blur(meme)
      if values["filter"] == "cubify":
        meme = cubify(meme)
      if values["filter"] == "pixel art":
        meme = pixel(meme)
      if values["filter"] == "funny watermark":
        meme = funnymark(meme)
      if values["filter"] == "flippy watermark":
        meme = flipmark(meme)
      if values["filter"] == "made with":
        meme = madewith(meme, values["top_text"])
      window.close()
      window = ouroborous_window() # and so the meme eats its own tail
      window["-IMAGE-"].update(thumbnail(meme, 500))
    elif event == "nevermind...": # undo button
      meme = oldmeme.pop() # pop an old meme off the stack
      window.close()
      window = ouroborous_window()
      if not oldmeme:
        window["nevermind..."].update(disabled=True)
      window["-IMAGE-"].update(thumbnail(meme, 500))
    elif event == "preview!": # preview without doing the thing
      if values["filter"] == "caption":
        prememe = caption(meme, values["top_text"], values["bottom_text"])
      if values["filter"] == "caption neue":
        prememe = caption_neue(meme, values["top_text"])
      if values["filter"] == "motivational poster":
        prememe = motivation(meme, values["top_text"], values["bottom_text"])
      if values["filter"] == "liquid rescale":
        prememe = liquid_rescale(meme)
      if values["filter"] == "implode":
        prememe = implode(meme)
      if values["filter"] == "explode":
        prememe = explode(meme)
      if values["filter"] == "invert":
        prememe = invert(meme)
      if values["filter"] == "swirl":
        prememe = swirl(meme)
      if values["filter"] == "deep fry":
        prememe = deep_fry(meme)
      if values["filter"] == "rotational blur":
        prememe = rotational_blur(meme)
      if values["filter"] == "cubify":
        prememe = cubify(meme)
      if values["filter"] == "pixel art":
        prememe = pixel(meme)
      if values["filter"] == "funny watermark":
        prememe = funnymark(meme)
      if values["filter"] == "flippy watermark":
        prememe = flipmark(meme)
      if values["filter"] == "made with":
        prememe = madewith(meme, values["top_text"])
      window["-IMAGE-"].update(thumbnail(prememe, 500))
    elif event == "export!":
      outname = namegen("memeify")
      fintext = "Image saved as: " + outname
      with Image(blob=meme) as img:
        img.save(filename=outname)
      window.close()
      window = export_window()
      window["-IMAGE-"].update(thumbnail(meme, 500))
      window["fintext"].update(fintext)
  window.close()

if __name__ == '__main__':
    main()
