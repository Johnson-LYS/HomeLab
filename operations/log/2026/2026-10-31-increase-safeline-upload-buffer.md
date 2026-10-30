---
date: 2026-10-31
type: tuning
affected: [frp, safeline-tengine]
verified_by: ai
---

# 雷池上传内存缓冲调整为 1MiB

- 用户确认将 `client_body_buffer_size` 从 128k 调到 1m，以减少较小图片上传的临时磁盘写入。
- 修改的是持久挂载 `/opt/safeline/resources/nginx/nginx.conf` 的 http 级配置，不修改自动生成的站点文件；容器重建仍可保留，升级后需核对此自定义项。
- 变更前备份：`/root/homelab-backups/20261031-upload-buffer/nginx.conf.before`。
- `docker exec safeline-tengine nginx -t` 成功后执行 `nginx -s reload` 平滑重载；校验失败会自动恢复备份。
- `nginx -T` 确认有效值为 1m；未改变 `client_max_body_size`、云端应用上传限制或检测引擎的 `t1k_body_size`。
- 回归：Trust readiness 200、PKI 根路径预期 404、OTA healthz 200；容器保持 running。
- 未创建业务上传数据；实际图片上传行为由后续正常业务观察。大于 1MiB 的请求仍可能落盘，不应通过提高日志级别掩盖警告。
- 回滚：恢复上述备份到原位置，执行 `docker exec safeline-tengine nginx -t` 成功后 `docker exec safeline-tengine nginx -s reload`。
