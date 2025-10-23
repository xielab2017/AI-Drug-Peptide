#!/usr/bin/env python3
"""
AI-Drug Peptide - 工作流管理模块
包含工作流编排器、任务调度器、状态管理器和错误处理器
"""

import os
import json
import logging
import asyncio
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    """任务定义"""
    task_id: str
    name: str
    function: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 3600
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowState:
    """工作流状态"""
    workflow_id: str
    name: str
    status: WorkflowStatus
    tasks: Dict[str, Task] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowError(Exception):
    """工作流异常"""
    pass

class TaskError(Exception):
    """任务异常"""
    pass

class StateManager:
    """状态管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.state_dir = Path(self.config.get('state_dir', './data/state'))
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._states: Dict[str, WorkflowState] = {}
        self._lock = threading.Lock()
    
    def save_state(self, state: WorkflowState) -> bool:
        """保存工作流状态"""
        try:
            with self._lock:
                self._states[state.workflow_id] = state
                
                # 保存到文件
                state_file = self.state_dir / f"{state.workflow_id}.json"
                state_data = asdict(state)
                
                # 转换datetime对象
                for key, value in state_data.items():
                    if isinstance(value, datetime):
                        state_data[key] = value.isoformat()
                
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(state_data, f, default=str, indent=2, ensure_ascii=False)
                
                logger.debug(f"State saved for workflow {state.workflow_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save state for workflow {state.workflow_id}: {e}")
            return False
    
    def load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """加载工作流状态"""
        try:
            with self._lock:
                # 首先检查内存
                if workflow_id in self._states:
                    return self._states[workflow_id]
                
                # 从文件加载
                state_file = self.state_dir / f"{workflow_id}.json"
                if not state_file.exists():
                    return None
                
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                # 转换datetime对象
                for key, value in state_data.items():
                    if key in ['created_at', 'started_at', 'completed_at'] and value:
                        state_data[key] = datetime.fromisoformat(value)
                
                # 转换Task对象
                if 'tasks' in state_data:
                    tasks = {}
                    for task_id, task_data in state_data['tasks'].items():
                        # 转换Task的datetime字段
                        for dt_field in ['created_at', 'started_at', 'completed_at']:
                            if task_data.get(dt_field):
                                task_data[dt_field] = datetime.fromisoformat(task_data[dt_field])
                        
                        # 转换TaskStatus
                        if 'status' in task_data:
                            task_data['status'] = TaskStatus(task_data['status'])
                        
                        tasks[task_id] = Task(**task_data)
                    state_data['tasks'] = tasks
                
                # 转换WorkflowStatus
                if 'status' in state_data:
                    state_data['status'] = WorkflowStatus(state_data['status'])
                
                state = WorkflowState(**state_data)
                self._states[workflow_id] = state
                
                logger.debug(f"State loaded for workflow {workflow_id}")
                return state
                
        except Exception as e:
            logger.error(f"Failed to load state for workflow {workflow_id}: {e}")
            return None
    
    def delete_state(self, workflow_id: str) -> bool:
        """删除工作流状态"""
        try:
            with self._lock:
                # 从内存删除
                if workflow_id in self._states:
                    del self._states[workflow_id]
                
                # 从文件删除
                state_file = self.state_dir / f"{workflow_id}.json"
                if state_file.exists():
                    state_file.unlink()
                
                logger.debug(f"State deleted for workflow {workflow_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete state for workflow {workflow_id}: {e}")
            return False
    
    def list_workflows(self) -> List[str]:
        """列出所有工作流ID"""
        try:
            workflow_ids = []
            for state_file in self.state_dir.glob("*.json"):
                workflow_id = state_file.stem
                workflow_ids.append(workflow_id)
            return workflow_ids
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 5)
        self.error_notifications = self.config.get('error_notifications', {})
    
    def handle_task_error(self, task: Task, error: Exception) -> bool:
        """处理任务错误"""
        logger.error(f"Task {task.task_id} failed: {str(error)}")
        
        # 记录错误信息
        task.error = str(error)
        task.status = TaskStatus.FAILED
        
        # 检查是否需要重试
        if task.retry_count < task.max_retries:
            return self._schedule_retry(task)
        else:
            logger.error(f"Task {task.task_id} exceeded max retries")
            return False
    
    def _schedule_retry(self, task: Task) -> bool:
        """安排重试"""
        task.retry_count += 1
        task.status = TaskStatus.RETRYING
        task.error = None
        
        logger.info(f"Scheduling retry {task.retry_count}/{task.max_retries} for task {task.task_id}")
        
        # 延迟重试
        time.sleep(self.retry_delay * task.retry_count)
        
        return True
    
    def handle_workflow_error(self, workflow_id: str, error: Exception) -> None:
        """处理工作流错误"""
        logger.error(f"Workflow {workflow_id} failed: {str(error)}")
        
        # 发送错误通知
        self._send_error_notification(workflow_id, error)
    
    def _send_error_notification(self, workflow_id: str, error: Exception) -> None:
        """发送错误通知"""
        if not self.error_notifications.get('enabled', False):
            return
        
        try:
            notification_data = {
                'workflow_id': workflow_id,
                'error': str(error),
                'timestamp': datetime.now().isoformat(),
                'traceback': traceback.format_exc()
            }
            
            # 这里可以集成邮件、Slack等通知方式
            logger.info(f"Error notification sent for workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_workers = self.config.get('max_workers', 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._running_tasks: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def submit_task(self, task: Task) -> bool:
        """提交任务"""
        try:
            with self._lock:
                if task.task_id in self._running_tasks:
                    logger.warning(f"Task {task.task_id} is already running")
                    return False
                
                # 更新任务状态
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                
                # 提交到线程池
                future = self.executor.submit(self._execute_task, task)
                self._running_tasks[task.task_id] = future
                
                logger.info(f"Task {task.task_id} submitted")
                return True
                
        except Exception as e:
            logger.error(f"Failed to submit task {task.task_id}: {e}")
            return False
    
    def _execute_task(self, task: Task) -> Any:
        """执行任务"""
        try:
            logger.info(f"Executing task {task.task_id}: {task.name}")
            
            # 执行任务函数
            result = task.function(*task.args, **task.kwargs)
            
            # 更新任务状态
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            
            logger.info(f"Task {task.task_id} completed successfully")
            return result
            
        except Exception as e:
            # 错误处理
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"Task {task.task_id} failed: {e}")
            raise
            
        finally:
            # 清理运行中的任务记录
            with self._lock:
                if task.task_id in self._running_tasks:
                    del self._running_tasks[task.task_id]
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        try:
            with self._lock:
                if task_id in self._running_tasks:
                    future = self._running_tasks[task_id]
                    future.cancel()
                    del self._running_tasks[task_id]
                    
                    logger.info(f"Task {task_id} cancelled")
                    return True
                else:
                    logger.warning(f"Task {task_id} not found in running tasks")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        with self._lock:
            if task_id in self._running_tasks:
                future = self._running_tasks[task_id]
                if future.done():
                    return TaskStatus.COMPLETED if not future.cancelled() else TaskStatus.CANCELLED
                else:
                    return TaskStatus.RUNNING
        return None
    
    def shutdown(self):
        """关闭调度器"""
        self.executor.shutdown(wait=True)
        logger.info("Task scheduler shutdown")

class WorkflowOrchestrator:
    """工作流编排器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.state_manager = StateManager(config)
        self.task_scheduler = TaskScheduler(config)
        self.error_handler = ErrorHandler(config)
        self._workflows: Dict[str, WorkflowState] = {}
        self._lock = threading.Lock()
    
    def create_workflow(self, name: str, tasks: List[Task]) -> str:
        """创建工作流"""
        workflow_id = str(uuid.uuid4())
        
        # 验证任务依赖关系
        self._validate_dependencies(tasks)
        
        # 创建工作流状态
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            name=name,
            status=WorkflowStatus.CREATED,
            tasks={task.task_id: task for task in tasks}
        )
        
        # 保存状态
        self.state_manager.save_state(workflow_state)
        
        with self._lock:
            self._workflows[workflow_id] = workflow_state
        
        logger.info(f"Workflow {workflow_id} created with {len(tasks)} tasks")
        return workflow_id
    
    def _validate_dependencies(self, tasks: List[Task]) -> None:
        """验证任务依赖关系"""
        task_ids = {task.task_id for task in tasks}
        
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise WorkflowError(f"Task {task.task_id} depends on non-existent task {dep_id}")
    
    async def execute_workflow(self, workflow_id: str) -> WorkflowState:
        """执行工作流"""
        # 加载工作流状态
        workflow_state = self.state_manager.load_state(workflow_id)
        if not workflow_state:
            raise WorkflowError(f"Workflow {workflow_id} not found")
        
        try:
            # 更新工作流状态
            workflow_state.status = WorkflowStatus.RUNNING
            workflow_state.started_at = datetime.now()
            self.state_manager.save_state(workflow_state)
            
            logger.info(f"Starting workflow {workflow_id}")
            
            # 执行任务
            await self._execute_tasks(workflow_state)
            
            # 更新完成状态
            workflow_state.status = WorkflowStatus.COMPLETED
            workflow_state.completed_at = datetime.now()
            workflow_state.progress = 100.0
            
            self.state_manager.save_state(workflow_state)
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            return workflow_state
            
        except Exception as e:
            # 处理工作流错误
            workflow_state.status = WorkflowStatus.FAILED
            workflow_state.completed_at = datetime.now()
            self.state_manager.save_state(workflow_state)
            
            self.error_handler.handle_workflow_error(workflow_id, e)
            raise
    
    async def _execute_tasks(self, workflow_state: WorkflowState) -> None:
        """执行工作流中的任务"""
        completed_tasks = set()
        failed_tasks = set()
        
        while len(completed_tasks) + len(failed_tasks) < len(workflow_state.tasks):
            # 找到可以执行的任务
            ready_tasks = self._get_ready_tasks(workflow_state.tasks, completed_tasks, failed_tasks)
            
            if not ready_tasks:
                # 没有可执行的任务，检查是否有失败的任务
                if failed_tasks:
                    raise WorkflowError(f"Workflow blocked by failed tasks: {failed_tasks}")
                else:
                    # 所有任务都已完成
                    break
            
            # 并行执行可执行的任务
            task_futures = []
            for task in ready_tasks:
                if task.task_id not in completed_tasks and task.task_id not in failed_tasks:
                    future = asyncio.get_event_loop().run_in_executor(
                        None, self._execute_single_task, task
                    )
                    task_futures.append((task.task_id, future))
            
            # 等待任务完成
            for task_id, future in task_futures:
                try:
                    await future
                    completed_tasks.add(task_id)
                    logger.info(f"Task {task_id} completed")
                except Exception as e:
                    failed_tasks.add(task_id)
                    logger.error(f"Task {task_id} failed: {e}")
            
            # 更新进度
            total_tasks = len(workflow_state.tasks)
            completed_count = len(completed_tasks)
            workflow_state.progress = (completed_count / total_tasks) * 100
            self.state_manager.save_state(workflow_state)
    
    def _get_ready_tasks(self, tasks: Dict[str, Task], completed: set, failed: set) -> List[Task]:
        """获取可执行的任务"""
        ready_tasks = []
        
        for task in tasks.values():
            if task.task_id in completed or task.task_id in failed:
                continue
            
            # 检查依赖是否满足
            dependencies_met = all(
                dep_id in completed for dep_id in task.dependencies
            )
            
            if dependencies_met:
                ready_tasks.append(task)
        
        return ready_tasks
    
    def _execute_single_task(self, task: Task) -> Any:
        """执行单个任务"""
        try:
            logger.info(f"Executing task {task.task_id}: {task.name}")
            
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            # 执行任务
            result = task.function(*task.args, **task.kwargs)
            
            # 更新完成状态
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            
            return result
            
        except Exception as e:
            # 处理任务错误
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            
            # 尝试重试
            if self.error_handler.handle_task_error(task, e):
                # 重试任务
                return self._execute_single_task(task)
            else:
                raise
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """暂停工作流"""
        workflow_state = self.state_manager.load_state(workflow_id)
        if not workflow_state:
            return False
        
        workflow_state.status = WorkflowStatus.PAUSED
        self.state_manager.save_state(workflow_state)
        
        logger.info(f"Workflow {workflow_id} paused")
        return True
    
    def resume_workflow(self, workflow_id: str) -> bool:
        """恢复工作流"""
        workflow_state = self.state_manager.load_state(workflow_id)
        if not workflow_state:
            return False
        
        if workflow_state.status != WorkflowStatus.PAUSED:
            logger.warning(f"Workflow {workflow_id} is not paused")
            return False
        
        # 异步恢复工作流
        asyncio.create_task(self.execute_workflow(workflow_id))
        
        logger.info(f"Workflow {workflow_id} resumed")
        return True
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """取消工作流"""
        workflow_state = self.state_manager.load_state(workflow_id)
        if not workflow_state:
            return False
        
        # 取消所有运行中的任务
        for task in workflow_state.tasks.values():
            if task.status == TaskStatus.RUNNING:
                self.task_scheduler.cancel_task(task.task_id)
                task.status = TaskStatus.CANCELLED
        
        workflow_state.status = WorkflowStatus.CANCELLED
        workflow_state.completed_at = datetime.now()
        self.state_manager.save_state(workflow_state)
        
        logger.info(f"Workflow {workflow_id} cancelled")
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowState]:
        """获取工作流状态"""
        return self.state_manager.load_state(workflow_id)
    
    def list_workflows(self) -> List[str]:
        """列出所有工作流"""
        return self.state_manager.list_workflows()
    
    def cleanup_workflows(self, older_than_days: int = 7) -> int:
        """清理旧工作流"""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        cleaned_count = 0
        
        for workflow_id in self.list_workflows():
            workflow_state = self.state_manager.load_state(workflow_id)
            if workflow_state and workflow_state.created_at < cutoff_date:
                if self.state_manager.delete_state(workflow_id):
                    cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old workflows")
        return cleaned_count

