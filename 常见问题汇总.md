# Sweetest 常见问题汇总(持续更新...)


## 安装配置


### 1.  是否支持 Python2.7？

答：不支持。

Sweetest 仅支持 Python3.6 或以上，原因如下：

1) 框架中使用了有序字典等特性；
2) 人生苦短，我用新版 :)


### 2.  安装后，无法正常启动浏览器？

答：请检查是否正确配置了 chromedriver：

要求和 Chrome 版本匹配；并且把路径添加到环境变量的 path 中。


### 3.  直接从 github 上下载源码能跑起来吗？

答：不能。

因为没有安装依赖库；建议使用 pip 安装，pip 会自动把依赖库也一起安装。


### 4.  是否支持 Mac、Linux？

答：支持。

但是无法使用 sweetest 来创建示例文件夹，需要自行下载示例并解压；

下载地址：<https://github.com/tonglei100/sweetest/tree/master/example>

另外，Mac 或 Linux 上的 chromedriver 在功能和稳定性上**可能**存在问题，建议还是在 Windows 上运行比较可靠。


## 支持范围


### 1.  除了 Chrome，是否支持 IE, Firefox, Safari 等浏览器？

答：支持。

Sweetest 底层是 Selenium 接口，按如下操作即可：

1) 配置好对应的浏览器驱动;
2) 在启动脚本里配置对应浏览器，如下：

```
desired_caps = {'platformName': 'Desktop', 'browserName': 'Ie'}
```


### 2.  支持 Android App 测试吗？

答：支持。

Sweetest 在移动端测试上底层使用的是 Appium，需要配置好 Appium 环境；

目前，已经在 OPPO R9s 上测试通过。


### 3.  支持 iOS App 测试吗？

答：不支持。

虽然底层的 Appium 支持 iOS，但是经过我们在 iPhone 6p 上测试，响应速度非常慢，经常卡死；

后续，我们会考虑使用其他框架作为底层来支持 iOS 测试，如 ATX。


### 4.  支持小程序测试吗？

答：支持 Android 上的小程序测试。

我们的在示例中有测试音乐台小程序的用例。


### 5.  支持 http 接口测试吗？

答：支持。

详情见示例中的用例。


### 6.  支持数据库操作吗？

答：支持。

详情见示例中的用例。


## 使用及功能

### 1. 我写了一个 setup 用例，为什么没有执行？

答：setup 是在普通用例之前执行的，如果没有普通用例就不会执行。
