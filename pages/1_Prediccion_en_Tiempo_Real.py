import streamlit as st 
from Home import face_rec
from streamlit_webrtc import webrtc_streamer
import av
import time

st.subheader('Sistema de Asistencia en Tiempo Real')


# Retrive the data from Redis Database
with st.spinner('Retriving Data from Redis DB ...'):    
    redis_face_db = face_rec.retrive_data(name='academy:register')
    st.dataframe(redis_face_db)
    
st.success("Los datos se han recuperado correctamente de REdis")

# time 
waitTime = 2 # time in sec
setTime = time.time()
realtimepred = face_rec.RealTimePred() # Clase prediccion en tiempo real

# Prediccion en tiempo real
def video_frame_callback(frame):
    global setTime
    
    img = frame.to_ndarray(format="bgr24") 

    pred_img = realtimepred.face_prediction(img,redis_face_db,
                                        'facial_features',['Name','Role'],thresh=0.5)
    
    timenow = time.time()
    difftime = timenow - setTime
    if difftime >= waitTime:
        realtimepred.savelogs_redis()
        setTime = time.time() # reset time      
        print('Guardar los datos en la base de datos de Redis')
    

    return av.VideoFrame.from_ndarray(pred_img, format="bgr24")


webrtc_streamer(key="prediccionentiemporeal", video_frame_callback=video_frame_callback,
                rtc_configuration={
                    "iceServers":[{"urls": ["stun:stun.l.google.com:19302"]}]
                                   }
                )

