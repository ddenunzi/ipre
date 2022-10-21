import cv2 as cv
from cv2 import imshow
import numpy as np
import create_lists as lists
from euler_rodrigues import rot

import sys

def separate_img_name(filename):
    filename=filename.split("/")
    return filename[2]

#CALIBRATE CAMERA, need more data
class CalibrateCamera:
    def __init__(self,images,object_points,pixels):

        self.image_points=[]
        self.image_points2=[]
        self.pixels=pixels
        self.object_points=[object_points]#list of coordinates
        self.dist_coeff=[0]
        self.images=images #list of images
        self.boardSize=(7,5)
        #define columns and rows
        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        #define criteria

 
    def circles_grid_centers(self):

        #To consider: The parameters below depend on pixel distances, areas, etc. The images have to be similar to be able to use the same parameters. For different sets of images, different parameters are needed.
        #For example: from folder "cropped_images" images sets are DSC09900 to DSC09915, DSC9916 to DSC09926, DSC09927 to DSC09934, etc.
        #FROM CROPPED_IMAGES, 12 SUCCESSFUL CIRCLESGRID DETECTION FOR 35 CIRCLES.
        blobParams = cv.SimpleBlobDetector_Params()
        blobParams.filterByCircularity = True
        blobParams.minCircularity = 0.2
        blobParams.minDistBetweenBlobs = 130
        blobParams.filterByInertia = True
        blobParams.minInertiaRatio = 0.01
        blobParams.filterByArea = True
        blobParams.minArea = 1100
        blobParams.maxArea = 1800
        blobParams.minThreshold = 8.5
        blobParams.maxThreshold = 2000
        blobParams.filterByColor = True
        blobParams.blobColor=0

        self.blobdetector = cv.SimpleBlobDetector_create(blobParams)


        for image in self.images:
            img=cv.imread(image)
            self.gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
            keypoints = self.blobdetector.detect(self.gray)
            self.im_with_keypoints = cv.drawKeypoints(self.gray, keypoints, np.array([]), (0,255,0), cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            #cv.imshow('img',self.im_with_keypoints)
            #cv.waitKey(0)
            im_with_keypoints_gray = cv.cvtColor(self.im_with_keypoints, cv.COLOR_BGR2GRAY)
            self.retval,self.centers=cv.findCirclesGrid(self.im_with_keypoints, self.boardSize, flags=(cv.CALIB_CB_SYMMETRIC_GRID+cv.CALIB_CB_CLUSTERING),blobDetector=self.blobdetector,parameters=None)
            if self.retval == True: 
              #cornerSubPix(image, corners, winSize, zeroZone, criteria) -> corners
                self.centers2=cv.cornerSubPix(self.gray, self.centers, (11,11),(-1,-1), self.criteria) 
                self.image_points.append(self.centers2)



            #image_points with photo name
                image_name=separate_img_name(image)
                self.image_points2.append([image_name,self.centers2])
    
 
        # Draw and display the corners

                img = cv.drawChessboardCorners(img, self.boardSize, self.centers2, self.retval)

                #cv.imshow('img',img)
                #cv.waitKey(0)

    
    def calibrate(self):
        #what is gray????? should this be for each picture???
        print(self.pixels)
        for pixel in self.pixels[:1]:
            print(self.object_points)
            print(pixel[1])
            
            self.retval_2,self.cam_matrix,self.dist_coeff,self.rotation_vector,self.translation_vector=cv.calibrateCamera(self.object_points, [pixel[1]], (3200,4800), None, None)
       # img = cv.imread('newimage') #what do i put in here?
       # h,  w = img.shape[:2]
           #print(self.retval_2)
            #print(self.cam_matrix)
            #print(self.dist_coeff)
            #print(self.rotation_vector)
            #print(self.translation_vector)
       # self.newcam_mtx, roi=cv.getOptimalNewCameraMatrix(self.cam_matrix,self.dist_coeff,(w,h),1,(w,h))


class ProjectPoints:

    def __init__(self, images,image_points, obj_coordinates_3d, camera_coordinates_3d, cam_matrix,dist_coef):

        self.obj_coordinates=np.array(obj_coordinates_3d)
        self.images=images
        self.image_points=image_points
        self.camera_coordinates=camera_coordinates_3d
        self.camera_matrix=cam_matrix
        self.distortion_coef=dist_coef
        self.projection_pixels=[]
        self.test_images_paths=['DSC09901.JPG','DSC09902.JPG','DSC09905.JPG','DSC09906.JPG','DSC09908.JPG','DSC09909.JPG','DSC09910.JPG','DSC09911.JPG','DSC09912.JPG','DSC09913.JPG','DSC09914.JPG','DSC09939.JPG']


    def projections(self,filename):
        print("Camera rotation vector: "+str(self.rotation_vector))
        print("Camera translation vector: "+str(self.translation_vector))

        pixels=cv.projectPoints(self.obj_coordinates,self.rotation_vector,self.translation_vector,self.camera_matrix,self.distortion_coef)
        print(pixels)
        blank_image = np.zeros((3200,4800,3), np.uint8)
        img=cv.imread('photos/still photos/'+str(filename))

        for pixel in pixels[0][1:]:
            new_image=cv.circle(img,(int(pixel[0][0]),int(pixel[0][1])), radius=10,color=(0,255,0),thickness=-1)
            blank_image=cv.circle(blank_image,(int(pixel[0][0]),int(pixel[0][1])), radius=10,color=(0,255,0),thickness=-1)

        imshow(filename,new_image)
        cv.imwrite('photos/reproject/'+str(filename),blank_image)

        cv.waitKey(0)

        self.projection_pixels.append([filename,pixels[0]])

 

    def create_projections(self):

        for camera in self.camera_coordinates:
            filename=camera[0]
            if filename in self.test_images_paths:
                print(filename)
                self.translation_vector=np.array(camera[1])
                self.rotation_vector=self.euler_rodrigues(camera[2])
                self.projections(filename)
        

    def euler_rodrigues(self,v):
        new_rotation=rot(v)
        new_rotation[0]=new_rotation[0]*(-1)
        print("yaw:")
        print(new_rotation[0])
        print("pitch:")
        new_rotation[1]=new_rotation[1]*(-1)
        new_rotation[2]=new_rotation[2]*(-1)
        print(new_rotation[1])
        print("roll:")
        print(new_rotation[2])

        return new_rotation
        
class FindErrors:
    def __init__(self,pixels_AM,pixels_P):
       #RAW LISTS DIRECTLY FROM PROJECTPOINTS AND AGISOFTMETASHAPE
        self.coordinates_AM=pixels_AM
        self.coordinates_P=pixels_P
        self.coordinates_CC=[]

        #FILTERED LISTS WITH ACCESSIBLE PIXELS
        self.coordinates_AM_filter=self.filter_AM()
        self.coordinates_P_filter=self.filter_P()
        self.coordinates_CC_filter=self.filter_CC()

    #RAW LIST DIRECTLY FROM CALIBRATECAMERA
    def add_coordinates_CC(self, pixels_BD):
        self.coordinates_CC=pixels_BD

    def filter_AM(self):

        pass
    
    def filter_P(self):
        pass

    def filter_CC(self):
        new=[]
        for i in range(len(self.coordinates_CC)):
            for j in range(len(i[1])):
                target_name='target '+str(j)
                target_x=i[1][0][j][0]
                target_y=i[1][0][j][1]
                pixel_coord=[i[0],target_name,target_x,target_y]
                new.append(pixel_coord)
        return new
                

def filter(points, image_names):
    new=[]
    for i in range(len(points)):
        for  j in range(len(image_names)):
            if points[i][0]==image_names[j]:
                new.append(points[i])
    return new




#https://python.hotexamples.com/examples/cv2/-/projectPoints/python-projectpoints-function-examples.html

