import streamlit as st
import pandas as pd
import re

# 시간 변환 함수 (기존과 동일)
def convert_to_seconds(time_val):
    if pd.isna(time_val) or time_val == "":
        return 0
    try:
        if isinstance(time_val, (int, float)):
            return time_val * 86400
        time_str = str(time_val).strip()
        parts = list(map(int, re.split('[:.]', time_str)))
        if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        elif len(parts) == 2: return parts[0] * 60 + parts[1]
    except:
        return 0
    return 0

def format_seconds_to_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# UI 구성
st.set_page_config(page_title="Event ID Tracker", layout="wide")
st.title("🆔 Event ID별 누적 시간 합산 툴")
st.info("B열의 Event ID와 P열의 시간을 매칭하여 합산합니다.")

files = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx", "xls"], accept_multiple_files=True)

if files:
    all_data = []
    for f in files:
        try:
            df = pd.read_excel(f)
            
            # B열(1) Event ID, P열(15) 시간 데이터 추출
            # dropna()를 통해 빈 행은 제외합니다.
            temp_df = df.iloc[:, [1, 15]].dropna(how='all')
            temp_df.columns = ['Event_ID', 'Duration']
            
            # 시간 데이터를 초 단위로 변환
            temp_df['Seconds'] = temp_df['Duration'].apply(convert_to_seconds)
            
            all_data.append(temp_df)
        except Exception as e:
            st.error(f"Error in {f.name}: {e}")

    if all_data:
        # 모든 파일 데이터 통합
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Event ID별로 그룹화하여 합산
        event_summary = combined_df.groupby('Event_ID')['Seconds'].sum().reset_index()
        
        # 초 단위를 다시 00:00:00 서식으로 변환
        event_summary['Total_Time'] = event_summary['Seconds'].apply(format_seconds_to_time)
        
        # 결과 출력
        st.subheader("📋 Event ID별 합산 결과")
        # 보기 좋게 정렬 (시간순 혹은 ID순)
        event_summary = event_summary.sort_values(by='Event_ID')
        
        st.dataframe(event_summary[['Event_ID', 'Total_Time']], use_container_width=True)
        
        # CSV 다운로드 기능
        csv = event_summary[['Event_ID', 'Total_Time']].to_csv(index=False).encode('utf-8-sig')
        st.download_button("결과를 CSV로 저장", csv, "event_summary.csv", "text/csv")
