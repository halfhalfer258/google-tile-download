# http://oregonarc.com/2011/02/command-line-tile-cutter-for-google-maps-improved/
# http://media.oregonarc.com/fish/tile.py
import os
os.environ['PROJ_LIB'] = r'D:\PYTHON\Lib\site-packages\osgeo\data\proj'  #系统中osgeo下的proj文件安装位置
os.environ['GDAL_DATA'] = r'D:\PYTHON\Lib\site-packages\osgeo\data'
from math import *
import math
import re
#废弃代码
# def geodistance(point_1,point_2):
#     #lng1,lat1,lng2,lat2 = (120.12802999999997,30.28708,115.86572000000001,28.7427)
#     lng1 , lat1 = point_1[0] , point_1[1]
#     lng2,lat2   = point_2[0] , point_2[1]
#     lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
#     dlon=lng2-lng1
#     dlat=lat2-lat1
#     a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#     distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
#     distance=round(distance/1000,3)
#     return distance
# def xyLength(min_lon,max_lon,min_lat,max_lat):
#     left_up = [min_lon , max_lat]
#     left_down = [min_lon , min_lat]
#     right_up = [max_lon , max_lat]
#     x_length = geodistance(left_up , right_up)
#     y_length = geodistance(left_up , left_down)
#     return x_length,y_length
# def dataArrToGeoTif(jpg_path ,  tif_path ,shp_path ,zoom):
#     '''
#     根据影像左上角经纬度给jpg文件定义地理坐标
#     :param jpg_path: 下载的影像文件
#     :param tif_path: 输出带地理坐标的影像文件位置
#     :param shp_path: 下载影像的shp坐标
#     :param zoom    : 缩放尺度
#     :return: None
#     '''
#     #获取shp文件的投影  直接定义为标准的Web 墨卡托
#     # shp_driver = ogr.GetDriverByName('ESRI Shapefile')
#     # data_source = shp_driver.Open(shp_path , 0)
#     # if data_source is None:
#     #     print("文件无法打开")
#     #     sys.exit(-1)
#     # layer = data_source.GetLayer(0)
#     # proje = layer.GetSpatialRef()
#     # temp_wtk = proje.ExportToWkt()
#     # temp_wtk = 'PROJCS["WGS_1984_Web_Mercator",GEOGCS["GCS_WGS_1984_Major_Auxiliary_Sphere",DATUM["D_WGS_1984_Major_Auxiliary_Sphere",SPHEROID["WGS_1984_Major_Auxiliary_Sphere",6378137.0,0.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.017453292519943295]],PROJECTION["Mercator"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["standard_parallel_1",0.0],UNIT["Meter",1.0]]'
#     # temp_wtk = 1
#     # del data_source
#     reads = readTif(jpg_path)
#     jpg_arr = reads[3]
#     min_lon,max_lon,min_lat,max_lat = outsourcingRectangle(shp_path)
#     writeTiff(jpg_arr , min_lon,max_lat,zoom,tif_path)

def resolution(z):
    return 20037508.3427892 * 2 / 256 / (2^z)
def m2Lon(num):
    '''
    将m单位转为十进制经度
    param  num:输入距离以m为单位
    '''
    lon = num * 360 / 31544206 
    return lon
def m2Lat(num):
    '''
    将m单位转为十进制经度
    param  num:输入距离以m为单位
    '''
    lat = num * 360 / 40030173 
    return lat
def lonlat2WebMerktor(lon,lat):
    '''
    经纬度转Web Merktor
    param  lat:维度
    param  lon:经度
    return    :Web Merktor 坐标
    '''
    x = lon * 20037508.342789/180
    y = math.log(math.tan((90+lat)*math.pi/360))/(math.pi/180)
    return x,y
def latlon2px(z,lat,lon):
    x = 2**z*(lon+180)/360*256
    y = -(.5*math.log((1+math.sin(math.radians(lat)))/(1-math.sin(math.radians(lat))))/math.pi-1)*256*2**(z-1)
    return x,y
def latlon2xy(z,lat,lon,left_top = False):
    '''
    经纬度转谷歌瓦片坐标
    '''
    x,y = latlon2px(z,lat,lon)
    if not left_top:#右下角向上取整
        x = math.ceil(x/256)+1#,int(x%256)
        y = math.ceil(y/256)+1#,int(y%256)
    else:           #左上角向下取整
        x = int(x/256) #,int(x%256)
        y = int(y/256) #,int(y%256)
    return x,y
