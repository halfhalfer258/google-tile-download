from fileinput import filename
from PIL import Image
import sys, os
from gmap_utils import *

def merge_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, bytes_type=None):
    type_dir = {'s': "satellite" , 'y':"satellite_label" , 'm':"map"}
    part_of_name = type_dir[bytes_type]
    if bytes_type is "s":
        TYPE, ext = 's', 'jpg'  #TODO 改为存PNG
    elif bytes_type is "m":
        TYPE, ext = 'm', 'png' 
    elif bytes_type is "y":
        TYPE, ext = 'y', 'jpg' 
    start_x, start_y = latlon2xy(zoom, lat_start, lon_stop)
    stop_x, stop_y = latlon2xy(zoom, lat_stop, lon_start ,left_top=True)
    
    if start_x>stop_x:
        start_x,stop_x = stop_x,start_x
    if start_y>stop_y:
        start_y,stop_y=stop_y,start_y

    print("x range", start_x, stop_x)
    print ("y range", start_y, stop_y)
    
    w = (stop_x - start_x) * 256
    h = (stop_y - start_y) * 256
    
    print ("width:", w)
    print ("height:", h)
    
    result = Image.new("RGB", (w, h))
    
    for x in range(start_x, stop_x):
        for y in range(start_y, stop_y):
            
            file_path = os.getcwd() +'/data/' +'_'+part_of_name+'_z' + str(zoom) +"_x_%d_to_%d_y_%d_to_%d"%(start_x,stop_x,start_y,stop_y) 
            filename = file_path + '/' + "%d_%d_%d_%s.%s" % (zoom, x, y, TYPE, ext)
            # '/'+ "%d_%d_%d_%s.%s" % (zoom, x, y, TYPE, ext)
            
            if not os.path.exists(filename):
                print ("-- missing", filename)
                continue
                    
            x_paste = (x - start_x) * 256
            y_paste = h - (stop_y - y) * 256
            
            try:
                i = Image.open(filename)
            except Exception as e:
                print ("-- %s, removing %s" % (e, filename))
                trash_dst = os.path.expanduser("~/.Trash/%s" % filename)
                os.rename(filename, trash_dst)
                continue
            
            result.paste(i, (x_paste, y_paste))
            
            del i
    save_filefolder = os.getcwd() + '/'+'merge'+'/meta_merge'
    if not os.path.exists(save_filefolder):
        os.makedirs(save_filefolder)
    # save_path = os.getcwd() + '/'+'merge'+'/'+str(zoom) + "_map_x_%d_to_%d_y_%d_to_%d_%s.%s" % (x_start,x_stop,y_start,y_stop,TYPE, ext)
    save_path = save_filefolder + '/'+str(zoom) +part_of_name+"_x_%d_to_%d_y_%d_to_%d_%s.%s"%(start_x,stop_x,start_y,stop_y,TYPE,ext)
    
    result.save(save_path)
    return(save_path)
if __name__ == "__main__":
    
    zoom = 20

    lat_start, lon_start = 28.182892, 112.096222
    lat_stop, lon_stop = 28.180114, 112.10135
    
    merge_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite=True)
