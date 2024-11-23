from flask import Flask, request, jsonify, render_template, redirect, url_for, flash , session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import openai
import os
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError  # 추가 필요

# 환경 변수 로드 및 OpenAI API 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

@app.route('/')
def home():
    return render_template('main.html')

# 로그인 매니저 설정
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.route('/check_login_status')
def check_login_status():
    logged_in = session.get('logged_in', False)
    return jsonify({'logged_in': logged_in})

# 감정 분석 및 일기 저장 엔드포인트
@app.route('/analyze', methods=['POST', 'GET'])
@login_required
def analyze():
    if request.method == 'POST':
        entry_text = request.form.get('entryText')
        try:
            # OpenAI API 감정 분석 요청
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Analyze the emotion in this text: '{entry_text}'",
                max_tokens=50,
                temperature=0.7
            )
            analysis_result = response.choices[0].text.strip()

            # 데이터베이스에 저장
            new_entry = DiaryEntry(
                user_id=current_user.id,
                entry_text=entry_text,
                emotion_analysis=analysis_result,
                feedback=f"Emotion Analysis Result: {analysis_result}"
            )
            db.session.add(new_entry)
            db.session.commit()

            flash("일기가 성공적으로 분석되고 저장되었습니다.")
            return redirect(url_for('my_diary'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return render_template('AILOG.html')

# 나의 일기 엔드포인트
@app.route('/my_diary')
@login_required
def my_diary():
    # 현재 사용자와 관련된 일기만 가져오기
    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.entry_date.desc()).all()
    return render_template('my_diary.html', entries=entries)

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
