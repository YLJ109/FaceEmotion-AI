""" 
AI情感检测系统 - FastAPI后端 (V3.1.0)
模块化架构：路由、服务、模型完全解耦
"""
from api import register_all_routes
from optimizer.dynamic_inference import DynamicInferenceOptimizer
from analytics.user_analytics import UserAnalytics
from adaptation.active_learner import AdaptiveLearner
from models.detector import FaceDetector
from core.database import DatabaseManager
from core.config import ConfigManager
from core.constants import LOGGING_CONFIG
import traceback
import time
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from pathlib import Path
import os
import logging
import warnings
import concurrent.futures
import multiprocessing
from contextlib import asynccontextmanager

warnings.filterwarnings('ignore', message='.*pynvml.*deprecated.*')

_cudnn_bin = Path(__file__).parent / ".venv" / "Lib" / "site-packages" / "nvidia" / "cudnn" / "bin"
if _cudnn_bin.exists():
    os.environ.setdefault("PATH", "")
    if str(_cudnn_bin.resolve()) not in os.environ["PATH"]:
        os.environ["PATH"] = str(_cudnn_bin.resolve()) + os.pathsep + os.environ["PATH"]
_cuda_bin = Path(__file__).parent / ".venv" / "Lib" / "site-packages" / "nvidia" / "cuda_runtime" / "bin"
if _cuda_bin.exists():
    if str(_cuda_bin.resolve()) not in os.environ["PATH"]:
        os.environ["PATH"] = str(_cuda_bin.resolve()) + os.pathsep + os.environ["PATH"]

logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)
logging.getLogger('api.system').setLevel(logging.WARNING)
logging.getLogger('core.config').setLevel(logging.WARNING)

config_manager = ConfigManager()
db_manager = DatabaseManager()
face_detector = None
emotion_model = None
detection_service = None
adaptive_learner = None
user_analytics = None
inference_optimizer = None

cpu_count = multiprocessing.cpu_count()
_shared_executor = concurrent.futures.ThreadPoolExecutor(max_workers=min(cpu_count * 2, 8))
logger.info(f"线程池: {cpu_count} CPU核心, {min(cpu_count * 2, 8)} 工作线程")


# 初始化所有必需的目录
from core.init_dirs import init_directories

@asynccontextmanager
async def lifespan(app: FastAPI):
    global face_detector, emotion_model, detection_service, adaptive_learner, user_analytics, inference_optimizer

    # 启动时初始化所有必需的目录
    init_directories()

    logger.info("=" * 60)
    logger.info("AI情感检测系统 V3.1.0 启动中...")
    logger.info("=" * 60)

    try:
        import pynvml as nvidia_smi
        nvidia_smi.nvmlInit()
        device_count = nvidia_smi.nvmlDeviceGetCount()
        if device_count > 0:
            handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
            gpu_name = nvidia_smi.nvmlDeviceGetName(handle)
            mem_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
            logger.info(f"GPU: {gpu_name} ({mem_info.total / 1024**3:.1f} GB)")
    except Exception:
        logger.info("无GPU可用")

    perf_config = config_manager.get_performance_config()
    logger.info(f"性能模式: {perf_config.get('description', 'N/A')}")

    try:
        import time as _time

        logger.info("加载 SSD 人脸检测模型...")
        start_time = _time.time()
        use_gpu = perf_config.get('use_gpu', False)
        face_detector = FaceDetector(
            min_detection_confidence=0.5,
            max_num_faces=5,
            use_gpu=use_gpu
        )
        logger.info(f"SSD 人脸检测器加载完成 ({_time.time() - start_time:.2f}s)")

        logger.info("加载 ONNX 情绪识别模型...")
        start_time = _time.time()
        onnx_path = os.path.join(os.path.dirname(__file__), 'weights', 'final_model.onnx')
        from models.emotion_classifier_onnx import EmotionClassifierONNX
        emotion_model = EmotionClassifierONNX(onnx_path)
        logger.info(f"ONNX 情绪识别模型加载完成 ({_time.time() - start_time:.2f}s, 7种表情)")

        from services.detection_service import DetectionService
        detection_service = DetectionService(
            config_manager=config_manager,
            face_detector=face_detector,
            emotion_classifier=emotion_model
        )
        logger.info("检测服务初始化完成")
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        raise

    db_manager.init_db()
    logger.info("数据库初始化完成")

    from adaptation.active_learner import AdaptiveLearner
    adaptive_learner = AdaptiveLearner(db_manager)
    adaptive_learner.load_from_database()
    logger.info(f"自适应学习引擎就绪 ({adaptive_learner.total_corrections} 条反馈)")

    user_analytics = UserAnalytics(db_manager)
    user_analytics._ensure_tables()
    logger.info("用户行为分析器就绪")

    inference_optimizer = DynamicInferenceOptimizer()
    logger.info("推理优化引擎就绪")

    register_all_routes(
        app=app,
        config_manager=config_manager,
        db_manager=db_manager,
        face_detector=face_detector,
        emotion_model=emotion_model,
        detection_service=detection_service,
        adaptive_learner=adaptive_learner,
        user_analytics=user_analytics,
        inference_optimizer=inference_optimizer,
        executor=_shared_executor
    )
    logger.info("所有API路由已注册")

    logger.info("=" * 60)
    logger.info("系统就绪! V3.1.0")
    logger.info("=" * 60)

    yield

    logger.info("系统关闭中...")
    _shared_executor.shutdown(wait=True)
    logger.info("系统已关闭")


app = FastAPI(
    title="AI情感检测系统",
    description="基于深度学习的人脸情感识别系统 (V3.1.0)",
    version="3.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://localhost:8000",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    elapsed = time.time() - start_time
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    if elapsed > 1.0:
        logger.warning(f"慢请求 [{request.method}] {request.url.path} - {elapsed:.2f}s")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_traceback = traceback.format_exc()
    logger.error(f"全局异常: {exc}\n{error_traceback}")
    detail = str(exc) if config_manager.get('debug', False) else "服务器内部错误"
    return JSONResponse(status_code=500, content={"detail": detail, "type": type(exc).__name__})


app.mount("/static", StaticFiles(directory="data/screenshots"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
