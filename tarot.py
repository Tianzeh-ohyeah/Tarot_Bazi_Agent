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

# --- 3. 资源定义 ---
def get_dynamic_lunar_params():
    """根据当前算命时刻，动态推算流年干支和紫微四化，拒绝 Hardcode"""
    now = datetime.now()
    year = now.year
    # 干支计算逻辑 (简化算法)
    gan = ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"]
    zhi = ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"]
    c_gan = gan[year % 10]
    c_zhi = zhi[year % 12]
    # 紫微四化逻辑（核心算力参数）
    si_hua_map = {
        "甲": "廉贞化禄、破军化权、武曲化科、太阳化忌",
        "乙": "天机化禄、天梁化权、紫微化科、太阴化忌",
        "丙": "天同化禄、天机化权、文昌化科、廉贞化忌",
        "丁": "太阴化禄、天同化权、天机化科、巨门化忌",
        "戊": "贪狼化禄、太阴化权、右弼化科、天机化忌",
        "己": "武曲化禄、贪狼化权、天梁化科、文曲化忌",
        "庚": "太阳化禄、武曲化权、太阴化科、天同化忌",
        "辛": "巨门化禄、太阳化权、文曲化科、文昌化忌",
        "壬": "天梁化禄、紫微化权、左辅化科、武曲化忌",
        "癸": "破军化禄、巨门化权、太阴化科、贪狼化忌"
    }
    return {
        "lunar_year": f"{c_gan}{c_zhi}",
        "si_hua": si_hua_map.get(c_gan, ""),
        "cur_date": now.strftime("%Y-%m-%d %H:%M")
    }

# --- 2. 资源定义：全量塔罗牌库 ---
MAJOR = ["愚者", "魔术师", "女教皇", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
SUITS = ["权杖", "圣杯", "宝剑", "星币"]
NUMS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "侍从", "骑士", "皇后", "国王"]
FULL_DECK = MAJOR + [f"{s}{n}" for s in SUITS for n in NUMS]
ZODIAC_HOURS = ["子时 (23:00-01:00)", "丑时 (01:00-03:00)", "寅时 (03:00-05:00)", "卯时 (05:00-07:00)", "辰时 (07:00-09:00)", "巳时 (09:00-11:00)", "午时 (11:00-13:00)", "未时 (13:00-15:00)", "申时 (15:00-17:00)", "酉时 (17:00-19:00)", "戌时 (19:00-21:00)", "亥时 (21:00-23:00)"]

