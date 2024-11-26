from flask import Flask, request, jsonify, render_template, redirect, url_for, flash , session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import openai
import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError  # 추가 필요

openai.api_key = "sk-proj-API있던 자리 입니다--"
# 환경 변수 로드 및 OpenAI API 설정
load_dotenv()  # .env 파일의 내용을 로드
openai.api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API Key를 가져옴

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 로그인 세션을 위한 비밀 키 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary_entries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 로그인되지 않은 사용자가 접근할 때 리디렉션할 페이지

# 사용자 모델 정의
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)  # 이메일 필드 추가
    password = db.Column(db.String(150), nullable=False)

# 일기 모델 정의
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_text = db.Column(db.Text, nullable=False)
    emotion_analysis = db.Column(db.String(255), nullable=True)
    feedback = db.Column(db.String(255), nullable=True)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@app.route('/')
def home():
    return render_template('main.html')

# 로그인 매니저 설정
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# 데이터베이스 생성
with app.app_context():
    db.create_all()

# 회원가입 엔드포인트
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        # JSON 데이터에서 필드를 가져옵니다.
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')  # 이메일 필드 추가
        password = data.get('password')

        # 비밀번호를 해시합니다.
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # 사용자 이름과 이메일 중복 확인
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({"success": False, "message": "이미 존재하는 사용자 이름 또는 이메일입니다."}), 400

        # 새로운 사용자 추가
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": True, "message": "회원가입이 완료되었습니다."}), 200

# 로그인 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    # JSON 데이터에서 이메일과 비밀번호를 가져옵니다.
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "로그인 실패! 이메일 또는 비밀번호를 확인하세요."}), 401

# 로그아웃 엔드포인트
@app.route('/logout')
def logout():
    logout_user()
    session['logged_in'] = False  # 세션에 로그아웃 상태 저장
    return jsonify({'success': True})

@app.route('/check_login_status', methods=['GET'])
def check_login_status():
    return jsonify({"logged_in": current_user.is_authenticated}), 200


# 감정 분석 및 일기 저장 엔드포인트
@app.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    if request.method == 'GET':
        # 일기 작성 페이지 렌더링
        return render_template('analyze.html')
    elif request.method == 'POST':
        # Content-Type이 application/json인지 확인
        if not request.is_json:
            return jsonify({"success": False, "message": "JSON 형식의 요청만 지원합니다."}), 415

        # JSON 데이터 파싱
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags')  # 대표 키워드

        # 필수 데이터 확인
        if not content or not tags:
            return jsonify({"success": False, "message": "일기 텍스트와 태그가 필요합니다."}), 400

        # OpenAI API 감정 분석
        try:
            messages = [
                {"role": "system", "content": "다음은 사용자 일기에 대한 피드백을 작성하는 AI입니다."},
                {"role": "user", "content": f"""
                    다음은 사용자 일기야. 이 일기에서 주요 키워드(태그)와 그에 관련된 감정을 중점적으로 분석해줘.

                    **조건:**
                    1. 일기 내용에서 중요한 키워드를 추출하고 각 키워드와 관련된 감정을 서술할 것.
                    2. 사용자가 작성한 태그(키워드)를 기준으로 중요한 내용을 중점적으로 읽을 것.
                    3. 피드백은 다정하고 친근한 반말로 작성하며, 친구처럼 위로하거나 공감하며 긍정적인 마무리로 끝낼 것. 꼭 반말로해야함
                    반말 예시) "오늘 그런일이있었어? 많이 힘들었지"
                    4. 절대 정치적, 선정적, 욕설, 폭언은 포함하지 말 것.
                    5. 피드백은 꼭 위로와 긍정의 메시지를 담을 것.
                    **일기 제목:** {title}

                    **일기 내용:** {content}

                    **태그(키워드):** {tags}
                """}
            ]

            # 최신 OpenAI Chat API 호출
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # 모델 설정 (gpt-4로 변경 가능)
                messages=messages
            )

            analysis_result = response['choices'][0]['message']['content'].strip()

            # DB에 저장
            new_entry = DiaryEntry(
                user_id=current_user.id,
                entry_text=content,
                emotion_analysis=tags,  # 태그를 분석 결과로 저장
                feedback=analysis_result
            )
            db.session.add(new_entry)
            db.session.commit()

            # 저장된 일기의 ID 반환
            return jsonify({
                "success": True,
                "message": "일기가 성공적으로 저장되었습니다.",
                "feedback": analysis_result,
                "diary_id": new_entry.id  # 저장된 일기의 ID 반환
            }), 200

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return jsonify({"success": False, "message": "감정 분석 중 오류가 발생했습니다."}), 500
@app.route('/save', methods=['POST'])
@login_required
def save_page():
    data = request.get_json()
    diary_id = data.get('diary_id')
    diary = DiaryEntry.query.filter_by(id=diary_id, user_id=current_user.id).first()

    if not diary:
        return jsonify({"success": False, "message": "일기를 찾을 수 없습니다."}), 404

    return render_template('save.html', diary=diary)


# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)