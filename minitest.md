## 文档使用

Minium的文档是采用Nodejs编写的，因此想看文档还需要安装NodeJs的环境，如果你不知道怎么安装请自行查找。文档的安装：

```javascript
npm i docsify-cli -g
```

然后checkout文档项目：

```javascript
git clone https://git.weixin.qq.com/minitest/minium-doc
```

安装依赖：

```javascript
cd minium-doc
npm install
```

本地部署：

```javascript
docsify serve .
```

然后通过浏览器访问 http://localhost:3000 即可以查看了