from skimage import io
import glob
import os
import cv2
from pydoc import doc
import numpy as np
import matplotlib.pyplot as plt
import pickle

from keras import preprocessing

#A COLLECTION OF FUNCTIONS THAT ARE CALLED FREQUENTLY IN THE TRACKER BACKEND
#Written by John ~25 hours

#This function takes in a labeled file of images and connects it to an array with ground-truth labels
def dataset(file_list, size=(400,512), flattened=False): #,size=(300,180)
  data = []
  for i, file in enumerate(file_list):
    image = plt.imread(file)
    #image = transform.resize(image, size, mode='constant')
    if flattened:
      image = image.flatten()

    data.append(image)

  labels = [1 if f.split("/")[-1][0] == 'W' else 0 for f in file_list]


  return np.array(data), np.array(labels)
 
#takes in a file list and loads the images into an np array
def ImgArray(file_list, step=1):
  outputArray=[]
  z = 0
  for i, file in enumerate(file_list):
    if (z%step)==0:
      image = plt.imread(file)
      outputArray.append(image)
    z=z+1
  return np.array(outputArray)

#takes in a video and puts out each frame as a jpg
def vidToImage(video_file):
  video = cv2.VideoCapture(video_file)

  try:
    if not os.path.exists('frames'):
        os.makedirs('frames')
  except OSError:
    print ('Error: Creating directory of data')
  
  currentframe = 0
  
  while(True):
      
    # reading from frame
    ret,frame = video.read()
  
    if ret:
        # if video is still left continue creating images
        name = './frames/frame' + str(numToIndex(currentframe, 4)) + '.jpg'
        print ('Creating...' + name)
  
        # writing the extracted images
        frame = cv2.resize(frame,(512,400))
        cv2.imwrite(name, frame)
  
        # increasing counter so that it will
        # show how many frames are created
        currentframe += 1
    else:
        break
    # Release all space and windows once done
  video.release()
  cv2.destroyAllWindows()

def vidToImage2(video_file, outFolder='frames'):
  video = cv2.VideoCapture(video_file )

  try:
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)
  except OSError:
    print ('Error: Creating directory of data')

  currentframe = 0


  while(True):
      
    # reading from frame
    ret,frame = video.read()

    if ret:
        # if video is still left continue creating images
        name = './'+ outFolder +'/frame' + str(numToIndex(currentframe, 5)) + '.jpg'
        print ('Creating...' + name)

        # writing the extracted images
        frame= cv2.resize(frame,(512,400))
        cv2.imwrite(name, frame)

        # increasing counter so that it will
        # show how many frames are created
        currentframe += 1
    else:
        break
    # Release all space and windows once done
  video.release()
  cv2.destroyAllWindows()


def ImgArrayResize(path,step=1,resizeDims=(64,64,3)):
    list1= getImgList(path)
    imgList= []
    for i, file in enumerate(list1):
        a= np.asarray(preprocessing.image.load_img(file, target_size=resizeDims))
        imgList.append(a)
    imgArray= np.asarray(imgList)
    return imgArray

#gets a list of all images in a directory
def getImgList(path):
  imlist = glob.glob(os.path.join(path, '*.jpg'))
  imlist.sort()
  return imlist 

#returns a np image array from a directory of image files
def folderToImgArray(ImgPath, step=1):
  imlist= glob.glob(os.path.join(ImgPath, '*.jpg'))
  imlist.sort()
  output= ImgArray(imlist, step)
  return output

#folder for prepping image arrays for Neural Net training
def folderToResizeImgArray(ImgPath,newDim):
  imlist= glob.glob(os.path.join(ImgPath, '*.jpg'))
  imlist.sort()
  outputArray=[]
  for file in enumerate(imlist):
    image= preprocessing.image.load_img(file, target_size=newDim)
    outputArray.append(image)
  return outputArray

  
#this loads and processes a single image to be passed to the Neural net for a prediction
def loadNetworkImage(path):
  b= preprocessing.image.load_img(path, target_size=(64,64,3))
  return b
  


