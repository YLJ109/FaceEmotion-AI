"""历史记录相关 API 路由"""
from fastapi import APIRouter, HTTPException
from database import DatabaseManager

router = APIRouter(prefix="/api/history", tags=["history"])

_db_manager = None


def init_history_router(db_manager: DatabaseManager):
    """初始化路由依赖"""
    global _db_manager
    _db_manager = db_manager


@router.get("")
async def get_history(limit: int = 50, offset: int = 0, type: str = None):
    """获取历史记录(分页)，支持按类型筛选"""
    history = _db_manager.get_history(limit, offset, detection_type=type)
    total = _db_manager.get_history_count(detection_type=type)

    # 获取各类型的统计数量
    type_counts = _db_manager.get_type_counts()

    return {
        "status": "success",
        "data": history,
        "total": total,
        "limit": limit,
        "offset": offset,
        "type_counts": type_counts  # 新增: 各类型数量统计
    }


@router.post("/save")
async def save_history(data: dict):
    """保存检测结果到历史记录"""
    try:
        detection_type = data.get('detection_type', 'unknown')
        results = data.get('results', [])
        source = data.get('source', '')
        image_path = data.get('image_path', '')
        image_type = data.get('image_type', '')
        thumbnail = data.get('thumbnail')

        # 新增：接收视频检测的额外字段
        dominant_emotion = data.get('dominant_emotion', 'neutral')
        confidence = data.get('confidence', 0.0)
        detected_faces = data.get('detected_faces', [])

        _db_manager.save_detection_result(
            detection_type=detection_type,
            results=results,
            source=source,
            image_path=image_path,
            image_type=image_type,
            thumbnail=thumbnail,
            dominant_emotion=dominant_emotion,
            confidence=confidence,
            detected_faces=detected_faces
        )
        return {"status": "success", "message": "历史记录已保存"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_history_stats():
    """获取历史记录统计信息"""
    stats = _db_manager.get_stats()
    total = _db_manager.get_history_count()
    return {
        "status": "success",
        "total_records": total,
        "stats": stats
    }


@router.delete("/type/{detection_type}")
async def delete_by_type(detection_type: str):
    """删除指定类型的所有历史记录"""
    try:
        deleted_count = _db_manager.delete_by_detection_type(detection_type)
        return {
            "status": "success",
            "message": f"已删除 {deleted_count} 条{detection_type}检测记录",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
