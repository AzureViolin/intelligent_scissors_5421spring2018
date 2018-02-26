import tkinter as tk
#from tkinter import *
from tkinter import ttk
from tkinter import NW
from tkinter import filedialog
from PIL import ImageTk as PILImageTk
from PIL import Image as PILImage
from PIL import ImageDraw as PILImageDraw
from intelligent_scissor import IntelligentScissor
import numpy as np
import time
from functools import partial
import cv2
import os

#TODO
#Zoom in Zoom out
#Show various debug pic
#refacdtor canvas draw line
focus_width = 5
unfocus_width = 1

highlight_id = []

debug_setting = False
brush_implemented = False

path_tree_file_name = './output/path_tree.png'
pixel_nodes_file_name = './output/pixel_nodes.png'
cost_graph_file_name = './output/cost_graph.png'
#Global variables shared between files
#cursor_x, cursor_y holds current cursor coordinates
cursor_x, cursor_y = 0, 0
#point_stack saves all past clicks
point_stack = []
#canvas ids of line segments in path drawn on canvas, correspond to the computed path
canvas_path = None
canvas_path_stack = []
min_path = []
canvas_contour_stack = []
history_paths = []
history_contour = []
contour_idx = None
hovered_mask_idx = -1
last_hovered_mask = -1

#Global variables used within this file
#file_name = ''
#image = ''
scissor_flag = False
finish_flag = False
last_x, last_y = 0, 0
canvas_id = 0
#start_x, start_y = 0, 0
i = 0
wrap_length = 1920

#TODO set these flags to False when a window is closed
scissor_window_exist = False
brush_window_exist = False
help_window_exist = False
about_window_exist = False

#scissor_mode = tk.StringVar()
#scissor_mode.set('image_with_contour')
#obj = IntelligentScissor(cvimg, (int(seed_x),int(seed_y)))
#obj.link_calculation()
#start_time = time.time()
#print('node dict generation')
#obj.generate_all_node_dict()
#start_time = time.time()
#print('node dict generation time:', time.time() - start_time)
def delete_debug_pics():
    if os.path.isfile(path_tree_file_name):
        os.remove(path_tree_file_name)
    if os.path.isfile(pixel_nodes_file_name):
        os.remove(pixel_nodes_file_name)
    if os.path.isfile(cost_graph_file_name):
        os.remove(cost_graph_file_name)

def open_image_by_file(file_name,image_tag):
    pil_img = PILImage.open(file_name)
    image = PILImageTk.PhotoImage(pil_img)
    canvas.background = image
    image_id = canvas.create_image(0,0, image=image, anchor=NW, tags=(image_tag))
    #get picture size and resize canvas window
    img_width, img_height = pil_img.size
    canvas.configure(width=img_width, height=img_height)
    return image_id

def open_image():
    global canvas, operand_image, cvimg, scissor_flag,  obj, draw_image, image_id
    #clear any information about previous image
    #TODO check if there's anything else left to be cleaned up
    delete_debug_pics()
    create_scissor_window()
    close_scissor_window()
    scissor_mode.set('image_with_contour')
    scissor_flag = False
    canvas.delete('all')
    canvas_contour_stack.clear()
    history_contour.clear()
    #TODO get current path
    file_name = filedialog.askopenfilename(initialdir = './images')
    #open image with pillow and load into PILImageTk
    pil_img = PILImage.open(file_name)
    operand_image = PILImageTk.PhotoImage(pil_img)
    #alternatively, open image directly with PILImageTk
    #image = PILImageTk.PhotoImage(file=file_name)
    image_id = canvas.create_image(0,0, image=operand_image, anchor=NW, tags = 'operand_image')

    #for draw contour with image
    draw_image = PILImageDraw.Draw(pil_img)

    obj = IntelligentScissor(np.array(pil_img))

    #get picture size and resize canvas window
    canvas.configure(width=operand_image.width(), height=operand_image.height())


