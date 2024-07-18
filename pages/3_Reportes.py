import pandas as pd
import streamlit as st
from Home import face_rec
import datetime



# from auth import authenticator

# st.set_page_config(page_title='Reporting',layout='wide')
st.subheader('Reportes')

# if st.session_state['authentication_status']:
#     authenticator.logout('Logout', 'sidebar', key='unique_key')


name = 'attendance:logs'
def load_logs(name,end=-1):
    logs_list = face_rec.r.lrange(name,start=0,end=end) # extrae los datos de redis
    return logs_list

# apartados para mostrar la informacion
tab1, tab2, tab3 = st.tabs(['Datos Registrados','Logs','Reportes de Asistencia'])

with tab1:
    if st.button('Actualizar Datos'):
        # recibir los datos de la base de datos de redis
        with st.spinner('Retriving Data from Redis DB ...'):
            redis_face_db = face_rec.retrive_data(name='academy:register')
            st.dataframe(redis_face_db[['Name','Role']])

with tab2:
    if st.button('Actualizar Logs'):
        st.write(load_logs(name=name))


with tab3:
    st.subheader('Reportes de Asistencia')

    # cargar atributos del logs en una lista de logs
    logs_list = load_logs(name=name)

    # paso 1: convierte los logs en una lista
    convert_byte_to_string = lambda x: x.decode('utf-8')
    logs_list_string = list(map(convert_byte_to_string, logs_list))

    # paso 2: un @ para una lista anidada
    split_string = lambda x: x.split('@')
    logs_nested_list = list(map(split_string, logs_list_string))
    

    logs_df = pd.DataFrame(logs_nested_list, columns= ['Name','Role','Timestamp'])

    # paso  3: analisis de reportes 
    #logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
    logs_df['Timestamp'] = logs_df['Timestamp'].apply(lambda x: x.split('.')[0])
    logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
    logs_df['Date'] = logs_df['Timestamp'].dt.date

    # paso 3.1 : Calcular llegada y salida
    # In time: At which person is first detected in that day (min Timestamp of the date)
    # Out time: At which person is last detected in that day (Max Timestamp of the date)

    report_df = logs_df.groupby(by=['Date','Name','Role']).agg(
        In_time = pd.NamedAgg('Timestamp','min'), # in time 
        Out_time = pd.NamedAgg('Timestamp','max') # out time
    ).reset_index()

    report_df['In_time']  = pd.to_datetime(report_df['In_time'])
    report_df['Out_time']  = pd.to_datetime(report_df['Out_time'])

    report_df['Duration'] = report_df['Out_time'] - report_df['In_time']

    # paso 4: marca si esta presente o ausente la persona
    all_dates = report_df['Date'].unique()
    name_role = report_df[['Name','Role']].drop_duplicates().values.tolist()

    date_name_rol_zip = []
    for dt in all_dates:
        for name, role in name_role:
            date_name_rol_zip.append([dt, name, role])

    date_name_rol_zip_df = pd.DataFrame(date_name_rol_zip, columns=['Date','Name','Role'])
    # 

    date_name_rol_zip_df = pd.merge(date_name_rol_zip_df, report_df, how='left',on=['Date','Name','Role'])

    # Duration
    # Hours
    date_name_rol_zip_df['Duration_seconds'] = date_name_rol_zip_df['Duration'].dt.seconds
    date_name_rol_zip_df['Duration_hours'] = date_name_rol_zip_df['Duration_seconds'] / (60*60)

    def status_marker(x):

        if pd.Series(x).isnull().all():
            return 'Ausente'
        
        elif x >= 0 and x < 1:
            return 'Austente (Menos de 1 hora)'
        
        elif x >= 1 and x < 4:
            return 'Medio Dia (Menos de 4 horas)'

        elif x >= 4 and x < 6:
            return 'Medio Dia'

        elif x >= 6:
            return 'Presente' 
        
    date_name_rol_zip_df['Status'] = date_name_rol_zip_df['Duration_hours'].apply(status_marker)

    # tab
    t1, t2 = st.tabs(['Reporte completo','Filtrar reporte'])

    with t1:
        st.subheader('Reporte completo')
        st.dataframe(date_name_rol_zip_df)

    with t2:
        st.subheader('Buscar Registros')

        # Date

        date_in = str(st.date_input('Filtrar Fecha', datetime.datetime.now().date()))
        
        # Filter the person names
        name_list = date_name_rol_zip_df['Name'].unique().tolist()
        name_in = st.selectbox('Seleccionar nombre', ['ALL']+name_list)

        # Filter rol
        role_list = date_name_rol_zip_df['Role'].unique().tolist()
        role_in = st.selectbox('Seleccionar Rol', ['ALL']+role_list)

        # Filter the duration

        duration_in = st.slider('Filtrar la duracion en horas mayor que', 0, 15, 6)

        # Status
        status_list = date_name_rol_zip_df['Status'].unique().tolist()
        status_in = st.multiselect('Seleccionar Estado', ['ALL']+status_list) # return 

        if st.button('Enter'):
            date_name_rol_zip_df['Date'] = date_name_rol_zip_df['Date'].astype(str)

            # filter date
            filter_df = date_name_rol_zip_df.query(f'Date == "{date_in}"')

            # Filter the name
            if name_in != 'ALL':
                filter_df = filter_df.query(f'Name == "{name_in}"')

            # Filter the ROLE
            if role_in != 'ALL':
                filter_df = filter_df.query(f'Role == "{role_in}"')


            # Filter the Duration
            if duration_in > 0:
                filter_df = filter_df.query(f'Duration_hours > {duration_in}')


            # Filter the Status
            if 'ALL' in status_in:
                filter_df = filter_df

            elif len(status_in) > 0:
                filter_df['status_condition'] = filter_df['Status'].apply(lambda x: True if x in status_in else False)
                filter_df = filter_df.query(f'status_condition == True')
                filter_df.drop(columns='status_condition',inplace=True)

            else:
                filter_df = filter_df


            st.dataframe(filter_df)

            










