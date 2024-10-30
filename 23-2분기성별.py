import pandas as pd
import glob

pd.set_option('display.float_format', '{:.0f}'.format)

# 파일 경로 설정 및 여러 CSV 파일 합치기 (23년 7월 ~ 12월)
file_paths_main = glob.glob("C:/Mtest/pj/2307~12/*.csv")
file_station_info = "C:/Mtest/pj/대여소/23대여소/서울특별시 공공자전거 대여소별 이용정보(월별)_23.7-12.csv"

# 파일이 1개만 있을 경우 처리
if len(file_paths_main) == 1:
    df_main = pd.read_csv(file_paths_main[0], encoding='utf-8')
else:
    # 여러 파일일 경우 concat 사용
    df_list = [pd.read_csv(file, encoding='utf-8') for file in file_paths_main]
    df_main = pd.concat(df_list, ignore_index=True)

# 대여소 정보 읽기
df_station = pd.read_csv(file_station_info, encoding='cp949')

# df_main과 df_station 병합
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

# 성별 null 값 제거 및 '남자', '여자'로 변환
df = df.dropna(subset=['성별'])  # 성별이 null인 데이터 제거
df['성별'] = df['성별'].replace({'남성': 'M', '여성': 'F'})  # 성별 변환
df['성별'] = df['성별'].replace({'M': '남자', 'F': '여자'})  # 'M'을 '남자', 'F'를 '여자'로 변환

# 운동량 및 탄소 절감량 계산 함수 추가
def calculate_workout_and_carbon(distance_km):
    workout_calories = distance_km * 30   # 1km 당 30 칼로리 소모
    carbon_savings = distance_km * 0.21   # 1km 당 0.21kg 탄소 절감
    return workout_calories, carbon_savings

# 전체 시간대의 성별별 대여 건수를 저장하기 위한 시리즈 초기화
total_gender_rent_count = pd.Series(dtype='int')  # 전체 시간대의 성별별 대여 건수 저장을 위한 시리즈

# 시간대별 성별 자전거 대여건수, 대여시간, 이동거리(KM) 및 성별 많이 탄 정보
hours = range(24)
print("\n2023.07.01 ~ 2023.12.31 시간대별 성별 자전거 대여건수, 대여시간(시간), 이동거리(KM) 및 성별 많이 탄 정보:")

for hour in hours:
    # 각 시간대별 성별 데이터
    hourly_gender_rent_count = df[(df['대여시간'] == hour) & (df['성별'].isin(['남자', '여자']))].groupby('성별').size()
    hourly_gender_rent_time = df[(df['대여시간'] == hour) & (df['성별'].isin(['남자', '여자']))].groupby('성별')['이용시간(시간)'].sum()
    hourly_gender_distance = df[(df['대여시간'] == hour) & (df['성별'].isin(['남자', '여자']))].groupby('성별')['이동거리(M)'].sum() / 1000  # 이동거리(M)를 km로 변환

    # 운동량 및 탄소 절감량 계산 함수 호출
    workout_calories, carbon_savings = calculate_workout_and_carbon(hourly_gender_distance)

    # 데이터 통합 및 출력
    gender_data = pd.DataFrame({
        '대여건수': hourly_gender_rent_count, 
        '대여시간(시간)': hourly_gender_rent_time, 
        '이동거리(KM)': hourly_gender_distance, 
        '운동량(칼로리)': workout_calories, 
        '탄소량(kg)': carbon_savings
    }).fillna(0)

    gender_data = gender_data[(gender_data['대여건수'] > 0) & 
                              (gender_data['이동거리(KM)'] > 0) & 
                              (gender_data['대여시간(시간)'] > 0) & 
                              (gender_data['운동량(칼로리)'] > 0) & 
                              (gender_data['탄소량(kg)'] > 0)]

    if not gender_data.empty:
        print(f"\n2023.07.01 ~ 2023.12.31 대여시간 {hour}시 성별 데이터:")
        print(gender_data)

    # 성별이 많이 탄 정보 출력
    if len(hourly_gender_rent_count) > 0:
        most_rented_gender = hourly_gender_rent_count.idxmax()
        most_rented_gender_count = hourly_gender_rent_count.max()
        print(f"2023.07.01 ~ 2023.12.31 {hour}시에는 {most_rented_gender}가 많이 탔음 ({most_rented_gender_count}명)")

    # 전체 시간대의 성별별 대여 건수를 합산
    total_gender_rent_count = total_gender_rent_count.add(hourly_gender_rent_count, fill_value=0)

# 전체 시간 동안 가장 많이 자전거를 대여한 성별 출력
overall_most_rented_gender = total_gender_rent_count.idxmax()
overall_most_rented_gender_count = int(total_gender_rent_count.max())
print(f"\n2023년 2분기 시간별 가장 많이 자전거를 대여한 성별은 {overall_most_rented_gender} ({overall_most_rented_gender_count}명)")

# 전체 대여수 차이 및 비율 계산
total_male_rent_count = int(total_gender_rent_count.get('남자', 0))  # 남자 대여 건수 (소수점 제거)
total_female_rent_count = int(total_gender_rent_count.get('여자', 0))  # 여자 대여 건수 (소수점 제거)
difference = total_male_rent_count - total_female_rent_count  # 남자와 여자의 차이
percentage_difference = (difference / total_female_rent_count) * 100 if total_female_rent_count > 0 else None  # 차이를 비율로 환산

# 출력
print(f"\n2023.07.01 ~ 2023.12.31 전체 시간 동안 가장 많이 자전거를 대여한 성별은 {overall_most_rented_gender} ({overall_most_rented_gender_count}명)")
print(f"\n2023.07.01 ~ 2023.12.31 전체 기간 동안 총 남자 대여 건수: {total_male_rent_count}명")
print(f"2023.07.01 ~ 2023.12.31 전체 기간 동안 총 여자 대여 건수: {total_female_rent_count}명")


if total_female_rent_count > 0:
    print(f"남자가 여자보다 총 {difference}건 더 많이 대여, 남자가 여자보다 {percentage_difference:.2f}% 더 많이 대여.")
else:
    print("여자의 대여 건수가 0이어서 비교할 수 없습니다.")
# 총 데이터 수 계산
total_count = len(df)
print(f"\n23-2분기성별 총 데이터수: {total_count}개")