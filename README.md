# asciigpu

asciigpu is a simple python program that reads the current GPU utilization and temperature (and more details if requested) and displays them in a clear way, using a clean terminal ui.

This project came to pass because I ran into the asciimatics terminal GUI libray and wanted to do something with it. At the time I was rendering on a GPU server and most monitoring software was a pain with multiple GPUs.

Requires asciimatics and nv

`pip install asciimatics`

and pynvml

`pip install nvidia-ml-py3`

![overview](https://github.com/flipswitchingmonkey/asciigpu/blob/master/screenshots/asciigpu_1.png)
![details](https://github.com/flipswitchingmonkey/asciigpu/blob/master/screenshots/asciigpu_2.png)
