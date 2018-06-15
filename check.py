def get_image_list_and_labels_win_IAM_cap(path):
    class_names = []       
    file_list = []
    labels = []
    for (dirpath1, dirnames,fnames) in walk(path):
        #print dirpath1, dirnames,fnames
       #file_list.extend(filenames)
        break
    for dir_n in dirnames:
        sub_dir=os.path.join(dirpath1, dir_n)
        #print sub_dir
        for dp, dn,filenames in walk(sub_dir):
            #print dp, dn,filenames
            for fn in filenames:
                if fn == 'Thumbs.db' or fn == '.DS_Store':
                    continue
                else:
                    file_path=os.path.join(dp,fn)      
                    #print file_path
                    class_name=fn
                    #print (class_name)
                    file_list.append(file_path)
                    #nbr = class_name #int(class_name[6:])-1
                    labels.append(class_name)
                
    return file_list,labels

def ver_hor_twoBlocksTest(Collinear_BB):
    ver_hor_pos = -1
    spacing = -1   ### distance between two BBs.....0 if its overlapped or nested
    Order_Changed = False
    sorted_BB = list(Collinear_BB)
    sorted_BB1 = list(Collinear_BB)

    if (Collinear_BB[0][0] >= Collinear_BB[1][0]) and (Collinear_BB[0][1] > Collinear_BB[1][1]):
        sorted_BB[0] = Collinear_BB[1]
        sorted_BB[1] = Collinear_BB[0]
        sorted_BB1[0] = Collinear_BB[1]
        sorted_BB1[1] = Collinear_BB[0]
        Order_Changed = True
    elif (Collinear_BB[0][0] > Collinear_BB[1][0]):
        sorted_BB[0] = Collinear_BB[1]
        sorted_BB[1] = Collinear_BB[0]
        Order_Changed = True
    elif (Collinear_BB[0][1] > Collinear_BB[1][1]):
        sorted_BB[0] = Collinear_BB[1]
        sorted_BB[1] = Collinear_BB[0]
        sorted_BB1[0] = Collinear_BB[1]
        sorted_BB1[1] = Collinear_BB[0]
        Order_Changed = True
        
        

    if (sorted_BB1[0][2] < sorted_BB1[1][0]) and (sorted_BB1[0][3] < sorted_BB1[1][1]):
        ver_hor_pos = 4
        spacing=  sorted_BB1[1][0] - sorted_BB1[0][2]  

    elif (sorted_BB1[0][2] > sorted_BB1[1][0]) and (sorted_BB1[0][3] > sorted_BB1[1][1]):
        ver_hor_pos = 5
        spacing =  sorted_BB1[0][3] - sorted_BB1[1][1]
        
    
    elif (sorted_BB[0][2] < sorted_BB[1][0]) and (sorted_BB[0][3] > sorted_BB[1][1]):
        ver_hor_pos = 1
        spacing=  sorted_BB[1][0] - sorted_BB[0][2]  

    elif (sorted_BB[0][2] > sorted_BB[1][0]) and (sorted_BB[0][3] < sorted_BB[1][1]):
        ver_hor_pos = 0
        spacing = sorted_BB[1][1] - sorted_BB[0][3] 

    elif (sorted_BB[0][0] <= sorted_BB[1][0]) and (sorted_BB[0][1] < sorted_BB[1][1]):
        # ver_hor_pos=2
        spacing =  0
        if (sorted_BB[0][2] > sorted_BB[1][2]) and (sorted_BB[0][3] > sorted_BB[1][3]):
            ver_hor_pos = 3
        elif (sorted_BB[0][2] > sorted_BB[1][0]) and (sorted_BB[0][3] > sorted_BB[1][1]):
            if (sorted_BB[0][2] < sorted_BB[1][2]) or (sorted_BB[0][3] < sorted_BB[1][3]):
                ver_hor_pos = 2

    return ver_hor_pos, Order_Changed, sorted_BB, spacing 

def check_overlap(n,BBs):
    #cnt_check = contours[n]
    #x_check,y_check,w_check,h_check = cv2.boundingRect(cnt_check)
    SPACE_OVERLAP_TH = 1
    BB_check= BBs[n]
    OVERALAPPED_FLAG=False
    OVERLAPPED_BBs_Array=[]
    OVERLAPPED_BBs_Array.append(BB_check)
    OVERLAPPED_BBs_Index=[]
    for k in range(n+1,len(BBs)):
        BBoxes=[]
        BBoxes.append(BB_check)
        #cnt = contours[n]
        #x,y,w,h = cv2.boundingRect(cnt)
        BBoxes.append(BBs[k])
        #print BBoxes
        ver_hor_pos, Order_Changed, sorted_BB,spacing= ver_hor_twoBlocksTest(BBoxes)
        #print ("spacing" + ': ' +str(spacing) + ' ' + "ver_hor_pos" + ': ' + str(ver_hor_pos))
        # ver_hor_pos ===>>  0-> vertical, 1-> horizontal, 2-> overlap, 3-> nested
        # ignore here --> Order_Changed, sorted_BB
            
        if ver_hor_pos > 1:
            OVERALAPPED_FLAG = True
            OVERLAPPED_BBs_Array.append(BBs[k])
            OVERLAPPED_BBs_Index.append(k)
        elif  (spacing >= 0) and (spacing < SPACE_OVERLAP_TH):
            OVERALAPPED_FLAG = True
            OVERLAPPED_BBs_Array.append(BBs[k])
            OVERLAPPED_BBs_Index.append(k)
            
    
        
    return OVERALAPPED_FLAG,OVERLAPPED_BBs_Array,OVERLAPPED_BBs_Index