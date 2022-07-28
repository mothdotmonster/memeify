#!/usr/bin/env python

from textwrap import wrap
from tokenize import String
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import argparse, sys, getopt, math, os

version = "0.0.1"

def usage():
  print("memeify version",version,"\nUSAGE:","\n-t / --top-text [text] - add top text""\n-b / --bottom-text [text] - add bottom text")

def word_wrap(image, draw, text, roi_width, roi_height):
    """Break long text to multiple lines, and reduce point size
    until all text fits within a bounding box."""
    mutable_message = text
    iteration_attempts = 100

    def eval_metrics(txt):
        """Quick helper function to calculate width/height of text."""
        metrics = draw.get_font_metrics(image, txt, True)
        return (metrics.text_width, metrics.text_height)

    while draw.font_size > 0 and iteration_attempts:
        iteration_attempts -= 1
        width, height = eval_metrics(mutable_message)
        if height > roi_height:
            draw.font_size -= 2  # Reduce pointsize
            mutable_message = text  # Restore original text
        elif width > roi_width:
                draw.font_size -= 2  # Reduce pointsize
                mutable_message = text  # Restore original text
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
  if type(top_text) == str:
    mutable_message = word_wrap(img, draw, top_text, int(img.width), 200)
    draw.text(int(img.width/2), int(draw.font_size), mutable_message)
    draw.draw(img)
  draw.font_size = 200
  if type(bottom_text) == str:
    mutable_message = word_wrap(img, draw, bottom_text, int(img.width), 200)
    draw.text(int(img.width/2), int(img.height)-20, mutable_message)
    draw.draw(img)

argv = sys.argv[3:]

if len(sys.argv) == 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
  usage()
  sys.exit(0)


if os.path.isfile(sys.argv[1]) == False:
  print("Error: Invalid input file!")
  sys.exit(1)
if sys.argv[2].endswith(".png") == False:
  print("Error: Invalid output filename, must end with .png!")
  sys.exit(1)

try:
  opts, args = getopt.getopt(argv, "t:b:", ["debug","top-text=","bottom-text="])
except getopt.GetoptError as err:
  # print help information and exit:
  print(err)  # will print something like "option -a not recognized"
  usage()
  sys.exit(2)

output = None

with Image(filename=sys.argv[1]) as img:
  with Drawing() as draw:
    for o, a in opts:
      if o in ("--debug"):
        debug = True
      elif o in ("-t", "--top-text"):
        caption(a, None)
      elif o in ("-b", "--bottom-text"):
        caption(None, a)
      else:
        assert False, "unhandled option"
    
    img.save(filename=sys.argv[2])