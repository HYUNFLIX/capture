import os
import sys

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory
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

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# CORS 설정
CORS(app)

# Blueprint 등록
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(capture_bp, url_prefix='/api')

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 데이터베이스 초기화
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return """
            <!DOCTYPE html>
            <html>
            <head><title>웹 페이지 캡처 도구</title></head>
            <body>
                <h1>🌐 웹 페이지 캡처 도구</h1>
                <p>✅ 서버가 성공적으로 실행되었습니다!</p>
                <p>🔧 API 테스트: <a href="/api/capture/health">/api/capture/health</a></p>
            </body>
            </html>
            """

if __name__ == '__main__':
    print("🚀 웹 페이지 캡처 도구 서버 시작...")
    print("📍 서버 주소: http://localhost:5001")
    print("🛑 서버 종료: Ctrl+C")
    app.run(host='0.0.0.0', port=5001, debug=True)
