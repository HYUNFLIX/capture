import os
import io
import base64
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from playwright.async_api import async_playwright
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader

capture_bp = Blueprint('capture', __name__)

@capture_bp.route('/capture', methods=['POST'])
def capture_webpage():
    """웹 페이지를 캡처하여 이미지 또는 PDF로 반환"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format', 'png')  # 'png' 또는 'pdf'
        
        if not url:
            return jsonify({'error': 'URL이 필요합니다.'}), 400
        
        # URL 유효성 검사
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 비동기 캡처 함수 실행
        screenshot_data = asyncio.run(capture_screenshot(url))
        
        if format_type.lower() == 'pdf':
            # PDF 생성
            pdf_buffer = create_pdf_from_image(screenshot_data)
            filename = f"webpage_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return send_file(
                io.BytesIO(pdf_buffer),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            # PNG 이미지 반환
            filename = f"webpage_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            return send_file(
                io.BytesIO(screenshot_data),
                mimetype='image/png',
                as_attachment=True,
                download_name=filename
            )
            
    except Exception as e:
        return jsonify({'error': f'캡처 중 오류가 발생했습니다: {str(e)}'}), 500

async def capture_screenshot(url):
    """Playwright를 사용하여 웹 페이지 전체 스크린샷 캡처"""
    async with async_playwright() as p:
        # Chromium 브라우저 실행 (헤드리스 모드)
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # 새 페이지 생성
        page = await browser.new_page(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        try:
            # 페이지 로드 (타임아웃 60초로 증가, 더 관대한 대기 조건)
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # 페이지가 완전히 로드될 때까지 대기
            await page.wait_for_timeout(3000)
            
            # 추가적인 네트워크 대기 (선택적)
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                # 네트워크 대기 실패해도 계속 진행
                pass
            
            # 전체 페이지 스크린샷 캡처
            screenshot = await page.screenshot(
                full_page=True,
                type='png'
            )
            
            return screenshot
            
        finally:
            await browser.close()

def create_pdf_from_image(image_data):
    """이미지 데이터를 PDF로 변환"""
    # 이미지 열기
    image = Image.open(io.BytesIO(image_data))
    
    # PDF 버퍼 생성
    pdf_buffer = io.BytesIO()
    
    # 이미지 크기에 맞는 PDF 페이지 크기 계산
    img_width, img_height = image.size
    
    # A4 크기 기준으로 스케일링
    a4_width, a4_height = A4
    
    # 이미지 비율 유지하면서 A4에 맞게 조정
    scale_x = a4_width / img_width
    scale_y = a4_height / img_height
    scale = min(scale_x, scale_y)
    
    new_width = img_width * scale
    new_height = img_height * scale
    
    # PDF 생성
    c = canvas.Canvas(pdf_buffer, pagesize=(new_width, new_height))
    
    # 이미지를 PDF에 추가
    image_reader = ImageReader(io.BytesIO(image_data))
    c.drawImage(image_reader, 0, 0, new_width, new_height)
    
    c.save()
    
    return pdf_buffer.getvalue()

@capture_bp.route('/health', methods=['GET'])
def health_check():
    """서비스 상태 확인"""
    return jsonify({'status': 'healthy', 'service': 'webpage-capture'})

