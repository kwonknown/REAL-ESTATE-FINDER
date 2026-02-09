import streamlit as st
import pandas as pd
from PublicDataReader import TransactionPrice

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="노운's 부동산 탐지기", layout="wide")
st.title("🏠 권노운의 실거래가 기반 급매 탐지 대시보드")

# 2. 지역 코드 데이터 (시군구 코드 매핑)
# 추가하고 싶은 지역이 있다면 '법정동코드 5자리'를 찾아 추가하세요.
REGION_DATA = {
    "서울특별시": {
        "노원구": "11350",
        "동대문구": "11230",
        "강남구": "11680",
        "송파구": "11710",
        "강동구": "11740",
        "성동구": "11200"
    },
    "경기도": {
        "구리시": "41310",
        "남양주시": "41360",
        "하남시": "41450",
        "성남시 수정구": "41131",
        "성남시 분당구": "41135",
        "광명시": "41210"
    }
}

# 3. 사이드바 - 설정 영역
with st.sidebar:
    st.header("💰 자금 및 대출 설정")
    salary = st.number_input("연봉 (원)", value=63300000)
    interest_rate = st.slider("대출 금리 (%)", 3.0, 7.0, 4.5, 0.1)
    
    st.subheader("보유 자산 상세")
    my_cash = st.number_input("실제 보유 현금 (원)", value=100000000)
    severance_pay = st.number_input("퇴직금 예상액 (원)", value=50000000)
    family_support = st.number_input("기타 지원금 (원)", value=50000000)
    
    total_cash = my_cash + severance_pay + family_support
    st.info(f"총 가용 현금: {total_cash/100000000:.2f}억 원")
    
    st.divider()
    
    st.header("📍 지역 및 기간 선택")
    # 시/도 선택에 따른 시/군/구 종속 선택
    selected_sido = st.selectbox("시/도 선택", list(REGION_DATA.keys()))
    sigungu_list = list(REGION_DATA[selected_sido].keys())
    selected_sigungu = st.selectbox("시/군/구 선택", sigungu_list)
    
    # 데이터 업데이트 주기를 고려하여 기본값을 1~2개월 전으로 설정 권장
    target_month = st.text_input("조회 월 (YYYYMM)", value="202512")

    st.divider()
    
    # 🚀 분석 실행 버튼
    launch_button = st.button("🚀 데이터 분석 런칭", use_container_width=True)

# 4. 상단 요약 정보 (DSR 기반 예산 산출)
# 원리금균등상환 30년, DSR 40% 기준 역산
max_annual_pay = salary * 0.4
monthly_rate = (interest_rate / 100) / 12
total_months = 30 * 12

if monthly_rate > 0:
    estimated_max_loan = (max_annual_pay / 12) * ((1 + monthly_rate)**total_months - 1) / (monthly_rate * (1 + monthly_rate)**total_months)
else:
    estimated_max_loan = (max_annual_pay / 12) * total_months

buyable_price = estimated_max_loan + total_cash

st.success(f"✅ 권노운님의 현재 매수 가능 예산(자본+대출): 약 **{buyable_price/100000000:.2f}억 원**")

# 5. 메인 분석 로직
if launch_button:
    service_key = st.secrets.get("SERVICE_KEY", None)
    sigungu_code = REGION_DATA[selected_sido][selected_sigungu]

    if not service_key:
        st.warning("⚠️ 서비스 키가 등록되지 않았습니다. 샘플 데이터를 표시합니다.")
        # 샘플 데이터 구성
        df = pd.DataFrame({
            '단지': [f'{selected_sigungu} 아파트A', f'{selected_sigungu} 아파트B', '단지C', '단지D'],
            '전용면적': [59.9, 84.5, 59.8, 84.9],
            '거래금액(만원)': [75000, 92000, 68000, 110000],
            '층': [12, 5, 8, 20],
            '년': [2025, 2025, 2025, 2025],
            '월': [12, 12, 12, 12]
        })
    else:
        try:
            # API 호출
            api = TransactionPrice(service_key)
            df = api.get_data(
                property_type="아파트",
                trade_type="매매",
                sigungu_code=sigungu_code,
                year_month=target_month
            )
        except Exception as e:
            st.error(f"🚨 API 데이터 로드 중 오류가 발생했습니다: {e}")
            df = pd.DataFrame()

    # 결과 시각화
    if not df.empty:
        st.subheader(f"📊 {selected_sido} {selected_sigungu} ({target_month}) 분석 결과")
        
        # 컬럼명 처리 (API 버전에 따라 다를 수 있음)
        price_col = '거래금액' if '거래금액' in df.columns else '거래금액(만원)'
        
        # 숫자형 변환 (쉼표 제거 등)
        if df[price_col].dtype == object:
            df[price_col] = df[price_col].str.replace(',', '').astype(int)
        
        # 매수 가능 여부 판단 (만원 단위 환산)
        df['매수성공가능'] = df[price_col].apply(lambda x: (x * 10000) <= buyable_price)
        
        # 하이라이트 함수
        def highlight_buyable(row):
            return ['background-color: #d4edda' if row['매수성공가능'] else '' for _ in row]

        # 데이터프레임 출력
        st.dataframe(
            df.style.apply(highlight_buyable, axis=1),
            use_container_width=True
        )
        
        # 간단한 통계
        col1, col2 = st.columns(2)
        with col1:
            st.metric("조회된 거래 건수", f"{len(df)}건")
        with col2:
            buyable_count = df['매수성공가능'].sum()
            st.metric("내 예산 안 매물", f"{buyable_count}건", delta=f"{buyable_count/len(df)*100:.1f}%")
            
    else:
        st.info(f"🧐 {target_month}월에는 {selected_sigungu} 지역에 신고된 거래 데이터가 없습니다. 한두 달 전으로 조회해 보세요.")

else:
    st.info("👈 왼쪽 사이드바에서 조건을 설정한 후 '분석 런칭' 버튼을 눌러주세요.")