def seed_to_graph(seed_x,seed_y):
    #global obj
    obj.update_seed((seed_x, seed_y))
    start_time = time.time()
    #print('cost_map_generation')
    obj.cost_map_generation()
    #obj.path_tree_generation()

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
    global last_x, last_y, start_x, start_y, scissor_flag, point_stack, finish_flag
    if scissor_mode.get() == 'image_with_contour':
        if scissor_flag == False:
            live_wire_mode(True)
            start_x, start_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
            last_x, last_y = start_x, start_y
            point_stack.clear()
            point_stack.append([start_x,start_y,-99])
            stack_label.configure(text=point_stack)
            print('start_x, start_y: {0} {1}'.format(start_x, start_y))
            seed_to_graph(start_x,start_y)
            canvas_path_stack.clear()
            canvas.delete(canvas_path)
            history_paths.clear()
        else :
            print('Warning: You have to finish a contour before starting a new one.')
    else:
        print('Warning: Initial seed only works in image with contour mode')

def close_contour_finish(event):
    global scissor_flag, canvas_id, canvas_path_stack, canvas_path, i, history_paths, finish_flag, obj, canvas_contour_stack
    print('close contour finish called')
    if scissor_flag == True:
        #canvas_id = canvas.create_line((last_x, last_y, start_x, start_y), fill=color, width=1,tags='currentline')
        canvas.delete(canvas_path)
        draw_path(start_x,start_y, line_width = unfocus_width)
        canvas_path_stack.append(canvas_path)
        canvas_contour_stack.append(canvas_path_stack[:])
        min_path = obj.get_path((int(start_x),int(start_y)))
        history_paths.append(min_path[:])
        history_contour.append((history_paths[:],1))
        i = i + 1
        #canvas.delete(canvas_path)
        canvas_path = -99
        point_stack.append([start_x,start_y,canvas_id])
        #TODO uncomment to integrate
        obj.generate_mask(history_paths, close = True)
        live_wire_mode(False)
    else:
        print('Warning: end() is called before start()')
    show_debug(show = debug_setting)

def finish(event):
    global scissor_flag
    if scissor_flag == True:
        print('finish called while contour is still open')
        live_wire_mode(False)
        canvas.delete(canvas_path)
        canvas_contour_stack.append(canvas_path_stack[:])
        min_path = obj.get_path((int(start_x),int(start_y)))
        history_paths.append(min_path[:])
        history_contour.append((history_paths[:],0))
        obj.generate_mask(history_paths, close = False)

def click_xy(event):
    global last_x, last_y, scissor_flag, point_stack, canvas_id, canvas_path, canvas_path_stack, i, highlight_id
    if scissor_flag == True and scissor_mode.get() == 'image_with_contour':
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        set_color('green')
        #fix current path on canvas, start new seed
        canvas.itemconfigure(canvas_path,width =unfocus_width)
        min_path = obj.get_path((int(x),int(y)))
        history_paths.append(min_path[:])
        canvas_path_stack.append(canvas_path)
        canvas_path = -99
        i = i + 1
        #canvas.delete(canvas_path)
        #generate new graph with new seed
        seed_to_graph(x,y)
        last_x, last_y = x, y
        point_stack.append([x,y,canvas_id])
        if os.path.isfile(path_tree_file_name):
            os.remove(path_tree_file_name)
    elif scissor_flag == False:
        print('Nothing will happen even if you keep clicking mouse, since we are not in live wire mode yet.')

    show_debug(show = debug_setting)

def delete_path(event):
    global canvas_id, last_x, last_y, scissor_flag, canvas_path, canvas_path_stack, finish_flag
    #[popx, popy, pop_id] = point_stack[-1]
    if scissor_flag == True:
        [popx, popy, pop_id] = point_stack.pop()
        if pop_id == -99 :
            live_wire_mode(False)
            canvas.delete(canvas_path)
            print('Delete initial seed of a contour')
        else :
            canvas_path_to_be_removed = canvas_path_stack.pop()
            min_path_to_be_removed = history_paths.pop()
            #delete point in stack
            canvas.delete(pop_id)
            [last_x, last_y, canvas_id] = point_stack[-1]
            seed_to_graph(last_x,last_y)
            #delete drawn path on canvas
            canvas.delete(canvas_path)
            canvas.delete(canvas_path_to_be_removed)

