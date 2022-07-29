#!/usr/bin/env python

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from datetime import datetime
import os
import PySimpleGUI as sg
import numpy as np
from gi.repository import GLib

version = "memeify 0.2.2 (linux)"

sg.theme('DarkAmber') # i like it

def word_wrap(image, draw, text, roi_width, roi_height):
  # Reduce point size until all text fits within a bounding box.
  mutable_message = text
  iteration_attempts = 100

  def eval_metrics(txt):
    # Quick helper function to calculate width/height of text.
    metrics = draw.get_font_metrics(image, txt, True)
    return (metrics.text_width, metrics.text_height)

  while draw.font_size > 0 and iteration_attempts:
    iteration_attempts -= 1
    width, height = eval_metrics(mutable_message)
    if height > roi_height:
      draw.font_size -= 2  # Reduce pointsize
    elif width > roi_width:
      draw.font_size -= 2  # Reduce pointsize
    else:
      break
  if iteration_attempts < 1:
    raise RuntimeError("Unable to calculate word_wrap for " + text)
  return mutable_message

def caption(image, top_text, bottom_text): # given an image (as a blob), caption it
  with Image(blob=image) as img:
    with Drawing() as draw:
      draw.stroke_color = "black"
      draw.stroke_width = 3
      draw.fill_color = Color('white')
      draw.font_family = 'Impact'
      draw.font_size = 200
      draw.text_alignment = "center"
      if len(top_text) > 0:
        mutable_message = word_wrap(img, draw, top_text, int(img.width), 200)
        draw.text(int(img.width/2), int(draw.font_size), mutable_message)
        draw.draw(img)
      draw.font_size = 200
      if len(bottom_text) > 0:
        mutable_message = word_wrap(img, draw, bottom_text, int(img.width), 200)
        draw.text(int(img.width/2), int(img.height)-20, mutable_message)
        draw.draw(img)
      return img.make_blob()

def deep_fry(image):
  with Image(blob=image) as img:
    img.transform(resize='200x200>')
    img.posterize(levels=4)
    img.format = "jpg"
    img.format = "png"
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

def meme_window(): # main meme-making window
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.T("")],[sg.Text("", expand_x=True,), sg.Text("choose a picture: "), sg.FileBrowse(key="-FILE-"), sg.Button("load image"), sg.Text("", expand_x=True,)],
    [sg.Text("filter:"), sg.DropDown(['deep fry', 'liquid rescale', 'implode', 'explode', 'swirl', 'invert', 'rotational blur'], key = "filter", expand_x=True)],
    [sg.Text("top text:"), sg.InputText(key="top_text", expand_x=True)],
    [sg.Text("bottom text:"), sg.InputText(key="bottom_text", expand_x=True)],
    [sg.Button("memeify!", expand_x=True), sg.Button("export!", expand_x=True)]]
  return sg.Window(version, layout, size=(600,700), finalize=True)

def ouroborous_window(): # special version without file selector as to stop users from ruining things
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text("filter:"), sg.DropDown(['deep fry', 'liquid rescale', 'implode', 'explode', 'swirl', 'invert', 'rotational blur'], key = "filter", expand_x=True)],
    [sg.Text("top text:"), sg.InputText(key="top_text", expand_x=True)],
    [sg.Text("bottom text:"), sg.InputText(key="bottom_text", expand_x=True)],
    [sg.Button("memeify!", expand_x=True), sg.Button("export!", expand_x=True)]]
  return sg.Window(version, layout, size=(600,700), finalize=True)

def export_window(): # output window
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.Text(key="fintext", expand_x=True, justification="center")]]
  return sg.Window("memeification complete!", layout, size=(600,600), finalize=True)

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
          img.transform(resize='500x500>')
          thumb = img.make_blob()
          window["-IMAGE-"].update(thumb)
    elif event == "memeify!":
      meme = caption(meme, values["top_text"], values["bottom_text"])
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

      with Image(blob=meme) as img:
        img.transform(resize='500x500>')
        thumb = img.make_blob()
        window.close()
        window = ouroborous_window() # and so the meme eats its own tail
        window["-IMAGE-"].update(thumb)
    elif event == "export!":
      meme = caption(meme, values["top_text"], values["bottom_text"])
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

      with Image(blob=meme) as img:
        outname = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES) + "/memeify-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"
        fintext = "Image saved as: " + outname
        img.save(filename=outname)
        img.transform(resize='500x500>')
        finthumb = img.make_blob()
        window.close()
        window = export_window()
        window["-IMAGE-"].update(finthumb)
        window["fintext"].update(fintext)
  window.close()

if __name__ == '__main__':
    main()
