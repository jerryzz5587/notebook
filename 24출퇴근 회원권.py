import pandas as pd 
import glob

pd.set_option('display.float_format', '{:.0f}'.format)

# 파일 경로 설정 및 여러 CSV 파일 합치기 (24년 1월 ~ 5월)
file_paths_main = glob.glob("C:/Mtest/pj/2401~05/*.csv")
file_station_info = "C:/Mtest/pj/대여소/서울특별시 공공자전거 대여소별 이용정보(월별)_24.1-6.csv"

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

# 회원권 데이터 필터링 (일일권, 정기권, 일일권(비회원))
pass_types = ['일일권', '정기권', '일일권(비회원)']
commute_df = commute_df[commute_df['대여구분코드'].isin(pass_types)]

# 각 시간대별 회원권 대여건수, 이동거리, 이용시간 계산
for hour in commute_hours:
    hourly_data = commute_df[commute_df['대여시간'] == hour]
    pass_type_group_stats = hourly_data.groupby('대여구분코드').agg(
        대여건수=('대여소명', 'size'),
        총이동거리=('이동거리(M)', 'sum'),
        총이용시간=('이용시간(분)', 'sum')
    )
    pass_type_group_stats['총이동거리(km)'] = pass_type_group_stats['총이동거리'] / 1000  # 이동거리(M)를 km로 변환

    # 가장 많이 대여한 회원권, 이동거리가 가장 긴 회원권, 이용시간이 가장 긴 회원권 찾기
    most_rented_pass_type = pass_type_group_stats['대여건수'].idxmax()
    most_distance_pass_type = pass_type_group_stats['총이동거리(km)'].idxmax()
    longest_time_pass_type = pass_type_group_stats['총이용시간'].idxmax()

    print(f"\n시간: {hour}시 회원권별 대여 통계:")
    print(pass_type_group_stats[['대여건수', '총이동거리(km)', '총이용시간']])
    print(f"가장 많이 대여한 회원권: {most_rented_pass_type}")
    print(f"이동거리가 가장 많은 회원권: {most_distance_pass_type}")
    print(f"이용시간이 가장 긴 회원권: {longest_time_pass_type}")

# 출퇴근 시간 전체 통계 계산
total_pass_type_group_stats = commute_df.groupby('대여구분코드').agg(
    대여건수=('대여소명', 'size'),
    총이동거리=('이동거리(M)', 'sum'),
    총이용시간=('이용시간(분)', 'sum')
)
total_pass_type_group_stats['총이동거리(km)'] = total_pass_type_group_stats['총이동거리'] / 1000  # 이동거리(M)를 km로 변환

# 대여 1건당 평균 이동거리 및 평균 이용시간 계산
total_pass_type_group_stats['대여건당평균이동거리(km)'] = total_pass_type_group_stats['총이동거리(km)'] / total_pass_type_group_stats['대여건수']
total_pass_type_group_stats['대여건당평균이용시간(분)'] = total_pass_type_group_stats['총이용시간'] / total_pass_type_group_stats['대여건수']

# 출퇴근 시간대 전체에서 가장 많이 대여한 회원권, 이동거리가 가장 긴 회원권, 이용시간이 가장 긴 회원권 찾기
total_most_rented_pass_type = total_pass_type_group_stats['대여건수'].idxmax()
total_distance_pass_type = total_pass_type_group_stats['총이동거리(km)'].idxmax()
total_time_pass_type = total_pass_type_group_stats['총이용시간'].idxmax()

# 평균과 비교 계산
total_average_rent_count = total_pass_type_group_stats['대여건수'].mean()
total_rent_percentage_above_avg = ((total_pass_type_group_stats.loc[total_most_rented_pass_type, '대여건수'] - total_average_rent_count) / total_average_rent_count) * 100

# 전체 출퇴근 시간대 통계 출력
print("\n출퇴근 시간대 전체 회원권별 대여 통계:")
print(total_pass_type_group_stats[['대여건수', '총이동거리(km)', '총이용시간', '대여건당평균이동거리(km)', '대여건당평균이용시간(분)']])
print(f"\n가장 많이 대여한 회원권: {total_most_rented_pass_type} ({total_pass_type_group_stats.loc[total_most_rented_pass_type, '대여건수']}건), 다른 회원권 평균보다 {total_rent_percentage_above_avg:.2f}% 높음")
print(f"이동거리가 가장 긴 회원권: {total_distance_pass_type} (대여 1건당 평균 이동거리: {total_pass_type_group_stats.loc[total_distance_pass_type, '대여건당평균이동거리(km)']:.2f} km)")
print(f"이용시간이 가장 긴 회원권: {total_time_pass_type} (1인당 평균 이용시간: {total_pass_type_group_stats.loc[total_time_pass_type, '대여건당평균이용시간(분)']:.2f}분)")