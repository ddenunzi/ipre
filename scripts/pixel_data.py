import cv2 as cv
import numpy as np
import projection_finder as pf
import create_lists as lists


TEST_REPROJECTION=pf.TEST_REPROJECTION_PIX
TEST_PROJECTION=pf.TEST_CALIBRATION_PIX
TEST_PROJECTION_METASHAPE=lists.PIXELS_S_COORDINATES

FINAL_REPROJECTION=pf.FINAL_REPROJECTION_PIX
FINAL_PROJECTION_METASHAPE=lists.PIXELS_M_COORDINATES