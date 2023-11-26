
'''
対象事業実施区域から2000mの範囲のMaxent用のパラメータをメッシュで作成するやつ。
作成されるパラメータは標高、傾斜角、斜面方位、TPI、林縁からの距離、半径250m内の草地面積


用意するもの
・2次メッシュ
・標高ラスター
・対象事業実施区域ポリゴン
・植生ポリゴン
・樹林のみポリゴン
・草地のみポリゴン

注：DEMは平面直角座標系やUTM座標系であること。

'''


# --------------以下を設定してください-------------------

# 2次メッシュは？
from datetime import datetime
import processing
import os
from qgis.PyQt.QtCore import QVariant
input1 = u'mesh2'

# 標高データは？
dem = "dem10"

# 対象事業実施区域は？
input2 = "sample_area"


# 植生データは？
input3 = "veg"
# 植生データの属性で環境類型区分のフィールド名は？
vegColName = "veg"

# 樹林のみのデータは？
input4 = "forest"

# 草地のみのデータは？
input5 = "grass"


# メッシュサイズ
meshsize = 100


# 出力ファイル名
Dir = ""
outputname = "mesh50_noheji2"

# 既にあるメッシュを使う時はそのレイヤ名を入力。新規にメッシュを作る場合は0、もしくは無記入にしておく。
input6 = ""


# ------------------------------------------------------


# 以下をすべてコピーしてPythonコンソールにて実行


starttime = datetime.now()


# Input_layer
input1 = QgsProject.instance().mapLayersByName(input1)[0]
inputdem = QgsProject.instance().mapLayersByName(dem)[0]
input2 = QgsProject.instance().mapLayersByName(input2)[0]
input3 = QgsProject.instance().mapLayersByName(input3)[0]
input4 = QgsProject.instance().mapLayersByName(input4)[0]
input5 = QgsProject.instance().mapLayersByName(input5)[0]


# ディレクトリの設定
if Dir == "":
    (Dir, filename) = os.path.split(input2.dataProvider().dataSourceUri())

#
os.mkdir(Dir + "/maxent_para")
os.chdir(Dir + "/maxent_para")


buffer = processing.run("native:buffer", {'INPUT': input2, 'DISTANCE': 2000, 'SEGMENTS': 100,
                                          'END_CAP_STYLE': 0, 'JOIN_STYLE': 0, 'MITER_LIMIT': 2, 'DISSOLVE': True, 'OUTPUT': 'memory:'})


if input6 == "0" or input6 == "":
    selectPlace = processing.run("native:selectbylocation", {
                                 'INPUT': input1, 'PREDICATE': [0], 'INTERSECT': buffer['OUTPUT'], 'METHOD': 0})
    select = processing.run("native:saveselectedfeatures", {
                            'INPUT': selectPlace['OUTPUT'], 'OUTPUT': 'memory:'})
    project = processing.run("native:reprojectlayer", {
                             'INPUT': select['OUTPUT'], 'TARGET_CRS': inputdem.crs().authid(), 'OUTPUT': 'memory:'})
    # getExtent
    box = project['OUTPUT'].extent()
    xmin = box.xMinimum()
    xmax = box.xMaximum()
    ymin = box.yMinimum()
    ymax = box.yMaximum()
    exta = str(xmin) + ',' + str(xmax) + ',' + str(ymin) + ',' + str(ymax)
    # Make mesh
    mesh = processing.run("qgis:creategrid", {'TYPE': 2, 'EXTENT': exta, 'HSPACING': meshsize, 'VSPACING': meshsize,
                                              'HOVERLAY': 0, 'VOVERLAY': 0, 'CRS': inputdem.crs().authid(), 'OUTPUT': 'memory:'})
    mesh1_1 = processing.run("qgis:fieldcalculator", {'INPUT': mesh['OUTPUT'], 'FIELD_NAME': 'PageNumber', 'FIELD_TYPE': 1,
                                                      'FIELD_LENGTH': 10, 'FIELD_PRECISION': 3, 'NEW_FIELD': True, 'FORMULA': ' @row_number ', 'OUTPUT': 'memory:'})
    mesh1_2 = processing.run("qgis:fieldcalculator", {'INPUT': mesh1_1['OUTPUT'], 'FIELD_NAME': 'X', 'FIELD_TYPE': 0,
                                                      'FIELD_LENGTH': 20, 'FIELD_PRECISION': 10, 'NEW_FIELD': True, 'FORMULA': ' x(centroid($geometry)) ', 'OUTPUT': 'memory:'})
    mesh2 = processing.run("qgis:fieldcalculator", {'INPUT': mesh1_2['OUTPUT'], 'FIELD_NAME': 'Y', 'FIELD_TYPE': 0,
                                                    'FIELD_LENGTH': 20, 'FIELD_PRECISION': 10, 'NEW_FIELD': True, 'FORMULA': ' y(centroid($geometry)) ', 'OUTPUT': 'memory:'})

