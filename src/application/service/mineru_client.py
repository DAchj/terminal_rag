import time
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class MineruClient:
    def __init__(self, base_url: str = "http://127.0.0.1:9998"):
        self.base_url = base_url.rstrip("/")

    def submit_task(self, file_path: str, lang_list: list[str] | None = None) -> str | None:
        """异步提交文件解析任务，返回 task_id"""
        with open(file_path, "rb") as f:
            resp = requests.post(
                f"{self.base_url}/tasks",
                files={"files": f},
                data={
                    "backend": "pipeline",
                    "lang_list": lang_list or ["ch"],
                    "return_md": True,
                },
            )
        if resp.status_code != 202:
            logger.error(f"提交任务失败 [{resp.status_code}]: {resp.text}")
            return None
        return resp.json()["task_id"]

    def get_task_status(self, task_id: str) -> dict:
        resp = requests.get(f"{self.base_url}/tasks/{task_id}")
        return resp.json()

    def wait_for_completion(self, task_id: str, poll_interval: float = 3.0, timeout: float = 300) -> Optional[dict]:
        """轮询等待任务完成，返回 task 完整信息"""
        start = time.time()
        while True:
            if time.time() - start > timeout:
                logger.error(f"任务 {task_id} 超时")
                return None
            status = self.get_task_status(task_id)
            s = status.get("status")
            if s == "completed":
                return status
            if s == "failed":
                logger.error(f"任务 {task_id} 失败: {status.get('error')}")
                return None
            time.sleep(poll_interval)

    def get_result(self, task_id: str) -> Optional[dict]:
        """获取解析结果中的 md_content"""
        resp = requests.get(f"{self.base_url}/tasks/{task_id}/result")
        if resp.status_code != 200:
            logger.error(f"获取结果失败 [{resp.status_code}]: {resp.text}")
            return None
        return resp.json()


mineru = MineruClient()
