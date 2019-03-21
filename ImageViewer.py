# ImageViewer.py
# Program to start evaluating an image in python
#
# Show the image with:
# os.startfile(imageList[n].filename)

import tkinter as tk
from tkinter import filedialog
import math
import os
import sys
from PixInfo import PixInfo
from PIL import Image, ImageTk
import numpy as np
from sklearn import preprocessing
from statistics import stdev 


# Main app.
class ImageViewer(tk.Frame):

    # Constructor.
    def __init__(self, master, pixInfo):

        tk.Frame.__init__(self, master)
        self.master = master
        self.pixInfo = pixInfo
        self.colorCode = pixInfo.get_colorCode()
        self.intenCode = pixInfo.get_intenCode()
        self.folderPath = pixInfo.get_folderPath()
        # Full-sized images.
        self.imageList = pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = pixInfo.get_photoList()
        # img name list
        self.imgNameList = pixInfo.get_imgNameList()
        # img index list for select preview
        self.indexList = pixInfo.get_indexList()
        # feature Matrix
        self.featureM = pixInfo.get_featureM()
        # relevance list
        self.relevanceList = pixInfo.get_relevanceList()
        # checkboxes list
        self.relBoxBools = [tk.IntVar() for i in range(len(self.imageList))]
        # Image size for formatting.
        self.xmax = pixInfo.get_xmax()
        self.ymax = pixInfo.get_ymax()
        # predefined column number for result listframe below
        self.colnum = 8
        # Define window size
        master.geometry("1250x750")

        # Create Picture chooser frame.
        # USED GRID STRUCTURE instead of .pack()
        listFrame = tk.Frame(master, relief="groove", borderwidth=1, padx=5, pady=5)
        listFrame.grid(row=1, column=0, columnspan=4,
                       sticky="news", padx=10, pady=5)

        # Create Control frame.
        controlFrame = tk.Frame(master, width=350)
        controlFrame.grid(row=0, column=3, sticky="sen", padx=10, pady=5)

        # Create listbox frame
        previewListFrame = tk.Frame(
            master, width=30, height=self.ymax+100, borderwidth=1)
        previewListFrame.grid_propagate(0)
        previewListFrame.grid(row=0, column=0, sticky="news", padx=5, pady=5)

        # Create Preview frame.
        previewFrame = tk.Frame(master, width=self.xmax+245, height=self.ymax+100, borderwidth=1,
                             relief="groove", highlightbackground='BLACK')
        previewFrame.grid_propagate(0)
        previewFrame.grid(row=0, column=1, sticky="news", padx=(5, 0), pady=5)
        self.previewFrame = previewFrame

        # Create Selected Photo List Frame
        selectPreviewFrame = tk.Frame(master, width=self.xmax+245, height=self.ymax+100,
                                   borderwidth=1, relief="groove", highlightbackground='BLACK')
        selectPreviewFrame.grid_propagate(0)
        selectPreviewFrame.grid(
            row=0, column=2, sticky="news", padx=(0, 5), pady=5)
        self.selectPreviewFrame = selectPreviewFrame

        # Create Results frame.
        master.rowconfigure(0, weight=0)
        master.columnconfigure(0, weight=1)
        master.rowconfigure(1, weight=1)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(2, weight=1)
        master.columnconfigure(3, weight=1)
        listFrame.rowconfigure(0, weight=1)
        listFrame.columnconfigure(0, weight=1)
        listFrame.columnconfigure(1, weight=0)
        controlFrame.rowconfigure(0, weight=1)
        controlFrame.columnconfigure(0, weight=1)
        previewFrame.rowconfigure(0, weight=1)
        previewFrame.columnconfigure(0, weight=1)

        # Layout preview listbox
        self.plistScrollbar = tk.Scrollbar(previewListFrame)
        self.plistScrollbar.pack(side="right", fill='y')

        self.plist = tk.Listbox(previewListFrame,
                             yscrollcommand=self.plistScrollbar.set,
                             selectmode="browse",
                             height=14)
        for i in range(len(self.imageList)):
            self.plist.insert(i, self.getFilename(self.imageList[i].filename))
        self.plist.pack(side='left', fill='both')
        #self.plist.grid(row=0, column=0, sticky=S+E+N+W)
        self.plist.activate(1)
        self.plist.bind('<<ListboxSelect>>', self.update_preview)
        self.plistScrollbar.config(command=self.plist.yview)

        # Layout Result Picture Grid list (The big gird below).
        # construct scrollbar
        self.listScrollbar = tk.Scrollbar(listFrame)
        self.listScrollbar.grid(row=0, column=1, sticky="ens")
        # create list
        self.list = tk.Frame(listFrame)
        self.list.rowconfigure(0, weight=1)
        self.list.columnconfigure(0, weight=1)
        self.list.grid_propagate(False)

        # add a canvas inside list
        self.listcanvas = tk.Canvas(self.list)
        self.listcanvas.grid(row=0, column=0, sticky="news")
        # add another frame for gridview images
        self.gridframe = tk.Frame(self.listcanvas)
        self.listcanvas.create_window(
            (0, 0), window=self.gridframe, anchor='nw')
        # get a grid view of clicable images
        listsize = len(self.photoList)
        # 8 images per row, then
        rownum = int(math.ceil(listsize/float(self.colnum)))
        fullsize = (0, 0, (self.xmax*self.colnum), (self.ymax*rownum))
        for i in range(rownum):
            for j in range(self.colnum):
                if (i*self.colnum+j) < listsize:
                    pho = self.photoList[i*self.colnum+j]
                    #pImg = Label(self.gridframe, image=pho)
                    pImg = tk.Button(self.gridframe, image=pho, fg='white',
                                  relief='flat', bg='white', bd=0, justify='center')
                    pImg.configure(image=pho)
                    pImg.photo = pho
                    pImg.config(
                        command=lambda f=self.imgNameList[i*self.colnum+j]: self.inspect_pic(f))
                    pImg.grid(row=i, column=j, sticky='news', padx=5, pady=5)
        self.gridframe.update_idletasks()
        # self.listcanvas.bbox(ALL)
        self.listcanvas.config(scrollregion=fullsize)
        self.list.grid(row=0, column=0, sticky='news')
        self.origY = self.listcanvas.yview()[0]
        self.listcanvas.configure(yscrollcommand=self.listScrollbar.set)
        # Tried scroll using mousewheel but it didn't work out well on Mac
        #self.listcanvas.bind_all("<MouseWheel>", self._on_mousewheel)
        #self.listcanvas.bind_all('<Shift-MouseWheel>', self.on_horizontal)
        self.list.bind('<<CanvasSelect>>', self.update_preview)
        self.listScrollbar.config(command=self.listcanvas.yview)

        # Layout Controls inside controlFrame
        button = tk.Button(controlFrame, text="Select Folder",
                        bg='white', padx=5, width=15,
                        command=lambda: self.inspect_pics())
        # self.list.get(ACTIVE)))
        button.grid(row=0, column=0, sticky='news', padx=5, pady=2)
        # label
        self.refImgLabel = tk.Label(
            controlFrame, text=self.folderPath, width=15, wraplength=100)
        self.refImgLabel.grid(row=0, column=1, sticky='news', padx=5, pady=2)
        # Color-code button
        self.b1 = tk.Button(controlFrame, text="Color-Code",
                         padx=5, width=15,
                         command=lambda: self.find_distance(method='CC'))
        self.b1.grid(row=1, column=1, sticky="news",padx=5, pady=2)
        # Intensity Button
        b2 = tk.Button(controlFrame, text="Intensity",
                    padx=5, width=15,
                    command=lambda: self.find_distance(method='inten'))
        b2.grid(row=1, column=0, sticky="news",padx=5, pady=2)
        # Color-code+intensity Button
        colorPlusInten = tk.Button(controlFrame, text="Color-code + Intensity",
                    padx=5, width=15, wraplength=100,
                    command=lambda: self.find_distance(method='CC+inten'))
        colorPlusInten.grid(row=2, column=0, sticky='news',padx=5, pady=2)
        # checkbox for RF
        self.rfbool = tk.IntVar()
        self.rfbox = tk.Checkbutton(controlFrame, text='Relevance Feedback', 
            padx=5, width= 15, wraplength=100, variable = self.rfbool, 
            offvalue = 0, onvalue=1,
            command=self.add_checkbox)
        self.rfbox.grid(row=2, column=1, sticky='news',padx=5, pady=2)
        # Reset Button
        resetButton = tk.Button(controlFrame, text='Reset',
                             padx=5, width=15,
                             command=lambda : self.reset())
        resetButton.grid(row=3, column=0, sticky="news",padx=5, pady=2)
        # Quit Button
        quitButton = tk.Button(controlFrame, text='Quit',
                            padx=5, width=15, command=lambda: sys.exit(0))
        quitButton.grid(row=3, column=1, sticky="news",padx=5, pady=2)

        # resize option for control frame
        controlFrame.rowconfigure(0, weight=1)
        controlFrame.rowconfigure(1, weight=1)
        controlFrame.rowconfigure(2, weight=1)
        controlFrame.rowconfigure(3, weight=1)

        # Layout Preview (The two big frames on top middle ).
        # preview the first image
        image = self.imageList[0]
        self.previewFrame.update()
        # resize to fit the frame
        imResize = image.resize(self.resize_img(self.previewFrame.winfo_width(
        ), self.previewFrame.winfo_height(), image), Image.ANTIALIAS)
        pho = ImageTk.PhotoImage(imResize)
        self.previewImg = tk.Label(self.previewFrame,
                                image=pho)
        self.previewImg.photo = pho
        self.previewImg.grid(row=0, column=0, sticky='news')
        # Select Image Preview
        # add a blank label in it
        self.selectImg = tk.Label(selectPreviewFrame)
        self.selectImg.grid(row=0, column=0, sticky='news')

    # bind mouse wheel scroll
    def _on_mousewheel(self, event):
        self.listcanvas.yview_scroll(-1*(event.delta/120), "units")

    # horizontal mouse wheel scroll
    def on_horizontal(self, event):
        self.listcanvas.xview_scroll(-1 * event.delta/120, 'units')

    # return resized scaled img
    def resize_img(self, rwidth, rheight, img):
        oldwidth = img.size[0]
        oldheight = img.size[1]
        ratio = float(oldwidth)/oldheight
        if ratio >= 1:
            return (int(rwidth), int(rwidth/ratio))
        else:
            return (int(rheight*ratio), int(rheight))

    # Event "listener" for listbox change.
    def update_preview(self, event):
        try:
            self.previewI = self.plist.curselection()[0]
        except:
            self.previewI = 0
        image = self.imageList[int(self.previewI)]
        # resize to fit the frame
        self.previewFrame.update()
        #print (self.resize_img(self.previewFrame.winfo_width(), self.previewFrame.winfo_height(), image))
        imResize = image.resize(self.resize_img(self.previewFrame.winfo_width(
        )-10, self.previewFrame.winfo_height()-10, image), Image.ANTIALIAS)
        pho = ImageTk.PhotoImage(imResize)
        self.previewImg.configure(
            image=pho)
        self.previewImg.photo = pho

    # Find the Manhattan Distance of each image and return a
    # list of distances between image i and each image in the
    # directory uses the comparison method of the passed
    # binList
    def find_distance(self, method):
        try:
            i = self.plist.curselection()[0]
        except:
            i = 0
        pixList = list(self.imageList[i].getdata())
        targetCC, targetIntens = self.pixInfo.encode(pixList)
        targetpixSize = len(pixList)
        if (method == 'inten'):
            MDs = self.calcMD(targetIntens, self.intenCode,
                              targetpixSize, self.pixInfo.get_pixSizeList())
        elif (method=='CC'):
            MDs = self.calcMD(targetCC, self.colorCode,
                              targetpixSize, self.pixInfo.get_pixSizeList())
        elif (method=='CC+inten'):
            targetFM = self.featureM[i]
            # check if RF is checked
            if (self.rfbool.get() == 0):
                # no need to do gaussian
                MDs=self.calcWeightD(targetFM, self.featureM, np.ones(targetFM.shape[0])*1/targetFM.shape[0])
            else:
                #print("relevance list: {}".format(self.relevanceList))
                # get the relevant images rows
                relevantM = []
                for i in range(len(self.relevanceList)):
                    if self.relevanceList[i]==1:
                        relevantM.append(self.featureM[i])
                print("Releveant Matrix Shape: {}".format(len(relevantM)))
                # calculate weight
                # stdM = np.std(relevantM, axis=0, ddof=1, dtype=np.float)
                stdM = []
                for i in range(len(relevantM[0])):
                    standarddev = stdev(np.array(relevantM)[:,i])
                    stdM.append(standarddev)
                stdM = np.array(stdM)
                weightM = []
                for i in range(len(stdM)):
                    if stdM[i]==0:
                        # check average
                        avg = (np.array(relevantM)[:,i]).mean()
                        if avg !=0:
                            weight = 1/(0.5*min(stdM[stdM!=0]))
                        else:
                            weight = 0
                    else:
                        weight = 1/stdM[i]
                    weightM.append(weight)
                weightM = np.array(weightM)
                weightM = weightM/np.linalg.norm(weightM, ord=1)
                MDs = self.calcWeightD(targetFM, self.featureM, weightM)


        MDTuples = [(self.photoList[i], MDs[i])
                    for i in range(len(self.imageList))]
        MDTuplesNames = {self.imgNameList[i]: MDs[i]
                         for i in range(len(self.imageList))}
        self.update_results(MDTuples, MDTuplesNames)
        return

    def calcMD(self, targetIntens, intenCodes, targetpixSize, pixSizeList):
        ret = []
        for j in range(len(intenCodes)):
            code = intenCodes[j]
            sum = 0
            for i in range(len(targetIntens)):
                sum += math.fabs(targetIntens[i]/float(targetpixSize) -
                                 float(code[i])/pixSizeList[j])
            ret.append(sum)
        return ret

    # get the weighted distance for each of the images
    def calcWeightD(self, targetFM, featureM, weightM):
        ret=[]
        for i in range(featureM.shape[0]):
            sum = 0
            for j in range(featureM.shape[1]):
                weight = weightM[j]
                sum += weight* math.fabs(featureM[i][j]-targetFM[j])
            ret.append(sum)
        return ret

    # Update the results window with the sorted results.
    def update_results(self, sortedTup, MDTuplesImg):

        # sort Manhattan Distance Arrays
        sorttuples = sorted(sortedTup, key=lambda x: x[1])
        # name list for future reference in button clicking
        #nameList = sorted(self.imgNameList, key=lambda x: MDTuplesImg[x])
        self.indexList = sorted(self.indexList, key=lambda i: sortedTup[i][1])
        # (name, previewPhoto) tuple list
        photoRemain = [(self.pixInfo.imgNameList[i], sorttuples[i][0])
                       for i in range(len(sorttuples))]
        # Place images on buttons, then on the canvas in order by distance.  Buttons envoke the inspect_pics method.
        # self.gridframe.grid_forget()
        self.gridframe.destroy()
        self.gridframe = tk.Frame(self.listcanvas)
        self.gridframe.update_idletasks()
        self.listcanvas.create_window(
            (0, 0), window=self.gridframe, anchor='nw')
        # get a grid view of images
        listsize = len(self.photoList)
        # 8 images per row, then
        rownum = int(math.ceil(listsize/float(self.colnum)))
        fullsize = (0, 0, (self.xmax*self.colnum), (self.ymax*rownum))
        for i in range(rownum):
            for j in range(self.colnum):
                if (i*self.colnum+j) < listsize:
                    pframe = tk.Frame(self.gridframe)
                    pframe.grid(row=i, column=j, sticky="news", padx=5, pady=5)
                    pho = photoRemain[i*self.colnum+j][1]
                    pImg = tk.Button(pframe, image=pho, fg='white',
                                  relief='flat', bg='white', bd=0, justify='center')
                    pImg.configure(image=pho)
                    pImg.photo = pho
                    #print("index :{}".format(self.indexList[i*self.colnum+j]))
                    pImg.config(
                        command=lambda f=self.imgNameList[self.indexList[i*self.colnum+j]]: self.inspect_pic(f))
                    pImg.grid(row=0, column=0, sticky='news')
                    if (self.rfbool.get() ==1):
                        # add checkbox
                        pcheckbox = tk.Checkbutton(pframe, text='Relevance', 
                            variable=self.relBoxBools[self.indexList[i*self.colnum+j]],
                            command=lambda x=self.indexList[i*self.colnum+j]: self.updateWeight(x))
                        if self.relevanceList[self.indexList[i*self.colnum+j]]==1:
                            pcheckbox.select()
                        pcheckbox.grid(row=1, column=0, sticky='news')
        # adjust size of canvas
        self.gridframe.update_idletasks()
        self.listcanvas.configure(yscrollcommand=self.listScrollbar.set)
        self.listcanvas.config(scrollregion=fullsize)
        self.listcanvas.yview_moveto(self.origY)
        self.listScrollbar.config(command=self.listcanvas.yview)

    # inspect the picture with filename, invoked in the button in selectPreviewFrame
    def inspect_pic(self, filename):
        image = Image.open(filename)
        # resize to fit the frame
        self.selectPreviewFrame.update()
        #print (self.resize_img(self.previewFrame.winfo_width(), self.previewFrame.winfo_height(), image))
        imResize = image.resize(self.resize_img(self.selectPreviewFrame.winfo_width()-10,
                                                self.selectPreviewFrame.winfo_height()-10, image), Image.ANTIALIAS)
        pho = ImageTk.PhotoImage(imResize)
        self.selectImg.configure(
            image=pho)
        self.selectImg.photo = pho

    # Open the pictures with the default operating system image viewer. Invoked in select_Folder button
    def inspect_pics(self):
        self.folderPath = filedialog.askdirectory(
            initialdir='./', title='Select your pictures folder')
        self.refImgLabel.config(text=self.folderPath)
        self.refreshCanvas()
        # os.startfile(filename)

    # add checkbox for the selectPreview pictures
    def add_checkbox(self):
        # add checkboxes
            # destroy grid inside canvas
            self.gridframe.destroy()
            # recreate
            self.gridframe = tk.Frame(self.listcanvas)
            self.gridframe.update_idletasks()
            self.listcanvas.create_window(
                (0, 0), window=self.gridframe, anchor='nw')
            # get a grid view of images
            listsize = len(self.photoList)
            # 8 images per row, then
            rownum = int(math.ceil(listsize/float(self.colnum)))
            fullsize = (0, 0, (self.xmax*self.colnum), (self.ymax*rownum))
            for i in range(rownum):
                for j in range(self.colnum):
                    if (i*self.colnum+j) < listsize:
                        pframe = tk.Frame(self.gridframe)
                        pframe.grid(row=i, column=j, sticky="news", padx=5, pady=5)
                        pho = self.photoList[self.indexList[i*self.colnum+j]]
                        pImg = tk.Button(pframe, image=pho, fg='white',
                                    relief='flat', bg='white', bd=0, justify='center')
                        pImg.configure(image=pho)
                        pImg.photo = pho
                        pImg.config(
                            command=lambda f=self.imgNameList[self.indexList[i*self.colnum+j]]: self.inspect_pic(f))
                        pImg.grid(row=0, column=0, sticky='news')
                        if self.rfbool.get()==1:
                            pcheckbox = tk.Checkbutton(pframe, text='Relevance', 
                                variable=self.relBoxBools[self.indexList[i*self.colnum+j]],
                                command=lambda x=self.indexList[i*self.colnum+j]: self.updateWeight(x))
                            pcheckbox.grid(row=1, column=0, sticky='news')
            # adjust size of canvas
            self.gridframe.update_idletasks()
            self.listcanvas.configure(yscrollcommand=self.listScrollbar.set)
            self.listcanvas.config(scrollregion=fullsize)
            self.listScrollbar.config(command=self.listcanvas.yview)

    # Refresh canvas when a new folder is selected
    def refreshCanvas(self):
        self.pixInfo.refreshPics(self.folderPath)
        self.colorCode = self.pixInfo.get_colorCode()
        self.intenCode = self.pixInfo.get_intenCode()
        # Full-sized images.
        self.imageList = self.pixInfo.get_imageList()
        # Thumbnail sized images.
        self.photoList = self.pixInfo.get_photoList()
        # img name list
        self.imgNameList = self.pixInfo.get_imgNameList()
        # self.gridframe.grid_forget()
        self.gridframe.destroy()
        self.gridframe = tk.Frame(self.listcanvas)
        self.gridframe.update_idletasks()
        self.listcanvas.create_window(
            (0, 0), window=self.gridframe, anchor='nw')
        # get a grid view of images
        listsize = len(self.photoList)
        # 8 images per row, then
        rownum = int(math.ceil(listsize/float(self.colnum)))
        fullsize = (0, 0, (self.xmax*self.colnum), (self.ymax*rownum))
        for i in range(rownum):
            for j in range(self.colnum):
                if (i*self.colnum+j) < listsize:
                    pho = self.photoList[i*self.colnum+j]
                    pImg = tk.Button(self.gridframe, image=pho, fg='white',
                                  relief='flat', bg='white', bd=0, justify='center')
                    pImg.configure(image=pho)
                    pImg.photo = pho
                    pImg.config(
                        command=lambda f=self.imgNameList[i*self.colnum+j]: self.inspect_pic(f))
                    pImg.grid(row=i, column=j, sticky="news", padx=5, pady=5)
        # adjust size of canvas
        self.gridframe.update_idletasks()
        self.listcanvas.configure(yscrollcommand=self.listScrollbar.set)
        self.listcanvas.config(scrollregion=fullsize)
        self.listScrollbar.config(command=self.listcanvas.yview)

        # update listbox
        self.plist.delete(0, 'end')
        for i in range(len(self.imageList)):
            self.plist.insert(i, self.getFilename(self.imageList[i].filename))

        # update Preview
        image = self.imageList[0]
        self.previewFrame.update()
        imResize = image.resize(self.resize_img(self.previewFrame.winfo_width(
        ), self.previewFrame.winfo_height(), image), Image.ANTIALIAS)
        pho = ImageTk.PhotoImage(imResize)
        self.previewImg.configure(
            image=pho)
        self.previewImg.photo = pho
        # update SelectPreview label to blank again
        self.selectImg.destroy()
        self.selectImg = tk.Label(self.selectPreviewFrame)
        self.selectImg.grid(row=0, column=0, sticky="news")

    def updateWeight(self, index):
        relBool = self.relBoxBools[index]
        # print("clicked index: {}; onvalue: {}".format(index, relBool.get()))
        # print("filename of index: {}".format(self.imgNameList[index]))
        self.relevanceList[index] = relBool.get()

    # Truncate the long filepath to only the filename
    def getFilename(self, fn):
        i = fn.rfind('/')
        return fn[i+1:]
    
    # reset the program
    def reset(self):
        self.indexList = list(range(len(self.imageList)))
        self.relevanceList = [0]*len(self.imageList)
        self.relBoxBools = [tk.IntVar() for i in range(len(self.imageList))]
        self.rfbox.deselect()
        self.gridframe.destroy()
        self.gridframe = tk.Frame(self.listcanvas)
        self.gridframe.update_idletasks()
        self.listcanvas.create_window(
            (0, 0), window=self.gridframe, anchor='nw')
        # get a grid view of images
        listsize = len(self.photoList)
        # 8 images per row, then
        rownum = int(math.ceil(listsize/float(self.colnum)))
        fullsize = (0, 0, (self.xmax*self.colnum), (self.ymax*rownum))
        for i in range(rownum):
            for j in range(self.colnum):
                if (i*self.colnum+j) < listsize:
                    pho = self.photoList[i*self.colnum+j]
                    pImg = tk.Button(self.gridframe, image=pho, fg='white',
                                  relief='flat', bg='white', bd=0, justify='center')
                    pImg.configure(image=pho)
                    pImg.photo = pho
                    pImg.config(
                        command=lambda f=self.imgNameList[i*self.colnum+j]: self.inspect_pic(f))
                    pImg.grid(row=i, column=j, sticky="news", padx=5, pady=5)
        # adjust size of canvas
        self.gridframe.update_idletasks()
        self.listcanvas.configure(yscrollcommand=self.listScrollbar.set)
        self.listcanvas.config(scrollregion=fullsize)
        self.listScrollbar.config(command=self.listcanvas.yview)


# Executable section.
if __name__ == '__main__':

    root = tk.Tk()
    root.title('Image Analysis Tool')

    pixInfo = PixInfo(root)

    imageViewer = ImageViewer(root, pixInfo)

    root.mainloop()
