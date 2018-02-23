import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw
from intelligent_scissor import IntelligentScissor
import numpy as np
import time

#TODO
#Zoom in Zoom out
#Show various debug pic
#refacdtor canvas draw line

debug_setting = True

#Global variables shared between files
#cursor_x, cursor_y holds current cursor coordinates
cursor_x, cursor_y = 0, 0
#point_stack saves all past clicks
point_stack = []
#canvas ids of line segments in path drawn on canvas, correspond to the computed path
canvas_path = []
canvas_path_stack = []
min_path = []
contour_stack = []
history_paths = []

#Global variables used within this file
#file_name = ''
#image = ''
scissor_flag = False
finish_flag = False
lastx, lasty = 0, 0
canvas_id = 0
#start_x, start_y = 0, 0
i = 0
wrap_length = 1920

#TODO set these flags to False when a window is closed
scissor_window_exist = False
brush_window_exist = False
help_window_exist = False
about_window_exist = False

#obj = IntelligentScissor(cvimg, (int(seed_x),int(seed_y)))
#obj.link_calculation()
#start_time = time.time()
#print('node dict generation')
#obj.generate_all_node_dict()
#print('node dict generation time:', time.time() - start_time)

def open_image():
    global canvas, image, cvimg, scissor_flag,  obj, draw_image
    #TODO remove debug clause
    default = False
    scissor_flag = False
    if default == True:
        image = ImageTk.PhotoImage(file='./images/test.jpg')
        #cvimg = cv2.imread("../images/test.jpg")
        cvimg = np.array(Image.open("./images/test.jpg"))
        canvas.create_image(0,0, image=image, anchor=NW)
    else :
        #TODO get current path
        file_name = filedialog.askopenfilename(initialdir = './images')
        image = ImageTk.PhotoImage(file=file_name)
        pil_img = Image.open(file_name)
        canvas.create_image(0,0, image=image, anchor=NW)
        draw_image = ImageDraw.Draw(pil_img)
    obj = IntelligentScissor(np.array(pil_img))

def seed_to_graph(seed_x,seed_y):
    #global obj
    obj.update_seed((seed_x, seed_y))
    start_time = time.time()
    #print('cost_map_generation')
    obj.cost_map_generation()
    obj.path_tree_generation()

    print('cost map generation time:', time.time() - start_time)
    #print('cost map generation COMPLETED')

def live_wire_mode(flag):
    global scissor_flag
    if flag == True:
        scissor_flag = True
        canvas.configure(cursor = 'pencil')
    else:
        scissor_flag = False
        canvas.configure(cursor = 'left_ptr')

def start(event):
    global lastx, lasty, start_x, start_y, scissor_flag, point_stack, finish_flag
    live_wire_mode(True)
    finish_flag = False
    start_x, start_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    lastx, lasty = start_x, start_y
    point_stack.append([start_x,start_y,-99])
    stack_label.configure(text=point_stack)
    print('start_x, start_y: {0} {1}'.format(start_x, start_y))
    seed_to_graph(start_x,start_y)

def close_contour_finish(event):
    global scissor_flag, canvas_id, canvas_path_stack, canvas_path, i, history_paths, finish_flag, obj, contour_stack
    print('close contour finish called')
    if (scissor_flag == True):
        #canvas_id = canvas.create_line((lastx, lasty, start_x, start_y), fill=color, width=1,tags='currentline')
        remove_canvas_path(canvas_path)
        canvas_path.clear()
        draw_path(start_x,start_y, line_width = 3)
        canvas_path_stack.append(canvas_path[:])
        min_path = obj.get_path((int(start_x),int(start_y)))
        history_paths.append(min_path[:])

        #min_path_label.configure(text = '{0}th canvas_path: {1}'.format(i,canvas_path))
        #history_paths_label.configure(text='path_stack {0}: {1}'.format(i, canvas_path_stack[i]))

        i = i + 1

        canvas_path.clear()
        live_wire_mode(False)

        point_stack.append([start_x,start_y,canvas_id])
        finish_flag = True
        #TODO uncomment to integrate
        obj.generate_mask(history_paths)
    else:
        print('Warning: end() is called before start()')
    show_debug(show = debug_setting)

def finish(event):
    global scissor_flag, finish_flag
    live_wire_mode(False)
    finish_flag = True
    print('finish called')

