"""WriteStep - TOEFL Writing practice app (Tkinter scaffold)."""


import json
import random
import tkinter as tk
import tkinter.font as tkfont
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


TIME_LIMIT_SECONDS = 8 * 60

# 화면 글꼴: 앞에서부터 이 컴퓨터에 설치된 첫 번째 글꼴을 쓴다.
FONT_CANDIDATES = ["한컴 말랑말랑 Bold", "한컴 말랑말랑 Regular", "맑은 고딕"]

REVIEW_ITEMS = [
    "Answered every part of the prompt",
    "Made the purpose of the email clear",
    "Included specific supporting details",
    "Used a clear request, suggestion, or question",
    "Checked grammar, spelling, and punctuation",
]

DIFFICULTY_ITEMS = [
    "Organizing ideas was difficult",
    "Covering every bullet point was difficult",
    "Coming up with ideas or details was difficult",
    "Recalling expressions without peeking was difficult",
    "Using a polite, formal tone was difficult",
    "Not enough time",
]

# Short labels for the 오답노트 list column.
DIFFICULTY_TAGS = {
    "Organizing ideas was difficult": "구성",
    "Covering every bullet point was difficult": "조건 누락",
    "Coming up with ideas or details was difficult": "아이디어",
    "Recalling expressions without peeking was difficult": "표현 떠올리기",
    "Using a polite, formal tone was difficult": "어조",
    "Not enough time": "시간 부족",
    # 예전 항목: 이전에 저장된 기록에도 짧은 이름이 보이도록 남겨 둔다.
    "Vocabulary was difficult": "어휘",
    "Grammar or sentence structure was difficult": "문법·문장",
}

PLACEHOLDER_PROMPT = "The selected email writing prompt will appear here. Read the prompt and write your response in the answer panel."

# 문제은행: 이 파일과 같은 폴더의 question_bank.json (문제를 추가할 때 코드는 고치지 않아도 된다)
QUESTION_BANK_PATH = Path(__file__).with_name("question_bank.json")

# 이메일 유형별 본문 작성 안내: (해야 할 일, [추천 표현...])
EMAIL_TYPES = {
    1: {
        "ko": "사과", "en": "Apology",
        "greeting_example": "Dear Professor Kim,",
        "guide": [
            ("사과할 일을 직접 말하기", ["I am writing to sincerely apologize for ...", "I am very sorry for ..."]),
            ("내가 한 행동에 대한 책임 인정하기", ["I take full responsibility for ...", "It was my fault that ..."]),
            ("상황이 발생한 이유 설명하기", ["Unfortunately, ...", "This happened because ..."]),
            ("상대방에게 미친 영향을 언급하기", ["I understand that this caused ...", "I realize this may have ..."]),
            ("해결 방법이나 재발 방지 계획 제시하기", ["Would it be possible to ...?", "In the future, I will make sure to ..."]),
        ],
    },
    2: {
        "ko": "문제·상황 알림", "en": "Problem/Status Report",
        "greeting_example": "Dear Professor Lee,",
        "guide": [
            ("무엇에 대해 연락하는지 밝히기", ["I am writing to let you know that ...", "I wanted to inform you about ..."]),
            ("문제 상황을 구체적으로 설명하기", ["The problem is that ...", "Unfortunately, ..."]),
            ("지금까지의 진행 상황 알리기", ["So far, I have ...", "At the moment, ..."]),
            ("필요한 도움이나 조치 요청하기", ["Could you please ...?", "I would appreciate it if you could ..."]),
            ("다음 계획과 연락 방법 안내하기", ["I will keep you updated on ...", "Please let me know if ..."]),
        ],
    },
    3: {
        "ko": "구직·직무 문의", "en": "Job Inquiry",
        "greeting_example": "Dear Hiring Manager,",
        "guide": [
            ("연락 목적과 관심 있는 자리 밝히기", ["I am writing to inquire about ...", "I am very interested in the ... position."]),
            ("내 경험이나 강점 소개하기", ["I have experience in ...", "I believe my skills in ... would ..."]),
            ("자격이나 업무 조건에 대해 질문하기", ["Could you tell me more about ...?", "I was wondering whether ..."]),
            ("일할 수 있는 시간이나 조건 알리기", ["I am available to work ...", "I would be able to start ..."]),
            ("다음 절차를 물으며 마무리하기", ["Please let me know how I can apply.", "I would be grateful for the chance to ..."]),
        ],
    },
    4: {
        "ko": "허가·승인 요청", "en": "Permission Request",
        "greeting_example": "Dear Professor Park,",
        "guide": [
            ("요청할 일을 분명히 말하기", ["I am writing to ask for permission to ...", "I would like to request ..."]),
            ("요청하는 이유 설명하기", ["The reason is that ...", "This would help me ..."]),
            ("구체적인 날짜나 방법 제시하기", ["I would need to ... on ...", "I plan to ..."]),
            ("상대의 부담을 줄이는 방안 제시하기", ["I will make sure that ...", "I can ... to make up for it."]),
            ("정중하게 승인 여부 묻기", ["Would it be possible to ...?", "Please let me know if this would be acceptable."]),
        ],
    },
    5: {
        "ko": "사직·활동 종료", "en": "Resignation",
        "greeting_example": "Dear Ms. Brown,",
        "guide": [
            ("그만두려는 사실 알리기", ["I am writing to inform you that I will be leaving ...", "I have decided to step down from ..."]),
            ("이유를 간단히 설명하기", ["This is because ...", "Due to ..., I am no longer able to ..."]),
            ("마지막 날짜 알리기", ["My last day will be ...", "I will be able to continue until ..."]),
            ("그동안의 경험에 감사 표현하기", ["I am grateful for the opportunity to ...", "I have really enjoyed ..."]),
            ("인수인계나 마무리 도움 제안하기", ["I would be happy to help ...", "Please let me know how I can make the transition smooth."]),
        ],
    },
    6: {
        "ko": "개선 제안", "en": "Suggestion",
        "greeting_example": "Dear Mr. Smith,",
        "guide": [
            ("제안하려는 주제 밝히기", ["I am writing to suggest ...", "I would like to share an idea about ..."]),
            ("현재의 문제점 설명하기", ["I have noticed that ...", "Currently, ..."]),
            ("구체적인 개선 방법 제시하기", ["One solution might be to ...", "I think it would be helpful to ..."]),
            ("기대되는 효과 설명하기", ["This would allow ...", "As a result, ..."]),
            ("의견을 묻거나 도움을 제안하며 마무리하기", ["What do you think about ...?", "I would be happy to help ..."]),
        ],
    },
}

BODY_HINT = "'표현 보기'로 추천 표현을 확인한 뒤 직접 작성하십시오."


