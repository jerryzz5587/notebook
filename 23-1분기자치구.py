import pandas as pd
import glob

pd.set_option('display.float_format', '{:.0f}'.format)

# 1. 파일 경로 설정 및 여러 CSV 파일 합치기 (23년 1월 ~ 6월)
file_paths_main = glob.glob("C:/Mtest/pj/2301~06/*.csv")
file_station_info = "C:/Mtest/pj/대여소/23대여소/서울특별시 공공자전거 대여소별 이용정보(월별)_23.1-6.csv"

# 파일 로드
df_list = [pd.read_csv(file, encoding='utf-8') for file in file_paths_main]
df_main = pd.concat(df_list, ignore_index=True)

# 대여소 정보 로드 및 병합
df_station = pd.read_csv(file_station_info, encoding='cp949')
df = pd.merge(df_main, df_station[['대여소명', '자치구']], on='대여소명', how='left')



# 연령대에서 '기타' 제외
df = df[df['연령대코드'] != '기타']  # 연령대가 '기타'인 데이터 제외

# 대여일자 형식을 datetime 형식으로 변환
df['대여일자'] = pd.to_datetime(df['대여일자'], format='%Y-%m-%d')

# 이용시간을 시간 단위로 변환 (소수점 제외)
df['이용시간(시간)'] = df['이용시간(분)'] // 60  # 분 -> 시간으로 변환, 소수점 제외

# 연령대 변환 (코드 대신 실제 연령대로 표시)
df['연령대'] = df['연령대코드'].replace({
    '~10대': '10대 이하',
    '20대': '20대',
    '30대': '30대',
    '40대': '40대',
    '50대': '50대',
    '60대': '60대',
    '70대~': '70대 이상'
})

# 운동량 및 탄소 절감량 계산 함수
def calculate_workout_and_carbon(distance_km):
    workout_calories = distance_km * 30   # 1km 당 30 칼로리 소모
    carbon_savings = distance_km * 0.21   # 1km 당 0.21kg 탄소 절감
    return workout_calories, carbon_savings



print("\n2023.01.01 ~ 2023.06.30 시간대별 자치구별 자전거 대여건수:")

###모든 시간 통틀어 가장 대여가 많이 발생한 자치구
# 서울 24개 자치구 목록
seoul_gu_list = [
    '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', 
    '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', 
    '용산구', '은평구', '종로구', '중구', '중랑구'
]

# 시간대별 자치구별 대여건수 계산 및 출력
hours = range(24)

for hour in hours:
    hourly_gu_rent_count = df[df['대여시간'] == hour].groupby('자치구').size()
    
    # 자치구별 대여건수 DataFrame으로 변환 후 헤더 추가
    df_hourly_gu = pd.DataFrame(hourly_gu_rent_count).reset_index()
    df_hourly_gu.columns = ['자치구', '자전거 대여건수']
    
    print(f"\n2023.01.01 ~ 2023.06.30 대여시간 {hour}시 자치구별 자전거 대여건수:")
    print(df_hourly_gu.to_string(index=False))  # index=False로 인덱스 제거

    # 시간별 가장 대여건수가 많은 자치구
    if not df_hourly_gu.empty:
        most_rented_gu = df_hourly_gu.loc[df_hourly_gu['자전거 대여건수'].idxmax()]
        print(f"{hour}시: 대여건수가 가장 많은 자치구는 {most_rented_gu['자치구']} ({most_rented_gu['자전거 대여건수']}건)")
    
    # 빠진 자치구 확인
    missing_gu = set(seoul_gu_list) - set(hourly_gu_rent_count.index)
    if missing_gu:
        print(f"출력되지 않은 자치구: {', '.join(missing_gu)}")

### 모든 시간 통틀어 가장 대여건수가 많은 자치구 ###
total_gu_rent_count = df.groupby('자치구').size()
most_rented_gu_overall = total_gu_rent_count.idxmax()
most_rented_gu_count_overall = total_gu_rent_count.max()

# 자치구별 대여수 평균 계산
average_rent_count = total_gu_rent_count.mean()
percentage_above_average = ((most_rented_gu_count_overall - average_rent_count) / average_rent_count) * 100
print(f"\n모든 시간 통틀어 가장 대여가 많이 발생한 자치구: {most_rented_gu_overall} ({most_rented_gu_count_overall}건)")
print(f"다른 자치구의 평균 대여수: {average_rent_count:.2f}건")
print(f"가장 많이 대여된 강서구의 대여수가 다른 자치구의 평균 대여수보다 {percentage_above_average:.2f}% 많음.")
total_count = len(df)
print(f"23-1분기자치구 총 데이터수: {total_count}개")