#    elif finish_flag==True:
#        while len(canvas_path_stack)>0:
#            path = canvas_path_stack.pop()
#            remove_canvas_path(path)
#        live_wire_mode(False)
#        finish_flag = False
#        canvas_path_stack.clear()
#        canvas.delete(canvas_path)
#
    else:
        #mask_idx, hovered_mask = obj.coordinate_mask(int(cursor_x),int(cursor_y))
        if hovered_mask_idx == -99:
            print('please move cursor inside an existing contour to delete')
        else:
            obj.delete_mask(hovered_mask_idx)
            remove_canvas_contour(canvas_contour_stack[hovered_mask_idx])
            canvas_contour_stack.pop(hovered_mask_idx)
            history_contour.pop(hovered_mask_idx)

        #TODO select existing contour and delete it

    #update debug info
    show_debug(show = debug_setting)

#def draw_line_image(path_):
    # TODO draw path in canvas_path_stack to image and saved as contour
#    pass

def get_xy(event):
    global cursor_x, cursor_y, cursor_label, canvas_id, last_x, last_y, canvas_path, hovered_mask_idx, last_hovered_mask
    cursor_x, cursor_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    cursor_label.configure(text = 'x:{0} y:{1}'.format(cursor_x, cursor_y))
    #print(cursor_x, cursor_y)
    width = operand_image.width()
    height = operand_image.height()
    if scissor_mode.get() == 'minimum_path' and scissor_flag == True:
        if cursor_x < width*3 and cursor_y < height*3 and cursor_x > 0 and cursor_y > 0:
            canvas.delete(canvas_path)
            draw_path_in_tree(cursor_x,cursor_y, line_width = focus_width)
        else:
            cursor_label.configure(text = 'cursor outside path tree image')
    elif cursor_x < width-1 and cursor_y < height-1 and cursor_x > 0 and cursor_y > 0:
        if scissor_flag == True:
            if scissor_mode.get() == 'image_with_contour':
                #remove last path in canvas
                canvas.delete(canvas_path)
                #draw new path on canvas
                draw_path(cursor_x,cursor_y, line_width = focus_width)
            #in_path = obj.get_path((int(cursor_x),int(cursor_y)))
            #min_path_label.configure(text = 'current canvas_path: {1}'.format(i,canvas_path))
        else:
            if len(obj.contour_mask_list) == 0:
                pass
            else:
                hovered_mask_idx = obj.coordinate_mask(int(cursor_x),int(cursor_y))
                if hovered_mask_idx == -99:
                    highlight_contour(canvas_contour_stack[last_hovered_mask], width = unfocus_width, color = 'green')
                else:
                    highlight_contour(canvas_contour_stack[hovered_mask_idx], width = focus_width, color = 'red')
                    last_hovered_mask = hovered_mask_idx
    else:
        cursor_label.configure(text = 'cursor outside image')

    show_debug(show = debug_setting)

