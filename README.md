# Homelab Kubernetes Infrastructure

🏗️ 通用的 Kubernetes 基础设施配置，提供完整的监控、日志和可观测性栈。

## 📋 功能特性

- 📊 **Prometheus** - 指标收集和存储
- 📝 **Loki** - 日志聚合系统
- 📈 **Grafana** - 统一可视化平台
- 🔍 **Kube-State-Metrics** - Kubernetes 状态指标（自定义增强版）
- 📡 **Node Exporter** - 节点级别监控
- 🚀 **一键部署脚本** - 快速部署整套栈

## 🚀 快速开始

### Kubernetes 环境

```bash
# 部署核心配置（命名空间、资源配额）
kubectl apply -f kubernetes/core/

# 部署完整监控栈
kubectl apply -f kubernetes/monitoring/
```

### Docker Compose 环境

```bash
cd monitoring
docker-compose up -d
```

访问:
- Grafana: http://localhost:30300
- Prometheus: http://localhost:30090
- Loki: http://localhost:3100

## 📁 目录结构

```
.
├── monitoring/           # Docker Compose 监控栈
│   ├── prometheus/      # Prometheus 配置
│   ├── loki/           # Loki 配置
│   ├── grafana/        # Grafana 配置
│   ├── promtail/       # Promtail 配置
│   └── docker-compose.yml
├── kubernetes/          # Kubernetes 部署
│   ├── core/          # 核心配置（namespace, quotas）
│   │   ├── namespaces.yaml
│   │   └── resource-quotas.yaml
│   ├── monitoring/    # 监控组件
│   │   ├── kube-state-metrics/   # 自定义指标导出器
│   │   ├── prometheus-*.yaml     # Prometheus 部署
│   │   ├── loki-*.yaml          # Loki 日志系统
│   │   ├── grafana-*.yaml       # Grafana 可视化
│   │   └── node-exporter.yaml   # 节点监控
│   └── logging/       # 日志组件
└── docs/              # 文档
    ├── KUBERNETES_MONITORING.md
    └── QUICKSTART.md
```

## 🔗 使用项目

本基础设施被以下项目使用:

- [Yanlord-Badminton-Booking](https://github.com/Coin-Corporation/Yanlord-Badminton-Booking) - 羽毛球场预订系统

## 🛠️ 自定义扩展

### Kube-State-Metrics 增强版

我们的自定义版本额外提供:
- ✅ CronJob 状态指标（active, next_schedule_time, last_schedule_time）
- ✅ Pod 启动时间和完成时间
- ✅ Service 信息（cluster_ip, type）
- ✅ Namespace 状态和创建时间
- ✅ 完整的 Pod 和 Deployment 信息

位置: `kubernetes/monitoring/kube-state-metrics/`

### Promtail Sidecar 模板

提供开箱即用的 Promtail sidecar 配置，支持:
- JSON 日志解析
- 自动时间戳提取
- 标签过滤
- 错误处理

## 📊 监控指标

### Prometheus 收集的指标

- **节点指标**: CPU、内存、磁盘、网络
- **Pod 指标**: 资源使用、状态、重启次数
- **容器指标**: CPU、内存、网络流量
- **Kubernetes 对象**: Deployment、Service、CronJob 状态

### Loki 日志聚合

- 支持 JSON 格式日志
- 按 namespace、pod、level 分类
- 全文搜索和过滤
- 与 Prometheus 指标关联

## 🔧 配置说明

### Prometheus

配置文件: `monitoring/prometheus/prometheus-config.yml`

主要配置:
- 数据保留期: 15 天
- 抓取间隔: 15 秒
- 目标: Kubernetes API、cAdvisor、Node Exporter、Kube-State-Metrics

### Loki

配置文件: `monitoring/loki/loki-config.yml`

主要配置:
- 日志保留期: 30 天
- 索引周期: 24 小时
- 存储: 文件系统 (可配置为 S3/GCS)

### Grafana

配置文件: `monitoring/grafana/grafana-datasources.yml`

预配置数据源:
- Prometheus (指标)
- Loki (日志)

## 🚢 部署方式

### 方式 1: 直接应用 YAML

```bash
kubectl apply -f kubernetes/core/
kubectl apply -f kubernetes/monitoring/
```

### 方式 2: 使用 Kustomize

```bash
kubectl apply -k kubernetes/monitoring/
```

### 方式 3: Docker Compose (本地开发)

```bash
cd monitoring
docker-compose up -d
```

## 📝 集成到应用项目

### 使用 Git Submodule（推荐）

在你的应用 repo 中:

```bash
# 添加为 submodule
git submodule add git@github.com:Coin-Corporation/homelab-k8s-infrastructure.git infrastructure

# 部署基础设施
kubectl apply -f infrastructure/kubernetes/monitoring/

# 部署你的应用
kubectl apply -f k8s/
```

### 直接引用

```bash
# 克隆此 repo
git clone https://github.com/Coin-Corporation/homelab-k8s-infrastructure.git

# 部署
cd homelab-k8s-infrastructure
kubectl apply -f kubernetes/monitoring/
```

## 🔍 验证部署

```bash
# 检查所有 Pod 状态
kubectl get pods -n monitoring
kubectl get pods -n kube-system

# 检查服务
kubectl get svc -n monitoring

# 访问 Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80

# 测试 Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

## 📚 文档

- [Kubernetes 监控指南](docs/KUBERNETES_MONITORING.md)
- [快速开始](docs/QUICKSTART.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

改进建议:
- 添加更多监控 Dashboard
- 支持更多存储后端
- 增强告警规则
- 添加自动化测试

## 📄 许可

MIT License

## 🙏 致谢

本项目使用以下开源组件:
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Loki](https://grafana.com/oss/loki/)
- [Kubernetes](https://kubernetes.io/)

---

**维护者**: Coin-Corporation  
**最后更新**: 2025-11-22
