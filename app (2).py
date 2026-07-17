import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="🌍 탄소배출 대시보드", layout="wide", initial_sidebar_state="expanded")

# CSS 커스텀
st.markdown("""
    <style>
        body { font-family: 'Segoe UI', sans-serif; }
        .metric-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      padding: 20px; border-radius: 10px; color: white; }
    </style>
""", unsafe_allow_html=True)

# 제목
st.title("🌍 교통수단별 탄소배출 대시보드")
st.markdown("---")

# 데이터 정의
usage_data = {
    "자가용": 84.2,
    "항공기": 9.6,
    "버스": 3.9,
    "철도": 3.7,
}

emission_factor = {
    "자가용": 171,
    "버스": 28,
    "철도": 18,
    "항공기": 255,
}

avg_speed = {
    "자가용": 90,
    "버스": 70,
    "철도": 300,
    "항공기": 900,
}

# 배출량 계산
emission_raw = {mode: usage_data[mode] * emission_factor[mode] for mode in usage_data}
total_emission = sum(emission_raw.values())
emission_share = {mode: (emission_raw[mode] / total_emission * 100) for mode in usage_data}
hourly_emission = {mode: (avg_speed[mode] * emission_factor[mode] / 1000) for mode in usage_data}

# ============= 패널1: 이용률 vs 탄소배출 =============
st.header("📊 패널1: 교통수단별 이용률 vs 탄소배출량")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🚗 이용률 (%)")
    fig1 = go.Figure(data=[
        go.Bar(
            y=list(usage_data.keys()),
            x=list(usage_data.values()),
            orientation='h',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
            text=[f"{v:.1f}%" for v in usage_data.values()],
            textposition='auto'
        )
    ])
    fig1.update_layout(height=400, showlegend=False, xaxis_title="이용률(%)")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("💨 탄소배출 비중 (%)")
    fig2 = go.Figure(data=[
        go.Bar(
            y=list(emission_share.keys()),
            x=list(emission_share.values()),
            orientation='h',
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
            text=[f"{v:.1f}%" for v in emission_share.values()],
            textposition='auto'
        )
    ])
    fig2.update_layout(height=400, showlegend=False, xaxis_title="탄소배출 비중(%)")
    st.plotly_chart(fig2, use_container_width=True)

st.info("💡 **발견**: 자가용은 이용률 84%이지만 탄소배출은 88%! 이용률 대비 더 많은 배출")

# ============= 패널2: 시간 대비 탄소배출 =============
st.header("⏱️ 패널2: 이동시간 입력 → 탄소배출 계산")

col_time1, col_time2 = st.columns([2, 1])
with col_time1:
    travel_time_min = st.slider("이동 시간을 선택하세요 (분)", 10, 240, 60, step=10)
with col_time2:
    hours = travel_time_min / 60
    st.metric("선택한 시간", f"{travel_time_min}분", f"= {hours:.1f}시간")

travel_time_hour = travel_time_min / 60

emission_by_time = {mode: (hourly_emission[mode] * travel_time_hour) for mode in usage_data}

fig3 = go.Figure(data=[
    go.Bar(
        x=list(emission_by_time.keys()),
        y=list(emission_by_time.values()),
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
        text=[f"{v:.2f} kg" for v in emission_by_time.values()],
        textposition='auto'
    )
])
fig3.update_layout(
    title=f"🌍 {travel_time_min}분 이동 시 교통수단별 탄소배출량",
    height=400,
    showlegend=False,
    yaxis_title="탄소배출량 (kg CO2)"
)
st.plotly_chart(fig3, use_container_width=True)

# 비교 텍스트
st.markdown("---")
col_comp1, col_comp2, col_comp3 = st.columns(3)
with col_comp1:
    st.metric("🚗 자가용", f"{emission_by_time['자가용']:.2f} kg", "기준값")
with col_comp2:
    savings_bus = (emission_by_time['자가용'] - emission_by_time['버스']) / emission_by_time['자가용'] * 100
    st.metric("🚌 버스로 가면", f"절감: {savings_bus:.0f}%")
with col_comp3:
    savings_train = (emission_by_time['자가용'] - emission_by_time['철도']) / emission_by_time['자가용'] * 100
    st.metric("🚄 철도로 가면", f"절감: {savings_train:.0f}%")

# ============= 패널3: 거리별 탄소발자국 시뮬레이터 =============
st.header("🛣️ 패널3: 여행 거리별 탄소발자국 시뮬레이터")

col_dist1, col_dist2 = st.columns([2, 1])
with col_dist1:
    distance_km = st.slider("여행 거리를 선택하세요 (km)", 50, 1000, 400, step=50)
with col_dist2:
    st.metric("선택한 거리", f"{distance_km} km")

# 각 수단별 배출량
distance_emission = {mode: (distance_km * emission_factor[mode] / 1000) for mode in usage_data}

fig4 = go.Figure(data=[
    go.Bar(
        x=list(distance_emission.keys()),
        y=list(distance_emission.values()),
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'],
        text=[f"{v:.1f} kg" for v in distance_emission.values()],
        textposition='auto'
    )
])
fig4.update_layout(
    title=f"🌍 {distance_km}km 여행 시 교통수단별 탄소배출량",
    height=400,
    showlegend=False,
    yaxis_title="탄소배출량 (kg CO2)"
)
st.plotly_chart(fig4, use_container_width=True)

# 나무 흡수량 환산 (1그루당 연간 약 20kg CO2 흡수)
tree_absorption_per_year = 20  # kg CO2/year

col_tree1, col_tree2, col_tree3, col_tree4 = st.columns(4)
modes_list = list(distance_emission.keys())

for idx, (col, mode) in enumerate(zip([col_tree1, col_tree2, col_tree3, col_tree4], modes_list)):
    trees_needed = distance_emission[mode] / tree_absorption_per_year
    tree_text = f"{trees_needed:.1f}그루"
    col.metric(f"🌲 {mode}", tree_text, help="1년간 흡수할 나무 수")

st.markdown("---")

# ============= 요약 통계 =============
st.header("📈 종합 통계")

tab1, tab2 = st.tabs(["교통수단 비교", "탄소 절감 시뮬레이션"])

with tab1:
    summary_df = pd.DataFrame({
        "교통수단": list(usage_data.keys()),
        "이용률(%)": list(usage_data.values()),
        "배출계수(gCO2e/km)": [emission_factor[m] for m in usage_data.keys()],
        "배출비중(%)": [emission_share[m] for m in usage_data.keys()],
        "평균속도(km/h)": [avg_speed[m] for m in usage_data.keys()],
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("자가용을 다른 수단으로 바꾸면?")
    
    if distance_km > 0:
        car_emission = distance_emission['자가용']
        
        for mode in ['버스', '철도', '항공기']:
            alternative_emission = distance_emission[mode]
            reduction = car_emission - alternative_emission
            reduction_pct = (reduction / car_emission * 100)
            
            st.write(f"**{mode}로 변경:**")
            col_alt1, col_alt2 = st.columns(2)
            with col_alt1:
                reduction_text = f"{reduction:.2f} kg CO2"
                pct_text = f"{reduction_pct:.1f}% 절감"
                st.metric("배출량 감소", reduction_text, pct_text)
            with col_alt2:
                trees = reduction / tree_absorption_per_year
                tree_count = f"{trees:.1f}그루"
                st.metric("나무 절약", tree_count)
            st.markdown("---")

# 푸터
st.markdown("---")
st.info("🌱 **탄소여권 프로젝트**: 교통수단 선택으로 탄소발자국을 줄이세요!")