def click_xy(event):
    global lastx, lasty, scissor_flag, point_stack, canvas_id, canvas_path, canvas_path_stack, i
    #print('event x y:{0} {1}'.format(event.x,event.y))
    #print('last  x y:{0} {1}'.format(lastx,lasty))
    if (scissor_flag == True):

        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        set_color('green')

        #fix current path on canvas, start new seed
        #canvas_id = canvas.create_line((lastx, lasty, x, y), fill=color, width=1,tags='currentline')
        #remove_canvas_path(canvas_path)
        #draw_path(x,y,line_width = 3)
        canvas.itemconfigure(canvas_path[0],width =3)
        min_path = obj.get_path((int(x),int(y)))
        history_paths.append(min_path[:])
        #min_path_label.configure(text='path_stack before append {0}: {1}'.format(i, canvas_path_stack))
        #history_paths_label.configure(text='path_stack {0}: {1}'.format(i, canvas_path_stack[0]))
        #history_paths_label.configure(text='path_stack after {0}: {1}'.format(i, canvas_path_stack))
        canvas_path_stack.append(canvas_path[:])
        #canvas_path_stack.append('test {0}'.format(i))
        #history_paths_label.configure(text='path_stack {0}: {1}'.format(i, canvas_path_stack[0]))
        i = i + 1
        canvas_path.clear()

        #generate new graph with new seed
        seed_to_graph(x,y)

        lastx, lasty = x, y
        point_stack.append([x,y,canvas_id])

    show_debug(show = debug_setting)

def delete_path(event):
    global canvas_id, lastx, lasty, scissor_flag, canvas_path, canvas_path_stack, finish_flag
    #[popx, popy, pop_id] = point_stack[-1]
    if scissor_flag == True:
        [popx, popy, pop_id] = point_stack.pop()
        #stack_label.configure(text=point_stack)

        canvas_path_to_be_removed = canvas_path_stack.pop()
        min_path_to_be_removed = history_paths.pop()
        if pop_id == -99 :
            live_wire_mode(False)
            remove_canvas_path(canvas_path)
        else :
            #delete point in stack
            canvas.delete(pop_id)
            [lastx, lasty, canvas_id] = point_stack[-1]
            seed_to_graph(lastx,lasty)
            #delete drawn path on canvas
            remove_canvas_path(canvas_path_to_be_removed)

    elif finish_flag==True:
        while len(canvas_path_stack)>0:
            path = canvas_path_stack.pop()
            remove_canvas_path(path)
        live_wire_mode(False)
        finish_flag = False
        canvas_path_stack.clear()
        canvas_path.clear()

    else:
        print('please move cursor inside an existing contour to delete')
        #TODO select existing contour and delete it

    #update debug info
    show_debug(show = debug_setting)

def draw_line_image(path_):
    # TODO draw path in canvas_path_stack to image and saved as countour
    pass

def get_xy(event):
    global cursor_x, cursor_y, cursor_label, canvas_id, lastx, lasty, canvas_path
    cursor_x, cursor_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    cursor_label.configure(text = 'x:{0} y:{1}'.format(cursor_x, cursor_y))
    #print(cursor_x, cursor_y)
    if scissor_flag == True:
        #remove last path in canvas
        remove_canvas_path(canvas_path)
        canvas_path.clear()
        #draw new path on canvas
        draw_path(cursor_x,cursor_y, line_width = 6)
        #in_path = obj.get_path((int(cursor_x),int(cursor_y)))
        #min_path_label.configure(text = 'current canvas_path: {1}'.format(i,canvas_path))
    show_debug(show = debug_setting)

def show_debug(show):
    if show == True:
        debug_label.configure(text='scissor_flag:{0}'.format(scissor_flag))
        debug2_label.configure(text='line_id:{0}'.format(canvas_id))
        debug3_label.configure(text='lastx:{0} lasty:{1}'.format(lastx,lasty))

        # TODO show debug info in different mode
        #debug4_label.configure(text='removed_id:{0}'.format(pop_id))
        #min_path_label.configure(text = 'min_path to be removed: {1}'.format(i,min_path_to_be_removed))
        #history_paths_label.configure(text='path_stack after pop: {1}'.format(i, history_paths))

    if scissor_flag == True:
        min_path_label.configure(text = '{0}th path: {1}'.format(i,min_path))
        history_paths_label.configure(text='history_paths after {0}th append: {1}'.format(i, history_paths))
        canvas_path_label.configure(text = '{0}th canvas path: {1}'.format(i,canvas_path))
        canvas_path_stack_label.configure(text='canvas path stack after {0}th append: {1}'.format(i, canvas_path_stack))
        #min_path_label.configure(text = 'closing min_path: {1}'.format(i,min_path))
        #history_paths_label.configure(text='closed history_paths : {1}'.format(i, history_paths))
        stack_label.configure(text=point_stack)


def remove_canvas_path(canvas_path_to_be_removed):
    canvas_path_len = len(canvas_path_to_be_removed)
    for line_id in canvas_path_to_be_removed:
        canvas.delete(line_id)
    #canvas_path_to_be_removed.clear()