def show_debug(show):
    if show == True:
        debug_label.configure(text='scissor_flag:{0}'.format(scissor_flag))
        debug2_label.configure(text='line_id:{0}'.format(canvas_id))
        debug3_label.configure(text='last_x:{0} last_y:{1}'.format(last_x,last_y))
        stack_label.configure(text='points in stack:{0}'.format(point_stack))
        history_paths_label.configure(text='canvas_contour_stack {0}: {1}'.format(i, canvas_contour_stack))
        hover_mask_label.configure(text = 'hover mask idx:{0} last hover idx:{1}'.format(hovered_mask_idx, last_hovered_mask))
        min_path_label.configure(text = 'obj contour mask list{0}: {1}'.format(i,obj.contour_mask_list))

        # TODO show debug info in different mode
        #debug4_label.configure(text='removed_id:{0}'.format(pop_id))
        #min_path_label.configure(text = 'min_path to be removed: {1}'.format(i,min_path_to_be_removed))
        #history_paths_label.configure(text='path_stack after pop: {1}'.format(i, history_paths))
        canvas_path_label.configure(text = '{0}th canvas path: {1}'.format(i,canvas_path))
        canvas_path_stack_label.configure(text='canvas path stack after {0}th append: {1}'.format(i, canvas_path_stack))

    if scissor_flag == True:
        pass
        #min_path_label.configure(text = '{0}th path: {1}'.format(i,min_path))
        #history_paths_label.configure(text='history_paths after {0}th append: {1}'.format(i, history_paths))

def highlight_contour(contour,width,color):
    for line_id in contour:
        #canvas.itemconfigure(line_id,width = width, color = color)
        canvas.itemconfigure(line_id,width = width, fill = color)

def remove_canvas_contour(canvas_path_to_be_removed):
    canvas_path_len = len(canvas_path_to_be_removed)
    for line_id in canvas_path_to_be_removed:
        canvas.delete(line_id)
    #canvas_path_to_be_removed.clear()

def draw_path_in_tree(x,y,line_width):
    global cursor_label, canvas_id, last_x, last_y, canvas_path, min_path_label, min_path
    cursor_label.configure(text = 'getting path in tree for x:{0} y:{1}'.format(cursor_x, cursor_y))
    min_path = obj.get_path_from_tree((int(x),int(y)))
    set_color('red')
    min_path_len = len(min_path)
    canvas_id = canvas.create_line(min_path, fill = color, width = line_width, tags = 'currentline')
    canvas_path = canvas_id

def draw_path(x,y,line_width):
    global cursor_label, canvas_id, last_x, last_y, canvas_path, min_path_label, min_path
    cursor_label.configure(text = 'get path for x:{0} y:{1}'.format(cursor_x, cursor_y))
    min_path = obj.get_path((int(x),int(y)))
    set_color('red')
    min_path_len = len(min_path)
    canvas_id = canvas.create_line(min_path, fill = color, width = line_width, tags = 'currentline')
    canvas_path = canvas_id
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

def zoom_in(event):
    global canvas
    for item in canvas.find_all():
        print (item)
        canvas.scale(item, 0,0,0.9,0.9)
    canvas.configure(3, 100,100)
    print ("zoom_in")

def zoom_out(event):
    print ("zoom_out")

def set_color(newcolor):
    global color
    color = newcolor
    canvas.dtag('all', 'paletteSelected')
    canvas.itemconfigure('palette', outline='white')
    canvas.addtag('paletteSelected', 'withtag', 'palette%s' % color)
    canvas.itemconfigure('paletteSelected', outline='#999999')

def save_contour():
    if scissor_flag==False:
        file_name = filedialog.asksaveasfilename(initialdir = './output',
                filetypes = (("png files","*.png"), ("jpeg files","*.jpg")))
        canvas.postscript(file=file_name, colormode='color')
    #return

def save_mask():
    if scissor_flag==False:
        save_file_name = filedialog.asksaveasfilename(initialdir = './output',
                filetypes = (("png files","*.png"), ("jpeg files","*.jpg")))
        mask_image = PILImage.fromarray((obj.mask*255).astype(np.uint8))
        mask_image.save(save_file_name)
        #input('mask saved, press enter to open mask')
        #opened_mask = PILImage.open(save_file_name)
        #print('================load pil image===============')
        #print (pil_img1)
        #mask_image_tk = PILImageTk.PhotoImage(opened_mask)
        #mask_image_id = canvas.create_image(0,0, image=mask_image_tk, anchor=NW)
        #open_image_by_file(file_name=save_file_name)
        #print('mask image id : {0}'.format(mask_image_id))
        #canvas.itemconfigure(image_id, image=mask_image_tk)
        #input('canvas should be updated by now, press enter to continue')

