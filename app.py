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
st.markdown("여행 중 이동 수단 선택과 이동 시간이 환경과 기후변화에 미치는 영향을 데이터로 쉽게 비교하고 확인해보세요.")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. 기초 데이터 (교통수단별 시간당 평균 속도 및 분당/1km당 CO2 배출량)
# -----------------------------------------------------------------------------
# 설명: 이용자가 '이동 시간(시간)'을 입력하면 평균 시속을 적용해 거리를 산출하고 탄소배출량을 계산합니다.
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
    "평균시속(km/h)": [40, 200, 20, 80, 35, 35, 35, 600],
    "카테고리": ["대중교통", "대중교통", "대중교통", "대중교통", "개인교통", "개인교통", "개인교통", "항공"]
}

df = pd.DataFrame(data)
# 1시간당 배출량(g) = 평균시속 * 1km당 배출량
df["1시간당 배출량(g)"] = df["평균시속(km/h)"] * df["1km당 CO2 배출량(g)"]

# -----------------------------------------------------------------------------
# 3. 사이드바 - 장거리 여행 탄소발자국 계산기 (시간 및 편도 횟수 기준)
# -----------------------------------------------------------------------------
st.sidebar.header("🚗 장거리 여행 탄소발자국 계산기")
st.sidebar.markdown("이번 여행에서 선택한 교통수단과 시간을 입력하여 배출량을 계산해보세요!")

selected_transport = st.sidebar.selectbox(
    "이용할 교통수단을 선택하세요:",
    df["교통수단"].tolist(),
    index=1  # 기본값: 고속열차 (KTX/SRT)
)

# 이동 시간(시간) 및 편도 기준 이용 횟수 슬라이더 (0.5시간 = 30분 단위 선택 가능)
time_hours = st.sidebar.slider("1회 이동 시간 (편도 기준, 시간):", 0.5, 24.0, 2.5, step=0.5)
frequency_per_trip = st.sidebar.slider("이용 횟수 (편도 탑승 기준):", 1, 10, 2)

# 선택된 교통수단의 데이터 조회
selected_row = df.loc[df["교통수단"] == selected_transport].iloc[0]
avg_speed = selected_row["평균시속(km/h)"]
emission_per_km = selected_row["1km당 CO2 배출량(g)"]
emission_per_hour = selected_row["1시간당 배출량(g)"]

# 배출량 및 추정 이동 거리 계산
estimated_distance_km = avg_speed * time_hours
single_trip_emission_g = emission_per_hour * time_hours
total_emission_g = single_trip_emission_g * frequency_per_trip
total_emission_kg = total_emission_g / 1000  # kg 단위 변환
annual_projected_kg = total_emission_kg * 12 # 연간 12회(월 1회) 여행 가정 시 비교용

# 소나무 1그루당 연간 CO2 흡수량 약 6.6kg 가정
trees_needed = total_emission_kg / 6.6

# -----------------------------------------------------------------------------
# 4. 상단 요약 매트릭스 (KPI Cards)
# -----------------------------------------------------------------------------
st.subheader(f"📊 '{selected_transport}' (편도 {time_hours}시간, 총 {frequency_per_trip}회 탑승) 여행 탄소발자국 분석")
st.caption(f"💡 선택하신 교통수단의 평균 시속({avg_speed} km/h)을 기준으로 1회당 약 {estimated_distance_km:,.1f} km 이동한 것으로 계산됩니다.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="편도 1회 이동 시 배출량", value=f"{single_trip_emission_g:,.0f} g CO₂")
with col2:
    st.metric(label="이번 여행 총 예상 배출량", value=f"{total_emission_kg:,.2f} kg CO₂")
with col3:
    st.metric(
        label="상쇄를 위해 필요한 소나무", 
        value=f"약 {trees_needed:,.2f} 그루",
        delta="이번 여행 배출량 기준",
        delta_color="off"
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 교통수단별 온실가스 배출량 비교 시각화 (Plotly 차트)
# -----------------------------------------------------------------------------
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader(f"💡 동일 시간(편도 {time_hours}시간) 이동 시 CO₂ 배출량 비교")
    
    color_map = {
        "대중교통": "#2E8B57",   # SeaGreen
        "개인교통": "#E6A817",   # Amber/Orange
        "항공": "#CD5C5C"        # IndianRed
    }
    
    # 시간 기준 차트를 위해 모든 교통수단의 해당 시간 동안 배출량 계산
    df["선택시간당 배출량(g)"] = df["1시간당 배출량(g)"] * time_hours
    
    fig_bar = px.bar(
        df.sort_values("선택시간당 배출량(g)", ascending=True),
        x="선택시간당 배출량(g)",
        y="교통수단",
        color="카테고리",
        color_discrete_map=color_map,
        orientation='h',
        text="선택시간당 배출량(g)",
        height=400
    )
    
    fig_bar.update_traces(texttemplate='%{text:,.0f} g', textposition='outside')
    fig_bar.update_layout(
        xaxis_title=f"편도 {time_hours}시간 이동 시 CO₂ 배출량 (g)",
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=20, t=30, b=0),
        legend=dict(title="분류", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🌱 친환경 열차 전환 시 감축 효과")
    st.markdown(f"이번 여행에서 **{selected_transport}**(으)로 총 **{total_emission_kg:,.2f} kg**의 탄소를 배출하게 됩니다.")
    
    # 고속열차(KTX/SRT)로 동일 시간(또는 동일 거리) 이동할 경우 비교
    train_row = df.loc[df["교통수단"] == "고속열차 (KTX/SRT)"].iloc[0]
    train_total_kg = (train_row["1km당 CO2 배출량(g)"] * estimated_distance_km * frequency_per_trip) / 1000
    reduction_kg = total_emission_kg - train_total_kg
    
    if reduction_kg > 0:
        st.success(f"🎉 동일 거리를 **고속열차(KTX/SRT)**로 전환할 경우, **{reduction_kg:,.2f} kg CO₂**를 줄일 수 있습니다!")
        st.write(f"이는 소나무 **약 {reduction_kg / 6.6:,.2f}그루**가 1년 동안 흡수하는 탄소량과 같습니다.")
    else:
        st.info("👍 이미 아주 친환경적인 대중교통 수단을 이용해 여행하고 계십니다! 훌륭합니다!")
        
    compare_df = pd.DataFrame({
        "구분": [f"현재 선택 ({selected_transport})", "고속열차 전환 시"],
        "총 배출량(kg)": [total_emission_kg, train_total_kg]
    })
    
    fig_pie = px.pie(
        compare_df, 
        names="구분", 
        values="총 배출량(kg)",
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
    display_df = df[["교통수단", "카테고리", "평균시속(km/h)", "1km당 CO2 배출량(g)", "1시간당 배출량(g)"]].copy()
    display_df["1시간당 배출량(g)"] = display_df["1시간당 배출량(g)"].round(1)
    st.dataframe(display_df.style.background_gradient(subset=["1km당 CO2 배출량(g)"], cmap="Greens"), use_container_width=True)
    st.markdown("- 출처: 유럽환경청(EEA) 및 한국기후환경 네트워크 추정치 기반 예시 데이터\n- 참고: 장거리 이동 기준 계산을 위해 교통수단별 평균 이동 속도(고속열차 200km/h, 고속버스 80km/h, 항공기 600km/h 등)를 적용하여 거리를 환산했습니다.")
