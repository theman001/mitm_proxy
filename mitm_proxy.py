import asyncio
import os
import importlib
import inspect
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster

class ProxyMaster:
    def __init__(self):
        self.module_path = "./utils"
        self.modules = []
        self.active_module = None

    def discover_modules(self):
        """utils 폴더 내의 .py 파일을 스캔하여 모듈 리스트 생성"""
        files = [f[:-3] for f in os.listdir(self.module_path) if f.endswith(".py") and f != "__init__.py"]
        for idx, name in enumerate(files, 1):
            self.modules.append({"id": idx, "name": name})
        return self.modules

    def load_module(self, choice):
        """선택한 번호의 모듈을 동적으로 로드 및 인스턴스화"""
        module_info = next((m for m in self.modules if m['id'] == choice), None)
        if not module_info:
            return False
        
        try:
            # 동적 임포트
            module_name = f"utils.{module_info['name']}"
            spec = importlib.util.find_spec(module_name)
            module = importlib.import_module(module_name)
            
            # 모듈 내의 클래스를 찾아 인스턴스화 (보통 첫 번째 클래스)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_name:
                    self.active_module = obj()
                    print(f"\n[+] 모듈 장착 완료: {module_info['name']}")
                    return True
        except Exception as e:
            print(f"[!] 모듈 로드 오류: {e}")
        return False

    def request(self, flow):
        if self.active_module and hasattr(self.active_module, 'handle_request'):
            self.active_module.handle_request(flow)

    def response(self, flow):
        if self.active_module and hasattr(self.active_module, 'handle_response'):
            self.active_module.handle_response(flow)

async def start_engine():
    pm = ProxyMaster()
    print("=== TOTAL MITM EXPLOIT SUITE v7.5 ===")
    
    # 모듈 탐색 및 출력
    modules = pm.discover_modules()
    if not modules:
        print("[!] utils 폴더에 모듈이 없습니다.")
        return

    print("\n[ 사용 가능한 모듈 리스트 ]")
    for m in modules:
        print(f" {m['id']}. {m['name']}")
    
    try:
        choice = int(input("\n[?] 장착할 모듈 번호를 입력하세요: "))
        if not pm.load_module(choice):
            print("[!] 잘못된 번호입니다.")
            return
    except ValueError:
        print("[!] 숫자만 입력 가능합니다.")
        return

    # 프록시 실행
    opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
    master = DumpMaster(opts)
    master.addons.add(pm)
    
    print(f"\n[*] Proxy Server Started on 127.0.0.1:8080")
    try:
        await master.run()
    except KeyboardInterrupt:
        master.shutdown()

if __name__ == "__main__":
    asyncio.run(start_engine())
