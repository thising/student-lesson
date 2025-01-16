import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import time
from st_files_connection import FilesConnection

st.set_page_config(page_title="童程童美关山校区学时查询",
                   page_icon="🤖",
                   initial_sidebar_state="auto",
                   menu_items={
                       'About': "### 该系统仅用于童程童美关山校区学员剩余学时查询\n"
                                "1. 请输入学生姓名，点击查询\n"
                                "2. 如果数据无误，请点击确认无误\n"
                                "3. 如果数据有误，或者没有您小孩的数据，请填写修改信息并提交修改\n"
                   })

SOURCE_DATA = ('data/source.csv')
REVISION_DATA = ('data/revision.csv')
GCS_SOURCE_DATA = 'student-lesson/source.csv'
GCS_REVISION_DATA = 'student-lesson/revision.csv'
NROWS = 3000

# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
gcs_conn = st.connection('gcs', type=FilesConnection)


if 'searched' not in st.session_state:
    st.session_state['searched'] = False

if 'ret_source' not in st.session_state:
    st.session_state['ret_source'] = pd.DataFrame()

if 'ret_revision' not in st.session_state:
    st.session_state['ret_revision'] = pd.DataFrame()

def timestamp():
    td = timedelta(hours=8)
    tz = timezone(td)
    dt = datetime.fromtimestamp(time.time(), tz)
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')

    return dt

def search(name, data):
    ret = data.query('学员姓名.str.contains("{}", na=False)'.format(name))
    return ret

def load_data(url, rows):
    data = pd.read_csv(url, nrows=rows)
    return data

def add(name, hours, card, request, remarks):
    last_index = 1
    if not revision.empty:
        last_index = revision.index[-1] + 1
    name = name.replace(',', '，')
    hours = hours.replace(',', '，')
    card = card.replace(',', '，')
    remarks = remarks.replace(',', '，')
    revision.loc[last_index] = [name, hours, card, request, remarks, timestamp()]
    # revision.to_csv(REVISION_DATA, encoding='utf-8', index=False)

    with gcs_conn.open(GCS_REVISION_DATA, "wt") as f:
        revision.to_csv(f, index=False)

def research():
    st.session_state['ret_source'] = search(name, source)
    st.session_state['ret_revision'] = search(name, revision)

# source = load_data(SOURCE_DATA, NROWS)
# revision = load_data(REVISION_DATA, NROWS)
source = gcs_conn.read(GCS_SOURCE_DATA, input_format="csv", ttl=600)
revision = gcs_conn.read(GCS_REVISION_DATA, input_format="csv", ttl=0)

st.title(f"童程童美关山校区学时查询")
st.subheader(f"关山校区！！！关山校区！！！关山校区！！！")

name = st.text_input(
            '学生姓名',
            value = '',
            placeholder = '请输入学生姓名',
            max_chars = 30,
            label_visibility = 'hidden'
        )

if st.button('查询', type = 'primary'):
    if len(name) == 0:
        st.error(f'学生姓名不能为空')
    else:
        research()
        st.session_state['searched'] = True

if st.session_state['searched']:
    with st.container(border = True):
        st.caption(f'原始记录')
        current_source = st.session_state['ret_source']
        if current_source.empty:
            st.warning(f'暂时没有找到{name}的原始记录')
        else:
            st.write(current_source)
            if st.button('确认无误', type = 'primary'):
                if len(name) > 0:
                    add(name, '已确认', '已确认', '', '确认无误')
                    research()
                    st.rerun()

    with st.container(border = True):
        st.caption(f'修改请求')
        current_revision = st.session_state['ret_revision']
        if current_revision.empty:
            st.write(f'家长还未提交{name}的修改请求')
            st.caption(f'您可以在下方的修改请求中填写您的情况说明，并提交给我们')
        else:
            st.write(current_revision)

    with st.form(f"revision_request_form"):
        _name = st.text_input("学生姓名", value=name, disabled = True)
        _hours = st.text_input("剩余学时", value='', max_chars = 30)
        _card = st.text_input("童享卡权益金", value='', max_chars = 30)
        _request = st.selectbox(
                "您的第一诉求是什么？",
                ("转课", "支持自营", "坚决退费"),
            )
        _remarks = st.text_area("情况备注", value='', placeholder = '其他情况都在该栏填写。例如畅学卡，xx年xx月xx日购买课时包……', max_chars = 200)
        submitted = st.form_submit_button("提交修改")
        st.caption(f'如果您提交错了，或者有遗漏信息，请再次提交正确信息即可，我们将以您最后一次提交的数据进行合并处理')
        if submitted:
            if len(name) > 0:
                add(_name, _hours, _card, _request, _remarks)
                research()
                st.rerun()
            else:
                st.error(f'学生姓名不能为空')