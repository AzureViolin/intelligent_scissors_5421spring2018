from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image

#Global variables shared between files
#cursor_x, cursor_y holds current cursor coordinates
cursor_x, cursor_y = 0, 0
#xy_stack saves all past clicks
xy_stack = []

#Global variables used within this file
#file_name = ''
#image = ''
start_flag = False
#lastx, lasty = 0, 0
#startx, starty = 0, 0

def start(event):
    global lastx, lasty, startx, starty, start_flag, xy_stack
    start_flag = True
    startx, starty = canvas.canvasx(event.x), canvas.canvasy(event.y)
    lastx, lasty = startx, starty
    xy_stack.append([startx,starty])
    print('startx, starty: {0} {1}'.format(startx, starty))

def end(event):
    if (start_flag == True):
        canvas.create_line((lastx, lasty, startx, starty), fill=color, width=5,tags='currentline')
    else:
        print('Warning: end() is called before start()')


def click_xy(event):
    global lastx, lasty, start_flag, xy_stack
    #print('event x y:{0} {1}'.format(event.x,event.y))
    #print('last  x y:{0} {1}'.format(lastx,lasty))
    if (start_flag == True):
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        canvas.create_line((lastx, lasty, x, y), fill=color, width=5,tags='currentline')
        lastx, lasty = x, y
        xy_stack.append([x,y])

def get_xy(event):
    global cursor_x, cursor_y
    cursor_x, cursor_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    #print(cursor_x, cursor_y)

def open_image():
    global canvas, image
    file_name = filedialog.askopenfilename()
    image = ImageTk.PhotoImage(file=file_name)
    canvas.create_image(0,0, image=image, anchor=NW)

def set_color(newcolor):
    global color
    color = newcolor
    canvas.dtag('all', 'paletteSelected')
    canvas.itemconfigure('palette', outline='white')
    canvas.addtag('paletteSelected', 'withtag', 'palette%s' % color)
    canvas.itemconfigure('paletteSelected', outline='#999999')


root = Tk()
root.title('Intelligent Scissors by Lei & Hao HKUST COMP5421 Spring 2018')

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

#TODO debugging
#l =ttk.Label(mainframe, text='Starting...')
#l.grid(column = 1, row = 0, sticky = W)
#l.bind('<Enter>', lambda e: l.configure(text='Moved mouse inside'))
#l.bind('<Return>', lambda e: l.configure(text='Pressed Return'))
#l.bind('<Leave>', lambda e: l.configure(text='Moved mouse outside'))
#l.bind('<1>', lambda e: l.configure(text='Clicked left mouse button'))
#l.bind('<Double-1>', lambda e: l.configure(text='Double clicked'))

canvas.bind('<Button-1>', click_xy)
canvas.bind('<Control-Button-1>', start)
root.bind('<Return>', end)
canvas.bind('<Motion>', get_xy)
#canvas.bind('<B1-Motion>', add_line)
#canvas.bind('<B1-ButtonRelease>', done_stroke)

id = canvas.create_rectangle((10, 10, 30, 30), fill='red', tags=('palette','palettered', 'paletteSelected'))
canvas.tag_bind(id, '<Button-1>', lambda x: set_color('red'))
id = canvas.create_rectangle((10, 35, 30, 55), fill='green', tags=('palette','palettegreen'))
canvas.tag_bind(id, '<Button-1>', lambda x: set_color('green'))
set_color('red')

canvas.itemconfigure('palette', width=5)

root.mainloop()

