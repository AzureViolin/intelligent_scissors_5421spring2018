# Usage
1. open image
1. click on any point as first seed, wait for computation to end
1. move mouse and see visualized path in real time (currently does not re-compute seeds)

## environment setup
python==3.6/3.4.3
opencv==3.1/3.4
heapdict
tkinter

## to run gui
```bash
cd core
python3 gui.py
```
- support open any image in system
- currently draw straight lines between clicks. Should be updated with drawing the path found by Dijkstra algorithm.
## interfaces
- cursor_x, cursor_y stores current mouse coordinates.
- xy_stack is a list that stores previous clicked points

## GUI operation manual
Done
1. Ctrl + left click : first seed
1. left  click : following seed
1. moving cursor in sissor mode: keep a stack for previous seeds in sequence shared between GUI and algorithm.  The top element is the current seed. GUI keep sending current cursor coordinates to algorithm, and algorithm keeps computing the path, send it back to GUI, where GUI visuializes it.

Currently in progress (partially implemented)
1. Enter : finish the current contour
1. Ctrl + Enter: close current contour and fish
1. Backspace: when scissoring, delete the last seed; otherwise, delete selected contour. Select a contour by moving onto it. Selected contour is red, un-selected ones are green.

Not implemented
1. Ctrl + '+' : zoom in
1. Ctrl + '-' : zoom out
1. Arrow key : navigate
