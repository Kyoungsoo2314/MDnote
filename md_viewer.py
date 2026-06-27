#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MDnote - Lightweight Markdown Viewer
더블 클릭으로 .md 파일을 바로 볼 수 있는 데스크톱 뷰어
v3.0 - 탭, 폴더 트리, 드래그앤드롭 지원
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import re
import json

# 드래그앤드롭 지원 (옵션)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False


# 테마 색상 정의
DARK_THEME = {
    'bg': '#1e1e2e',
    'fg': '#cdd6f4',
    'h1': '#89b4fa',
    'h2': '#89b4fa',
    'h3': '#89dceb',
    'h4': '#a6e3a1',
    'h5': '#94e2d5',
    'h6': '#89b4fa',
    'emphasis': '#f38ba8',
    'code': '#f5c2e7',
    'code_bg': '#313244',
    'link': '#89dceb',
    'quote': '#a6adc8',
    'list': '#fab387',
    'hr': '#45475a',
    'checkbox': '#a6e3a1',
    'strikethrough': '#6c7086',
    'select_bg': '#45475a',
    'tree_bg': '#181825',
    'tree_fg': '#cdd6f4',
    'tree_select': '#313244',
    'tab_bg': '#313244',
    'tab_active': '#45475a',
}

LIGHT_THEME = {
    'bg': '#eff1f5',
    'fg': '#4c4f69',
    'h1': '#1e66f5',
    'h2': '#1e66f5',
    'h3': '#04a5e5',
    'h4': '#40a02b',
    'h5': '#179299',
    'h6': '#1e66f5',
    'emphasis': '#d20f39',
    'code': '#8839ef',
    'code_bg': '#dce0e8',
    'link': '#04a5e5',
    'quote': '#7c7f93',
    'list': '#fe640b',
    'hr': '#9ca0b0',
    'checkbox': '#40a02b',
    'strikethrough': '#9ca0b0',
    'select_bg': '#ccd0da',
    'tree_bg': '#e6e9ef',
    'tree_fg': '#4c4f69',
    'tree_select': '#ccd0da',
    'tab_bg': '#dce0e8',
    'tab_active': '#ccd0da',
}


