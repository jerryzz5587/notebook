import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 준비
data = [
    {"시간": 7, "자치구": "강서구", "대여소": "2701. 마곡나루역 5번출구 뒤편", "대여건수": 7960, "평균이용시간(분)": 13.65, "평균이동거리(km)": 2.06},
    {"시간": 8, "자치구": "강서구", "대여소": "2701. 마곡나루역 5번출구 뒤편", "대여건수": 11525, "평균이용시간(분)": 27.30, "평균이동거리(km)": 4.17},
    {"시간": 9, "자치구": "강서구", "대여소": "2715.마곡나루역 2번 출구", "대여건수": 7835, "평균이용시간(분)": 13.77, "평균이동거리(km)": 1.85},
    {"시간": 17, "자치구": "강서구", "대여소": "2715.마곡나루역 2번 출구", "대여건수": 12575, "평균이용시간(분)": 28.00, "평균이동거리(km)": 3.30},
    {"시간": 18, "자치구": "강서구", "대여소": "2715.마곡나루역 2번 출구", "대여건수": 14375, "평균이용시간(분)": 36.07, "평균이동거리(km)": 4.34},
    {"시간": 19, "자치구": "강서구", "대여소": "2715.마곡나루역 2번 출구", "대여건수": 11175, "평균이용시간(분)": 27.16, "평균이동거리(km)": 3.15},
]

# 데이터프레임으로 변환
graph_df = pd.DataFrame(data)

# 출퇴근 시간대 (7, 8, 9시 / 17, 18, 19시) 대여건수 시각화
commute_df = graph_df[graph_df['시간'].isin([7, 8, 9, 17, 18, 19])]

# 대여건수 시각화
plt.figure(figsize=(10, 6))
plt.bar(commute_df['시간'].astype(str), commute_df['대여건수'], color='skyblue')
plt.title('출퇴근 시간대 (7, 8, 9시 / 17, 18, 19시) 대여건수', fontsize=15)
plt.ylabel('대여건수', fontsize=12)
plt.xlabel('시간', fontsize=12)
plt.xticks(commute_df['시간'].astype(str))
plt.tight_layout()
plt.show()

# 평균 이동거리 시각화
plt.figure(figsize=(10, 6))
plt.bar(commute_df['시간'].astype(str), commute_df['평균이동거리(km)'], color='lightgreen')
plt.title('출퇴근 시간대 전체(7, 8, 9시 / 17, 18, 19시) 대여 1건당 평균 이동거리', fontsize=15)
plt.ylabel('평균 이동거리 (km)', fontsize=12)
plt.xlabel('시간', fontsize=12)
plt.xticks(commute_df['시간'].astype(str))
plt.tight_layout()
plt.show()

# 평균 이용시간 시각화
plt.figure(figsize=(10, 6))
plt.bar(commute_df['시간'].astype(str), commute_df['평균이용시간(분)'], color='lightcoral')
plt.title('출퇴근 시간대 전체(7, 8, 9시 / 17, 18, 19시) 대여 1건당평균 이용시간', fontsize=15)
plt.ylabel('평균 이용시간 (분)', fontsize=12)
plt.xlabel('시간', fontsize=12)
plt.xticks(commute_df['시간'].astype(str))
plt.tight_layout()
plt.show()






