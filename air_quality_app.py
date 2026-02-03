import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ============================================
# 페이지 설정
# ============================================
st.set_page_config(
    page_title="천안도시공사 실내공기질 확인",
    page_icon="🏢",
    layout="wide"
)

# ============================================
# 환경 기준치 설정
# ============================================
AIR_QUALITY_STANDARDS = {
    '미세먼지': {
        'unit': 'μg/m³',
        'good': 30,
        'moderate': 80,
        'bad': 150,
        'name': '미세먼지(PM10)'
    },
    '초미세먼지': {
        'unit': 'μg/m³',
        'good': 15,
        'moderate': 35,
        'bad': 75,
        'name': '초미세먼지(PM2.5)'
    },
    '이산화탄소': {
        'unit': 'ppm',
        'good': 450,
        'moderate': 700,
        'bad': 1000,
        'name': '이산화탄소(CO₂)'
    },
    '폼알데하이드': {
        'unit': 'μg/m³',
        'good': 60,
        'moderate': 100,
        'bad': 210,
        'name': '폼알데하이드(HCHO)'
    },
    '일산화탄소': {
        'unit': 'ppm',
        'good': 5,
        'moderate': 10,
        'bad': 25,
        'name': '일산화탄소(CO)'
    },
    '이산화질소': {
        'unit': 'ppm',
        'good': 0.03,
        'moderate': 0.05,
        'bad': 0.10,
        'name': '이산화질소(NO₂)'
    },
    '라돈': {
        'unit': 'Bq/m³',
        'good': 100,
        'moderate': 148,
        'bad': 200,
        'name': '라돈(Rn)'
    },
    '총휘발성유기화합물': {
        'unit': 'μg/m³',
        'good': 400,
        'moderate': 500,
        'bad': 1000,
        'name': 'TVOC'
    }
}


# ============================================
# 함수 정의
# ============================================

def load_data():
    """CSV 데이터 로드"""
    df = pd.read_csv(
        ".\천안도시공사_실내공기질측정현황_20240701.csv",
        encoding='euc-kr'
    )
    return df


def extract_building_name(location):
    """측정지점에서 건물명 추출"""
    return location.rsplit('-', 1)[0].strip()


def get_air_quality_status(value, pollutant):
    """공기질 상태 판정"""
    if pollutant not in AIR_QUALITY_STANDARDS:
        return "알 수 없음", "⚪"
    
    standards = AIR_QUALITY_STANDARDS[pollutant]
    
    if value <= standards['good']:
        return "좋음", "🟢"
    elif value <= standards['moderate']:
        return "보통", "🟡"
    elif value <= standards['bad']:
        return "나쁨", "🟠"
    else:
        return "매우 나쁨", "🔴"


def create_gauge_chart(value, pollutant):
    """게이지 차트 생성"""
    if pollutant not in AIR_QUALITY_STANDARDS:
        return None
    
    standards = AIR_QUALITY_STANDARDS[pollutant]
    status, icon = get_air_quality_status(value, pollutant)
    
    # 색상 설정
    if status == "좋음":
        color = "#00C851"
    elif status == "보통":
        color = "#FFD700"
    elif status == "나쁨":
        color = "#FF8800"
    else:
        color = "#FF4444"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{icon} {standards['name']}<br>{status}", 'font': {'size': 16}},
        number={'suffix': f" {standards['unit']}", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, standards['bad'] * 1.2]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, standards['good']], 'color': '#E8F5E9'},
                {'range': [standards['good'], standards['moderate']], 'color': '#FFF9C4'},
                {'range': [standards['moderate'], standards['bad']], 'color': '#FFE0B2'},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': standards['bad']
            }
        }
    ))
    
    fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
    
    return fig


