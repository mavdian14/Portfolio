# Databricks notebook source
#make necessary imports
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
import matplotlib.image as mpimg
from moviepy.editor import VideoFileClip
import math

# COMMAND ----------

#apply frame masking & find region of interest
def interested_region(img, vertices):
    if len(img.shape) > 2:
        mask_color_ignore = (255,) * img.shape[2]
    else:
        mask_color_ignore = 255
    #fillPoly fills a polygon shape
    cv2.fillPoly(np.zeros_like(img), vertices,mask_color_ignore)
    #btiwise_and is the cv2 version of the bitwise AND formula
    return cv2.bitwise_and(img,np.zeros_like(img))

# COMMAND ----------

#Conversion of pixels to a line in Hough Transform Space
def hough_lines(img,rho,theta,threshold,min_line_len,max_line_gap):
    #HoughlinesP uses the probabilistic Hough transformation
    lines = cv2.HoughlinesP(img,rho,theta,threshold,np.array([]),minLineLength=min_line_len,maxLineGap=max_line_gap)
    line_img = np.zeros((img.shape[0], img.shape[1],3), dtype=np.uint8)
    lines_drawn(line_img,lines)
    return line_img

# COMMAND ----------

#Create two lines in each frame after Hough transform
def lines_drawn(img,lines,color=[255,0,0],thickness=6):
    global cache
    global first_frame
    slope_l, slope_r = [],[]
    lane_l, lane_r = [],[]
    
    α =0.2 
   for line in lines:
          for x1,y1,x2,y2 in line:
              slope = (y2-y1)/(x2-x1)
              if slope > 0.4:
                   slope_r.append(slope)
                   lane_r.append(line)
            elif slope < -0.4:
                slope_l.append(slope)
                lane_l.append(line)
        img.shape[0] = min(y1,y2,img.shape[0])
    if((len(lane_l)==0) or (len(lane_r)==0)):
        print('no lane detected')
        return 1
    slope_mean_l = np.mean(slope_l,axis=0)
    slope_mean_r = np.mean(slope_r,axis=0)
    mean_l = np.mean(np.array(lane_l),axis=0)
    mean_r = np.mean(np.array(lane_r),axis=0)
    
    if ((slope_mean_r == 0 ) or (slope_mean_l == 0)):
        print('dividing by zero')
        return 1
    
    x1_l = int((img.shape[0] - mean_l[0][1] - (slope_mean_l*mean_l[0][0]))/slope_mean_l)
    x2_l = int((img.shape[0] - mean_l[0][1] -(slope_mean_l* mean_l[0][0]))/slope_mean_l)
    x1_r = int((img.shape[0] - mean_r[0][1] - (slope_mean_r * mean_r[0][0]))/slope_mean_r)
    x2_r = int((img.shape[0] - mean_r[0][1] - (slope_mean_r * mean_r[0][0]))/slope_mean_r)
    
    if x1_l > x1_r:
        x1_l = int((x1_l+x1_r)/2)
        x1_r = x1_l
        y1_l = int((slope_mean_l * x1_l) + mean_l[0][1] - (slope_mean_l * mean_l[0][0]))
        y1_r = int((slope_mean_r * x1_r ) + mean_r[0][1] - (slope_mean_r * mean_r[0][0]))
        y2_l = int((slope_mean_l * x2_l ) + mean_l[0][1] - (slope_mean_l * mean_l[0][0]))
        y2_r = int((slope_mean_r * x2_r ) + mean_r[0][1] - (slope_mean_r * mean_r[0][0]))
    else:
        y1_l = img.shape[0]
        y2_l = img.shape[0]
        y1_r = img.shape[0]
        y2_r = img.shape[0]
        
    present_frame = np.array([x1_l,y1_l,x2_l,y2_l,x1_r,y1_r,x2_r,y2_r],dtype ="float32")
    
    if first_frame == 1:
        next_frame = present_frame
        first_frame = 0
    else:
        prev_frame = cache
        next_frame = (1-α)*prev_frame+α*present_frame
    
    cv2.line(img, (int(next_frame[0]), int(next_frame[1])), (int(next_frame[2]),int(next_frame[3])),color,thickness)
    cv2.line(img, (int(next_frame[4]), int(next_frame[5])), (int(next_frame[6]),int(next_frame[7])), color, thickness)
    
    cache = next_frame

# COMMAND ----------

