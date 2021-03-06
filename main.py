import pandas as pd
import cv2
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from PIL import Image
import PIL.ImageOps
import os,ssl,time

#Setting an HTTPS Context to fetch data from OpenML
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context


X, y = fetch_openml('mnist_784', version=1, return_X_y=True)
print(pd.Series(y).value_counts())
classes = ['0', '1', '2','3', '4','5', '6', '7', '8', '9']
nclasses = len(classes)

X_train,X_test,y_train,y_test=train_test_split(X,y,random_state=9,train_size=7500,test_size=2500)
X_train_scale=X_train/255.0
X_test_scale=X_test/255.0
clf=LogisticRegression(solver="saga",multi_class='multinomial').fit(X_train_scale,y_train)

y_pred=clf.predict(X_test_scale)
print(accuracy_score(y_test,y_pred))

cap=cv2.VideoCapture(0)
while (True):
    try:
        ret,frame=cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        height, width = gray.shape
        upper_left = (int(width / 2 - 56), int(height / 2 - 56))
        bottom_right = (int(width / 2 + 56), int(height / 2 + 56))
        cv2.rectangle(gray, upper_left, bottom_right, (0, 255, 0), 2)

        roi = gray[upper_left[1]:bottom_right[1], upper_left[0]:bottom_right[0]]

        im_pil=Image.fromarray(roi)
        im_bg=im_pil.convert('L')
        im_bg__resz=im_bg.resize((28,28),Image.ANTIALIAS)
        im_bg__resz_inv=PIL.ImageOps.invert(im_bg__resz)
        pxl_fltr=20

        min_pixel = np.percentile(im_bg__resz_inv, pxl_fltr)
        im_bg__resz_inv_scaled = np.clip(im_bg__resz_inv-min_pixel, 0, 255)

        max_pixel = np.max(im_bg__resz_inv, pxl_fltr)
        im_bg__resz_inv_scaled = np.asarray(im_bg__resz_inv_scaled)/max_pixel

        tstSmpl=np.array(im_bg__resz_inv_scaled).reshape(1,784)
        tst_Pred=clf.predict(tstSmpl)

        print("Predicted Classes",tst_Pred)
        cv2.imshow('Fraem', gray)
        
        if cv2.waitKey(1)&0xFF==ord('q'):
            break
    except Exception as e:
        pass
cap.release()
cv2.destroyAllWindows()