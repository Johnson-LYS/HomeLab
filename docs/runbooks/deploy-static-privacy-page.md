# 静态隐私政策页面部署说明

## 1. 适用范围

本文用于在 `ali99` 上部署其他 App 的静态隐私政策页面。

推荐统一使用以下地址格式：

```text
https://app.bi8syn.com/<app-slug>/privacy/
```

对应服务器文件路径：

```text
/<app-slug>/privacy/index.html
```

例如，App 标识为 `example-app` 时：

```text
公开地址：https://app.bi8syn.com/example-app/privacy/
文件路径：/example-app/privacy/index.html
```

`<app-slug>` 使用小写字母、数字和连字符，例如 `fmo-companion`，不要包含空格、下划线或中文。

## 2. 当前架构

```text
浏览器
  │ HTTPS 443
  ▼
ali99（8.138.130.141）
  │ 宿主机 Nginx 1.22.1
  └── /<app-slug>/privacy/index.html
```

- Nginx 直接运行在 `ali99` 宿主机，不是容器。
- 站点配置：`/etc/nginx/sites-available/fmo-sites.conf`
- TLS 公共配置：`/etc/nginx/snippets/fmo-bi8syn-ssl.conf`
- 证书目录：`/etc/nginx/ssl/fmo-bi8syn/`
- 证书由 acme.sh 管理，并由 `acme-fmo-renew.timer` 自动续期。
- `app.bi8syn.com` 已解析到 `ali99`，现有证书也已覆盖该域名。

只要继续使用 `app.bi8syn.com/<app-slug>/privacy/`，通常不需要：

- 新增 DNS 记录；
- 修改证书 SAN；
- 新增 FRP 转发；
- 修改 PVE 或内网服务器。

## 3. 操作边界

部署会修改服务器文件并重载 Nginx，执行前须按 `policies/guardrails.md` 获得人工确认。

每次实际部署完成后，还必须在同一次仓库提交中：

1. 更新受影响的 `inventory/` 文件；
2. 向 `operations/log/YYYY/` 追加一条操作记录。

仓库中不得写入密码、私钥、Token 或其他明文凭据；SSH 统一使用 1Password SSH Agent。

## 4. 部署前准备

准备好最终版本的单文件静态网页，例如：

```text
./index.html
```

建议页面不引用外部 JavaScript、字体或统计脚本。当前站点使用严格 CSP；内联 CSS 可用，但外部资源默认会被浏览器阻止。

先设置本次部署变量：

```bash
APP_SLUG=example-app
LOCAL_HTML=./index.html
```

检查变量与本地文件：

```bash
case "$APP_SLUG" in
  (*[!a-z0-9-]*|'') echo "APP_SLUG 不合法"; exit 1 ;;
esac
test -f "$LOCAL_HTML"
```

只读检查服务器现状：

```bash
ssh ali99 'set -eu
nginx -v
systemctl is-active nginx
systemctl is-enabled nginx
nginx -t
systemctl is-active acme-fmo-renew.timer
test -f /etc/nginx/sites-available/fmo-sites.conf
'
```

## 5. 部署静态文件

先上传到固定、明确的暂存路径：

```bash
REMOTE_STAGE="/tmp/${APP_SLUG}-privacy-index.html"
scp "$LOCAL_HTML" "ali99:$REMOTE_STAGE"
```

在服务器上创建时间戳备份，并原子替换页面。将下面的 `example-app` 改为实际的 `<app-slug>`：

```bash
ssh ali99 'set -eu
APP_SLUG=example-app
DEPLOY_STAMP=$(date +%Y%m%d-%H%M%S)
TARGET_DIR="/$APP_SLUG/privacy"
STAGE_FILE="/tmp/${APP_SLUG}-privacy-index.html"
BACKUP_DIR="/root/homelab-backups/$DEPLOY_STAMP"

test -f "$STAGE_FILE"
install -d -o root -g root -m 0755 "$TARGET_DIR"
install -d -o root -g root -m 0700 "$BACKUP_DIR"

if test -f "$TARGET_DIR/index.html"; then
  install -o root -g root -m 0600 \
    "$TARGET_DIR/index.html" \
    "$BACKUP_DIR/${APP_SLUG}-privacy-index.html"
fi

install -o root -g root -m 0644 \
  "$STAGE_FILE" \
  "$TARGET_DIR/index.html.new"
mv "$TARGET_DIR/index.html.new" "$TARGET_DIR/index.html"
rm "$STAGE_FILE"

sha256sum "$TARGET_DIR/index.html"
echo "BACKUP_DIR=$BACKUP_DIR"
'
```

保存输出中的 `BACKUP_DIR`，回滚时需要使用。

## 6. 增加 Nginx 路由

先备份配置：

```bash
ssh ali99 'set -eu
DEPLOY_STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/root/homelab-backups/$DEPLOY_STAMP"
install -d -o root -g root -m 0700 "$BACKUP_DIR"
install -o root -g root -m 0600 \
  /etc/nginx/sites-available/fmo-sites.conf \
  "$BACKUP_DIR/fmo-sites.conf"
echo "BACKUP_DIR=$BACKUP_DIR"
'
```

编辑 `/etc/nginx/sites-available/fmo-sites.conf`，在 `server_name app.bi8syn.com;` 对应的 HTTPS `server` 块中加入以下三段。将 `example-app` 替换为实际 `<app-slug>`：

```nginx
location = /example-app/privacy {
    return 308 /example-app/privacy/;
}

location = /example-app/privacy/ {
    root /;
    default_type text/html;
}

location = /example-app/privacy/index.html {
    root /;
    default_type text/html;
}
```

注意：

