import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 타이틀
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="교통수단별 탄소배출 대시보드",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 교통수단별 탄소배출 및 탄소발자국 대시보드")
st.markdown("일상 속 이동 수단 선택이 환경과 기후변화에 미치는 영향을 데이터로 쉽게 비교하고 확인해보세요.")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. 기초 데이터 (교통수단별 1km당 CO2 배출량 - 평균 참고치, 단위: g/km)
# -----------------------------------------------------------------------------
data = {
    "교통수단": [
        "지하철 / 전기열차", 
        "고속열차 (KTX/SRT)", 
        "시내버스", 
        "고속/시외버스", 
        "하이브리드 승용차", 
        "가솔린 승용차", 
        "디젤 승용차", 
        "국내선 항공기"
    ],
    "1km당 CO2 배출량(g)": [6, 14, 28, 33, 90, 150, 170, 255],
    "카테고리": ["대중교통", "대중교통", "대중교통", "대중교통", "개인교통", "개인교통", "개인교통", "항공"]
}

df = pd.DataFrame(data)

# -----------------------------------------------------------------------------
# 3. 사이드바 - 나의 이동 습관 계산기
# -----------------------------------------------------------------------------
st.sidebar.header("🚗 나의 이동 탄소발자국 계산기")
st.sidebar.markdown("평소 이동하는 습관을 입력하여 배출량을 계산해보세요.")

selected_transport = st.sidebar.selectbox(
    "주로 이용하는 교통수단을 선택하세요:",
    df["교통수단"].tolist(),
    index=5  # 기본값: 가솔린 승용차
)

distance_km = st.sidebar.slider("1회 이동 거리 (km):", 1, 500, 30)
frequency_per_week = st.sidebar.slider("주간 이동 횟수 (왕복 기준 횟수):", 1, 14, 5)

# 선택된 교통수단의 배출량 조회
emission_per_km = df.loc[df["교통수단"] == selected_transport, "1km당 CO2 배출량(g)"].values[0]
weekly_emission_g = emission_per_km * distance_km * frequency_per_week
annual_emission_kg = (weekly_emission_g * 52) / 1000  # kg 단위 변환

# 소나무 1그루당 연간 CO2 흡수량 약 6.6kg 가정
trees_needed = annual_emission_kg / 6.6

# -----------------------------------------------------------------------------
# 4. 상단 요약 매트릭스 (KPI Cards)
# -----------------------------------------------------------------------------
st.subheader(f"📊 '{selected_transport}' 이용 시 나의 탄소발자국 분석")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="1회 이동 시 배출량", value=f"{emission_per_km * distance_km:,} g CO₂")
with col2:
    st.metric(label="연간 예상 배출량", value=f"{annual_emission_kg:,.1f} kg CO₂")
with col3:
    st.metric(
        label="상쇄를 위해 필요한 소나무", 
        value=f"약 {trees_needed:,.1f} 그루",
        delta="연간 기준",
        delta_color="off"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 교통수단별 온실가스 배출량 비교 시각화 (Plotly 차트)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("💡 교통수단별 1km당 CO₂ 배출량 비교")
    
    color_map = {
        "대중교통": "#2E8B57",   # SeaGreen
        "개인교통": "#E6A817",   # Amber/Orange
        "항공": "#CD5C5C"        # IndianRed
    }
    
    fig_bar = px.bar(
        df.sort_values("1km당 CO2 배출량(g)", ascending=True),
        x="1km당 CO2 배출량(g)",
        y="교통수단",
        color="카테고리",
        color_discrete_map=color_map,
        orientation='h',
        text="1km당 CO2 배출량(g)",
        height=400
    )
    
    fig_bar.update_traces(texttemplate='%{text} g', textposition='outside')
    fig_bar.update_layout(
        xaxis_title="CO₂ 배출량 (g/km)",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=20, t=30, b=0),
        legend=dict(title="분류", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🌱 대중교통 전환 시 감축 효과")
    st.markdown(f"현재 **{selected_transport}**(으)로 연간 **{annual_emission_kg:,.1f} kg**의 탄소를 배출하고 있습니다.")
    
    subway_emission_km = df.loc[df["교통수단"] == "지하철 / 전기열차", "1km당 CO2 배출량(g)"].values[0]
    subway_annual_kg = (subway_emission_km * distance_km * frequency_per_week * 52) / 1000
    reduction_kg = annual_emission_kg - subway_annual_kg
    
    if reduction_kg > 0:
        st.success(f"🎉 지하철/전기열차로 전환할 경우, **연간 {reduction_kg:,.1f} kg CO₂**를 줄일 수 있습니다!")
        st.write(f"이는 소나무 **약 {reduction_kg / 6.6:,.1f}그루**를 새로 심는 것과 동일한 환경적 가치를 가집니다.")
    else:
        st.info("👍 이미 가장 친환경적인 대중교통 수단을 이용하고 계십니다! 훌륭합니다!")
        
    compare_df = pd.DataFrame({
        "구분": [f"현재 ({selected_transport})", "지하철 전환 시"],
        "연간 배출량(kg)": [annual_emission_kg, subway_annual_kg]
    })
    
    fig_pie = px.pie(
        compare_df, 
        names="구분", 
        values="연간 배출량(kg)",
        color="구분",
        color_discrete_sequence=["#FF7F50", "#2E8B57"],
        hole=0.4
    )
    fig_pie.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=250)
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. 하단 데이터 테이블 안내
# -----------------------------------------------------------------------------
with st.expander("📋 상세 데이터 표 보기 및 참고문헌"):
    st.dataframe(df.style.background_gradient(subset=["1km당 CO2 배출량(g)"], cmap="Greens"), use_container_width=True)
    st.markdown("- 출처: 유럽환경청(EEA) 및 한국기후환경 네트워크 추정치 기반 예시 데이터\n- 참고: 실제 배출량은 탑승 인원 및 주행 환경에 따라 달라질 수 있습니다.")
