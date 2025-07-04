import os
import sys
import logging
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# 모듈 import
try:
    from src.models.user import db
    from src.routes.user import user_bp
    from src.routes.capture import capture_bp
except ImportError as e:
    print(f"❌ Import 에러: {e}")
    print("폴더 구조를 확인해주세요.")
    sys.exit(1)

def create_app():
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__, static_folder='static')
    
    # 환경 설정
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    
    # CORS 설정
    CORS(app, origins=['*'])  # 운영환경에서는 특정 도메인으로 제한 권장
    
    # Blueprint 등록
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(capture_bp, url_prefix='/api')
    
    # 데이터베이스 설정
    database_dir = Path(__file__).parent / 'database'
    database_dir.mkdir(exist_ok=True)  # 데이터베이스 폴더 생성
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_dir / 'app.db'}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ 데이터베이스 초기화 완료")
        except Exception as e:
            print(f"❌ 데이터베이스 초기화 실패: {e}")
    
    return app

# Flask 앱 생성
app = create_app()

# 헬스체크 라우트 (로드밸런서용)
@app.route('/health')
@app.route('/api/health')
def health_check():
    """서비스 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'service': 'webpage-capture',
        'version': '1.0.0',
        'environment': os.environ.get('ENVIRONMENT', 'development')
    })

# 메인 라우트
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """정적 파일 서빙 및 SPA 라우팅"""
    static_folder_path = app.static_folder
    
    if static_folder_path is None:
        return create_fallback_page(), 200
    
    # 정적 파일 요청 처리
    if path and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    
    # index.html 반환 (SPA 라우팅 지원)
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    else:
        return create_fallback_page(), 200

def create_fallback_page():
    """정적 파일이 없을 때 기본 페이지"""
    return f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>웹 페이지 캡처 도구</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                margin: 0;
                padding: 40px 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }}
            h1 {{ color: #333; margin-bottom: 20px; }}
            .status {{ color: #155724; background: #d4edda; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .api-link {{ color: #007bff; text-decoration: none; font-weight: 600; }}
            .api-link:hover {{ text-decoration: underline; }}
            .info {{ color: #666; line-height: 1.6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 웹 페이지 캡처 도구</h1>
            <div class="status">✅ 서버가 성공적으로 실행되었습니다!</div>
            
            <div class="info">
                <p><strong>🔧 API 엔드포인트:</strong></p>
                <p>• <a href="/api/capture/health" class="api-link">헬스체크</a></p>
                <p>• <a href="/health" class="api-link">서버 상태</a></p>
                <p>• POST /api/capture (웹페이지 캡처)</p>
                
                <hr style="margin: 30px 0; border: 1px solid #eee;">
                
                <p><strong>📁 정적 파일 위치:</strong></p>
                <p>static/index.html 파일을 추가하여<br>웹 인터페이스를 사용할 수 있습니다.</p>
                
                <p style="margin-top: 30px; font-size: 14px; color: #888;">
                    Environment: {os.environ.get('ENVIRONMENT', 'development')}<br>
                    Port: {os.environ.get('PORT', '5001')}
                </p>
            </div>
        </div>
    </body>
    </html>
    """

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': '요청한 리소스를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': '서버 내부 오류가 발생했습니다.'}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """예상치 못한 에러 처리"""
    app.logger.error(f"Unhandled exception: {error}")
    return jsonify({'error': 'Server Error', 'message': '서버에서 오류가 발생했습니다.'}), 500

def setup_logging():
    """로깅 설정"""
    if not app.debug:
        # 운영환경에서만 로깅 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

if __name__ == '__main__':
    # 환경변수에서 설정 읽기
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'false').lower() in ['true', '1', 'yes']
    environment = os.environ.get('ENVIRONMENT', 'development')
    
    # 로깅 설정
    setup_logging()
    
    # 시작 메시지
    print("=" * 50)
    print("🚀 웹 페이지 캡처 도구 서버 시작")
    print("=" * 50)
    print(f"📍 서버 주소: http://{host}:{port}")
    print(f"🔧 환경: {environment}")
    print(f"🐛 디버그 모드: {'ON' if debug else 'OFF'}")
    print(f"📊 헬스체크: http://{host}:{port}/health")
    print("🛑 서버 종료: Ctrl+C")
    print("=" * 50)
    
    try:
        # Flask 앱 실행
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,  # 멀티스레딩 지원
            use_reloader=debug  # 디버그 모드에서만 리로더 사용
        )
    except KeyboardInterrupt:
        print("\n🛑 서버가 정상적으로 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        sys.exit(1)