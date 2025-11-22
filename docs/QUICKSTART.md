# 🚀 监控系统 - 快速上手指南

## ⚡ 5 分钟快速开始

### 1. 启动监控系统

```bash
# 方式 1: 使用快速启动脚本（推荐）
./monitoring/start-monitoring.sh

# 方式 2: 使用 docker compose
docker compose -f docker-compose.logging.yml up -d
```

### 2. 访问系统

打开浏览器：**http://localhost:3001**

- 用户名：`admin`
- 密码：`admin`
- **Grafana**: http://localhost:3001 - 可视化界面
- **Prometheus**: http://localhost:9090 - 指标查询
- **Loki**: http://localhost:3100 - 日志服务

（首次登录可选择跳过修改密码）

### 3. 查看 Kubernetes Dashboard

1. 登录 Grafana 后，点击左侧菜单 **📊 Dashboards**
2. 找到 **"Kubernetes - Yanlord 集群监控"** dashboard
3. 可以查看：
   - 节点 CPU/内存使用率
   - Pod CPU/内存使用
   - Pod 状态和重启次数

### 4. 开始查询日志

1. 点击左侧菜单 **🔍 Explore**
2. 确保数据源为 **Loki**
3. 输入查询：
   ```logql
   {container=~"yanlord-booking.*"}
   ```
4. 点击 **Run query** 或按 `Shift + Enter`

---

## 📖 常用查询示例

### 📝 Loki 日志查询

#### 查看所有应用日志
```logql
{container=~"yanlord-booking.*"}
```

#### 只看错误日志
```logql
{container=~"yanlord-booking.*"} |= "ERROR"
```

#### 查看预订成功的日志
```logql
{container=~"yanlord-booking.*"} |= "success"
```

### 📊 Prometheus 指标查询

在 Grafana Explore 中选择 **Prometheus** 数据源，然后尝试这些查询：

#### 查看节点 CPU 使用率
```promql
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

#### 查看节点内存使用率
```promql
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

#### 查看 Pod CPU 使用率
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="default",pod=~"yanlord.*"}[5m])) by (pod)
```

#### 查看 Pod 内存使用
```promql
sum(container_memory_usage_bytes{namespace="default",pod=~"yanlord.*"}) by (pod)
```

#### 查看 Pod 重启次数
```promql
sum(kube_pod_container_status_restarts_total{namespace="default",pod=~"yanlord.*"}) by (pod)
```

### 查看某个任务的日志（替换为实际任务ID前8位）
```logql
{container=~"yanlord-booking.*"} |= "job_id" |= "b10433aa"
```

### 统计最近1小时的错误数
```logql
sum(count_over_time({container=~"yanlord-booking.*"} |= "ERROR" [1h]))
```

---

## 📊 创建仪表板

### 方法 1: 快速创建

1. 点击 **+ → Dashboard → Add visualization**
2. 选择 **Loki** 数据源
3. 输入查询语句
4. 点击 **Apply**

### 方法 2: 导入预设

1. 点击 **Dashboards → New → Import**
2. 输入 Dashboard ID: `13639` (Loki Dashboard)
3. 选择 Loki 数据源
4. 点击 **Import**

---

## 🛠️ 常用命令

### 查看服务状态
```bash
docker compose -f docker-compose.logging.yml ps
```

### 查看日志
```bash
# 查看所有服务日志
docker compose -f docker-compose.logging.yml logs -f

# 只看 Loki 日志
docker compose -f docker-compose.logging.yml logs -f loki

# 只看 Prometheus 日志
docker compose -f docker-compose.logging.yml logs -f prometheus

# 只看 Promtail 日志
docker compose -f docker-compose.logging.yml logs -f promtail
```

### 验证 Prometheus 配置
```bash
# 检查 Prometheus 配置是否有效
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml

# 查看 Prometheus targets 状态
curl http://localhost:9090/api/v1/targets
```

### 重启服务
```bash
docker compose -f docker-compose.logging.yml restart
```

### 停止服务
```bash
docker compose -f docker-compose.logging.yml down
```

### 完全清理（包括数据）
```bash
docker compose -f docker-compose.logging.yml down -v
```

---

## 🎯 推荐的查询技巧

### 1. 使用标签过滤
```logql
{container="yanlord-booking", level="ERROR"}
```

### 2. 正则表达式匹配
```logql
{container=~"yanlord-booking.*"} |~ "error|fail|exception"
```

### 3. 排除某些内容
```logql
{container=~"yanlord-booking.*"} != "DEBUG"
```

### 4. 时间范围查询
```logql
{container=~"yanlord-booking.*"} [5m]  # 最近5分钟
{container=~"yanlord-booking.*"} [1h]  # 最近1小时
```

### 5. 聚合统计
```logql
# 每5分钟的日志数量
sum(rate({container=~"yanlord-booking.*"}[5m]))

# 按日志级别分组统计
sum by (level) (count_over_time({container=~"yanlord-booking.*"}[1h]))
```

---

## 🔧 故障排查

### 系统无法访问？
```bash
# 检查服务状态
docker compose -f docker-compose.logging.yml ps

# 检查端口占用
lsof -i :3000
```

### 没有看到日志？
```bash
# 1. 确认应用容器正在运行
docker ps | grep yanlord

# 2. 检查 Promtail 是否正常
docker compose -f docker-compose.logging.yml logs promtail

# 3. 检查 Loki 健康状态
curl http://localhost:3100/ready
```

### Docker socket 权限问题？
```bash
# macOS / Linux
sudo chmod 666 /var/run/docker.sock
```

---

## 💡 最佳实践

1. **定期检查日志存储大小**
   ```bash
   docker volume inspect yanlord-booking_loki-data
   ```

2. **设置告警规则**
   - 错误率过高
   - 预订失败次数
   - 系统异常

3. **保存常用查询**
   - 在 Grafana Explore 中点击 ⭐ 收藏查询

4. **创建专属仪表板**
   - 预订成功率
   - 错误趋势
   - 实时日志流

---

## 📚 更多资源

- [完整文档](./monitoring/README.md)
- [Loki 官方文档](https://grafana.com/docs/loki/latest/)
- [LogQL 查询语法](https://grafana.com/docs/loki/latest/logql/)
- [Grafana 仪表板库](https://grafana.com/grafana/dashboards/)

---

**提示**: 建议先在 Explore 中测试查询，确认无误后再添加到仪表板。