def create_comparison_chart(df, pollutant):
    """건물 간 비교 차트"""
    df_copy = df.copy()
    df_copy['건물명'] = df_copy['측정지점'].apply(extract_building_name)
    
    # 건물별 평균
    building_avg = df_copy.groupby('건물명')[pollutant].mean().reset_index()
    building_avg = building_avg.sort_values(pollutant, ascending=True)
    
    fig = px.bar(
        building_avg,
        x=pollutant,
        y='건물명',
        orientation='h',
        title=f"건물별 {AIR_QUALITY_STANDARDS[pollutant]['name']} 비교",
        labels={pollutant: f"{AIR_QUALITY_STANDARDS[pollutant]['name']} ({AIR_QUALITY_STANDARDS[pollutant]['unit']})"},
        color=pollutant,
        color_continuous_scale=['green', 'yellow', 'orange', 'red']
    )
    
    fig.update_layout(height=400)
    
    return fig


# ============================================
# 메인 앱
# ============================================

st.title("🏢 천안도시공사 실내공기질 확인")
st.markdown("#### 건물명을 입력하여 실내 공기질 정보를 확인하세요")
st.markdown("---")

# 데이터 로드
try:
    df = load_data()
    df['건물명'] = df['측정지점'].apply(extract_building_name)
    st.success(f"✅ 총 {len(df)}개 측정지점의 데이터를 불러왔습니다.")
except Exception as e:
    st.error(f"❌ 데이터 로드 실패: {e}")
    st.stop()

# 사이드바
with st.sidebar:
    st.header("📊 공기질 기준")
    
    st.markdown("""
    ### 등급 기준
    - 🟢 **좋음**: 환기 권장하지 않음
    - 🟡 **보통**: 환기 권장
    - 🟠 **나쁨**: 환기 필요
    - 🔴 **매우 나쁨**: 즉시 환기 필요
    """)
    
    st.markdown("---")
    
    # 건물 목록
    st.subheader("🏢 건물 목록")
    buildings = sorted(df['건물명'].unique())
    for i, building in enumerate(buildings, 1):
        st.write(f"{i}. {building}")
    
    st.markdown("---")
    
    st.info("""
    📅 **측정일자**  
    2024년 7월 1일
    
    📍 **측정기관**  
    천안도시공사
    """)

# ============================================
# 검색 영역
# ============================================

st.subheader("🔍 건물 검색")

# 검색 방법 선택
search_method = st.radio(
    "검색 방법 선택",
    ["드롭다운에서 선택", "직접 입력"],
    horizontal=True
)

if search_method == "드롭다운에서 선택":
    buildings = sorted(df['건물명'].unique())
    selected_building = st.selectbox(
        "건물을 선택하세요",
        ["선택하세요"] + buildings
    )
else:
    selected_building = st.text_input(
        "건물명을 입력하세요",
        placeholder="예: 천안역 지하도상가, 국민체육센터"
    )

search_button = st.button("🔍 검색", type="primary", use_container_width=True)

# ============================================
# 검색 결과 표시
# ============================================

