import os
import random
import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from datetime import datetime  # 用于获取当前日期
from google import genai
from dotenv import load_dotenv

# --- 1. 核心修复：API 环境适配 ---
# 它会自动在你当前文件夹找 .env 文件并读取里面的变量
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
AVAILABLE_MODEL = "models/gemini-1.5-flash"
try:
    models = client.models.list()
    flash_models = [m.name for m in models if "flash" in m.name.lower()]
    if flash_models: 
        AVAILABLE_MODEL = flash_models[0] # 保持 models/gemini-1.5-flash 格式
except: 
    pass

# --- 2. 资源定义：全量塔罗牌库 ---
MAJOR = ["愚者", "魔术师", "女教皇", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
SUITS = ["权杖", "圣杯", "宝剑", "星币"]
NUMS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "侍从", "骑士", "皇后", "国王"]
# 构建 78 张全量牌组
FULL_DECK = MAJOR + [f"{s}{n}" for s in SUITS for n in NUMS]

# 十二时辰
ZODIAC_HOURS = [
    "子时 (23:00-01:00)", "丑时 (01:00-03:00)", "寅时 (03:00-05:00)", 
    "卯时 (05:00-07:00)", "辰时 (07:00-09:00)", "巳时 (09:00-11:00)", 
    "午时 (11:00-13:00)", "未时 (13:00-15:00)", "申时 (15:00-17:00)", 
    "酉时 (17:00-19:00)", "戌时 (19:00-21:00)", "亥时 (21:00-23:00)"
]

