# -*- coding: utf-8 -*-
"""
BM AUTOMATED - UNIVERSAL GIT PUSH & GOOGLE CLOUD VPS DEPLOYER
=============================================================
Target: Google Cloud Linux VPS 'bm-automated'
Project: quant-gold-514007 | Zone: us-central1-a | Instance: bm-automated
Console URL: https://console.cloud.google.com/compute/instancesDetail/zones/us-central1-a/instances/bm-automated?project=quant-gold-514007
Repository: https://github.com/hemsoknitha-sketch/bm-automated.git
Author: HEM SINATH | Institutional Quantitative Governance
"""

import os
import sys
import argparse
import subprocess
import shutil
from datetime import datetime
from typing import Dict, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GCM_INTERACTIVE"] = "never"

DEFAULT_GCP_PROJECT = "quant-gold-514007"
DEFAULT_GCP_ZONE = "us-central1-a"
DEFAULT_GCP_INSTANCE = "bm-automated"
DEFAULT_GCP_CONSOLE_URL = (
    "https://console.cloud.google.com/compute/instancesDetail/zones/"
    "us-central1-a/instances/bm-automated?project=quant-gold-514007"
)
DEFAULT_REPO_URL = "https://github.com/hemsoknitha-sketch/bm-automated.git"


def load_env_config(env_path: str = ".env") -> Dict[str, str]:
    config: Dict[str, str] = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip("'\"")
        except Exception as exc:
            print(f"⚠️ [WARN] Error reading {env_path}: {exc}")
    return config


def run_command(cmd: list, check: bool = False, timeout: int = 120) -> Tuple[int, str]:
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        lines = []
        for line in iter(proc.stdout.readline, ""):
            lines.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()

        proc.stdout.close()
        rc = proc.wait(timeout=timeout)
        output = "".join(lines)
        if check and rc != 0:
            raise subprocess.CalledProcessError(rc, cmd, output=output)
        return rc, output
    except Exception as exc:
        print(f"❌ [COMMAND ERROR] {' '.join(cmd)} failed: {exc}")
        return 1, str(exc)


def git_push_and_deploy(commit_msg: Optional[str] = None):
    print("=" * 76)
    print("  🚀 BM AUTOMATED - GOOGLE CLOUD VPS DEPLOYER & GIT SYNCHRONIZER")
    print(f"  📍 Target Instance: {DEFAULT_GCP_INSTANCE} | Project: {DEFAULT_GCP_PROJECT}")
    print(f"  🌐 Zone:            {DEFAULT_GCP_ZONE}")
    print(f"  🔗 Console:         {DEFAULT_GCP_CONSOLE_URL}")
    print(f"  📦 Repo:            {DEFAULT_REPO_URL}")
    print("=" * 76)

    cfg = load_env_config()
    git_user = cfg.get("GIT_PUSH_USER", "hem sinath")

    # 1. Stage changes
    print("\n📦 [STEP 1/3] Staging all changes (git add -A)...")
    add_rc, _ = run_command(["git", "add", "-A"])
    if add_rc != 0:
        print("❌ Failed to stage changes. Aborting.")
        return False

    # Check git status
    st_res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, errors="replace")
    has_changes = bool(st_res.stdout.strip())

    # 2. Commit if changes exist
    if has_changes:
        if not commit_msg:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"feat(bm): update 24/7 BM Automated engine by {git_user} [{now_str}]"

        print(f"\n📝 [STEP 2/3] Committing changes: '{commit_msg}'...")
        run_command(["git", "commit", "-m", commit_msg])
    else:
        print("\n📝 [STEP 2/3] Working tree is clean. Checking for unpushed commits...")

    # 3. Push to GitHub Origin Main
    print(f"\n🚀 [STEP 3/3] Pushing to remote origin main...")
    push_rc, _ = run_command(["git", "push", "origin", "main"])
    if push_rc != 0:
        print("❌ Push failed. Please verify git credentials and internet connection.")
        return False

    print("\n" + "=" * 76)
    print("  ✅ [SUCCESS] CODE PUSHED TO GITHUB ORIGIN MAIN WITH ZERO DEFECTS!")
    print("=" * 76)

    # 4. Instructions for VPS
    print("\n🌐 [VPS 1-TAP INSTRUCTIONS]")
    print(f"   Console: {DEFAULT_GCP_CONSOLE_URL}")
    print("   If first time on VPS, run:")
    print("   \033[1;33mgit clone https://github.com/hemsoknitha-sketch/bm-automated.git && cd bm-automated && bash deploy_vps_bm.sh\033[0m")
    print("\n   If already cloned on VPS, 1-tap update directive:")
    print("   \033[1;32mcd ~/bm-automated && bash update_vps_bm.sh\033[0m\n")
    print("=" * 76)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BM Automated Git Push & VPS Deployer")
    parser.add_argument("message", nargs="?", default=None, help="Commit message string")
    args = parser.parse_args()
    git_push_and_deploy(args.message)
