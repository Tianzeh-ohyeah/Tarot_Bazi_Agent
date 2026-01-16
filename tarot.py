import os
import random
import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# --- 1. 核心修复：API 环境适配 ---
# 它会自动在你当前文件夹找 .env 文件并读取里面的变量
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"SDK 初始化失败: {e}")

def get_intelligent_model_pool():
    """动态探测可用模型并按性能排序"""
    try:
        models = client.models.list()
        pool = []
        for m in models:
            m_name = m.name.lower()
            # 排除非对话模型
            if any(x in m_name for x in ["embedding", "tts", "imagen", "aqa"]):
                continue
            if "gemini" in m_name:
                pool.append(m.name)
        
        # 2026 算力优先级排序
        def model_priority(name):
            name = name.lower()
            if "3-flash" in name: return 10
            if "2.5-flash" in name: return 8
            if "2.0-flash" in name: return 6
            if "1.5-pro" in name: return 4
            return 2

        pool.sort(key=model_priority, reverse=True)
        return pool if pool else ["models/gemini-1.5-flash"]
    except:
        # 保底固态列表
        return ["models/gemini-3-flash", "models/gemini-2.5-flash", "models/gemini-1.5-flash"]

# 全局算力状态
MODEL_POOL = get_intelligent_model_pool()
MODEL_LOCK = threading.Lock()
CURRENT_MODEL_INDEX = 0

# --- 2. 资源定义：全量塔罗牌库 ---
MAJOR = ["愚者", "魔术师", "女教皇", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
SUITS = ["权杖", "圣杯", "宝剑", "星币"]
NUMS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "侍从", "骑士", "皇后", "国王"]
FULL_DECK = MAJOR + [f"{s}{n}" for s in SUITS for n in NUMS]
ZODIAC_HOURS = ["子时 (23:00-01:00)", "丑时 (01:00-03:00)", "寅时 (03:00-05:00)", "卯时 (05:00-07:00)", "辰时 (07:00-09:00)", "巳时 (09:00-11:00)", "午时 (11:00-13:00)", "未时 (13:00-15:00)", "申时 (15:00-17:00)", "酉时 (17:00-19:00)", "戌时 (19:00-21:00)", "亥时 (21:00-23:00)"]

