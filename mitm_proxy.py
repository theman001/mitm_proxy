import asyncio
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from utils.kakao_extractor import KakaoExtractor

class ProxyMaster:
    def __init__(self, host="127.0.0.1", port=8080):
        self.opts = options.Options(listen_host=host, listen_port=port)
        self.master = DumpMaster(self.opts)
        # 기능 모듈 인스턴스화
        self.kakao = KakaoExtractor()

    # mitmproxy의 이벤트 훅 연결
    def request(self, flow):
        self.kakao.handle_request(flow)

    def response(self, flow):
        self.kakao.handle_response(flow)

    async def run(self):
        print(f"🚀 SQLi & Proxy Suite v7.0 가동 중...")
        print(f"[*] Proxy Listen: {self.opts.listen_host}:{self.opts.listen_port}")
        print("[*] 시스템 프록시를 설정하고 카카오톡 로그인을 진행하십시오.")
        try:
            await self.master.run()
        except KeyboardInterrupt:
            self.master.shutdown()

if __name__ == "__main__":
    proxy = ProxyMaster()
    asyncio.run(proxy.run())