def xy2latlon(z,x,y):
    '''
    谷歌瓦片坐标转经纬度
    '''
    lon = x/math.pow(2,z)*360-180
    n = math.pi - 2*math.pi*y/math.pow(2,z)
    lat = 180/math.pi*math.atan(0.5*(math.exp(n)-math.exp(-n)))
    return lon ,lat
def realLonLat2DownloadLonLat(zoom,min_lon,max_lon,min_lat,max_lat):
    '''
    输入经纬度转实际下载的经纬度
    '''
    start_x, start_y = latlon2xy(zoom, max_lat, min_lon,left_top=True)
    stop_x, stop_y = latlon2xy(zoom, min_lat, max_lon )

    left_top_download_x,left_top_download_y = xy2latlon(zoom ,start_x,start_y)
    right_down_download_x,right_down_download_y = xy2latlon(zoom ,stop_x, stop_y)

    return left_top_download_x,left_top_download_y,right_down_download_x,right_down_download_y


# 根据WGS-84 的经纬度获取谷歌地图中的瓦片坐标
def wgs84_to_tile(z,j, w):
    '''
    Get google-style tile cooridinate from geographical coordinate
    j : Longitude 
    w : Latitude
    z : zoom
    '''
    isnum = lambda x: isinstance(x, int) or isinstance(x, float)
    if not(isnum(j) and isnum(w)):
        raise TypeError("j and w must be int or float!")

    if not isinstance(z, int) or z < 0 or z > 22:
        raise TypeError("z must be int and between 0 to 22.")

    if j < 0:
        j = 180 + j
    else:
        j += 180
    j /= 360  # make j to (0,1)

    w = 85.0511287798 if w > 85.0511287798 else w
    w = -85.0511287798 if w < -85.0511287798 else w
    w = log(tan((90 + w) * pi / 360)) / (pi / 180)
    w /= 180  # make w to (-1,1)
    w = 1 - (w + 1) / 2  # make w to (0,1) and left top is 0-point

    num = 2**z
    x = floor(j * num)
    y = floor(w * num)
    return x, y

def degreeToDecimal(degree):
    '''
    度分秒转十进制
    '''
    longitude_split = re.split(u"°|\'|\"", degree)[:3]
    if len(longitude_split) == 3:
        x = [float(j) for j in longitude_split]
        decimal = x[0] + x[1] / 60 + x[2] / 3600
    return decimal

from osgeo import ogr
import sys
def outsourcingRectangle(shp_path):
    '''
    从shp文件找到最小外包矩形与start_lon,stop_lon,start_lat,stop_lat
    '''
    if shp_path.split('.')[-1] == "shp":
        key_word = "ESRI Shapefile"
    elif shp_path.split('.')[-1] == "kml":
        key_word = "KML"
    driver = ogr.GetDriverByName(key_word)
    data_source = driver.Open(shp_path , 0)
    if data_source is None:
        print("文件无法打开")
        sys.exit(-1)
    layer = data_source.GetLayer(0)
    #一个 shp 文件下可能有多个子shp，取最大lon , lat
    out_lon_lat = [0,0,0,0]
    max_lon =0 
    min_lon =999
    max_lat =0
    min_lat =999
    for feature in layer:
        geometry = feature.geometry()
        rectangle_now = geometry.GetEnvelope()
        
        if min_lon>rectangle_now[0]:
            min_lon = rectangle_now[0]
        if max_lon<rectangle_now[1]:
            max_lon = rectangle_now[1]
        if min_lat>rectangle_now[2]:
            min_lat = rectangle_now[2]
        if max_lat<rectangle_now[3]:
            max_lat = rectangle_now[3]           
        pass
    return min_lon,max_lon,min_lat,max_lat

from osgeo import gdal
from osgeo import osr
import numpy as np

def getSRSPair(wkt):
    '''
    获得给定数据的投影参考系和地理参考系
    :param wkt: wkt文件，用于定义投影
    :return: 投影参考系和地理参考系
    '''
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(wkt)
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs

def geo2lonlat(wkt, x, y):
    '''
    将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
    :param wkt: wkt文件，用于定义投影
    :param x: 投影坐标x
    :param y: 投影坐标y
    :return: 投影坐标(x, y)对应的经纬度坐标(lon, lat)
    '''
    prosrs, geosrs = getSRSPair(wkt)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]

