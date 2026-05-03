"""
AI 推理效率优化引擎
通过动态推理策略降低资源占用，提升低配设备流畅度。
"""
import logging
import time
import numpy as np
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class DynamicInferenceOptimizer:
    """
    动态推理优化器

    策略:
    1. 自适应帧跳过 - 根据处理耗时动态调整检测频率
    2. 动态图像质量 - GPU 负载高时降低发送分辨率
    3. 智能检测缩放 - 无面部变动时复用上一帧结果
    4. 推理后端切换 - 自动选择 CPU/GPU 最优方案
    """

    def __init__(self):
        self.enabled = True

        # 帧跳过参数
        self.current_skip = 1          # 当前每隔几帧做检测
        self.min_skip = 1
        self.max_skip = 4
        self.target_latency_ms = 80    # 目标单帧处理延迟
        self.latency_history = []      # 最近延迟记录

        # 图像质量参数
        self.send_width = 160
        self.send_height = 120
        self.min_width = 80
        self.max_width = 320

        # 运动检测
        self._prev_face_center = None
        self._prev_face_size = None
        self._motion_threshold = 20    # 像素位移阈值

        # GPU 监控
        self._gpu_high_load = False
        self._gpu_check_interval = 5.0  # 每 5s 检查一次
        self._last_gpu_check = 0

        # 统计数据
        self.total_frames_skipped = 0
        self.total_frames_processed = 0

    # ── 帧跳过策略 ───────────────────────────────────

    def should_skip_frame(self, current_time: float, proc_elapsed_ms: float = 0) -> bool:
        """根据当前处理延迟决定是否跳过此帧"""
        if not self.enabled:
            return False

        # 记录延迟历史（滑动窗口）
        if proc_elapsed_ms > 0:
            self.latency_history.append(proc_elapsed_ms)
            if len(self.latency_history) > 10:
                self.latency_history.pop(0)

        # 根据平均延迟调整跳过率
        if self.latency_history:
            avg_latency = np.mean(self.latency_history)
            if avg_latency > self.target_latency_ms * 1.5:
                self.current_skip = min(self.max_skip, self.current_skip + 1)
            elif avg_latency < self.target_latency_ms * 0.7:
                self.current_skip = max(self.min_skip, self.current_skip - 1)

        # 跳过决策
        self.total_frames_processed += 1
        if self.current_skip > 1:
            should_skip = (self.total_frames_processed % self.current_skip) != 0
            if should_skip:
                self.total_frames_skipped += 1
            return should_skip

        return False

    # ── 动态图像质量 ─────────────────────────────────

    def optimize_send_resolution(self, gpu_memory_mb: float = 0) -> tuple:
        """
        根据 GPU 负载动态调整发送分辨率
        返回 (width, height)
        """
        if gpu_memory_mb > 0:
            # 显存使用超过 80% 时降级
            try:
                import pynvml
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                usage_ratio = mem_info.used / mem_info.total

                if usage_ratio > 0.8:
                    self.send_width = max(self.min_width, self.send_width - 40)
                    self.send_height = int(self.send_width * 0.75)
                elif usage_ratio < 0.4 and self.send_width < self.max_width:
                    self.send_width = min(self.max_width, self.send_width + 40)
                    self.send_height = int(self.send_width * 0.75)
            except Exception:
                pass

        return (self.send_width, self.send_height)

    # ── 运动检测复用 ─────────────────────────────────

    def check_motion(self, faces: list) -> bool:
        """
        检测人脸是否大幅移动
        无移动时返回 True（可复用上一帧结果）
        """
        if not faces:
            self._prev_face_center = None
            self._prev_face_size = None
            return False  # 无人脸，必须检测

        face = faces[0]
        x, y, w, h = face['bbox']
        center = (x + w // 2, y + h // 2)
        size = w * h

        if self._prev_face_center is not None:
            dx = abs(center[0] - self._prev_face_center[0])
            dy = abs(center[1] - self._prev_face_center[1])
            ds = abs(size - self._prev_face_size)

            # 位移和尺寸变化都很小 → 可复用
            if dx < self._motion_threshold and dy < self._motion_threshold \
               and ds < self._prev_face_size * 0.1:
                return True

        self._prev_face_center = center
        self._prev_face_size = size
        return False

    # ── 推理配置生成 ─────────────────────────────────

    def get_inference_config(self) -> Dict:
        """返回当前推理配置（供前端参考）"""
        return {
            'frame_skip': self.current_skip,
            'send_width': self.send_width,
            'send_height': self.send_height,
            'enabled': self.enabled,
            'total_skipped': self.total_frames_skipped,
            'total_processed': self.total_frames_processed,
        }

    # ── ONNX 会话优化 ────────────────────────────────

    @staticmethod
    def optimize_onnx_session(session_options, use_fp16: bool = True):
        """
        配置 ONNX Runtime 会话选项以优化性能
        """
        import onnxruntime as ort
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.enable_cpu_mem_arena = False
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        if use_fp16:
            session_options.add_session_config_entry('session.enable_fp16', '1')
        return session_options
