#!/usr/bin/env python

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from datetime import datetime
import os
import PySimpleGUI as sg

version = "memeify 0.1.0"

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

sg.theme('DarkAmber')

def meme_window(): # main meme-making window
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.T("")],[sg.Text("", expand_x=True,), sg.Text("choose a picture: "), sg.FileBrowse(key="-FILE-"), sg.Button("load image"), sg.Text("", expand_x=True,)],
    [sg.InputText("TOP TEXT", key="top_text", expand_x=True)],
    [sg.InputText("BOTTOM TEXT", key="bottom_text", expand_x=True)],
    [sg.Button("memeify!", expand_x=True), sg.Button("export!", expand_x=True)]]
  return sg.Window(version, layout, size=(600,700), finalize=True)

def ouroborous_window(): # special version without file selector as to stop users from ruining things
  layout = [
    [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
    [sg.InputText("TOP TEXT", key="top_text", expand_x=True)],
    [sg.InputText("BOTTOM TEXT", key="bottom_text", expand_x=True)],
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
          meme = img.make_blob()
          img.transform(resize='500x500>')
          thumb = img.make_blob()
          window["-IMAGE-"].update(thumb)
    elif event == "memeify!":
      with Image(blob=meme) as img:
        with Drawing() as draw:
          draw.stroke_color = "black"
          draw.stroke_width = 3
          draw.fill_color = Color('white')
          draw.font_family = 'Impact'
          draw.font_size = 200
          draw.text_alignment = "center"
          if len(values["top_text"]) > 0:
            mutable_message = word_wrap(img, draw, values["top_text"], int(img.width), 200)
            draw.text(int(img.width/2), int(draw.font_size), mutable_message)
            draw.draw(img)
          draw.font_size = 200
          if len(values["bottom_text"]) > 0:
            mutable_message = word_wrap(img, draw, values["bottom_text"], int(img.width), 200)
            draw.text(int(img.width/2), int(img.height)-20, mutable_message)
            draw.draw(img)
          meme = img.make_blob()
          img.transform(resize='500x500>')
          thumb = img.make_blob()
          window.close()
          window = ouroborous_window() # and so the meme eats its own tail
          window["-IMAGE-"].update(thumb)
    elif event == "export!":
      with Image(blob=meme) as img:
        with Drawing() as draw:
          draw.stroke_color = "black"
          draw.stroke_width = 3
          draw.fill_color = Color('white')
          draw.font_family = 'Impact'
          draw.font_size = 200
          draw.text_alignment = "center"
          if len(values["top_text"]) > 0:
            mutable_message = word_wrap(img, draw, values["top_text"], int(img.width), 200)
            draw.text(int(img.width/2), int(draw.font_size), mutable_message)
            draw.draw(img)
          draw.font_size = 200
          if len(values["bottom_text"]) > 0:
            mutable_message = word_wrap(img, draw, values["bottom_text"], int(img.width), 200)
            draw.text(int(img.width/2), int(img.height)-20, mutable_message)
            draw.draw(img)
          outname = "memeify-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"
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
