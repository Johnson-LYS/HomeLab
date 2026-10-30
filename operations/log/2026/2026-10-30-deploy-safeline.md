---
date: 2026-10-30
type: deployment
affected: [frp, ali99-2, safeline]
verified_by: ai
status: deployed
---

# frp 设备部署雷池

用户授权：先检查硬件与磁盘，在 frp 安装雷池，先接 Trust，验收后接 PKI 和 OTA，保留回滚配置。

## 预检与备份

- Intel Celeron 3865U，2 核，支持 SSSE3，不支持 AVX2；7.7GiB 内存，部署前可用 7.3GiB。
- `/dev/sda2` 根分区 13GB，部署前剩余约 11GB；无额外磁盘。
- 两端备份：`/root/homelab-backups/20261030-safeline`，包含原 FRP 配置与云端 Nginx 配置。
- 独立 SSH 入口可用；家庭路由器、Surge 配置不改。

## 安装

- Debian 官方 docker.io/docker-compose；设备直连源下载缓慢，改由 Mac 下载官方 deb 后投放 APT 缓存，APT 正常校验安装。
- 使用官方 `https://waf-ce.chaitin.cn/release/latest/compose.yaml`，固定版本 9.4.3；数据库镜像版本遵循官方 manager 配置 15.18。
- 安装目录 `/opt/safeline`；管理端口仅绑定 `127.0.0.1:9443`。
- 独立数据库密码从 `op://HomeLab/safeline-frp-db/password` 注入；配置权限 0600，仓库不保存秘密。
- Compose override 将各容器 stdout 日志限制为 10MB × 2；业务攻击日志另需设置保留策略。

## 接入与验证

- 官方 Compose 的检测管理鉴权默认开启，但 Token 留空会导致 FVM 下发规则报 401；保持鉴权开启，通过 `op://HomeLab/safeline-frp-internal/password` 统一内部 Token 后，规则下发正常。
- 管理凭据保存到 `op://HomeLab/safeline-frp-admin/password`。API 登录按该版本 UI 的 CSRF 与 AES 流程执行，凭据不输出。
- 站点配置：Trust site 2/19090；PKI site 3/19091；OTA site 4/19089。全局真实 IP 为 `http_header/X-Real-IP`，保留 Host；不覆盖云端原始 HTTPS 协议头。全局关闭 gzip/br，保持 OTA 文件字节与 ETag 语义。
- 站点级高级代理设置需要额外授权；采用社区版支持的全局真实 IP 配置，未绕过产品授权检查。
- `safeline-local-only.service` 禁止非 loopback 访问 19089/19090/19091/65443，SSH 22 不受影响；9443 仅回环绑定。
- Trust 与 PKI 原先共享远端 18090，因此新增 Trust 独立远端 18091。先切换云端 Trust 并验收，再切换 PKI 和 OTA 的 FRPC 目标。
- 云端 `trust-waf` 只服务 Trust，`fmo-trust` 只服务 PKI；覆盖客户端传入的 X-Forwarded-For，防止伪造 IP。原有证书与续期机制保持。
- Trust 公网首页/readiness 200，未登录管理 API 401；PKI 根及管理 API 404；OTA 首页及 healthz 200。模拟 SQL 注入在本机及公网均 403。
- 公网携带伪造 IP 头的攻击探测中，雷池记录实际公网来源而非伪造值，socket IP 为 127.0.0.1。
- OTA 已存在 RF-Link 0.1.2 build 4 发布包；公网 Range 0-15 返回 206，Content-Range 为 `bytes 0-15/70977069`，16 字节 SHA256 与内网一致。latest.json 返回 no-cache/must-revalidate，APK 保留 immutable 缓存头。
- 三站均未开启浏览器挑战和动态加密；没有操作生产 CA、管理员 Passkey 或签名业务。真实 Passkey 登录/照片上传仍需管理员交互验收，不能仅靠 readiness 宣称完整通过。
- 7 个容器正常，mgt/detector/postgres healthcheck healthy；空载容器内存约 650MB，根分区剩余约 8.5GB。攻击日志保留 3 天，统计 7 天、报告 0。

## 回滚

- 切换前业务继续使用直达 n100 的原始映射；切换后可从备份恢复客户端片段，校验后重启 frpc。
- 云端配置从备份恢复并 `nginx -t` 后 reload。
- 停用雷池使用 `docker compose stop`，保留数据库、配置与镜像，不删除数据卷。
- 已保存并通过 `sh -n` 的回滚脚本：先在 frp 执行备份目录中的 `rollback-frp.sh`，再在 ali99-2 执行 `rollback-cloud.sh`；恢复窗口 Trust 可能短暂不可用。脚本将新配置移至备份目录而非删除。
- 备份目录含 `sites.after.json`、`proxy.after.json`、`retention.after.json` 等配置快照；原始备份永久保留。