class OracleSystem:
    def __init__(self, master):
        self.master = master
        master.title("TZ 多维算力决策系统")
        master.geometry("1100x950")
        master.configure(bg="#000000")
        
        self.C_GOLD = "#D4AF37"
        self.C_BG = "#000000"
        self.C_INPUT_BG = "#0A0A0F" 
        self.C_TEXT = "#FFFFFF"     
        
        # 强制设置下拉框样式：黑底白字
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=self.C_INPUT_BG, background="#222", foreground=self.C_TEXT, arrowcolor=self.C_GOLD)
        self.master.option_add("*TCombobox*Listbox.background", self.C_INPUT_BG)
        self.master.option_add("*TCombobox*Listbox.foreground", self.C_TEXT)
        self.master.option_add("*TCombobox*Listbox.selectBackground", self.C_GOLD)

        self.setup_ui()
        self.animate_stars()

    def setup_ui(self):
        # 严格执行 30% : 40% : 30%
        self.master.grid_rowconfigure(0, weight=30) 
        self.master.grid_rowconfigure(1, weight=40) 
        self.master.grid_rowconfigure(2, weight=30) 
        self.master.grid_columnconfigure(0, weight=1)

        # --- 1. 输入区 (30%) ---
        self.input_area = tk.Frame(self.master, bg=self.C_BG, padx=40, pady=5)
        self.input_area.grid(row=0, sticky="nsew")
        
        # 标题装饰
        tk.Label(self.input_area, text="🔱 核心命理维度采集 🔱", fg=self.C_GOLD, bg=self.C_BG, font=("Microsoft YaHei", 12, "bold")).pack(pady=(10, 5))

        # 第一行：名讳与出生地
        f1 = tk.Frame(self.input_area, bg=self.C_BG); f1.pack(fill="x", pady=5)
        tk.Label(f1, text="名讳:", fg=self.C_TEXT, bg=self.C_BG, font=("Microsoft YaHei", 10)).pack(side="left")
        self.name_ent = tk.Entry(f1, width=12, bg=self.C_INPUT_BG, fg=self.C_TEXT, insertbackground=self.C_GOLD, font=("Microsoft YaHei", 10), borderwidth=1, relief="solid")
        self.name_ent.pack(side="left", padx=10, ipady=3); self.name_ent.insert(0, "无名氏")

        tk.Label(f1, text="出生地:", fg=self.C_TEXT, bg=self.C_BG, font=("Microsoft YaHei", 10)).pack(side="left", padx=(20, 0))
        self.place_ent = tk.Entry(f1, width=18, bg=self.C_INPUT_BG, fg=self.C_TEXT, insertbackground=self.C_GOLD, font=("Microsoft YaHei", 10), borderwidth=1, relief="solid")
        self.place_ent.pack(side="left", padx=10, ipady=3); self.place_ent.insert(0, "北京")

        # 第二行：生辰
        f2 = tk.Frame(self.input_area, bg=self.C_BG); f2.pack(fill="x", pady=5)
        self.calendar_type = ttk.Combobox(f2, values=["阳历 (公历)", "阴历 (农历)"], width=10, state="readonly")
        self.calendar_type.set("阳历 (公历)"); self.calendar_type.pack(side="left")
        self.year_cb = ttk.Combobox(f2, values=[str(y) for y in range(1940, 2027)], width=6); self.year_cb.set("1996"); self.year_cb.pack(side="left", padx=5)
        self.month_cb = ttk.Combobox(f2, values=[f"{m:02d}" for m in range(1, 13)], width=4); self.month_cb.set("03"); self.month_cb.pack(side="left", padx=5)
        self.day_cb = ttk.Combobox(f2, values=[f"{d:02d}" for d in range(1, 32)], width=4); self.day_cb.set("05"); self.day_cb.pack(side="left", padx=5)
        self.hour_cb = ttk.Combobox(f2, values=ZODIAC_HOURS, width=6, state="readonly"); self.hour_cb.set("巳时"); self.hour_cb.pack(side="left", padx=10)

        # 第三行：核心祈愿 (重点保障空间)
        f3 = tk.Frame(self.input_area, bg=self.C_BG); f3.pack(fill="x", pady=(10, 0))
        tk.Label(f3, text="心中祈愿之疑:", fg=self.C_GOLD, bg=self.C_BG, font=("Microsoft YaHei", 11, "bold")).pack(side="left")
        self.quest_ent = tk.Entry(f3, bg="#0F0F1A", fg=self.C_TEXT, insertbackground=self.C_GOLD, font=("Microsoft YaHei", 12), borderwidth=1, relief="solid")
        self.quest_ent.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=12) # 增加内部高度
        self.quest_ent.insert(0, "测算近期的事业财运发展")

        # --- 2. 星空动画区 (40%) ---
        self.canvas = tk.Canvas(self.master, bg=self.C_BG, highlightthickness=0)
        self.canvas.grid(row=1, sticky="nsew")
        self.run_btn = tk.Button(self.canvas, text="✦ 开启算力合参 ✦", command=self.start_workflow, 
                                 bg=self.C_GOLD, fg="black", activebackground="#FFE082",
                                 font=("Microsoft YaHei", 14, "bold"), padx=50, pady=15, relief="flat", cursor="hand2")
        self.canvas_btn_window = self.canvas.create_window(550, 200, window=self.run_btn)

        # --- 3. 输出展示区 (30%) ---
        output_frame = tk.Frame(self.master, bg=self.C_BG, padx=40, pady=15)
        output_frame.grid(row=2, sticky="nsew")
        self.out_panel = tk.Frame(output_frame, bg="#050505", highlightthickness=1, highlightbackground="#222")
        self.out_panel.pack(fill="both", expand=True)
        self.out_text = tk.Text(self.out_panel, wrap="word", bg="#050505", fg="#F0F0F0", font=("Microsoft YaHei", 11), padx=30, pady=20, borderwidth=0, spacing2=8)
        self.out_text.pack(fill="both", expand=True)

    # --- 核心修复：添加缺失的 API 生成方法 ---
    def safe_generate_content(self, prompt):
        global CURRENT_MODEL_INDEX
        for _ in range(len(MODEL_POOL)):
            with MODEL_LOCK: model_name = MODEL_POOL[CURRENT_MODEL_INDEX]
            try:
                response = client.models.generate_content(model=model_name, contents=prompt)
                if response and response.text: return response.text
            except Exception:
                with MODEL_LOCK: CURRENT_MODEL_INDEX = (CURRENT_MODEL_INDEX + 1) % len(MODEL_POOL)
                continue
        return "机群响应超时，请重试。"

    def start_workflow(self):
        self.out_text.delete("1.0", tk.END)
        self.run_btn.config(state="disabled", text="正在推演量子场...")
        info = {
            "name": self.name_ent.get(), "place": self.place_ent.get(),
            "calendar": self.calendar_type.get(), "question": self.quest_ent.get(),
            "birth": f"{self.year_cb.get()}-{self.month_cb.get()}-{self.day_cb.get()}",
            "hour": self.hour_cb.get()
        }
        threading.Thread(target=self._run_agents, args=(info,), daemon=True).start()