def draw_path(x,y,line_width):
    global cursor_label, canvas_id, lastx, lasty, canvas_path, min_path_label, min_path
    cursor_label.configure(text = 'getting path for x:{0} y:{1}'.format(cursor_x, cursor_y))
    min_path = obj.get_path((int(x),int(y)))
    set_color('red')
    min_path_len = len(min_path)
    canvas_id = canvas.create_line(min_path, fill = color, width = line_width, tags = 'currentline')
    canvas_path.append(canvas_id)
    #for index, point in enumerate(min_path):
    #    if index < (min_path_len - 1):
    #        next_point = min_path[index + 1]
    #    else:
    #        #print('reached last point, break for loop')
    #        break
        #canvas_id = canvas.create_line((point[0],point[1],next_point[0],next_point[1]), fill = color, width = line_width, tags = 'currentline')
        #canvas_path.append(canvas_id)


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
    if scissor_flag==True or finish_flag==True:
        file_name = filedialog.asksaveasfilename(initialdir = './images',
                filetypes = (("png files","*.png"), ("jpeg files","*.jpg")))
        canvas.postscript(file=file_name, colormode='color')
    #return

def save_mask():
    if finish_flag==True:
        file_name = filedialog.asksaveasfilename(initialdir = './images',
                filetypes = (("png files","*.png"), ("jpeg files","*.jpg")))
        Image.fromarray((obj.mask*255).astype(np.uint8)).save(file_name)
    #return

def create_help_window():
    global help_window_exist
    if help_window_exist == False:
        help_window_exist = True
        help_window = tkinter.Toplevel(root)
        help_window.title('Help')
        help_frame = ttk.Frame(help_window,padding='5', borderwidth = '8')
        help_frame.grid(column = 0, row = 0)
        #TODO better way to show help text
        help_text = tkinter.Text(help_window)
        help_text.grid(column = 0, row = 0)

def create_about_window():
    global about_window_exist
    if about_window_exist == False:
        about_window_exist = True
        about_window = tkinter.Toplevel(root)
        about_window.title('About this software')
        about_frame = ttk.Frame(about_window,padding='5', borderwidth = '8')
        about_frame.grid(column = 0, row = 0)
        about_label = ttk.Label(about_frame, wraplength = 300, text = 'This piece of software is a computer vision course project (COMP5421 Spring 2018 HKUST) by Hao & Lei, all rights reserved ... for you! \n\nSeriously, do what ever you want with it.\n\nLicense: MIT')
        about_label.grid(column = 0, row = 0)

def create_brush_window():
    global brush_window_exist
    if brush_window_exist == False:
        brush_window_exist = True
        brush_window = tkinter.Toplevel(root)
        brush_window.title('Brush Config')

def create_scissor_window():
    global scissor_window_exist, scissor_mode
    if scissor_window_exist == False:
        scissor_window_exist = True
        #window
        scissor_window = tkinter.Toplevel(root)
        scissor_window.title('Scissor Config')
        scissor_window.grid_columnconfigure(0,weight = 1)
        scissor_window.grid_rowconfigure(0, weight = 1)
        #frame
        scissor_frame = ttk.Frame(scissor_window,padding='5', borderwidth = '8')
        scissor_frame.grid(column = 0, row = 0, sticky = (N,W,E,S))
        #contents
        scissor_range_label = ttk.Label(scissor_frame, text='Scissor Range')
        work_mode_label = ttk.Label(scissor_frame, text='Work Mode')
        debug_mode_label = ttk.Label(scissor_frame, text='Debug Mode')
        scissor_debug_label = ttk.Label(scissor_frame, text='<debug info>')
        scissor_debug2_label = ttk.Label(scissor_frame, text='<debug info>')

        #TODO show separators
        separator1 = ttk.Separator(scissor_frame, orient=HORIZONTAL)
        separator2 = ttk.Separator(scissor_frame, orient=HORIZONTAL)

        brush_selection = BooleanVar()
        scissor_range = ttk.Checkbutton(scissor_frame, text = 'Brush Selection', variable = brush_selection, onvalue = True, offvalue = False)

        scissor_mode = StringVar()
        image_only = ttk.Radiobutton(scissor_frame, text = 'Image Only', variable = scissor_mode, value = 'image_only')
        image_with_contour = ttk.Radiobutton(scissor_frame, text = 'Image with Contour', variable = scissor_mode, value = 'image_with_contour')
        pixel_nodes = ttk.Radiobutton(scissor_frame, text = 'Pixel Nodes', variable = scissor_mode, value = 'pixel_nodes')
        cost_graph = ttk.Radiobutton(scissor_frame, text = 'Cost Graph', variable = scissor_mode, value = 'cost_graph')
        path_tree = ttk.Radiobutton(scissor_frame, text = 'Path Tree', variable = scissor_mode, value = 'path_tree')
        minimum_path = ttk.Radiobutton(scissor_frame, text = 'Minimum Path', variable = scissor_mode, value = 'minimum_path')
        gradient_map = ttk.Radiobutton(scissor_frame, text = 'Gradient Map', variable = scissor_mode, value = 'gradient_map')

        scissor_range_label.grid(column = 0, row = 0, sticky = (W,N))
        scissor_range.grid(column = 0, row = 1, sticky = (W,N))
        separator1.grid(column = 0, row = 4, sticky = W)

        work_mode_label.grid(column = 0, row = 5, sticky = (W,N))
        image_only.grid(column = 0, row = 6, sticky = W)
        image_with_contour.grid(column = 1, row = 6, sticky = W)

        debug_mode_label.grid(column = 0, row = 7, sticky = (W,N))
        pixel_nodes.grid(column = 0, row = 8, sticky = W)
        cost_graph.grid(column = 1, row = 8, sticky = W)
        path_tree.grid(column = 0, row = 9, sticky = W)
        minimum_path.grid(column = 1, row = 9, sticky = W)
        gradient_map.grid(column = 0, row = 10, sticky = W)

        separator2.grid(column = 0, row = 13, sticky = W)
        scissor_debug_label.grid(column = 0, row = 14, sticky = (W,N))
        scissor_debug2_label.grid(column = 0, row = 15, sticky = (W,N))

        #binding
        scissor_window.bind('<1>',lambda e : scissor_debug_label.configure(text = scissor_mode.get()))
        scissor_window.bind('<1>',lambda e : scissor_debug2_label.configure(text = brush_selection.get()))

