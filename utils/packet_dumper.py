import datetime

class PacketDumper:
    def __init__(self, context):
        self.name = "Raw Packet Dumper"
        self.priority = 99  # 가장 마지막에 실행 (기록 목적)
        self.context = context
        self.log_file = f"dump_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    def handle_request(self, flow):
        # 요청(Request) 덤프
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.datetime.now()}] [REQ] {flow.request.method} {flow.request.pretty_url}\n")
            if flow.request.headers:
                f.write(f"Headers: {dict(flow.request.headers)}\n")
            # POST 데이터 등 바디 내용 기록
            if flow.request.content:
                f.write(f"Body: {flow.request.get_text()[:500]}...\n") # 너무 길면 생략

    def handle_response(self, flow):
        # 응답(Response) 덤프
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now()}] [RES] {flow.response.status_code} for {flow.request.pretty_url}\n")
            
            # Shared Context에 중요한 데이터(토큰 등)가 저장되어 있다면 같이 기록
            captured_token = self.context.get("kakao_token")
            if captured_token:
                f.write(f">>> [!] Captured Data in Context: {captured_token}\n")
            
            # 응답 바디 기록 (JSON 등 분석용)
            if flow.response.content:
                f.write(f"Content: {flow.response.get_text()[:1000]}\n")
            f.write("-" * 80 + "\n")
