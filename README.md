# tn-lm

张量网络论文库与工具库静态站点(位于 `app/`)。

## 本地预览

在仓库根目录启动一个本地静态服务器,然后浏览器访问 `http://localhost:8000/app/`:

```bash
python -m http.server 8000 -p HTTP/1.1
```

> 注意:Python 3.14 起 `-p` 是 `--protocol`(HTTP 协议版本)选项;端口是位置参数,直接写在命令后面。误写成 `-p 8000` 会把响应状态行破坏,浏览器报 `ERR_INVALID_HTTP_RESPONSE`。
