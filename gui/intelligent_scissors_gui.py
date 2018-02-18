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
lastx, lasty = 0, 0
canvas_id = 0
#startx, starty = 0, 0

def start(event):
    global lastx, lasty, startx, starty, start_flag, xy_stack
    start_flag = True
    startx, starty = canvas.canvasx(event.x), canvas.canvasy(event.y)
    lastx, lasty = startx, starty
    xy_stack.append([startx,starty,-99])
    stack_label.configure(text=xy_stack)
    print('startx, starty: {0} {1}'.format(startx, starty))

def close_contour_finish(event):
    global start_flag, canvas_id
    print('close contour finish called')
    if (start_flag == True):
        canvas_id = canvas.create_line((lastx, lasty, startx, starty), fill=color, width=5,tags='currentline')
        start_flag = False
    else:
        print('Warning: end() is called before start()')

def finish(event):
    global start_flag
    start_flag = False
    print('finish called')

def click_xy(event):
    global lastx, lasty, start_flag, xy_stack, canvas_id
    #print('event x y:{0} {1}'.format(event.x,event.y))
    #print('last  x y:{0} {1}'.format(lastx,lasty))
    if (start_flag == True):
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        canvas_id = canvas.create_line((lastx, lasty, x, y), fill=color, width=5,tags='currentline')
        lastx, lasty = x, y
        xy_stack.append([x,y,canvas_id])
        stack_label.configure(text=xy_stack)

def delete(event):
    global canvas_id, lastx, lasty, start_flag
    #[popx, popy, pop_id] = xy_stack[-1]
    if start_flag == True:
        [popx, popy, pop_id] = xy_stack.pop()
        stack_label.configure(text=xy_stack)
        if pop_id == -99 :
            start_flag = False
        else :
            canvas.delete(pop_id)
            [lastx, lasty, canvas_id] = xy_stack[-1]
            stack_label.configure(text=xy_stack)
            debug_label.configure(text='canvas_id:{0}'.format(canvas_id))
            debug2_label.configure(text='removed_id:{0}'.format(pop_id))
            debug3_label.configure(text='lastx:{0} lasty:{1}'.format(lastx,lasty))

def get_xy(event):
    global cursor_x, cursor_y, cursor_label, canvas_id, lastx, lasty
    cursor_x, cursor_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    cursor_label.configure(text = 'x:{0} y:{1}'.format(cursor_x, cursor_y))
    debug_label.configure(text='start_flag:{0}'.format(start_flag))
    debug2_label.configure(text='line_id:{0}'.format(canvas_id))
    debug3_label.configure(text='lastx:{0} lasty:{1}'.format(lastx,lasty))
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
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

#frame
mainframe = ttk.Frame(root,padding='20', borderwidth = '8')
mainframe['relief'] = 'ridge'
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))

#define scroll bar
h = ttk.Scrollbar(mainframe, orient=HORIZONTAL)
v = ttk.Scrollbar(mainframe, orient=VERTICAL)

#canvas
canvas = Canvas(mainframe, width=500, height=500, bg='white',scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set,xscrollcommand=h.set)
canvas.grid(column=0, row=1, sticky=(N,W,E,S))

#scroll bar setup
h['command'] = canvas.xview
v['command'] = canvas.yview
h.grid(column=0, row=2, sticky=(W,E))
v.grid(column=1, row=1, sticky=(N,S))

#button
button_open_image = ttk.Button(mainframe, text = 'open image', command = open_image).grid(column=0,row=0, sticky=(W,N))

#size grip
ttk.Sizegrip(root).grid(column=1, row=1, sticky=(S,E))

#show cursor coornidate
cursor_label =ttk.Label(mainframe, text='x:0,y:0')
cursor_label.grid(column = 0, row = 3, sticky = (E,S))
canvas.bind('<Leave>', lambda e: cursor_label.configure(text='cursor outside canvas'))

#show other debug info
stack_label = ttk.Label(mainframe, text='<stack info>')
stack_label.grid(column = 0, row = 7, sticky = (E,S))
debug_label = ttk.Label(mainframe, text='<debug info>')
debug_label.grid(column = 0, row = 4, sticky = (E,S))
debug2_label = ttk.Label(mainframe, text='<debug2 info>')
debug2_label.grid(column = 0, row = 5, sticky = (E,S))
debug3_label = ttk.Label(mainframe, text='<debug3 info>')
debug3_label.grid(column = 0, row = 6, sticky = (E,S))

#Main function binding
canvas.bind('<Button-1>', click_xy)
canvas.bind('<Control-Button-1>', start)
root.bind('<Return>', finish)
root.bind('<BackSpace>', delete)
root.bind('<Control-Return>', close_contour_finish)
canvas.bind('<Motion>', get_xy)
#canvas.bind('<B1-Motion>', add_line)
#canvas.bind('<B1-ButtonRelease>', done_stroke)

#TODO palette, should do with color chooser dialog
canvas_id = canvas.create_rectangle((10, 10, 30, 30), fill='red', tags=('palette','palettered', 'paletteSelected'))
canvas.tag_bind(canvas_id, '<Button-1>', lambda x: set_color('red'))
canvas_id = canvas.create_rectangle((10, 35, 30, 55), fill='green', tags=('palette','palettegreen'))
canvas.tag_bind(canvas_id, '<Button-1>', lambda x: set_color('green'))
set_color('red')
canvas.itemconfigure('palette', width=5)

root.mainloop()