if search_button and selected_building and selected_building != "선택하세요":
    # 건물 데이터 필터링
    building_data = df[df['건물명'].str.contains(selected_building, case=False, na=False)]
    
    if len(building_data) == 0:
        st.warning(f"⚠️ '{selected_building}' 건물을 찾을 수 없습니다.")
        st.info("💡 사이드바의 건물 목록을 참고하세요.")
    else:
        st.markdown("---")
        st.header(f"📊 {selected_building} - 실내공기질 측정 결과")
        
        # 측정지점 정보
        st.info(f"📍 측정지점: {len(building_data)}개소 - {', '.join(building_data['측정지점'].tolist())}")
        
        # 평균값 계산
        avg_values = building_data.select_dtypes(include='number').mean()
        
        # ============================================
        # 미세먼지 정보 (주요 정보)
        # ============================================
        st.markdown("---")
        st.subheader("🌫️ 미세먼지 농도")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pm10 = avg_values['미세먼지']
            status_pm10, icon_pm10 = get_air_quality_status(pm10, '미세먼지')
            
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h2>{icon_pm10} 미세먼지 (PM10)</h2>
                <h1 style='color: #1f77b4; margin: 10px 0;'>{pm10:.1f} μg/m³</h1>
                <h3>{status_pm10}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # 게이지 차트
            fig_pm10 = create_gauge_chart(pm10, '미세먼지')
            st.plotly_chart(fig_pm10, use_container_width=True)
        
        with col2:
            pm25 = avg_values['초미세먼지']
            status_pm25, icon_pm25 = get_air_quality_status(pm25, '초미세먼지')
            
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <h2>{icon_pm25} 초미세먼지 (PM2.5)</h2>
                <h1 style='color: #ff7f0e; margin: 10px 0;'>{pm25:.1f} μg/m³</h1>
                <h3>{status_pm25}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # 게이지 차트
            fig_pm25 = create_gauge_chart(pm25, '초미세먼지')
            st.plotly_chart(fig_pm25, use_container_width=True)
        
        # ============================================
        # 기타 오염물질
        # ============================================
        st.markdown("---")
        st.subheader("🧪 기타 실내 공기질 항목")
        
        # 2x3 그리드
        pollutants = ['이산화탄소', '폼알데하이드', '일산화탄소', '이산화질소', '라돈', '총휘발성유기화합물']
        
        row1_cols = st.columns(3)
        row2_cols = st.columns(3)
        
        for i, pollutant in enumerate(pollutants):
            col = row1_cols[i] if i < 3 else row2_cols[i-3]
            
            with col:
                value = avg_values[pollutant]
                status, icon = get_air_quality_status(value, pollutant)
                standards = AIR_QUALITY_STANDARDS[pollutant]
                
                st.markdown(f"""
                <div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px; height: 150px;'>
                    <h4>{icon} {standards['name']}</h4>
                    <h2 style='margin: 10px 0;'>{value:.1f}</h2>
                    <p style='color: #666;'>{standards['unit']}</p>
                    <p><strong>{status}</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        # ============================================
        # 상세 데이터 테이블
        # ============================================
        st.markdown("---")
        st.subheader("📋 측정지점별 상세 데이터")
        
        # 데이터 정리
        display_df = building_data[['측정지점', '미세먼지', '초미세먼지', '이산화탄소', '폼알데하이드', 
                                      '일산화탄소', '이산화질소', '라돈', '총휘발성유기화합물']].copy()
        
        # 스타일 적용
        def highlight_status(val, pollutant):
            """값에 따라 배경색 지정"""
            if pd.isna(val):
                return ''
            status, _ = get_air_quality_status(val, pollutant)
            if status == "좋음":
                return 'background-color: #E8F5E9'
            elif status == "보통":
                return 'background-color: #FFF9C4'
            elif status == "나쁨":
                return 'background-color: #FFE0B2'
            else:
                return 'background-color: #FFCDD2'
        
        st.dataframe(
            display_df.style.format({
                '미세먼지': '{:.1f}',
                '초미세먼지': '{:.1f}',
                '이산화탄소': '{:.0f}',
                '폼알데하이드': '{:.1f}',
                '일산화탄소': '{:.1f}',
                '이산화질소': '{:.3f}',
                '라돈': '{:.1f}',
                '총휘발성유기화합물': '{:.1f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # ============================================
        # 비교 차트
        # ============================================
        st.markdown("---")
        st.subheader("📊 다른 건물과 비교")
        
        compare_pollutant = st.selectbox(
            "비교할 항목 선택",
            ['미세먼지', '초미세먼지', '이산화탄소', '폼알데하이드', '일산화탄소', 
             '이산화질소', '라돈', '총휘발성유기화합물']
        )
        
        fig_compare = create_comparison_chart(df, compare_pollutant)
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # ============================================
        # 건강 권고사항
        # ============================================
        st.markdown("---")
        st.subheader("💡 건강 권고사항")
        
        # 나쁨 이상인 항목 찾기
        bad_items = []
        for pollutant in pollutants + ['미세먼지', '초미세먼지']:
            value = avg_values[pollutant]
            status, icon = get_air_quality_status(value, pollutant)
            if status in ["나쁨", "매우 나쁨"]:
                bad_items.append((pollutant, status, icon))
        
        if bad_items:
            st.warning("⚠️ 다음 항목의 공기질이 좋지 않습니다:")
            for pollutant, status, icon in bad_items:
                standards = AIR_QUALITY_STANDARDS[pollutant]
                st.markdown(f"- {icon} **{standards['name']}**: {status} → 즉시 환기가 필요합니다!")
        else:
            st.success("✅ 모든 항목이 양호합니다! 쾌적한 실내 환경이 유지되고 있습니다.")
        
        st.info("""
        ### 📌 실내공기질 관리 방법
        
        **일상적 관리**
        - 하루 3회 이상, 회당 10분 이상 환기
        - 실내 습도 40~60% 유지
        - 공기청정기 필터 주기적 교체
        
        **공기질이 나쁠 때**
        - 즉시 환기 실시
        - 공기청정기 가동
        - 민감군(어린이, 노약자) 노출 최소화
        - 실내 활동 자제
        """)

elif search_button and (not selected_building or selected_building == "선택하세요"):
    st.warning("⚠️ 건물을 선택하거나 입력해주세요.")

# ============================================
# 전체 현황
# ============================================

st.markdown("---")
st.subheader("📊 전체 건물 공기질 현황")

# 모든 건물의 평균 미세먼지
tab1, tab2, tab3 = st.tabs(["🌫️ 미세먼지", "📈 통계", "🗂️ 전체 데이터"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pm10_all = create_comparison_chart(df, '미세먼지')
        st.plotly_chart(fig_pm10_all, use_container_width=True)
    
    with col2:
        fig_pm25_all = create_comparison_chart(df, '초미세먼지')
        st.plotly_chart(fig_pm25_all, use_container_width=True)

with tab2:
    st.markdown("### 📊 측정 항목별 평균값")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    overall_avg = df.select_dtypes(include='number').mean()
    
    with col_stat1:
        st.metric(
            "미세먼지 평균",
            f"{overall_avg['미세먼지']:.1f} μg/m³",
            delta=None
        )
        st.metric(
            "초미세먼지 평균",
            f"{overall_avg['초미세먼지']:.1f} μg/m³",
            delta=None
        )
    
    with col_stat2:
        st.metric(
            "이산화탄소 평균",
            f"{overall_avg['이산화탄소']:.0f} ppm",
            delta=None
        )
        st.metric(
            "폼알데하이드 평균",
            f"{overall_avg['폼알데하이드']:.1f} μg/m³",
            delta=None
        )
    
    with col_stat3:
        st.metric(
            "일산화탄소 평균",
            f"{overall_avg['일산화탄소']:.1f} ppm",
            delta=None
        )
        st.metric(
            "이산화질소 평균",
            f"{overall_avg['이산화질소']:.3f} ppm",
            delta=None
        )
    
    with col_stat4:
        st.metric(
            "라돈 평균",
            f"{overall_avg['라돈']:.1f} Bq/m³",
            delta=None
        )
        st.metric(
            "TVOC 평균",
            f"{overall_avg['총휘발성유기화합물']:.1f} μg/m³",
            delta=None
        )

with tab3:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # CSV 다운로드
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name="천안도시공사_실내공기질_측정현황.csv",
        mime="text/csv"
    )

# ============================================
# 푸터
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏢 천안도시공사 실내공기질 측정 현황</p>
    <p style='font-size: 0.8em;'>측정일자: 2024년 7월 1일</p>
    <p style='font-size: 0.8em;'>※ 실내공기질 관리법에 따른 측정 기준 적용</p>
</div>
""", unsafe_allow_html=True)
