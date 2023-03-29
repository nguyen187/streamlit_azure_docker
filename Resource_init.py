import streamlit as st
import pandas as pd
import numpy as np
import datetime
import pyodbc
import xgboost as xgb
import joblib
import time
from keras.models import load_model
from scipy import signal
from scipy.signal import savgol_filter
import seaborn as sns
import matplotlib.pyplot as plt
from markdown import markdown
from PIL import Image
# Khởi tạo biến toàn cục connection pool
# pool = None

def get_connection_string():
    # Trả về chuỗi kết nối database của bạn
    server = st.secrets["server"]
    database = st.secrets["database"]
    user = st.secrets["username"]
    passwd = st.secrets["password"]
    return f"driver={{ODBC Driver 17 for SQL Server}}; server={server}; database={database};UID={user}; PWD={passwd}"

# def get_pool():
#     # Tạo pool kết nối nếu chưa được tạo
#     global pool
#     if pool is None:
#         connection_string = get_connection_string()
#         pool = ConnectionPool(minimum=1, maximum=10, connection_string=connection_string)
#     return pool

# @st.cache(hash_funcs={pyodbc.Connection: id})
@st.cache_resource
def get_connection():
    # Lấy một kết nối từ pool
    connection_string = get_connection_string()
    conx = pyodbc.connect(connection_string)
    return conx

def get_cursor():
    # Tạo con trỏ để truy vấn database
    connection = get_connection()
    cursor = connection.cursor()
    return connection,cursor

def close_connection(conx):
    return conx.close()
    
# Khởi tạo biến toàn cục model
xgb_model_raman = None
scale = None
ann_model_process = None
@st.cache_resource #use save method by cach_resource of streamlit => optimal time, use tempolary memory 
def load_model_resource():
    # Đọc model nếu chưa được đọc
    global xgb_model_raman,scale,ann_model_process
    
    if xgb_model_raman is None:
        xgb_model_raman = xgb.XGBRegressor() #use labrary XGBRegressor to load model model_xgb.json due to xgb.json model need a library 
        xgb_model_raman.load_model("./model/model_xgb.json") # load model model_xgb.json from streamlit server 
        scale = joblib.load('./model/scale.pkl') # load moel scale.pkl from streamlit server
        ann_model_process = load_model("./model/network.h5") # load moel network.h5 from streamlit server
    return xgb_model_raman,scale,ann_model_process


USERS = {
            'test@localhost.com',
            'trinhntrung@gmail.com'
        }
server = st.secrets["server"]
database = st.secrets["database"]
user = st.secrets["username"]
passwd = st.secrets["password"]
@st.cache_resource
def Login(w =False):
    #if st.experimental_user.email in USERS:
    if w == True:
        #st.write("# Welcome to BioPharm Website! 👋") #w=true in home 
        st.write('Hello, %s!' % st.experimental_user.email)
        #st.write('server: {sv}'.format(sv = server))
        image = Image.open('anhbia.png')
        st.image(image)
    return True
    #else:
        #st.error("Your account don't permission", icon="🚨")
        #return False
def Login_2(w =False):
    user = st.text_input('User:')
    #text Customer ID and show at sidebar position
    password = st.text_input('Password:')
    
    extract_user = '''
    select * from admin
    where user = ?'''
    connection, cursor =get_cursor()
    if st.button('login:'):
        sql_user = cursor.execute(extract_user,user)
        sql_user = pd.DataFrame(sql_user)
        if sql_user.empty:
            st.stop()
        sql_user = np.array(sql_user[0][0])
        sql_pass = sql_user[1]
        if sql_pass == password:
            Login(w==True)
        else:
            st.warning("Please check password")
            return
    if w == True:
        #st.write("# Welcome to BioPharm Website! 👋") #w=true in home 
        #st.write('Hello, %s!' % st.experimental_user.email)
        #st.write('server: {sv}'.format(sv = server))
        image = Image.open('anhbia.png')
        st.image(image)
    return True

def Login_3(w = True):
    admin = {
            'test',
            'admin'
        }
    Pa= {
       'test'
   }
    col1, col2 = st.columns([1, 1])
    user = col1.text_input('User:')
    password = col2.text_input('Password:',type='password')
    if st.button('Login'):
        if user in admin and password in Pa :
            st.write('Hello, %s!' % user)
        else:
            st.error("Please check password")
            return False
            st.stop()
    image = Image.open('./image/anhbia.png')
    st.image(image)
    return True