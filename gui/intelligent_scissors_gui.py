from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image

file_name = ''
gif1 = ''
def open_image():
    global file_name, canvas, gif1
    file_name = filedialog.askopenfilename()
    gif1 = ImageTk.PhotoImage(file=file_name)
    canvas.create_image(0,0, image=gif1, anchor=NW)
    print('pressed open image')

root = Tk()
root.title("canvas test with image")

mainframe = ttk.Frame(root,padding='20', borderwidth = '8')
mainframe['relief'] = 'ridge'
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))

h = ttk.Scrollbar(mainframe, orient=HORIZONTAL)
v = ttk.Scrollbar(mainframe, orient=VERTICAL)
canvas = Canvas(mainframe, width=500, height=500, bg='white',scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set,xscrollcommand=h.set)

button_open_image = ttk.Button(mainframe, text = 'open image', command = open_image).grid(column=0,row=0, sticky=(W,N))

h['command'] = canvas.xview
v['command'] = canvas.yview
ttk.Sizegrip(root).grid(column=1, row=1, sticky=(S,E))
canvas.grid(column=0, row=1, sticky=(N,W,E,S))
h.grid(column=0, row=2, sticky=(W,E))
v.grid(column=1, row=1, sticky=(N,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
lastx, lasty = 0, 0

def xy(event):
    global lastx, lasty
    lastx, lasty = canvas.canvasx(event.x), canvas.canvasy(event.y)

def setColor(newcolor):
    global color
    color = newcolor
    canvas.dtag('all', 'paletteSelected')
    canvas.itemconfigure('palette', outline='white')
    canvas.addtag('paletteSelected', 'withtag', 'palette%s' % color)
    canvas.itemconfigure('paletteSelected', outline='#999999')

def addLine(event):
    global lastx, lasty
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    canvas.create_line((lastx, lasty, x, y), fill=color, width=5,
    tags='currentline')
    lastx, lasty = x, y

def doneStroke(event):
    canvas.itemconfigure('currentline', width=1)

canvas.bind("<Button-1>", xy)
canvas.bind("<B1-Motion>", addLine)
canvas.bind("<B1-ButtonRelease>", doneStroke)

id = canvas.create_rectangle((10, 10, 30, 30), fill="red", tags=('palette',
'palettered'))
canvas.tag_bind(id, "<Button-1>", lambda x: setColor("red"))
id = canvas.create_rectangle((10, 35, 30, 55), fill="blue", tags=('palette',
'paletteblue'))
canvas.tag_bind(id, "<Button-1>", lambda x: setColor("blue"))
id = canvas.create_rectangle((10, 60, 30, 80), fill="green", tags=('palette',
'palettegreen', 'paletteSelected'))
canvas.tag_bind(id, "<Button-1>", lambda x: setColor("green"))
setColor('green')

canvas.itemconfigure('palette', width=5)

root.mainloop()