class Config:
    """설정 관리 클래스"""

    def __init__(self):
        self.config_dir = Path.home() / 'AppData' / 'Roaming' / 'MDnote'
        self.config_file = self.config_dir / 'config.json'
        self.recent_file = self.config_dir / 'recent.json'
        self.config = self.load_config()
        self.recent_files = self.load_recent_files()

    def load_config(self):
        """설정 파일 로드"""
        default_config = {
            'theme': 'dark',
            'font_size': 11,
            'always_on_top': False,
            'sidebar_width': 200,
            'last_folder': '',
        }

        # 설정 디렉토리 생성 (앱 시작 시 확실히 생성)
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Failed to create config directory: {e}")

        if not self.config_file.exists():
            # 기본 설정 저장
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Failed to save default config: {e}")
            return default_config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return {**default_config, **json.load(f)}
        except:
            return default_config

    def save_config(self):
        """설정 파일 저장"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def load_recent_files(self):
        """최근 파일 목록 로드"""
        if not self.recent_file.exists():
            return []

        try:
            with open(self.recent_file, 'r', encoding='utf-8') as f:
                files = json.load(f)
                return [f for f in files if Path(f).exists()][:10]
        except:
            return []

    def add_recent_file(self, file_path):
        """최근 파일에 추가"""
        file_path = str(file_path)

        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]

        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.recent_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_files, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save recent files: {e}")


class TabInfo:
    """탭 정보 저장 클래스"""

    def __init__(self, file_path=None, content="", frame=None, text_widget=None):
        self.file_path = file_path
        self.content = content
        self.edit_mode = False
        self.has_unsaved_changes = False
        self.frame = frame
        self.text_widget = text_widget


class MarkdownViewer:
    def __init__(self, root, file_path=None):
        self.root = root
        self.root.title("MDnote")
        self.root.geometry("1200x800")

        # 아이콘 설정
        icon_path = Path(__file__).parent / 'md_viewer.ico'
        if icon_path.exists():
            try:
                self.root.iconbitmap(str(icon_path))
            except:
                pass

        # 설정 로드
        self.config = Config()
        self.tabs = {}  # tab_id -> TabInfo
        self.current_folder = None

        # 테마 설정
        self.themes = {'dark': DARK_THEME, 'light': LIGHT_THEME}
        self.current_theme = self.config.config['theme']
        self.colors = self.themes[self.current_theme]

        # 폰트 크기
        self.font_size = self.config.config['font_size']

        # 항상 위 설정
        if self.config.config['always_on_top']:
            self.root.attributes('-topmost', True)

        # 창 닫기 이벤트
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # 스타일 설정
        self.setup_styles()

        # 메뉴바 생성
        self.create_menu()

        # UI 구성
        self.create_ui()

        # 드래그앤드롭 설정
        self.setup_drag_and_drop()

        # 파일이 주어진 경우 열기
        if file_path:
            self.open_file(file_path)

    def setup_styles(self):
        """ttk 스타일 설정"""
        style = ttk.Style()
        style.theme_use('clam')  # clam 테마 사용 (배경색 적용 가능)

        # 노트북 스타일 - 배경색 통일
        style.configure('Custom.TNotebook',
                        background=self.colors['tree_bg'],
                        borderwidth=0,
                        tabmargins=[0, 5, 0, 0])

        # 노트북 탭 영역 배경
        style.configure('Custom.TNotebook.Tab',
                        background=self.colors['tree_bg'],
                        foreground=self.colors['quote'],
                        padding=[15, 6],
                        font=('맑은 고딕', 10))

        style.map('Custom.TNotebook.Tab',
                  background=[('selected', self.colors['bg'])],
                  foreground=[('selected', self.colors['fg'])],
                  expand=[('selected', [0, 0, 0, 2])])

        # 트리뷰 스타일
        style.configure('Dark.Treeview',
                        background=self.colors['tree_bg'],
                        foreground=self.colors['tree_fg'],
                        fieldbackground=self.colors['tree_bg'],
                        font=('Segoe UI Emoji', 9))
        style.map('Dark.Treeview',
                  background=[('selected', self.colors['tree_select'])])

        # 스크롤바 스타일
        style.configure('Vertical.TScrollbar',
                        background=self.colors['tree_bg'],
                        troughcolor=self.colors['bg'])

    def create_ui(self):
        """UI 생성"""
        # 메인 프레임
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # PanedWindow (사이드바 + 콘텐츠)
        self.paned = tk.PanedWindow(
            self.main_frame,
            orient=tk.HORIZONTAL,
            bg=self.colors['bg'],
            sashwidth=4,
            sashrelief=tk.FLAT
        )
        self.paned.pack(fill=tk.BOTH, expand=True)

        # 사이드바 (폴더 트리)
        self.create_sidebar()

        # 콘텐츠 영역 (탭 + 텍스트)
        self.create_content_area()

        # 상태바
        self.create_status_bar()

    def create_sidebar(self):
        """사이드바 (폴더 트리) 생성"""
        sidebar_width = self.config.config.get('sidebar_width', 200)

        self.sidebar_frame = tk.Frame(self.paned, bg=self.colors['tree_bg'], width=sidebar_width)

        # 폴더 헤더
        header_frame = tk.Frame(self.sidebar_frame, bg=self.colors['tree_bg'])
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        self.folder_label = tk.Label(
            header_frame,
            text="폴더를 열어주세요",
            bg=self.colors['tree_bg'],
            fg=self.colors['tree_fg'],
            font=("맑은 고딕", 9),
            anchor="w"
        )
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 트리뷰
        tree_frame = tk.Frame(self.sidebar_frame, bg=self.colors['tree_bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        self.tree = ttk.Treeview(tree_frame, show='tree', style='Dark.Treeview')
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 트리뷰 이벤트
        self.tree.bind('<Double-1>', self.on_tree_double_click)

        self.paned.add(self.sidebar_frame, minsize=150)

    def create_content_area(self):
        """콘텐츠 영역 (탭 노트북) 생성"""
        self.content_frame = tk.Frame(self.paned, bg=self.colors['tree_bg'])

        # 탭 노트북
        self.notebook = ttk.Notebook(self.content_frame, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 탭 변경 이벤트
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # 탭 닫기 (마우스 중간 클릭)
        self.notebook.bind('<Button-2>', self.on_tab_middle_click)

        self.paned.add(self.content_frame, minsize=400)

    def create_status_bar(self):
        """상태바 생성"""
        self.status_bar = tk.Label(
            self.main_frame,
            text="Ready",
            anchor="w",
            fg=self.colors['quote'],
            bg=self.colors['bg'],
            font=("Consolas", 9),
            padx=10,
            pady=3
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_drag_and_drop(self):
        """드래그앤드롭 설정"""
        if HAS_DND:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        """드래그앤드롭 이벤트 처리"""
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            if file_path.lower().endswith('.md'):
                self.open_file(file_path)
            elif os.path.isdir(file_path):
                self.open_folder(file_path)

    def create_menu(self):
        """메뉴 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="파일 열기 (Ctrl+O)", command=self.open_file_dialog)
        file_menu.add_command(label="폴더 열기 (Ctrl+Shift+O)", command=self.open_folder_dialog)

        # 최근 파일 서브메뉴
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="최근 파일", menu=self.recent_menu)
        self.update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="저장 (Ctrl+S)", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="탭 닫기 (Ctrl+W)", command=self.close_current_tab)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.quit_app)

        # 보기 메뉴
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="보기", menu=view_menu)

        # 테마 서브메뉴
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="테마", menu=theme_menu)
        theme_menu.add_command(label="다크 테마", command=lambda: self.switch_theme('dark'))
        theme_menu.add_command(label="라이트 테마", command=lambda: self.switch_theme('light'))
        theme_menu.add_separator()
        theme_menu.add_command(label="테마 전환 (Ctrl+T)", command=self.toggle_theme)

        # 폰트 크기 서브메뉴
        font_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="폰트 크기", menu=font_menu)
        font_menu.add_command(label="크게 (Ctrl++)", command=self.increase_font_size)
        font_menu.add_command(label="작게 (Ctrl+-)", command=self.decrease_font_size)
        font_menu.add_command(label="기본 (Ctrl+0)", command=self.reset_font_size)

        view_menu.add_separator()
        view_menu.add_command(label="편집 모드 (Ctrl+E)", command=self.toggle_edit_mode)
        view_menu.add_separator()
        view_menu.add_command(label="항상 위", command=self.toggle_always_on_top)

        # 단축키 바인딩
        self.root.bind('<Control-o>', lambda e: self.open_file_dialog())
        self.root.bind('<Control-O>', lambda e: self.open_folder_dialog())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-e>', lambda e: self.toggle_edit_mode())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<Control-w>', lambda e: self.close_current_tab())
        self.root.bind('<Control-plus>', lambda e: self.increase_font_size())
        self.root.bind('<Control-equal>', lambda e: self.increase_font_size())
        self.root.bind('<Control-minus>', lambda e: self.decrease_font_size())
        self.root.bind('<Control-0>', lambda e: self.reset_font_size())
        self.root.bind('<Control-Tab>', lambda e: self.next_tab())
        self.root.bind('<Control-Shift-Tab>', lambda e: self.prev_tab())

    def update_recent_menu(self):
        """최근 파일 메뉴 업데이트"""
        self.recent_menu.delete(0, tk.END)

        if not self.config.recent_files:
            self.recent_menu.add_command(label="(없음)", state=tk.DISABLED)
            return

        for file_path in self.config.recent_files:
            file_name = Path(file_path).name
            self.recent_menu.add_command(
                label=file_name,
                command=lambda fp=file_path: self.open_file(fp)
            )

    # ===== 탭 관리 =====

    def create_tab(self, file_path=None, content=""):
        """새 탭 생성"""
        # 탭 프레임
        tab_frame = tk.Frame(self.notebook, bg=self.colors['bg'])

        # 파일 경로 표시
        path_label = tk.Label(
            tab_frame,
            text=str(file_path) if file_path else "",
            anchor="w",
            fg=self.colors['quote'],
            bg=self.colors['bg'],
            font=("Consolas", 9)
        )
        path_label.pack(fill=tk.X, padx=15, pady=(10, 5))

        # 텍스트 위젯
        text_widget = scrolledtext.ScrolledText(
            tab_frame,
            wrap=tk.WORD,
            font=("맑은 고딕", self.font_size),
            padx=30,
            pady=25,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['select_bg'],
            selectforeground=self.colors['fg'],
            borderwidth=0,
            highlightthickness=0
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 텍스트 스타일 설정
        self.setup_text_styles(text_widget)

        # 탭 이름
        tab_name = Path(file_path).name if file_path else "새 탭"
        self.notebook.add(tab_frame, text=tab_name)

        # 탭 정보 저장
        tab_id = str(id(tab_frame))
        self.tabs[tab_id] = TabInfo(
            file_path=Path(file_path) if file_path else None,
            content=content,
            frame=tab_frame,
            text_widget=text_widget
        )

        # 탭 선택
        self.notebook.select(tab_frame)

        return tab_id

    def get_current_tab(self):
        """현재 선택된 탭 정보 반환"""
        try:
            current_frame = self.notebook.nametowidget(self.notebook.select())
            tab_id = str(id(current_frame))
            return self.tabs.get(tab_id)
        except:
            return None

    def get_tab_id_by_frame(self, frame):
        """프레임으로 탭 ID 찾기"""
        return str(id(frame))

    def close_current_tab(self):
        """현재 탭 닫기"""
        tab = self.get_current_tab()
        if not tab:
            return

        if tab.has_unsaved_changes:
            response = messagebox.askyesnocancel(
                "저장되지 않은 변경사항",
                "변경사항을 저장하시겠습니까?"
            )
            if response is None:
                return
            elif response:
                self.save_file()

        # 탭 제거
        tab_id = self.get_tab_id_by_frame(tab.frame)
        self.notebook.forget(tab.frame)
        del self.tabs[tab_id]

        self.update_title()

    def on_tab_changed(self, event):
        """탭 변경 이벤트"""
        self.update_title()
        self.update_status_bar()

    def on_tab_middle_click(self, event):
        """탭 중간 클릭으로 닫기"""
        try:
            clicked_tab = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
            if clicked_tab != '':
                self.notebook.select(clicked_tab)
                self.close_current_tab()
        except:
            pass

    def next_tab(self):
        """다음 탭으로 이동"""
        current = self.notebook.index(self.notebook.select())
        total = self.notebook.index("end")
        if total > 0:
            self.notebook.select((current + 1) % total)

    def prev_tab(self):
        """이전 탭으로 이동"""
        current = self.notebook.index(self.notebook.select())
        total = self.notebook.index("end")
        if total > 0:
            self.notebook.select((current - 1) % total)

    # ===== 폴더 트리 =====

    def open_folder_dialog(self):
        """폴더 열기 다이얼로그"""
        folder_path = filedialog.askdirectory(
            title="폴더 선택",
            initialdir=self.config.config.get('last_folder', '')
        )
        if folder_path:
            self.open_folder(folder_path)

    def open_folder(self, folder_path):
        """폴더 열기 및 트리 표시"""
        folder_path = Path(folder_path)
        if not folder_path.exists():
            return

        self.current_folder = folder_path
        self.config.config['last_folder'] = str(folder_path)
        self.config.save_config()

        # 폴더 레이블 업데이트
        self.folder_label.config(text=folder_path.name)

        # 트리 초기화 및 채우기
        self.populate_tree(folder_path)

    def populate_tree(self, folder_path, parent=''):
        """트리에 파일 목록 추가"""
        if parent == '':
            # 트리 초기화
            for item in self.tree.get_children():
                self.tree.delete(item)

        try:
            items = sorted(folder_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))

            for item in items:
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    # 폴더
                    node = self.tree.insert(parent, 'end', text=f"📁 {item.name}", open=False)
                    # 하위 항목 추가 (재귀)
                    self.populate_tree(item, node)
                elif item.suffix.lower() == '.md':
                    # 마크다운 파일
                    self.tree.insert(parent, 'end', text=f"📄 {item.name}", values=(str(item),))
        except PermissionError:
            pass

    def on_tree_double_click(self, event):
        """트리 더블클릭 이벤트"""
        item = self.tree.selection()
        if not item:
            return

        item = item[0]
        values = self.tree.item(item, 'values')

        if values:
            file_path = values[0]
            self.open_file(file_path)

    # ===== 파일 작업 =====

    def open_file_dialog(self):
        """파일 열기 다이얼로그"""
        file_path = filedialog.askopenfilename(
            title="Markdown 파일 선택",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            self.open_file(file_path)

    def open_file(self, file_path):
        """파일 열기"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{file_path}")
                return

            # 이미 열린 탭이 있는지 확인
            for tab_id, tab in self.tabs.items():
                if tab.file_path and tab.file_path == file_path:
                    # 이미 열린 탭 선택
                    self.notebook.select(tab.frame)
                    return

            # 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 새 탭 생성
            tab_id = self.create_tab(file_path, content)
            tab = self.tabs[tab_id]

            # 마크다운 렌더링
            self.render_markdown(tab.text_widget, content)

            # 해당 파일의 폴더를 사이드바에 자동 표시
            folder_path = file_path.parent
            if self.current_folder != folder_path:
                self.open_folder(folder_path)

            # 최근 파일에 추가
            self.config.add_recent_file(file_path)
            self.update_recent_menu()

            # 상태 업데이트
            self.update_title()
            self.update_status_bar()

        except Exception as e:
            messagebox.showerror("오류", f"파일을 열 수 없습니다:\n{str(e)}")

    def save_file(self):
        """현재 파일 저장"""
        tab = self.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showinfo("알림", "저장할 파일이 없습니다.")
            return

        if not tab.edit_mode:
            messagebox.showinfo("알림", "편집 모드에서만 저장할 수 있습니다.")
            return

        try:
            content = tab.text_widget.get(1.0, tk.END).rstrip('\n')

            with open(tab.file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            tab.content = content
            tab.has_unsaved_changes = False
            self.update_title()

            # 상태바에 저장 완료 메시지
            original_status = self.status_bar.cget("text")
            self.status_bar.config(text="✓ 저장 완료")
            self.root.after(2000, lambda: self.status_bar.config(text=original_status))

        except Exception as e:
            messagebox.showerror("오류", f"파일 저장 실패:\n{str(e)}")

    # ===== 편집 모드 =====

    def toggle_edit_mode(self):
        """편집 모드 전환"""
        tab = self.get_current_tab()
        if not tab or not tab.file_path:
            messagebox.showinfo("알림", "먼저 파일을 열어주세요.")
            return

        # 현재 스크롤 위치 저장
        scroll_pos = tab.text_widget.yview()[0]

        tab.edit_mode = not tab.edit_mode

        if tab.edit_mode:
            # 편집 모드로 전환
            tab.text_widget.config(state=tk.NORMAL)
            tab.text_widget.delete(1.0, tk.END)
            tab.text_widget.insert(1.0, tab.content)

            # 변경사항 추적
            tab.text_widget.bind('<<Modified>>', lambda e: self.on_text_modified(tab))

            self.update_title()

            # 스크롤 위치 복원
            tab.text_widget.update_idletasks()
            tab.text_widget.yview_moveto(scroll_pos)
        else:
            # 읽기 모드로 전환
            if tab.has_unsaved_changes:
                response = messagebox.askyesnocancel(
                    "저장되지 않은 변경사항",
                    "변경사항을 저장하시겠습니까?"
                )
                if response is None:
                    tab.edit_mode = True
                    return
                elif response:
                    self.save_file()

            # raw markdown 내용 업데이트
            tab.content = tab.text_widget.get(1.0, tk.END).rstrip('\n')

            # 렌더링 모드로 복귀
            self.render_markdown(tab.text_widget, tab.content)
            tab.has_unsaved_changes = False
            self.update_title()

            # 스크롤 위치 복원
            tab.text_widget.update_idletasks()
            tab.text_widget.yview_moveto(scroll_pos)

    def on_text_modified(self, tab):
        """텍스트 수정 감지"""
        if tab.edit_mode:
            tab.text_widget.edit_modified(False)
            tab.has_unsaved_changes = True
            self.update_title()

    # ===== 테마 및 폰트 =====

    def toggle_theme(self):
        """테마 전환"""
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.switch_theme(new_theme)

    def switch_theme(self, theme_name):
        """테마 변경"""
        if theme_name not in self.themes:
            return

        self.current_theme = theme_name
        self.colors = self.themes[theme_name]
        self.config.config['theme'] = theme_name
        self.config.save_config()

        # 스타일 재설정
        self.setup_styles()

        # UI 업데이트
        self.refresh_ui()

    def refresh_ui(self):
        """UI 새로고침"""
        # 메인 프레임
        self.main_frame.config(bg=self.colors['bg'])
        self.paned.config(bg=self.colors['bg'])

        # 사이드바
        self.sidebar_frame.config(bg=self.colors['tree_bg'])
        self.folder_label.config(bg=self.colors['tree_bg'], fg=self.colors['tree_fg'])

        # 콘텐츠
        self.content_frame.config(bg=self.colors['tree_bg'])

        # 상태바
        self.status_bar.config(bg=self.colors['bg'], fg=self.colors['quote'])

        # 모든 탭 업데이트
        for tab_id, tab in self.tabs.items():
            tab.frame.config(bg=self.colors['bg'])
            tab.text_widget.config(
                bg=self.colors['bg'],
                fg=self.colors['fg'],
                insertbackground=self.colors['fg'],
                selectbackground=self.colors['select_bg'],
                selectforeground=self.colors['fg']
            )
            self.setup_text_styles(tab.text_widget)

            # 내용 다시 렌더링
            if tab.content and not tab.edit_mode:
                self.render_markdown(tab.text_widget, tab.content)

    def increase_font_size(self):
        """폰트 크기 증가"""
        if self.font_size < 24:
            self.font_size += 1
            self.config.config['font_size'] = self.font_size
            self.config.save_config()
            self.refresh_ui()

    def decrease_font_size(self):
        """폰트 크기 감소"""
        if self.font_size > 8:
            self.font_size -= 1
            self.config.config['font_size'] = self.font_size
            self.config.save_config()
            self.refresh_ui()

    def reset_font_size(self):
        """폰트 크기 초기화"""
        self.font_size = 11
        self.config.config['font_size'] = self.font_size
        self.config.save_config()
        self.refresh_ui()

    def toggle_always_on_top(self):
        """항상 위 토글"""
        current = self.config.config['always_on_top']
        new_value = not current
        self.config.config['always_on_top'] = new_value
        self.config.save_config()
        self.root.attributes('-topmost', new_value)

    # ===== 상태 업데이트 =====

    def update_title(self):
        """제목 표시줄 업데이트"""
        tab = self.get_current_tab()
        if not tab or not tab.file_path:
            self.root.title("MDnote")
        else:
            file_name = tab.file_path.name
            mode_indicator = " [편집]" if tab.edit_mode else ""
            unsaved_indicator = " *" if tab.has_unsaved_changes else ""
            self.root.title(f"MDnote - {file_name}{mode_indicator}{unsaved_indicator}")

    def update_status_bar(self):
        """상태바 업데이트"""
        tab = self.get_current_tab()
        if not tab or not tab.content:
            self.status_bar.config(text="Ready")
            return

        content = tab.content
        lines = content.count('\n') + 1
        chars = len(content)
        words = len(content.split())

        dnd_status = "| 드래그앤드롭 지원" if HAS_DND else ""
        status_text = f"Lines: {lines}  |  Words: {words}  |  Characters: {chars}  {dnd_status}"
        self.status_bar.config(text=status_text)

    def quit_app(self):
        """앱 종료"""
        # 저장되지 않은 변경사항 확인
        for tab_id, tab in self.tabs.items():
            if tab.has_unsaved_changes:
                response = messagebox.askyesnocancel(
                    "저장되지 않은 변경사항",
                    f"'{tab.file_path.name}'에 저장되지 않은 변경사항이 있습니다.\n저장하시겠습니까?"
                )
                if response is None:
                    return
                elif response:
                    self.notebook.select(tab.frame)
                    self.save_file()

        # 종료 전 설정 저장
        self.config.save_config()
        self.root.quit()

    # ===== 마크다운 렌더링 =====

    def setup_text_styles(self, text_widget):
        """텍스트 스타일 설정"""
        # 제목들
        heading_configs = [
            ("h1", 20, 15, 10),
            ("h2", 18, 12, 8),
            ("h3", 16, 10, 6),
            ("h4", 14, 8, 5),
            ("h5", 13, 6, 4),
            ("h6", 12, 4, 3),
        ]

        for tag, size, sp1, sp3 in heading_configs:
            text_widget.tag_configure(
                tag,
                font=("맑은 고딕", int(size * self.font_size / 11), "bold"),
                foreground=self.colors.get(tag, self.colors['fg']),
                spacing1=sp1,
                spacing3=sp3
            )

        # 코드
        code_size = max(8, int(self.font_size * 0.9))
        text_widget.tag_configure(
            "code",
            font=("Consolas", code_size),
            background=self.colors['code_bg'],
            foreground=self.colors['code']
        )
        text_widget.tag_configure(
            "code_block",
            font=("Consolas", code_size),
            background=self.colors['code_bg'],
            foreground=self.colors['code'],
            lmargin1=20,
            lmargin2=20
        )
        # 코드 블록 헤더용 태그 (임베드 위젯 대신 텍스트로 표시 → 스크롤 성능 유지)
        text_widget.tag_configure(
            "code_lang",
            font=("Consolas", code_size),
            foreground=self.colors['quote'],
            background=self.colors['code_bg']
        )
        text_widget.tag_configure(
            "code_copy",
            font=("Consolas", code_size, "bold"),
            foreground=self.colors['link'],
            background=self.colors['tree_bg'],
            relief=tk.RAISED,
            borderwidth=1
        )

        # 텍스트 기반 표 헤더/구분선
        text_widget.tag_configure(
            "tbl_head",
            font=("맑은 고딕", self.font_size, "bold"),
            foreground=self.colors['h3'],
            background=self.colors['code_bg']
        )
        text_widget.tag_configure(
            "tbl_sep",
            foreground=self.colors['hr'],
            lmargin1=24,
            lmargin2=24
        )

        # 링크
        text_widget.tag_configure(
            "link",
            foreground=self.colors['link'],
            underline=True
        )

        # 강조
        text_widget.tag_configure(
            "bold",
            font=("맑은 고딕", self.font_size, "bold"),
            foreground=self.colors['emphasis']
        )
        text_widget.tag_configure(
            "italic",
            font=("맑은 고딕", self.font_size, "italic")
        )

        # 취소선
        text_widget.tag_configure(
            "strikethrough",
            foreground=self.colors['strikethrough'],
            overstrike=True
        )

        # 인용
        text_widget.tag_configure(
            "blockquote",
            foreground=self.colors['quote'],
            lmargin1=20,
            lmargin2=20
        )

        # 리스트
        text_widget.tag_configure(
            "list",
            foreground=self.colors['list'],
            lmargin1=20,
            lmargin2=30
        )

        # 리스트 마커
        text_widget.tag_configure(
            "list_marker",
            foreground=self.colors['emphasis']
        )

        # 수평선
        text_widget.tag_configure(
            "hr",
            foreground=self.colors['hr'],
            font=("Arial", 1)
        )

        # 체크박스
        text_widget.tag_configure(
            "checkbox",
            foreground=self.colors['checkbox']
        )

    def insert_code_block_with_copy(self, text_widget, code_lines, lang=""):
        """코드 블록 삽입.

        복사 버튼을 임베드 위젯(tk.Frame/Button) 대신 클릭 가능한 텍스트 태그로
        구현한다. 코드블록이 수백 개인 대용량 문서에서 임베드 위젯이 많으면
        스크롤이 끊기므로(위젯 재배치 비용), 위젯을 전혀 만들지 않는다.
        """
        code_text = '\n'.join(code_lines)

        # 헤더 줄: 언어 표시 + 클릭 가능한 Copy 링크
        self._copy_seq = getattr(self, '_copy_seq', 0) + 1
        btn_tag = f"copybtn_{self._copy_seq}"

        if lang:
            text_widget.insert(tk.END, f" {lang} ", "code_lang")
            text_widget.insert(tk.END, "  ")
        text_widget.insert(tk.END, " ⧉ Copy ", ("code_copy", btn_tag))
        text_widget.insert(tk.END, "\n")

        def do_copy(event, ct=code_text):
            self.root.clipboard_clear()
            self.root.clipboard_append(ct)
            self.status_bar.config(text="✓ 코드 복사됨")
            self.root.after(1500, self.update_status_bar)
            return "break"

        text_widget.tag_bind(btn_tag, "<Button-1>", do_copy)
        text_widget.tag_bind(btn_tag, "<Enter>",
                             lambda e: text_widget.config(cursor="hand2"))
        text_widget.tag_bind(btn_tag, "<Leave>",
                             lambda e: text_widget.config(cursor=""))

        # 코드 내용 삽입 (텍스트 태그만 사용)
        for line in code_lines:
            text_widget.insert(tk.END, line + '\n', "code_block")

    def strip_inline(self, text):
        """테이블 셀 표시용 인라인 마크다운 마커 제거"""
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)
        text = re.sub(r'~~(.+?)~~', r'\1', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        return text.strip()

    def parse_table(self, lines, start):
        """start 위치에서 GFM 테이블 블록 파싱.

        (rows, aligns, end_index) 반환 또는 테이블이 아니면 None.
        rows[0]은 헤더 행, end_index는 테이블 다음 줄 인덱스.
        """
        header = lines[start]
        if '|' not in header:
            return None
        if start + 1 >= len(lines):
            return None

        separator = lines[start + 1].strip()
        # 구분선: 파이프 / 대시 / 콜론 / 공백으로만 구성, 대시 1개 이상
        if not re.match(r'^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?$', separator):
            return None

        def split_row(row):
            row = row.strip()
            row = row.replace('\\|', '\x00')  # 이스케이프된 파이프 보호
            if row.startswith('|'):
                row = row[1:]
            if row.endswith('|'):
                row = row[:-1]
            return [c.strip().replace('\x00', '|') for c in row.split('|')]

        # 정렬 파싱
        aligns = []
        for cell in split_row(separator):
            left = cell.startswith(':')
            right = cell.endswith(':')
            if left and right:
                aligns.append('center')
            elif right:
                aligns.append('right')
            else:
                aligns.append('left')

        rows = [split_row(header)]
        i = start + 2
        while i < len(lines):
            line = lines[i]
            if '|' not in line or line.strip() == '':
                break
            rows.append(split_row(line))
            i += 1

        return rows, aligns, i

    def insert_table(self, text_widget, rows, aligns):
        """테이블을 텍스트 + 픽셀 탭스톱으로 삽입.

        임베드 위젯(tk.Frame/Label)을 쓰지 않으므로 표가 많아도 스크롤이
        끊기지 않는다. 열 정렬은 Text 위젯의 픽셀 탭스톱으로 처리해 한글처럼
        가변폭 글자도 정확히 정렬되고, 폭을 넘는 셀은 자동 줄바꿈한다.
        """
        from tkinter import font as tkfont

        ncols = max(len(r) for r in rows)
        grid = [[self.strip_inline(row[c]) if c < len(row) else ''
                 for c in range(ncols)] for row in rows]
        aligns = [(aligns[c] if c < len(aligns) else 'left') for c in range(ncols)]

        body_font = tkfont.Font(family="맑은 고딕", size=self.font_size)
        head_font = tkfont.Font(family="맑은 고딕", size=self.font_size, weight="bold")

        # 열별 자연 폭(픽셀)
        natural = []
        for c in range(ncols):
            w = 0
            for r in range(len(grid)):
                f = head_font if r == 0 else body_font
                w = max(w, f.measure(grid[r][c]))
            natural.append(w)

        text_widget.update_idletasks()
        avail = text_widget.winfo_width()
        if avail <= 1:
            avail = 900  # 최초 렌더 시 폭 미확정 대비 기본값
        LM = 24    # 좌측 여백
        PAD = 28   # 열 간격
        usable = max(320, avail - LM - 40)
        if sum(natural) + PAD * (ncols - 1) <= usable:
            col_w = natural[:]
        else:
            cap = max(110, int((usable - PAD * (ncols - 1)) / ncols))
            col_w = [min(n, cap) for n in natural]
        col_w = [max(36, w) for w in col_w]

        # 열 좌측 좌표 + 탭스톱(정렬 포함)
        xs = []
        x = LM
        for c in range(ncols):
            xs.append(x)
            x += col_w[c] + PAD
        tabs = []
        for c in range(ncols):
            if aligns[c] == 'right':
                tabs += [xs[c] + col_w[c], 'right']
            elif aligns[c] == 'center':
                tabs += [xs[c] + col_w[c] // 2, 'center']
            else:
                tabs += [xs[c], 'left']

        self._tbl_seq = getattr(self, '_tbl_seq', 0) + 1
        tab_tag = f"tbltab_{self._tbl_seq}"
        text_widget.tag_configure(tab_tag, tabs=tuple(tabs),
                                  lmargin1=LM, lmargin2=LM, spacing1=2, spacing3=2)

        def wrap_cell(text, w, f):
            """셀 내용을 폭 w(픽셀) 안에 들어가도록 줄바꿈 (단어 우선, 필요시 글자)"""
            if not text:
                return ['']
            lines = []
            cur = ''
            for word in text.split(' '):
                trial = word if cur == '' else cur + ' ' + word
                if f.measure(trial) <= w or cur == '':
                    if cur == '' and f.measure(word) > w:
                        piece = ''
                        for ch in word:
                            if f.measure(piece + ch) <= w or piece == '':
                                piece += ch
                            else:
                                lines.append(piece)
                                piece = ch
                        cur = piece
                    else:
                        cur = trial
                else:
                    lines.append(cur)
                    cur = word
                    if f.measure(cur) > w:
                        piece = ''
                        for ch in cur:
                            if f.measure(piece + ch) <= w or piece == '':
                                piece += ch
                            else:
                                lines.append(piece)
                                piece = ch
                        cur = piece
            lines.append(cur)
            return lines

        def emit_row(r, header):
            f = head_font if header else body_font
            line_tags = (tab_tag, "tbl_head") if header else (tab_tag,)
            wrapped = [wrap_cell(grid[r][c], col_w[c], f) for c in range(ncols)]
            maxl = max(len(wc) for wc in wrapped)
            for k in range(maxl):
                text_widget.insert(tk.END, '\t', line_tags)
                for c in range(ncols):
                    seg = wrapped[c][k] if k < len(wrapped[c]) else ''
                    text_widget.insert(tk.END, seg, line_tags)
                    if c < ncols - 1:
                        text_widget.insert(tk.END, '\t', line_tags)
                text_widget.insert(tk.END, '\n', line_tags)

        # 헤더
        emit_row(0, header=True)
        # 헤더 아래 가로 구분선
        total_px = xs[-1] + col_w[-1] - LM
        dash_px = body_font.measure('─') or 8
        n_dash = max(10, int(total_px / dash_px))
        text_widget.insert(tk.END, '─' * n_dash + '\n', "tbl_sep")
        # 본문
        for r in range(1, len(grid)):
            emit_row(r, header=False)
        text_widget.insert(tk.END, '\n')

    def render_markdown(self, text_widget, content):
        """마크다운 렌더링"""
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)

        lines = content.split('\n')
        in_code_block = False
        code_block_content = []
        code_block_lang = ""

        i = 0
        while i < len(lines):
            line = lines[i]

            # 코드 블록 토글
            if line.strip().startswith('```'):
                if not in_code_block:
                    # 코드 블록 시작
                    in_code_block = True
                    code_block_lang = line.strip()[3:]  # 언어 추출
                    code_block_content = []
                else:
                    # 코드 블록 끝 - 복사 버튼과 함께 렌더링
                    in_code_block = False
                    self.insert_code_block_with_copy(text_widget, code_block_content, code_block_lang)
                i += 1
                continue

            # 코드 블록 내부
            if in_code_block:
                code_block_content.append(line)
                i += 1
                continue

            # 테이블 (코드 블록 밖에서만)
            table = self.parse_table(lines, i)
            if table:
                rows, aligns, end = table
                self.insert_table(text_widget, rows, aligns)
                i = end
                continue

            # 수평선
            if re.match(r'^[-*_]{3,}$', line.strip()):
                text_widget.insert(tk.END, '─' * 50 + '\n', "hr")
                i += 1
                continue

            # 제목 (H1-H6)
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                tag = f"h{level}"
                text_widget.insert(tk.END, text + '\n', tag)
                i += 1
                continue

            # 인용
            if line.startswith('> '):
                text_widget.insert(tk.END, line[2:] + '\n', "blockquote")
                i += 1
                continue

            # 체크박스 리스트
            checkbox_match = re.match(r'^(\s*)[-*+]\s+\[([ xX])\]\s+(.+)$', line)
            if checkbox_match:
                indent, check, item_content = checkbox_match.groups()
                text_widget.insert(tk.END, indent)
                checkbox_symbol = '☑' if check.lower() == 'x' else '☐'
                text_widget.insert(tk.END, checkbox_symbol + ' ', "checkbox")
                self.insert_formatted_text(text_widget, item_content, base_tag="list")
                i += 1
                continue

            # 순서 있는 리스트
            if re.match(r'^\s*\d+\.\s+', line):
                self.insert_list_item(text_widget, line)
                i += 1
                continue

            # 순서 없는 리스트
            if re.match(r'^\s*[-*+]\s+', line):
                self.insert_list_item(text_widget, line)
                i += 1
                continue

            # 일반 텍스트
            self.insert_formatted_text(text_widget, line)
            i += 1

        text_widget.config(state=tk.DISABLED)

    def insert_list_item(self, text_widget, line):
        """리스트 항목 삽입"""
        match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
        if match:
            indent, marker, content = match.groups()
            text_widget.insert(tk.END, indent)
            text_widget.insert(tk.END, marker + ' ', "list_marker")
            self.insert_formatted_text(text_widget, content, base_tag="list")
        else:
            text_widget.insert(tk.END, line + '\n')

    def insert_formatted_text(self, text_widget, text, base_tag=None):
        """포맷팅된 텍스트 삽입"""
        # 취소선 처리
        if '~~' in text:
            parts = text.split('~~')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    self.process_inline_formatting(text_widget, part, base_tag)
                else:
                    text_widget.insert(tk.END, part, "strikethrough")
        else:
            self.process_inline_formatting(text_widget, text, base_tag)

        text_widget.insert(tk.END, '\n')

    def process_inline_formatting(self, text_widget, text, base_tag=None):
        """인라인 포맷팅 처리"""
        if '`' in text:
            parts = text.split('`')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    self.insert_bold_italic(text_widget, part, base_tag)
                else:
                    text_widget.insert(tk.END, part, "code")
        else:
            self.insert_bold_italic(text_widget, text, base_tag)

    def insert_bold_italic(self, text_widget, text, base_tag=None):
        """굵게, 기울임 처리"""
        bold_pattern = r'\*\*(.+?)\*\*|__(.+?)__'

        last_end = 0
        for match in re.finditer(bold_pattern, text):
            if match.start() > last_end:
                tag = base_tag if base_tag else None
                text_widget.insert(tk.END, text[last_end:match.start()], tag)

            bold_text = match.group(1) or match.group(2)
            text_widget.insert(tk.END, bold_text, "bold")
            last_end = match.end()

        if last_end < len(text):
            tag = base_tag if base_tag else None
            text_widget.insert(tk.END, text[last_end:], tag)


def main():
    """메인 함수"""
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    # 드래그앤드롭 지원 여부에 따라 루트 윈도우 생성
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = MarkdownViewer(root, file_path)
    root.mainloop()


if __name__ == "__main__":
    main()
