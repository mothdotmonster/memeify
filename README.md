# magick-memes
memey scripts for imagemagick

TODO:
- switch to using mktemp instead of just hoping the user doesn't care about anything with tmp in the name
- figure out why deepfry gives a warning when run with only top text

# cubify
![cubify](images/cubify.png)

turn any image into a cube with one easy step!

USAGE: `cubify [in] [out]`

# memeify 
![memeify](images/memeify.png)

adds "meme" captions to images

USAGE: `memeify [in] [out] [top text] [bottom text (optional)]`

# memeify-neue
![memeify-neue](images/neue.png)

adds modern "meme" captions to images

USAGE: `memeify-neue [in] [out] [text]`

# deepfry
![deepfry](images/deepfry.png)

"deep fries" images, and optionally calls `memeify` to add captions

USAGE: `deepfry [in] [out] [top text (optional)] [bottom text (optional)]`
