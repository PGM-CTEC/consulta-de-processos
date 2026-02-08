"""
Consulta Processual - Launcher
Inicia automaticamente backend e frontend
"""
import os
import sys
import subprocess
import time
import webbrowser
import threading
import socket
from pathlib import Path

# Configurações
DEFAULT_BACKEND_PORT = 8010
DEFAULT_FRONTEND_PORT = 5173

class ConsultaProcessualLauncher:
    def __init__(self):
        if getattr(sys, "frozen", False):
            self.base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
        else:
            self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.python_cmd = None
        self.npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        self.cleaned_up = False
        self.skip_frontend = False
        self.backend_port = self._find_available_port(DEFAULT_BACKEND_PORT)
        self.backend_url = f"http://127.0.0.1:{self.backend_port}"
        self.frontend_port = self._find_available_port(DEFAULT_FRONTEND_PORT)
        self.frontend_url = f"http://localhost:{self.frontend_port}"

    def print_header(self):
        """Exibe cabeçalho da aplicação"""
        print("=" * 60)
        print("     CONSULTA PROCESSUAL - Sistema DataJud")
        print("=" * 60)
        print()

    def pause(self, message: str = "\nPressione Enter para sair..."):
        """Pausa a execucao apenas em modo interativo."""
        if sys.stdin.isatty():
            input(message)

    def _is_port_in_use(self, port: int) -> bool:
        def _check(addr: str, family: int) -> bool:
            try:
                with socket.socket(family, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.2)
                    return sock.connect_ex((addr, port)) == 0
            except OSError:
                return False

        if _check("127.0.0.1", socket.AF_INET):
            return True
        # Também verifica IPv6 local, pois o Vite pode bindar em ::1
        if _check("::1", socket.AF_INET6):
            return True
        return False

    def _find_available_port(self, start_port: int, max_tries: int = 10) -> int:
        port = start_port
        for _ in range(max_tries):
            if not self._is_port_in_use(port):
                return port
            port += 1
        return start_port

    def check_python(self):
        """Verifica se Python esta instalado"""
        print("[1/6] Verificando Python...")
        candidates = [
            (["python"], "python"),
            (["py", "-3"], "py -3"),
        ]
        for cmd, label in candidates:
            try:
                result = subprocess.run(
                    cmd + ["--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                version = (result.stdout or result.stderr).strip()
                print(f"[OK] Python {version} encontrado ({label})")
                self.python_cmd = cmd
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        print("[!] Python nao encontrado!")
        print("   Por favor, instale Python de: https://www.python.org/downloads/")
        return False

    def check_node(self):
        """Verifica se Node.js esta instalado"""
        print("\n[2/6] Verificando Node.js...")
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print(f"[OK] Node.js {version} encontrado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[!] Node.js nao encontrado!")
            print("   Por favor, instale Node.js de: https://nodejs.org/")
            return False

        try:
            result = subprocess.run(
                [self.npm_cmd, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            npm_version = result.stdout.strip()
            print(f"[OK] npm {npm_version} encontrado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[!] npm nao encontrado!")
            print("   Verifique a instalacao do Node.js e o PATH do npm.")
            return False

        # Verifica se o Node consegue criar processos filhos (necessario para Vite/esbuild)
        try:
            result = subprocess.run(
                [
                    "node",
                    "-e",
                    "const {spawn}=require('child_process');"
                    "const cp=spawn(process.platform==='win32'?'cmd.exe':'sh',"
                    "[process.platform==='win32'?'/c':'-c','exit 0']);"
                    "cp.on('error',e=>{console.error(e.code||'spawn_error');process.exit(1)});"
                    "cp.on('exit',code=>process.exit(code||0));",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print("[!] Node bloqueado para criar processos filhos (spawn EPERM).")
                print("   O Vite/esbuild nao conseguira iniciar nesta maquina.")
                print("   Continuarei apenas com o backend.")
                self.skip_frontend = True
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[!] Falha ao validar execucao de processos filhos no Node.")
            return False

    def install_backend_deps(self):
        """Instala dependências do backend"""
        print("\n[3/6] Instalando dependencias do backend...")
        
        # Tenta usar o venv se existir
        pip_cmd = self.python_cmd + ["-m", "pip"]
        venv_pip = self.backend_dir / "venv" / "Scripts" / "pip.exe"
        if venv_pip.exists():
            pip_cmd = [str(venv_pip)]
            print(f"Uso de venv detectado: {venv_pip}")

        try:
            requirements_file = "requirements-runtime.txt"
            if not (self.backend_dir / requirements_file).exists():
                requirements_file = "requirements.txt"
            subprocess.run(
                pip_cmd + ["install", "-r", requirements_file],
                cwd=self.backend_dir,
                check=True
            )
            print("[OK] Dependencias do backend instaladas")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Erro ao instalar dependencias do backend: {e}")
            return False

    def install_frontend_deps(self):
        """Instala dependências do frontend"""
        print("\n[4/6] Instalando dependências do frontend...")

        # Verifica se node_modules existe
        node_modules = self.frontend_dir / "node_modules"
        if node_modules.exists():
            print("[OK] Dependencias do frontend ja instaladas")
            return True

        try:
            subprocess.run(
                [self.npm_cmd, "install"],
                cwd=self.frontend_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("[OK] Dependencias do frontend instaladas")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERRO] Erro ao instalar dependencias do frontend: {e}")
            return False

    def start_backend(self):
        """Inicia servidor backend"""
        print("\n[5/6] Iniciando servidor backend...")
        
        # Tenta usar o python do venv se existir
        python_cmd = self.python_cmd
        venv_python = self.backend_dir / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            python_cmd = [str(venv_python)]
            print(f"Uso de venv detectado: {venv_python}")

        try:
            self.backend_process = subprocess.Popen(
                python_cmd + [
                    "-m",
                    "uvicorn",
                    "backend.main:app",
                    "--port",
                    str(self.backend_port),
                    "--host",
                    "127.0.0.1",
                    "--reload",
                ],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            time.sleep(3)  # Aguarda backend iniciar

            if self.backend_process.poll() is None:
                print(f"[OK] Backend rodando em {self.backend_url}")
                return True
            else:
                stdout, stderr = self.backend_process.communicate(timeout=1)
                if stdout:
                    print((stdout or "").strip())
                if stderr:
                    print((stderr or "").strip())
                print("[ERRO] Backend falhou ao iniciar")
                return False
        except Exception as e:
            print(f"[ERRO] Erro ao iniciar backend: {e}")
            return False

    def start_frontend(self):
        """Inicia servidor frontend"""
        print("\n[6/6] Iniciando servidor frontend...")
        try:
            # Define variável de ambiente para não abrir navegador automaticamente
            env = os.environ.copy()
            env["BROWSER"] = "none"
            env["VITE_BACKEND_URL"] = self.backend_url

            self.frontend_process = subprocess.Popen(
                [self.npm_cmd, "run", "dev", "--", "--port", str(self.frontend_port), "--strictPort"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            time.sleep(5)  # Aguarda frontend iniciar

            if self.frontend_process.poll() is None:
                print(f"[OK] Frontend rodando em {self.frontend_url}")
                return True
            else:
                stdout, stderr = self.frontend_process.communicate(timeout=1)
                if stdout:
                    print((stdout or "").strip())
                if stderr:
                    print((stderr or "").strip())
                print("[ERRO] Frontend falhou ao iniciar")
                return False
        except Exception as e:
            print(f"[ERRO] Erro ao iniciar frontend: {e}")
            return False

    def open_browser(self):
        """Abre navegador com a aplicação"""
        print(f"\n{'='*60}")
        print("[OK] APLICACAO INICIADA COM SUCESSO!")
        print(f"{'='*60}")
        print(f"\nAbrindo navegador em: {self.frontend_url}")
        print("\nPara encerrar a aplicação, feche esta janela ou pressione Ctrl+C")
        print(f"{'='*60}\n")

        time.sleep(2)
        webbrowser.open(self.frontend_url)

    def cleanup(self):
        """Encerra processos ao sair"""
        if self.cleaned_up:
            return
        self.cleaned_up = True
        print("\n\nEncerrando aplicação...")

        if self.backend_process:
            print("  Parando backend...")
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except Exception:
                pass

        if self.frontend_process:
            print("  Parando frontend...")
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except Exception:
                pass

        print("\n[OK] Aplicacao encerrada com sucesso!")

    def run(self):
        """Executa o launcher"""
        try:
            self.print_header()

            # Verificações
            if not self.check_python():
                self.pause()
                return False

            if not self.check_node():
                self.pause()
                return False

            # Instalação de dependências
            if not self.install_backend_deps():
                self.pause()
                return False

            if not self.skip_frontend:
                if not self.install_frontend_deps():
                    self.pause()
                    return False

            # Iniciar servidores
            if not self.start_backend():
                self.pause()
                return False

            if not self.skip_frontend:
                if not self.start_frontend():
                    self.cleanup()
                    self.pause()
                    return False

            # Abrir navegador
            if not self.skip_frontend:
                self.open_browser()
            else:
                print(f"\n[OK] Backend rodando em {self.backend_url}")
                print("[!] Frontend nao iniciado devido a restricao de spawn no Node.")
                print("   Inicie o frontend em um ambiente sem essa restricao.")

            # Manter rodando
            try:
                while True:
                    time.sleep(1)
                    # Verifica se processos ainda estão rodando
                    if self.backend_process.poll() is not None:
                        print("\n[!] Backend parou inesperadamente!")
                        break
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        print("\n[!] Frontend parou inesperadamente!")
                        break
            except KeyboardInterrupt:
                print("\n\nInterrompido pelo usuário...")

            return True

        except Exception as e:
            print(f"\n[ERRO] Erro inesperado: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.cleanup()
            self.pause()


if __name__ == "__main__":
    launcher = ConsultaProcessualLauncher()
    sys.exit(0 if launcher.run() else 1)
