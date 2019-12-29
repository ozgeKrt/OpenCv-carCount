import cv2 as cv
import numpy as np

class koordinatTut:
    def __init__(self,x,y):
        self.x=x
        self.y=y

class Sensor:
    def __init__(self,koordinat1,koordinat2,genislik,yukseklik):
        self.koordinat1=koordinat1
        self.koordinat2=koordinat2
        self.genislik=genislik
        self.yukseklik=yukseklik

        self.maske_alan=abs(self.koordinat2.x-self.koordinat1.x)*abs(self.koordinat2.y-self.koordinat1.y)

        self.Maske=np.zeros((yukseklik,genislik,1),np.uint8)
        cv.rectangle(self.Maske,(self.koordinat1.x,self.koordinat1.y),(self.koordinat2.x,self.koordinat2.y),(255),cv.FILLED)

        self.algilayici_durum=False
        self.arac_sayisi=0;

cap = cv.VideoCapture("4.Geçit Stream 1.2.mp4")
fgbg =cv.createBackgroundSubtractorMOG2()
kernel = np.ones((6,6),np.uint8)

# aracin algilanacagi alaninin koordinatlari veriliyor
algilayici1 = Sensor(koordinatTut(200, 320), koordinatTut(120,340), 950, 1080)
algilayici2 = Sensor(koordinatTut(500, 320), koordinatTut(420, 340), 950, 1080)

maske = np.zeros((1080, 950, 1), np.uint8)
cv.rectangle(maske, (550, 250), (80, 450), (255), cv.FILLED)
alanDurum=False

