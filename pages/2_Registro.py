import streamlit as st
from Home import face_rec
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer
import av




st.subheader('Registro')

## init registration form
registration_form = face_rec.RegistrationForm()

# step-2: Collect facial embedding of that person
def video_callback_func(frame):
    img = frame.to_ndarray(format='bgr24') # 3d array bgr
    reg_img, embedding = registration_form.get_embedding(img)
    # two step process
    # 1st step save data into local computer txt
    if embedding is not None:
        with open('face_embedding.txt',mode='ab') as f:
            np.savetxt(f,embedding)

    return av.VideoFrame.from_ndarray(reg_img,format='bgr24')


####### Registration Form ##########
with st.container(border=True):
    name = st.text_input(label='Nombre',placeholder='Ingrese Nombre y Apellido')
    role = st.selectbox(label='Rol', placeholder='Seleccionar Rol', options=('--select--',
                                                                          'Empleado', 'Encargado', 'Auxiliar', 'Invitado','Teacher','Student'))
    course = st.selectbox(label='Selecionar Sucursal', placeholder='Selecionar Sucursal',
                          options=('--select--','Victoria',
                                   'Mante','Reynosa'))
   
    address = st.text_area(label='Direccion', placeholder='Ingrese su direccion')
    contact = st.text_input(label='Numero de contacto', placeholder='Ingrese su numero de contacto')
    email = st.text_input(label='Email', placeholder='Ingrese su Email')

    st.write(' Da click en Start para capturar tus samples faciales')
    with st.expander('Instrucciones'):
        st.caption('1. Realiza diferences expresiones para capturar detalles del rostro')
        st.caption('2. Da Click en Stop despues de obtener 200 samples')

    webrtc_streamer(key='registro', video_frame_callback=video_callback_func,
                    rtc_configuration={
                        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                    }
                    )





# step-3: save the data in redis database


if st.button('Enviar'):
    return_val = registration_form.save_data_in_redis_db(name,role)
    if return_val == True:
        st.success(f"{name} registered sucessfully")
    elif return_val == 'name_false':
        st.error('Please enter the name: Name cannot be empty or spaces')

    elif return_val == 'file_false':
        st.error('face_embedding.txt is not found. Please refresh the page and execute again.')
