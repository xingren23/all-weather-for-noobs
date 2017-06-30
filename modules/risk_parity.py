# _*_ coding:utf8 _*_
# !/usr/bin/env python
import pandas as pd
import numpy as np
from scipy.optimize import minimize

 # 风险预算优化
def calculate_portfolio_var(w,V):
    # 计算组合风险的函数
    w = np.matrix(w)
    return (w*V*w.T)[0,0]

def calculate_risk_contribution(w,V):
    # 计算单个资产对总体风险贡献度的函数
    w = np.matrix(w)
    sigma = np.sqrt(calculate_portfolio_var(w,V))
    # 边际风险贡献
    MRC = V*w.T
    # 风险贡献
    RC = np.multiply(MRC,w.T)/sigma
    return RC

def risk_budget_objective(x,pars):
    # 计算组合风险
    V = pars[0]# 协方差矩阵
    x_t = pars[1] # 组合中资产预期风险贡献度的目标向量
    sig_p =  np.sqrt(calculate_portfolio_var(x,V)) # portfolio sigma
    risk_target = np.asmatrix(np.multiply(sig_p,x_t))
    asset_RC = calculate_risk_contribution(x,V)
    J = sum(np.square(asset_RC-risk_target.T))[0,0] # sum of squared error
    return J

def total_weight_constraint(x):
    return np.sum(x)-1.0

def long_only_constraint(x):
    return x

def calcu_w(x, V):
    """
    # 根据资产预期目标风险贡献度来计算各资产的权重
    :param x: 风险贡献度向量 map
    :param V: 资产的协方差矩阵
    :return:
    """
    w0 = [1.0/len(x) for i in x]
    x_t = x.values()
    print x_t, w0
    print V
    cons = ({'type': 'eq', 'fun': total_weight_constraint}, {'type': 'ineq', 'fun': long_only_constraint})
    res= minimize(risk_budget_objective, w0, args=[V,x_t], method='SLSQP',constraints=cons, options={'disp': True})
    weights = {}
    for i, item in enumerate(x):
        weights[item] = res.x[i]
    return weights


if __name__ == "__main__":
    # risk weight to value weight
    tickers = ['SPY', 'QQQ', 'EWJ', 'FXI', 'DBC', 'LQD', 'EMB', 'TLT', 'IEF', 'GLD']
    data_pd = pd.DataFrame()
    x = {}
    for ticker in tickers:
        data = pd.read_csv('output/%s.csv' % ticker, index_col='date')
        data_pd[ticker] = data['Returns']
        x[ticker] = 1.0 / len(tickers)

    data_pd = data_pd.dropna()
    V = np.matrix(data_pd.corr(min_periods=255*2))
    weights = calcu_w(x, V)
    print weights
