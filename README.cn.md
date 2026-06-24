# PyAirLink
PyAirLink 是一个通过web来管理2G/3G/4G/5G模块的工具，可以用来替代你那台只用于接收短信的备用机

## 硬件要求
1. 模块必须支持UART传递AT信令，请注意接口可以是物理上的TTL接口，也可以是逻辑上的(例如通过USB接口、网口、TCPServer等)
2. 有自己的一台服务器(系统不限，但只在Linux下测试过)，能以任意一种方式与模块用UART标准连接。
3. 如果模块插入USB后不显示TTL接口，参考以下操作
```shell
# 添加ID，使得接口显示出来，注意，USB的ID以实际为准(1286 4e3d)，可以用lsusb命令获取
sudo modprobe option
sudo sh -c 'echo 1286 4e3d > /sys/bus/usb-serial/drivers/option1/new_id'
# 可能会出现几个tty(ACM|USB)，可以通过minicom测试串口：
sudo minicom -D /dev/ttyACM0
```

## 功能
1. web api
2. 短信自动转发
   - 邮件
   - Bark
   - server酱
   - 企业微信
3. 定时/手动重启
4. 定时/手动发送短信
5. 执行自定义AT信令

## 前情提要

感谢 [sms_forwarder_air780_esp32](https://github.com/boris1993/sms_forwarder_air780_esp32) 这个项目的启发。他是通过编写固件的形式实现相关功能。两边对比如下：

PyAirLink的优点
- 不需要额外的ESP32硬件，相关功能转移到了你自己的NAS/软路由
- 是否支持电信网络仅取决于你买什么模块
- 对硬件无要求，硬件投入较低。例如我用的是这个(AT固件版本) ![img.jpg](doc/Air780E.jpg)
- 模块和服务器并不需要物理上在同一个地方，有两种方法
  - DTU固件的模块，配置两边通过厂家或者你自己的云平台来交互(使用sim卡的流量)
  - 模块加上一个TTL转网络的转换器
- 不需要焊接等硬件操作，也不需要学习刷写固件

PyAirLink的缺点

- 需要有台服务器，功耗毫无优势
- 模块不能随身带。有这个需求，为什么不用5ber之类的方案？

## 使用
1. 先找出/定义接口路径，Linux一般是/dev/tty(ACM|USB)+数字，Windows一般是COM+数字
2. 确认波特率
3. 确认模块已启动
### source code
```shell
git clone https://github.com/zsy5172/PyAirLink.git
cd PyAirLink
pip install -r requiremenets.txt
cp config.ini.template data/config.ini
# 将config.ini内容根据你的实际情况修改
python main.py
```

### container

```shell
docker run -d -p 10103:10103 -v /PyAirLink/data:/PyAirLink/data --device=/dev/ttyACM0 --name PyAirLink --restart always ghcr.io/zsy5172/pyairlink:master
```
记得启动前先根据实际情况修改你的路径映射，然后将config.ini.template的内容复制到/PyAirLink/data/config.ini内并调整配置

现在你可以通过访问 [http://localhost:10103/docs#/](http://localhost:10103/docs#/) 来操作模块了。
