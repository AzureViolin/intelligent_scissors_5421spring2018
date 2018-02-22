from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
from intelligent_scissor import IntelligentScissor
import numpy as np
import time

#Global variables shared between files
#cursor_x, cursor_y holds current cursor coordinates
cursor_x, cursor_y = 0, 0
#xy_stack saves all past clicks
xy_stack = []
#canvas ids of line segments in path drawn on canvas, correspond to the computed path
canvas_path = []
canvas_path_stack = []

#Global variables used within this file
#file_name = ''
#image = ''
start_flag = False
lastx, lasty = 0, 0
canvas_id = 0
#startx, starty = 0, 0

#obj = IntelligentScissor(cvimg, (int(seed_x),int(seed_y)))
#obj.link_calculation()
#start_time = time.time()
#print('node dict generation')
#obj.generate_all_node_dict()
#print('node dict generation time:', time.time() - start_time)

def open_image():
    global canvas, image, cvimg, start_flag, obj
    #TODO remove debug clause
    default = False
    start_flag = False
    if default == True:
        image = ImageTk.PhotoImage(file='../images/test.jpg')
        #cvimg = cv2.imread("../images/test.jpg")
        cvimg = np.array(Image.open("../images/test.jpg"))
        canvas.create_image(0,0, image=image, anchor=NW)
    else :
        file_name = filedialog.askopenfilename()
        image = ImageTk.PhotoImage(file=file_name)
        #cvimg = cv2.imread(file_name)
        cvimg = np.array(Image.open(file_name))
        canvas.create_image(0,0, image=image, anchor=NW)
    obj = IntelligentScissor(cvimg)

def seed_to_graph(seed_x,seed_y):
    global obj
    obj.update_seed((seed_x, seed_y))
    start_time = time.time()
    print('cost_map_generation')
    obj.cost_map_generation()
    print('cost map generation time:', time.time() - start_time)
    print('cost map generation COMPLETED')

def start(event):
    global lastx, lasty, startx, starty, start_flag, xy_stack
    start_flag = True
    startx, starty = canvas.canvasx(event.x), canvas.canvasy(event.y)
    lastx, lasty = startx, starty
    xy_stack.append([startx,starty,-99])
    stack_label.configure(text=xy_stack)
    print('startx, starty: {0} {1}'.format(startx, starty))
    seed_to_graph(startx,starty)

def close_contour_finish(event):
    global start_flag, canvas_id
    print('close contour finish called')
    if (start_flag == True):
        canvas_id = canvas.create_line((lastx, lasty, startx, starty), fill=color, width=1,tags='currentline')
        start_flag = False
    else:
        print('Warning: end() is called before start()')

def finish(event):
    global start_flag
    start_flag = False
    print('finish called')

def click_xy(event):
    global lastx, lasty, start_flag, xy_stack, canvas_id, canvas_path
    #print('event x y:{0} {1}'.format(event.x,event.y))
    #print('last  x y:{0} {1}'.format(lastx,lasty))
    if (start_flag == True):

        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        set_color('green')

        #fix current path on canvas, start new seed
        #canvas_id = canvas.create_line((lastx, lasty, x, y), fill=color, width=1,tags='currentline')
        draw_path()
        canvas_path_stack.append(canvas_path)
        canvas_path.clear()

        #generate new graph with new seed
        seed_to_graph(x,y)

        lastx, lasty = x, y
        xy_stack.append([x,y,canvas_id])
        stack_label.configure(text=xy_stack)
    debug_label.configure(text='start_flag:{0}'.format(start_flag))
    debug2_label.configure(text='line_id:{0}'.format(canvas_id))
    debug3_label.configure(text='lastx:{0} lasty:{1}'.format(lastx,lasty))

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
    global cursor_x, cursor_y, cursor_label, canvas_id, lastx, lasty, canvas_path
    cursor_x, cursor_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    cursor_label.configure(text = 'x:{0} y:{1}'.format(cursor_x, cursor_y))
    debug_label.configure(text='start_flag:{0}'.format(start_flag))
    debug2_label.configure(text='line_id:{0}'.format(canvas_id))
    debug3_label.configure(text='lastx:{0} lasty:{1}'.format(lastx,lasty))
    #print(cursor_x, cursor_y)
    if start_flag == True:
        #remove last path in canvas
        canvas_path_len = len(canvas_path)
        for line_id in canvas_path:
            canvas.delete(line_id)
        canvas_path.clear()
        #draw new path on canvas
        draw_path()

