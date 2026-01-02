import asyncio
import os
import importlib.util
import inspect
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster

class ProxyMaster:
    def __init__(self):
        self.module_path = "./utils"
        self.modules = []
        self.active_modules = []  # 다중 모듈 저장 리스트

    def discover_modules(self):
        self.modules = [] # 초기화
        files = [f[:-3] for f in os.listdir(self.module_path) if f.endswith(".py") and f != "__init__.py"]
        for idx, name in enumerate(files, 1):
            self.modules.append({"id": idx, "name": name})
        return self.modules

    def load_modules(self, choices):
        """번호 리스트(예: [1, 2])를 받아 해당 모듈들을 모두 로드"""
        for choice in choices:
            module_info = next((m for m in self.modules if m['id'] == choice), None)
            if not module_info: continue
            
            try:
                module_name = f"utils.{module_info['name']}"
                spec = importlib.util.find_spec(module_name)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_name:
                        instance = obj()
                        self.active_modules.append(instance)
                        print(f"[+] 모듈 장착 완료: {module_info['name']}")
                        # 가이드가 있는 모듈(예: SSL Bypass)은 즉시 출력
                        if hasattr(instance, 'get_guide'):
                            instance.get_guide()
            except Exception as e:
                print(f"[!] 모듈 {module_info['name']} 로드 오류: {e}")

    # 모든 활성화된 모듈의 request 핸들러 호출
    def request(self, flow):
        for module in self.active_modules:
            if hasattr(module, 'handle_request'):
                module.handle_request(flow)

    # 모든 활성화된 모듈의 response 핸들러 호출
    def response(self, flow):
        for module in self.active_modules:
            if hasattr(module, 'handle_response'):
                module.handle_response(flow)

async def start_engine():
    pm = ProxyMaster()
    print("=== TOTAL MITM EXPLOIT SUITE v8.5 (Multi-Orchestrator) ===")
    
    modules = pm.discover_modules()
    print("\n[ 사용 가능한 모듈 리스트 ]")
    for m in modules:
        print(f" {m['id']}. {m['name']}")
    
    print("\n[*] 여러 모듈을 선택하려면 콤마(,)로 구분하십시오 (예: 1,2)")
    user_input = input("[?] 장착할 모듈 번호들: ").strip()
    
    try:
        choices = [int(x.strip()) for x in user_input.split(',')]
        pm.load_modules(choices)
    except ValueError:
        print("[!] 입력 형식이 잘못되었습니다.")
        return

    opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
    master = DumpMaster(opts)
    master.addons.add(pm)
    
    print(f"\n[*] Total {len(pm.active_modules)} Modules Running...")
    try: await master.run()
    except KeyboardInterrupt: master.shutdown()

if __name__ == "__main__":
    asyncio.run(start_engine())
