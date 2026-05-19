# RandomNano
RandomNano is a Python program that selects a random set of albums from a given music folder. You can then transfer this random selection of albums to your mp3 player. I created this program as a way of exploring albums in my library that I wouldn't usually listen to. This program also include

## Features
- Selects a random set of albums either by number of albums or by total size in GBs.
- Optional on-the-fly mp3 conversion via ffmpeg
- Optional optimisation of imbedded artwork in order to ensure compatability with Rockbox devices and simpler mp3 players.
- Ensures the same albums aren't selected twice. The program will select every album in your library once before it cycles back through previously selected albums.

## Screenshot

![App Screenshot](https://github.com/Presto-mp3/RandomNano/blob/main/RandomNano%20Screenshot.PNG)

## Dependencies
- Python
- ffmpeg (for mp3 conversion)
