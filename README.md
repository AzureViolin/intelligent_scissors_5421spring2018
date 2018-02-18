## environment setup
python==3.6
opencv==3.1

## to run gui
```python
python3 gui/intelligent_scissors_gui.py
```
- support open any image in system
- currently draw straight lines between clicks. Should be updated with drawing the path found by Dijkstra algorithm.
## interfaces
- cursor_x, cursor_y stores current mouse coordinates.
- xy_stack is a list that stores previous clicked points