### Agent运行主体逻辑非必要不修改！！！(Start) ###
    def _run_agents(self, info):
        try:
            # 1. 真实洗牌与抽牌：确保算法透明
            # 从 78 张牌中随机抽取 9 张，并决定正逆位
            sample_cards = random.sample(FULL_DECK, 9)
            drawn_results = [{"card": card, "direction": random.choice(["正位", "逆位"])} for card in sample_cards]
            
            # Agent 1: 八字大势算力
            self._write("【Agent 1】正在排演八字大势...\n")
            p1 = (f"你是一位精通子平八字的命理逻辑师。针对诉求：{info['question']}，基于{info['calendar']} {info['birth']} {info['hour']}排盘。"
                  f"1. 核心任务：列出四柱干支、定格局、分析五行喜忌。2. 话术要求：将负面煞星转化为‘性格的磨刀石’，将命理不足转化为‘待开启的修行课’。"
                  f"语气沉稳、客观。限制180字。")
            a1_out = self.safe_generate_content(p1)

            # Agent 2: 紫微精细坐标
            self._write("【Agent 2】正在定位紫微宫位...\n")
            p2 = (f"你是一位精通紫微斗数的星命专家。基于{info['calendar']} {info['hour']}定位相关宫位。"
                  f"1. 核心任务：分析主星庙旺与辅星影响。2. 话术要求：若遇煞星，解读为‘环境给予的特殊考验’。语气睿智、透彻。限制180字。")
            a2_out = self.safe_generate_content(p2)

            # Agent 3: 塔罗全量变量（使用真实抽牌结果）
            self._write(f"【Agent 3】从78张全量牌库中抽取的九星阵为：{[c['card'] for c in drawn_results]}...\n")
            p3 = (f"作为塔罗决策师，解读九星阵：{drawn_results}。针对问题：{info['question']}。"
                  f"1. 任务：解读现状与短期变量。2. 话术要求：遇到死神、塔等牌时，解读为‘旧事物的告别与新生’。限制250字。")
            a3_out = self.safe_generate_content(p3)

            # Agent 4: 智慧合参
            self._write("【Agent 4】正在进行多维算力收敛...\n")
            p4 = (f"你是【最高合参主祭司】。整合：八字({a1_out})、紫微({a2_out})与塔罗({a3_out})。"
                  f"1. 任务目标：若用户问了具体问题({info['question']})，必须优先且犀利地回答该问题。2. 通用任务：若用户问题模糊，请通过叙事方式详细推演其未来3-6个月的【财运】、【感情】、【事业】。"
                  f"3. 叙事要求：具备画面感，描述具体特征（如对方外貌、具体月份、避坑行业）。4. 格式：必须包含【避坑指南】、【转运支点】、3个关键词、1句寄语。限制180字。")
            a4_out = self.safe_generate_content(p4)

            self.master.after(0, lambda: self._final_display(a1_out, a2_out, a3_out, a4_out, info, drawn_results))
        except Exception as e:
            self._write(f"\n[算力中断]: {e}")
            self.master.after(0, lambda: self.run_btn.config(state="normal", text="✦ 重新开启推演 ✦"))
### Agent运行主体逻辑非必要不修改！！！(END) ###
    def _final_display(self, a1, a2, a3, a4, info, cards):
        self.out_text.delete("1.0", tk.END)
        content = [
            f"🔱 {info['name']} · 多维合参报告 🔱",
            f"【 塔罗变量 】\n" + " | ".join([f"{c['card']}({c['direction']})" for c in cards]),
            f"【 八字推演 】\n{a1}",
            f"【 星命坐标 】\n{a2}",
            f"【 塔罗指引 】\n{a3}",
            f"【 综合指南 】\n{a4}"
        ]
        self.paragraph_write("\n\n".join(content))
        self.run_btn.config(state="normal", text="✦ 开启算力合参 ✦")

    def _write(self, msg):
        self.master.after(0, lambda: self.out_text.insert(tk.END, msg))

    def paragraph_write(self, text):
        for para in text.split('\n'):
            self.out_text.insert(tk.END, para + '\n')
            self.out_text.see(tk.END); self.out_text.update(); time.sleep(0.08)

    def animate_stars(self):
        self.canvas.delete("s")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w < 10: w, h = 1100, 380
        cx, cy = w/2, h/2
        if hasattr(self, 'canvas_btn_window'): self.canvas.coords(self.canvas_btn_window, cx, cy)
        t = time.time()
        for i in range(130):
            r = 10 + (i * 2.8)
            angle = t * (0.015 + i*0.0002) + i
            x, y = cx + r * 2.0 * math.cos(angle), cy + r * math.sin(angle)
            self.canvas.create_oval(x, y, x+1.5, y+1.5, fill=random.choice([self.C_GOLD, "white", "#333"]), outline="", tags="s")
        self.master.after(40, self.animate_stars)

if __name__ == "__main__":
    root = tk.Tk()
    app = OracleSystem(root)
    root.mainloop()