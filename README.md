# 介绍

## 背景

目前，Web 自动化测试基本上是以 Selenium 为接口来编写测试代码，但效果往往不是很好，普遍遇到如下问题：
1. 用例设计人员的编码能力很弱，测试代码编写和维护成本高，效果差；
2. 测试代码量大，测试意图不直观，无法支撑千、万级别的用例规模；
3. Web 页面元素的定位非常繁琐，且页面结构经常变动，导致用例失效。

我们知道，传统的测试用例一般是在 Excel 中用文本编写的，如果自动化测试用例也这么写，是不是就可以解决问题1和2？
对于问题3，我想是时候对开发提出一些要求了，同时我们的元素定位也要优化，让页面自由的去变化，而我们的定位只做最小适用。

## 实现思路

1. Selenium 为底层接口；
2. 在 Excel 中用文本编写测试用例；
3. 元素定位表格化，且优先使用“板块通用定位法”；
4. 要求开发提供必要的、统一的元素属性；
5. 框架负责解析测试用例，执行用例，记录日志，输出测试结果。

## 方案

1. 开发语言：Python
2. 底层接口：Selenium
3. 用例工具：Excel

测试用例如下图：
![testcase](https://github.com/tonglei100/sweetest/blob/master/testcase.png)


# 安装

## 环境要求

- 系统要求：Windows
- Python 版本：3.6+
- Selenium
- 浏览器：Chrome
- Chrome 驱动: chromedriver

## 安装 sweetest
> pip install sweetest

## 快速体验
打开 cmd 命令窗口，切换到某个目录，如：D:\Autotest

> sweetest
  cd sweetest_sample
  python start.py

![install](https://github.com/tonglei100/sweetest/blob/master/install.png)

OK，如果一切顺利的话，sweetest 已经跑起来了

## 目录结构
![dir](https://github.com/tonglei100/sweetest/blob/master/dir.png)

