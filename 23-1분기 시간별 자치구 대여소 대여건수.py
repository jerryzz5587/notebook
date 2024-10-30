import pandas as pd 
import glob

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

# 모든 시간 통틀어 가장 대여가 많이 발생한 대여소 ###
total_station_rent_count = df.groupby(['자치구', '대여소명']).size()
most_rented_station_overall = total_station_rent_count.idxmax()
most_rented_station_count_overall = total_station_rent_count.max()

# 대여소별 대여수 평균 계산
average_station_rent_count = total_station_rent_count.mean()

# 가장 많이 대여된 대여소의 대여수가 평균보다 몇 건 더 많은지 계산
difference_in_rent_count = most_rented_station_count_overall - average_station_rent_count

# 가장 적게 대여된 대여소 계산
total_station_rent_count = df.groupby(['자치구', '대여소명']).size()
least_rented_station_overall = total_station_rent_count.idxmin()
least_rented_station_count_overall = total_station_rent_count.min()

# 가장 많이 대여된 대여소의 대여수가 평균보다 몇 % 높은지 계산
percentage_above_average_station = ((most_rented_station_count_overall - average_station_rent_count) / average_station_rent_count) * 100

# 가장 적게 대여된 대여소의 대여수가 평균보다 몇 % 낮은지 계산
percentage_below_average_station = ((average_station_rent_count - least_rented_station_count_overall) / average_station_rent_count) * 100

# 가장 적게 대여된 대여소의 대여수가 평균보다 몇 건 더 적은지 계산
difference_in_least_rent_count = average_station_rent_count - least_rented_station_count_overall

# 자치구별 대여소 개수 계산
station_count_per_gu = df.groupby('자치구')['대여소명'].nunique()
total_station_count = station_count_per_gu.sum()

# 자치구별 대여 건수 계산
total_rent_count_per_gu = df.groupby('자치구').size()
most_rented_gu = total_rent_count_per_gu.idxmax()
most_rented_gu_count = total_rent_count_per_gu.max()
least_rented_gu = total_rent_count_per_gu.idxmin()
least_rented_gu_count = total_rent_count_per_gu.min()

# 자치구별 평균 대여 건수 계산
average_rent_count_per_gu = total_rent_count_per_gu.mean()

# 출력
print(f"\n모든 시간 통틀어 가장 대여가 많이 발생한 대여소: {most_rented_station_overall[0]} {most_rented_station_overall[1]}에서 {most_rented_station_count_overall}건")
print(f"가장 많이 대여된 대여소의 대여수가 다른 대여소 평균 대여수보다 {difference_in_rent_count:.0f}건 더 많음.")
print(f"가장 많이 대여된 대여소의 대여수가 평균 대여수보다 {percentage_above_average_station:.2f}% 높음.")

print(f"\n모든 시간 통틀어 가장 대여가 적게 발생한 대여소: {least_rented_station_overall[0]} {least_rented_station_overall[1]}에서 {least_rented_station_count_overall}건")
print(f"가장 적게 대여된 대여소의 대여수가 평균 대여수보다 {percentage_below_average_station:.2f}% 낮음.")
print(f"가장 적게 대여된 대여소의 대여수가 다른 대여소 평균 대여수보다 {difference_in_least_rent_count:.0f}건 더 적음.")

print(f"서울 자치구 내 총 대여소 개수: {total_station_count}개")

for gu, count in station_count_per_gu.items():
    print(f"{gu} 대여소: {count}개")

print(f"\n모든 시간 통틀어 가장 대여가 많이 발생한 자치구: {most_rented_gu} ({most_rented_gu_count}건)")
print(f"모든 시간 통틀어 가장 대여가 적게 발생한 자치구: {least_rented_gu} ({least_rented_gu_count}건)")
print(f"서울 자치구 평균 대여 건수: {average_rent_count_per_gu:.2f}건")

for gu, count in total_rent_count_per_gu.items():
    print(f"{gu} 총 대여 건수: {count}건")
total_count = len(df)
print(f"23-1분기대여소 총 데이터수: {total_count}개")

