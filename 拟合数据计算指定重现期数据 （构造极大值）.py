import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import genextreme
import matplotlib as mpl

# 设置Matplotlib的字体为SimHei
mpl.rcParams['font.sans-serif'] = 'SimHei'

# 解决负号'-'显示为方块的问题
mpl.rcParams['axes.unicode_minus'] = False


# 读取CSV文件
data = pd.read_csv('D:/path/2000年1月1日～2019年12月31日中国各区县降水量日度数据.csv')

# 输入县区代码、省代码或市代码
code = input("请输入县区代码、省代码或市代码：")

# 输入月份范围
month_range = input("请输入月份范围，例如7-9或1-5,9-12：")

# 解析月份范围
months = []
for part in month_range.split(','):
    if '-' in part:
        start, end = map(int, part.split('-'))
        months.extend(range(start, end + 1))
    else:
        months.append(int(part))

# 筛选数据
filtered_data = data[(data['县代码'] == int(code)) |
                     (data['省代码'] == int(code)) |
                     (data['市代码'] == int(code))].copy()

filtered_data['日期'] = pd.to_datetime(filtered_data['日期'])  # 转换日期列为日期类型

filtered_data = filtered_data[filtered_data['日期'].dt.month.isin(months)]

if len(filtered_data) == 0:
    print("筛选后的数据为空。请确保输入的代码和月份范围正确，并在数据集中存在匹配的记录。")
else:
    # 根据日期排序数据
    sorted_data = filtered_data.sort_values('日期')

    # 将NaN值替换为零
    sorted_data['降水量'] = sorted_data['降水量'].fillna(0)

    # 计算每三天的降雨总量
    sorted_data['三日降雨量'] = sorted_data['降水量'].rolling(window=3, min_periods=1).sum()

    # 按年份分组并计算每年的最大三日降水量
    yearly_max = sorted_data.groupby(sorted_data['日期'].dt.year)['三日降雨量'].max()

    # 转换单位为mm
    yearly_max = yearly_max * 0.1

    # 构造极端最大降水量
    pmp = yearly_max.max() * 3

    # 构造降水等差序列
    pseq = np.arange(np.ceil(pmp / 10) * 10, np.floor(yearly_max.max() / 10) * 10, -10)

    # 将降水等差序列排序
    seq = np.arange(1, len(pseq) + 1)

    # 拟合P-III型曲线
    params = genextreme.fit(yearly_max)
    xbar, cv, cs = genextreme.stats(*params, moments='mvs')

    # 生成P-III型频率曲线
    x = np.linspace(pseq.min(), pseq.max(), 100)
    y = genextreme.pdf(x, *params)

    # 绘制P-III型频率曲线
    plt.plot(x, y)
    plt.xlabel('年度最大三日降水量 (mm)')
    plt.ylabel('概率密度')
    plt.title('P-III型频率曲线')
    plt.grid(True)
    plt.show()

    # 输入重现期
    return_period = float(input("请输入重现期："))

    # 计算重现期下的最大三日降雨量
    design_value = genextreme.ppf(1 - 1 / return_period, *params)

    # 输出结果
    print("最大三日降雨量:", design_value, "mm")

    # 按年份输出每年的最大三日降水量到Excel文件
    yearly_max_df = yearly_max.reset_index()
    yearly_max_df.columns = ['年份', '最大三日降水量 (mm)']
    yearly_max_df.to_excel('年度最大三日降水量.xlsx', index=False)

    # 计算水文学中常见的参数
    x = genextreme.ppf(1 - 1 / return_period, *params)  # x拔
    Cv = np.sqrt((np.exp(params[0] * (1 - 2 / return_period)) - 1) * np.exp(params[0]) / (np.exp(params[0]) - 1))  # 变差系数
    Cs = (np.exp(params[0]) - 1) / (np.exp(params[0]) + 1)  # 偏斜系数

    # 输出参数数值
    print("x拔:", x)
    print("变差系数Cv:", Cv)
    print("偏斜系数Cs:", Cs)