while True:
    ret,kare=cap.read()
    kesilmiş_kare=kare[0:1080,650:1600]
    kare_gri=cv.cvtColor(kesilmiş_kare,cv.COLOR_BGR2GRAY)
    fgkare = fgbg.apply(kare_gri)

    closing = cv.morphologyEx(fgkare, cv.MORPH_CLOSE, kernel)
    opening = cv.morphologyEx(closing, cv.MORPH_OPEN, kernel)

    median = cv.medianBlur(opening, 15)

    #filtrelemeden sonra beyaz olan alanlarinin yerlerini bulur ve contours dizisi icerisinde tutar
    contours, hierarchy=cv.findContours(median,cv.RETR_TREE,cv.CHAIN_APPROX_NONE)
    sonuc=kesilmiş_kare.copy()

    #bulunan aracları beyaz kareler seklinde gosterir
    arac_doldur=np.zeros((kesilmiş_kare.shape[0],kesilmiş_kare.shape[1],1),np.uint8)

    alan_maske = cv.bitwise_and(arac_doldur, arac_doldur, mask=maske)
    alan_beyaz_piksel = np.sum(alan_maske == 255)
    alan = abs(550 - 80) * abs(250 - 450)
    alan_oran = alan_beyaz_piksel / alan

    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)
        if w >100 | h>100:
            cv.rectangle(arac_doldur, (x, y), (x + w, y + h), (255), cv.FILLED)


    if alan_oran>0.3 and alanDurum==False:
        #bulunan contour lara gore kare cizdirmesi
        for cnt in contours:
            x,y,w,h=cv.boundingRect(cnt)
            if 100<w > 150 | 100 <h >150:
             cv.rectangle(sonuc, (x, y), (x + w, y + h), (255, 0, 0), 2)
        alanDurum=True

        if alan_oran > 0.3 and alanDurum == True:
            # bulunan contour lara gore kare cizdirmesi
            for cnt in contours:
                x, y, w, h = cv.boundingRect(cnt)
                if 100<w > 150 | 100 <h >150:
                    cv.rectangle(sonuc, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if alan_oran<0.3 and alanDurum== True:
            x, y, w, h = cv.boundingRect(cnt)
            if  100<w > 150 | 100 <h >150:
                cv.rectangle(sonuc, (x, y), (x + w, y + h), (255),cv.FILLED)
            alanDurum==False

    #algilayicilar(sensor) ekrana cikartiliyor
    cv.rectangle(sonuc,(algilayici1.koordinat1.x,algilayici1.koordinat1.y),(algilayici1.koordinat2.x,algilayici1.koordinat2.y),(0,0,255),cv.FILLED)
    cv.rectangle(sonuc,(algilayici2.koordinat1.x,algilayici2.koordinat1.y),(algilayici2.koordinat2.x,algilayici2.koordinat2.y),(0,0,255),cv.FILLED)


    algilaciyi1_maske=cv.bitwise_and(arac_doldur,arac_doldur,mask=algilayici1.Maske)
    algilaciyi2_maske = cv.bitwise_and(arac_doldur, arac_doldur, mask=algilayici2.Maske)

    algilayici1_beyaz_piksel=np.sum(algilaciyi1_maske==255)
    algilayici2_beyaz_piksel = np.sum(algilaciyi2_maske == 255)

    algilayici1_oran = algilayici1_beyaz_piksel/algilayici1.maske_alan
    algilayici2_oran = algilayici1_beyaz_piksel / algilayici2.maske_alan


    # araclari bir bolgeden gectikten sonra sayilmasini saglamak icin, bolgenin cizimi
    #sayim
    if (algilayici1_oran>=0.3) and algilayici1.algilayici_durum==False:
        cv.rectangle(sonuc, (algilayici1.koordinat1.x, algilayici1.koordinat1.y),
                     (algilayici1.koordinat2.x, algilayici1.koordinat2.y), (0, 255, 0), cv.FILLED)
        algilayici1.algilayici_durum = True

    elif (algilayici1_oran<=0.3) and algilayici1.algilayici_durum==True:
        cv.rectangle(sonuc, (algilayici1.koordinat1.x, algilayici1.koordinat1.y),
                     (algilayici1.koordinat2.x, algilayici1.koordinat2.y), (0, 0, 255), cv.FILLED)

        algilayici1.algilayici_durum = False
        algilayici1.arac_sayisi +=1
    else:
        cv.rectangle(sonuc, (algilayici1.koordinat1.x, algilayici1.koordinat1.y),
                     (algilayici1.koordinat2.x, algilayici1.koordinat2.y), (0, 0, 255), cv.FILLED)

    if (algilayici2_oran>=0.4) and algilayici2.algilayici_durum==False:
        cv.rectangle(sonuc, (algilayici2.koordinat1.x, algilayici2.koordinat1.y),
                     (algilayici2.koordinat2.x, algilayici2.koordinat2.y), (0, 255, 0), cv.FILLED)
        algilayici2.algilayici_durum = True

    elif (algilayici2_oran <= 0.4) and algilayici2.algilayici_durum == True:
        cv.rectangle(sonuc, (algilayici2.koordinat1.x, algilayici2.koordinat1.y),
                     (algilayici2.koordinat2.x, algilayici2.koordinat2.y), (0, 0, 255), cv.FILLED)
        algilayici2.algilayici_durum = False
        algilayici2.arac_sayisi += 1
    else:
        cv.rectangle(sonuc, (algilayici2.koordinat1.x, algilayici2.koordinat1.y),
                     (algilayici2.koordinat2.x, algilayici2.koordinat2.y), (0, 0, 255), cv.FILLED)

    cv.putText(sonuc,algilayici1.arac_sayisi.__str__(),(algilayici1.koordinat1.x-60,algilayici1.koordinat1.y+60),cv.FONT_HERSHEY_COMPLEX,3,(0,255,0))
    cv.putText(sonuc,algilayici2.arac_sayisi.__str__(),(algilayici2.koordinat1.x+100,algilayici2.koordinat1.y+60),cv.FONT_HERSHEY_COMPLEX,3,(0,255,0))

    cv.imshow("Arabalar", sonuc)
    if cv.waitKey(1) & 0xff == ord('q'):
       break

cap.release()
cv.destroyAllWindows()