root = Tk()
root.title('Intelligent Scissors by Lei & Hao HKUST COMP5421 Spring 2018')
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

#menu
menubar = Menu(root)
file_menu = Menu(menubar, tearoff = 0)
file_menu.add_command(label="Open Image", command = open_image)
file_menu.add_separator()
file_menu.add_command(label="Save Contour", command = save_contour)
file_menu.add_command(label="Save Mask", command = save_mask)
file_menu.add_separator()
file_menu.add_command(label="Exit", command = root.quit)
menubar.add_cascade(label="File", menu=file_menu)

tools_menu = Menu(menubar, tearoff = 0)
tools_menu.add_command(label = "Scissor", command = create_scissor_window)
tools_menu.add_command(label = "Brush", command = create_brush_window)
menubar.add_cascade(label="Tools", menu=tools_menu)

help_menu = Menu(menubar, tearoff = 0)
help_menu.add_command(label = "Help", command = create_help_window)
help_menu.add_command(label = "About", command = create_about_window)
menubar.add_cascade(label="Help", menu=help_menu)

root.configure(menu = menubar)

#frame
mainframe = ttk.Frame(root,padding='3', borderwidth = '8')
#mainframe['relief'] = 'ridge'
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))

#define scroll bar
h = ttk.Scrollbar(mainframe, orient=HORIZONTAL)
v = ttk.Scrollbar(mainframe, orient=VERTICAL)

#canvas
canvas = Canvas(mainframe, width=640, height=480, bg='white',scrollregion=(0, 0, 1920, 1080), yscrollcommand=v.set,xscrollcommand=h.set)
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


stack_label = ttk.Label(mainframe, text='<stack info>', wraplength = wrap_length, justify = 'left')
stack_label.grid(column = 0, row = 6, columnspan = 4, sticky = (W,N))

canvas_path_label = ttk.Label(mainframe, text='<canvas path info>', wraplength = wrap_length, justify = 'left')
canvas_path_label.grid(column = 0, row = 7, columnspan = 4, sticky = (W,N))
canvas_path_stack_label = ttk.Label(mainframe, text='<canvas path stack info>', wraplength = wrap_length, justify = 'left')
canvas_path_stack_label.grid(column = 0, row = 8, columnspan = 4, sticky = (W,N))

min_path_label = ttk.Label(mainframe, text='<min path info>', wraplength = wrap_length, justify = 'left')
min_path_label.grid(column = 0, row = 9, columnspan = 4, sticky = (W,N))
history_paths_label = ttk.Label(mainframe, text='<history paths info>', wraplength = wrap_length, justify = 'left')
history_paths_label.grid(column = 0, row = 10, columnspan = 4, sticky = (W,N))


#Main function binding
canvas.bind('<Button-1>', click_xy)
canvas.bind('<Control-Button-1>', start)
root.bind('<Return>', finish)
root.bind('<BackSpace>', delete_path)
root.bind('<Control-Return>', close_contour_finish)
canvas.bind('<Motion>', get_xy)
canvas.bind('<3>',lambda e : canvas.scan_mark(e.x, e.y))
canvas.bind('<B3-Motion>',lambda e: canvas.scan_dragto(e.x, e.y))
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

