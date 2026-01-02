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
        self.active_modules = []

    def discover_modules(self):
        self.modules = []
        if not os.path.exists(self.module_path):
            os.makedirs(self.module_path)
        files = [f[:-3] for f in os.listdir(self.module_path) if f.endswith(".py") and f != "__init__.py"]
        for idx, name in enumerate(files, 1):
            self.modules.append({"id": idx, "name": name})
        return self.modules

    def load_modules(self, choices):
        """번호를 입력받아 모듈 로드 후 priority 기준 정렬"""
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
            except Exception as e:
                print(f"[!] 모듈 {module_info['name']} 로드 오류: {e}")

        # 핵심: 우선순위(priority) 기준 오름차순 정렬 (낮은 숫자가 먼저 실행)
        self.active_modules.sort(key=lambda x: getattr(x, 'priority', 100))
        
        print("\n" + "="*50)
        print("[!] 모듈 파이프라인 구성 완료 (실행 순서):")
        for idx, mod in enumerate(self.active_modules, 1):
            prio = getattr(mod, 'priority', 100)
            mod_name = getattr(mod, 'name', mod.__class__.__name__)
            print(f"  {idx}. [Prio:{prio:2}] {mod_name}")
            if hasattr(mod, 'get_guide'):
                mod.get_guide()
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
    print("=== TOTAL MITM EXPLOIT SUITE v8.7 (Priority Engine) ===")
    
    modules = pm.discover_modules()
    if not modules:
        print("[!] utils 폴더에 모듈이 없습니다.")
        return

    print("\n[ 사용 가능한 모듈 리스트 ]")
    for m in modules:
        print(f" {m['id']}. {m['name']}")
    
    print("\n[*] 실행할 모듈 번호들을 입력하십시오 (예: 2,1,3)")
    user_input = input("[?] 선택: ").strip()
    
    try:
        choices = [int(x.strip()) for x in user_input.split(',')]
        pm.load_modules(choices)
    except ValueError:
        print("[!] 입력 형식이 잘못되었습니다.")
        return

    opts = options.Options(listen_host='127.0.0.1', listen_port=8080)
    master = DumpMaster(opts)
    master.addons.add(pm)
    
    print(f"[*] Proxy Server Running on 127.0.0.1:8080...")
    try: await master.run()
    except KeyboardInterrupt: master.shutdown()

if __name__ == "__main__":
    asyncio.run(start_engine())
