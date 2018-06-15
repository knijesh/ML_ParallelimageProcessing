from util import *
from check import get_image_list_and_labels_win_IAM_cap,ver_hor_twoBlocksTest,check_overlap
import cv2
import math
import numpy as np
from multiprocessing import Queue
from keras.models import load_model

def pred(file_list,labels,q):
    Output_list =[]
    file_Output_list1 = []
    new_Char_BBs = []
    count = 0
    Model_File = 'C:\\Work\\Barclays\\modelNormalTapeFontChar1_13k_offaligned_48by32.h5'
    model=load_model(Model_File)
    for file_path in file_list: 
        #print(file_path)
        count = count+1
        file_path1 = file_path.split("\\")[-2] +'/'+file_path.split("\\")[-1]
        #print file_path1
        #print '/Users/g01179665/Desktop/PPI Templates/PPI/NormalTape Cropped/'+ file_path1   
        img = cv2.imread(file_path)
        #print(img)
        if img is None:
            print ('Blank Image')
        else:
            count = count+1
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 80, 120, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, math.pi/2, 2, None, 30, 1)
            y3,x3,z3=img.shape
            list2 = []
            list2y = []
            a,b,c = lines.shape
            for i in range(a):
                list1 = [lines[i][0][0], lines[i][0][1],lines[i][0][0]-lines[i][0][2]]
                list2.append(list1)
            list2 = [n for n in list2 if n[2]==0 ]
            list2 = sorted(list2, key=lambda x:x[0], reverse=False)
            x = list2[0][0]
            y=  list2[0][1]
            IntensityAvg = gray.mean(axis=1)
            IntensityAvg=IntensityAvg.tolist()
            IntensityAvg1  = [[i,a,abs(a-b)] for i,(a,b) in enumerate(zip(IntensityAvg,IntensityAvg[1:]))]
            ymap = [y for y,a,b in IntensityAvg1 if a >40][0]

            orig = img.copy()
            #print(orig)
            w=134
            x1=x+3
            x2=x+w
            y1=max(1,ymap-40)
            y2=y1+1100
            #y2 =y1+1000
            h=y2-y1   
            #print(h)        

            #cv2.rectangle(orig,(x1,y1),(x2,y2),(0,255,0),2)
            #cv2.rectangle(orig,(x1,y1),(x2,y2),(0,255,0),2)
            im = gray[y1:y2, x1:x2]

            img1=im.copy()
            img=im.copy()
            img2=im.copy()
            img3=im.copy()
            img4 =im.copy()
            im_sum=np.sum(img1,axis=0)
            noise_thresh= np.max(im_sum)/4 #### Column profiling threshold
            for k in range(len(im_sum)):
                if im_sum[k] < noise_thresh:
                    img2[:,k]=0



            im_sum=np.sum(img2,axis=1)
            noise_thresh= 255*2        #### Row profiling threshold
            for k in range(len(im_sum)):
                if im_sum[k] < noise_thresh:
                    img2[k,:]=0

            ret,thresh = cv2.threshold(img2,100,255,0)
            im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img3, contours, -1, (128,128,128), 3)
            contour_noise_thres= 120
            img4=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

            dimlist = []
            charlist = []
            Char_BBs=[]
            Dot_BBs=[]
            for n in range(len(contours)):
                cnt = contours[n]
                c_area = cv2.contourArea(cnt)
                x1,y1,w,h = cv2.boundingRect(cnt)
                #dimlist.append([x, y, w, h])
                #BB_area=w*h

                #print("BB_area" + str(BB_area))
                x2=x1+w
                y2=y1+h
                CC_area = np.count_nonzero(thresh[y1:y2,x1:x2]) #number of while pixel 

                if CC_area > contour_noise_thres:
                    #print BB_area,CC_area    
                    dimlist.append([x1, y1, w, h,CC_area])
                    dimlist = sorted(dimlist, key=lambda x:x[1], reverse=False)
                    dimlist = [n for n in dimlist if n[3]<75 and n[2] <75 and n[2]>10 and n[3]>10]
                    #print("CC_area" + str(CC_area))
            for x1,y1,w,h,CC_area in dimlist:
                BB_area=w*h
                #print("BB_area" + str(BB_area))
                x2=x1+w
                y2=y1+h
                if CC_area > 0.5*BB_area and BB_area <450:
                    cv2.rectangle(img4,(x1,y1),(x2,y2),(0,0,255),2)
                    Char_BBs.append([x1,y1,x2,y2,0])
                else:
                    cv2.rectangle(img4,(x1,y1),(x2,y2),(0,255,0),2)
                    Char_BBs.append([x1,y1,x2,y2,1])
            OVERLAPPED_BB=False
            OVERALAPPED_TO_IGNORE=np.zeros((1,len(Char_BBs)),np.uint8)
            new_Char_BBs=list(Char_BBs)
            for t in range(len(Char_BBs)):
                if OVERALAPPED_TO_IGNORE[0,t]==1:
                    continue
                OVERALAPPED_FLAG,OVERLAPPED_BBs_Array,OVERLAPPED_BBs_Index=check_overlap(t,Char_BBs)
                #print (OVERALAPPED_FLAG)

                if OVERALAPPED_FLAG:
                    #print OVERLAPPED_BBs_Index
                    for Ind in OVERLAPPED_BBs_Index :
                        OVERALAPPED_TO_IGNORE[0,Ind] =1
                    x1_arr=[]
                    y1_arr=[]
                    x2_arr=[]
                    y2_arr=[]
                    flag_arr =[]
                    #print OVERLAPPED_BBs_Array
                    for n in range(len(OVERLAPPED_BBs_Array)):
                        #cnt = contours[n]
                        #x,y,w,h = cv2.boundingRect(cnt)
                        x1_arr.append(OVERLAPPED_BBs_Array[n][0])
                        y1_arr.append(OVERLAPPED_BBs_Array[n][1])
                        x2_arr.append(OVERLAPPED_BBs_Array[n][2])
                        y2_arr.append(OVERLAPPED_BBs_Array[n][3])
                        flag_arr.append(OVERLAPPED_BBs_Array[n][4])
                    x1=min(x1_arr)
                    y1=min(y1_arr)
                    x2=max(x2_arr)
                    y2=max(y2_arr)
                    flag=max(flag_arr)

                    new_Char_BBs[t]=[x1,y1,x2,y2,flag]

            ind_dec=0
            for t in range(len(Char_BBs)):
                if OVERALAPPED_TO_IGNORE[0,t]==1:
                    del new_Char_BBs[t-ind_dec]
                    ind_dec += 1 
            dimlist1 =[]
            if len(new_Char_BBs) >0 :
                #print (len(new_Char_BBs))
                if len(new_Char_BBs) > 1 :
                    #print(len(new))
                    #new_Char_BBs = [new_Char_BBs[0] + [new_Char_BBs[1][1] -new_Char_BBs[0][3]]] + [new_Char_BBs[1] + [new_Char_BBs[2][1] -new_Char_BBs[1][3]]] + [ [a[0],a[1],a[2],a[3],a[4],a[1]-b[3]] for i,(a,b) in enumerate(zip(new_Char_BBs[1:],new_Char_BBs))][1:]
                    new_Char_BBs = [new_Char_BBs[0] + [new_Char_BBs[1][1] -new_Char_BBs[0][3]]] + [ [a[0],a[1],a[2],a[3],a[4],a[1]-b[3]] for i,(a,b) in enumerate(zip(new_Char_BBs[1:],new_Char_BBs))]
                    avgdist = np.sum(new_Char_BBs,axis=0)/len(new_Char_BBs)
                    avgdist = avgdist[5]
                    new_Char_BBs1 = [n for n in new_Char_BBs if n[5]<4*avgdist]
                else:
                    new_Char_BBs = new_Char_BBs[0] + [5]
                    new_Char_BBs1 = new_Char_BBs

                #new_Char_BBs = [new_Char_BBs[0] + [0]] + [ [a[0],a[1],a[2],a[3],a[4],a[1]-b[1]] for i,(a,b) in enumerate(zip(new_Char_BBs[1:],new_Char_BBs))]
                img5=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)
                for d in range(len(new_Char_BBs1)):
                    if new_Char_BBs1[d][4] == 1:
                        cv2.rectangle(img5,(new_Char_BBs1[d][0],new_Char_BBs1[d][1]),(new_Char_BBs1[d][2],new_Char_BBs1[d][3]),(0,255,0),2)
                    else:
                        cv2.rectangle(img5,(new_Char_BBs1[d][0],new_Char_BBs1[d][1]),(new_Char_BBs1[d][2],new_Char_BBs1[d][3]),(0,0,255),2)
                    dimlist1.append([new_Char_BBs1[d][0], new_Char_BBs1[d][1], new_Char_BBs1[d][2], new_Char_BBs1[d][3], new_Char_BBs1[d][4]])

                dimlist1 = sorted(dimlist1, key=lambda x:x[1], reverse=False)
            charlist = []
            #print(dimlist1)
            for x1,y1,x2,y2,flag in dimlist1:
                #print(flag)
                if flag == 0:
                    Char = '.'
                    charlist.append(Char)
                else :
                    gray = cv2.cvtColor(img5, cv2.COLOR_BGR2GRAY)
                    roi = gray[y1:y2, x1:x2]              
                    crop_img = cv2.resize(roi, (32, 48))
                    #crop_img=  cv2.bitwise_not(crop_img)
                    thresh = crop_img.flatten() / 255.0
                    Test = thresh.reshape(1, 1, 48, 32).astype('float32')
                    Test = thresh.reshape(1, 1, 48, 32).astype('float32')
                    predictC = model.predict(Test)
                    #print(predictC)
                    Char = np.argmax(predictC)
                    #print(Char)
                    charlist.append(Char)
                if '.' in charlist:
                    result = charlist.index('.')
                    charlist1 = charlist[max(result-5,0):result] + charlist[result:]
                else:
                    charlist1 = charlist
                Output = ''.join(str(e) for e in charlist1)
                #print Output
                #cv2.imwrite('/Users/g01179665/Desktop/PPI Templates/PPI/POC/Results/Normal Tape/'+ file_path.split("/")[-2] +'/' + file_path.split("/")[-1].split(".")[0] + '_' +  Output +'.tif',img5)

                Output_list.append(Output)
                file_Output_list1.append(file_path.split("/")[-1])
            q.put(charlist)
    #return charlist
            