def lonlat2geo(wkt, lon, lat):
    '''
    将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）
    :param wkt: wkt文件，用于定义投影
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度
    :return: 经纬度坐标(lon, lat)对应的投影坐标
    '''
    prosrs, geosrs = getSRSPair(wkt)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]

def imagexy2geo(dataset, row, col):
    '''
    根据GDAL的六参数模型将影像图上坐标（行列号）转为投影坐标或地理坐标（根据具体数据的坐标系统转换）
    :param dataset: GDAL地理数据
    :param row: 像素的行号
    :param col: 像素的列号
    :return: 行列号(row, col)对应的投影坐标或地理坐标(x, y)
    '''
    trans = dataset.GetGeoTransform()
    px = trans[0] + col * trans[1] + row * trans[2]
    py = trans[3] + col * trans[4] + row * trans[5]
    return px, py


def geo2imagexy(dataset, x, y):
    '''
    根据GDAL的六 参数模型将给定的投影或地理坐标转为影像图上坐标（行列号）
    :param dataset: GDAL地理数据
    :param x: 投影或地理坐标x
    :param y: 投影或地理坐标y
    :return: 影坐标或地理坐标(x, y)对应的影像图上行列号(row, col)
    '''
    trans = dataset.GetGeoTransform()
    a = np.array([[trans[1], trans[2]], [trans[4], trans[5]]])
    b = np.array([x - trans[0], y - trans[3]])
    return np.linalg.solve(a, b)  # 使用numpy的linalg.solve进行二元一次方程的求解


#  读取tif数据集
def readTif(fileName, xoff = 0, yoff = 0, data_width = 0, data_height = 0):
    '''
    依次返回:width, height, bands, data, geotrans, proj
    '''
    dataset = gdal.Open(fileName)
    if dataset == None:
        print(fileName + "文件无法打开")
    #  栅格矩阵的列数
    width = dataset.RasterXSize 
    #  栅格矩阵的行数
    height = dataset.RasterYSize 
    #  波段数
    bands = dataset.RasterCount 
    #  获取数据
    if(data_width == 0 and data_height == 0):
        data_width = width
        data_height = height
    data = dataset.ReadAsArray(xoff, yoff, data_width, data_height)
    #  获取仿射矩阵信息
    geotrans = dataset.GetGeoTransform()
    #  获取投影信息
    proj = dataset.GetProjection()
    return width, height, bands, data, geotrans, proj

