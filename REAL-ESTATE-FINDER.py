import streamlit as st
import pandas as pd
from PublicDataReader import TransactionPrice

# 1. 페이지 설정
st.set_page_config(page_title="노운's 부동산 탐지기", layout="wide")
st.title("🏠 권노운의 실거래가 기반 급매 탐지 대시보드")

# 지역 코드 데이터 (시군구 코드 매핑)
REGION_DATA = {
    "서울특별시": {
        "노원구": "11350",
        "동대문구": "11230",
        "강남구": "11680",
        "송파구": "11710",
        "강동구": "11740"
    },
    "경기도": {
        "구리시": "41310",
        "남양주시": "41360",
        "하남시": "41450",
        "성남시 수정구": "41131",
        "성남시 분당구": "41135"
    }
}

# 2. 사용자 설정 (사이드바)
with st.sidebar:
    st.header("💰 자금 및 대출 설정")
    salary = st.number_input("연봉 (원)", value=63300000)
    interest_rate = st.slider("대출 금리 (%)", 3.0, 7.0, 4.5, 0.1)
    
    st.subheader("보유 자산 상세")
    my_cash = st.number_input("실제 보유 현금 (원)", value=100000000)
    severance_pay = st.number_input("퇴직금 예상액 (원)", value=50000000)
    family_support = st.number_input("부모님/기타 지원금 (원)", value=50000000)
    total_cash = my_cash + severance_pay + family_support
    
    st.header("📍 지역 세부 선택")
    # 시/도 선택
    selected_sido = st.selectbox("시/도 선택", list(REGION_DATA.keys()))
    
    # 선택된 시/도에 따른 시/군/구 목록 필터링
    sigungu_list = list(REGION_DATA[selected_sido].keys())
    selected_sigungu = st.selectbox("시/군/구 선택", sigungu_list)
    
    target_month = st.text_input("조회 월 (YYYYMM)", value="202512")

    # 🚀 분석 런칭 버튼
    launch_button = st.button("🚀 분석 실행", use_container_width=True)

# 3. 예산 계산 로직
max_annual_pay = salary * 0.4
monthly_rate = (interest_rate / 100) / 12
total_months = 30 * 12
# DSR 기반 최대 대출 가능액 계산
estimated_max_loan = (max_annual_pay / 12) * ((1 + monthly_rate)**total_months - 1) / (monthly_rate * (1 + monthly_rate)**total_months)
buyable_price = estimated_max_loan + total_cash

st.success(f"✅ 권노운님의 현재 매수 가능 예산(자본+대출): 약 **{buyable_price/100000000:.2f}억 원**")

# 4. 버튼 클릭 시 데이터 분석 실행
if launch_button:
    service_key = st.secrets.get("SERVICE_KEY", None)
    sigungu_code = REGION_DATA[selected_sido][selected_sigungu]

    if not service_key:
        st.warning("⚠️ SERVICE_KEY 미등록으로 샘플 데이터를 표시합니다.")
        df = pd.DataFrame({
            '단지': [f'{selected_sigungu} 아파트A', f'{selected_sigungu} 아파트B', '단지C', '단지D'],
            '전용면적': [59, 84, 59, 84],
            '거래금액(만원)': [75000, 92000, 68000, 110000],
            '층': [12, 5, 8, 20]
        })
    else:
        try:
            api = TransactionPrice(service_key)
            df = api.get_data(
                property_type="아파트",
                trade_type="매매",
                sigungu_code=sigungu_code,
                year_month=target_month
            )
        except Exception as e:
            st.error(f"데이터 로드 에러: {e}")
            df = pd.DataFrame()

    # 5. 시각화 및 필터링
    if not df.empty:
        st.subheader(f"📊 {selected_sido} {selected_sigungu} ({target_month}) 실거래 현황")
        
        # 예산 내 진입 가능 여부 체크
        # API 결과의 거래금액 컬럼명이 라이브러리에 따라 다를 수 있어 체크 필요
        price_col = '거래금액' if '거래금액' in df.columns else '거래금액(만원)'
        
        # 예산 내 매물 하이라이트
        def highlight_buyable(val):
            actual_price = val * 10000 if price_col == '거래금액(만원)' else val
            return 'background-color: #d4edda' if actual_price <= buyable_price else ''

        st.dataframe(df.style.applymap(highlight_buyable, subset=[price_col]), use_container_width=True)
    else:
        st.info("선택하신 기간 및 지역에 거래 데이터가 없습니다.")
