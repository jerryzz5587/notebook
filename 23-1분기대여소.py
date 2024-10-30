import pandas as pd
import glob

pd.set_option('display.float_format', '{:.0f}'.format)

# 파일 경로 설정 및 여러 CSV 파일 합치기 (23년 1월 ~ 6월)
file_paths_main = glob.glob("C:/Mtest/pj/2301~06/*.csv")
file_station_info = "C:/Mtest/pj/대여소/23대여소/서울특별시 공공자전거 대여소별 이용정보(월별)_23.1-6.csv"

# 파일 로드
df_list = [pd.read_csv(file, encoding='utf-8') for file in file_paths_main]
df_main = pd.concat(df_list, ignore_index=True)

# 대여소 정보 로드 및 병합
df_station = pd.read_csv(file_station_info, encoding='cp949')
df = pd.merge(df_main, df_station[['대여소명', '자치구']], on='대여소명', how='left')



#연령대에서 '기타' 제외
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

hours = range(24)

### 시간대별 대여소별 대여건수 (대여가 가장 많은 대여소 출력) ###
print("\n2023.01.01 ~ 2023.06.30 시간대별 대여가 가장 많은 대여소 (상위 1개씩):")

for hour in hours:
    hourly_station_rent_count = df[df['대여시간'] == hour].groupby(['자치구', '대여소명']).size()
    if len(hourly_station_rent_count) > 0:
        most_rented_station = hourly_station_rent_count.idxmax()
        most_rented_station_count = hourly_station_rent_count.max()
        print(f"2023.01.01 ~ 2023.06.30 {hour}시: {most_rented_station[0]} {most_rented_station[1]}에서 {most_rented_station_count}건")

### 모든 시간 통틀어 가장 대여가 많이 발생한 대여소 ###
total_station_rent_count = df.groupby(['자치구', '대여소명']).size()
most_rented_station_overall = total_station_rent_count.idxmax()
most_rented_station_count_overall = total_station_rent_count.max()

print(f"\n모든 시간 통틀어 가장 대여가 많이 발생한 대여소: {most_rented_station_overall[0]} {most_rented_station_overall[1]}에서 {most_rented_station_count_overall}건")
total_count = len(df)
print(f"23-1분기대여소 총 데이터수: {total_count}개")