def type_label(number):
    """'사과 Apology'처럼 유형 이름 전체. 예전 기록의 7·8번 유형은 '유형 7'로 표시."""
    info = EMAIL_TYPES.get(number)
    return f"{info['ko']} {info['en']}" if info else f"유형 {number}"


def type_short(number):
    info = EMAIL_TYPES.get(number)
    return info["ko"] if info else f"유형 {number}"


def load_question_bank():
    """문제 목록을 읽는다. 파일이 없거나 깨져 있으면 빈 목록 (그때는 임시 문구로 연습)."""
    try:
        questions = json.loads(QUESTION_BANK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(questions, list):
        return []
    return [q for q in questions if isinstance(q, dict) and {"id", "type", "difficulty", "title"} <= q.keys()]


def format_question(question):
    """문제 하나를 Prompt 칸에 보여줄 글로 만든다. 이 글이 연습 기록에도 그대로 저장된다."""
    lines = [question["title"], "", question.get("situation", ""), ""]
    lines.append(f"{question.get('task', 'Write an email.')} In the email, do each of the following:")
    lines += [f"- {bullet}" for bullet in question.get("bullets", [])]
    lines += ["", "Write as much as you can and in complete sentences.", ""]
    lines += [f"To: {question.get('to', '')}", f"Subject: {question.get('subject', '')}"]
    return "\n".join(lines)


def format_duration(seconds):
    minutes, secs = divmod(int(round(seconds)), 60)
    return f"{minutes}분 {secs:02d}초"


def format_datetime(text):
    try:
        return datetime.fromisoformat(text).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return text or "-"


class WriteStepApp(tk.Tk):
    """Single-file GUI scaffold; feature logic will be added incrementally."""

    def __init__(self):
        super().__init__()
        self.title("WriteStep | TOEFL Writing Practice")
        # 화면보다 크면 아래쪽 버튼이 가려지므로 화면 크기에 맞춰 창 크기와 위치를 정한다.
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        width, height = min(1180, screen_w - 40), min(760, screen_h - 90)
        self.geometry(f"{width}x{height}+{(screen_w - width) // 2}+{max(0, (screen_h - height) // 2 - 30)}")
        self.minsize(min(980, width), min(640, height))
        self.configure(bg="#F5F6FA")

        self.app_config_path = Path.home() / ".writestep" / "config.json"
        self.workspace = None
        self.profile = None
        self.timer_job = None
        self.remaining_seconds = 0
        self.practice_selection = None
        self.current_page = None
        self.question_bank = load_question_bank()
        self._load_saved_profile()

        installed = set(tkfont.families(self))
        self.font = next((name for name in FONT_CANDIDATES if name in installed), "TkDefaultFont")
        # 따로 글꼴을 정하지 않은 위젯(라디오버튼, 입력칸, 목록 등)도 같은 글꼴을 쓰게 한다.
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(name).configure(family=self.font)
        self._configure_style()
        self._build_shell()
        self.show_page("홈" if self.profile else "처음 설정")

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#F5F6FA")
        style.configure("Sidebar.TFrame", background="#20263A")
        style.configure("TLabel", background="#F5F6FA", foreground="#20263A", font=(self.font, 11))
        style.configure("Title.TLabel", font=(self.font, 23, "bold"), foreground="#20263A")
        style.configure("Sub.TLabel", font=(self.font, 11), foreground="#697386")
        style.configure("SidebarTitle.TLabel", background="#20263A", foreground="white", font=(self.font, 17, "bold"))
        style.configure("Nav.TButton", background="#20263A", foreground="#E6E9F2", font=(self.font, 11), padding=(14, 12), anchor="w", borderwidth=0)
        style.map("Nav.TButton", background=[("active", "#343D58")], foreground=[("active", "white")])
        style.configure("Primary.TButton", background="#5967D8", foreground="white", font=(self.font, 11, "bold"), padding=(18, 11), borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#4855C4")])
        style.configure("Card.TFrame", background="white", relief="flat")
        style.configure("CardTitle.TLabel", background="white", font=(self.font, 14, "bold"))
        style.configure("CardText.TLabel", background="white", foreground="#697386", wraplength=260)
        style.configure("SmallTitle.TLabel", background="white", font=(self.font, 11, "bold"))
        style.configure("Field.TLabel", background="white")
        for widget in ("TRadiobutton", "TCheckbutton"):
            style.configure(widget, background="white", padding=(0, 2))
            style.map(widget, background=[("active", "white")])
        style.configure("CardBody.TLabel", background="white", font=(self.font, 10))
        style.configure("StatValue.TLabel", background="white", font=(self.font, 18, "bold"))
        style.configure("Stat.Horizontal.TProgressbar", troughcolor="#ECEEF5", background="#5967D8", bordercolor="#ECEEF5", lightcolor="#5967D8", darkcolor="#5967D8", thickness=10)
        # 답안 입력 화면의 인사말·본문·맺음말 영역 (흰 카드 안의 연회색 칸)
        style.configure("Section.TFrame", background="#F5F6FA")
        style.configure("SectionTitle.TLabel", background="#F5F6FA", font=(self.font, 11, "bold"))
        style.configure("SectionHint.TLabel", background="#F5F6FA", foreground="#D04A4A", font=(self.font, 9), wraplength=340)
        style.configure("GuideStep.TLabel", background="#F5F6FA", font=(self.font, 10, "bold"))
        style.configure("GuidePhrase.TLabel", background="#F5F6FA", foreground="#D04A4A", font=(self.font, 10))
        style.configure("Chip.TButton", font=(self.font, 9), padding=(6, 1))
        style.configure("TPanedwindow", background="#F5F6FA")

    def _build_shell(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(self, style="Sidebar.TFrame", padding=(18, 24))
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.rowconfigure(6, weight=1)
        ttk.Label(sidebar, text="WriteStep", style="SidebarTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 30))

        self.navigation = ["홈", "연습하기", "오답노트", "학습통계"]
        for row, page_name in enumerate(self.navigation, start=1):
            ttk.Button(
                sidebar,
                text=page_name,
                style="Nav.TButton",
                command=lambda name=page_name: self.show_page(name),
            ).grid(row=row, column=0, sticky="ew", pady=3)

        self.content = ttk.Frame(self, padding=(38, 30))
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

    def show_page(self, page_name):
        """Replace the main content with the selected page."""
        if not self.profile and page_name != "처음 설정":
            page_name = "처음 설정"
        if self.current_page in ("문제 풀이", "자가점검") and page_name not in ("문제 풀이", "자가점검"):
            if not messagebox.askyesno("저장 전 연습 내용", "저장하지 않은 내용은 삭제됩니다. 나가시겠습니까?", parent=self):
                return
            self.practice_selection = None
        self._stop_timer()
        self.unbind_all("<MouseWheel>")
        for child in self.content.winfo_children():
            child.destroy()
        # Pages set their own stretch rows; clear what the previous page left behind.
        for row in range(6):
            self.content.rowconfigure(row, weight=0)

        self.current_page = page_name
        if page_name == "처음 설정":
            self._show_setup()
        elif page_name == "홈":
            self._show_home()
        elif page_name == "연습하기":
            self._show_practice()
        elif page_name == "문제 풀이":
            self._show_writing_screen()
        elif page_name == "자가점검":
            self._show_self_review()
        elif page_name == "오답노트":
            self._show_notes()
        elif page_name == "학습통계":
            self._show_stats()
        else:
            self._show_placeholder(page_name)

    def _show_home(self):
        name = self.profile["name"]
        exam_date = date.fromisoformat(self.profile["exam_date"])
        days_left = (exam_date - date.today()).days

        if days_left > 0:
            exam_message = f"TOEFL 시험까지 D-{days_left}일 남았습니다."
        elif days_left == 0:
            exam_message = "오늘은 TOEFL 시험일입니다."
        else:
            exam_message = "등록한 시험일이 지났습니다. 프로필에서 변경할 수 있습니다."

        ttk.Label(self.content, text=f"{name}님, 환영합니다.", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self.content, text=exam_message, style="Sub.TLabel").grid(row=0, column=0, sticky="w", pady=(55, 0)) #윗줄이랑 간격유지하려면 어떻게해야함? 

        body = ttk.Frame(self.content)
        body.grid(row=1, column=0, sticky="new", pady=(36, 0))
        body.columnconfigure((0, 1), weight=1)

        self._make_card(body, 0, 0, "오늘의 연습", "이메일 문제의 난이도와 유형을 골라 답안을 작성합니다.", "연습 시작", lambda: self.show_page("연습하기"))
        self._make_card(body, 0, 1, "오답노트", "답안과 함께 내가 느낀 실수 원인·어려웠던 점을 기록합니다.", "오답노트 보기", lambda: self.show_page("오답노트"))
        self._make_card(body, 1, 0, "학습통계", "유형별 연습 횟수와 자주 기록한 어려움을 살펴봅니다.", "통계 보기", lambda: self.show_page("학습통계"))

    def _make_card(self, parent, row, column, title, description, button_text, command):
        card = ttk.Frame(parent, style="Card.TFrame", padding=22)
        card.grid(row=row, column=column, sticky="nsew", padx=(0 if column == 0 else 12, 12 if column == 0 else 0), pady=(0, 14))
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, text=description, style="CardText.TLabel").pack(anchor="w", pady=(10, 18))
        ttk.Button(card, text=button_text, style="Primary.TButton", command=command).pack(anchor="w")

    def _show_practice(self):
        ttk.Label(self.content, text="이메일 연습 설정", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self.content, text="난이도와 문제 유형을 하나씩 선택하십시오.", style="Sub.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 22))

        panel = ttk.Frame(self.content, style="Card.TFrame", padding=24)
        panel.grid(row=2, column=0, sticky="new")
        ttk.Label(panel, text="난이도", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.difficulty_var = tk.StringVar(value="중")
        difficulty_row = ttk.Frame(panel, style="Card.TFrame")
        difficulty_row.grid(row=1, column=0, sticky="w", pady=(0, 22))
        for col, level in enumerate(("상", "중", "하")):
            ttk.Radiobutton(difficulty_row, text=level, value=level, variable=self.difficulty_var).grid(row=0, column=col, padx=(0, 24))

        ttk.Label(panel, text="문제 유형", style="CardTitle.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 10))
        self.type_var = tk.IntVar(value=0)
        type_grid = ttk.Frame(panel, style="Card.TFrame")
        type_grid.grid(row=3, column=0, sticky="w")
        for n in EMAIL_TYPES:
            ttk.Radiobutton(type_grid, text=f"{n}. {type_label(n)}", value=n, variable=self.type_var).grid(row=(n - 1) // 2, column=(n - 1) % 2, sticky="w", padx=(0, 32), pady=8)

        ttk.Label(panel, text="선택한 조건에 맞는 문제가 문제은행에서 출제됩니다.", style="CardText.TLabel", wraplength=600).grid(row=4, column=0, sticky="w", pady=(18, 18))
        buttons = ttk.Frame(panel, style="Card.TFrame")
        buttons.grid(row=5, column=0, sticky="w")
        ttk.Button(buttons, text="홈으로", command=lambda: self.show_page("홈")).pack(side="left", padx=(0, 10))
        ttk.Button(buttons, text="문제 풀기", style="Primary.TButton", command=self._start_practice).pack(side="left")

    def _start_practice(self):
        difficulty = self.difficulty_var.get()
        problem_type = self.type_var.get()
        if not difficulty:
            messagebox.showwarning("선택 필요", "난이도를 선택하십시오.", parent=self)
            return
        if not problem_type:
            messagebox.showwarning("선택 필요", "문제 유형을 선택하십시오.", parent=self)
            return
        # 같은 유형·난이도 문제가 여러 개면 그중 하나를 무작위로 고른다.
        candidates = [q for q in self.question_bank if q["type"] == problem_type and q["difficulty"] == difficulty]
        if candidates:
            question = random.choice(candidates)
            prompt = {"id": question["id"], "text": format_question(question)}
        else:
            messagebox.showinfo("문제 없음", "해당 조건의 문제가 없어 임시 문구로 진행합니다.", parent=self)
            prompt = {"id": None, "text": PLACEHOLDER_PROMPT}
        self._begin_practice(difficulty, problem_type, prompt)

    def _retry_note(self):
        """오답노트에서 고른 기록과 같은 유형·난이도·문제로 새 연습을 시작한다."""
        record = self.selected_note
        if record is None:
            return
        if record["type"] not in EMAIL_TYPES:
            messagebox.showinfo("다시 풀기 불가", "이전 유형 체계의 기록이라 다시 풀 수 없습니다.", parent=self)
            return
        prompt = {"id": record["prompt_id"], "text": record["prompt"] or PLACEHOLDER_PROMPT}
        self._begin_practice(record.get("difficulty", "중"), record["type"], prompt)

    def _begin_practice(self, difficulty, problem_type, prompt):
        self.practice_selection = {
            "difficulty": difficulty,
            "type": problem_type,
        }
        self.practice_prompt = prompt
        self.remaining_seconds = TIME_LIMIT_SECONDS
        self.overtime_seconds = 0
        self.practice_duration_seconds = 0
        self.practice_answer = ""
        # 인사말·본문·맺음말은 자가점검 화면에 다녀와도 유지되도록 따로 보관한다.
        self.greeting_var = tk.StringVar(value="")
        self.email_body = ""
        self.email_closing = ""
        self.review_vars = [(item, tk.BooleanVar(value=False)) for item in REVIEW_ITEMS]
        self.difficulty_vars = [(item, tk.BooleanVar(value=False)) for item in DIFFICULTY_ITEMS]
        self.reflection_draft = ""
        self.show_page("문제 풀이")

    def _show_writing_screen(self):
        selected = self.practice_selection
        # 위쪽: [제목·유형] ··· [작성 중 점검 체크리스트] [타이머]
        ttk.Label(self.content, text="Writing practice", style="Title.TLabel").grid(row=0, column=0, sticky="sw")
        ttk.Label(self.content, text=f"{selected['difficulty']} · {type_label(selected['type'])}", style="Sub.TLabel").grid(row=1, column=0, sticky="nw", pady=(4, 0))
        checklist = ttk.Frame(self.content, style="Card.TFrame", padding=(14, 8))
        checklist.grid(row=0, column=1, rowspan=2, sticky="e", padx=(16, 16))
        ttk.Label(checklist, text="작성 중 점검", style="SmallTitle.TLabel").pack(anchor="w", pady=(0, 2))
        for item, variable in self.review_vars:
            # 창이 좁으면 잘리지 않고 줄바꿈되도록 wraplength가 있는 tk.Checkbutton을 쓴다.
            tk.Checkbutton(
                checklist, text=item, variable=variable, font=(self.font, 9), wraplength=300, justify="left", anchor="w",
                bg="white", activebackground="white", highlightthickness=0, borderwidth=0, padx=0, pady=0,
            ).pack(anchor="w", fill="x")
        self.timer_label = ttk.Label(self.content, text="8:00", style="Title.TLabel", foreground="#5967D8")
        self.timer_label.grid(row=0, column=2, rowspan=2, sticky="e")
        self.content.rowconfigure(2, weight=1)
        exercise = ttk.Frame(self.content)
        exercise.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(14, 0))
        exercise.columnconfigure(0, weight=4, uniform="writing")
        exercise.columnconfigure(1, weight=6, uniform="writing")
        exercise.rowconfigure(0, weight=1)

        prompt_frame = ttk.Frame(exercise, style="Card.TFrame", padding=18)
        prompt_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        
        ttk.Label(prompt_frame, text="Prompt", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        prompt_area = ttk.Frame(prompt_frame, style="Card.TFrame")
        prompt_area.pack(fill="both", expand=True)
        # spacing2: 줄바꿈된 줄 사이 간격, spacing3: 문단(빈 줄로 나뉜 부분) 아래 간격
        self.prompt_box = tk.Text(prompt_area, wrap="word", font=(self.font, 11, "bold"), padx=6, pady=4, relief="flat", spacing2=3, spacing3=3)
        prompt_scroll = ttk.Scrollbar(prompt_area, orient="vertical", command=self.prompt_box.yview)
        self.prompt_box.configure(yscrollcommand=prompt_scroll.set)
        self.prompt_box.pack(side="left", fill="both", expand=True)
        prompt_scroll.pack(side="right", fill="y")
        self.prompt_box.insert("1.0", self.practice_prompt["text"])
        self.prompt_box.configure(state="disabled")

        email_type = EMAIL_TYPES[selected["type"]]
        answer_frame = ttk.Frame(exercise, style="Card.TFrame", padding=14)
        answer_frame.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        answer_frame.columnconfigure(0, weight=1)
        answer_frame.rowconfigure(1, weight=1)  # 본문 영역만 늘어나고 줄어든다.

        # 1. 인사말: 예시만 보여주고 직접 쓴다.
        greeting, _ = self._make_section(answer_frame, 0, "1. 인사말 Greeting", f"예: {email_type['greeting_example']}")
        greeting_entry = ttk.Entry(greeting, textvariable=self.greeting_var, font=(self.font, 11))
        greeting_entry.pack(fill="x")
        greeting_entry.bind("<KeyRelease>", self._update_word_count)

        # 2. 본문: 왼쪽 입력칸 | 오른쪽 작성 안내 (가운데 경계선을 끌어 폭 조절)
        body, _ = self._make_section(answer_frame, 1, "2. 본문 Body", BODY_HINT)
        panes = ttk.PanedWindow(body, orient="horizontal")
        panes.pack(fill="both", expand=True)
        body_area = ttk.Frame(panes, style="Section.TFrame")
        self.body_box = tk.Text(body_area, wrap="word", font=(self.font, 11), undo=True, padx=10, pady=8, relief="solid", borderwidth=1, width=20, height=4)
        body_scroll = ttk.Scrollbar(body_area, orient="vertical", command=self.body_box.yview)
        self.body_box.configure(yscrollcommand=body_scroll.set)
        body_scroll.pack(side="right", fill="y")
        self.body_box.pack(side="left", fill="both", expand=True)
        self.body_box.insert("1.0", self.email_body)
        self.body_box.bind("<KeyRelease>", self._update_word_count)
        guide_area = ttk.Frame(panes, style="Section.TFrame", padding=(10, 0, 0, 0))
        panes.add(body_area, weight=1)
        panes.add(guide_area, weight=1)
        self._build_body_guide(guide_area, email_type)
        # 화면에 처음 그려져 폭이 정해지면 입력칸과 안내를 반반으로 나눈다. (그 뒤로는 사용자가 조절)
        def split_once(event):
            if event.width > 1:
                panes.sashpos(0, event.width // 2)
                panes.unbind("<Configure>")

        panes.bind("<Configure>", split_once)

        # 3. 맺음말: 맺음 인사와 서명. 예시만 보여주고 직접 쓴다.
        closing, _ = self._make_section(answer_frame, 2, "3. 맺음말 Closing", "예: Sincerely, / [Your Name]")
        self.closing_box = tk.Text(closing, wrap="word", font=(self.font, 11), undo=True, padx=10, pady=6, relief="solid", borderwidth=1, width=20, height=2)
        self.closing_box.pack(fill="x")
        self.closing_box.insert("1.0", self.email_closing)
        self.closing_box.bind("<KeyRelease>", self._update_word_count)

        footer = ttk.Frame(self.content)
        footer.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        ttk.Button(footer, text="Cancel", command=self._cancel_practice).pack(side="left")
        self.word_count_label = ttk.Label(footer, text="Word count: 0", style="Sub.TLabel")
        self.word_count_label.pack(side="left", padx=(18, 0))
        ttk.Button(footer, text="Finish", style="Primary.TButton", command=self._finish_practice).pack(side="right")
        self._update_word_count()
        self._tick_timer()

    def _make_section(self, parent, row, title, hint):
        """답안 카드 안에 '제목 ··· 안내' 줄이 있는 연회색 영역을 만들어 (영역, 안내 Label)을 돌려준다."""
        section = ttk.Frame(parent, style="Section.TFrame", padding=(10, 8))
        section.grid(row=row, column=0, sticky="nsew", pady=(0, 6))
        title_row = ttk.Frame(section, style="Section.TFrame")
        title_row.pack(fill="x", pady=(0, 4))
        ttk.Label(title_row, text=title, style="SectionTitle.TLabel").pack(side="left")
        hint_label = ttk.Label(title_row, text=hint, style="SectionHint.TLabel")
        hint_label.pack(side="right")
        return section, hint_label

    def _build_body_guide(self, parent, email_type):
        """본문 옆에 유형별 '해야 할 일'과 추천 표현을 보여준다. 답안 입력칸과 별개라 답안에는 들어가지 않는다.
        추천 표현은 접어 두고, [표현 보기]를 누를 때마다 펼치거나 접는다. (삽입·복사 없이 직접 쓰게 한다)"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        inner = self._make_scrollable(parent, row=0)
        inner.columnconfigure(0, weight=1)
        step_labels, phrase_labels = [], []
        row = 0
        for step, phrases in email_type["guide"]:
            label = ttk.Label(inner, text=f"• {step}", style="GuideStep.TLabel")
            label.grid(row=row, column=0, sticky="w", pady=(8 if row else 0, 2))
            step_labels.append(label)
            row += 1
            # 단계마다 [표현 보기] 버튼과 그 아래 (처음엔 접힌) 표현 목록을 둔다.
            phrase_area = ttk.Frame(inner, style="Section.TFrame")
            phrase_area.grid(row=row, column=0, sticky="w", padx=(12, 0))
            row += 1
            labels = [ttk.Label(phrase_area, text=phrase, style="GuidePhrase.TLabel", justify="left") for phrase in phrases]
            phrase_labels.extend(labels)
            peek_button = ttk.Button(phrase_area, text="표현 보기", style="Chip.TButton")
            peek_button.configure(command=lambda button=peek_button, shown=labels: self._toggle_phrases(button, shown))
            peek_button.pack(anchor="w", pady=1)

        # 안내 폭이 바뀌면 글자 줄바꿈 폭도 맞춘다.
        last_width = [0]

        def rewrap(event):
            if event.width != last_width[0]:
                last_width[0] = event.width
                for label in step_labels:
                    label.configure(wraplength=max(80, event.width - 8))
                for phrase_label in phrase_labels:
                    phrase_label.configure(wraplength=max(60, event.width - 20))

        inner.bind("<Configure>", rewrap, add="+")

    def _toggle_phrases(self, button, labels):
        """버튼 아래에 표현을 펼치거나 접는다. 버튼 글자도 '표현 보기' ↔ '표현 숨기기'로 바꾼다."""
        if labels[0].winfo_ismapped():
            for label in labels:
                label.pack_forget()
            button.configure(text="표현 보기")
        else:
            for label in labels:
                label.pack(anchor="w", pady=1)
            button.configure(text="표현 숨기기")

    def _email_parts(self):
        """(인사말, 본문, 맺음말). 안내 문구는 별도 위젯이라 여기에 섞이지 않는다."""
        greeting = self.greeting_var.get().strip()
        body = self.body_box.get("1.0", "end-1c").strip()
        closing = self.closing_box.get("1.0", "end-1c").strip()
        return greeting, body, closing

    def _compose_email(self):
        """세 부분을 빈 줄로 이어 실제 이메일 형태의 답안 하나로 만든다."""
        return "\n\n".join(part for part in self._email_parts() if part)

    def _update_word_count(self, _event=None):
        count = len(self._compose_email().split())
        self.word_count_label.configure(text=f"Word count: {count}")

    def _tick_timer(self):
        if not hasattr(self, "timer_label") or not self.timer_label.winfo_exists():
            return
        if self.remaining_seconds > 0:
            minutes, seconds = divmod(self.remaining_seconds, 60)
            self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.remaining_seconds -= 1
        else:
            self.overtime_seconds = getattr(self, "overtime_seconds", 0) + 1
            minutes, seconds = divmod(self.overtime_seconds, 60)
            self.timer_label.configure(text=f"+{minutes:02d}:{seconds:02d}", foreground="#D04A4A")
        self.timer_job = self.after(1000, self._tick_timer)

    def _stop_timer(self):
        if self.timer_job is not None:
            try:
                self.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None

    def _finish_practice(self):
        self._stop_timer()
        self.email_body = self.body_box.get("1.0", "end-1c")
        self.email_closing = self.closing_box.get("1.0", "end-1c")
        self.email_greeting = self._email_parts()[0]
        self.practice_answer = self._compose_email()
        self.practice_duration_seconds = TIME_LIMIT_SECONDS - self.remaining_seconds + getattr(self, "overtime_seconds", 0)
        self.show_page("자가점검")

    def _cancel_practice(self):
        self.show_page("연습하기")

    def _show_self_review(self):
        ttk.Label(self.content, text="After practice", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self.content, text="Select the difficulties you experienced and add a note.", style="Sub.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 20))
        panel = ttk.Frame(self.content, style="Card.TFrame", padding=22)
        panel.grid(row=2, column=0, sticky="new")
        ttk.Label(panel, text="Difficulties", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        for row, (item, variable) in enumerate(self.difficulty_vars, start=1):
            ttk.Checkbutton(panel, text=item, variable=variable).grid(row=row, column=0, sticky="w", pady=4)
        row = len(self.difficulty_vars) + 1  # 어려움 항목 수에 맞춰 아래 칸을 이어 붙인다.
        ttk.Label(panel, text="Additional notes", style="CardTitle.TLabel").grid(row=row, column=0, sticky="w", pady=(16, 8))
        panel.columnconfigure(0, weight=1)
        self.reflection_box = tk.Text(panel, height=5, width=1, wrap="word", font=(self.font, 11), padx=10, pady=8, relief="solid", borderwidth=1)
        self.reflection_box.grid(row=row + 1, column=0, sticky="ew")
        self.reflection_box.insert("1.0", getattr(self, "reflection_draft", ""))
        ttk.Label(panel, text="작성 중 점검 항목은 답안 화면의 체크 상태대로 저장됩니다.", style="CardText.TLabel", wraplength=600).grid(row=row + 2, column=0, sticky="w", pady=(10, 18))
        buttons = ttk.Frame(panel, style="Card.TFrame")
        buttons.grid(row=row + 3, column=0, sticky="ew")
        ttk.Button(buttons, text="Back to answer", command=self._return_to_writing).pack(side="left")
        ttk.Button(buttons, text="Save", style="Primary.TButton", command=self._save_practice).pack(side="right")

    def _return_to_writing(self):
        self.reflection_draft = self.reflection_box.get("1.0", "end-1c")
        self.show_page("문제 풀이")

    def _save_practice(self):
        now = datetime.now()
        selection = self.practice_selection
        answer_name = f"{now.strftime('%Y%m%d_%H%M%S_%f')}_type{selection['type']}_{selection['difficulty']}.txt"
        answer_path = self.workspace / "answers" / answer_name
        reviewed_items = [label for label, var in self.review_vars if var.get()]
        difficulty_items = [label for label, var in self.difficulty_vars if var.get()]
        reflection = self.reflection_box.get("1.0", "end-1c").strip()
        record = {
            "completed_at": now.isoformat(timespec="seconds"),
            "difficulty": selection["difficulty"],
            "type": selection["type"],
            "prompt_id": self.practice_prompt["id"],
            "prompt": self.practice_prompt["text"],
            "duration_seconds": max(0, self.practice_duration_seconds),
            "time_limit_seconds": TIME_LIMIT_SECONDS,
            "overtime_seconds": getattr(self, "overtime_seconds", 0),
            "answer_file": str(answer_path),
            "answer": self.practice_answer,
            "word_count": len(self.practice_answer.split()),
            "email_parts": {"greeting": self.email_greeting, "body": self.email_body.strip(), "closing": self.email_closing.strip()},
            "review_items": reviewed_items,
            "difficulty_items": difficulty_items,
            "reflection": reflection,
        }
        try:
            answer_path.parent.mkdir(parents=True, exist_ok=True)
            answer_path.write_text(self.practice_answer, encoding="utf-8")
            records_path = self.workspace / "practice_records.json"
            if records_path.exists():
                records = json.loads(records_path.read_text(encoding="utf-8"))
                if not isinstance(records, list):
                    records = []
            else:
                records = []
            records.append(record)
            records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError) as error:
            messagebox.showerror("저장 오류", f"답안 또는 학습 기록을 저장하지 못했습니다.\n{error}", parent=self)
            return

        messagebox.showinfo("저장 완료", "학습 폴더에 저장했습니다.", parent=self)
        self.practice_selection = None
        self.current_page = None
        self.show_page("홈")

    # ----- Saved records -----

    def _load_records(self):
        """practice_records.json을 읽어 (최신순 기록 목록, 읽지 못한 기록 수)를 돌려준다."""
        records_path = self.workspace / "practice_records.json"
        if not records_path.exists():
            return [], 0
        try:
            raw_records = json.loads(records_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            messagebox.showerror("기록 불러오기 오류", f"연습 기록 파일을 읽지 못했습니다.\n{error}", parent=self)
            return [], 0
        if not isinstance(raw_records, list):
            return [], 0

        records = [record for record in raw_records if isinstance(record, dict) and "type" in record]
        for record in records:
            # 예전 버전에서 저장한 기록에는 없는 항목을 채워 둔다. (예전 제한시간은 10분)
            record.setdefault("answer", "")
            record.setdefault("prompt", "")
            record.setdefault("prompt_id", None)
            record.setdefault("reflection", "")
            record.setdefault("review_items", [])
            record.setdefault("difficulty_items", [])
            record.setdefault("duration_seconds", 0)
            record.setdefault("answer_file", "")
            record.setdefault("word_count", len(record["answer"].split()))
            record.setdefault("overtime_seconds", max(0, record["duration_seconds"] - 10 * 60))
        records.sort(key=lambda record: record.get("completed_at", ""), reverse=True)
        return records, len(raw_records) - len(records)

    def _show_empty_records(self, row):
        panel = ttk.Frame(self.content, style="Card.TFrame", padding=24)
        panel.grid(row=row, column=0, sticky="new")
        ttk.Label(panel, text="저장된 연습 기록이 없습니다.", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(panel, text="자가점검까지 저장한 연습이 여기에 표시됩니다.", style="CardText.TLabel", wraplength=500).pack(anchor="w", pady=(10, 18))
        ttk.Button(panel, text="연습하러 가기", style="Primary.TButton", command=lambda: self.show_page("연습하기")).pack(anchor="w")

    # ----- 오답노트 -----

    def _show_notes(self):
        ttk.Label(self.content, text="오답노트", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        records, skipped = self._load_records()
        subtitle = "기록을 선택해 답안과 어려움·메모를 확인합니다. 자동 채점은 하지 않습니다."
        if skipped:
            subtitle += f" (읽을 수 없는 기록 {skipped}건 제외)"
        ttk.Label(self.content, text=subtitle, style="Sub.TLabel", wraplength=760).grid(row=1, column=0, sticky="w", pady=(8, 16))
        if not records:
            self._show_empty_records(row=2)
            return
        self.notes_records = records

        # 필터: 유형, 난이도
        filters = ttk.Frame(self.content)
        filters.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(filters, text="유형").pack(side="left", padx=(0, 6))
        self.notes_type_var = tk.StringVar(value="전체 유형")
        type_box = ttk.Combobox(filters, textvariable=self.notes_type_var, values=["전체 유형"] + [type_short(n) for n in EMAIL_TYPES], state="readonly", width=14)
        type_box.pack(side="left", padx=(0, 18))
        ttk.Label(filters, text="난이도").pack(side="left", padx=(0, 6))
        self.notes_level_var = tk.StringVar(value="전체 난이도")
        level_box = ttk.Combobox(filters, textvariable=self.notes_level_var, values=["전체 난이도", "상", "중", "하"], state="readonly", width=10)
        level_box.pack(side="left")
        type_box.bind("<<ComboboxSelected>>", self._refresh_notes_list)
        level_box.bind("<<ComboboxSelected>>", self._refresh_notes_list)
        self.notes_count_label = ttk.Label(filters, style="Sub.TLabel")
        self.notes_count_label.pack(side="right")

        self.content.rowconfigure(3, weight=1)
        body = ttk.Frame(self.content)
        body.grid(row=3, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1, uniform="notes")
        body.columnconfigure(1, weight=1, uniform="notes")
        body.rowconfigure(0, weight=1)

        # 왼쪽: 기록 목록
        list_frame = ttk.Frame(body, style="Card.TFrame", padding=12)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.notes_list = tk.Listbox(list_frame, font=(self.font, 10), relief="flat", highlightthickness=0, activestyle="none", selectbackground="#E3E6FA", selectforeground="#20263A", exportselection=False)
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.notes_list.yview)
        self.notes_list.configure(yscrollcommand=list_scroll.set)
        list_scroll.pack(side="right", fill="y")
        self.notes_list.pack(side="left", fill="both", expand=True)
        self.notes_list.bind("<<ListboxSelect>>", self._on_note_select)

        # 오른쪽: 선택한 기록의 상세 내용
        detail_frame = ttk.Frame(body, style="Card.TFrame", padding=18)
        detail_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        # 버튼을 먼저 아래쪽에 배치해 창이 작아져도 가려지지 않게 한다.
        self.retry_button = ttk.Button(detail_frame, text="이 문제 다시 풀기", style="Primary.TButton", command=self._retry_note)
        self.retry_button.pack(side="bottom", anchor="e", pady=(12, 0))
        self.note_detail = tk.Text(detail_frame, wrap="word", font=(self.font, 10), relief="flat")
        detail_scroll = ttk.Scrollbar(detail_frame, orient="vertical", command=self.note_detail.yview)
        self.note_detail.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side="right", fill="y")
        self.note_detail.pack(side="left", fill="both", expand=True)

        self._refresh_notes_list()

    def _refresh_notes_list(self, _event=None):
        type_filter = self.notes_type_var.get()
        level_filter = self.notes_level_var.get()
        # 필터를 통과한 기록만 모은다. 목록의 n번째 줄 = shown_records[n]
        self.shown_records = []
        for record in self.notes_records:
            if type_filter != "전체 유형" and type_short(record["type"]) != type_filter:
                continue
            if level_filter != "전체 난이도" and record.get("difficulty") != level_filter:
                continue
            self.shown_records.append(record)

        self.notes_list.delete(0, "end")
        for record in self.shown_records:
            tags = ", ".join(DIFFICULTY_TAGS.get(item, item) for item in record["difficulty_items"]) or "-"
            memo = record["reflection"].replace("\n", " ")[:12]
            self.notes_list.insert("end", f"{format_datetime(record.get('completed_at', ''))[5:]} | {type_short(record['type'])} | {record.get('difficulty', '')} | {tags} | {memo}")

        self.notes_count_label.configure(text=f"{len(self.shown_records)} / {len(self.notes_records)}건")
        if self.shown_records:
            self.notes_list.selection_set(0)
            self._show_note_detail(self.shown_records[0])
        else:
            self._show_note_detail(None)

    def _on_note_select(self, _event=None):
        selected = self.notes_list.curselection()
        if selected:
            self._show_note_detail(self.shown_records[selected[0]])

    def _show_note_detail(self, record):
        self.selected_note = record
        self.retry_button.configure(state="disabled" if record is None else "normal")
        if record is None:
            text = "조건에 맞는 기록이 없습니다."
        else:
            lines = [
                format_datetime(record.get("completed_at", "")),
                f"{type_label(record['type'])} · 난이도 {record.get('difficulty', '')} · {record['word_count']} words · 작성 시간 {format_duration(record['duration_seconds'])}",
            ]
            if record["overtime_seconds"]:
                lines.append(f"제한시간 {format_duration(record['overtime_seconds'])} 초과")

            lines += ["", "[문제]", record["prompt"] or "저장된 문제 내용이 없습니다."]
            if record["prompt_id"] is None:
                lines.append("(문제은행 연결 전 기록으로, 임시 문구가 저장되어 있습니다.)")

            lines += ["", "[내 답안]", record["answer"] or "(빈 답안)"]

            lines += ["", "[작성 중 체크한 항목]"]
            for item in REVIEW_ITEMS:
                mark = "☑" if item in record["review_items"] else "☐"
                lines.append(f"{mark} {item}")

            lines += ["", "[연습 후 어려움 항목]"]
            if record["difficulty_items"]:
                for item in record["difficulty_items"]:
                    lines.append(f"• {item}")
            else:
                lines.append("선택한 어려움 항목이 없습니다.")

            lines += ["", "[복습 메모]", record["reflection"] or "남긴 메모가 없습니다."]
            if record["answer_file"]:
                lines += ["", "[답안 파일]", record["answer_file"]]
            text = "\n".join(lines)

        self.note_detail.configure(state="normal")
        self.note_detail.delete("1.0", "end")
        self.note_detail.insert("1.0", text)
        self.note_detail.configure(state="disabled")

    # ----- 학습통계 -----

    def _show_stats(self):
        ttk.Label(self.content, text="학습통계", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        records, skipped = self._load_records()
        subtitle = "저장된 연습 기록의 학습통계."
        if skipped:
            subtitle += f" (읽을 수 없는 기록 {skipped}건 제외)"
        ttk.Label(self.content, text=subtitle, style="Sub.TLabel", wraplength=760).grid(row=1, column=0, sticky="w", pady=(8, 16))
        if not records:
            self._show_empty_records(row=2)
            return

        self.content.rowconfigure(2, weight=1)
        body = self._make_scrollable(self.content, row=2)
        body.columnconfigure((0, 1), weight=1, uniform="stats")

        total = len(records)
        average_words = sum(record["word_count"] for record in records) / total
        average_duration = sum(record["duration_seconds"] for record in records) / total
        overtime_count = sum(1 for record in records if record["overtime_seconds"] > 0)

        tiles = ttk.Frame(body)
        tiles.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        tiles.columnconfigure((0, 1, 2, 3), weight=1, uniform="tile")
        tile_values = [
            ("총 연습 횟수", f"{total}회"),
            ("평균 단어 수", f"{average_words:.0f} words"),
            ("평균 작성 시간", format_duration(average_duration)),
            ("제한시간 초과", f"{overtime_count}회 ({overtime_count / total:.0%})"),
        ]
        for col, (label, value) in enumerate(tile_values):
            tile = ttk.Frame(tiles, style="Card.TFrame", padding=16)
            tile.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0 if col == 3 else 6))
            ttk.Label(tile, text=label, style="CardText.TLabel").pack(anchor="w")
            ttk.Label(tile, text=value, style="StatValue.TLabel").pack(anchor="w", pady=(6, 0))

        type_counts = Counter(record["type"] for record in records)
        # 이름이 길면 막대와 횟수가 밀려 잘리므로 통계에서는 짧은 이름을 쓴다.
        type_rows = [(type_short(n), type_counts.get(n, 0)) for n in EMAIL_TYPES]
        type_rows += [(type_short(n), count) for n, count in sorted(type_counts.items()) if n not in EMAIL_TYPES]
        self._make_count_card(body, 1, 0, "이메일 유형별 연습 횟수", type_rows, total, rowspan=2)

        level_counts = Counter(record["difficulty"] for record in records)
        self._make_count_card(body, 1, 1, "난이도별 연습 횟수", [(level, level_counts.get(level, 0)) for level in ("상", "중", "하")], total)

        difficulty_counts = Counter(item for record in records for item in record["difficulty_items"])
        difficulty_rows = [(DIFFICULTY_TAGS[item], difficulty_counts.get(item, 0)) for item in DIFFICULTY_ITEMS]
        difficulty_rows += [(DIFFICULTY_TAGS.get(item, item), count) for item, count in difficulty_counts.items() if item not in DIFFICULTY_ITEMS]
        self._make_count_card(body, 2, 1, "연습 후 어려움 항목", difficulty_rows, total)

        review_counts = Counter(item for record in records for item in record["review_items"])
        review_rows = [(item, review_counts.get(item, 0)) for item in REVIEW_ITEMS]
        self._make_count_card(body, 3, 0, f"작성 중 체크 항목별 빈도 (전체 {total}회 중)", review_rows, total, columnspan=2)

    def _make_count_card(self, parent, row, column, title, rows, total, rowspan=1, columnspan=1):
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        if columnspan == 2:
            padx = 0
        else:
            padx = (0, 7) if column == 0 else (7, 0)
        card.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew", padx=padx, pady=(0, 14))
        card.columnconfigure(1, weight=1)
        ttk.Label(card, text=title, style="SmallTitle.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        next_row = 1
        for offset, (label, count) in enumerate(rows):
            ttk.Label(card, text=label, style="CardBody.TLabel").grid(row=next_row + offset, column=0, sticky="w", padx=(0, 12), pady=3)
            ttk.Progressbar(card, style="Stat.Horizontal.TProgressbar", maximum=max(total, 1), value=count).grid(row=next_row + offset, column=1, sticky="ew")
            ttk.Label(card, text=f"{count}회", style="CardBody.TLabel").grid(row=next_row + offset, column=2, sticky="e", padx=(10, 0))

    def _make_scrollable(self, parent, row):
        """Return a frame inside a vertically scrollable canvas placed at the given grid row."""
        holder = ttk.Frame(parent)
        holder.grid(row=row, column=0, columnspan=2, sticky="nsew")
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)
        canvas = tk.Canvas(holder, background="#F5F6FA", highlightthickness=0)
        scroll = ttk.Scrollbar(holder, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        inner = ttk.Frame(canvas)
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width - 4))

        def on_wheel(event):
            # 마우스가 이 스크롤 영역(안쪽 위젯 포함) 위에 있을 때만 움직인다.
            pointed = self.winfo_containing(event.x_root, event.y_root)
            if pointed is None or not str(pointed).startswith(str(canvas)):
                return
            if inner.winfo_reqheight() > canvas.winfo_height():
                canvas.yview_scroll(int(-event.delta / 120), "units")

        # show_page()가 화면을 바꿀 때 unbind_all로 해제한다.
        canvas.bind_all("<MouseWheel>", on_wheel)
        return inner

    def _show_setup(self):
        ttk.Label(self.content, text="처음 설정", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.content,
            text="설정한 프로필과 폴더는 다음 실행부터 자동 적용됩니다.",
            style="Sub.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(12, 24))

        form = ttk.Frame(self.content, style="Card.TFrame", padding=24)
        form.grid(row=2, column=0, sticky="new")
        form.columnconfigure(1, weight=1)

        self.name_var = tk.StringVar(value=self.profile.get("name", "") if self.profile else "")
        self.exam_date_var = tk.StringVar(value=self.profile.get("exam_date", "") if self.profile else "")
        self.workspace_var = tk.StringVar(value=str(self.workspace) if self.workspace else "")

        ttk.Label(form, text="이름", style="Field.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 18), pady=8)
        ttk.Entry(form, textvariable=self.name_var, width=42).grid(row=0, column=1, sticky="ew", pady=8)
        ttk.Label(form, text="TOEFL 시험일 (YYYY-MM-DD)", style="Field.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 18), pady=8)
        ttk.Entry(form, textvariable=self.exam_date_var, width=42).grid(row=1, column=1, sticky="ew", pady=8)
        ttk.Label(form, text="학습 폴더", style="Field.TLabel").grid(row=2, column=0, sticky="w", padx=(0, 18), pady=8)
        folder_row = ttk.Frame(form, style="Card.TFrame")
        folder_row.grid(row=2, column=1, sticky="ew", pady=8)
        folder_row.columnconfigure(0, weight=1)
        ttk.Entry(folder_row, textvariable=self.workspace_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(folder_row, text="폴더 선택", command=self._choose_workspace).grid(row=0, column=1, padx=(8, 0))

        ttk.Label(
            form,
            text="프로필, 연습 기록, 답안 파일을 이 폴더에 저장합니다.",
            style="CardText.TLabel",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 18))
        ttk.Button(form, text="설정 저장하고 시작", style="Primary.TButton", command=self._save_setup).grid(row=4, column=0, columnspan=2, sticky="w")

    def _choose_workspace(self):
        selected = filedialog.askdirectory(title="WriteStep 학습 폴더 선택")
        if selected:
            self.workspace_var.set(selected)

    def _save_setup(self):
        name = self.name_var.get().strip()
        exam_date_text = self.exam_date_var.get().strip()
        folder_text = self.workspace_var.get().strip()

        if not name:
            messagebox.showerror("입력 확인", "이름을 입력하십시오.", parent=self)
            return
        try:
            exam_date = datetime.strptime(exam_date_text, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("입력 확인", "시험일을 YYYY-MM-DD 형식으로 입력하십시오.", parent=self)
            return
        if not folder_text or not Path(folder_text).is_dir():
            messagebox.showerror("폴더 확인", "저장할 폴더를 선택하십시오.", parent=self)
            return

        workspace = Path(folder_text).expanduser().resolve()
        profile = {"name": name, "exam_date": exam_date.isoformat()}
        try:
            workspace.mkdir(parents=True, exist_ok=True)
            (workspace / "profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
            records_path = workspace / "practice_records.json"
            if not records_path.exists():
                records_path.write_text("[]", encoding="utf-8")
            (workspace / "answers").mkdir(exist_ok=True)
            self.app_config_path.parent.mkdir(parents=True, exist_ok=True)
            self.app_config_path.write_text(
                json.dumps({"workspace": str(workspace)}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as error:
            messagebox.showerror("저장 오류", f"설정 파일을 저장하지 못했습니다.\n{error}", parent=self)
            return

        self.workspace = workspace
        self.profile = profile
        self.show_page("홈")

    def _load_saved_profile(self):
        """Load the selected study folder and profile, if they already exist."""
        try:
            config = json.loads(self.app_config_path.read_text(encoding="utf-8"))
            workspace = Path(config["workspace"]).expanduser()
            profile = json.loads((workspace / "profile.json").read_text(encoding="utf-8"))
            if profile.get("name") and profile.get("exam_date"):
                date.fromisoformat(profile["exam_date"])
                self.workspace = workspace
                self.profile = profile
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            self.workspace = None
            self.profile = None

    def _show_placeholder(self, page_name):
        ttk.Label(self.content, text=page_name, style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(self.content, text=f"{page_name} 화면 준비 중입니다.", style="Sub.TLabel").grid(row=1, column=0, sticky="nw", pady=(22, 0))


if __name__ == "__main__":
    app = WriteStepApp()
    app.mainloop()
