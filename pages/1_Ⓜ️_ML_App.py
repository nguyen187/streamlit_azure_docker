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
from Resource_init import get_cursor,load_model_resource,Login
st.set_page_config(
    page_title="ML App",
    page_icon="Ⓜ️",
)
# Ẩn phần menu chứa dòng chữ "Streamlit"
hide_streamlit_style = """
            <style>
            #MainMenu {display: none;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


@st.cache_data
def load_data(input_df):
    #use to load data - return lai
    return input_df


class BiopharmApp:
    def __init__(self):
     # create structure   
        self.input_df1 = pd.DataFrame()
        self.input_df2 = pd.DataFrame()
        self.result_df = pd.DataFrame()
        self.conx, self.cursor = get_cursor()
        self.xgb_model_raman = None
        self.scale = None
        self.ann_model_process = None
        self.xgb_model_raman, self.scale,self.ann_model_process = load_model_resource()

    def predict(self):
        X_pro = self.input_df1 # X_pro = input_df1...dataframe of csv file
        X_pro['Sugar mass flow'] = X_pro['Sugar feed rate(Fs:L/h)']*X_pro['Substrate concentration(S:g/L)']
        Col1 = ['Sugar mass flow','Water for injection/dilution(Fw:L/h)','Temperature(T:K)','Dissolved oxygen concentration(DO2:mg/L)','Vessel Volume(V:L)','pH(pH:pH)','Temperature(T:K)']
        X_pro = X_pro[Col1]

        X_pro = self.scale.fit_transform(X_pro) # use model scale in resource init => transform =>X_pro
        y_head_pro = self.ann_model_process.predict(X_pro) #use model ann_model_process in resource init
        self.input_df1 = self.input_df1.drop(['Sugar mass flow'], axis=1)

        self.input_df2 = self.input_df2.drop(['202','201'], axis=1)
        self.input_df2 = self.input_df2.iloc[:, 1100:1350]

        X_ra1 = signal.savgol_filter(self.input_df2.values, window_length=11, polyorder=3, mode="nearest")
        X_ra1 = savgol_filter(X_ra1, 17, polyorder=3, deriv=2)
        y_head_ra = self.xgb_model_raman.predict(X_ra1)

        df_cus_ID = np.full((self.input_df1.shape[0], 1), self.cus_ID) # create a dataframe with 1 column and value = self.cus_ID
        df_pro_ID = np.full((self.input_df1.shape[0], 1), self.pro_ID)
        df_batch_ID = np.full((self.input_df1.shape[0], 1), self.batch_ID)

        self.input_df1['Penicillin concentration(P:g/L)'] = y_head_ra #replace column with name"Penicillin concentration(P:g/L)" =y_head_ra 
        self.input_df1['predict_Pen'] = y_head_pro #create new comlumn "predict_Pen" and attached value "y_head_pro"
        self.result_df = pd.concat([pd.DataFrame(df_cus_ID, columns=['Cust']), pd.DataFrame(df_pro_ID, columns=['Project_ID']), pd.DataFrame(df_batch_ID, columns=['2-PAT control(PAT_ref:PAT ref)']),
                            self.input_df1,self.input_df2], axis=1)  # include cus_id,pro_id,test_id,data
        self.result_df = load_data(self.result_df) #result dataframe include all values from customer ID, project ID, batch_ID,df_batch_ID, input_df1, input_df2
        st.header('Result') #lable of st 


        progress_text = "in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100): #decorate for progress bar
            time.sleep(0.01)
            my_bar.progress(percent_complete + 1, text=progress_text)
        st.dataframe(self.result_df) # show dataframe(results) , like print in jupyter notebook
        self.result_df = self.result_df.fillna(value=0) #if value na, set it is 0 because sql database does't work with na
       
    def insert_sql(self,data):
        # self.df.rename(columns={"2-PAT control(PAT_ref:PAT ref)": "Batch ID", "Batch ID": "2-PAT control(PAT_ref:PAT ref)"})
        sql_columns = ','.join(['"{}"'.format(col) for col in data.columns])
        sql_values = ','.join(['?'] * len(data.columns))
        insert_exp_sql = '''
        INSERT INTO {table} ({columns})
        VALUES ({values})
        '''.format(table='db_dboard', columns=sql_columns, values=sql_values)
        #server and databaes were connected with secrets.toml, table in database is showed here
        for row in data.itertuples():
            self.cursor.execute(insert_exp_sql, row[1:]) #insert every sinle row in db
        self.conx.commit() #save the inserted data
        st.success('Done!', icon="✅")
        st.balloons()
    
    def load_input(self):
        #Collect user input feature into dataframe
        upload_file1 = st.sidebar.file_uploader('Upload your input csv file process',type=['csv'])
        #upload csv file=> save to link of uploaded file "upload_file1"
        upload_file2 = st.sidebar.file_uploader('Upload your input csv file raman',type=['csv'])
        if upload_file1 is not None and upload_file2 is not None:
            input_df1 = pd.read_csv(upload_file1)
            # input_df1 is dataframe 
            input_df2 = pd.read_csv(upload_file2)
            # Cache the data frame so it's only loaded once
            self.input_df1  = load_data(input_df1)
            # self.input_df1...load dataframe "input_df1" to @st.cache_data
            self.input_df2 = load_data(input_df2)
            # Display the dataframe and allow the user to stretch the dataframe
            # across the full width of the container, based on the checkbox value
            st.header('Process Data:')
            st.dataframe(self.input_df1)
            #show dataframe at default location at main body if not locate position
            st.header('Raman Data:')
            st.dataframe(self.input_df2)
            
            self.cus_ID = st.sidebar.text_input('Customer ID:')
            #text Customer ID and show at sidebar position
            self.pro_ID = st.sidebar.text_input('Project ID:')
            self.batch_ID = st.sidebar.text_input('Batch ID (number only):')
            self.experimental_date  = st.sidebar.date_input(
                "Experimental date is", 
                datetime.date(2023, 2, 2))
            st.sidebar.write('Experimental date is:', self.experimental_date )
            submit_time = datetime.datetime.now().strftime(
                        "%m/%d/%Y %H:%M:%S")  # save time now
            return True
        else: 
            return False
    def Run(self):
        self.load_input() # call def load_input to get
        #input_df1, input_df2, cus_ID,pro_ID, batch_ID... 
        if st.sidebar.button('Submit'): #click buttom submit => 
            #call def predict
            #call def insert_sql
            self.predict()
            self.insert_sql(self.result_df)
            
if __name__=='__main__':

    if Login()==False:
        st.stop()
    web = BiopharmApp() # web = class biopharmapp 
    web.Run() # go to def run of class "biopharmapp"
    