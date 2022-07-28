#!/usr/bin/env python

from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from datetime import datetime
import os
import PySimpleGUI as sg
from gi.repository import GLib

version = "memeify 0.0.3"

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

def caption(top_text, bottom_text):
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

sg.theme('DarkAmber')

infile = "example.png"

layout = [
  [sg.Image(key="-IMAGE-", expand_x=True, expand_y=True)],
  [sg.T("")],[sg.Text("", expand_x=True,), sg.Text("choose a picture: "), sg.FileBrowse(key="-FILE-"), sg.Button("load image"), sg.Text("", expand_x=True,)],
  [sg.InputText("TOP TEXT", key="top_text", expand_x=True)],
  [sg.InputText("BOTTOM TEXT", key="bottom_text", expand_x=True)],
  [sg.Button("memeify!", expand_x=True)]]
window = sg.Window(version , layout, size=(600,700))

while True:
  event, values = window.read()
  if event == sg.WIN_CLOSED or event=="Exit":
    break
  if event == "load image":
    if os.path.exists(values["-FILE-"]):
      with Image(filename=values["-FILE-"]) as img:
        img.transform(resize='500x500>')
        thumb = img.make_blob()
        window["-IMAGE-"].update(thumb)
  elif event == "memeify!":
    with Image(filename=values["-FILE-"]) as img:
      with Drawing() as draw:
        caption(values["top_text"], values["bottom_text"])
        outname = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES) + "/memeify-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".png"
        img.save(filename=outname)
        window.close()

fintext = "Image saved to: " + outname
with Image(filename=outname) as img:
  img.transform(resize='500x500>')
  finthumb = img.make_blob()
layout=[[sg.Image(data=finthumb, expand_x=True, expand_y=True)],
  [sg.Text(fintext, expand_x=True, justification="center")]]
window = sg.Window("memeification complete!", layout, size=(600,600))

while True:
  event, values = window.read()
  if event == sg.WIN_CLOSED or event=="Exit":
    break

window.close()
