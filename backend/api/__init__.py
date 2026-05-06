"""API 路由注册中心 - 统一管理所有路由模块"""
from fastapi import FastAPI
from core.config import ConfigManager
from core.database import DatabaseManager
from adaptation.active_learner import AdaptiveLearner
from analytics.user_analytics import UserAnalytics
from optimizer.dynamic_inference import DynamicInferenceOptimizer
import concurrent.futures


def register_all_routes(
    app: FastAPI,
    config_manager: ConfigManager,
    db_manager: DatabaseManager,
    face_detector,
    emotion_model,
    adaptive_learner: AdaptiveLearner,
    user_analytics: UserAnalytics,
    inference_optimizer: DynamicInferenceOptimizer,
    executor: concurrent.futures.ThreadPoolExecutor
):
    """注册所有 API 路由"""

    # 1. 导入路由模块
    from api.websocket import router as ws_router, init_ws_router
    from api.detection import router as detection_router, init_detection_router
    from api.history import router as history_router, init_history_router
    from api.ai_features import router as ai_router, init_ai_router
    from api.system import router as system_router, init_system_router

    # 2. 初始化各路由依赖
    init_ws_router(
        config_manager=config_manager,
        db_manager=db_manager,
        face_detector=face_detector,
        emotion_model=emotion_model,
        adaptive_learner=adaptive_learner,
        executor=executor
    )

    init_detection_router(
        face_detector=face_detector,
        emotion_model=emotion_model,
        db_manager=db_manager
    )

    init_history_router(db_manager=db_manager)

    init_ai_router(
        adaptive_learner=adaptive_learner,
        user_analytics=user_analytics,
        inference_optimizer=inference_optimizer,
        db_manager=db_manager
    )

    init_system_router(
        config_manager=config_manager,
        face_detector=face_detector,
        emotion_model=emotion_model,
        adaptive_learner=adaptive_learner,
        inference_optimizer=inference_optimizer
    )

    # 3. 注册路由到 FastAPI 应用
    app.include_router(ws_router)
    app.include_router(detection_router)
    app.include_router(history_router)
    app.include_router(ai_router)
    app.include_router(system_router)
