import matplotlib.pyplot as plt
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'

# 데이터 설정
categories = ['20대', '30대', '40대', '50대']
counts = [666.6964, 326.3834, 300.1516, 297.5685]  # 대여건수를 '만' 단위로 변경

# 그래프 설정
x = np.arange(len(categories))
width = 0.5  # 막대 너비

fig, ax = plt.subplots()
rects = ax.bar(x, counts, width, color='skyblue', label='대여건수')

# 막대 위에 값 표시
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.2f}만',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 약간의 여백
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects)

# 그래프 제목과 라벨 설정
ax.set_ylabel('대여건수 (단위: 만)')
ax.set_title('출퇴근 시간대 연령대별 대여건수')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()

# 그래프 출력
plt.show()

# 이동거리 그래프
avg_distances = [1801.4776, 1911.4776, 1500.0000, 1600.0000]  # 이동거리 데이터를 '천 km' 단위로 변경
fig, ax = plt.subplots()
rects = ax.bar(x, avg_distances, width, color='lightgreen', label='이동거리')

autolabel(rects)

ax.set_ylabel('평균 이동거리 (단위: 천 km)')
ax.set_title('출퇴근 시간대 연령대별 평균 이동거리')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()

plt.show()

# 이용시간 그래프
total_times = [2529.8094, 1500.0000, 1300.0000, 1200.0000]  # 이용시간 데이터를 '천 시간' 단위로 변경
fig, ax = plt.subplots()
rects = ax.bar(x, total_times, width, color='coral', label='이용시간')

autolabel(rects)

ax.set_ylabel('총 이용시간 (단위: 천 시간)')
ax.set_title('출퇴근 시간대 연령대별 총 이용시간')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()

plt.show()