def show_image_only(event):
    canvas.delete('debug_image')
    canvas.delete('reopened_image')
    image_id = canvas.create_image(0,0, image=operand_image, anchor=NW, tags = ('reopened_image'))
    canvas.tag_raise(image_id)
    print('re opend image id:',image_id)
    canvas.configure(width=operand_image.width(), height=operand_image.height())
    return image_id
    #input('image should change now, enter to continue')

def show_image_with_contour(event):
    image_id = show_image_only(event)
    canvas.tag_lower(image_id)

def show_pixel_nodes(event):
    if scissor_mode.get() != 'pixel_nodes':
        if os.path.isfile(pixel_nodes_file_name):
            pass
        else:
            print('......generating pixel_nodes......')
            start_time = time.time()
            obj.link_calculation()
            print('pixel_nodes generation time:', time.time() - start_time)
            pixel_nodes_img = PILImage.fromarray((np.squeeze(obj.pixel_node)).astype(np.uint8))
            pixel_nodes_img.save(pixel_nodes_file_name)
        open_image_by_file(pixel_nodes_file_name, image_tag = 'debug_image')

def show_cost_graph(event):
    if scissor_mode.get() != 'cost_graph':
        if os.path.isfile(cost_graph_file_name):
            pass
        else:
            print('......generating cost_graph......')
            start_time = time.time()
            obj.link_calculation()
            print('cost_graph generation time:', time.time() - start_time)
            print ('cost graph shape and dtype:',obj.cost_graph.shape, obj.cost_graph.dtype)
            cost_graph_img = PILImage.fromarray(np.squeeze(obj.cost_graph).astype(np.uint8))
            cost_graph_img.save(cost_graph_file_name)
        open_image_by_file(cost_graph_file_name, image_tag = 'debug_image')

def show_path_tree(event):
    if scissor_mode.get() != 'minimum_path' and scissor_mode.get() != 'path_tree':
        if os.path.isfile(path_tree_file_name):
            pass
        else:
            print('......generating path tree......')
            start_time = time.time()
            obj.path_tree_generation()
            print('path_tree generation time:', time.time() - start_time)
            #path_tree_img = PILImage.fromarray((obj.path_tree*255).astype(np.uint8))
            path_tree_img = PILImage.fromarray((obj.path_tree))
            path_tree_img.save(path_tree_file_name)

        open_image_by_file(path_tree_file_name, image_tag = 'debug_image')

def show_minimum_path(event):
    if scissor_mode.get() != 'minimum_path' and scissor_mode.get() != 'path_tree':
        show_path_tree(event)

def create_help_window():
    global help_window_exist,help_window
    if help_window_exist == False:
        help_window_exist = True
        help_window = tk.Toplevel(root)
        help_window.protocol('WM_DELETE_WINDOW', close_help_window)
        help_window.title('Help')
        help_frame = ttk.Frame(help_window,padding='5', borderwidth = '8')
        help_frame.grid(column = 0, row = 0)
        #TODO better way to show help text
        help_text = tk.Text(help_window)
        help_text.grid(column = 0, row = 0)
        help_text.insert('1.0', '''
File-->Save Contour, save image with contour marked;
File-->Save Mask, save compositing mask for PhotoShop;
Tool-->Scissor, open a panel to choose what to draw in the window


Work Mode:

Image Only: show original image without contour superimposed on it;

Image with Contour: show original image with contours superimposed on it;


Debug Mode:

Pixel Node:  Draw a cost graph with original image pixel colors at the center of each 3by3 window, and black everywhere else;

Cost Graph: Draw a cost graph with both pixel colors and link costs, where you can see whether your cost computation is reasonable or not, e.g., low cost (dark intensity) for links along image edges.

Path Tree: show minimum path tree in the cost graph for the current seed; You can use the counter widget to simulate how the tree is computed by specifying the number of expanded nodes. The tree consists of links with yellow color. The back track direction (towards the seed) goes from light yellow to dark yellow.

Min Path: show the minimum path between the current seed and the mouse position;
To use the "path tree" and "min path" in debug mode, you need to have an active seed point. the active seed point is the last "left click / ctrl + left click" point on the contour you are working with, e.g., the contour that has not yet be committed by "enter / ctrl + enter". (See the short cut keys below)


Ctrl+"+", zoom in;
Ctrl+"-", zoom out;

Ctrl+Left click first seed;
Left click, following seeds;

Enter, finish the current contour;
Ctrl+Enter, finish the current contour as closed;

Backspace, when scissoring, delete the last seed; otherwise, delete selected contour.
Select a contour by moving onto it. Selected contour is red, un-selected ones are green.
''')
        help_text.configure(state='disabled')

