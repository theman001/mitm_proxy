import re
from mitmproxy import http

class KakaoExtractor:
    def __init__(self):
        # 모듈 로더에서 표시될 이름
        self.name = "KakaoTalk Token & UUID Extractor"
        self.priority = 50  # 분석 단계 (중간 순위)
        self.context = context  # 전달받은 공유 객체 저장
        # 분석 타겟 호스트
        self.auth_host = "auth.kakao.com"
        self.api_host = "kauth.kakao.com"

    def handle_request(self, flow: http.HTTPFlow):
        """
        프록시 요청 단계 핸들러
        """
        if self.auth_host in flow.request.pretty_host:
            # 필요한 경우 요청 패킷 로그 출력
            pass

    def handle_response(self, flow: http.HTTPFlow):
        """
        프록시 응답 단계 핸들러 (데이터 추출 핵심)
        """
        # 타겟 호스트 확인
        if any(host in flow.request.pretty_host for host in [self.auth_host, self.api_host]):
            content = flow.response.get_text()
            
            # JSON 응답 내 핵심 데이터 정규표현식 추출
            token = re.search(r'"access_token":"(.*?)"', content)
            uuid = re.search(r'"device_uuid":"(.*?)"', content)
            refresh = re.search(r'"refresh_token":"(.*?)"', content)

            if token or uuid:
                print("\n" + "🚀 " + "="*46)
                print(f"[!] {self.name} - 데이터 탐지됨")
                if token:   print(f" > Access Token:  {token.group(1)}")
                if refresh: print(f" > Refresh Token: {refresh.group(1)}")
                if uuid:    print(f" > Device UUID:   {uuid.group(1)}")
                print("="*50 + "\n")
