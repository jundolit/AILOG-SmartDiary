
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
}

// Close Side Navigation
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}

// Open '약관동의' modal
function openJoinModal() {
    document.getElementById('modalBackdrop').style.display = 'block';
    document.getElementById('cocoaModal').style.display = 'block';
}

// Close '약관동의' modal
function closeJoinModal() {
    document.getElementById('modalBackdrop').style.display = 'none';
    document.getElementById('cocoaModal').style.display = 'none';
}

// Open '회원가입' modal
function openSignupModal() {
    closeJoinModal(); // Close the '약관동의' modal
    const signupModal = document.getElementById('signupModal');
    signupModal.style.display = 'block'; // Open '회원가입' modal
    signupModal.style.zIndex = 1001; // Set higher z-index
}

// Close '회원가입' modal
function closeSignupModal() {
    document.getElementById('signupModal').style.display = 'none'; // Close '회원가입' modal
}

document.addEventListener("DOMContentLoaded", function() {
    const checkAll = document.querySelector('input._check_all');
    const checkboxes = document.querySelectorAll('.checkbox input[type="checkbox"]:not(._check_all)');
    const joinButton = document.querySelector('._join_btn'); // '가입하기' button
    const cancelButton = document.querySelector('.btn-default'); // '취소' button

    // Handle '모두 동의' checkbox
    if (checkAll) {
        checkAll.addEventListener("change", function() {
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = checkAll.checked;
            });
            updateJoinButtonState();
        });
    }

    // Update '가입하기' button state based on checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", updateJoinButtonState);
    });

    function updateJoinButtonState() {
        const allChecked = Array.from(checkboxes).every(checkbox => checkbox.checked);
        joinButton.disabled = !allChecked;
    }

    // Initial '가입하기' button state
    updateJoinButtonState();

    // '취소' button closes the '약관동의' modal
    if (cancelButton) {
        cancelButton.addEventListener("click", closeJoinModal);
    }

    // '가입하기' button click opens '회원가입' modal
    joinButton.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default behavior
        if (allCheckboxesChecked()) { // Check if all required checkboxes are checked
            openSignupModal(); // Open '회원가입' modal
        } else {
            alert("모든 체크박스에 동의해야 합니다."); // Alert if checkboxes are unchecked
        }
    });
});

// Check if all checkboxes are checked
function allCheckboxesChecked() {
    const checkboxes = document.querySelectorAll('.checkbox input[type="checkbox"]:not(._check_all)');
    return Array.from(checkboxes).every(checkbox => checkbox.checked);
}
// 로그인 모달 열기
function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
    document.getElementById('loginModal').style.zIndex = 1001; // 다른 모달보다 위에 표시
}

// 로그인 모달 닫기
function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

// 로그인 버튼 클릭 시 로그인 모달 열기
document.addEventListener("DOMContentLoaded", function() {
    const loginButton = document.getElementById('loginButton');

    if (loginButton) {
        loginButton.addEventListener('click', function(event) {
            event.preventDefault();
            openLoginModal();
        });
    } else {
        console.error('Login button not found');
    }
});

document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const result = await response.json();
        if (result.success) {
            alert("로그인에 성공했습니다.");
            closeLoginModal();
            window.location.href = "/";  // 로그인 후 이동할 페이지
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert("로그인 중 오류가 발생했습니다.");
    }
});
document.getElementById('signupForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });

        const result = await response.json();
        if (result.success) {
            alert("회원가입이 성공적으로 완료되었습니다.");
            closeSignupModal();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert("회원가입 중 오류가 발생했습니다.");
    }
    console.log({ username, email, password });

});
document.addEventListener("DOMContentLoaded", async function() {
    // 로그인 상태 확인
    const response = await fetch('/check_login_status');
    const data = await response.json();

    const loginButton = document.getElementById('loginButton');
    if (data.logged_in) {
        loginButton.innerText = 'Logout';
        loginButton.onclick = logout;
    } else {
        loginButton.innerText = 'Login';
        loginButton.onclick = openLoginModal;
    }
});




// 로그아웃 함수
async function logout() {
    try {
        const response = await fetch('/logout', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            const loginButton = document.getElementById('loginButton');
            loginButton.innerText = 'Login';
            loginButton.onclick = openLoginModal;
            alert("로그아웃되었습니다.");
        }
    } catch (error) {
        console.error("Error during logout:", error);
        alert("로그아웃 중 문제가 발생했습니다.");
    }
}

document.addEventListener("DOMContentLoaded", async function () {
    const loginButton = document.getElementById('loginButton');

    // 로그인 상태 확인 및 버튼 상태 업데이트
    async function updateLoginButton() {
        const response = await fetch('/check_login_status');
        const data = await response.json();

        if (data.logged_in) {
            // 로그인 상태: Logout 설정
            loginButton.innerText = 'Logout';
            loginButton.onclick = async function () {
                const logoutResponse = await fetch('/logout');
                const logoutResult = await logoutResponse.json();
                if (logoutResult.success) {
                    alert('로그아웃되었습니다.');
                    // 상태 업데이트
                    loginButton.innerText = 'Login';
                    loginButton.onclick = openLoginModal;
                }
            };
        } else {
            // 비로그인 상태: Login 설정
            loginButton.innerText = 'Login';
            loginButton.onclick = openLoginModal;
        }
    }

    // 페이지 로드 시 버튼 초기화
    await updateLoginButton();
});
document.addEventListener("DOMContentLoaded", async function () {
    const loginButton = document.getElementById('loginButton');

    // 로그인 상태 확인 및 버튼 상태 업데이트
    async function updateLoginButton() {
        const response = await fetch('/check_login_status');
        const data = await response.json();

        if (data.logged_in) {
            // 로그인 상태: Logout 설정
            setLogoutState();
        } else {
            // 비로그인 상태: Login 설정
            setLoginState();
        }
    }

    // Logout 상태로 버튼 설정
    function setLogoutState() {
        loginButton.innerText = 'Logout';
        loginButton.onclick = async function () {
            const logoutResponse = await fetch('/logout');
            const logoutResult = await logoutResponse.json();
            if (logoutResult.success) {
                alert('로그아웃되었습니다.');
                setLoginState(); // Logout 후 Login 상태로 변경
            }
        };
    }

    // Login 상태로 버튼 설정
    function setLoginState() {
        loginButton.innerText = 'Login';
        loginButton.onclick = openLoginModal;
    }

    // 페이지 로드 시 버튼 초기화
    await updateLoginButton();
});

// Login 모달 열기 함수
function openLoginModal() {
    const loginModal = document.getElementById('loginModal');
    if (loginModal) {
        loginModal.style.display = 'block';
        loginModal.style.zIndex = 1001; // 모달을 다른 요소보다 위로 표시
    }
}

// Login 모달 닫기 함수
function closeLoginModal() {
    const loginModal = document.getElementById('loginModal');
    if (loginModal) {
        loginModal.style.display = 'none';
    }
}
// 일기 저장 함수
async function saveDiaryEntry(entryText) {
    try {
        // /analyze 요청 처리
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: entryText })
        });

        const result = await response.json();

        if (result.success) {
            alert("일기가 성공적으로 저장되었습니다!");

            // /save 요청
            const saveResponse = await fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ diary_id: result.diary_id })
            });

            const saveResultHTML = await saveResponse.text();

            // save.html을 현재 페이지에 렌더링
            document.open();
            document.write(saveResultHTML);
            document.close();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error("Error saving diary entry:", error);
        alert("일기 저장 중 오류가 발생했습니다.");
    }
}

