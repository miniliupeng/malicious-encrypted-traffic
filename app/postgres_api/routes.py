from flask import Flask
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from ..config import Config
from flask import Blueprint, request, jsonify, current_app

pg_api = Blueprint('pg_api', __name__)
app = Flask(__name__)
CORS(app)  # 允许跨域请求

def get_pg_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    return conn
@pg_api.route('/log_app/pcap_label_stats', methods=['GET'])
def get_pcap_label_stats():
    """
    统计 app_log 表中每个 pcap_label 的数量
    """
    try:
        conn = get_pg_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                pcap_label, 
                COUNT(*) as count 
            FROM 
                app_log 
            GROUP BY 
                pcap_label 
            ORDER BY 
                count DESC;
    
        """
        cursor.execute(query)
        stats = cursor.fetchall()
        
        cursor.close()
        conn.close()

        

        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching pcap_label stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@pg_api.route('/traffic_log/summary_stats', methods=['GET'])
def get_traffic_log_summary_stats():
    """
     统计 traffic_log 数据总个数，并单独统计 'Malicious_traffic' 标签的数据总个数 total_count\malicious
    """
    try:
        conn = get_pg_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                COUNT(*) AS total_count,
                COUNT(*) FILTER (WHERE pcap_label = 'Malicious_traffic') AS malicious_count
            FROM
                traffic_log;
        """
        
        cursor.execute(query)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching traffic_log summary stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@pg_api.route('/traffic_log/time_stats', methods=['GET'])
def get_traffic_log_time_stats():
    """
     以四小时为单位，统计每个时间段内的数据总数并显示。
    """
    try:
        conn = get_pg_connection()
        cursor = conn.cursor()
        
        # SQL核心逻辑:
        # 1. date_trunc('day', log_time): 将时间戳截断到当天的开始 (00:00:00)
        # 2. EXTRACT(hour FROM log_time)::int / 4: 提取小时数，用整数除法计算出它属于哪个4小时的区间 (0, 1, 2, 3, 4, 5)
        # 3. ... * interval '4 hours': 将区间序号乘以4小时，得到区间的偏移量
        # 4. 将1和3的结果相加，得到每个4小时区间的开始时间点
        #time_interval_start\log_count
        query = """
            SELECT
                date_trunc('day', log_time) + 
                (EXTRACT(hour FROM log_time)::int / 4) * interval '4 hours' 
                AS time_interval_start,
                COUNT(*) AS log_count
            FROM
                traffic_log
            GROUP BY
                time_interval_start
            ORDER BY
                time_interval_start;
        """
        
        cursor.execute(query)
        stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching traffic_log time stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@pg_api.route('/traffic_log/malicious_traffic', methods=['GET'])
def get_malicious_traffic_logs():
    """
    统计并显示 pcap_label 为 'Malicious_traffic' 的所有数据，支持分页。
    """
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100)) # 默认每页100条
        offset = (page - 1) * limit

        conn = get_pg_connection()
        cursor = conn.cursor()
        
        # 查询分页数据的 SQL
        query = """
            SELECT 
                id, log_num, log_time, src, sport, dst, dport, protol, pcap_label 
            FROM 
                traffic_log 
            WHERE 
                pcap_label = 'Malicious_traffic' 
            ORDER BY 
                log_time DESC 
            LIMIT %s OFFSET %s;
        """
        
        cursor.execute(query, (limit, offset))
        logs = cursor.fetchall()
        
        # 查询总数的 SQL
        count_query = """
            SELECT COUNT(*) 
            FROM traffic_log 
            WHERE pcap_label = 'Malicious_traffic';
        """
        cursor.execute(count_query)
        # 从查询结果中获取 'count' 字段的值
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': logs,
            'total': total,
      'page': page,
            'limit': limit
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching malicious traffic logs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500  
@pg_api.route('/traffic_log/malicious_traffic/src_stats', methods=['GET'])
def get_malicious_traffic_src_stats():
    """
    恶意IP个数
    """
    try:
        conn = get_pg_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT
                src,
                COUNT(*) as count
            FROM
                traffic_log
            WHERE
                pcap_label = 'Malicious_traffic'
            GROUP BY
                src
            ORDER BY
                count DESC;
        """
        
        cursor.execute(query)
        stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching malicious traffic src stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@pg_api.route('/log_app/pcap_label_stat555', methods=['GET'])
def get_pcap_label_top5_stats():
    """
    统计 app_log 表中每个 pcap_label 的数量，并按数量倒序显示和占比（Top5应用）pcap_label\count\proportion
    """
    try:
        conn = get_pg_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                pcap_label, 
                COUNT(*) as count 
            FROM 
                app_log 
            GROUP BY 
                pcap_label 
            ORDER BY 
                count DESC
            LIMIT 5
        """
        cursor.execute(query)
        stats = cursor.fetchall()
        
        cursor.close()
        conn.close()

        total_count = sum(item['count'] for item in stats)#流量数量
       
        if total_count > 0:
            for item in stats:
                proportion = round(item['count'] / total_count, 3)
                item['proportion'] = proportion #占比
        else:
            for item in stats:
                item['proportion'] = 0

        return jsonify({
            'success': True,
            'data': stats,
            'total_logs': total_count 
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching pcap_label stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500










    







        
       