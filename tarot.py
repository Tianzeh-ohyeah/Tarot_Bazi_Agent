import os
import random
import tkinter as tk
from tkinter import ttk
import threading
import time
import math
from google import genai
from google.genai import types
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

# --- 2. 资源定义 ---
MAJOR = ["愚者", "魔术师", "女教皇", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
FULL_DECK = MAJOR + [f"{s}{n}" for s in ["权杖", "圣杯", "宝剑", "星币"] for n in ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "侍从", "骑士", "皇后", "国王"]]

class OracleSystem:
    def __init__(self, master):
        self.master = master
        master.title("TZ Tarot + Bazi Multi-Agent System")
        master.geometry("1100x950")
        master.configure(bg="#050508")

        # 核心色彩与样式
        self.C_GOLD = "#D4AF37"
        self.C_PURPLE_DARK = "#1A1A2E"
        self.C_INPUT_BG = "#12121A"
        self.FONT_INPUT = ("Microsoft YaHei", 11) # 约 11px
        self.FONT_TEXT = ("SimSun", 12)

        self.setup_styles()
        self.setup_ui()
        self.animate_stars()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # 定制 Combobox 样式模拟 iPhone 滚轮感
        style.configure("iPhone.TCombobox", 
                        fieldbackground=self.C_INPUT_BG, 
                        background=self.C_GOLD, 
                        foreground="white",
                        darkcolor=self.C_INPUT_BG,
                        lightcolor=self.C_GOLD,
                        font=self.FONT_INPUT)

    def setup_ui(self):
        # --- 布局 2:5:3 分配 ---

        # 1. 顶部输入面板 (占比 2 - 约 180px)
        self.top_panel = tk.Frame(self.master, bg="#050508", height=200)
        self.top_panel.pack(fill="x", padx=50, pady=10)
        self.top_panel.pack_propagate(False)

        # 姓名/性别/地点行
        row1 = tk.Frame(self.top_panel, bg="#050508")
        row1.pack(pady=10)
        
        tk.Label(row1, text="姓名", fg=self.C_GOLD, bg="#050508", font=self.FONT_INPUT).pack(side="left", padx=5)
        self.name_ent = tk.Entry(row1, width=12, bg=self.C_INPUT_BG, fg="white", font=self.FONT_INPUT,
                                borderwidth=0, highlightthickness=1, highlightbackground=self.C_GOLD, insertbackground="white")
        self.name_ent.pack(side="left", padx=10, ipady=2)
        self.name_ent.insert(0, "Placeholder")

        tk.Label(row1, text="性别", fg=self.C_GOLD, bg="#050508", font=self.FONT_INPUT).pack(side="left", padx=5)
        self.gender_cb = ttk.Combobox(row1, values=["男 (乾造)", "女 (坤造)"], width=10, style="iPhone.TCombobox")
        self.gender_cb.set("女 (坤造)"); self.gender_cb.pack(side="left", padx=10)

        tk.Label(row1, text="出生地", fg=self.C_GOLD, bg="#050508", font=self.FONT_INPUT).pack(side="left", padx=5)
        self.city_ent = tk.Entry(row1, width=12, bg=self.C_INPUT_BG, fg="white", font=self.FONT_INPUT,
                                borderwidth=0, highlightthickness=1, highlightbackground=self.C_GOLD)
        self.city_ent.pack(side="left", padx=10, ipady=2)
        self.city_ent.insert(0, "Placeholder")

        # iPhone 滚轮式时间选择行
        row2 = tk.Frame(self.top_panel, bg="#050508")
        row2.pack(pady=10)
        
        tk.Label(row2, text="生辰推演", fg=self.C_GOLD, bg="#050508", font=self.FONT_INPUT).pack(side="left", padx=5)
        self.year_cb = ttk.Combobox(row2, values=[str(y) for y in range(1960, 2031)], width=6, style="iPhone.TCombobox")
        self.year_cb.set("1998"); self.year_cb.pack(side="left", padx=2)
        
        self.month_cb = ttk.Combobox(row2, values=[f"{m:02d}" for m in range(1, 13)], width=4, style="iPhone.TCombobox")
        self.month_cb.set("08"); self.month_cb.pack(side="left", padx=2)
        
        self.day_cb = ttk.Combobox(row2, values=[f"{d:02d}" for d in range(1, 32)], width=4, style="iPhone.TCombobox")
        self.day_cb.set("15"); self.day_cb.pack(side="left", padx=2)
        
        self.hour_cb = ttk.Combobox(row2, values=[f"{h:02d}:00" for h in range(24)], width=6, style="iPhone.TCombobox")
        self.hour_cb.set("21:00"); self.hour_cb.pack(side="left", padx=10)

        # 2. 中部核心星阵 (占比 5 - 约 450px)
        self.mid_panel = tk.Frame(self.master, bg="#050508", height=450)
        self.mid_panel.pack(fill="x")
        self.mid_panel.pack_propagate(False)

        self.canvas = tk.Canvas(self.mid_panel, width=1100, height=450, bg="#050508", highlightthickness=0)
        self.canvas.pack()
        
        # 按钮悬浮在星阵中下方
        self.run_btn = tk.Button(self.mid_panel, text="✦ 开启三阶全量推演 ✦", command=self.start_workflow, 
                                bg=self.C_GOLD, fg="black", font=("Microsoft YaHei", 12, "bold"), 
                                padx=50, pady=12, relief="flat", cursor="hand2")
        self.canvas.create_window(550, 380, window=self.run_btn)

        # 3. 底部输出区 (占比 3 - 约 280px)
        self.bottom_panel = tk.Frame(self.master, bg=self.C_PURPLE_DARK, height=300)
        self.bottom_panel.pack(fill="both", expand=True, padx=50, pady=(0, 30))
        
        self.out_text = tk.Text(self.bottom_panel, wrap="word", bg=self.C_PURPLE_DARK, fg="#EEE", 
                                font=self.FONT_TEXT, padx=35, pady=30, borderwidth=0, spacing2=6)
        self.out_text.pack(side="left", fill="both", expand=True)
        
        scroll = tk.Scrollbar(self.bottom_panel, command=self.out_text.yview)
        scroll.pack(side="right", fill="y")
        self.out_text.config(yscrollcommand=scroll.set)

    # --- Agent 核心逻辑 (完整保留并优化) ---
    def start_workflow(self):
        self.out_text.delete("1.0", tk.END)
        self.run_btn.config(state="disabled", text="正在链接因果...")
        
        info = {
            "name": self.name_ent.get(), "gender": self.gender_cb.get(),
            "birth": f"{self.year_cb.get()}-{self.month_cb.get()}-{self.day_cb.get()}",
            "hour": self.hour_cb.get(), "city": self.city_ent.get()
        }
        threading.Thread(target=self._run_agents, args=(info,), daemon=True).start()

    def _run_agents(self, info):
        try:
            # AGENT 1: 八字专家
            self._write("【Agent 1: 正在排演东方八字...】\n")
            p1 = f"作为八字专家，解读{info['gender']}性命盘。姓名:{info['name']}, 生日:{info['birth']} {info['hour']}, 地点:{info['city']}。重点分析五行喜忌。限制120字。"
            a1_out = client.models.generate_content(model=AVAILABLE_MODEL, contents=p1).text
            
            # AGENT 2: 塔罗专家 (全量计算)
            self._write("【Agent 2: 正在感应西方塔罗全量象意...】\n")
            drawn_cards = [{"name": random.choice(FULL_DECK), "up": random.choice([True, False])} for _ in range(9)]
            p2 = f"作为塔罗祭司，解读9张牌：{drawn_cards}。必须详细给出【事业】、【爱情】、【金钱】三个维度的解析。限制250字。"
            a2_out = client.models.generate_content(model=AVAILABLE_MODEL, contents=p2).text
            
            # AGENT 3: 总结祭司
            self._write("【Agent 3: 正在合参天地最终预示...】\n")
            p3 = f"你是主祭司。基于八字报告：{a1_out} 和 塔罗报告：{a2_out}，为缘主{info['name']}做终极合参总结。寻找中西预示的交集。100字内。"
            a3_out = client.models.generate_content(model=AVAILABLE_MODEL, contents=p3).text

            self.master.after(0, lambda: self._final_display(a1_out, a2_out, a3_out))
        except Exception as e:
            self._write(f"\n[系统波动]: {e}")
            self.master.after(0, lambda: self.run_btn.config(state="normal", text="✦ 开启全量命理推演 ✦"))

    def _final_display(self, a1, a2, a3):
        self.out_text.delete("1.0", tk.END)
        header = f"✧ 缘主 {self.name_ent.get()} 之命合参报告 ✧\n" + "═"*50 + "\n\n"
        self.typewriter(header)
        self.typewriter(f"【 东方命理：干支定数 】\n{a1}\n\n")
        self.typewriter(f"【 西方塔罗：星辰全览 】\n{a2}\n\n")
        self.typewriter(f"【 终极合参：灵曦指引 】\n{a3}\n\n")
        self.run_btn.config(state="normal", text="✦ 开启全量命理推演 ✦")

    def _write(self, msg):
        self.master.after(0, lambda: self.out_text.insert(tk.END, msg))

    def typewriter(self, text):
        for char in text:
            self.out_text.insert(tk.END, char)
            self.out_text.see(tk.END)
            self.out_text.update()
            time.sleep(0.01)

    def animate_stars(self):
        """高尚感星阵逻辑"""
        self.canvas.delete("s")
        cx, cy = 550, 180
        t = time.time()
        for i in range(70):
            r = 60 + (i * 2.5)
            angle = t * (0.15 + i*0.002) + i
            x, y = cx + r * math.cos(angle), cy + r * math.sin(angle)
            color = random.choice([self.C_GOLD, "white", "#3D3D5C"])
            size = random.uniform(0.5, 2.5)
            self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline="", tags="s")
        self.master.after(40, self.animate_stars)

if __name__ == "__main__":
    root = tk.Tk()
    app = OracleSystem(root)
    root.mainloop()