class OracleSystem:
    def __init__(self, master):
        self.master = master
        master.title("TZ 多维算力决策系统 v2026")
        master.geometry("1100x950")
        master.configure(bg="#000000")
        
        self.C_GOLD = "#D4AF37"
        self.C_BG = "#000000"
        self.C_INPUT_BG = "#0A0A0F" 
        self.C_TEXT = "#FFFFFF"     
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=self.C_INPUT_BG, background="#222", foreground=self.C_TEXT, arrowcolor=self.C_GOLD)
        self.master.option_add("*TCombobox*Listbox.background", self.C_INPUT_BG)
        self.master.option_add("*TCombobox*Listbox.foreground", self.C_TEXT)
        self.master.option_add("*TCombobox*Listbox.selectBackground", self.C_GOLD)

        self.setup_ui()
        self.animate_stars()

    def setup_ui(self):
        self.master.grid_rowconfigure(0, weight=30) 
        self.master.grid_rowconfigure(1, weight=40) 
        self.master.grid_rowconfigure(2, weight=30) 
        self.master.grid_columnconfigure(0, weight=1)

        self.input_area = tk.Frame(self.master, bg=self.C_BG, padx=40, pady=5)
        self.input_area.grid(row=0, sticky="nsew")
        
        tk.Label(self.input_area, text="🔱 核心命理维度采集 🔱", fg=self.C_GOLD, bg=self.C_BG, font=("Microsoft YaHei", 12, "bold")).pack(pady=(10, 5))

        f1 = tk.Frame(self.input_area, bg=self.C_BG); f1.pack(fill="x", pady=5)
        tk.Label(f1, text="名讳:", fg=self.C_TEXT, bg=self.C_BG, font=("Microsoft YaHei", 10)).pack(side="left")
        self.name_ent = tk.Entry(f1, width=10, bg=self.C_INPUT_BG, fg=self.C_TEXT, insertbackground=self.C_GOLD, font=("Microsoft YaHei", 10), borderwidth=1, relief="solid")
        self.name_ent.pack(side="left", padx=5, ipady=3); self.name_ent.insert(0, "无名氏")

        tk.Label(f1, text="乾坤:", fg=self.C_TEXT, bg=self.C_BG, font=("Microsoft YaHei", 10)).pack(side="left", padx=(15, 0))
        self.gender_cb = ttk.Combobox(f1, values=["乾 (男)", "坤 (女)"], width=6, state="readonly")
        self.gender_cb.set("乾 (男)"); self.gender_cb.pack(side="left", padx=5)

        tk.Label(f1, text="出生地:", fg=self.C_TEXT, bg=self.C_BG, font=("Microsoft YaHei", 10)).pack(side="left", padx=(15, 0))
        self.place_ent = tk.Entry(f1, width=15, bg=self.C_INPUT_BG, fg=self.C_TEXT, insertbackground=self.C_GOLD, font=("Microsoft YaHei", 10), borderwidth=1, relief="solid")
        self.place_ent.pack(side="left", padx=5, ipady=3); self.place_ent.insert(0, "北京")

        f2 = tk.Frame(self.input_area, bg=self.C_BG); f2.pack(fill="x", pady=5)
        self.calendar_type = ttk.Combobox(f2, values=["阳历 (公历)", "阴历 (农历)"], width=10, state="readonly")
        self.calendar_type.set("阳历 (公历)"); self.calendar_type.pack(side="left")
        self.year_cb = ttk.Combobox(f2, values=[str(y) for y in range(1940, 2027)], width=6); self.year_cb.set("1996"); self.year_cb.pack(side="left", padx=5)
        self.month_cb = ttk.Combobox(f2, values=[f"{m:02d}" for m in range(1, 13)], width=4); self.month_cb.set("03"); self.month_cb.pack(side="left", padx=5)
        self.day_cb = ttk.Combobox(f2, values=[f"{d:02d}" for d in range(1, 32)], width=4); self.day_cb.set("05"); self.day_cb.pack(side="left", padx=5)
        self.hour_cb = ttk.Combobox(f2, values=ZODIAC_HOURS, width=12, state="readonly"); self.hour_cb.set("巳时 (09:00-11:00)"); self.hour_cb.pack(side="left", padx=10)

        f3 = tk.Frame(self.input_area, bg=self.C_BG); f3.pack(fill="x", pady=(10, 0))
        tk.Label(f3, text="心中祈愿之疑:", fg=self.C_GOLD, bg=self.C_BG, font=("Microsoft YaHei", 11, "bold")).pack(side="left")
        self.quest_ent = tk.Entry(f3, bg="#0F0F1A", fg=self.C_TEXT, insertbackground=self.C_GOLD, font=("Microsoft YaHei", 12), borderwidth=1, relief="solid")
        self.quest_ent.pack(side="left", fill="x", expand=True, padx=(10, 0), ipady=12)
        self.quest_ent.insert(0, "测算近期的事业财运发展")

        self.canvas = tk.Canvas(self.master, bg=self.C_BG, highlightthickness=0)
        self.canvas.grid(row=1, sticky="nsew")
        self.run_btn = tk.Button(self.canvas, text="✦ 开启算力合参 ✦", command=self.start_workflow, 
                                 bg=self.C_GOLD, fg="black", activebackground="#FFE082",
                                 font=("Microsoft YaHei", 14, "bold"), padx=50, pady=15, relief="flat", cursor="hand2")
        self.canvas_btn_window = self.canvas.create_window(550, 200, window=self.run_btn)

        output_frame = tk.Frame(self.master, bg=self.C_BG, padx=40, pady=15)
        output_frame.grid(row=2, sticky="nsew")
        self.out_panel = tk.Frame(output_frame, bg="#050505", highlightthickness=1, highlightbackground="#222")
        self.out_panel.pack(fill="both", expand=True)
        self.out_text = tk.Text(self.out_panel, wrap="word", bg="#050505", fg="#F0F0F0", font=("Microsoft YaHei", 11), padx=30, pady=20, borderwidth=0, spacing2=8)
        self.out_text.pack(fill="both", expand=True)

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
            "name": self.name_ent.get(), 
            "gender": self.gender_cb.get(),
            "place": self.place_ent.get(),
            "calendar": self.calendar_type.get(), 
            "question": self.quest_ent.get(),
            "birth": f"{self.year_cb.get()}-{self.month_cb.get()}-{self.day_cb.get()}",
            "hour": self.hour_cb.get()
        }
        threading.Thread(target=self._run_agents, args=(info,), daemon=True).start()

    def _run_agents(self, info):
        try:
            # 获取动态时空参数（非hardcode）
            lunar = get_dynamic_lunar_params()
            
            # 1. 真实洗牌与抽牌
            sample_cards = random.sample(FULL_DECK, 9)
            drawn_results = [{"card": card, "direction": random.choice(["正位", "逆位"])} for card in sample_cards]
            card_names = [f"{c['card']}({c['direction']})" for c in drawn_results]
            
            # 构造全量信息上下文，确保每个 Agent 拥有完整画像
            user_context = (f"【命主信息】姓名：{info['name']}，性别：{info['gender']}，出生地：{info['place']}，"
                            f"生辰：{info['calendar']} {info['birth']} {info['hour']}。\n"
                            f"【测算时空】公历日期：{lunar['cur_date']}，流年干支：{lunar['lunar_year']}年。\n"
                            f"【心中祈愿】：{info['question']}\n")

            # Agent 1: 八字大势算力
            self._write("【Agent 1】正在排演八字大势...\n")
            p1 = (user_context + 
                  f"你是一位命理逻辑大师。请基于以下维度合参：\n"
                  f"一、排出四柱干支及十神格局，判定喜忌与五行平衡度；\n"
                  f"二、深度推算当前{lunar['lunar_year']}对命局的交互，捕捉天克地冲、三合六合及岁运压力；\n"
                  f"三、运用神煞（贵人/煞星）与梅花易数体用逻辑锁定近期变数；\n"
                  f"四、将负面变量解读为‘性格的磨刀石’，将命理不足转化为‘待开启的修行课’。\n"
                  f"语气沉稳、古雅、透彻。限制100字。")
            a1_out = self.safe_generate_content(p1)

            # Agent 2: 紫微精细坐标
            self._write("【Agent 2】正在定位紫微宫位...\n")
            p2 = (user_context +
                  f"你是一位精通紫微斗数与星命学的专家。请基于以下维度合参：\n"
                  f"一、审视命盘格局与主星庙旺，重点分析‘三方四正’的能量守恒与‘身宫’后天倾向；\n"
                  f"二、锁定当前流年四化：{lunar['si_hua']}，推演其对原局宫位的引动，定位化禄的支点与化忌的雷区；\n"
                  f"三、计算六煞星（如铃星、陀罗）对诉求宫位的干扰程度；\n"
                  f"四、将煞星解读为‘环境给予的特殊考验’，将挫折视为‘时空坐标的重组’。\n"
                  f"语气睿智、透彻、具穿透力。限制100字。")
            a2_out = self.safe_generate_content(p2)

            # Agent 3: 塔罗全量变量
            self._write(f"【Agent 3】塔罗九阵能量同步中...\n")
            p3 = (user_context +
                  f"你是一位塔罗决策专家。请基于当前九星阵：{card_names} 进行时空扫描：\n"
                  f"一、解读阵中‘核心轴线’的能量流动，判定用户诉求（{info['question']}）在短期内的变量与阻力点；\n"
                  f"二、带入流年{lunar['lunar_year']}火旺磁场，分析四元素牌组（权杖/圣杯/宝剑/星币）的消长：火强则动，水弱则躁，土燥则裂，金熔则变；\n"
                  f"三、对‘死神、高塔、恶魔’等重度牌意进行‘向死而生’的叙事性转化，揭示深层潜意识指引。\n"
                  f"要求：话术具画面感，限制100字。")
            a3_out = self.safe_generate_content(p3)

            # Agent 4: 智慧合参
            self._write("【Agent 4】正在进行多维算力收敛...\n")
            p4 = (f"你是【最高合参主祭司】。你的使命是将三个平行时空的推演结果收敛为唯一的生命指南。\n"
                f"1. 八字({a1_out}) 占比40%：底层气数，决定了今年事业/感情的‘水位高低’。\n"
                f"2. 紫微({a2_out}) 占比30%：空间人事，决定了风险和机会具体落在哪个‘宫位’。\n"
                f"3. 塔罗({a3_out}) 占比10%：短期灵性，捕捉命主当下的‘心理状态’对因果的微调。\n"
                f"4. 年份({lunar['lunar_year']}) 占比20%：时空背景，基于{lunar['lunar_year']}的特性，如2026丙午年‘离火九运、赤马躁动’，判定大环境对命主原局的压制或助燃。\n\n"
                f"【冲突对冲规则】：\n"
                f"- 若八字/紫微吉，年份背景/塔罗凶：定性为‘在动荡环境中逆势而上，虽有外部喧嚣，但根基稳固’。\n"
                f"- 若八字/紫微凶，年份背景/塔罗吉：定性为‘虚火旺盛之局，当下的好运多为幻象，切忌贪大求全’。\n"
                f"- 四者冲突时：以八字定调，以年份定气，以紫微定损益，以塔罗定破局点。\n\n"
                f"【核心任务】：\n"
                f"请基于上述权重分配，针对诉求（{info['question']}）编撰一段【命运剧本】。\n\n"
                f"【叙事任务】：\n"
                f"不要罗列术语。请以‘在接下来的时空里，你正在经历一段...’开头，针对诉求描述接下来会发生的好事与转机。\n"
                f"因果线：从当下的念头(塔罗)出发 -> 经过2026大环境的洗礼 -> 遇到具体的事件节点(紫微) -> 最终回归天定好局(八字)。\n"
                f"必须包含：具体月份、贵人特征、避灾动作、最终好结果。\n"
                f"【输出要求】：\n"
                f"一、📖【命运剧本】(沉浸式叙事，引导用户往好了想，往对了做)\n"
                f"二、✨【福缘指引】(具体的方位、颜色、数字)\n"
                f"三、🛡️【避忌暗礁】(为了剧本圆满，需要避开的具体行为)\n"
                f"限制500字。")
            a4_out = self.safe_generate_content(p4)

            self.master.after(0, lambda: self._final_display(a4_out, info))
        except Exception as e:
            self._write(f"\n[算力中断]: {e}")
            self.master.after(0, lambda: self.run_btn.config(state="normal", text="✦ 重新开启推演 ✦"))

    def _final_display(self, a4_out, info):
        self.out_text.delete("1.0", tk.END) # 关键：清空之前的计算过程提示
        
        # 1. 瞬间展示抬头
        self.out_text.insert(tk.END, f"尊敬的 {info['name']} 阁下：\n", "gold_tag")
        self.out_text.insert(tk.END, f"针对您所关心的 “{info['question']}” \n")
        self.out_text.insert(tk.END, f"主祭司已合参多维算力，结合 2026 丙午流年气场为您开启命运演化。\n")
        self.out_text.insert(tk.END, f"{'—' * 60}\n\n")
        
        # 2. 调用极速分段打印 Agent 4 的结论
        self.paragraph_write(a4_out)
        
        # 3. 设置样式
        self.out_text.tag_config("gold_tag", foreground="#D4AF37", font=("Microsoft YaHei", 12, "bold"))
        
        # 4. 恢复按钮状态
        self.run_btn.config(state="normal", text="✦ 开启新一轮推演 ✦")

    def paragraph_write(self, text):
        """极速段落闪现，不磨叽"""
        lines = text.split('\n')
        for line in lines:
            self.out_text.insert(tk.END, line + '\n')
            self.out_text.update()
            time.sleep(0.03) # 极快速度，几乎秒出

    def _write(self, msg):
        self.master.after(0, lambda: self.out_text.insert(tk.END, msg))

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