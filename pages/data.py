import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

SOURCE_DATA = ('data/source.csv')
REVISION_DATA = ('data/revision.csv')
NROWS = 3000

def load_data(url, rows):
    data = pd.read_csv(url, nrows=rows)
    return data

source = load_data(SOURCE_DATA, NROWS)
revision = load_data(REVISION_DATA, NROWS)

st.title(f"数据查看")
st.subheader(f"关山校区！！！关山校区！！！关山校区！！！")

with st.container(border = True):
    st.header(f'校方原始数据')
    st.write(source)

with st.container(border = True):
    st.header(f'家长修改申请')
    st.write(revision)