def create_about_window():
    global about_window_exist, about_window
    if about_window_exist == False:
        about_window_exist = True
        about_window = tk.Toplevel(root)
        about_window.protocol('WM_DELETE_WINDOW', close_about_window)
        about_window.title('About this software')
        about_frame = ttk.Frame(about_window,padding='5', borderwidth = '8')
        about_frame.grid(column = 0, row = 0)
        about_label = ttk.Label(about_frame, wraplength = 300, text = 'This piece of software is a computer vision course project (COMP5421 Spring 2018 HKUST) by Hao & Lei, all rights reserved ... for you! \n\nSeriously, do what ever you want with it.\n\nLicense: MIT')
        about_label.grid(column = 0, row = 0)

def create_brush_window():
    global brush_window_exist, brush_window
    if brush_window_exist == False:
        brush_window_exist = True
        brush_window = tk.Toplevel(root)
        brush_window.protocol('WM_DELETE_WINDOW', close_brush_window)
        brush_window.title('Brush Config')

def create_scissor_window():
    global scissor_window_exist, scissor_mode, scissor_window
    if scissor_window_exist == False:
        scissor_window_exist = True
        #window
        scissor_window = tk.Toplevel(root)
        scissor_window.protocol('WM_DELETE_WINDOW', close_scissor_window)
        scissor_window.title('Scissor Config')
        scissor_window.grid_columnconfigure(0,weight = 1)
        scissor_window.grid_rowconfigure(0, weight = 1)
        #frame
        scissor_frame = ttk.Frame(scissor_window,padding='5', borderwidth = '8')
        scissor_frame.grid(column = 0, row = 0, sticky = (tk.N,tk.W,tk.E,tk.S))
        #contents
        scissor_range_label = ttk.Label(scissor_frame, text='Scissor Range')
        work_mode_label = ttk.Label(scissor_frame, text='Work Mode')
        debug_mode_label = ttk.Label(scissor_frame, text='Debug Mode')
        scissor_debug_label = ttk.Label(scissor_frame, text='<debug info>')
        scissor_debug2_label = ttk.Label(scissor_frame, text='<debug info>')


        #TODO show separators
        separator1 = ttk.Separator(scissor_frame, orient=tk.HORIZONTAL)
        separator2 = ttk.Separator(scissor_frame, orient=tk.HORIZONTAL)

        brush_selection = tk.BooleanVar()
        scissor_range = ttk.Checkbutton(scissor_frame, text = 'Brush Selection', variable = brush_selection, onvalue = True, offvalue = False)

        scissor_mode = tk.StringVar()
        scissor_mode.set('image_with_contour')
        image_only = ttk.Radiobutton(scissor_frame, text = 'Image Only', variable = scissor_mode, value = 'image_only')
        image_with_contour = ttk.Radiobutton(scissor_frame, text = 'Image with Contour', variable = scissor_mode, value = 'image_with_contour')
        pixel_nodes = ttk.Radiobutton(scissor_frame, text = 'Pixel Nodes', variable = scissor_mode, value = 'pixel_nodes')
        cost_graph = ttk.Radiobutton(scissor_frame, text = 'Cost Graph', variable = scissor_mode, value = 'cost_graph')
        path_tree = ttk.Radiobutton(scissor_frame, text = 'Path Tree', variable = scissor_mode, value = 'path_tree')
        minimum_path = ttk.Radiobutton(scissor_frame, text = 'Minimum Path', variable = scissor_mode, value = 'minimum_path')
        gradient_map = ttk.Radiobutton(scissor_frame, text = 'Gradient Map', variable = scissor_mode, value = 'gradient_map')

        if brush_implemented == True:
            scissor_range_label.grid(column = 0, row = 0, sticky = (tk.W,tk.N))
            scissor_range.grid(column = 0, row = 1, sticky = (tk.W,tk.N))
        separator1.grid(column = 0, row = 4, sticky = tk.W)

        work_mode_label.grid(column = 0, row = 5, sticky = (tk.W,tk.N))
        image_only.grid(column = 0, row = 6, sticky = tk.W)
        image_with_contour.grid(column = 1, row = 6, sticky = tk.W)

        debug_mode_label.grid(column = 0, row = 7, sticky = (tk.W,tk.N))
        pixel_nodes.grid(column = 0, row = 8, sticky = tk.W)
        cost_graph.grid(column = 1, row = 8, sticky = tk.W)
        path_tree.grid(column = 0, row = 9, sticky = tk.W)
        minimum_path.grid(column = 1, row = 9, sticky = tk.W)
        #gradient_map.grid(column = 0, row = 10, sticky = tk.W)

        separator2.grid(column = 0, row = 13, sticky = tk.W)
        if debug_setting == True:
            scissor_debug_label.grid(column = 0, row = 14, sticky = (tk.W,tk.N))
            scissor_debug2_label.grid(column = 0, row = 15, sticky = (tk.W,tk.N))

        #binding
        scissor_window.bind('<1>',lambda e : scissor_debug_label.configure(text = scissor_mode.get()))
        scissor_window.bind('<1>',lambda e : scissor_debug2_label.configure(text = brush_selection.get()))
        image_only.bind('<1>',show_image_only)
        image_with_contour.bind('<1>',show_image_with_contour)
        pixel_nodes.bind('<1>',show_pixel_nodes)
        cost_graph.bind('<1>',show_cost_graph)
        path_tree.bind('<1>',show_path_tree)
        minimum_path.bind('<1>',show_minimum_path)