## This block gets the list of x,y positions for each frame
def getPosList(imgArray, stepSize=1):
  #poslist= np.zeros((listlen-1, 2)) #x,y
  poslist= np.empty((0,2), int)


  for i in range(0,imgArray.shape[0]-1,stepSize):
    img1=imgArray[i,:,:,:]
    img2=imgArray[i+1,:,:,:]

    #frame_compare
    pos=frame_compare(img1,img2)
    #print(pos)
    
    poslist= np.append(poslist,np.array([pos]),axis=0)
    #All i want to do is add new paired x and y values to a new row... how is this
    #so much to ask



  return poslist

#poslist= getPosList(data,5)


#Pulls a sub image from a larger image at the specified location
def pullSub(inImg, pos, outputSize):
  if outputSize[0]>inImg.shape[0] or outputSize[1]>inImg.shape[1]:
    return "output bigger than image"
  xmin=int(pos[0]-(outputSize[0]/2))
  xmax=int(pos[0]+(outputSize[0]/2))
  ymin=int(pos[1]-(outputSize[1]/2))
  ymax=int(pos[1]+(outputSize[1]/2))
  if xmin<0:
    xmin=0
  if xmax>(inImg.shape[1]):
    xmax=(inImg.shape[1]-1)
  if ymin<0:
    ymin=0
  if ymax>(inImg.shape[0]):
    ymax=(inImg.shape[0]-1)

  subImg=inImg[ymin:ymax, xmin:xmax]

  return subImg


#This function is the core of the tracking system, compares 2 sequential frames for movement between them
def frame_compare(img1,img2,showImg=False):
  #plt.imshow(img1)
  #plt.imshow(img2)
  #sum=img2-img1
  sum= np.zeros(img2.shape)

  rowLen=sum.shape[0]
  colLen=sum.shape[1]

  for pixelx in range(0,colLen):
    for pixely in range(0,rowLen): #here
      for pixelrgb in range(0,3):
        if img2[pixely,pixelx,pixelrgb] >= img1[pixely,pixelx,pixelrgb]:
          sum[pixely,pixelx,pixelrgb]= img2[pixely,pixelx,pixelrgb]-img1[pixely,pixelx,pixelrgb]
        else:
          sum[pixely,pixelx,pixelrgb]= img1[pixely,pixelx,pixelrgb]-img2[pixely,pixelx,pixelrgb]

  ##print(img1[1:5,1:5])
  #print(img2[1:5,1:5])
  #print(sum[1:5,1:5])

  #print(sum.shape[0])


  dif_sens=40 #remove later
  dif_sense= 10 #was 10

  motion_sensitivity=1.1 * 1000

  xavg=0
  yavg=0


  #for xx in range(0, sum.shape[1]):
  # for yy in range(0, sum.shape[0]):
  #   for zz in range(0, sum.shape[2]):
  #     if sum[yy, xx, zz]<= dif_sens:
  #        sum[yy,xx,zz]=0


  #print(sum[0:10, 0:10])

  difArray= np.zeros((sum.shape[0],sum.shape[1]))
  #print(difArray.shape)
  totPixelDif=0
  numNonZpixels=0
  for pixelx in range(0,colLen):
    for pixely in range(0,rowLen):
      for pixelrgb in range(0,3):
        chanPixelDif= sum[pixely,pixelx,pixelrgb]
        totPixelDif = totPixelDif + chanPixelDif
      if totPixelDif > dif_sense*3:
        #print('hi')
        difArray[pixely,pixelx]=totPixelDif
      totPixelDif=0

  #print(difArray)
  difArray[:,:]= difArray[:,:]/3
  #print(difArray)

  #print(difArray)
  weightTot=0
  for pixelx in range(0,colLen):
    for pixely in range(0,rowLen):
      xavg=xavg + (difArray[pixely,pixelx]*pixelx)
      yavg=yavg + (difArray[pixely,pixelx]*pixely)

      weightTot= weightTot + difArray[pixely,pixelx]

  if xavg>motion_sensitivity:
    xavg=round(xavg/weightTot)
    yavg=round(yavg/weightTot)
    pos=[xavg, yavg]
  else: #returns 1,1 if change below threshold
    xavg=1
    yavg=1
    pos=[xavg, yavg]

  size=3

  #imshow
  #print(difArray)
  if showImg==True:
    plt.subplot(2,2,1)
    plt.imshow(sum)
    plt.subplot(2,2,2)
    plt.imshow(difArray)
    plt.subplot(2,2,3)
    difArrayMarked= difArray
    #difArrayMarked[round(yavg-size):round(yavg+size), round(xavg-size):round(xavg+size)]= 1000000
    plt.imshow(difArrayMarked)
    print(xavg,yavg)
    plt.scatter(xavg,yavg)
    plt.subplot(2,2,4)
    plt.imshow(img2)

  #Bring Back
  # plt.subplot(1,1,1)
  # plt.imshow(img2)
  # plt.scatter(xavg,yavg)

  return pos


