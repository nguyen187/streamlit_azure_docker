import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from Resource_init import get_cursor,Login
import pandas as pd
import numpy as np
import pyodbc
st.set_page_config(
    page_title="Home Page",
    page_icon="📊",
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
def extract_data_cached(data, columns): #improve performance 
    return data[columns]

class Vi:
    def __init__(self):
        self.conx,self.cursor = get_cursor()
        self.cus_ID = st.sidebar.text_input('Customer ID:')
        self.pro_ID = st.sidebar.text_input('Project ID:')
        self.batch_ID = st.sidebar.text_input('Batch ID (mumber only):')
 
    def get_options(self): #show multi parameter selection in figures - copy code from open source
        # ------ query to extral col name of databse----------
        extract_col_name_sql = '''
                select COLUMN_NAME
                from INFORMATION_SCHEMA.COLUMNS
                where TABLE_NAME='db_dboard'
        '''
        col_name = self.cursor.execute(extract_col_name_sql)
        df_name_sql = pd.DataFrame(col_name)
        df_name_sql = np.array(df_name_sql[0])

        self.col_name = [df_name_sql[i][0]
                         for i in range(42)]
        self.options = self.col_name[3:]
        
        # self.x_ax = format_option(self.x_ax)
    def extract_data(self,list_input):
        if self.cus_ID =='' or self.pro_ID =='':
                st.warning('Please enter a information project')
        extract_sql = '''
        '''
        # self.df.rename(columns={"2-PAT control(PAT_ref:PAT ref)": "Batch ID", "Batch ID": "2-PAT control(PAT_ref:PAT ref)"})
        sql_columns = ','.join(['"{}"'.format(col) for col in list_input])
        if self.batch_ID != '':
            extract_sql = '''
            SELECT  {columns}
            FROM {table}
            WHERE Cust = '{Cust_ID}' and Project_ID = '{Pro_ID}' and [2-PAT control(PAT_ref:PAT ref)]={Batch_ID}
            '''.format(table='db_dboard', columns=sql_columns,Cust_ID = self.cus_ID,Pro_ID = self.pro_ID,Batch_ID = self.batch_ID )
        elif self.batch_ID == '':
            extract_sql = '''
            SELECT  {columns}
            FROM {table}
            WHERE Cust = '{Cust_ID}' and Project_ID = '{Pro_ID}'
            '''.format(table='db_dboard', columns=sql_columns,Cust_ID = self.cus_ID,Pro_ID = self.pro_ID)
       
        extract = self.cursor.execute(extract_sql)
        # fetches all (or all remaining) rows of a query result set and returns a list of tuples.
        df_extract = np.array(extract.fetchall())
        df_extract = pd.DataFrame(
            df_extract.reshape(-1, len(list_input)), columns=list_input)  # dataframe
        self.conx.commit()
        return df_extract
    def interaction(self):
        st.header('Parameter Interaction')
        col1, col2 = st.columns([1, 3]) #devide show body to 4 part (1+3): 1st- parameter selection = 1 piece , 2nd - figure = 3 pieces 
        x_ax = col1.selectbox("X axis:",self.options) #selectbox => clicked to select option
        y_ax = col1.selectbox("y axis:",self.options)
        hue = col1.selectbox("hue:",self.options)
        if col1.button('Show interaction'):
            df_plot = self.extract_data([x_ax,y_ax,hue])
            df_plot = extract_data_cached(df_plot,[x_ax,y_ax,hue])
            sns.set_style("darkgrid")
            fig = plt.figure(figsize=(10, 4))
            
            sns.scatterplot(x = df_plot[x_ax].values,y = df_plot[y_ax].values,hue=df_plot[hue].values)
            col2.pyplot(fig)
        
    def Contribution(self):
        plt.rcParams['text.color'] = '#000000'
        plt.rcParams['axes.labelcolor']= '#909090'
        plt.rcParams['xtick.color'] = '#909090'
        plt.rcParams['ytick.color'] = '#909090'
        plt.rcParams['font.size']=11
        color_palette_list = ['#009ACD', '#ADD8E6', '#63D1F4', '#0EBFE9',   
                            '#C1F0F6', '#0099CC']
        
        st.header('Contribution')
        col1, col2 = st.columns([1, 3]) 
        col_choose1 = col1.selectbox("Column value:",self.options)

        if col1.button('Show Contribution'):
            df_plot = self.extract_data([col_choose1])
            sns.set_style("darkgrid")
            fig = plt.figure(figsize=(10, 4))
            plt.pie(x = df_plot[[col_choose1]].value_counts(),labels= df_plot[[col_choose1]].value_counts().keys(), startangle=90, colors=color_palette_list, autopct='%1.0f%%')
            col2.pyplot(fig)
    def monitoring(self):
        st.header('Pen Monitoring at time')
        #col1, col2 = st.columns([1, 3])
        #x_ax = col1.selectbox("X :",self.options)  # 
        x_ax = 'Time (h)'  # 
        y_ax = 'Penicillin concentration(P:g/L)'  #
        #if col1.button('Show Monitoring'):
        df_plot = self.extract_data([x_ax,y_ax])
        sns.set_style("darkgrid")
        fig = plt.figure(figsize=(10, 4))
        sns.lineplot(x = df_plot[x_ax].values,y = df_plot[y_ax].values)
        st.pyplot(fig)
    def prediction(self):
        st.header('Pen Prediction')
        #col1, col2 = st.columns([1, 3])
        #x_ax = col1.selectbox("X :",self.options)  # 
        x_ax = 'Time (h)'  # 
        y_ax = 'predict_Pen'  #
        #hue = 'Sugar feed rate(Fs:L/h)' #
        #if col1.button('Show Prediction'):
        df_plot = self.extract_data([x_ax,y_ax])
        sns.set_style("darkgrid")
        fig = plt.figure(figsize=(10, 4))
        sns.scatterplot(x = df_plot[x_ax].values,y = df_plot[y_ax].values,palette=['red'])
        st.pyplot(fig)

 #   def show_bar(self):
 #       st.header('Contribution')
 #       col1, col2 = st.columns([1, 3])
 #       x_ax = col1.selectbox("X bar :",self.options)
 #       y_ax = col1.selectbox("y bar:",self.options)
 #       hue = col1.selectbox("hue bar:",self.options)
 #       if col1.button('Done_B'):
 #           df_plot = self.extract_data([x_ax,y_ax,hue])
 #           sns.set_style("darkgrid")
 #           fig = plt.figure(figsize=(10, 4))
 #           sns.barplot(x = df_plot[x_ax].values,y = df_plot[y_ax].values,hue=df_plot[hue].values)
 #           col2.pyplot(fig)

if __name__=='__main__':
    if Login()==False:
        st.stop()
    v = Vi()
    v.get_options()
    if st.checkbox('Pen Monitoring at time'):
        v.monitoring()
    if st.checkbox('Pen Prediction'):
        v.prediction()
    if st.checkbox('Interaction'):
        v.interaction()
    if st.checkbox('Contribution'):
        v.Contribution()

