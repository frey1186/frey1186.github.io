#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 19:53:28 2017

@author: felo

实现了一下使用knn实现手写数字识别的过程。
"""

from __future__ import division
import numpy as np
import os
from scipy.stats import mode
from pandas import Series,DataFrame


# 读取单个文件，并形成一个列表
def read_txt(file_name):
    ret = []
    with file(file_name) as f:
        for line in range(32):
            ret += f.readline()[:32]
    return ret





# 读取真个目录中的所有文件，并形成一个array，和一个标签列表label
def get_trainingData(dir_path):
    ret_array = []
    labelData = []
    file_name_list = os.listdir(dir_path)
    for file_name in file_name_list:
        ret = read_txt(dir_path+'/'+file_name)
        ret_array.append(ret)
        labelData.append(file_name[0])
    trainingData = np.array(ret_array)
    labelData = np.array(labelData)
    trainingData =trainingData.astype('f2')
    labelData = labelData.astype('f2')
    return trainingData,labelData





# print(trainingData,labelData)



# knn 算法
# k：表示k值
# trainingData，label：表示训练集和标签
# data：表示输入值，列表
def knn(k, trainingData, labelData, data):
    data1 = np.zeros_like(trainingData)
    for i in range(trainingData.shape[0]):
        data1[i] = data

    data_sum = ((trainingData - data1)**2).sum(axis=1)  # 求欧式距离
    d = np.sqrt(data_sum)
    #k_list = np.sort(np.where(d>np.sort(d)[:k][0],0,1) * labelData)[-k:]
    index_list = (np.where(d>np.sort(d)[k-1],0,1))  # 将距离排序，取前k个，
    s1 = Series(labelData, index=index_list) # 前k个索引为1，其他为0
    ret = mode(s1[1]).mode
    return ret[0]



if __name__ == '__main__':
    dir_path = '/Users/felo/Desktop/machinelearninginaction/Ch02/digits/trainingDigits'
    test_dir_path = '/Users/felo/Desktop/machinelearninginaction/Ch02/digits/testDigits'
    trainingData,labelData = get_trainingData(dir_path)
    testData,testLabel = get_trainingData(test_dir_path)
    k =3  # 这里取k为3
    wrong_count = 0
    for i,data in enumerate(testData):
        ret = knn(k, trainingData, labelData, data)
        #print('knn number is :%s ,the real number  is : %s.'%(ret, testLabel[i]))
        print '#',
        if ret != testLabel[i]:
            wrong_count +=1
    wrong_percent = wrong_count*100/len(testLabel)
    print("wrong count:%s,wrong percnet:%.2f" %(wrong_count, wrong_percent))