#gets list of images within a folder location
def getImgList(ImgPath):
  imlist = glob.glob(os.path.join(ImgPath, '*.jpg'))
  imlist.sort()
  return imlist

#saves a Python List to a pickle file with name outFilename
def listToFile(listName, outFilename):
    outfile= open(outFilename,'wb')
    pickle.dump(listName,outfile)
    outfile.close()

#retrieves python lists from pickle memory
def listFromFile(inFilename):
    infile= open(inFilename,'rb')
    out_object= pickle.load(infile)
    infile.close()
    return out_object

#Takes an integer counting number and appends the correct number of preceeding zeros
#meant to prepare image filenames sequentially
def numToIndex(n,numDigits):
  out=''
  num=str(n)
  for i in range(0,numDigits-len(num)):
    out= out+'0'
  out= out+ num
  return out

def sort_rename(path):
  #Takes in a path to a file of numbered, sequential images
  #renames all the files in the directory with '_*' sequential number from 1:n added

  ldseg = glob.glob(os.path.join(path, '*.jpg')) #pulls list of all files in folder
  print('Dataset contains {} images'.format(len(ldseg))) #returns how many images in list
  listlen= len(ldseg)

  print(ldseg) #For some reason, glob pulls the files in a wrong order
  ldseg.sort() #this sorts them alphabetically ASSUMES IMAGES ARE NUMBERED ALREADY/PROPERLY
  print(ldseg)

  i=1
  for filename in ldseg:
    dst =  filename.split('_')[0] + '_' + numToIndex(i,5) + '.jpg' #removes original index marker after a "_"
    print(dst)
    print(filename)
    src =filename
    print(src)
    print(dst)
    os.rename(src, dst)
    i += 1


#Renames all numbered files in a folder with a preceeding zeros tag
def tempRename(path):
  ldseg = glob.glob(os.path.join(path, '*.jpg')) #pulls list of all files in folder
  print('Dataset contains {} images'.format(len(ldseg))) #returns how many images in list
  listlen= len(ldseg)

  for filename in ldseg:
    end= filename.split('_')[-1]
    print(end)
    if len(end)<9:
      end= '000'+ end
      dst= filename.split('_')[0] + end
      os.rename(filename,dst)
    print(end)
    

#Takes in an array of sequential images, and the associated tracked position list
#Returns a window with the position markers overlayed on the image
def showLabeledVid(imgArray,posList,fps=30,overlay=True):
    fg= plt.figure()
    ax = fg.gca()
    h = ax.imshow(imgArray[0])

    i=0
    if overlay:
        #for img in imgs:
        for ii in range(1, posList.shape[0]):
            h.set_data(imgArray[ii])
            plt.draw()
            a = plt.scatter(posList[ii-1,0],posList[ii-1,1],s=3)
            plt.pause(fps/60)
            a.remove()
            i+=1
    else:
        for ii in range(1, posList.shape[0]):
            h.set_data(imgArray[ii])
            plt.draw()
            plt.pause(1/fps)
            i+=1



#sort_rename('D:/WormTrack/WormData/Labeled/')
# a=getImgList('D:/WormTrack/WormData/Labeled_Backup/')
# print(a[0:5])
# print('hello there')
# a.sort()
# print(a[0:5])
#sort_rename('D:/WormTrack/WormData/LabeledBackup/')