def close_scissor_window():
    global scissor_window_exist
    scissor_window_exist = False
    scissor_window.destroy()

def close_brush_window():
    global brush_window_exist
    brush_window_exist = False
    brush_window.destroy()

def close_help_window():
    global help_window_exist
    help_window_exist = False
    help_window.destroy()

def close_about_window():
    global about_window_exist
    about_window_exist = False
    about_window.destroy()


root = tk.Tk()
root.title('Intelligent Scissors by Lei & Hao HKUST COMP5421 Spring 2018')
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

#menu
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff = 0)
file_menu.add_command(label="Open Image", command = open_image)
file_menu.add_separator()
file_menu.add_command(label="Save Contour", command = save_contour)
file_menu.add_command(label="Save Mask", command = save_mask)
file_menu.add_separator()
file_menu.add_command(label="Exit", command = root.destroy)
menubar.add_cascade(label="File", menu=file_menu)

tools_menu = tk.Menu(menubar, tearoff = 0)
tools_menu.add_command(label = "Scissor", command = create_scissor_window)
if brush_implemented == True:
    tools_menu.add_command(label = "Brush", command = create_brush_window)
menubar.add_cascade(label="Tools", menu=tools_menu)

help_menu = tk.Menu(menubar, tearoff = 0)
help_menu.add_command(label = "Help", command = create_help_window)
help_menu.add_command(label = "About", command = create_about_window)
menubar.add_cascade(label="Help", menu=help_menu)

root.configure(menu = menubar)