else:
    input6 = QgsProject.instance().mapLayersByName(input6)[0]
    mesh1_1 = processing.run("qgis:fieldcalculator", {'INPUT': input6, 'FIELD_NAME': 'PageNumber', 'FIELD_TYPE': 1,
                                                      'FIELD_LENGTH': 10, 'FIELD_PRECISION': 3, 'NEW_FIELD': True, 'FORMULA': ' @row_number ', 'OUTPUT': 'memory:'})
    mesh1_2 = processing.run("qgis:fieldcalculator", {'INPUT': mesh1_1['OUTPUT'], 'FIELD_NAME': 'X', 'FIELD_TYPE': 0,
                                                      'FIELD_LENGTH': 20, 'FIELD_PRECISION': 10, 'NEW_FIELD': True, 'FORMULA': ' x(centroid($geometry)) ', 'OUTPUT': 'memory:'})
    mesh2 = processing.run("qgis:fieldcalculator", {'INPUT': mesh1_2['OUTPUT'], 'FIELD_NAME': 'Y', 'FIELD_TYPE': 0,
                                                    'FIELD_LENGTH': 20, 'FIELD_PRECISION': 10, 'NEW_FIELD': True, 'FORMULA': ' y(centroid($geometry)) ', 'OUTPUT': 'memory:'})
    # getExtent
    box = mesh2['OUTPUT'].extent()
    xmin = box.xMinimum()
    xmax = box.xMaximum()
    ymin = box.yMinimum()
    ymax = box.yMaximum()
    exta = str(xmin) + ',' + str(xmax) + ',' + str(ymin) + ',' + str(ymax)


