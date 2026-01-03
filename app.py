import streamlit as st
import pandas as pd
import requests
import json

# --- 1. API 설정 ---
# 실제 사용 시 환경 변수나 st.secrets를 사용하는 것이 안전합니다.
APP_KEY = "PSmBdpWduaskTXxqbcT6PuBTneKitnWiXnrL"
APP_SECRET = "adyZ3eYxXM74UlaErGZWe1SEJ9RPNo2wOD/mDWkJqkKfB0re+zVtKNiZM5loyVumtm5It+jTdgplqbimwqnyboerycmQWrlgA/Uwm8u4K66LB6+PhIoO6kf8zS196RO570kjshkBBecQzUUfwLlDWBIlTu/Mvu4qYYi5dstnsjgZh3Ic2Sw="
URL_BASE = "https://openapi.koreainvestment.com:9443" # 실전투자용 (모의투자는 포트번호 다름)

# --- 2. 접근 토큰 발급 함수 ---
def get_access_token():
    headers = {"content-type":"application/json"}
    body = {
        "grant_type":"client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    path = "oauth2/tokenP"
    res = requests.post(f"{URL_BASE}/{path}", headers=headers, data=json.dumps(body))
    return res.json()['access_token']

# --- 3. 거래대금 상위 종목 조회 함수 ---
def get_trading_volume_top(token):
    path = "uapi/domestic-stock/v1/quotations/volume-rank"
    headers = {
        "Content-Type": "application/json",
        "authorization": f"Bearer {token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHPST01710000", # 거래대금/거래량 상위 조회 TR ID
        "custtype": "P"
    }
    # params: 0:전체, 1:기타, 2:코스피, 3:코스닥 등
    params = {
        "fid_cond_mrkt_div_code": "J", # 주식
        "fid_cond_scr_div_code": "20171", # 화면번호
        "fid_input_iscd": "0000", # 0000:전체
        "fid_div_cls_code": "0", # 0:거래대금 상위, 1:거래량 상위
        "fid_blank": ""
    }
    res = requests.get(f"{URL_BASE}/{path}", headers=headers, params=params)
    return res.json()['output']

# --- 4. Streamlit UI 구성 ---
st.set_page_config(page_title="한투 API 거래대금 대시보드", layout="wide")
st.title("🚀 국내주식 거래대금 상위 TOP 20")

if st.button('데이터 불러오기'):
    with st.spinner('데이터를 가져오는 중...'):
        try:
            token = get_access_token()
            data = get_trading_volume_top(token)
            
            # 데이터프레임 변환 및 전처리
            df = pd.DataFrame(data)
            # 필요한 컬럼만 추출 및 이름 변경
            df = df[['hts_kor_isnm', 'stck_prpr', 'prdy_ctrt', 'acml_tr_pbmn']]
            df.columns = ['종목명', '현재가', '등락률', '누적거래대금(백만)']
            
            # 숫자형 변환
            df['현재가'] = pd.to_numeric(df['현재가'])
            df['등락률'] = pd.to_numeric(df['등락률'])
            df['누적거래대금(백만)'] = pd.to_numeric(df['누적거래대금(백만)']) // 1000000 # 단위를 백만으로 조정 예시
            
            # 화면 출력
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 상위 종목 리스트")
                st.dataframe(df.style.highlight_max(axis=0, subset=['등락률'], color='lightcoral'))
            
            with col2:
                st.subheader("📈 거래대금 차트")
                st.bar_chart(df.set_index('종목명')['누적거래대금(백만)'])
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("버튼을 눌러 실시간 거래대금 순위를 확인하세요.")