#  保存tif文件函数
def writeTiff(im_data, min_lon,max_lat,zoom ,path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
        im_bands, im_height, im_width = im_data.shape
    # 计算6参数 定义投影系
    space_resolution_x = space_resolution_y = resolution(zoom)  #单位为m
    space_resolution_x = m2Lon(space_resolution_x)
    space_resolution_y = m2Lat(space_resolution_y)
    # space_resolution_x = space_resolution_y = 2

    # im_proj = proje_shp
    # wkt     = im_proj.ExportToWkt()
    temp_wtk = 'PROJCS["WGS_1984_Web_Mercator",GEOGCS["GCS_WGS_1984_Major_Auxiliary_Sphere",DATUM["D_WGS_1984_Major_Auxiliary_Sphere",SPHEROID["WGS_1984_Major_Auxiliary_Sphere",6378137.0,0.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.017453292519943295]],PROJECTION["Mercator"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["standard_parallel_1",0.0],UNIT["Meter",1.0]]'
    # temp_wtk = 1
    im_proj = osr.SpatialReference()
    im_proj.SetWellKnownGeogCS('EPSG:4326')#定义为WGS 84坐标系
    # utm_num = int(min_lon / 6) + 31      #投影带
    # im_proj.SetUTM(utm_num , True)
    wkt = im_proj
    
    # x ,y = lonlat2geo(wkt,min_lon,max_lat)
    # x,y=latlon2px(zoom , max_lat,min_lon)
    # x2,y2 = lonlat2geo(wkt , min_lon ,min_lat)
    x , y = min_lon , max_lat
    im_geotrans = [x , space_resolution_x , 0 ,y , space_resolution_y,0]

    #创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if(dataset!= None):
        dataset.SetGeoTransform(im_geotrans) #写入仿射变换参数
        dataset.SetProjection(wkt) #写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i+1).WriteArray(im_data[i])
    del dataset
    pass

import subprocess

def cmdProcessTest(src_file,tar_file,geo_code,ullr):
    '''
    通过gdal_translate与cmd,给图像定义坐标系
    param src_file :输入文件路径
    param tar_file :输出文件路径
    param geo_code :坐标系代码
    param ullr     :图像左上角与右下角经纬度
    '''
    
    gdal_translate = r"D:\PYTHON\Lib\site-packages\osgeo\gdal_translate.exe"
    
    if src_file[-4:] ==".jpg":
        file_type ="JPEG"
    elif src_file[-4:] ==".tif":
        file_type ="GTiff"
    # cmd_str        = "-of JPEG -a_srs EPSG:3857  -a_ullr 111.8908885 28.4891832 112.7791468 27.8831196"
    cmd_file_type ="-of " + file_type
    cmd_geo_code  ="-a_srs " + geo_code
    cmd_ullr      ="a_ullr " + ullr 
    cmd_str       =cmd_file_type + './' + cmd_geo_code +'./'+ cmd_ullr 
    
    temp_str ='D:\\PYTHON\\Lib\\site-packages\\osgeo\\gdal_translate.exe'+ \
    ' -of '+file_type+' -a_srs '+geo_code+' -a_ullr '+ullr+' '+src_file+' '+tar_file
    # os.system(temp_str)
    sub = subprocess.Popen(temp_str , shell=True)
    sub.wait()
    pass
from PIL import Image
import numpy as np
def dataArrToGeoTif(src_file ,  tar_file ,shp_path ,geo_code,zoom):
    '''
    根据影像左上角经纬度给jpg文件定义地理坐标
    :param src_file: 下载的影像文件
    :param tar_file: 输出带地理坐标的影像文件位置
    :param shp_path: 下载影像的shp坐标
    :param geo_code: 坐标系/投影 EPSG代码   修改代码后坐标计算方法也要修改,建议删了
    :param zoom    : 缩放尺度
    :return: None
    '''
    reads = readTif(src_file)
    jpg_arr = reads[3]
    min_lon,max_lon,min_lat,max_lat = outsourcingRectangle(shp_path)      #计算shp的经纬度坐标
    left_top_x,left_top_y,right_down_x,right_down_y = realLonLat2DownloadLonLat(zoom,min_lon,max_lon,min_lat,max_lat)#修改为下载的瓦片坐标
    web_x_left_top,web_y_left_top     = lonlat2WebMerktor(left_top_x,left_top_y)   #转为墨卡托投影
    web_x_right_down,web_y_right_down = lonlat2WebMerktor(right_down_x,right_down_y)
    web_x_left_top,web_y_left_top,web_x_right_down,web_y_right_down = left_top_x,left_top_y,right_down_x,right_down_y

    
    urrl_str = str(web_x_left_top)+' '+str(web_y_left_top)+' '+str(web_x_right_down)+' '+str(web_y_right_down)
    # geo_code = "EPSG:4326"
    tar_file_geo = "/".join(tar_file.split('/')[:-1]) + '/'+geo_code.split(':')[-1]+'_' + tar_file.split('/')[-1]
    cmdProcessTest(src_file ,tar_file_geo , geo_code,urrl_str)



if __name__ == "__main__":
    test_path =r"E:\DATA2021\StudyArea\Ext\NX.shp"
    # final = outsourcingRectangle(test_path)

    img_test =r"E:\DATA2021\GEHistory\Py\merge\10_map_x_830_to_832_y_427_to_429img_s.jpg"
    out_tif_path =r"E:\DATA2021\GEHistory\Py\merge\test.tif"
    # zoom = img_test.split("")
    src_file       = r"E:\DATA2021\GEHistory\Py\merge\10_map_x_830_to_832_y_427_to_429img_s.jpg"
    tar_file       = r"E:\DATA2021\GEHistory\Py\merge\geo_test.tif"
    zoom = 10

    cmdProcessTest(src_file ,tar_file , "EPSG:3857","111.8908885 28.4891832 112.7791468 27.8831196")
    # dataArrToGeoTif(r"E:\DATA2021\GEHistory\Py\merge\meta_merge\15satellite_x_26568_to_26651_y_13676_to_13741_s.jpg")
    # dataArrToGeoTif(img_test ,out_tif_path, test_path ,zoom)
    dataSet = gdal.Open(img_test)
    pass