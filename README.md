记录
=====
概述
--
由于时间紧，可能大多数接口废着，还没完善  
此版本是version3  
version1基本是嗯抄pymycqu，抄完爆红数目极多  
version2是在vsc把抄下来的代码试着缕清过程，然后用wireshark(?)抓包初体验（？  
总之啥都没会，做出来依托
_答辩_
******
1
--
目前做出来的几个部分中，包含有course
_(课程)_
, room _(房间)_, card _(卡上账目)_, user _(用户)_ 几个部分  
~~不保证接口能用~~  
**测试跑不动找问题真的耗费时间**  
学学[^markdown1]   
[^markdown1]: 此处是**markdown**的*Markdown is a lightweight markup language that you can use to add formatting elements to plaintext text documents.*  
It's 23:45, Dec 30. 知道问题出在哪里，在auth文件中，目前怀疑是加密的问题, 把pymycqu的代码照搬过来后
报错解决, 还能改一改

2
--
* 第一项（_要填空格_）
  - 我等会插一个[链接](https://pymycqu.hagb.name/master/index.html)/[图片](https://pymycqu.hagb.name/master/py-modindex.html)
  - 刚才那个注解怎么不能生效捏
    >很奇怪，注解表示不出来
* 第二项 
  - 包含了一个test，但是还没有填进去对应的数据，我拿自己的试了但是一直在解决测试问题
（_一会插图_）  
  - 总之连接是可用的，因为[^status_code]是2开头的
[^status_code]:表示链接情况
* 第三项
 - 具体的教程请看[郭佬的教程](https://pymycqu.hagb.name/master/index.htm)

3
--
>写给我自己看的  

|form|name1|name2|name3|
|----|-----|----|----|
|urllib|request|post|response|
|requests|get|post|Session|
|dataclasses|dataclass| | |

* 怎么用request/get/post?
  - 或许当时想不起来headers, params, body这些参数，立即搜索
  - 如果不会的东西多，先抄抄怎么用，再试着自己写
  - 还可以[开摆](https://bilibili.com)
--------
写了一点垃圾，耗时三小时，效率底层的🐀决定浅学markdown[^注1]
[^注1]:暂时还没开始看html的东西，🐀🐀也想看到自己写的脚本能运行捏