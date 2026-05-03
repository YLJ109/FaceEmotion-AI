"""
数据库模拟数据填充脚本
生成 50 条有真实感的使用记录，覆盖近 30 天
运行方式: python seed_demo_data.py
"""

import sqlite3
import json
import random
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'emotion.db')

FEATURES = ['实时检测', '图片检测', '批量检测', '视频检测', '系统设置', '主题切换']
EMOTIONS = ['happy', 'sad', 'angry', 'surprised',
            'fearful', 'disgusted', 'neutral']

# 功能权重（模拟真实使用频率分布）
FEATURE_WEIGHTS = {
    '实时检测': 40,
    '图片检测': 20,
    '批量检测': 15,
    '视频检测': 10,
    '系统设置': 8,
    '主题切换': 7,
}

# 各情绪出现权重
EMOTION_WEIGHTS = {
    'happy': 25,
    'neutral': 30,
    'sad': 15,
    'surprised': 10,
    'angry': 8,
    'fearful': 7,
    'disgusted': 5,
}


def weighted_choice(items, weights):
    total = sum(weights)
    r = random.random() * total
    cumulative = 0
    for item, w in zip(items, weights):
        cumulative += w
        if r <= cumulative:
            return item
    return items[-1]


def random_timestamp(days_ago):
    """生成过去 days_ago 天内的随机时间戳"""
    now = datetime.datetime.now()
    delta = datetime.timedelta(
        days=random.uniform(0, days_ago),
        hours=random.uniform(0, 24),
        minutes=random.uniform(0, 60),
        seconds=random.uniform(0, 60),
    )
    return (now - delta).strftime('%Y-%m-%d %H:%M:%S')


def random_session_id():
    return f'session_{random.randint(100000, 999999)}_{random.randint(1000, 9999)}'


def seed_database():
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── 1. 清空旧数据 ──
    for table in ['feature_usage', 'detection_history', 'session_stats', 'statistics']:
        cursor.execute(f'DELETE FROM {table}')
    print('✅ 已清空旧数据')

    # ── 2. 生成 feature_usage 记录（50 条） ──
    print('📝 生成功能使用记录...')
    feature_count = {}
    for _ in range(50):
        feature = weighted_choice(
            FEATURES, [FEATURE_WEIGHTS[f] for f in FEATURES])
        feature_count[feature] = feature_count.get(feature, 0) + 1
        ts = random_timestamp(30)
        sid = random_session_id()
        duration = random.randint(1000, 30000)
        emotion = weighted_choice(
            EMOTIONS, [EMOTION_WEIGHTS[e] for e in EMOTIONS])
        metadata = json.dumps({'emotion': emotion, 'source': 'seed'})
        cursor.execute(
            'INSERT INTO feature_usage (timestamp, feature, session_id, duration_ms, metadata) VALUES (?, ?, ?, ?, ?)',
            (ts, feature, sid, duration, metadata)
        )
    print(f'  已插入 {feature_count}')

    # ── 3. 生成 detection_history 记录（50 条） ──
    print('📝 生成检测历史记录...')
    detection_types = ['realtime', 'image', 'batch', 'video']
    for _ in range(50):
        emotion = weighted_choice(
            EMOTIONS, [EMOTION_WEIGHTS[e] for e in EMOTIONS])
        faces = [{
            'bbox': [random.randint(50, 200), random.randint(50, 200), random.randint(80, 150), random.randint(80, 150)],
            'emotion': emotion,
            'confidence': round(random.uniform(0.65, 0.98), 4),
            'scores': {e: round(random.uniform(0.01, 0.5), 4) for e in EMOTIONS},
        }]
        faces[0]['scores'][emotion] = round(random.uniform(0.65, 0.98), 4)
        ts = random_timestamp(30)
        dtype = random.choice(detection_types)
        source = {'realtime': '实时摄像头检测', 'image': '图片上传检测',
                  'batch': '批量图片检测', 'video': '视频文件检测'}[dtype]
        cursor.execute(
            'INSERT INTO detection_history (timestamp, detection_type, source, results, dominant_emotion, confidence) VALUES (?, ?, ?, ?, ?, ?)',
            (ts, dtype, source, json.dumps(faces),
             emotion, faces[0]['confidence'])
        )
    print('  ✅ 检测历史已插入')

    # ── 4. 生成 session_stats 记录 ──
    print('📝 生成会话统计...')
    sessions = {}
    cursor.execute('SELECT session_id, timestamp, metadata FROM feature_usage')
    for row in cursor.fetchall():
        sid, ts, meta = row
        if sid not in sessions:
            sessions[sid] = {'start': ts, 'end': ts,
                             'features': set(), 'detections': 0, 'emotions': []}
        s = sessions[sid]
        if ts < s['start']:
            s['start'] = ts
        if ts > s['end']:
            s['end'] = ts
        s['features'].add(json.loads(meta).get('emotion', 'neutral'))
        s['detections'] += 1

    for sid, s in sessions.items():
        emotions = list(s['features'])
        dominant = max(
            set(emotions), key=emotions.count) if emotions else 'neutral'
        cursor.execute(
            'INSERT INTO session_stats (session_id, start_time, end_time, total_detections, features_used, dominant_emotion, avg_confidence) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (sid, s['start'], s['end'], s['detections'], json.dumps(
                list(s['features'])), dominant, round(random.uniform(0.7, 0.9), 2))
        )
    print(f'  ✅ 已插入 {len(sessions)} 条会话统计')

    # ── 5. 生成 statistics 日汇总 ──
    print('📝 生成日统计汇总...')
    cursor.execute(
        'SELECT DATE(timestamp) as d, dominant_emotion, confidence FROM detection_history ORDER BY d')
    daily = {}
    for d, emotion, conf in cursor.fetchall():
        if d not in daily:
            daily[d] = {'total': 0, 'emotions': {}, 'confs': []}
        daily[d]['total'] += 1
        daily[d]['emotions'][emotion] = daily[d]['emotions'].get(
            emotion, 0) + 1
        daily[d]['confs'].append(conf)

    for date_str, data in daily.items():
        avg_conf = sum(data['confs']) / \
            len(data['confs']) if data['confs'] else 0
        cursor.execute(
            'INSERT INTO statistics (date, total_detections, emotion_counts, avg_confidence) VALUES (?, ?, ?, ?)',
            (date_str, data['total'], json.dumps(
                data['emotions']), round(avg_conf, 4))
        )
    print(f'  ✅ 已插入 {len(daily)} 天统计数据')

    conn.commit()
    conn.close()
    print()
    print('=' * 50)
    print('🎉 模拟数据填充完成!')
    print(f'📊 功能使用记录: 50 条')
    print(f'📊 检测历史记录: 50 条')
    print(f'📊 会话统计: {len(sessions)} 条')
    print(f'📊 日汇总: {len(daily)} 天')
    print('=' * 50)


if __name__ == '__main__':
    seed_database()
