"""
AI 辅助用户行为分析模块
自动统计各功能使用频率、用户偏好、检测模式分布，
为系统功能迭代提供数据支撑。
"""
import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

# 功能页面列表
FEATURE_PAGES = ['realtime', 'image', 'batch', 'video', 'settings', 'theme']
FEATURE_NAMES = {
    'realtime': '实时检测',
    'image': '图片检测',
    'batch': '批量检测',
    'video': '视频检测',
    'settings': '系统设置',
    'theme': '主题切换',
}


class UserAnalytics:
    """用户行为分析器"""

    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    # ── 数据库操作 ────────────────────────────────────

    def _ensure_tables(self):
        """确保分析相关表存在"""
        if not self.db_manager:
            return
        conn = self.db_manager._get_conn()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                feature TEXT NOT NULL,
                session_id TEXT,
                duration_ms INTEGER DEFAULT 0,
                metadata TEXT
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feature_usage_feature
            ON feature_usage(feature)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feature_usage_timestamp
            ON feature_usage(timestamp)
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                start_time DATETIME,
                end_time DATETIME,
                total_detections INTEGER DEFAULT 0,
                features_used TEXT,
                dominant_emotion TEXT,
                avg_confidence REAL DEFAULT 0,
                device_info TEXT
            )
        ''')

        conn.commit()

    def log_feature_usage(self, feature: str, session_id: str = '',
                          duration_ms: int = 0, metadata: Dict = None):
        """记录功能使用事件"""
        if feature not in FEATURE_PAGES:
            return
        if not self.db_manager:
            return

        try:
            self.db_manager._execute('''
                INSERT INTO feature_usage (feature, session_id, duration_ms, metadata)
                VALUES (?, ?, ?, ?)
            ''', (feature, session_id, duration_ms,
                  json.dumps(metadata or {}, ensure_ascii=False)))
        except Exception as e:
            logger.debug(f"记录功能使用失败: {e}")

    def log_session(self, session_id: str, device_info: str = ''):
        """记录会话开始"""
        if not self.db_manager:
            return
        try:
            self.db_manager._execute('''
                INSERT OR IGNORE INTO session_stats (session_id, start_time, device_info)
                VALUES (?, datetime('now'), ?)
            ''', (session_id, device_info))
        except Exception as e:
            logger.debug(f"记录会话失败: {e}")

    def update_session(self, session_id: str, detections: int = 0,
                       features: List[str] = None, emotion: str = '',
                       confidence: float = 0.0):
        """更新会话统计"""
        if not self.db_manager or not session_id:
            return
        try:
            self.db_manager._execute('''
                UPDATE session_stats SET
                    end_time = datetime('now'),
                    total_detections = total_detections + ?,
                    features_used = ?,
                    dominant_emotion = CASE WHEN ? != '' THEN ? ELSE dominant_emotion END,
                    avg_confidence = (avg_confidence + ?) / 2.0
                WHERE session_id = ?
            ''', (detections, json.dumps(features or [], ensure_ascii=False),
                  emotion, emotion, confidence, session_id))
        except Exception as e:
            logger.debug(f"更新会话失败: {e}")

    # ── 分析接口 ──────────────────────────────────────

    def get_feature_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取各功能使用统计"""
        if not self.db_manager:
            return self._empty_stats()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        try:
            conn = self.db_manager._get_conn()
            cursor = conn.cursor()

            # 功能使用频次
            cursor.execute('''
                SELECT feature, COUNT(*) as count
                FROM feature_usage
                WHERE timestamp >= ?
                GROUP BY feature ORDER BY count DESC
            ''', (cutoff,))
            feature_counts = {row['feature']: row['count']
                              for row in cursor.fetchall()}

            # 总使用次数
            cursor.execute(
                'SELECT COUNT(*) FROM feature_usage WHERE timestamp >= ?', (cutoff,))
            total_usage = cursor.fetchone()[0]

            # 每日趋势
            cursor.execute('''
                SELECT DATE(timestamp) as day, COUNT(*) as count
                FROM feature_usage
                WHERE timestamp >= ?
                GROUP BY day ORDER BY day
            ''', (cutoff,))
            daily_trend = [{'date': row['day'], 'count': row['count']}
                           for row in cursor.fetchall()]

            # 会话数
            cursor.execute('''
                SELECT COUNT(*) FROM session_stats
                WHERE start_time >= ?
            ''', (cutoff,))
            session_count = cursor.fetchone()[0]

            # 来源分布（从 detection_history 统计）
            cursor.execute('''
                SELECT source, COUNT(*) as count
                FROM detection_history
                WHERE timestamp >= ? AND source != ''
                GROUP BY source ORDER BY count DESC
            ''', (cutoff,))
            source_distribution = {row['source']: row['count']
                                   for row in cursor.fetchall()}

            return {
                'feature_usage': {FEATURE_NAMES.get(k, k): v
                                  for k, v in feature_counts.items()},
                'total_usage': total_usage,
                'daily_trend': daily_trend,
                'session_count': session_count,
                'source_distribution': source_distribution,
                'period_days': days,
            }

        except Exception as e:
            logger.error(f"获取功能统计失败: {e}")
            return self._empty_stats()

    def get_emotion_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """情绪趋势分析（基于检测历史）"""
        if not self.db_manager:
            return {}

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        try:
            conn = self.db_manager._get_conn()
            cursor = conn.cursor()

            # 各情绪占比
            cursor.execute('''
                SELECT dominant_emotion, COUNT(*) as count
                FROM detection_history
                WHERE timestamp >= ? AND dominant_emotion IS NOT NULL
                GROUP BY dominant_emotion ORDER BY count DESC
            ''', (cutoff,))
            emotion_dist = {row['dominant_emotion']: row['count']
                            for row in cursor.fetchall()}

            # 每日主导情绪变化
            cursor.execute('''
                SELECT DATE(timestamp) as day,
                       dominant_emotion,
                       COUNT(*) as count
                FROM detection_history
                WHERE timestamp >= ? AND dominant_emotion IS NOT NULL
                GROUP BY day, dominant_emotion
                ORDER BY day
            ''', (cutoff,))
            daily_emotions = {}
            for row in cursor.fetchall():
                day = row['day']
                if day not in daily_emotions:
                    daily_emotions[day] = {}
                daily_emotions[day][row['dominant_emotion']] = row['count']

            return {
                'emotion_distribution': emotion_dist,
                'daily_emotion_trend': daily_emotions,
                'total': sum(emotion_dist.values()),
            }

        except Exception as e:
            logger.error(f"情绪趋势分析失败: {e}")
            return {}

    def get_insights(self, days: int = 30) -> List[Dict[str, str]]:
        """生成可读洞察报告"""
        insights = []
        stats = self.get_feature_stats(days)

        if not stats or stats['total_usage'] == 0:
            insights.append({
                'type': 'info',
                'message': '数据不足，请多使用系统以生成分析洞察',
            })
            return insights

        total = stats['total_usage']
        usage = stats['feature_usage']

        # 最常用功能
        if usage:
            top_feature = max(usage, key=usage.get)
            insights.append({
                'type': 'highlight',
                'message': f'最受欢迎功能：{top_feature}（使用{usage[top_feature]}次）',
                'feature': top_feature,
            })

        # 活动天数
        trend = stats.get('daily_trend', [])
        active_days = len(trend)
        insights.append({
            'type': 'info',
            'message': f'近{days}天活跃{active_days}天，共{total}次检测',
            'value': f'{active_days}/{days}',
        })

        # 情绪分布
        emotion_analysis = self.get_emotion_trend_analysis(days)
        dist = emotion_analysis.get('emotion_distribution', {})
        if dist:
            top_emotion = max(dist, key=dist.get)
            insights.append({
                'type': 'emotion',
                'message': f'常见情绪：{top_emotion}（出现{dist[top_emotion]}次）',
                'emotion': top_emotion,
            })

        # 会话活跃度
        session_count = stats.get('session_count', 0)
        if session_count > 0:
            avg_per_session = round(total / session_count, 1)
            insights.append({
                'type': 'info',
                'message': f'每会话平均{avg_per_session}次检测，共{session_count}次会话',
                'value': str(avg_per_session),
            })

        return insights

    def _empty_stats(self) -> Dict:
        return {
            'feature_usage': {},
            'total_usage': 0,
            'daily_trend': [],
            'session_count': 0,
            'period_days': 30,
        }
