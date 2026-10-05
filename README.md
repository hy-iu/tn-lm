# tn-lm

张量网络论文库与工具库静态站点(位于 `app/`)。

## 本地预览

在仓库根目录启动一个本地静态服务器,然后浏览器访问 `http://localhost:8000/app/`:

```bash
python -m http.server 8000 -p HTTP/1.1
```

> 注意:Python 3.14 起 `-p` 是 `--protocol`(HTTP 协议版本)选项;端口是位置参数,直接写在命令后面。误写成 `-p 8000` 会把响应状态行破坏,浏览器报 `ERR_INVALID_HTTP_RESPONSE`。

## 转载声明

`chats/` 下两份知乎内容存档转载自以下三个回答,仅作个人学习与研究之用,无任何商业用途,版权归原答主所有:

- 「关于DMRG有什么著作和综述推荐?」——答主 [拉格朗日的忧郁](https://www.zhihu.com/question/426281684/answer/3423870293) 与 [一只冰牙喵](https://www.zhihu.com/question/426281684/answer/3426403454),条目整理见 `chats/DMRG著作与综述推荐_知乎两答资源清单.md`
- 「什么是张量网络(tensor network)?」——答主 [邹一剑](https://www.zhihu.com/question/54786880/answer/146629145),全文存档见 `chats/什么是张量网络_知乎邹一剑答_全文存档.md`

按知乎默认许可协议(CC BY-NC-SA 4.0,即署名-非商业性使用-相同方式共享)标注;如答主另有版权设置或对本次存档有异议,请联系我删除。
