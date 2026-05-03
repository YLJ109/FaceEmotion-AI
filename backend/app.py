""" 
AI情感检测系统 - FastAPI后端 (V3.0.0)
模块化架构：路由、服务、模型完全解耦
"""
from api import register_all_routes
from optimizer.dynamic_inference import DynamicInferenceOptimizer
from analytics.user_analytics import UserAnalytics
from multimodal.voice_analyzer import VoiceAnalyzer
from adaptation.active_learner import AdaptiveLearner
from models.emotion_classifier_onnx import EmotionClassifierONNX
from models.detector import FaceDetector
from database import DatabaseManager
from config import ConfigManager
from constants import LOGGING_CONFIG
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
from contextlib import asynccontextmanager

# 抑制废弃警告
warnings.filterwarnings('ignore', message='.*pynvml.*deprecated.*')

# ==================== 导入核心模块 ====================

# ==================== 运行时环境配置 ====================
_cudnn_bin = Path(__file__).parent / ".venv" / "Lib" / \
    "site-packages" / "nvidia" / "cudnn" / "bin"
if _cudnn_bin.exists():
    os.environ.setdefault("PATH", "")
    if str(_cudnn_bin.resolve()) not in os.environ["PATH"]:
        os.environ["PATH"] = str(_cudnn_bin.resolve()) + \
            os.pathsep + os.environ["PATH"]
_cuda_bin = Path(__file__).parent / ".venv" / "Lib" / \
    "site-packages" / "nvidia" / "cuda_runtime" / "bin"
if _cuda_bin.exists():
    if str(_cuda_bin.resolve()) not in os.environ["PATH"]:
        os.environ["PATH"] = str(_cuda_bin.resolve()) + \
            os.pathsep + os.environ["PATH"]

logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# ==================== 全局实例管理器 ====================
config_manager = ConfigManager()
db_manager = DatabaseManager()
face_detector = None
emotion_model = None
adaptive_learner = None
voice_analyzer = None
user_analytics = None
inference_optimizer = None
# 全局共享线程池
_shared_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# ==================== Lifespan 事件处理器 ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭的生命周期管理"""
    global face_detector, emotion_model, adaptive_learner, voice_analyzer, user_analytics, inference_optimizer

    logger.info("=" * 60)
    logger.info("🚀 AI情感检测系统 V3.0.0 启动中...")
    logger.info("=" * 60)

    # GPU 检测
    try:
        import pynvml as nvidia_smi
        nvidia_smi.nvmlInit()
        device_count = nvidia_smi.nvmlDeviceGetCount()
        if device_count > 0:
            handle = nvidia_smi.nvmlDeviceGetHandleByIndex(0)
            gpu_name = nvidia_smi.nvmlDeviceGetName(handle)
            mem_info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
            logger.info(
                f"✅ GPU: {gpu_name} ({mem_info.total / 1024**3:.1f} GB)")
    except Exception:
        logger.info("⚠️ 无GPU可用")

    # 加载模型
    try:
        # ✅ 优化1: 启用ONNX RFB人脸检测器(更高精度)
        onnx_face_model_path = './models/version-RFB-320.onnx'
        use_onnx_detector = config_manager.get('use_onnx_face_detector', False)

        face_detector = FaceDetector(
            proto_file='./models/deploy.prototxt',
            model_file='./models/res10_300x300_ssd_iter_140000_fp16.caffemodel',
            onnx_model_path=onnx_face_model_path,
            use_onnx=use_onnx_detector
        )
        logger.info("✅ 人脸检测器加载成功")

        onnx_path = os.path.join(os.path.dirname(
            __file__), 'models', 'emotion_model.onnx')
        if not os.path.exists(onnx_path):
            raise RuntimeError(f"ONNX模型不存在: {onnx_path}")

        emotion_model = EmotionClassifierONNX(onnx_path)
        logger.info("✅ ONNX情感分类器加载成功")
    except Exception as e:
        logger.error(f"❌ 模型加载失败: {e}")
        raise

    # 初始化数据库
    db_manager.init_db()
    logger.info("✅ 数据库初始化完成")

    # 初始化 AI 引擎
    adaptive_learner = AdaptiveLearner(db_manager)
    adaptive_learner.load_from_database()
    logger.info("✅ AI自适应学习引擎就绪")

    voice_analyzer = VoiceAnalyzer()
    logger.info("✅ AI多模态语音分析器就绪")

    user_analytics = UserAnalytics(db_manager)
    user_analytics._ensure_tables()
    logger.info("✅ AI用户行为分析器就绪")

    inference_optimizer = DynamicInferenceOptimizer()
    logger.info("✅ AI推理优化引擎就绪")
    logger.info("✅ AI生成式音乐引擎就绪")

    logger.info("=" * 60)
    logger.info("✅ 系统就绪！V3.0.0 模块化架构")
    logger.info("=" * 60)

    # 注册所有 API 路由 (在应用启动前完成)
    register_all_routes(
        app=app,
        config_manager=config_manager,
        db_manager=db_manager,
        face_detector=face_detector,
        emotion_model=emotion_model,
        adaptive_learner=adaptive_learner,
        voice_analyzer=voice_analyzer,
        user_analytics=user_analytics,
        inference_optimizer=inference_optimizer,
        executor=_shared_executor
    )
    logger.info("✅ 所有 API 路由已注册")

    yield  # 应用运行期间保持状态

    # 关闭时的清理工作
    logger.info("🛑 系统关闭中...")
    _shared_executor.shutdown(wait=True)
    logger.info("✅ 系统已关闭")

# ==================== FastAPI 应用初始化 ====================
app = FastAPI(
    title="AI情感检测系统",
    description="基于深度学习的人脸情感识别系统 (V3.0.0 模块化架构)",
    version="3.0.0",
    lifespan=lifespan
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://localhost:3000", "http://localhost:8000",
        "http://127.0.0.1:5173", "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 慢请求监控中间件


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    elapsed = time.time() - start_time
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    if elapsed > 1.0:
        logger.warning(
            f"⏱ 慢请求 [{request.method}] {request.url.path} - {elapsed:.2f}s")
    return response

# 全局异常处理


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_traceback = traceback.format_exc()
    logger.error(f"❌ 全局异常: {exc}\n{error_traceback}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )

# 静态文件服务
app.mount("/static", StaticFiles(directory="data/screenshots"), name="static")

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 启动 Uvicorn 服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