class OracleSystem:
    def __init__(self, master):
        self.master = master
        self.now = datetime.now()
        master.title("TZ 多维算力决策系统")
        master.geometry("1100x950")
        master.configure(bg="#050508")
        
        self.C_GOLD = "#D4AF37"
        self.C_BG = "#050508"
        self.C_CARD = "#0D0D14"
        
        self.setup_ui()
        self.animate_stars()

    def setup_ui(self):
        # --- 总体容器 ---
        main_container = tk.Frame(self.master, bg=self.C_BG)
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        # --- 1. 顶部面板：用户信息与诉求 (占比约 25%) ---
        input_card = tk.LabelFrame(main_container, text=" 缘主基本盘与诉求 ", fg=self.C_GOLD, bg=self.C_CARD, 
                                   font=("Microsoft YaHei", 10, "bold"), padx=20, pady=15, relief="flat", highlightthickness=1, highlightbackground="#222")
        input_card.pack(fill="x", side="top", pady=(0, 10))

        # 姓名与日历行
        row1 = tk.Frame(input_card, bg=self.C_CARD)
        row1.pack(fill="x", pady=5)
        
        tk.Label(row1, text="缘主姓名:", fg="#888", bg=self.C_CARD, font=("Microsoft YaHei", 9)).pack(side="left")
        self.name_ent = tk.Entry(row1, width=10, bg="#ffffff", fg="black", insertbackground="white", borderwidth=0, font=("Microsoft YaHei", 10))
        self.name_ent.pack(side="left", padx=(5, 20))
        self.name_ent.insert(0, "无名氏")

        tk.Label(row1, text="出生历法:", fg="#888", bg=self.C_CARD, font=("Microsoft YaHei", 9)).pack(side="left")
        self.calendar_type = ttk.Combobox(row1, values=["阳历 (公历)", "阴历 (农历)"], width=12)
        self.calendar_type.set("阳历 (公历)")
        self.calendar_type.pack(side="left", padx=5)

        tk.Label(row1, text="生辰时间:", fg="#888", bg=self.C_CARD, font=("Microsoft YaHei", 9)).pack(side="left", padx=(20, 5))
        self.year_cb = ttk.Combobox(row1, values=[str(y) for y in range(1930, self.now.year + 1)], width=6); self.year_cb.set("1996")
        self.year_cb.pack(side="left", padx=2)
        self.month_cb = ttk.Combobox(row1, values=[f"{m:02d}" for m in range(1, 13)], width=4); self.month_cb.set("03")
        self.month_cb.pack(side="left", padx=2)
        self.day_cb = ttk.Combobox(row1, values=[f"{d:02d}" for d in range(1, 32)], width=4); self.day_cb.set("05")
        self.day_cb.pack(side="left", padx=2)
        self.hour_cb = ttk.Combobox(row1, values=ZODIAC_HOURS, width=16); self.hour_cb.set("巳时 (09:00-11:00)")
        self.hour_cb.pack(side="left", padx=5)

        # 诉求行 (作为主视觉输入)
        row2 = tk.Frame(input_card, bg=self.C_CARD)
        row2.pack(fill="x", pady=(15, 0))
        tk.Label(row2, text="心中所求之事:", fg=self.C_GOLD, bg=self.C_CARD, font=("Microsoft YaHei", 11, "bold")).pack(side="left")
        self.quest_ent = tk.Entry(row2, bg="#1a1a24", fg="#FFF", insertbackground="white", borderwidth=0, font=("Microsoft YaHei", 12))
        self.quest_ent.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=8)
        self.quest_ent.insert(0, "测算近期的事业财运发展")

        # --- 2. 中部：星阵动画 (占比约 35%) ---
        mid_frame = tk.Frame(main_container, bg=self.C_BG)
        mid_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(mid_frame, bg=self.C_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # 按钮悬浮在 Canvas 之上
        self.run_btn = tk.Button(self.canvas, text="✦ 开启多维算力合参 ✦", command=self.start_workflow, 
                                 bg=self.C_GOLD, fg="black", activebackground="#B8962D",
                                 font=("Microsoft YaHei", 12, "bold"), padx=40, pady=10, relief="flat", cursor="hand2")
        # 在 Canvas 底部中心放置按钮
        self.canvas_btn_window = self.canvas.create_window(0, 0, window=self.run_btn)

        # --- 3. 底部：输出区 (占比约 40%) ---
        self.bottom_panel = tk.Frame(main_container, bg="#101018", highlightthickness=1, highlightbackground="#333")
        self.bottom_panel.pack(fill="both", expand=True, pady=(10, 0))
        
        self.out_text = tk.Text(self.bottom_panel, wrap="word", bg="#101018", fg="#DDD", 
                                font=("SimSun", 12), padx=30, pady=25, borderwidth=0, spacing2=8)
        self.out_text.pack(side="left", fill="both", expand=True)
        
        # 滚动条美化
        scrollbar = tk.Scrollbar(self.bottom_panel, command=self.out_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.out_text.config(yscrollcommand=scrollbar.set)

    # 逻辑部分保持原样 (start_workflow, _run_agents, _final_display, _write, typewriter)
    def start_workflow(self):
        self.out_text.delete("1.0", tk.END)
        self.run_btn.config(state="disabled", text="正在进行大数据底层排盘...")
        info = {
            "name": self.name_ent.get(), "calendar": self.calendar_type.get(),
            "birth": f"{self.year_cb.get()}-{self.month_cb.get()}-{self.day_cb.get()}",
            "hour": self.hour_cb.get(), "question": self.quest_ent.get()
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
            p1 = (f"你是一位精通子平八字的命理逻辑师。针对缘主诉求：{info['question']}，基于{info['calendar']} {info['birth']} {info['hour']}排盘。"
                  f"1. 核心任务：分析格局与五行喜忌。2. 话术要求：将负面煞星转化为‘性格的磨刀石’，将命理不足转化为‘待开启的修行课’。"
                  f"语气需沉稳、客观。限制180字。")
            a1_out = client.models.generate_content(model=AVAILABLE_MODEL, contents=p1).text

            # Agent 2: 紫微精细坐标
            self._write("【Agent 2】正在定位紫微宫位...\n")
            p2 = (f"你是一位精通紫微斗数的星命专家。基于{info['calendar']} {info['hour']}定位相关宫位。"
                  f"1. 核心任务：结合诉求分析主星庙旺与辅星影响。2. 话术要求：如果遇到‘煞星’，请解读为‘环境给予的特殊考验’，并指出其中隐藏的‘变强机会’。"
                  f"语气需睿智、透彻。限制180字。")
            a2_out = client.models.generate_content(model=AVAILABLE_MODEL, contents=p2).text

            # Agent 3: 塔罗全量变量（使用真实抽牌结果）
            self._write(f"【Agent 3】从78张全量牌库中抽取的九星阵为：{[c['card'] for c in drawn_results]}...\n")
            p3 = (f"作为塔罗决策师，解读9张牌阵结果：{drawn_results}。针对问题：{info['question']}。"
                  f"1. 核心任务：解读现状与短期变量。2. 话术要求：遇到死神、塔等牌时，解读为‘旧事物的告别与新生’或‘能量的剧烈转化点’。"
                  f"语气需极具疗愈感、温柔且坚定。限制250字。")
            a3_out = client.models.generate_content(model=AVAILABLE_MODEL, contents=p3).text

            # Agent 4: 智慧合参
            self._write("【Agent 4】正在进行多维算力收敛...\n")
            p4 = (f"你是【最高合参主祭司】。你需要整合：八字分析({a1_out})、紫微细节({a2_out})与塔罗变量({a3_out})。"
                  f"1. 核心算法：东方命理占70%权重，塔罗占30%权重。若多方皆吉，则强化信心，引导‘顺势而为’；若多方遇阻，则必须给出具体的‘避坑指南’。"
                  f"2. 疗愈话术：给运气不好的用户以‘希望的微光’和‘转运的支点’。让他们觉得‘不顺是暂时的，我有方法可以变得更好’。"
                  f"3. 总结：3个好运关键词，1句疗愈寄语。限制120字。")
            a4_out = client.models.generate_content(model=AVAILABLE_MODEL, contents=p4).text

            self.master.after(0, lambda: self._final_display(a1_out, a2_out, a3_out, a4_out, info, drawn_results))
        except Exception as e:
            self._write(f"\n[算力中断]: {e}")
            self.master.after(0, lambda: self.run_btn.config(state="normal", text="✦ 重新开启推演 ✦"))

### Agent运行主体逻辑非必要不修改！！！(END) ###

    def _final_display(self, a1, a2, a3, a4, info, cards):
        self.out_text.delete("1.0", tk.END)
        self.typewriter(f"✧ {info['name']} 之【{info['calendar']}】多维合参报告 ✧\n" + "═"*55 + "\n")
        self.typewriter(f"【 关键变量：塔罗真实抽牌阵 】\n| " + " | ".join([f"{c['card']}({c['direction']})" for c in cards]) + " |\n\n")
        self.typewriter(f"【 壹 · 八字算力推演 】\n{a1}\n\n")
        self.typewriter(f"【 贰 · 紫微宫位坐标 】\n{a2}\n\n")
        self.typewriter(f"【 叁 · 塔罗镜像参考 】\n{a3}\n\n")
        self.typewriter(f"【 肆 · 终极合参避坑指南 】\n{a4}\n\n")
        self.run_btn.config(state="normal", text="✦ 开启多维算力合参 ✦")

    def _write(self, msg):
        self.master.after(0, lambda: self.out_text.insert(tk.END, msg))

    def typewriter(self, text):
        for char in text:
            self.out_text.insert(tk.END, char); self.out_text.see(tk.END)
            self.out_text.update(); time.sleep(0.01)

    def animate_stars(self):
        self.canvas.delete("s")
        # 动态获取当前 Canvas 的中心位置
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w/2, h/2
        
        # 更新按钮位置
        self.canvas.coords(self.canvas_btn_window, cx, h - 50)
        
        t = time.time()
        for i in range(100):
            r = 30 + (i * 1.8)
            angle = t * (0.05 + i*0.0005) + i
            x, y = cx + r * math.cos(angle), cy + r * math.sin(angle)
            color = random.choice([self.C_GOLD, "white", "#333366"])
            self.canvas.create_oval(x, y, x+2, y+2, fill=color, outline="", tags="s")
        self.master.after(40, self.animate_stars)

if __name__ == "__main__":
    root = tk.Tk(); app = OracleSystem(root); root.mainloop()