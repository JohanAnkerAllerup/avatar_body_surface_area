# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 21:07:43 2020

@author: johan
"""
#avatar_lesions_BSA
#Determines the procentage of the body surface area affected based on patient drawn lesions avatar
#All avatars has a left most reference box with a known area of 1 cm^2 and meassured area of 3667 pixels 
#which is used to calculate pixels_per_metric  = 3667px / 1 cm2 = 3667px/cm2.

from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import os
import pandas as pd

def lesion_areas(photo, ref, path):    
    # load the image, convert it to grayscale, and blur it slightly
    image = cv2.imread(photo)
    image = cv2.resize(image, (1000,1000))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # threshold the image, then perform a series of erosions +
    # dilations to remove any small regions of noise
    thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY_INV)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)
    # find contours in thresholded image, then grab the largest
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    (cnts, _) = contours.sort_contours(cnts)
    
    
    lesion_areas = []
    for i in cnts:
        area = cv2.contourArea(i)
        #to turn in to cm2 divide by size of reference lesion in pixels which is 1 cm2
        area_cm2 = area/ref
        lesion_areas.append(area_cm2)
    all_areas_cm2 = sum(lesion_areas)
    # loop over the contours individually and draw contours
    for c in cnts:
        cv2.drawContours(image, [c], -1, (0, 255, 255), 2)
    #show  and save image
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    photo_name = photo.replace(".jpg", "_lesion_contours.jpg")    
    path = path +  photo_name
    path = path.replace("'", "" )
    cv2.imwrite(path, image)
    print('Pic with lesion contours saved at: ' + path)
    return all_areas_cm2
        

def avatar_size(photo, ref, path):
    image = cv2.imread(photo)
    image = cv2.resize(image, (1000,1000))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # find contours in thresholded image, then grab the largest
    edged = cv2.Canny(gray, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)
    
    
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
    	cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
     
    c = max(cnts, key=cv2.contourArea)
    avatar_size = cv2.contourArea(c)
    avatar_cm2 = avatar_size/ref
    cv2.drawContours(image, [c], -1, (0, 255, 255), 2)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    photo_name = photo.replace(".jpg", "_avatar_contour.jpg")    
    path = path +  photo_name
    path = path.replace("'", "" )
    cv2.imwrite(path, image)
    print('Pic with avatar contours saved at: ' + path)
    return avatar_cm2

BSA_procent_list= []
patient_ID = []

def avatar_lesions_BSA(photo_dir, ref, save_path):       
    for i, j in enumerate(os.listdir(photo_dir)):
        full_path = os.path.join(photo_dir, j)
        patient_ID.append(full_path)
        print(full_path)
        avatar_area= avatar_size(full_path, ref, save_path)
        lesion = lesion_areas(full_path, ref, save_path)
        BSA_procent =  avatar_area / lesion
        BSA_procent_list.append(BSA_procent)
        print(BSA_procent)
#        return BSA_procent
        image = cv2.imread(full_path)
        image = cv2.resize(image, (1000,1000))
        image = cv2.putText(image, "Avatar area:"+ str(avatar_area), (50,50), cv2.FONT_HERSHEY_SIMPLEX , 1 , (80,0,255), 2)
        image = cv2.putText(image, "Leisions area:" + str(lesion), (50,80), cv2.FONT_HERSHEY_SIMPLEX , 1 , (80,0,255), 2)
        image = cv2.putText(image, "Leisions procentage of bodyarea:" + str(lesion/avatar_area), (50,100), cv2.FONT_HERSHEY_SIMPLEX , 1 , (80,0,255), 2)
        image = cv2.putText(image, "Path:" + str(full_path), (50,130), cv2.FONT_HERSHEY_SIMPLEX , 1 , (80,0,255), 2)
        photo_name = j.replace(".jpg", "_full.jpg")   
        cv2.imwrite(photo_name, image)
        cv2.imshow("Image", image)
        cv2.waitKey(0)
    
    df = pd.DataFrame({"ID": patient_ID,"BSA": BSA_procent_list})
    print (df)

avatar_lesions_BSA(photo_dir = 'files', ref = 3667, save_path=r'output')
    
