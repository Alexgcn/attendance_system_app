import streamlit as st



st.set_page_config(page_title='Attendance System',layout='wide')

st.header('Sistema de Asistencia utilizando Reconocimiento Facial')

with st.spinner("Cargando modelos y conectándose a la base de datos Redis ..."):
    import face_rec
    
st.success('El modelo se ha cargado correctamente.')
st.success('Conexión exitosa a la base de datos Redis.')