#process each frame of video to detect lane
def weighted_img(img, initial_img,α=0.8, β=1., λ=0.):
    #addweighted() function helps in adding 2 images & blending them by passing the alpha, beta, & gamma values
    return cv2.addWeighted(initial_img,α, img, β, λ)

def process_image(image):
    
    global first_frame
    #cvtcolor is used to convery an image from 1 color space to another
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_hsv = cv2.cvtColor(image,cv2.COLOR_RGB2HSV)
    
    lower_yellow = np.array([20,100,100], dtype = "uint8")
    upper_yellow = np.array([30,255,255], dtype = "uint8")
    
    #the inRange() returns a sequence of numbers, 0,..,n by default
    mask_yellow = cv2.inRange(img_hsv,lower_yellow,upper_yellow)
     mask_white = cv2.inRange(gray_image, 200, 255)
    mask_yw = cv2.bitwise_or(mask_white, mask_yellow)
    mask_yw_image = cv2.bitwise_and(gray_image, mask_yw)
    
    #gaussianBlur() is a way to apply a low-pass filter in skimage
    gauss_gray= cv2.GaussianBlur(mask_yw_image, (5, 5), 0)
    
    #Canny() is used to detect the edges in an image
    canny_edges = cv2.Canny(gauss_gray,50,150)
    
    canny_edges = cv2.Canny(gauss_gray,50,150)
    
    imshape = image.shape
    lower_left = [imshape[1]/9,imshape[0]]
    lower_right = [imshape[1]-imshape[1]/9,imshape[0]]
    top_left = [imshape[1]/2-imshape[1]/8,imshape[0]/2+imshape[0]/10]
    top_right = [imshape[1]/2+imshape[1]/8,imshape[0]/2+imshape[0]/10]
    vertices = [np.array([lower_left,top_left,top_right,lower_right],dtype=np.int32)]
    roi_image = interested_region(canny_edges, vertices)
    
    theta = np.pi/180
    
    line_image = hough_lines(roi_image, 4, theta, 30, 100, 180)
    result = weighted_img(line_image, image, α=0.8, β=1., λ=0.)
    return result

# COMMAND ----------

#clip the input video to frames and get the resultant output video file
first_frame = 1
white_output = '__path_to_output_file__'
clip1 = VideoFileClip("__path_to_input_file__")
white_clip = clip1.f1_image(process_image)
white_clip.write_videofile(white_output, audio=False)

# COMMAND ----------

#Lane Line Detection Project GUI
import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import os
import numpy as np

global last_frame1
last_frame1 = np.zeros((480,640,3), dtype=np.uint8)
global last_frame2
last_frame2 = np.zeros((480,640,3), dtype=np.uint8)
global cap1
global cap2
#videoCapture() allows you to read,capture,& display video files & camera stream
cap1 = cv2.VideoCapture("path_to_input_test_video")
cap2 = cv2.VideoCapture("path_to_resultant_lane_detected_video")

def show_vid():
    #isOpened() is a boolean which returns True if the cap object has started capturing the frames
    if not cap1.isOpened():
        print("cant open the camera1")
        flag1, frame1 = cap1.read()
        #resize() is used to resize an image
        frame1 = cv2.resize(frame1,(400,500))
        if flag1 is None:
            print("Major error!")
        elif flag1:
            global last_frame1
            last_frame1 = frame1.copy()
            
            pic = cv2.cvtColor(last_frame1,cv2.COLOR_BGR2RGB)
            #fomarray() creates an image memory from an object exporting the array interface
            img = Image.fromarray(pic)
            
            imgtk = ImageTk.PhotoImage(image=img)
            
            lmain.imgtk = imgtk
            lmain.configure(image=imgtk)
            lmain.after(10,show_vid)
            
if __name__ == '__main__':
    root=tk.Tk()
    #.Label() creates a label widget
    lmain=tk.Label(master=root)
    lmain2 = tk.Label(master=root)
    lmain.pack(side=LEFT)
    #.pack() converts a given list of values into their corresponding string representation
    lmain2.pack(side=RIGHT)
    root.title("Lane-line detection")
    #.geometry() sets the geometry of a tk frame
    root.geometry("900x700+100+10")
    #
    exitbutton = Button(root, text='Quit',fg="red",command=   root.destroy).pack(side = BOTTOM,)
    show_vid()
    show_vid2()
    #mainloop() runs the tk event loop
    root.mainloop()                                  
    cap.release()
