import os

class SSLPinningBypass:
    def __init__(self):
        self.name = "SSL Pinning Bypass (Frida-based)"
        # 앱이 시스템 인증서를 신뢰하도록 강제하는 Frida 스크립트
        self.frida_script = """
        /* SSL Pinning Bypass Script for KakaoTalk & Generic Apps */
        Java.perform(function() {
            var array_list = Java.use("java.util.ArrayList");
            var ApiClient = Java.use("com.android.org.conscrypt.TrustManagerImpl");

            ApiClient.checkTrustedRecursive.implementation = function(a1, a2, a3, a4, a5, a6) {
                console.log("[+] Bypassing SSL Pinning...");
                return array_list.$new();
            };
        });
        """

    def handle_request(self, flow):
        # 네트워크 패킷에는 직접 관여하지 않음
        pass

    def handle_response(self, flow):
        # 네트워크 패킷에는 직접 관여하지 않음
        pass

    def get_guide(self):
        """사용자에게 후킹 방법 안내"""
        print("\n" + "🛡️ " + "="*46)
        print(f"[!] {self.name} 가동 중...")
        print("[*] 이 모듈은 네트워크 패킷 변조가 아닌 '앱 후킹 가이드'를 제공합니다.")
        print("[*] 아래 절차를 통해 SSL Pinning을 무력화하십시오:")
        print(" 1. Frida 설치: pip install frida-tools")
        print(" 2. 카카오톡 프로세스 확인: frida-ps -U")
        print(" 3. 후킹 실행: frida -U -f com.kakao.talk -l bypass.js --no-pause")
        print("-" * 50)
        
        # 스크립트 파일로 자동 저장
        with open("bypass.js", "w") as f:
            f.write(self.frida_script)
        print("[+] bypass.js 파일이 생성되었습니다.")
        print("="*50 + "\n")
