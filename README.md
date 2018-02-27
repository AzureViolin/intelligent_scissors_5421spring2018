# Usage
1. open image, wait for initialization
1. click on any point as first seed, wait a little bit for computation to end if picture is large
1. move mouse and see visualized path in real time

## environment setup
python == 3.6/3.4.3
opencv == 3.1/3.4
```bash
sudo apt-get install python3-pip python3-tk python3-pil.imagetk
sudo pip3 install numpy
```

## to run gui
```bash
python3 gui.py
```
- allow open any image in system

## interfaces & global variables
- cursor_x, cursor_y stores current mouse coordinates.
- point_stack is a list that stores previous clicked points
- canvas_path is the current path drawn on canvas
- canvas_path_stack is a list that stores previous drawn lines (in canvas_id)
- history_paths is a list that stores previous computed min paths (in pixel list)

## GUI
Implemented required feature:
1. Ctrl + left click : first seed
1. left  click : following seed
1. moving cursor in sissor mode: keep a stack for previous seeds in sequence shared between GUI and algorithm.  The top element is the current seed. GUI keep sending current cursor coordinates to algorithm, and algorithm keeps computing the path, send it back to GUI, where GUI visuializes it.
1. Enter : finish the current contour
1. Ctrl + Enter: close current contour and fish
1. Backspace: when scissoring, delete the last seed. otherwise, delete selected contour. Select a contour by moving onto it. Selected contour is thicker, un-selected ones are thinner.

Implemented additional feature:
1. Click right mouse button and grad to pan in any zoom level
1. Scroll bar
1. Different width for live wire and drawn path
1. Change cursor to pencil when in live wire mode, change it back to pointer when not.
1. Size grid at bottom right corner
1. Auto resize canvas when window is resized
1. Show mouse coordinates below canvas
1. Help menu, Help and About window

Wish list:
1. point marker for marking start and intermediate points.
1. opacity setting for all lines and markers
1. Ctrl + '+' : zoom in
1. Ctrl + '-' : zoom out
