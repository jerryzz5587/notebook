import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Set font for displaying Korean characters
plt.rcParams['font.family'] = 'Malgun Gothic'

# Data for plotting
gender = ['남자', '여자']
rental_count = [17041491, 11372248]
avg_distance = [2.93, 2.95]
avg_time = [24.47, 22.56]

# Creating figure for rental count
fig, ax1 = plt.subplots()
bars = ax1.bar(gender, rental_count, color=['skyblue', 'lightcoral'], alpha=0.7)
ax1.set_xlabel('성별')
ax1.set_ylabel('대여건수 (건)', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_title('성별 대여건수')

# Adding text labels on top of bars for rental count
for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 50000, f'{yval:,}', ha='center', va='bottom', fontsize=10, color='black')

plt.show()

# Creating figure for average distance per rental
fig, ax2 = plt.subplots()
bars_distance = ax2.bar(gender, avg_distance, color=['skyblue', 'lightcoral'], alpha=0.7)
ax2.set_xlabel('성별')
ax2.set_ylabel('평균 이동거리 (km)', color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_title('성별 대여 1건당 평균 이동거리')

# Adding text labels on top of bars for average distance
for bar in bars_distance:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 50, f'{yval:.2f}', ha='center', va='bottom', fontsize=10, color='black')

plt.show()

# Creating figure for average time per rental
fig, ax3 = plt.subplots()
bars_time = ax3.bar(gender, avg_time, color=['skyblue', 'lightcoral'], alpha=0.7)
ax3.set_xlabel('성별')
ax3.set_ylabel('평균 이용시간 (분)', color='black')
ax3.tick_params(axis='y', labelcolor='black')
ax3.set_title('성별 대여 1건당 평균 이용시간')

# Adding text labels on top of bars for average time
for bar in bars_time:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 50, f'{yval:.2f}', ha='center', va='bottom', fontsize=10, color='black')

plt.show()





