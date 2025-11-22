#!/usr/bin/env python3
"""
轻量级 Kubernetes State Metrics Exporter
暴露基本的 Pod、Deployment、Node 状态指标
"""
import time
from kubernetes import client, config
from prometheus_client import start_http_server, Gauge
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义 Prometheus 指标
kube_pod_info = Gauge('kube_pod_info', 'Pod information', ['namespace', 'pod', 'node', 'pod_ip', 'uid'])
kube_pod_status_phase = Gauge('kube_pod_status_phase', 'Pod phase', ['namespace', 'pod', 'phase'])
kube_pod_container_status_ready = Gauge('kube_pod_container_status_ready', 'Container ready status', ['namespace', 'pod', 'container'])
kube_pod_container_status_restarts = Gauge('kube_pod_container_status_restarts_total', 'Container restarts', ['namespace', 'pod', 'container'])
kube_pod_labels = Gauge('kube_pod_labels', 'Pod labels', ['namespace', 'pod', 'label_app'])
kube_deployment_spec_replicas = Gauge('kube_deployment_spec_replicas', 'Desired replicas', ['namespace', 'deployment'])
kube_deployment_replicas = Gauge('kube_deployment_status_replicas', 'Deployment replicas', ['namespace', 'deployment'])
kube_deployment_replicas_available = Gauge('kube_deployment_status_replicas_available', 'Available replicas', ['namespace', 'deployment'])
kube_node_info = Gauge('kube_node_info', 'Node information', ['node', 'kernel_version', 'os_image', 'container_runtime_version'])
kube_node_status_condition = Gauge('kube_node_status_condition', 'Node condition', ['node', 'condition', 'status'])
kube_cronjob_info = Gauge('kube_cronjob_info', 'CronJob information', ['namespace', 'cronjob'])
kube_cronjob_status_active = Gauge('kube_cronjob_status_active', 'Active jobs count', ['namespace', 'cronjob'])
kube_cronjob_next_schedule_time = Gauge('kube_cronjob_next_schedule_time', 'Next schedule time', ['namespace', 'cronjob'])
kube_cronjob_status_last_schedule_time = Gauge('kube_cronjob_status_last_schedule_time', 'Last schedule time', ['namespace', 'cronjob'])
kube_cronjob_spec_suspend = Gauge('kube_cronjob_spec_suspend', 'CronJob suspend status', ['namespace', 'cronjob'])
kube_pod_start_time = Gauge('kube_pod_start_time', 'Pod start time', ['namespace', 'pod'])
kube_pod_completion_time = Gauge('kube_pod_completion_time', 'Pod completion time', ['namespace', 'pod'])
kube_pod_created = Gauge('kube_pod_created', 'Pod creation time', ['namespace', 'pod'])
kube_service_info = Gauge('kube_service_info', 'Service information', ['namespace', 'service', 'cluster_ip', 'type'])
kube_namespace_created = Gauge('kube_namespace_created', 'Namespace creation time', ['namespace'])
kube_namespace_status_phase = Gauge('kube_namespace_status_phase', 'Namespace phase', ['namespace', 'phase'])

