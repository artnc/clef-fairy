# Clef Fairy

This is a quick-and-dirty script that takes PDF sheet music written in treble clef and spits out bass clef transpositions. Doesn't work on scans.

## Usage

1. Install [Docker](https://docs.docker.com/docker-for-mac/install/) on your Mac or Linux machine
1. Clone this repo
1. Run `./clef-fairy /path/to/sheet/music.pdf`
1. Wait a comically long time (on my laptop: about 6 seconds per page)

The result will be generated at `/path/to/sheet/music.bass.pdf`.
