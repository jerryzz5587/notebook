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

# 출퇴근 시간대 데이터 필터링 (오전 7, 8, 9시 / 오후 5, 6, 7시)
commute_hours = [7, 8, 9, 17, 18, 19]
commute_df = df[df['대여시간'].isin(commute_hours)]

# 출퇴근 시간대별 대여소별 대여건수, 평균 이용시간, 평균 이동거리 계산
result = []
for hour in commute_hours:
    hourly_data = commute_df[commute_df['대여시간'] == hour]
    top_3_stations = hourly_data.groupby(['자치구', '대여소명']).size().nlargest(3)
    for (gu, station), count in top_3_stations.items():
        avg_time = hourly_data[(hourly_data['자치구'] == gu) & (hourly_data['대여소명'] == station)]['이용시간(분)'].mean()
        avg_distance = hourly_data[(hourly_data['자치구'] == gu) & (hourly_data['대여소명'] == station)]['이동거리(M)'].mean() / 1000  # 이동거리(M)를 km로 변환
        result.append((hour, gu, station, count, avg_time, avg_distance))

# 출퇴근 시간대 전체 통계 계산
total_commute_rent_count = commute_df.shape[0]
total_avg_time = commute_df['이용시간(분)'].mean()  # 평균 이용시간을 분으로 계산
total_avg_distance = commute_df['이동거리(M)'].mean() / 1000  # 평균 이동거리(KM) 계산

# 출근 시간대 대여건수 계산 (오전 7, 8, 9시)
morning_hours = [7, 8, 9]
morning_df = df[df['대여시간'].isin(morning_hours)]
total_morning_rent_count = morning_df.shape[0]

# 퇴근 시간대 대여건수 계산 (오후 5, 6, 7시)
evening_hours = [17, 18, 19]
evening_df = df[df['대여시간'].isin(evening_hours)]
total_evening_rent_count = evening_df.shape[0]

# 출근 시간대와 퇴근 시간대 대여건수 비교
rent_difference = total_morning_rent_count - total_evening_rent_count
percentage_difference = (rent_difference / total_evening_rent_count) * 100 if total_evening_rent_count > 0 else None

# 출퇴근 시간대 가장 많은 대여가 발생한 자치구 계산
most_rented_gu_commute = commute_df['자치구'].value_counts().idxmax()
most_rented_gu_commute_count = commute_df['자치구'].value_counts().max()

# 결과 출력
print("\n23년 1분기 출퇴근 시간대별 상위 3개 대여소 (이용건수, 평균 이용시간(분), 평균 이동거리):")
for hour, gu, station, count, avg_time, avg_distance in result:
    print(f"시간: {hour}시, 자치구: {gu}, 대여소: {station}, 대여건수: {count}건, 평균 이용시간: {avg_time:.2f}분, 평균 이동거리: {avg_distance:.2f}km")

# 출퇴근 시간 전체 통계 출력
print(f"\n출퇴근시간 전체 자전거 대여건수: {total_commute_rent_count}건")
print(f"출퇴근 시간 평균 이용시간: {total_avg_time:.2f}분")
print(f"출퇴근시간 평균 이동거리: {total_avg_distance:.2f}km")

# 출근 및 퇴근 시간대 대여건수 비교 출력
print(f"\n출근시간 (7, 8, 9시) 대여건수 총: {total_morning_rent_count}건")
print(f"퇴근시간 (17, 18, 19시) 대여건수 총: {total_evening_rent_count}건")
if rent_difference > 0:
    print(f"출근시간이 퇴근시간보다 {rent_difference}건 대여수가 더 많으며 {percentage_difference:.2f}% 더 많이 대여가 발생")
else:
    print(f"퇴근시간이 출근시간보다 {-rent_difference}건 대여수가 더 많으며 {abs(percentage_difference):.2f}% 더 많이 대여가 발생")

# 출퇴근 시간대 가장 많은 대여가 발생한 자치구 출력
print(f"\n출퇴근 시간대 가장 많은 대여가 발생한 자치구: {most_rented_gu_commute} ({most_rented_gu_commute_count}건)")






