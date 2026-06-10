import os
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from application.service.mineru_client import mineru
from application.service.document_processor import (
    get_unprocessed_files,
    mark_processed,
    mark_failed,
    chunk_and_store,
)

logger = logging.getLogger(__name__)
load_dotenv()

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_SOURCE_DIR = os.path.join(_BASE, os.getenv("KNOWLEDGE_SOURCE_DIR", "knowledge_files"))
_TASKS_FILE = os.path.join(_SOURCE_DIR, ".pending_tasks.json")


def _load_pending_tasks() -> dict:
    if not os.path.exists(_TASKS_FILE):
        return {}
    with open(_TASKS_FILE, "r") as f:
        return json.load(f)


def _save_pending_tasks(tasks: dict):
    os.makedirs(_SOURCE_DIR, exist_ok=True)
    with open(_TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def _remove_pending_task(task_id: str):
    tasks = _load_pending_tasks()
    tasks.pop(task_id, None)
    _save_pending_tasks(tasks)


class IngestionScheduler:
    def __init__(self):
        self.source_dir = _SOURCE_DIR
        self.scheduler = BackgroundScheduler(daemon=True)
        os.makedirs(self.source_dir, exist_ok=True)

    def start(self):
        if self.scheduler.running:
            return

        # 定时任务1: 每分钟的第0-55秒，每15秒执行一次
        self.scheduler.add_job(
            self._submit_new_files,
            CronTrigger(second="*/15"),
            id="submit_files",
            name="提交新文件",
            replace_existing=True,
        )

        # 定时任务2: 每分钟的第0-55秒，每5秒执行一次
        self.scheduler.add_job(
            self._poll_running_tasks,
            CronTrigger(second="*/5"),
            id="poll_tasks",
            name="轮询解析任务",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(f"调度器已启动: 提交 */15 * * * * * | 轮询 */5 * * * * * | 目录: {self.source_dir}")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    # ==================== 定时任务1: 提交新文件 ====================

    def _submit_new_files(self):
        try:
            files = get_unprocessed_files(self.source_dir)
            pending = _load_pending_tasks()
            pending_paths = {info["file_path"] for info in pending.values()}
            files = [f for f in files if f not in pending_paths ]

            for file_path in files:

                logger.info(f"提交新文件: {os.path.basename(file_path)}")
                task_id = mineru.submit_task(file_path)
                if not task_id:
                    mark_failed(file_path)
                    continue
                pending[task_id] = {
                    "file_path": file_path,
                    "submitted_at": datetime.now(timezone.utc).isoformat(),
                }
                _save_pending_tasks(pending)
                logger.info(f"已提交 {os.path.basename(file_path)} → task_id: {task_id}")
        except Exception as e:
            logger.exception(f"提交任务出错: {e}")

    # ==================== 定时任务2: 轮询任务状态 ====================

    def _poll_running_tasks(self):
        try:
            pending = _load_pending_tasks()
            if not pending:
                return

            for task_id, info in list(pending.items()):
                file_path = info["file_path"]
                try:
                    status = mineru.get_task_status(task_id)
                    s = status.get("status")

                    if s == "completed":
                        self._handle_completed(task_id, file_path)
                    elif s == "failed":
                        logger.error(f"解析失败: {os.path.basename(file_path)}, {status.get('error')}")
                        _remove_pending_task(task_id)
                        mark_failed(file_path)
                except Exception as e:
                    logger.warning(f"查询任务 {task_id} 失败: {e}")
        except Exception as e:
            logger.exception(f"轮询任务出错: {e}")

    def _handle_completed(self, task_id: str, file_path: str):
        logger.info(f"解析完成: {os.path.basename(file_path)}")
        result = mineru.get_result(task_id)
        if not result:
            _remove_pending_task(task_id)
            mark_failed(file_path)
            return

        md_content = None
        for _, data in result.get("results", {}).items():
            md_content = data.get("md_content")
            break

        if not md_content:
            logger.warning(f"文件 {file_path} 解析结果无 md_content")
            _remove_pending_task(task_id)
            mark_failed(file_path)
            return

        chunk_count = chunk_and_store(md_content, file_path)
        _remove_pending_task(task_id)
        if chunk_count > 0:
            mark_processed(file_path)
            logger.info(f"入库完成: {os.path.basename(file_path)}, {chunk_count} 条")
        else:
            mark_failed(file_path)


# 全局调度器实例
scheduler = IngestionScheduler()