#frame
mainframe = ttk.Frame(root,padding='3', borderwidth = '8')
#mainframe['relief'] = 'ridge'
mainframe.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

#define scroll bar
h = ttk.Scrollbar(mainframe, orient=tk.HORIZONTAL)
v = ttk.Scrollbar(mainframe, orient=tk.VERTICAL)

#canvas
canvas = tk.Canvas(mainframe, width=640, height=480, bg='white',scrollregion=(0, 0, 1920, 1080), yscrollcommand=v.set,xscrollcommand=h.set)
canvas.grid(column=0, row=0, columnspan = 4, rowspan = 4, sticky=(tk.N,tk.W,tk.E,tk.S))
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
h.grid(column=0, row=4, columnspan = 4, sticky=(tk.W,tk.E))
v.grid(column=4, row=0, rowspan = 4,  sticky=(tk.N,tk.S))

#button
#button_open_image = ttk.Button(mainframe, text = 'open image', command = open_image).grid(column=5,row=0, sticky=(tk.E,tk.N))

#size grip
ttk.Sizegrip(root).grid(column=1, row=1, sticky=(tk.S,tk.E))

#show cursor coornidate
cursor_label =ttk.Label(mainframe, text='x:0,y:0')
cursor_label.grid(column = 0, row = 5, sticky = (tk.W,tk.N))
canvas.bind('<Leave>', lambda e: cursor_label.configure(text='cursor outside canvas'))

#show other debug info
debug_label = ttk.Label(mainframe, text='<debug info>')
debug2_label = ttk.Label(mainframe, text='<debug2 info>')
debug3_label = ttk.Label(mainframe, text='<debug3 info>')



stack_label = ttk.Label(mainframe, text='<stack info>', wraplength = wrap_length, justify = 'left')

canvas_path_label = ttk.Label(mainframe, text='<canvas path info>', wraplength = wrap_length, justify = 'left')
canvas_path_stack_label = ttk.Label(mainframe, text='<canvas path stack info>', wraplength = wrap_length, justify = 'left')

min_path_label = ttk.Label(mainframe, text='<min path info>', wraplength = wrap_length, justify = 'left')
history_paths_label = ttk.Label(mainframe, text='<history paths info>', wraplength = wrap_length, justify = 'left')

if debug_setting == True:
    hover_mask_label = ttk.Label(mainframe, text='<hover_mask info>')
    debug_label.grid(column = 0, row = 9, sticky = (tk.W,tk.N))
    debug2_label.grid(column = 0, row = 6, sticky = (tk.W,tk.N))
    debug3_label.grid(column = 0, row = 7, sticky = (tk.W,tk.N))
    hover_mask_label.grid(column = 0, row = 8, sticky = (tk.W,tk.N))
    stack_label.grid(column = 0, row = 16, columnspan = 4, sticky = (tk.W,tk.N))
    canvas_path_label.grid(column = 0, row = 17, columnspan = 4, sticky = (tk.W,tk.N))
    canvas_path_stack_label.grid(column = 0, row = 18, columnspan = 4, sticky = (tk.W,tk.N))
    min_path_label.grid(column = 0, row = 19, columnspan = 4, sticky = (tk.W,tk.N))
    history_paths_label.grid(column = 0, row = 20, columnspan = 4, sticky = (tk.W,tk.N))


#Main function binding
canvas.bind('<Button-1>', click_xy)
canvas.bind('<Control-Button-1>', start)
root.bind('<Return>', finish)
root.bind('<BackSpace>', delete_path)
root.bind('<Control-Return>', close_contour_finish)
root.bind('<Control-a>', zoom_in)
root.bind('<Control-z>', zoom_out)
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

open_image()
create_scissor_window()
close_scissor_window()
scissor_mode.set('image_with_contour')


def close_root():
    print('close root window')
    delete_debug_pics()
    root.destroy()

root.protocol('WM_DELETE_WINDOW', close_root)
root.mainloop()

