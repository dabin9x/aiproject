import streamlit as st
st.title('나의 첫 웹서비스 만들기')
a=st.text_input('이름을 입력해주세요')
b=st.selectbox('좋아하는 음식을 선택해주세요',['떡볶이','햄버거','샌드위치'])
if st.button('인사말 생성'):
  st.write('반갑습니다')
  st.info(a+'님 안녕하세요')
  st.warning(b+'저도 같아요')
  st.error('잘부탁드려요')
  st.balloons()
