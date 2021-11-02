#python3.7.9
#packages used: opencv ,imutils, argparse ,numpy ,pyzbar
#  exec command :     python opencvDecoder.py -i "photos" -r "output.json"  


import cv2
import imutils
import argparse
import json

def cropPic(img):
    bardet = cv2.barcode_BarcodeDetector()
    ok, decoded_info, decoded_type, corners = bardet.detectAndDecode(img)
    #print(ok,decoded_info,decoded_type,corners)
    
    minx,miny,maxx,maxy = 2000,2000,0,0;
    results  = []
    if (corners is None):
        return []
    for solution in corners:
        for corner in solution:
            #print(corner);
            x = corner[0];
            y = corner[1];
            if (x < minx):
                minx = x
            if (x > maxx):
                maxx = x;
            if (y < miny):
                miny = y;
            if (y > maxy):
                maxy = y;
        #print(minx,miny,maxx,maxy)
    
        #print(img.shape)
        width = img.shape[0]
        height = img.shape[1]
        temp = 300
        cropH=img[int(miny-temp):int(maxy+temp),0:int(width)]
        cropV=img[0:int(height),int(minx-temp):int(maxx+temp)]
        #cv2.imwrite(f"cropH{len(results)}.png", cropH)
        #cv2.imwrite(f"cropV{len(results)}.png", cropV)
        results = results + [cropH] + [cropV]
        
        
    return results
    

import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import os

def isGoodCode(s):
    return isinstance(s,str) and len(s)==14 and s.isdigit()
def decode2Str(x):
    return x.data.decode("utf-8")
def decode(x,angle):
    r=rotate_bound(x,angle)
    a=pyzbar.decode(r)
    texts=map(decode2Str,a)
    return list(texts)
def tryrotate(img,angle):
    if (angle > 5*360):
        return []
    else:
        codes = list(set(list(filter(isGoodCode,decode(img,angle)))))
                                   
        if (codes == []):
            return tryrotate(img,angle+50);
        else:
            return codes;
def barcode(gray):
  texts = pyzbar.decode(gray)
  if texts == []:
    gray = np.uint8(np.clip((1.1 * gray + 10), 0, 255))
    angle = barcode_angle(gray)
  return texts
 
def rotate_bound(image, angle):
  (h, w) = image.shape[:2]
  (cX, cY) = (w // 2, h // 2)
 
  M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
  cos = np.abs(M[0, 0])
  sin = np.abs(M[0, 1])
  
  nW = int((h * sin) + (w * cos))
  nH = int((h * cos) + (w * sin))
 
  M[0, 2] += (nW / 2) - cX
  M[1, 2] += (nH / 2) - cY
 
  return cv2.warpAffine(image, M, (nW, nH))

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--imagedir", required = True, help = "dirpath to the image file")
ap.add_argument("-r", "--resultfile", required = True, help = "path to the result file")
args = vars(ap.parse_args())

def isPic(file):
    return file.endswith(".jpg")  or file.endswith(".png")

resultPath = args["resultfile"]
if (os.path.exists(resultPath)):
    if (os.path.isfile(resultPath)):
        pass;
    else:
        raise Exception("ResultPath is a directory")
else:
    with open(resultPath,"w") as f:
        pass
with open(args["resultfile"],"r+") as f:
    f.seek(0)
    fileContent=f.read()
    if (fileContent == ""):
        result=json.loads("{}")
    else:
        result=json.loads(fileContent)
    filelist=filter(isPic,os.listdir(args["imagedir"]));
    for filename in filelist:
        print(filename)
        if (filename in result):
            print("exist")
            continue
        
        
        codes = []
        image=cv2.imread(os.path.join(args["imagedir"],filename))
        images=cropPic(image)
        images=images+[image]
        for image in images:
            try:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                #gray = np.uint8(np.clip((1.1 * img + 10), 0, 255))
                texts = tryrotate(gray,0)
                if (texts!=[]):
                    codes= texts
                    break;
                else:
                    texts = tryrotate(image,0)
                    if (texts!=[]):
                        codes= texts
                        break;
                
            except Exception as e:
                print(e)
        else:
            print("识别失败")
        print("识别成功",list(set(codes)))
        result[filename] = list(set(codes))
        f.seek(0)
        json.dump(result,f,indent=4,separators=(",",":"))
        f.flush()
            
        
        
    