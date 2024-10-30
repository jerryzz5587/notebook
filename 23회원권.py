import pandas as pd
import glob

pd.set_option('display.float_format', '{:.0f}'.format)
# 파일 경로 설정 및 여러 CSV 파일 합치기 (23년 1월 ~ 12월)
file_paths_main = glob.glob("C:/Mtest/pj/2301~12/*.csv")
file_station_info = "C:/Mtest/pj/대여소/23대여소/서울특별시 공공자전거 대여소별 이용정보(월별)_23.1-6.csv"
file_station_info = "C:/Mtest/pj/대여소/23대여소/서울특별시 공공자전거 대여소별 이용정보(월별)_23.7-12.csv"
df_list = [pd.read_csv(file, encoding='utf-8') for file in file_paths_main]

df_main = pd.concat(df_list, ignore_index=True)
df_station = pd.read_csv(file_station_info, encoding='cp949')

# df_main 사용하여 필요한 데이터를 처리합니다.
df = df_main

# 성별 null 값 제거 및 '남자', '여자'로 변환
df = df.dropna(subset=['성별'])  # 성별이 null인 데이터 제거
df['성별'] = df['성별'].replace({'남성': 'M', '여성': 'F'})  # 성별 변환
df['성별'] = df['성별'].replace({'M': '남자', 'F': '여자'})  # 'M'을 '남자', 'F'를 '여자'로 변환

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

def calculate_workout_and_carbon(distance_km):
    workout_calories = distance_km * 30   # 1km 당 30 칼로리 소모
    carbon_savings = distance_km * 0.21   # 1km 당 0.21kg 탄소 절감
    return workout_calories, carbon_savings

hours = range(24)

print("\n2023.01.01 ~ 2023.12.31 시간대별 정기권, 일일권, 비회원 자전거 대여건수, 대여시간(시간), 이동거리(KM), 운동량(칼로리), 탄소량(kg):")

for hour in hours:
    # 시간대별 정기권, 일일권, 비회원 데이터 필터링
    hourly_pass_type_rent_count = df[(df['대여시간'] == hour) & (df['대여구분코드'].isin(['정기권', '일일권', '일일권(비회원)']))].groupby('대여구분코드').size()
    hourly_pass_type_rent_time = df[(df['대여시간'] == hour) & (df['대여구분코드'].isin(['정기권', '일일권', '일일권(비회원)']))].groupby('대여구분코드')['이용시간(시간)'].sum()
    hourly_pass_type_distance = df[(df['대여시간'] == hour) & (df['대여구분코드'].isin(['정기권', '일일권', '일일권(비회원)']))].groupby('대여구분코드')['이동거리(M)'].sum() / 1000  # 이동거리(M)를 km로 변환

    if not hourly_pass_type_rent_count.empty:
        most_rented_pass_type = hourly_pass_type_rent_count.idxmax()
        most_rented_pass_distance = hourly_pass_type_distance[most_rented_pass_type]
        print(f"\n2023.01.01 ~ 2023.12.31 {hour}시에는 {most_rented_pass_type}이 가장 많이 사용됨 (이동거리: {most_rented_pass_distance:.2f} km)")

    # 운동량 및 탄소량 계산 (이동거리가 있는 데이터만 계산)
    workout_calories, carbon_savings = calculate_workout_and_carbon(hourly_pass_type_distance)

    # 데이터 통합 및 필터링 (0인 데이터 제외)
    pass_type_data = pd.DataFrame({
        '대여건수': hourly_pass_type_rent_count, 
        '대여시간(시간)': hourly_pass_type_rent_time, 
        '이동거리(KM)': hourly_pass_type_distance, 
        '운동량(칼로리)': workout_calories, 
        '탄소량(kg)': carbon_savings
    }).fillna(0)

    # 운동량과 탄소량도 포함하여 0인 데이터 제외
    pass_type_data = pass_type_data[(pass_type_data['대여건수'] > 0) & 
                                    (pass_type_data['이동거리(KM)'] > 0) & 
                                    (pass_type_data['대여시간(시간)'] > 0) & 
                                    (pass_type_data['운동량(칼로리)'] > 0) & 
                                    (pass_type_data['탄소량(kg)'] > 0)]
    if not pass_type_data.empty:
        print(f"\n2023.01.01 ~ 2023.12.31 대여시간 {hour}시 정기권, 일일권, 비회원 데이터:")
        print(pass_type_data)

# 전체 회원권별 대여수 및 이동거리 계산
total_pass_type_rent_count = df[df['대여구분코드'].isin(['정기권', '일일권', '일일권(비회원)'])].groupby('대여구분코드').size()
total_pass_type_distance = df[df['대여구분코드'].isin(['정기권', '일일권', '일일권(비회원)'])].groupby('대여구분코드')['이동거리(M)'].sum() / 1000  # 이동거리(M)를 km로 변환

# 전체 시간 동안 가장 많이 사용된 회원권 계산
overall_most_rented_pass_type = total_pass_type_rent_count.idxmax()
overall_most_rented_pass_count = int(total_pass_type_rent_count.max())
average_pass_type_rent_count = total_pass_type_rent_count.mean()
average_pass_type_distance = total_pass_type_distance.mean()

# 전체 시간 동안 가장 많이 사용된 회원권의 대여수 및 이동거리 비교
percentage_above_average_rent_count = ((overall_most_rented_pass_count - average_pass_type_rent_count) / average_pass_type_rent_count) * 100
percentage_above_average_distance = ((total_pass_type_distance[overall_most_rented_pass_type] - average_pass_type_distance) / average_pass_type_distance) * 100

print(f"\n2023.01.01 ~ 2023.12.31 전체 시간 동안 가장 많이 사용된 회원권: {overall_most_rented_pass_type} ({overall_most_rented_pass_count}건)")
print(f"다른 회원권의 평균 대여수: {average_pass_type_rent_count:.2f}건")
print(f"다른 회원권의 평균 이동거리: {average_pass_type_distance:.2f} km")
print(f"가장 많이 사용된 회원권의 대여수가 다른 회원권의 평균 대여수보다 {percentage_above_average_rent_count:.2f}% 많습니다.")
print(f"가장 많이 사용된 회원권의 이동거리가 다른 회원권의 평균 이동거리보다 {percentage_above_average_distance:.2f}% 많습니다.")

# 총 데이터 수 계산
total_count = len(df)
print(f"23년 회원권 총 데이터수: {total_count}개")
