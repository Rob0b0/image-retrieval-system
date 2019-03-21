# PixInfo.py
# Program to start evaluating an image in python

from PIL import Image, ImageTk
import glob, os, math
import numpy as np
from sklearn import preprocessing
from statistics import stdev 
import pandas as pd
# import skimage.io

# Pixel Info class.
class PixInfo:
    
    # Constructor.
    def __init__(self, master):
    
        self.master = master
        self.imageList = []
        self.photoList = []
        self.imgNameList=[]
        self.pixSizeList=[]
        self.xmax = 0
        self.ymax = 0
        self.colorCode = []
        self.intenCode = []
        self.picPath = 'images'
        self.refreshPics(self.picPath)
            
    def refreshPics(self, folderPath):
        self.imageList = []
        self.photoList = []
        self.imgNameList=[]
        self.pixSizeList=[]
        self.xmax = 0
        self.ymax = 0
        self.colorCode = []
        self.intenCode = []
        self.picPath = folderPath
        # Add each image (for evaluation) into a list, 
        # and a Photo from the image (for the GUI) in a list.
        for infile in sorted(glob.glob(self.picPath+'/*.jpg'), key=lambda x: self.getFileInt(x)): #, key=lambda x: self.getFileInt(x)
            file, ext = os.path.splitext(infile)
            im = Image.open(infile)
            self.imgNameList.append(infile)
            # skim = skimage.io.imread(infile)
            # skim = skim.reshape(skim.shape[0]*skim.shape[1], skim.shape[2])
            # Resize the image for thumbnails.
            imSize = im.size
            x = int(imSize[0]/3)
            y = int(imSize[1]/3)
            imResize = im.resize((x, y), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(imResize)

            # Find the max height and width of the set of pics.
            if x > self.xmax:
              self.xmax = x
            if y > self.ymax:
              self.ymax = y
            
            # Add the images to the lists.
            self.imageList.append(im)
            self.photoList.append(photo)

        # Create a list of pixel data for each image and add it
        # to a list.
        for im in self.imageList[:]:
            pixList = list(im.getdata())
            CcBins, InBins = self.encode(pixList)
            self.colorCode.append(CcBins)
            self.intenCode.append(InBins)
            self.pixSizeList.append(len(pixList))
        # only use the following two lines for grading
        # self.colorCode = pd.read_csv("colorCode.csv", header=None, delimiter=',').values[:, 2:]
        # self.intenCode = pd.read_csv("intensity.csv", header=None, delimiter=',').values[:, 2:]
        # normalize intensitycode
        row_sums = np.linalg.norm(self.intenCode, axis=1, ord=1)
        normInten = (self.intenCode/row_sums[:, np.newaxis])
        # normalize cc code
        row_sums = np.linalg.norm(self.colorCode, axis=1, ord=1)
        normCC = self.colorCode/row_sums[:,np.newaxis]
        # concatenate them together
        self.featureM = np.concatenate((normInten, normCC), axis=1)
        # calculate mean
        means = np.average(self.featureM, axis=0)
        # calculate stddev
        #stddev = np.std(self.featureM, axis=0, ddof=1, dtype=np.float)
        stddev = []
        for i in range(self.featureM.shape[1]):
            standardev = stdev(self.featureM[:,i])
            stddev.append(standardev)
        # calcualte gaussian normal
        gauss_norm = np.zeros((self.featureM.shape[0], self.featureM.shape[1]))
        for i in range(self.featureM.shape[0]):
            for j in range(self.featureM.shape[1]):
                if (stddev[j]!=0):
                    gauss_norm[i][j] = (self.featureM[i][j]-means[j])/(stddev[j])
                else:
                    gauss_norm[i][j]=0
        self.featureM = gauss_norm
        # gaussian normalization
        # self.featureM = preprocessing.StandardScaler().fit_transform(self.featureM)
        self.indexList = list(range(len(self.imageList)))
        self.relevanceList = [0]*len(self.imageList)

    # Bin function returns an array of bins for each 
    # image, both Intensity and Color-Code methods.
    def encode(self, pixlist):
        
        # 2D array initilazation for bins, initialized
        # to zero.
        CcBins = [0 for i in range(64)]
        InBins = [0 for i in range(25)]
        # for intensity method
        for rgb in pixlist:
            intensity = rgb[0]*0.299+rgb[1]*0.587+rgb[2]*0.114
            if (intensity >= 250):
                InBins[24]+=1
            else:
                InBins[int(intensity/10)]+=1
        # for color code method
        for rgb in pixlist:
            mask = rgb[0]//64*16+rgb[1]//64*4+rgb[2]//64
            CcBins[mask]+=1
        
        return CcBins, InBins
    
    def getFileInt(self, fn):
        i = fn.rfind('/')
        j= fn.rfind('.')
        return int(fn[i+1: j])
    
    
    # Accessor functions:
    def get_imageList(self):
        return self.imageList
    
    def get_photoList(self):
        return self.photoList
    
    def get_imgNameList(self):
        return self.imgNameList

    def get_xmax(self):
        return self.xmax
    
    def get_ymax(self):
        return self.ymax
    
    def get_colorCode(self):
        return self.colorCode
        
    def get_intenCode(self):
        return self.intenCode

    def get_folderPath(self):
        return self.picPath

    def get_pixSizeList(self):
        return self.pixSizeList

    def get_indexList(self):
        return self.indexList

    def get_featureM(self):
        return self.featureM

    def get_relevanceList(self):
        return self.relevanceList