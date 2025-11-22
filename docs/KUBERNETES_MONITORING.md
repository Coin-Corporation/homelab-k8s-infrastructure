# Kubernetes 监控配置指南

本文档说明如何在本地 Grafana 中查看 Kubernetes 集群监控 dashboard。

## 📋 前置要求

1. 本地运行的 Kubernetes 集群 (minikube, kind, Docker Desktop 等)
2. `kubectl` 已配置好并能访问集群
3. Docker 和 Docker Compose 已安装

## 🚀 快速开始

### 1. 启动监控栈

```bash
# 启动 Grafana + Prometheus + Loki 监控系统
docker compose -f docker-compose.logging.yml up -d
```

这将启动以下服务：
- **Grafana**: http://localhost:3001 - 可视化平台
- **Prometheus**: http://localhost:9090 - 指标收集
- **Loki**: http://localhost:3100 - 日志聚合
- **Node Exporter**: http://localhost:9100 - 节点指标
- **Promtail**: 日志采集器

### 2. 配置 Kubernetes 指标采集

由于 Prometheus 运行在 Docker 容器中，需要配置它访问你的 Kubernetes 集群。

#### 方法 A: 使用 Docker Desktop Kubernetes (推荐)

如果你使用 Docker Desktop 的内置 Kubernetes：

```bash
# Prometheus 已配置 extra_hosts，可以通过 host.docker.internal 访问宿主机
# 确保你的 kubeconfig 在默认位置 ~/.kube/config
# 无需额外配置
```

#### 方法 B: 使用 minikube

```bash
# 1. 暴露 minikube API server
minikube kubectl -- proxy --port=8001 &

# 2. 修改 prometheus-config.yml 中的 kubernetes_sd_configs
# 将 API server 地址改为 http://host.docker.internal:8001
```

#### 方法 C: 在 Kubernetes 内部署 Prometheus (推荐生产环境)

```bash
# 部署 kube-state-metrics
kubectl apply -f https://github.com/kubernetes/kube-state-metrics/examples/standard

# 然后在集群内部署 Prometheus
# 使用 k8s/ 目录下的配置
```

### 3. 访问 Grafana Dashboard

1. 打开浏览器访问: http://localhost:3001
2. 登录 (用户名: `admin`, 密码: `admin`)
3. 点击左侧菜单 **Dashboards**
4. 选择 **"Kubernetes - Yanlord 集群监控"**

你将看到：
- ✅ 节点 CPU 使用率
- ✅ 节点内存使用率  
- ✅ Pod CPU 使用率
- ✅ Pod 内存使用
- ✅ Pod 状态
- ✅ Pod 重启次数

## 🔧 故障排查

### Prometheus 无法连接到 Kubernetes

检查 Prometheus targets 状态：

```bash
# 方法 1: Web UI
open http://localhost:9090/targets

# 方法 2: API
curl http://localhost:9090/api/v1/targets | jq
```

如果看到错误，检查：

1. **kubectl 是否能正常访问集群**
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

2. **Prometheus 容器内是否能访问 API server**
   ```bash
   docker exec prometheus wget -O- http://host.docker.internal:8001/api/v1/nodes
   ```

### Dashboard 没有数据

1. **检查 Prometheus 是否有数据**
   ```bash
   # 访问 Prometheus UI 执行查询
   open http://localhost:9090
   
   # 尝试查询: up
   # 应该能看到所有 targets
   ```

2. **检查 Grafana 数据源配置**
   - 在 Grafana 中进入 Configuration → Data sources
   - 点击 Prometheus
   - 点击 "Save & Test" 按钮
   - 应该显示绿色的 "Data source is working"

3. **检查你的 Pods 是否在运行**
   ```bash
   kubectl get pods -n default
   # 确保有 yanlord-* 开头的 pods
   ```

### 修改 Prometheus 配置

```bash
# 1. 编辑配置文件
vi monitoring/prometheus-config.yml

# 2. 重启 Prometheus
docker compose -f docker-compose.logging.yml restart prometheus

# 3. 验证配置
docker exec prometheus promtool check config /etc/prometheus/prometheus.yml
```

## 📊 自定义 Dashboard

### 添加新的面板

1. 在 Dashboard 中点击右上角的 **Add panel**
2. 选择 **Prometheus** 数据源
3. 输入 PromQL 查询，例如：
   ```promql
   # Pod 网络接收字节数
   sum(rate(container_network_receive_bytes_total{namespace="default"}[5m])) by (pod)
   
   # Pod 文件系统使用率
   (container_fs_usage_bytes / container_fs_limit_bytes) * 100
   ```
4. 点击 **Apply**

### 导入社区 Dashboard

Grafana 社区提供了很多优秀的 Kubernetes dashboards：

1. 访问 https://grafana.com/grafana/dashboards/
2. 搜索 "kubernetes"
3. 找到喜欢的 dashboard，记下 ID
4. 在 Grafana 中: Dashboards → Import → 输入 ID → Import

推荐的 Dashboards:
- **315**: Kubernetes cluster monitoring
- **8588**: Kubernetes Deployment Statefulset Daemonset metrics
- **6417**: Kubernetes Cluster (Prometheus)

## 🛠️ 高级配置

### 启用持久化存储

数据已经持久化到 Docker volumes：
```bash
# 查看 volumes
docker volume ls | grep yanlord

# 查看 Prometheus 数据大小
docker exec prometheus du -sh /prometheus
```

### 配置告警

编辑 `monitoring/prometheus-config.yml` 添加告警规则：

```yaml
rule_files:
  - "alerts/*.yml"
```

创建 `monitoring/alerts/kubernetes.yml`:

```yaml
groups:
  - name: kubernetes
    interval: 30s
    rules:
      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[5m]) > 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} is crash looping"
```

### 暴露到外网

如果需要从其他机器访问：

```bash
# 修改 docker-compose.logging.yml 中的端口绑定
# 将 "3001:3000" 改为 "0.0.0.0:3001:3000"

# 或者使用 nginx 反向代理
```

## 📚 参考资源

- [Prometheus 查询语法](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard 最佳实践](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [Kubernetes 监控指标](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)
- [LogQL 查询语法](https://grafana.com/docs/loki/latest/logql/)

## 🆘 需要帮助？

查看 `monitoring/QUICKSTART.md` 获取更多查询示例和使用技巧。
