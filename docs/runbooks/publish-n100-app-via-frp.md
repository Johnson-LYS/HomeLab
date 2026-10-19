# 通过 FRP 发布 n100 应用

## 固定架构

```text
公网用户 → ali99-2 Nginx:443
         → ali99-2 127.0.0.1:18xxx
         → FRP TLS 隧道
         → frp 网关 192.168.8.198
         → n100 192.168.8.15:<应用端口>
```

- FRP 控制端口：`ali99-2:7000/tcp`。
- 允许的应用映射池：`18000-18099`。
- `frps.proxyBindAddr` 固定为 `127.0.0.1`，映射端口不能直接被公网访问。
- Nginx 是唯一的应用公网入口。

## 1. 前置检查

```bash
ssh frp 'systemctl is-active frpc; /usr/local/bin/frpc --version'
ssh ali99-2 'systemctl is-active frps nginx; nginx -t; /usr/local/bin/frps --version'
```

在 `frp` 网关检查 n100 应用可达：

```bash
ssh frp 'curl -fsS http://192.168.8.15:<应用端口>/health'
```

如果应用没有健康检查端点，可先使用 `curl -I` 或 `nc -vz` 做 TCP 检查。

## 2. 分配映射端口

在 `ali99-2` 查看已占用端口：

```bash
ssh ali99-2 "ss -lnt | grep -E '127\\.0\\.0\\.1:18[0-9]{3}' || true"
```

从 `18000-18099` 中选择一个未占用端口，并同步登记到 `inventory/network.md` 与 `inventory/services.md`。

## 3. 增加 frpc 代理

在 `frp:/etc/frp/conf.d/<app-name>.toml` 增加：

```toml
[[proxies]]
name = "n100-<app-name>"
type = "tcp"
localIP = "192.168.8.15"
localPort = <应用端口>
remotePort = <18xxx>
```

先校验，再重启：

```bash
ssh frp 'set -eu
runuser -u frp -- /usr/local/bin/frpc verify -c /etc/frp/frpc.toml
systemctl restart frpc
systemctl is-active frpc
journalctl -u frpc -n 50 --no-pager
'
```

在云端确认只监听回环地址：

```bash
ssh ali99-2 "ss -lntp | grep '127.0.0.1:<18xxx>'"
curl -fsS http://127.0.0.1:<18xxx>/health
```

如果监听地址不是 `127.0.0.1`，停止发布并检查 `/etc/frp/frps.toml` 的 `proxyBindAddr`。

## 4. 配置 Nginx 与 HTTPS

为应用创建独立 Nginx vhost，将后端指向：

```nginx
proxy_pass http://127.0.0.1:<18xxx>;
```

同时传递常用代理头：

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

修改前备份现有配置，修改后必须执行：

```bash
ssh ali99-2 'nginx -t && systemctl reload nginx'
```

DNS A 记录应指向 `47.109.85.53`。使用 Certbot 为新域名签发证书并确认自动续期；不要复用与新域名不匹配的证书。

## 5. 三段验证

1. `frp` → `n100:<应用端口>`；
2. `ali99-2:127.0.0.1:<18xxx>` → FRP → n100；
3. 公网 `https://<应用域名>/` → Nginx → FRP → n100。

检查服务与日志：

```bash
ssh frp 'systemctl status frpc --no-pager; journalctl -u frpc -n 100 --no-pager'
ssh ali99-2 'systemctl status frps nginx --no-pager; journalctl -u frps -n 100 --no-pager'
```

## 6. 回滚

1. 先从 Nginx 移除或禁用新域名 vhost，并执行 `nginx -t && systemctl reload nginx`；
2. 将对应 `<app-name>.toml` 移出 `/etc/frp/conf.d/`；
3. 校验并重启 frpc；
4. 确认云端对应 `127.0.0.1:<18xxx>` 已停止监听；
5. 更新 inventory，并向 `operations/log/YYYY/` 追加操作记录。