- 这里必须使用 `root /;`。不要把目录精确匹配写成指向 `index.html` 的 `alias`，否则可能形成内部重定向循环并返回 500。
- 当前安全响应头在 `server` 层统一配置。不要在上述 `location` 中随意增加 `add_header`，因为 Nginx 会因此停止继承父级的整组响应头。
- 保留兜底的 `location / { return 404; }`，防止意外暴露其他文件。

修改后先校验，再平滑重载：

```bash
ssh ali99 'set -eu
nginx -t
systemctl reload nginx
systemctl is-active nginx
'
```

不要跳过 `nginx -t`，也不需要为此次部署重启 Nginx。

## 7. 验证

### 7.1 在服务器本机验证

将 `example-app` 替换为实际 `<app-slug>`：

```bash
ssh ali99 'set -eu
curl -ksS -o /dev/null -w "slashless=%{http_code} redirect=%{redirect_url}\n" \
  --resolve app.bi8syn.com:443:127.0.0.1 \
  https://app.bi8syn.com/example-app/privacy

curl -ksS -o /dev/null -w "canonical=%{http_code} type=%{content_type}\n" \
  --resolve app.bi8syn.com:443:127.0.0.1 \
  https://app.bi8syn.com/example-app/privacy/

curl -ksSI \
  --resolve app.bi8syn.com:443:127.0.0.1 \
  https://app.bi8syn.com/example-app/privacy/
'
```

预期结果：

- 不带末尾 `/` 的地址返回 `308`，并跳转到带 `/` 的地址；
- 规范地址返回 `200`；
- `Content-Type` 为 `text/html`；
- 响应中包含 CSP、`X-Content-Type-Options`、`X-Frame-Options` 和 `Referrer-Policy`。

### 7.2 从公网验证

```bash
curl -fsSIL "https://app.bi8syn.com/${APP_SLUG}/privacy/"
curl -fsS "https://app.bi8syn.com/${APP_SLUG}/privacy/" | sed -n '1,20p'
```

最后使用浏览器打开：

```text
https://app.bi8syn.com/<app-slug>/privacy/
```

确认页面内容、App 名称、发布日期、联系邮箱和跳转地址均正确。

## 8. 回滚

如果 `nginx -t` 失败，不要重载；直接恢复刚才备份的配置。将示例中的时间戳目录替换为实际备份目录：

```bash
ssh ali99 'set -eu
BACKUP_DIR=/root/homelab-backups/20260827-120000
install -o root -g root -m 0644 \
  "$BACKUP_DIR/fmo-sites.conf" \
  /etc/nginx/sites-available/fmo-sites.conf
nginx -t
systemctl reload nginx
'
```

如果新页面内容有误，使用部署静态文件时保存的备份恢复：

```bash
ssh ali99 'set -eu
APP_SLUG=example-app
BACKUP_DIR=/root/homelab-backups/20260827-120000
install -o root -g root -m 0644 \
  "$BACKUP_DIR/${APP_SLUG}-privacy-index.html" \
  "/$APP_SLUG/privacy/index.html.new"
mv "/$APP_SLUG/privacy/index.html.new" "/$APP_SLUG/privacy/index.html"
'
```

若该 App 是首次部署、没有旧页面，则优先恢复 Nginx 配置，使新路径重新返回 404；页面文件可暂时保留，待另行确认后再清理。

## 9. 部署后记录

实际部署成功后，在 HomeLab 仓库中完成闭环：

1. 更新 `inventory/services.md`；若公开入口或网络路径发生变化，同时更新 `inventory/network.md`；
2. 在 `operations/log/YYYY/` 新增一条记录，至少包含：
   - App 标识和公开 URL；
   - 页面文件路径；
   - Nginx 配置路径；
   - 备份目录；
   - `nginx -t`、本机 SNI、公网 HTTPS 的验证结果；
   - 回滚方法；
3. 检查仓库中没有凭据或私钥；
4. 提交并推送本次文档变更。

## 10. 常见问题

### 返回 404

- 检查 URL 中的 `<app-slug>` 是否与目录、Nginx location 完全一致；
- 检查 `/<app-slug>/privacy/index.html` 是否存在；
- 检查配置是否加在 `app.bi8syn.com` 的 HTTPS `server` 块内；
- 执行 `nginx -T` 确认生效配置，并查看 Nginx error log。

### 返回 500 或日志出现 internal redirection cycle

通常是精确目录 location 使用了错误的 `alias .../index.html`。改用本文的 `root /;` 三段式配置。

### 浏览器提示证书不匹配

确认访问的是 `app.bi8syn.com`。如果改用新的子域名，就必须先配置 DNS，并重新签发包含新域名 SAN 的证书；这不属于标准路径部署流程。

### HTTP 返回备案相关错误

中国大陆云服务器的 80 端口可能被云厂商拦截并显示备案提示。隐私政策应直接使用 HTTPS 地址。当前证书续期采用 TLS-ALPN，不依赖 HTTP-01。

### acme.sh 续期失败

先检查：

```bash
ssh ali99 'systemctl status acme-fmo-renew.timer --no-pager; journalctl -u acme-fmo-renew.service -n 100 --no-pager'
```

若是访问 Let's Encrypt API 超时，应处理 `ali99` 的受控出站网络，或评估迁移到 DNS-01；不要临时关闭证书校验，也不要把 DNS API 密钥写入仓库。

## 11. 最短执行清单

- 确定 `<app-slug>` 和最终 `index.html`；
- 获得变更确认；
- 检查 Nginx、证书续期计时器和现有配置；
- 备份旧页面与 Nginx 配置；
- 部署 `/<app-slug>/privacy/index.html`；
- 增加三段精确 location；
- 执行 `nginx -t` 后 reload；
- 验证 308、200、安全响应头和公网 HTTPS；
- 更新 inventory、追加 operations log；
- 提交并推送。