def collect_metrics():
    """收集 Kubernetes 指标"""
    try:
        # 加载 Kubernetes 配置
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()
        batch_v1 = client.BatchV1Api()
        
        logger.info("开始收集指标...")
        
        # 收集 Pod 指标
        pods = v1.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            namespace = pod.metadata.namespace
            pod_name = pod.metadata.name
            phase = pod.status.phase or "Unknown"
            node_name = pod.spec.node_name or ""
            pod_ip = pod.status.pod_ip or ""
            uid = pod.metadata.uid or ""
            
            # Pod info (关键指标)
            kube_pod_info.labels(
                namespace=namespace,
                pod=pod_name,
                node=node_name,
                pod_ip=pod_ip,
                uid=uid
            ).set(1)
            
            # Pod start time
            if pod.status.start_time:
                start_timestamp = pod.status.start_time.timestamp()
                kube_pod_start_time.labels(namespace=namespace, pod=pod_name).set(start_timestamp)
            
            # Pod creation time
            if pod.metadata.creation_timestamp:
                created_timestamp = pod.metadata.creation_timestamp.timestamp()
                kube_pod_created.labels(namespace=namespace, pod=pod_name).set(created_timestamp)
            
            # Pod completion time (for completed pods)
            if phase in ['Succeeded', 'Failed'] and pod.status.conditions:
                for condition in pod.status.conditions:
                    if condition.type == 'Ready' and condition.last_transition_time:
                        completion_timestamp = condition.last_transition_time.timestamp()
                        kube_pod_completion_time.labels(namespace=namespace, pod=pod_name).set(completion_timestamp)
                        break
            
            # Pod 状态
            phase_value = 1 if phase else 0
            kube_pod_status_phase.labels(namespace=namespace, pod=pod_name, phase=phase).set(phase_value)
            
            # Pod labels
            app_label = pod.metadata.labels.get('app', '') if pod.metadata.labels else ''
            kube_pod_labels.labels(
                namespace=namespace,
                pod=pod_name,
                label_app=app_label
            ).set(1)
            
            # 容器状态
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    container_name = container.name
                    ready = 1 if container.ready else 0
                    restarts = container.restart_count or 0
                    
                    kube_pod_container_status_ready.labels(
                        namespace=namespace, pod=pod_name, container=container_name
                    ).set(ready)
                    
                    kube_pod_container_status_restarts.labels(
                        namespace=namespace, pod=pod_name, container=container_name
                    ).set(restarts)
        
        # 收集 Deployment 指标
        deployments = apps_v1.list_deployment_for_all_namespaces(watch=False)
        for deployment in deployments.items:
            namespace = deployment.metadata.namespace
            deployment_name = deployment.metadata.name
            spec_replicas = deployment.spec.replicas or 0
            replicas = deployment.status.replicas or 0
            available_replicas = deployment.status.available_replicas or 0
            
            kube_deployment_spec_replicas.labels(
                namespace=namespace, deployment=deployment_name
            ).set(spec_replicas)
            
            kube_deployment_replicas.labels(
                namespace=namespace, deployment=deployment_name
            ).set(replicas)
            
            kube_deployment_replicas_available.labels(
                namespace=namespace, deployment=deployment_name
            ).set(available_replicas)
        
        # 收集 Node 指标
        nodes = v1.list_node(watch=False)
        for node in nodes.items:
            node_name = node.metadata.name
            kernel_version = node.status.node_info.kernel_version if node.status.node_info else ""
            os_image = node.status.node_info.os_image if node.status.node_info else ""
            container_runtime = node.status.node_info.container_runtime_version if node.status.node_info else ""
            
            # Node info
            kube_node_info.labels(
                node=node_name,
                kernel_version=kernel_version,
                os_image=os_image,
                container_runtime_version=container_runtime
            ).set(1)
            
            if node.status.conditions:
                for condition in node.status.conditions:
                    condition_type = condition.type
                    status = condition.status
                    status_value = 1 if status == "True" else 0
                    
                    kube_node_status_condition.labels(
                        node=node_name, condition=condition_type, status=status
                    ).set(status_value)
        
        # 收集 CronJob 指标
        cronjobs = batch_v1.list_cron_job_for_all_namespaces(watch=False)
        for cronjob in cronjobs.items:
            namespace = cronjob.metadata.namespace
            cronjob_name = cronjob.metadata.name
            
            # CronJob info
            kube_cronjob_info.labels(namespace=namespace, cronjob=cronjob_name).set(1)
            
            # Active jobs count
            active_count = len(cronjob.status.active) if cronjob.status.active else 0
            kube_cronjob_status_active.labels(namespace=namespace, cronjob=cronjob_name).set(active_count)
            
            # Suspend status
            suspend = 1 if cronjob.spec.suspend else 0
            kube_cronjob_spec_suspend.labels(namespace=namespace, cronjob=cronjob_name).set(suspend)
            
            # Last schedule time
            if cronjob.status.last_schedule_time:
                last_schedule_timestamp = cronjob.status.last_schedule_time.timestamp()
                kube_cronjob_status_last_schedule_time.labels(namespace=namespace, cronjob=cronjob_name).set(last_schedule_timestamp)
            
            # Next schedule time
            if cronjob.status.last_schedule_time:
                # 计算下次调度时间（简化版，假设从上次调度时间推算）
                from datetime import datetime, timezone
                import re
                
                # 解析 cron 表达式获取间隔（简化处理）
                schedule = cronjob.spec.schedule
                # 对于简单的 */N 格式
                match = re.match(r'\*/(\d+)', schedule.split()[0])
                if match:
                    interval_minutes = int(match.group(1))
                    last_schedule = cronjob.status.last_schedule_time
                    next_schedule = last_schedule.timestamp() + (interval_minutes * 60)
                    kube_cronjob_next_schedule_time.labels(namespace=namespace, cronjob=cronjob_name).set(next_schedule)
        
        # 收集 Service 指标
        services = v1.list_service_for_all_namespaces(watch=False)
        for service in services.items:
            namespace = service.metadata.namespace
            service_name = service.metadata.name
            cluster_ip = service.spec.cluster_ip or ""
            service_type = service.spec.type or "ClusterIP"
            
            kube_service_info.labels(
                namespace=namespace,
                service=service_name,
                cluster_ip=cluster_ip,
                type=service_type
            ).set(1)
        
        # 收集 Namespace 指标
        namespaces = v1.list_namespace(watch=False)
        for ns in namespaces.items:
            namespace = ns.metadata.name
            phase = ns.status.phase if ns.status and ns.status.phase else "Active"
            
            if ns.metadata.creation_timestamp:
                created_timestamp = ns.metadata.creation_timestamp.timestamp()
                kube_namespace_created.labels(namespace=namespace).set(created_timestamp)
            
            phase_value = 1 if phase == "Active" else 0
            kube_namespace_status_phase.labels(namespace=namespace, phase=phase).set(phase_value)
        
        logger.info("指标收集完成")
        
    except Exception as e:
        logger.error(f"收集指标时出错: {e}")

def main():
    """主函数"""
    logger.info("启动 Kube State Metrics Exporter")
    
    # 启动 HTTP 服务器
    start_http_server(8080)
    logger.info("Metrics 服务器已启动，端口: 8080")
    
    # 定期收集指标
    while True:
        collect_metrics()
        time.sleep(15)  # 每 15 秒收集一次

if __name__ == '__main__':
    main()
