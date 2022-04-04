#!/usr/bin/python

# import urllib

import os, sys, argparse

from urllib.request import ProxyHandler,build_opener
import requests
import random

from gmap_utils import *
# from urllib import request
import random
#进度条封装
from tqdm import trange
import eventlet
import enlighten
def download_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, proxy=None,bytes_type=None):
    
    type_dir = {'s': "satellite" , 'y':"satellite_label" , 'm':"map"}
    part_of_name = type_dir[bytes_type]
    start_x, start_y = latlon2xy(zoom, lat_start, lon_stop)
    stop_x, stop_y = latlon2xy(zoom, lat_stop, lon_start ,left_top=True)
    #TEST
    left_top_x,left_top_y = xy2latlon(zoom , stop_x,stop_y)
    right_down_x,right_down_y = xy2latlon(zoom , start_x, start_y)
    #可能 参数输入的Start和Stop写反，  做可能的修正
    if start_x>stop_x:
        start_x,stop_x = stop_x,start_x
    if start_y>stop_y:
        start_y,stop_y=stop_y,start_y
    
    print ("x range", start_x, stop_x)
    print ("y range", start_y, stop_y)
    total_num = (stop_x-start_x) * (stop_y-start_y)
    print("total : %d"%(total_num))


    proxy_handler = ProxyHandler(
        {
        'http':'http://' + proxy,
        'https':'https://'+ proxy
        }
    )
    cwd = os.getcwd()
    dirname = cwd + '/' + 'data' + '/'+'_'+part_of_name+'_z' + str(zoom) + "_x_%d_to_%d_y_%d_to_%d"%(start_x,stop_x,start_y,stop_y)
    try:
        if not os.path.exists(dirname):
            os.mkdir(dirname)
    except: 
        print("没有创建保存文件夹，程序结束")
        sys.exit(1)
        pass
    retry_num =0
    time_limit = 5 #单个瓦片限制时间下载，超出则重新请求重新下载
    bar_mananger= enlighten.get_manager()
    total = bar_mananger.counter(total = total_num , desc="Total" , color="red")
    # single =bar_mananger.counter(total = row_num , desc="Single" , color="blue")
    # for x in trange(start_x, stop_x + 1 ,desc='1st loop',miniters=5):
  
    for x in range(start_x, stop_x + 1):
        # for y in trange(start_y, stop_y,desc='2st loop'):
        y=start_y
        print_y = 0
        print_stop_y = stop_y-start_y
        eventlet.monkey_patch(time=True)
       
        
        # while(y<=stop_y): 
        # while print_y in trange(print_stop_y ,desc='2st loop',mininterval=2):#leave=bool(x==stop_x) 
        with eventlet.Timeout(time_limit , False):
            while print_y in range(print_stop_y):
                
                total.update() #bar update
                y =print_y + start_y
                url = None
                filename = None

                #生成随机 header 与 目标服务器
                # 收集到的常用Header
                my_headers = [
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
                "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
                'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
                'Opera/9.25 (Windows NT 5.1; U; en)',
                'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
                'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
                "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
                "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
                'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1'
                ]
                sever_num = [1 ,2 ,3] #随机访问一个服务器
                head = random.choice(my_headers) #随机伪装一个浏览器
                sever_now = random.choice(sever_num)

                if bytes_type == 's':        
                    # url = "http://khm1.google.com/kh?v=87&hl=en&x=%d&y=%d&z=%d" % (x, y, zoom)
                    url = "http://mt%d.google.com/vt/lyrs=s@162000000&hl=zh-CN&x=%d&s=&y=%d&z=%d" % (sever_now,x, y, zoom)
                    filename = "%d_%d_%d_s.jpg" % (zoom, x, y)
                elif bytes_type == 'm':
                    url = "http://mt%d.google.com/vt/lyrs=m@162000000&hl=cn&x=%d&s=&y=%d&z=%d" % (sever_now,x, y, zoom)
                    filename = "%d_%d_%d_m.png" % (zoom, x, y)   
                elif bytes_type == 'y' :
                    url = "http://mt%d.google.com/vt/lyrs=y@162000000&hl=cn&x=%d&s=&y=%d&z=%d" % (sever_now,x, y, zoom)
                    filename = "%d_%d_%d_y.jpg" % (zoom, x, y) 
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                if os.path.exists(dirname + '/' + filename): #文件重复时跳过下载
                    # print("Exist and Jump" + ":" +  filename)
                    print_y= print_y + 1
                    start_flag = False
                    continue
    
                bytes = None
                
                time_out = eventlet.Timeout(time_limit)
                retry_limit = 9999
                try:
                    # print(url)
                    # req = request.Request(url , data = None ,headers = headers)
                    # response = request.urlopen(req)
                    # with eventlet.Timeout
                
                    opener = build_opener(proxy_handler)
                    opener.add_handler = [('User-agent', head)]
                    response = opener.open(url,timeout=5)
                    bytes = response.read()

                except requests.Timeout as t:
                    retry_num = retry_num + 1
                    
                    if t is not time_out:
                        print("--", filename,"->", t,"_RetryTimes:",retry_num)
                    else:
                        print("-- 单个瓦片超时,重新下载_RetryTimes:%d"%retry_num)
                    if retry_num>retry_limit:
                        sys.exit(1)
                    else:
                        print_y = print_y-1
                    continue
                except Exception as e:
                    time_out.cancel()
                    print("--", filename,"->", e,"_RetryTimes:",retry_num)
                    retry_num = retry_num + 1
                    if retry_num>retry_limit:
                        sys.exit(1)
                    else:
                        print_y = print_y-1
                    continue
                finally :
                    time_out.cancel()
                
                
                f = open(dirname + '/' + filename,'wb')
                f.write(bytes)
                f.close()
                
                
                # time.sleep(1 + random.random())
                print_y = print_y +1
                # single.update() #bar update
                # if print_y == print_stop_y - 1:
                #     single.clear()
                
    total.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Prossess our agruments')
    parser.add_argument('--lat_start', type=float, default=28.182892,nargs=1, help='The starting latitude point')
    parser.add_argument('--lat_stop', type=float, default=28.180114,nargs=1, help='The ending latitude point')
    parser.add_argument('--lon_start', type=float, default=112.096222,nargs=1, help='The starting longitude point')
    parser.add_argument('--lon_stop', type=float, default=112.10135,nargs=1, help='The ending longitude point')
    parser.add_argument('--shp_path' , type=str, default=r"E:\DATA2021\GEHistory\Py\xiantao.kml",help='Download by shp area')
    parser.add_argument('--zoom', type=int, default=18, help='The zoom level to download')
    # parser.add_argument('--satellite', type=bool, nargs=1, help='Download satellite imagery or maps?')
    parser.add_argument('--proxy' , type=str,default='127.0.0.1:1080',help='SSR local Server : local port')
    parser.add_argument('--img_type' , type=str,default='s',help='file type of download bytes')

    args = parser.parse_args()
    # if args.lat_start is None \
    #      or args.lat_stop is None \
    #      or args.lon_start is None \
    #      or args.lon_stop is None:
    #TEST 
    # args.shp_path = r"E:\DATA2021\StudyArea\Ext\NX.shp"
    # args.shp_path = r"E:\DATA2021\GEHistory\Py\xiantao.kml"
    if args.shp_path is not None:
        lon_start , lon_stop,lat_start,lat_stop = outsourcingRectangle(args.shp_path)
    else:
        # print('NOTICE: one of the latitude or longitude arguments was not found') 
        # print('using the default arguments')
        print("未输入shp范围,将按默认范围下载数据")
        lat_start, lon_start = 46.53, 6.6
        lat_stop, lon_stop = 46.49, 6.7
    
    if args.zoom is None:
        print('NOTICE: zoom was not found, using the default zoom value of 15')
        zoom = 15
    else:
        zoom = args.zoom
    # lat_start, lon_start = 46.53, 6.6
    # lat_stop, lon_stop = 46.49, 6.7
    proxy_xinjie = args.proxy  #本地代理服务器与端口设置
    
    img_type = args.img_type
    bytes_type = img_type
    print("Extent : Latitude from %f to %f ,Longitude from %f to %f" % (lat_start,lat_stop,lon_start,lon_stop))
    #下载影像
    download_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, proxy=proxy_xinjie,bytes_type=img_type)

    from merge_tiles import merge_tiles
    mergefile_path = merge_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop,bytes_type=img_type)
    #geo 数据保存路径
    geo_data_path  = '/'.join(mergefile_path.split('/')[:-2]) + '/' + "geo_merge"
    if not os.path.exists(geo_data_path):
        os.mkdir(geo_data_path)
    geo_name =  '/'+ 'Geo_' + mergefile_path.split('/')[-1].split('.')[0] + ".tif"  #带坐标数据保存位置
    geo_save = geo_data_path + geo_name
    geo_code = "EPSG:4326"
    dataArrToGeoTif(mergefile_path,geo_save,args.shp_path,geo_code,zoom)