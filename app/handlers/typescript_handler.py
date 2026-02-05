import os
import json
import subprocess
import re
import shutil
from typing import List, Dict, Any
from .base import BaseRunner


class TypeScriptRunner(BaseRunner):

    def __init__(self):
        super().__init__()
        self.npm_path = shutil.which("npm")
        self.npx_path = shutil.which("npx")
        if not self.npm_path or not self.npx_path:
            raise RuntimeError("npm and npx must be installed and available in PATH")

    def get_dependencies(self, code: str) -> List[str]:
        dependencies = set()
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            r'import\s*{\s*.*\s*}\s*from\s*[\'"]([^\'"]+)[\'"]'
        ]

        for pattern in import_patterns:
            for match in re.finditer(pattern, code):
                dep = match.group(1)
                if not dep.startswith((".", "/")):
                    dependencies.add(dep.split("/")[0])

        dependencies.update(["typescript", "ts-node"])
        return list(dependencies)

    def install_dependencies(self, dependencies: List[str], workspace_path: str):
        if not dependencies:
            return

        package_json = {
            "dependencies": {dep: "latest" for dep in dependencies}
        }

        tsconfig = {
            "compilerOptions": {
                "target": "es2016",
                "module": "commonjs",
                "esModuleInterop": True,
                "forceConsistentCasingInFileNames": True,
                "strict": True,
                "skipLibCheck": True
            }
        }

        with open(os.path.join(workspace_path, "package.json"), "w") as f:
            json.dump(package_json, f)

        with open(os.path.join(workspace_path, "tsconfig.json"), "w") as f:
            json.dump(tsconfig, f)

        npm_env = {
            **os.environ,
            "HOME": "/tmp",
            "NPM_CONFIG_CACHE": "/tmp/.npm",
            "NO_UPDATE_NOTIFIER": "1"
        }

        npm_args = [
            "install",
            "--no-audit",
            "--no-fund",
            "--no-optional",
            "--production",
            "--silent"
        ]

        try:
            subprocess.run(
                [self.npm_path] + npm_args,
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
                env=npm_env
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"npm install failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            raise RuntimeError("npm install timed out")

    def _get_file_extension(self) -> str:
        return ".ts"

    def _prepare_code(
        self,
        code: str,
        inputs: Dict[str, Any],
        env_vars: Dict[str, str]
    ) -> str:
        env_code = "\n".join(
            [f"process.env['{k}'] = '{v}';" for k, v in env_vars.items()]
        )

        input_lines = []
        for k, v in inputs.items():
            input_lines.append(f"const {k}: any = {json.dumps(v)};")

        header = "\n".join(input_lines + ([env_code] if env_code else []))
        if header:
            code = f"{header}\n{code}"

        code += """
let result: any = null;
try {
    if (typeof (globalThis as any).output !== 'undefined') {
        result = (globalThis as any).output;
    }
} catch (error) {
    console.error('Error capturing result:', error);
}

console.log('__RESULT_START__');
console.log(JSON.stringify(result));
console.log('__RESULT_END__');
"""
        return code

    def _run_directly(
        self,
        code_file_path: str,
        inputs: Dict[str, Any],
        env_vars: Dict[str, str],
        execution_timeout: int
    ) -> subprocess.CompletedProcess:
        workspace = os.path.dirname(code_file_path)
        self.install_dependencies(["typescript", "ts-node"], workspace)
        return self._run_ts_node(code_file_path, workspace, env_vars, execution_timeout)

    def _run_with_dependencies(
        self,
        code_file_path: str,
        dependencies: List[str],
        inputs: Dict[str, Any],
        env_vars: Dict[str, str],
        execution_timeout: int
    ) -> subprocess.CompletedProcess:
        workspace = os.path.dirname(code_file_path)
        self.install_dependencies(dependencies, workspace)
        return self._run_ts_node(code_file_path, workspace, env_vars, execution_timeout)

    def _run_ts_node(
        self,
        code_file_path: str,
        workspace: str,
        env_vars: Dict[str, str],
        execution_timeout: int
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            [self.npx_path, "ts-node", code_file_path],
            capture_output=True,
            text=True,
            timeout=execution_timeout,
            cwd=workspace,
            env={**os.environ, **env_vars}
        )

    def _process_output(self, stdout: str) -> tuple[str, Dict[str, Any]]:
        try:
            parts = stdout.split("__RESULT_START__")
            if len(parts) != 2:
                return stdout, {}

            normal_output = parts[0].strip()
            result_part = parts[1].split("__RESULT_END__")[0].strip()

            try:
                result_data = json.loads(result_part) if result_part else {}
            except json.JSONDecodeError:
                result_data = {}

            return normal_output, result_data
        except Exception:
            return stdout, {}
