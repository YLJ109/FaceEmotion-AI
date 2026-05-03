"""数据库管理 - SQLite连接池优化版"""
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器 - 使用持久连接+写事务合并"""

    def __init__(self, db_path='data/emotion.db'):
        self.db_path = db_path
        Path('data').mkdir(exist_ok=True)
        self._conn = None  # 延迟初始化持久连接
        # ✅ 新增: 统计缓存
        self._stats_cache = None
        self._stats_cache_time = 0
        self._stats_cache_ttl = 300  # 5分钟缓存

    def _get_conn(self):
        """获取持久连接（check_same_thread=False允许跨线程）"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _execute(self, sql: str, params=()):
        """便捷执行方法"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor

    def init_db(self):
        """初始化数据库表"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # 扩展 detection_history 表，添加更多字段
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                detection_type TEXT,
                source TEXT DEFAULT '',
                image_path TEXT DEFAULT '',
                image_type TEXT DEFAULT '',
                thumbnail TEXT,
                results TEXT,
                detected_faces TEXT,
                dominant_emotion TEXT,
                confidence REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                emotion TEXT,
                predicted_emotion TEXT,
                correct_emotion TEXT,
                feedback_type TEXT,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_detections INTEGER DEFAULT 0,
                emotion_counts TEXT,
                avg_confidence REAL
            )
        ''')

        # 索引优化
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_timestamp
            ON detection_history(timestamp DESC)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feedback_timestamp
            ON user_feedback(timestamp DESC)
        ''')

        # ✅ 新增: 关键查询字段索引（性能优化）
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_detection_type
            ON detection_history(detection_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_dominant_emotion
            ON detection_history(dominant_emotion)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_confidence
            ON detection_history(confidence)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_compound
            ON detection_history(detection_type, timestamp DESC)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feature_usage_session
            ON feature_usage(session_id)
        ''')

        # === 数据库迁移：为旧表添加缺失字段 ===
        self._migrate_database(cursor)

        # === 新增表：功能使用统计 ===
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                feature TEXT NOT NULL,
                session_id TEXT DEFAULT '',
                duration_ms INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feature_usage_feature
            ON feature_usage(feature)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_feature_usage_ts
            ON feature_usage(timestamp)
        ''')

        # === 新增表：会话统计 ===
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                start_time DATETIME,
                end_time DATETIME,
                total_detections INTEGER DEFAULT 0,
                features_used TEXT DEFAULT '[]',
                dominant_emotion TEXT DEFAULT '',
                avg_confidence REAL DEFAULT 0.0,
                device_info TEXT DEFAULT ''
            )
        ''')

        # === 新增表：自适应学习日志 ===
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT DEFAULT '',
                raw_scores TEXT,
                calibrated_scores TEXT,
                dominant_before TEXT,
                dominant_after TEXT,
                calibration_strength REAL DEFAULT 0.0
            )
        ''')

        conn.commit()
        logger.info("✅ 数据库初始化完成（含分析表）")

    def _migrate_database(self, cursor):
        """数据库迁移：检查并添加缺失的字段"""
        try:
            # 检查 detection_history 表的字段
            cursor.execute('PRAGMA table_info(detection_history)')
            columns = [row[1] for row in cursor.fetchall()]

            # 添加缺失的字段（SQLite 限制：不能添加带 CURRENT_TIMESTAMP 默认值的列）
            if 'created_at' not in columns:
                logger.info('添加 created_at 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN created_at DATETIME
                ''')

            if 'detected_faces' not in columns:
                logger.info('添加 detected_faces 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN detected_faces TEXT
                ''')

            if 'dominant_emotion' not in columns:
                logger.info('添加 dominant_emotion 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN dominant_emotion TEXT
                ''')

            if 'confidence' not in columns:
                logger.info('添加 confidence 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN confidence REAL
                ''')

            if 'thumbnail' not in columns:
                logger.info('添加 thumbnail 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN thumbnail TEXT
                ''')

            if 'image_type' not in columns:
                logger.info('添加 image_type 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN image_type TEXT DEFAULT ''
                ''')

            if 'source' not in columns:
                logger.info('添加 source 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN source TEXT DEFAULT ''
                ''')

            if 'image_path' not in columns:
                logger.info('添加 image_path 字段到 detection_history 表')
                cursor.execute('''
                    ALTER TABLE detection_history 
                    ADD COLUMN image_path TEXT DEFAULT ''
                ''')

            logger.info('数据库迁移完成')
        except Exception as e:
            logger.error(f'数据库迁移失败: {e}')

    def save_detection_result(self, detection_type: str, results: List[Dict], source: str = '',
                              image_path: str = '', image_type: str = '', thumbnail: str = None,
                              dominant_emotion: str = None, confidence: float = None, detected_faces: List[Dict] = None):
        """保存检测结果（增强版）

        Args:
            detection_type: 检测类型
            results: 检测结果
            source: 来源
            image_path: 图片路径
            image_type: 图片类型
            thumbnail: 缩略图
            dominant_emotion: 主导情绪（可选，如果不提供则从 results 中提取）
            confidence: 置信度（可选，如果不提供则从 results 中提取）
            detected_faces: 检测到的人脸数据（可选，如果不提供则从 results 中提取）
        """
        # 如果没有提供 dominant_emotion 和 confidence，则从 results 中提取
        if dominant_emotion is None or confidence is None:
            max_confidence = 0
            extracted_emotion = None

            if results:
                for r in results:
                    conf = r.get('confidence', 0)
                    if conf > max_confidence:
                        max_confidence = conf
                        extracted_emotion = r.get('emotion')

            if dominant_emotion is None:
                dominant_emotion = extracted_emotion or 'neutral'
            if confidence is None:
                confidence = max_confidence

        # 如果没有提供 detected_faces，则从 results 中提取
        if detected_faces is None:
            detected_faces = results if results else []

        # 将人脸数据序列化为 JSON
        detected_faces_json = json.dumps(
            detected_faces, ensure_ascii=False) if detected_faces else '[]'

        self._execute('''
            INSERT INTO detection_history (detection_type, source, image_path, image_type, thumbnail, 
                                          results, detected_faces, dominant_emotion, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+8 hours'))
        ''', (detection_type, source, image_path, image_type, thumbnail,
              json.dumps(results, ensure_ascii=False), detected_faces_json, dominant_emotion, confidence))

    def save_feedback(self, feedback: Dict):
        """保存用户反馈"""
        self._execute('''
            INSERT INTO user_feedback (emotion, predicted_emotion, correct_emotion, feedback_type, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            feedback.get('emotion'),
            feedback.get('predicted_emotion'),
            feedback.get('correct_emotion'),
            feedback.get('feedback_type'),
            feedback.get('notes', '')
        ))

    def _normalize_faces(self, faces: List[Dict]) -> List[Dict]:
        """规范化人脸数据，确保所有字段都有默认值

        Args:
            faces: 原始人脸数据列表

        Returns:
            规范化后的人脸数据列表
        """
        normalized = []
        for face in faces:
            normalized_face = {
                'bbox': face.get('bbox', [0, 0, 0, 0]),
                'emotion': face.get('emotion', 'neutral'),
                'confidence': face.get('confidence', 0.0),
                'emotions': face.get('emotions', {})
            }
            normalized.append(normalized_face)
        return normalized

    def get_history(self, limit: int = 50, offset: int = 0, detection_type: str = None) -> List[Dict]:
        """获取历史记录（分页），支持按类型筛选"""
        if detection_type and detection_type != 'all':
            cursor = self._execute('''
                SELECT * FROM detection_history
                WHERE detection_type = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (detection_type, limit, offset))

            count_cursor = self._execute('''
                SELECT COUNT(*) as count FROM detection_history
                WHERE detection_type = ?
            ''', (detection_type,))
        else:
            cursor = self._execute('''
                SELECT * FROM detection_history
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))

            count_cursor = self._execute('''
                SELECT COUNT(*) as count FROM detection_history
            ''')

        results = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            results.append({
                'id': row_dict.get('id'),
                'timestamp': row_dict.get('timestamp'),
                'created_at': row_dict.get('created_at') or row_dict.get('timestamp'),
                'detection_type': row_dict.get('detection_type'),
                'source': row_dict.get('source', ''),
                'image_path': row_dict.get('image_path', ''),
                'image_type': row_dict.get('image_type', ''),
                'thumbnail': row_dict.get('thumbnail'),
                'results': json.loads(row_dict['results']) if row_dict.get('results') else [],
                'detected_faces': self._normalize_faces(json.loads(row_dict['detected_faces']) if row_dict.get('detected_faces') else []),
                'dominant_emotion': row_dict.get('dominant_emotion') or 'neutral',
                'confidence': row_dict.get('confidence') or 0.0
            })
        return results

    def get_history_count(self, detection_type: str = None) -> int:
        """获取历史记录总数，支持按类型筛选"""
        if detection_type and detection_type != 'all':
            cursor = self._execute(
                'SELECT COUNT(*) as count FROM detection_history WHERE detection_type = ?',
                (detection_type,)
            )
        else:
            cursor = self._execute(
                'SELECT COUNT(*) as count FROM detection_history'
            )
        row = cursor.fetchone()
        return row['count'] if row else 0

    def get_type_counts(self) -> Dict[str, int]:
        """获取各检测类型的数量统计"""
        cursor = self._execute('''
            SELECT detection_type, COUNT(*) as count
            FROM detection_history
            GROUP BY detection_type
        ''')

        counts = {}
        for row in cursor.fetchall():
            counts[row['detection_type']] = row['count']

        return counts

    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据（带缓存优化）"""
        import time

        # ✅ 优化: 检查缓存是否有效
        current_time = time.time()
        if (self._stats_cache and
                (current_time - self._stats_cache_time) < self._stats_cache_ttl):
            return self._stats_cache

        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM detection_history')
        total_detections = cursor.fetchone()[0]

        cursor.execute('''
            SELECT dominant_emotion, COUNT(*) as count
            FROM detection_history WHERE dominant_emotion IS NOT NULL
            GROUP BY dominant_emotion ORDER BY count DESC
        ''')
        emotion_stats = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(
            'SELECT AVG(confidence) FROM detection_history WHERE confidence > 0')
        avg_confidence = cursor.fetchone()[0] or 0

        # 来源分布
        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM detection_history WHERE source != ''
            GROUP BY source ORDER BY count DESC
        ''')
        source_stats = {row[0]: row[1] for row in cursor.fetchall()}

        stats = {
            'total_detections': total_detections,
            'emotion_distribution': emotion_stats,
            'source_distribution': source_stats,
            'average_confidence': round(avg_confidence, 3)
        }

        # ✅ 更新缓存
        self._stats_cache = stats
        self._stats_cache_time = current_time

        return stats

    def delete_by_detection_type(self, detection_type: str) -> int:
        """根据检测类型删除所有记录

        Args:
            detection_type: 检测类型（如 'video', 'image' 等）

        Returns:
            删除的记录数量
        """
        cursor = self._execute(
            'DELETE FROM detection_history WHERE detection_type = ?',
            (detection_type,)
        )
        self._conn.commit()
        return cursor.rowcount

    def close(self):
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
