import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time

SOURCE_DATA = ('data.csv')
REVISION_DATA = ('revision.csv')
NROWS = 2000

if 'searched' not in st.session_state:
    st.session_state['searched'] = False

if 'ret_source' not in st.session_state:
    st.session_state['ret_source'] = pd.DataFrame()

if 'ret_revision' not in st.session_state:
    st.session_state['ret_revision'] = pd.DataFrame()

def timestamp():
    return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")

def search(name, data):
    ret = data.query('学员姓名.str.contains("{}", na=False)'.format(name))
    return ret

def load_data(url, rows):
    data = pd.read_csv(url, nrows=rows)
    return data

def add(name, hours, card, remarks):
    last_index = 1
    if not revision.empty:
        last_index = revision.index[-1] + 1
    name = name.replace(',', '，').replace('.', '。')
    hours = hours.replace(',', '，').replace('.', '。')
    card = card.replace(',', '，').replace('.', '。')
    remarks = remarks.replace(',', '，').replace('.', '。')
    revision.loc[last_index] = [name, hours, card, remarks, timestamp()]
    revision.to_csv(REVISION_DATA, encoding='utf-8', index=False)

def research():
    st.session_state['ret_source'] = search(name, source)
    st.session_state['ret_revision'] = search(name, revision)

source = load_data(SOURCE_DATA, NROWS)
revision = load_data(REVISION_DATA, NROWS)

st.title(f"童程童美关山校区学时查询")
st.subheader(f"关山校区！！！关山校区！！！关山校区！！！")

name = st.text_input(
            '学生姓名',
            value = '',
            placeholder = '请输入学生姓名',
            max_chars = 10,
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
                    add(name, '', '', '确认无误')
                    research()
                    st.rerun()

    with st.container(border = True):
        st.caption(f'修改请求')
        current_revision = st.session_state['ret_revision']
        if current_revision.empty:
            st.write(f'家长还未提交{name}的修改请求')
        else:
            st.write(current_revision)

    with st.form(f"revision_request_form"):
        _name = st.text_input("学生姓名", value=name, disabled = True)
        _hours = st.text_input("剩余学时", value='', max_chars = 10)
        _card = st.text_input("童享卡权益金", value='', max_chars = 10)
        _remarks = st.text_input("情况备注", value='', max_chars = 50)
        submitted = st.form_submit_button("提交")
        if submitted:
            if len(name) > 0:
                add(_name, _hours, _card, _remarks)
                research()
                st.rerun()
            else:
                st.error(f'学生姓名不能为空')