# 工作流管理工厂类
class WorkflowManagerFactory:
    """工作流管理器工厂"""
    
    @staticmethod
    def create_orchestrator(config: Dict[str, Any] = None) -> WorkflowOrchestrator:
        """创建工作流编排器"""
        return WorkflowOrchestrator(config)
    
    @staticmethod
    def create_state_manager(config: Dict[str, Any] = None) -> StateManager:
        """创建状态管理器"""
        return StateManager(config)
    
    @staticmethod
    def create_task_scheduler(config: Dict[str, Any] = None) -> TaskScheduler:
        """创建任务调度器"""
        return TaskScheduler(config)
    
    @staticmethod
    def create_error_handler(config: Dict[str, Any] = None) -> ErrorHandler:
        """创建错误处理器"""
        return ErrorHandler(config)

# 使用示例
if __name__ == "__main__":
    # 配置示例
    config = {
        'state_dir': './data/state',
        'max_workers': 4,
        'max_retries': 3,
        'retry_delay': 5,
        'error_notifications': {
            'enabled': True
        }
    }
    
    # 创建工作流管理器
    orchestrator = WorkflowManagerFactory.create_orchestrator(config)
    
    # 定义示例任务
    def task_1():
        print("Executing task 1")
        time.sleep(2)
        return "Task 1 result"
    
    def task_2():
        print("Executing task 2")
        time.sleep(1)
        return "Task 2 result"
    
    def task_3():
        print("Executing task 3")
        time.sleep(1)
        return "Task 3 result"
    
    # 创建任务
    tasks = [
        Task(
            task_id="task_1",
            name="First Task",
            function=task_1
        ),
        Task(
            task_id="task_2",
            name="Second Task",
            function=task_2,
            dependencies=["task_1"]
        ),
        Task(
            task_id="task_3",
            name="Third Task",
            function=task_3,
            dependencies=["task_1"]
        )
    ]
    
    # 创建工作流
    workflow_id = orchestrator.create_workflow("Example Workflow", tasks)
    print(f"Created workflow: {workflow_id}")
    
    # 执行工作流
    async def run_workflow():
        try:
            result = await orchestrator.execute_workflow(workflow_id)
            print(f"✓ Workflow completed: {result.status.value}")
            print(f"Progress: {result.progress:.1f}%")
        except Exception as e:
            print(f"✗ Workflow failed: {e}")
    
    # 运行异步工作流
    asyncio.run(run_workflow())
