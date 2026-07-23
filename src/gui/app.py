"""GUI アプリのエントリポイント。"""
from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from src.config.loader import load_config
from src.usecase.runner import run_all, run_build, run_export_data, run_fetch_source


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("EC Mockup ツール")
        self.resizable(True, True)
        self.minsize(640, 500)

        self._q: queue.Queue[tuple[str, str]] = queue.Queue()
        self._running = False

        self._build_ui()
        self._load_env()
        self.after(100, self._poll_queue)

    # ------------------------------------------------------------------
    # UI 構築
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        # --- 設定フレーム ---
        cfg_frame = ttk.LabelFrame(self, text="設定", padding=8)
        cfg_frame.pack(fill="x", padx=10, pady=6)

        fields: list[tuple[str, str, bool]] = [
            ("GitHub リポジトリ", "github_repo", False),
            ("GitHub Ref (ブランチ/タグ)", "github_ref", False),
            ("ECDB API URL", "ecdb_url", False),
            ("ECDB API Key", "ecdb_key", True),
            ("MakeShop 公開 URL", "makeshop_url", False),
            ("Live Site URL", "live_url", False),
        ]

        self._vars: dict[str, tk.StringVar] = {}
        for row, (label, key, secret) in enumerate(fields):
            ttk.Label(cfg_frame, text=label).grid(row=row, column=0, sticky="w", **pad)
            var = tk.StringVar()
            self._vars[key] = var
            show = "*" if secret else ""
            entry = ttk.Entry(cfg_frame, textvariable=var, width=52, show=show)
            entry.grid(row=row, column=1, sticky="ew", **pad)
        cfg_frame.columnconfigure(1, weight=1)

        # --- 操作フレーム ---
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=4)

        self._btn_all = ttk.Button(btn_frame, text="▶ フルビルド", command=self._on_full_build)
        self._btn_all.pack(side="left", padx=4)

        self._btn_fetch = ttk.Button(btn_frame, text="ソース取得のみ", command=self._on_fetch_source)
        self._btn_fetch.pack(side="left", padx=4)

        self._btn_build = ttk.Button(btn_frame, text="ビルドのみ", command=self._on_build_only)
        self._btn_build.pack(side="left", padx=4)

        self._btn_open = ttk.Button(btn_frame, text="出力を開く", command=self._on_open_output)
        self._btn_open.pack(side="right", padx=4)

        # --- 進捗バー ---
        self._progress = ttk.Progressbar(self, mode="indeterminate")
        self._progress.pack(fill="x", padx=10, pady=2)

        # --- ログ ---
        log_frame = ttk.LabelFrame(self, text="ログ", padding=4)
        log_frame.pack(fill="both", expand=True, padx=10, pady=4)
        self._log = scrolledtext.ScrolledText(
            log_frame, state="disabled", height=14, wrap="word",
            font=("Consolas", 9),
        )
        self._log.pack(fill="both", expand=True)

        # ステータスバー
        self._status_var = tk.StringVar(value="準備完了")
        ttk.Label(self, textvariable=self._status_var, anchor="w").pack(
            fill="x", padx=10, pady=2
        )

    # ------------------------------------------------------------------
    # .env 読み込みで初期値セット
    # ------------------------------------------------------------------

    def _load_env(self) -> None:
        try:
            cfg = load_config()
            self._vars["github_repo"].set(cfg.github_repository)
            self._vars["github_ref"].set(cfg.github_ref)
            self._vars["ecdb_url"].set(cfg.ecdb_api_base_url)
            self._vars["ecdb_key"].set(cfg.ecdb_api_key)
            self._vars["makeshop_url"].set(cfg.makeshop_public_base_url)
            self._vars["live_url"].set(cfg.live_site_base_url)
            self._log_append("[INFO] .env を読み込みました")
        except Exception as e:
            self._log_append(f"[WARN] .env 読み込み失敗: {e}")

    # ------------------------------------------------------------------
    # ボタンハンドラ
    # ------------------------------------------------------------------

    def _on_full_build(self) -> None:
        self._run_async(lambda cfg, cb: run_all(cfg, on_progress=cb))

    def _on_fetch_source(self) -> None:
        self._run_async(lambda cfg, cb: run_fetch_source(cfg, on_progress=cb))

    def _on_build_only(self) -> None:
        self._run_async(lambda cfg, cb: run_build(cfg, on_progress=cb))

    def _on_open_output(self) -> None:
        try:
            cfg = load_config()
            out = cfg.app_output_dir
            if out.exists():
                os.startfile(str(out))
            else:
                messagebox.showwarning("未生成", f"出力ディレクトリが存在しません:\n{out}")
        except Exception as e:
            messagebox.showerror("エラー", str(e))

    # ------------------------------------------------------------------
    # 非同期実行
    # ------------------------------------------------------------------

    def _run_async(self, task) -> None:
        if self._running:
            messagebox.showwarning("実行中", "処理が完了するまでお待ちください")
            return
        self._running = True
        self._set_buttons_state("disabled")
        self._progress.start(10)
        self._status_var.set("実行中...")
        self._log_append("=" * 50)

        def worker() -> None:
            try:
                cfg = load_config()
                def on_progress(step: str, msg: str) -> None:
                    self._q.put((step, msg))
                task(cfg, on_progress)
                self._q.put(("__done__", "完了しました"))
            except Exception as e:
                self._q.put(("__error__", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------
    # キューポーリング（メインスレッドで UI 更新）
    # ------------------------------------------------------------------

    def _poll_queue(self) -> None:
        try:
            while True:
                step, msg = self._q.get_nowait()
                if step == "__done__":
                    self._on_task_done(msg)
                elif step == "__error__":
                    self._on_task_error(msg)
                else:
                    self._log_append(f"[{step}] {msg}")
                    self._status_var.set(msg[:80])
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _on_task_done(self, msg: str) -> None:
        self._progress.stop()
        self._running = False
        self._set_buttons_state("normal")
        self._status_var.set("完了")
        self._log_append(f"✓ {msg}")

    def _on_task_error(self, msg: str) -> None:
        self._progress.stop()
        self._running = False
        self._set_buttons_state("normal")
        self._status_var.set("エラー")
        self._log_append(f"[ERROR] {msg}")
        messagebox.showerror("エラー", msg)

    # ------------------------------------------------------------------
    # ユーティリティ
    # ------------------------------------------------------------------

    def _log_append(self, text: str) -> None:
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _set_buttons_state(self, state: str) -> None:
        for btn in (self._btn_all, self._btn_fetch, self._btn_build):
            btn.configure(state=state)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
