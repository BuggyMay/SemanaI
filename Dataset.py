import os
from pathlib import Path
import re
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import pandas as pd
import glob


def returnElllipseListFiles(path):
    return [str(f) for f in Path(path).glob('**/*-ellipseList.txt')]

def transformCoordinates(st, wmax, hmax):
    "esta funcion debe ser completada por los alumnos"
    lista = st.split(" ")
    maxis, minaxis = float(lista[0]), float(lista[1])
    angle = float(lista[2])
    # width = int(np.abs(np.cos(angle)) * maxis * 2) 
    # height = int(np.abs(np.cos(angle + np.deg2rad(90))) * minaxis * 2)
    width =  int(math.cos(angle*math.pi/180.0 ) * minaxis) *2
    height =  int(math.sin(angle*math.pi/180.0 + 90.0) * maxis) *2

    x = int(float(lista[3])) - width/2
    y = int(float(lista[4])) - height/2

    if x < 0:
        width = width - abs(x)
        x = max(0, x) 
    elif x + width > wmax:
        width = min( wmax-abs(x) ,width ) -1
        x = min(wmax , x)

    if y < 0:
        height = height - abs(y)
        y = max(0, y)
    elif y + height > hmax:
        height = min( hmax-abs(y) ,height ) -1
        y = min(hmax , y) - 1 

    return (int(x), int(y), width, height)


def generateArray(old_file):
    "esta funcion debe ser completada por los alumnos"
    with open(old_file, "r") as f:
        arr = f.readlines()
        
    rg = re.compile("(\d)*_(\d)*_(\d)*_big")

    output = []

    arr_len = len(arr)
    i = 0
    while i != arr_len:
        val = arr[i].rstrip('\n')
        # print(val)
        mtch = rg.match(val)
        jumps = 0
        if mtch:
            try:
                val = "{}.jpg".format(val)
                # verifies if the image exists
                img = mpimg.imread(os.path.join("dataset", val))
                (h, w, _) = img.shape
                
                # fig,ax = plt.subplots(1)
                # ax.imshow(img)
                di = dict()
                di["name"] = val
                jumps = int(arr[i+1].rstrip('\n'))
                origin = i+2
                temp = []
                for j in range(origin, origin+jumps):
                    coords = arr[j].rstrip("\n")
                    rec = transformCoordinates(coords, w, h)
                    temp.append(rec)

                    # rect = patches.Rectangle((rec[0],rec[1]),rec[2],rec[3],linewidth=1,edgecolor='r',facecolor='none')
                    # ax.add_patch(rect)
                
                # plt.show()
                di["annotations"] = temp
                di["size"] = { "height" : h, "width" : w }
                output.append(di)
                i = jumps + origin
            except:
                print("{} not found...".format(val))
                i+=1
        else:
            i+=1
    return output
        


def changePandasExtension(row):
    return row.replace(".jpg", ".xml")

def pdToXml(name, coordinates, size, img_folder):
    xml = ['<annotation>']
    xml.append("    <folder>{}</folder>".format(img_folder))
    xml.append("    <filename>{}</filename>".format(name))
    xml.append("    <source>")
    xml.append("        <database>Unknown</database>")
    xml.append("    </source>")
    xml.append("    <size>")
    xml.append("        <width>{}</width>".format(size["width"]))
    xml.append("        <height>{}</height>".format(size["height"]))
    xml.append("        <depth>3</depth>".format())
    xml.append("    </size>")
    xml.append("    <segmented>0</segmented>")

    for field in coordinates:
        xmin, ymin = max(0,field[0]), max(0,field[1])
        xmax = min(size["width"], field[0]+field[2])
        ymax = min(size["height"], field[1]+field[3])

        xml.append("    <object>")
        xml.append("        <name>Face</name>")
        xml.append("        <pose>Unspecified</pose>")
        xml.append("        <truncated>0</truncated>")
        xml.append("        <difficult>0</difficult>")
        xml.append("        <bndbox>")
        xml.append("            <xmin>{}</xmin>".format(int(xmin)))
        xml.append("            <ymin>{}</ymin>".format(int(ymin)))
        xml.append("            <xmax>{}</xmax>".format(int(xmax)))
        xml.append("            <ymax>{}</ymax>".format(int(ymax)))
        xml.append("        </bndbox>")
        xml.append("    </object>")
    xml.append('</annotation>')
    return '\n'.join(xml)


def saveXmlToFile(name, file):
    with open(name, "w+") as f:
        f.write(file)


folder = glob.glob("dataset/*.jpg")
folder = pd.Series(folder)
print(folder)

# generating the xml labels
files = returnElllipseListFiles("labels")
dic = []
for f in files:
    dic += generateArray(f)

df = pd.DataFrame(dic)
# generate the name of xml file
print(df)
df["xml_name"] = df["name"].apply(changePandasExtension)
df["xml_file"] = df.apply(lambda row: pdToXml(row["name"], row["annotations"], row["size"], "images"), axis=1)
# saves the dataframe
df.apply(lambda row: saveXmlToFile(os.path.join("dataset", row['xml_name']), row['xml_file']), axis=1)


# cleaning imagesist()
names = df["name"].values.tolist()
folder = folder.apply(lambda x: x.replace("dataset\\",""))
val = folder.isin(names)
print(val)

cool_files = folder[val]
print(cool_files)
val = val.apply(lambda row: not row)

delete_files = folder[val]
delete_files.apply(lambda x: os.remove(os.path.join("dataset", x)))