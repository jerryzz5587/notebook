import pandas as pd
import glob

pd.set_option('display.float_format', '{:.0f}'.format)
# 1. 파일 경로 설정 및 여러 CSV 파일 합치기 (23년 1월 ~ 6월)
file_paths_main = glob.glob("C:/Mtest/pj/2301~06/*.csv")
file_station_info = "C:/Mtest/pj/대여소/23대여소/서울특별시 공공자전거 대여소별 이용정보(월별)_23.1-6.csv"
df_list = [pd.read_csv(file, encoding='utf-8') for file in file_paths_main]
if len(file_paths_main) == 1:
    df_main = pd.read_csv(file_paths_main[0], encoding='utf-8')
else:
    # 여러 파일일 경우 concat 사용
    df_list = [pd.read_csv(file, encoding='utf-8') for file in file_paths_main]
    df_main = pd.concat(df_list, ignore_index=True)

df_station = pd.read_csv(file_station_info, encoding='cp949')
df = pd.merge(df_main, df_station[['대여소명', '자치구']], on='대여소명', how='left')




# 2. 성별 null 값 제거 및 '남자', '여자'로 변환
df = df.dropna(subset=['성별'])  # 성별이 null인 데이터 제거
df['성별'] = df['성별'].replace({'남성': 'M', '여성': 'F'})  # 성별 변환
df['성별'] = df['성별'].replace({'M': '남자', 'F': '여자'})  # 'M'을 '남자', 'F'를 '여자'로 변환

# 3. 연령대에서 '기타' 제외
df = df[df['연령대코드'] != '기타']  # 연령대가 '기타'인 데이터 제외

# 4. 대여일자 형식을 datetime 형식으로 변환
df['대여일자'] = pd.to_datetime(df['대여일자'], format='%Y-%m-%d')

# 5. 이용시간을 시간 단위로 변환 (소수점 제외)
df['이용시간(시간)'] = df['이용시간(분)'] // 60  # 분 -> 시간으로 변환, 소수점 제외

# 6. 연령대 변환 (코드 대신 실제 연령대로 표시)
df['연령대'] = df['연령대코드'].replace({
    '~10대': '10대 이하',
    '20대': '20대',
    '30대': '30대',
    '40대': '40대',
    '50대': '50대',
    '60대': '60대',
    '70대~': '70대 이상'
})
### 1. 시간대별 연령별 자전거 대여건수, 대여시간, 이동거리(KM), 운동량, 탄소량 출력 ###
print("2024.01.01 ~ 2024.05.30 시간대별 연령별 자전거 대여건수, 대여시간(시간), 이동거리(KM), 운동량(칼로리), 탄소량(kg):")

# 운동량 및 탄소 절감량 계산 함수
def calculate_workout_and_carbon(distance_km):
    workout_calories = distance_km * 30   # 1km 당 30 칼로리 소모
    carbon_savings = distance_km * 0.21   # 1km 당 0.21kg 탄소 절감
    return workout_calories, carbon_savings

hours = range(24)  # 0시부터 23시까지의 시간대

for hour in hours:
    # 각 시간대별 연령대별 데이터
    hourly_age_rent_count = df[df['대여시간'] == hour].groupby('연령대').size()
    hourly_age_rent_time = df[df['대여시간'] == hour].groupby('연령대')['이용시간(시간)'].sum()
    hourly_age_distance = df[df['대여시간'] == hour].groupby('연령대')['이동거리(M)'].sum() / 1000  # 이동거리(M)를 km로 변환

    # 운동량 및 탄소량 계산
    workout_calories, carbon_savings = calculate_workout_and_carbon(hourly_age_distance)

    # 데이터 통합 및 출력
    age_data = pd.DataFrame({
        '대여건수': hourly_age_rent_count, 
        '대여시간(시간)': hourly_age_rent_time, 
        '이동거리(KM)': hourly_age_distance, 
        '운동량(칼로리)': workout_calories, 
        '탄소량(kg)': carbon_savings
    }).reindex(
        ['10대 이하', '20대', '30대', '40대', '50대', '60대', '70대 이상']
    ).fillna(0).astype(int)

    # 0이 아닌 데이터만 필터링
    age_data = age_data[(age_data['대여건수'] > 0) & 
                        (age_data['이동거리(KM)'] > 0) & 
                        (age_data['대여시간(시간)'] > 0) & 
                        (age_data['운동량(칼로리)'] > 0) & 
                        (age_data['탄소량(kg)'] > 0)]
    
    if not age_data.empty:
        print(f"\n2024.01.01 ~ 2024.05.30 대여시간 {hour}시 연령대별 데이터:")
        print(age_data)
        total_count = len(df)
    # 가장 많이 대여한 연령대 찾기
    total_age_rent_count = df.groupby('연령대').size()
    if len(hourly_age_rent_count) > 0:
        most_rented_age = hourly_age_rent_count.idxmax()
        most_rented_age_count = hourly_age_rent_count.max()
        print(f"2024.01.01 ~ 2024.05.30 {hour}시에는 {most_rented_age}가 많이 탔음 ({most_rented_age_count}명)")
        total_count = len(df)
# 연령대별 대여수 평균 계산
# 가장 많이 대여된 연령대 계산
most_rented_age_overall = total_age_rent_count.idxmax()
most_rented_age_count_overall = total_age_rent_count.max()
average_age_rent_count = total_age_rent_count.mean()
percentage_above_average_age = ((most_rented_age_count_overall - average_age_rent_count) / average_age_rent_count) * 100
print(f"\n모든 시간 통틀어 가장 대여가 많이 발생한 연령대: {most_rented_age_overall} ({most_rented_age_count_overall}건)")
print(f"다른 연령대의 평균 대여수: {average_age_rent_count:.2f}건")
print(f"가장 많이 대여된 연령대의 대여수가 다른 연령대의 평균 대여수보다 {percentage_above_average_age:.2f}% 높음.")       
print(f"24년 연령별 총 데이터수: {total_count}개")