# 先知爬虫小脚本

本项目基于[XianZhiCrawler](https://github.com/ph0ebus/XianZhiCrawler) 项目进行的修改，由于该作者的原项目无法使用（当前了解到的最新的项目），并且本人以前的先知库又过于老旧，那就自能自力更生了。

最开始本来打算采取html2md进行编写的，后面编写发现确实没那个能力，而且本人的主要目的只是为了离线知识库，所以是不是markdown关系都不是很大（虽然不是markdown有时候可能会因为网页宽度限制导致代码无法完全观察，但是影响不大）。

本项目采取的是selenium+chromedriver进行实现，实话实话，速度真的很慢，而且单线程，感觉跑到天荒地老都跑不完整个先知社区（开玩笑的，跑个一天应该差不多了）

1. 下载[chromedriver](https://googlechromelabs.github.io/chrome-for-testing/)，选择合适的版本下载即可；
2. 解压到自己心仪的位置，然后修改`server=Server('r"<path>"')`为`chromedriver.exe`所在路径即可；
3. `python xianzhicrawler-pdf.py start-paper end-paper`，注意`start-paper>end-paper`，因为该脚本是逆向下载；

最后，该脚本可优化的点还有很多，各位师傅发挥自己的能力吧！
