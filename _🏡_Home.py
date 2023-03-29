import streamlit as st
from Resource_init import Login_3

st.set_page_config(
    page_title="Home Page",
    page_icon="🟢",
)
# Ẩn phần menu chứa dòng chữ "Streamlit"
hide_streamlit_style = """
            <style>
            #MainMenu {display: none;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



if __name__ == '__main__':
    Login_3(w = True)
    
    #if Login(w = True) == False: #w=true=> printe Welcome to ...in resource init
    #    st.stop()
# st.markdown(
#     """
#     Streamlit is an open-source app framework built specifically for
#     Machine Learning and Data Science projects.
#     **👈 Select a demo from the sidebar** to see some examples
#     of what Streamlit can do!
#     ### Want to learn more?
#     - Check out [streamlit.io](https://streamlit.io)
#     - Jump into our [documentation](https://docs.streamlit.io)
#     - Ask a question in our [community
#         forums](https://discuss.streamlit.io)
#     ### See more complex demos
#     - Use a neural net to [analyze the Udacity Self-driving Car Image
#         Dataset](https://github.com/streamlit/demo-self-driving)
#     - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
# """
# )