# clipDEM
DEMclip = processing.run("gdal:cliprasterbymasklayer", {
                         'INPUT': inputdem, 'MASK': buffer['OUTPUT'], 'NODATA': None, 'ALPHA_BAND': True, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': False, 'OPTIONS': '', 'DATA_TYPE': 0, 'OUTPUT': 'DEMclip.tif'})


# DEM2Point
DEMpoint = processing.run("native:pixelstopoints", {
                          'INPUT_RASTER': DEMclip['OUTPUT'], 'RASTER_BAND': 1, 'FIELD_NAME': 'DEM', 'OUTPUT': 'memory:'})


# join DEM to mesh
selectmesh = processing.run("native:selectbylocation", {
                            'INPUT': mesh2['OUTPUT'], 'PREDICATE': [0], 'INTERSECT': buffer['OUTPUT'], 'METHOD': 0})
select2 = processing.run("native:saveselectedfeatures", {
                         'INPUT': selectmesh['OUTPUT'], 'OUTPUT': 'memory:'})
mesh2 = processing.run("qgis:joinbylocationsummary", {'INPUT': select2['OUTPUT'], 'JOIN': DEMpoint['OUTPUT'], 'PREDICATE': [
                       0], 'JOIN_FIELDS': ['DEM'], 'SUMMARIES': [6], 'DISCARD_NONMATCHING': False, 'OUTPUT': 'memory:'})


# slope(中央値）
slope2 = processing.run("gdal:slope", {'INPUT': DEMclip['OUTPUT'], 'BAND': 1, 'SCALE': 1, 'AS_PERCENT': False,
                                       'COMPUTE_EDGES': False, 'ZEVENBERGEN': False, 'OPTIONS': '', 'OUTPUT': 'slope.tif'})
slopepoint = processing.run("native:pixelstopoints", {
                            'INPUT_RASTER': slope2['OUTPUT'], 'RASTER_BAND': 1, 'FIELD_NAME': 'slope', 'OUTPUT': 'memory:'})
mesh3 = processing.run("qgis:joinbylocationsummary", {'INPUT': mesh2['OUTPUT'], 'JOIN': slopepoint['OUTPUT'], 'PREDICATE': [
                       0], 'JOIN_FIELDS': ['slope'], 'SUMMARIES': [7], 'DISCARD_NONMATCHING': False, 'OUTPUT': 'memory:'})

# 斜面方位(最頻値)
aspect2 = processing.run("gdal:aspect", {'INPUT': DEMclip['OUTPUT'], 'BAND': 1, 'TRIG_ANGLE': False,
                                         'ZERO_FLAT': False, 'COMPUTE_EDGES': False, 'ZEVENBERGEN': False, 'OPTIONS': '', 'OUTPUT': 'aspect.tif'})
aspectpoint = processing.run("native:pixelstopoints", {
                             'INPUT_RASTER': aspect2['OUTPUT'], 'RASTER_BAND': 1, 'FIELD_NAME': 'aspect', 'OUTPUT': 'memory:'})
mesh4 = processing.run("qgis:joinbylocationsummary", {'INPUT': mesh3['OUTPUT'], 'JOIN': aspectpoint['OUTPUT'], 'PREDICATE': [
                       0], 'JOIN_FIELDS': ['aspect'], 'SUMMARIES': [10], 'DISCARD_NONMATCHING': False, 'OUTPUT': 'memory:'})

# TPI
tpi2 = processing.run("gdal:tpitopographicpositionindex", {
                      'INPUT': DEMclip['OUTPUT'], 'BAND': 1, 'COMPUTE_EDGES': False, 'OPTIONS': '', 'OUTPUT': 'tpi.tif'})
tpipoint = processing.run("native:pixelstopoints", {
                          'INPUT_RASTER': tpi2['OUTPUT'], 'RASTER_BAND': 1, 'FIELD_NAME': 'tpi', 'OUTPUT': 'memory:'})
mesh5 = processing.run("qgis:joinbylocationsummary", {'INPUT': mesh4['OUTPUT'], 'JOIN': tpipoint['OUTPUT'], 'PREDICATE': [
                       0], 'JOIN_FIELDS': ['tpi'], 'SUMMARIES': [7], 'DISCARD_NONMATCHING': False, 'OUTPUT': 'memory:'})


'''
# 任意セルサイズの標高ラスター作成
DEM_resize = processing.run("gdal:rasterize", {'INPUT':mesh2['OUTPUT'],'FIELD':'DEM_mean','BURN':0,'UNITS':1,'WIDTH':meshsize,
                            'HEIGHT':meshsize,'EXTENT':exta,'NODATA':0,'OPTIONS':'','DATA_TYPE':5,'INIT':0,'INVERT':False,'OUTPUT':'DEM' + str(meshsize) + '.tif'})


250mメッシュ標高から作る場合
# メッシュの中心点のポイント作成
gridPoint = processing.run("qgis:regularpoints", {'EXTENT':exta,'SPACING':meshsize,'INSET':meshsize/2,
                           'RANDOMIZE':False,'IS_SPACING':True,'CRS':inputdem.crs().authid(),'OUTPUT':'memory:'})


# slope
slope2 = processing.run("gdal:slope", {'INPUT':DEM_resize['OUTPUT'],'BAND':1,'SCALE':1,'AS_PERCENT':False,
                        'COMPUTE_EDGES':False,'ZEVENBERGEN':False,'OPTIONS':'','OUTPUT':'slope' + str(meshsize) + '.tif'})
gridPoint2 = processing.run("qgis:rastersampling", {
                            'INPUT':gridPoint['OUTPUT'],'RASTERCOPY':slope2['OUTPUT'],'COLUMN_PREFIX':'Slope','OUTPUT':'memory:'})

# aspect
aspect2 = processing.run("gdal:aspect", {'INPUT':DEM_resize['OUTPUT'],'BAND':1,'TRIG_ANGLE':False,'ZERO_FLAT':False,
                         'COMPUTE_EDGES':False,'ZEVENBERGEN':False,'OPTIONS':'','OUTPUT':'aspect' + str(meshsize) + '.tif'})
gridPoint3 = processing.run("qgis:rastersampling", {
                            'INPUT':gridPoint2['OUTPUT'],'RASTERCOPY':aspect2['OUTPUT'],'COLUMN_PREFIX':'Aspect','OUTPUT':'memory:'})


# tpi
tpi2 = processing.run("gdal:tpitopographicpositionindex", {
                      'INPUT':DEM_resize['OUTPUT'],'BAND':1,'COMPUTE_EDGES':False,'OPTIONS':'','OUTPUT':'tpi' + str(meshsize) + '.tif'})
gridPoint4 = processing.run("qgis:rastersampling", {
                            'INPUT':gridPoint3['OUTPUT'],'RASTERCOPY':tpi2['OUTPUT'],'COLUMN_PREFIX':'TPI','OUTPUT':'memory:'})
'''


# 空間結合し、植生フィールド作成
spJoin2 = processing.run("qgis:addfieldtoattributestable", {
                         'INPUT': mesh5['OUTPUT'], 'FIELD_NAME': 'mainVeg', 'FIELD_TYPE': 2, 'FIELD_LENGTH': 50, 'FIELD_PRECISION': 0, 'OUTPUT': 'memory:'})


# 植生インターセクト--------------------


intersect = processing.run("native:intersection", {
                           'INPUT': mesh2['OUTPUT'], 'OVERLAY': input3, 'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [], 'OUTPUT': 'memory:'})
# あとでrunにする
intersect2 = processing.runAndLoadResults("qgis:fieldcalculator", {
                                          'INPUT': intersect['OUTPUT'], 'FIELD_NAME': 'area', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 20, 'FIELD_PRECISION': 10, 'NEW_FIELD': True, 'FORMULA': '$area/10000', 'OUTPUT': 'intersectionVeg.shp'})


# 植生ディゾルブ

dissolvedVeg = processing.run("native:aggregate", {'INPUT': intersect2['OUTPUT'], 'GROUP_BY': 'Array( \"PageNumber\" , \"' + vegColName + '\" )', 'AGGREGATES': [{'aggregate': 'first_value', 'delimiter': ',', 'input': '\"PageNumber\"', 'length': 10, 'name': 'PageNumber', 'precision': 0, 'type': 4}, {
                              'aggregate': 'first_value', 'delimiter': ',', 'input': '\"' + vegColName + '\"', 'length': 20, 'name': 'veg', 'precision': 0, 'type': 10}, {'aggregate': 'sum', 'delimiter': ',', 'input': '\"area\"', 'length': 20, 'name': 'area', 'precision': 10, 'type': 6}], 'OUTPUT': 'TEMPORARY_OUTPUT'})

# QgsProject.instance().addMapLayer(dissolvedVeg['OUTPUT'])


# 最大面積の植生を取得
# meshデータのフィーチャを1つずつ選択して、反復処理
#edit_layer = spJoin2['OUTPUT']


for feature in spJoin2['OUTPUT'].getFeatures():
    pageNum = feature['PageNumber']
    print(pageNum)
    # selectedpolygon = ディソルブポリゴンから、該当するpagenumberのポリゴンだけを抽出
    expression = '"PageNumber" =  \'' + str(pageNum) + '\''
    request = QgsFeatureRequest().setFilterExpression(expression)
    #selectedpolygon = processing.run("qgis:selectbyattribute", {'INPUT': dissolvedVeg['OUTPUT'], 'FIELD': 'PageNumber', 'OPERATOR': 0, 'VALUE': pageNum, 'METHOD': 0})
    # Make veg and area dictionary
    veg_dict = {}
    for veg_feature in dissolvedVeg['OUTPUT'].getFeatures(request):
        veg_dict[veg_feature['veg']] = veg_feature['area']
    # find max area veg
    max_veg = max(veg_dict, key=veg_dict.get)
    # edit_layer.dataProvider().changeAttributeValues({QgsFeatureId:{fieldindex:"updateTest"}})
    new_value = {feature.fieldNameIndex("mainVeg"): max_veg}
    spJoin2['OUTPUT'].dataProvider().changeAttributeValues({
        feature.id(): new_value})


# 林縁----------------

# 中心点
centerPoint = processing.run("native:centroids", {
                             'INPUT': mesh2['OUTPUT'], 'ALL_PARTS': False, 'OUTPUT': 'memory:'})


# 樹林のディゾルブ
disso = processing.run("native:dissolve", {
                       'INPUT': input4, 'FIELD': [], 'OUTPUT': 'memory:'})


# 頂点の抽出
node = processing.run("native:extractvertices", {
                      'INPUT': disso['OUTPUT'], 'OUTPUT': 'memory:'})
node2 = processing.run("qgis:fieldcalculator", {'INPUT': node['OUTPUT'], 'FIELD_NAME': 'TEMPname', 'FIELD_TYPE': 2,
                                                'FIELD_LENGTH': 80, 'FIELD_PRECISION': 3, 'NEW_FIELD': True, 'FORMULA': '\'distance\'', 'OUTPUT': 'memory:'})

# 距離マトリックス
matrix = processing.run("qgis:distancematrix", {'INPUT': centerPoint['OUTPUT'], 'INPUT_FIELD': 'PageNumber',
                                                'TARGET': node2['OUTPUT'], 'TARGET_FIELD': 'TEMPname', 'MATRIX_TYPE': 2, 'NEAREST_POINTS': 1, 'OUTPUT': 'rinen.shp'})
matrix2 = processing.run("qgis:fieldcalculator", {'INPUT': matrix['OUTPUT'], 'FIELD_NAME': 'rinen', 'FIELD_TYPE': 0,
                                                  'FIELD_LENGTH': 20, 'FIELD_PRECISION': 10, 'NEW_FIELD': True, 'FORMULA': '\"MIN\"', 'OUTPUT': 'memory:'})


# 林内の抽出
rinnai1 = processing.run("native:selectbylocation", {
                         'INPUT': matrix2['OUTPUT'], 'PREDICATE': [0], 'INTERSECT': input4, 'METHOD': 0})
rinnai2 = processing.run("native:saveselectedfeatures", {
                         'INPUT': rinnai1['OUTPUT'], 'OUTPUT': 'memory:'})
rinnai3 = processing.run("qgis:fieldcalculator", {'INPUT': rinnai2['OUTPUT'], 'FIELD_NAME': 'rinen', 'FIELD_TYPE': 0,
                                                  'FIELD_LENGTH': 10, 'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': ' \"rinen\" *-1', 'OUTPUT': 'memory:'})

# 林外の抽出
matrix2['OUTPUT'].selectAll()
ringai1 = processing.run("native:selectbylocation", {
                         'INPUT': matrix2['OUTPUT'], 'PREDICATE': [0], 'INTERSECT': input4, 'METHOD': 3})
ringai2 = processing.run("native:saveselectedfeatures", {
                         'INPUT': ringai1['OUTPUT'], 'OUTPUT': 'memory:'})
# 林の内外のマージ
merge_rinen = processing.run("native:mergevectorlayers", {'LAYERS': [
                             rinnai3['OUTPUT'], ringai2['OUTPUT']], 'CRS': input4.crs().authid(), 'OUTPUT': 'memory:'})


# 結合
Join3 = processing.run("native:joinattributestable", {'INPUT': spJoin2['OUTPUT'], 'FIELD': 'PageNumber', 'INPUT_2': merge_rinen['OUTPUT'], 'FIELD_2': 'InputID', 'FIELDS_TO_COPY': [
                       'rinen'], 'METHOD': 1, 'DISCARD_NONMATCHING': False, 'PREFIX': '', 'OUTPUT': 'memory:'})


# 草地250----------------

buffer250 = processing.run("native:buffer", {'INPUT': centerPoint['OUTPUT'], 'DISTANCE': 250, 'SEGMENTS': 100,
                                             'END_CAP_STYLE': 0, 'JOIN_STYLE': 0, 'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': 'memory:'})
intersect3 = processing.run("native:intersection", {
                            'INPUT': buffer250['OUTPUT'], 'OVERLAY': input5, 'INPUT_FIELDS': [], 'OVERLAY_FIELDS': [], 'OUTPUT': 'memory:'})
dissolve = processing.run("native:dissolve", {
                          'INPUT': intersect3['OUTPUT'], 'FIELD': ['PageNumber'], 'OUTPUT': 'memory:'})
grass = processing.run("qgis:fieldcalculator", {'INPUT': dissolve['OUTPUT'], 'FIELD_NAME': 'grass250', 'FIELD_TYPE': 0,
                                                'FIELD_LENGTH': 20, 'FIELD_PRECISION': 10, 'NEW_FIELD': True, 'FORMULA': '$area/10000', 'OUTPUT': 'Grass250.shp'})

# 結合
Join4 = processing.run("native:joinattributestable", {'INPUT': Join3['OUTPUT'], 'FIELD': 'PageNumber', 'INPUT_2': grass['OUTPUT'], 'FIELD_2': 'PageNumber', 'FIELDS_TO_COPY': [
                       'grass250'], 'METHOD': 1, 'DISCARD_NONMATCHING': False, 'PREFIX': '', 'OUTPUT': outputname + '.shp'})


# 終了
iface.addVectorLayer(outputname + '.shp', "できたやつ", "ogr")


print("開始時刻" + str(starttime))
print("終了時刻" + str(datetime.now()))
