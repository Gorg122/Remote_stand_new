import os

import cv2
import time

def Video():
    #cap = cv2.VideoCapture(0)

    HIGH_VALUE = 10000
    WIDTH = HIGH_VALUE
    HEIGHT = HIGH_VALUE

    capture = cv2.VideoCapture(0)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #focus = int(capture.get(cv2.CAP_PROP_AUTOFOCUS))
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    #capture.set(cv2.CAP_PROP_FOCUS, 200)
    capture.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))


    # Get the Default resolutions
    #frame_width = int(capture.get(4))
    #frame_height = int(capture.get(4))
    cur_dir = os.getcwd()
    #os.chdir(cur_dir)
    print(cur_dir)
    # print(width)
    # print(height)
    print(frame_width)
    print(frame_height)
    files = "video_timing.txt"
    timing = open(files)
    time_rest = timing.readline()
    print(time_rest)
    timing.close()

    tik = time.time()
    print(tik)
    tok = 0.0
    # Define the codec and filename.
    #fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    #out = cv2.VideoWriter('output.mp4',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (frame_width,frame_height))
    out = cv2.VideoWriter('video/video.mp4', fourcc, 30.0, (frame_width, frame_height))

    print("tok = ", tok)
    print("tok-tik = ", tok - tik)
    start = 0
    while(capture.isOpened() and (tok-tik<=int(time_rest) or (start == 1))):
        ret, frame = capture.read()
        tok = time.time()
        #print("tok-tik = ", tok - tik)
        if ret==True :
            #print("tok-tik = ", tok - tik)
            # write the  frame
            out.write(frame)
            #cv2.imshow('frame',frame)
            #if cv2.waitKey(1) & 0xFF == ord('q') & int(tok - tik) >= 30:
            if int(tok - tik) >= int(time_rest*3):
                break
        else:
            break

    # Release everything if job is finished
    capture.release()
    out.release()
    cv2.destroyAllWindows()
    time.sleep(4)
    files_2 = "video_done.txt"
    done_chek = open(files_2, "w")
    done_chek.write("done")
    done_chek.close()
    quit()
#if __name__ == '__main__':
Video()