def draw_path():
    global cursor_label, canvas_id, lastx, lasty, canvas_path
    cursor_label.configure(text = 'getting path for x:{0} y:{1}'.format(cursor_x, cursor_y))
    path = obj.get_path((int(cursor_x),int(cursor_y)))
    set_color('red')
    path_len = len(path)
    for index, point in enumerate(path):
        if index < (path_len - 1):
            next_point = path[index + 1]
        else:
            #print('reached last point, break for loop')
            break
        canvas_id = canvas.create_line((point[0],point[1],next_point[0],next_point[1]), fill = color, width = 1, tags = 'currentline')
        #canvas_id = canvas.create_line((point[1],point[0],next_point[1],next_point[0]), fill = color, width = 1, tags = 'currentline')
        canvas_path.append(canvas_id)


        #cursor_label.configure(text = 'getting path for x:{0} y:{1}'.format(cursor_x, cursor_y))
        #path = obj.get_path((int(cursor_x),int(cursor_y)))
        #print(path)

def set_color(newcolor):
    global color
    color = newcolor
    canvas.dtag('all', 'paletteSelected')
    canvas.itemconfigure('palette', outline='white')
    canvas.addtag('paletteSelected', 'withtag', 'palette%s' % color)
    canvas.itemconfigure('paletteSelected', outline='#999999')

def save_contour():
    return

def save_mask():
    return

root = Tk()
root.title('Intelligent Scissors by Lei & Hao HKUST COMP5421 Spring 2018')
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

#menu
menubar = Menu(root)
filemenu = Menu(menubar, tearoff = 0)
filemenu.add_command(label="Open Image", command = open_image)
filemenu.add_separator()
filemenu.add_command(label="Save Contour", command = save_contour)
filemenu.add_command(label="Save Mask", command = save_mask)
filemenu.add_separator()
filemenu.add_command(label="Exit", command = root.quit)
menubar.add_cascade(label="File", menu=filemenu)

toolmenu = Menu(menubar, tearoff = 0)
toolmenu.add_command(label = "Scissor")
menubar.add_cascade(label="Tool", menu=toolmenu)

root.configure(menu = menubar)

#frame
mainframe = ttk.Frame(root,padding='20', borderwidth = '8')
mainframe['relief'] = 'ridge'
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))

#define scroll bar
h = ttk.Scrollbar(mainframe, orient=HORIZONTAL)
v = ttk.Scrollbar(mainframe, orient=VERTICAL)

#canvas
canvas = Canvas(mainframe, width=640, height=480, bg='white',scrollregion=(0, 0, 1000, 1000), yscrollcommand=v.set,xscrollcommand=h.set)
canvas.grid(column=0, row=0, columnspan = 4, rowspan = 4, sticky=(N,W,E,S))
mainframe.columnconfigure(0,weight = 3)
mainframe.columnconfigure(1,weight = 3)
mainframe.columnconfigure(2,weight = 3)
mainframe.columnconfigure(3,weight = 3)
mainframe.rowconfigure(0,weight = 3)
mainframe.rowconfigure(1,weight = 3)
mainframe.rowconfigure(2,weight = 3)
mainframe.rowconfigure(3,weight = 3)


#scroll bar setup
h['command'] = canvas.xview
v['command'] = canvas.yview
h.grid(column=0, row=4, columnspan = 4, sticky=(W,E))
v.grid(column=4, row=0, rowspan = 4,  sticky=(N,S))

#button
#button_open_image = ttk.Button(mainframe, text = 'open image', command = open_image).grid(column=5,row=0, sticky=(E,N))

#size grip
ttk.Sizegrip(root).grid(column=1, row=1, sticky=(S,E))

#show cursor coornidate
cursor_label =ttk.Label(mainframe, text='x:0,y:0')
cursor_label.grid(column = 3, row = 5, sticky = (E,N))
canvas.bind('<Leave>', lambda e: cursor_label.configure(text='cursor outside canvas'))

#show other debug info
debug_label = ttk.Label(mainframe, text='<debug info>')
debug_label.grid(column = 0, row = 5, sticky = (W,N))
debug2_label = ttk.Label(mainframe, text='<debug2 info>')
debug2_label.grid(column = 1, row = 5, sticky = (W,N))
debug3_label = ttk.Label(mainframe, text='<debug3 info>')
debug3_label.grid(column = 2, row = 5, sticky = (W,N))
stack_label = ttk.Label(mainframe, text='<stack info>', wraplength = 600, justify = 'left')
stack_label.grid(column = 0, row = 6, columnspan = 4, sticky = (W,N))

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
set_color('green')
canvas.itemconfigure('palette', width=5)

root.mainloop()

