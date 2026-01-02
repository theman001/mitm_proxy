import asyncio
import os
import importlib.util
import inspect
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster

# 모듈 간 데이터 공유를 위한 저장소
class SharedContext:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

class ProxyMaster:
    def __init__(self):
        self.module_path = "./utils"
        self.modules = []
        self.active_modules = []
        self.context = SharedContext() # 공유 객체 생성

    def discover_modules(self):
        self.modules = []
        files = [f[:-3] for f in os.listdir(self.module_path) if f.endswith(".py") and f != "__init__.py"]
        for idx, name in enumerate(files, 1):
            self.modules.append({"id": idx, "name": name})
        return self.modules

    def load_modules(self, choices):
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
                        # 인스턴스 생성 시 context 주입
                        instance = obj(self.context) 
                        self.active_modules.append(instance)
            except Exception as e:
                print(f"[!] 모듈 {module_info['name']} 로드 오류: {e}")

        self.active_modules.sort(key=lambda x: getattr(x, 'priority', 100))
        
        print("\n" + "🔄 " + "="*46)
        print("[!] Shared Context 파이프라인 활성화")
        for idx, mod in enumerate(self.active_modules, 1):
            print(f"  {idx}. [Prio:{getattr(mod, 'priority', 100)}] {mod.name}")
        print("="*50 + "\n")

    def request(self, flow):
        for module in self.active_modules:
            if hasattr(module, 'handle_request'):
                module.handle_request(flow)

    def response(self, flow):
        for module in self.active_modules:
            if hasattr(module, 'handle_response'):
                module.handle_response(flow)

async def start_engine():
    pm = ProxyMaster()
    print("=== TOTAL MITM EXPLOIT SUITE v9.0 (Shared Context) ===")
    
    modules = pm.discover_modules()
    print("\n[ 사용 가능한 모듈 리스트 ]")
    for m in modules:
        print(f" {m['id']}. {m['name']}")
    
    user_input = input("\n[?] 선택 (예: 1,2): ").strip()
    try:
        choices = [int(x.strip()) for x in user_input.split(',')]
        pm.load_modules(choices)
    except ValueError:
        return

    opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
    master = DumpMaster(opts)
    master.addons.add(pm)
    
    try: await master.run()
    except KeyboardInterrupt: master.shutdown()

if __name__ == "__main__":
    asyncio.run(start_engine())
