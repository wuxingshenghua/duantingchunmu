import pandas as pd
import math as mt
import numpy as np

ws = pd.read_excel('D:/dracd/验证数据.xlsx')
pdata = ws.iloc[:, 1]  # 导入降水系列数据

# 计算样本统计参数
mean = np.mean(pdata)  # 降水系列的均值
std = np.std(pdata)  # 降水系列的标准偏差
Cs = pdata.skew()  # 降水系列的偏态系数
Cv = std / mean  # 降水系列的变差系数
max = max(pdata)  # 最大值
min = min(pdata)  # 最小值

# 计算P3分布统计参数
alpha = 4 / Cs ** 2  # 参数alpha
beta = 2 / (mean * Cs * Cv)  # 参数beta
x0 = mean * (1 - 2 * Cv / Cs)  # 参数x0

pmp = max + 3 * std  # 构造极端最大降水量
pseq = [i for i in range(mt.ceil(pmp / 10) * 10, mt.floor(x0 / 10) * 10, -10)]  # 构造降水等差序列
seq = [i for i in range(1, len(pseq) + 1)]  # 将降水等差序列排序

quantiles = []  # 计算p3分布各分位点的概率密度函数值
for i in range(len(pseq)):
    quantile = beta ** alpha / mt.gamma(alpha) * (pseq[i] - x0) ** (alpha - 1) * mt.exp(-(pseq[i] - x0) * beta)
    quantiles.append(quantile)

probabilities = []  # 计算各分位点之间的区间概率
probabilities.append(0)
for i in range(1, len(quantiles)):
    probability = (quantiles[i - 1] + quantiles[i]) * (pseq[i - 1] - pseq[i]) / 2
    probabilities.append(probability)

accum_probblts = []  # 计算累计概率
for i in range(len(probabilities)):
    accum_probblts.append(sum(probabilities[:i + 1]))


def Linterpo(x, y, xi):
    if xi < x[0]:
        yi = y[0] + (xi - x[0]) / (x[0] - x[1]) * (y[0] - y[1])
    if xi > x[-1]:
        yi = y[-1] + (xi - x[-1]) / (x[-1] - x[-2]) * (y[-1] - y[-2])
    else:
        for j in range(len(x)):
            if xi >= x[j] and xi < x[j + 1]:
                yi = y[j] + (xi - x[j]) / (x[j + 1] - x[j]) * (y[j + 1] - y[j])
    return yi


p = [1 / 10000, 1 / 1000, 1 / 100, 1 / 50, 1 / 30, 1 / 20, 1 / 10, 1 / 5]  # 设计频率
for i in range(len(p)):
    pp = round(Linterpo(accum_probblts, pseq, p[i]), 1)
    print(str(round(p[i] * 100, 1)) + '%设计频率的年降水量是' + str(pp) + 'mm')