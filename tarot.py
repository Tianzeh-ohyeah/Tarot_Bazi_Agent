import os
import random
import tkinter as tk
from tkinter import ttk
import threading
import time
import math
import json
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# --- 1. 核心修复：API 环境与算力探测 (完全保留你的原始逻辑) ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    print(f"SDK 初始化失败: {e}")

def get_intelligent_model_pool():
    """你的原始探测逻辑：排查黑名单，按性能排序"""
    try:
        models = client.models.list()
        pool = []
        black_list = ["computer-use", "embedding", "tts", "imagen", "aqa", "vision"]
        for m in models:
            m_name = m.name.lower()
            if "gemini" in m_name and not any(x in m_name for x in black_list):
                if any(v in m_name for v in ["flash", "pro"]):
                    full_name = m.name if m.name.startswith("models/") else f"models/{m.name}"
                    pool.append(full_name)
        def model_priority(name):
            n = name.lower()
            if "3-flash" in n: return 10
            if "2.0-flash" in n: return 8
            if "1.5-pro" in n: return 6
            return 0
        pool.sort(key=model_priority, reverse=True)
        return pool[:3] if pool else ["models/gemini-1.5-flash"]
    except:
        return ["models/gemini-1.5-flash"]

# --- 2. 动态命理资源 (还原你的流年四化逻辑) ---
def get_dynamic_lunar_params():
    now = datetime.now()
    year = now.year
    gan = ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"]
    zhi = ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"]
    c_gan = gan[year % 10]
    c_zhi = zhi[year % 12]
    si_hua_map = {
        "甲": "廉贞化禄、破军化权、武曲化科、太阳化忌", "乙": "天机化禄、天梁化权、紫微化科、太阴化忌",
        "丙": "天同化禄、天机化权、文昌化科、廉贞化忌", "丁": "太阴化禄、天同化权、天机化科、巨门化忌",
        "戊": "贪狼化禄、太阴化权、右弼化科、天机化忌", "己": "武曲化禄、贪狼化权、天梁化科、文曲化忌",
        "庚": "太阳化禄、武曲化权、太阴化科、天同化忌", "辛": "巨门化禄、太阳化权、文曲化科、文昌化忌",
        "壬": "天梁化禄、紫微化权、左辅化科、武曲化忌", "癸": "破军化禄、巨门化权、太阴化科、贪狼化忌"
    }
    return {"lunar_year": f"{c_gan}{c_zhi}", "si_hua": si_hua_map.get(c_gan, ""), "cur_date": now.strftime("%Y-%m-%d %H:%M")}

MAJOR = ["愚者", "魔术师", "女教皇", "女皇", "皇帝", "教皇", "恋人", "战车", "力量", "隐士", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔", "高塔", "星星", "月亮", "太阳", "审判", "世界"]
SUITS = ["权杖", "圣杯", "宝剑", "星币"]
NUMS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "侍从", "骑士", "皇后", "国王"]
FULL_DECK = MAJOR + [f"{s}{n}" for s in SUITS for n in NUMS]
ZODIAC_HOURS = [
    "子时 (23:00-01:00)", "丑时 (01:00-03:00)", "寅时 (03:00-05:00)", 
    "卯时 (05:00-07:00)", "辰时 (07:00-09:00)", "巳时 (09:00-11:00)", 
    "午时 (11:00-13:00)", "未时 (13:00-15:00)", "申时 (15:00-17:00)", 
    "酉时 (17:00-19:00)", "戌时 (19:00-21:00)", "亥时 (21:00-23:00)"
]

# --- 3. UI 重新编排 ---
class OracleSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("TZ 多维算力神谕决策系统 v2026")
        self.master.geometry("1150x950")
        self.master.configure(bg="#050508")
        
        self.C_GOLD = "#D4AF37"
        self.C_BG = "#050508"
        self.C_INPUT_BG = "#0A0A1F" 
        
        self.chat_history = [] 
        self.master_data = None 
        self.model_pool = get_intelligent_model_pool()

        self.style = ttk.Style()
        self.style.theme_use('clam')
        # 1. 基础配置
        self.style.configure("TCombobox", 
                             fieldbackground="#0A0A1F", 
                             background="#1A1A3A",
                             foreground="white",        # 默认文字白色
                             darkcolor="#0A0A1F", 
                             lightcolor="#0A0A1F",
                             bordercolor="#333333",
                             font=("Microsoft YaHei", 13))

        # 2. 核心修复：强制只读状态（readonly）下的文字也是白色
        self.style.map("TCombobox", 
                       foreground=[('readonly', 'white')], 
                       fieldbackground=[('readonly', "#0A0A1F")])
        
        # 核心：下拉弹出列表的字号与颜色全局注入 (针对 Windows 系统弹窗)
        self.master.option_add("*TCombobox*Listbox.background", self.C_INPUT_BG)
        self.master.option_add("*TCombobox*Listbox.foreground", "white")
        self.master.option_add("*TCombobox*Listbox.selectBackground", self.C_GOLD)
        self.master.option_add("*TCombobox*Listbox.selectForeground", "black")
        self.master.option_add("*TCombobox*Listbox.font", ("Microsoft YaHei", 14)) # 这里控制下拉出来的列表字号

        self.setup_ui()
        self.animate_stars()

    def setup_ui(self):
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.master, bg=self.C_BG, height=80, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        mid_container = tk.Frame(self.master, bg=self.C_BG)
        mid_container.grid(row=1, column=0, sticky="nsew", padx=25)
        mid_container.columnconfigure(1, weight=1)
        mid_container.rowconfigure(0, weight=1)

        # --- 左侧参数区 ---
        # 稍微加宽一点（从360到380），给大号字体留空间
        left_pillar = tk.Frame(mid_container, bg="#0D0D1A", width=380, bd=1, relief="flat", padx=25)
        left_pillar.grid(row=0, column=0, sticky="nsew")
        left_pillar.grid_propagate(False)

        tk.Label(left_pillar, text="🔱 维度参数矩阵", fg=self.C_GOLD, bg="#0D0D1A", font=("Microsoft YaHei", 18, "bold")).pack(pady=(20, 30))

        self.name_ent = self._create_input_pair(left_pillar, "✦ 您的姓名:", "无姓名")
        self.place_ent = self._create_input_pair(left_pillar, "✦ 您的出生地:", "上海市 黄浦区")
        
        # --- 极性与历法 ---
        tk.Label(left_pillar, text="✦ 极性与历法:", fg="#999", bg="#0D0D1A", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(15,0))
        f_row2 = tk.Frame(left_pillar, bg="#0D0D1A")
        f_row2.pack(fill="x", pady=10)
        self.gender_cb = ttk.Combobox(f_row2, values=["乾 (男)", "坤 (女)"], state="readonly", font=("Microsoft YaHei", 13))
        self.gender_cb.set("乾 (男)")
        self.gender_cb.pack(side="left", expand=True, padx=(0,5), ipady=6) 
        self.calendar_cb = ttk.Combobox(f_row2, values=["公历", "农历"], state="readonly", font=("Microsoft YaHei", 13))
        self.calendar_cb.set("公历")
        self.calendar_cb.pack(side="right", expand=True, ipady=6)

        # --- 降生日期 ---
        tk.Label(left_pillar, text="✦ 降生日期 (年/月/日):", fg="#999", bg="#0D0D1A", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(15,0))
        f_row3 = tk.Frame(left_pillar, bg="#0D0D1A")
        f_row3.pack(fill="x", pady=10)
        self.year_cb = ttk.Combobox(f_row3, values=[str(y) for y in range(1940, 2027)], width=6, font=("Microsoft YaHei", 13))
        self.year_cb.set("1996")
        self.year_cb.pack(side="left", ipady=6)
        self.month_cb = ttk.Combobox(f_row3, values=[f"{m:02d}" for m in range(1, 13)], width=4, font=("Microsoft YaHei", 13))
        self.month_cb.set("03")
        self.month_cb.pack(side="left", padx=5, ipady=6)
        self.day_cb = ttk.Combobox(f_row3, values=[f"{d:02d}" for d in range(1, 32)], width=4, font=("Microsoft YaHei", 13))
        self.day_cb.set("05")
        self.day_cb.pack(side="left", ipady=6)

        # --- 具体时辰 (移至日期下方，逻辑连贯) ---
        tk.Label(left_pillar, text="✦ 降生时辰:", fg="#999", bg="#0D0D1A", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(15,0))
        self.hour_cb = ttk.Combobox(left_pillar, values=ZODIAC_HOURS, state="readonly", font=("Microsoft YaHei", 13))
        self.hour_cb.set("巳时 (09:00-11:00)")
        self.hour_cb.pack(fill="x", pady=10, ipady=6)

        # --- 真太阳时校准 (紧跟时辰) ---
        f_sun = tk.Frame(left_pillar, bg="#0D0D1A")
        f_sun.pack(fill="x", pady=(5, 15))
        self.use_true_sun = tk.BooleanVar(value=False)
        self.sun_check = tk.Checkbutton(f_sun, text="校准真太阳时 (依据经度偏移)", variable=self.use_true_sun,
                                        bg="#0D0D1A", fg=self.C_GOLD, selectcolor="#0D0D1A",
                                        activebackground="#0D0D1A", activeforeground=self.C_GOLD,
                                        font=("Microsoft YaHei", 10))
        self.sun_check.pack(side="left")

        # --- 后续右侧和底部逻辑保持不变 ---
        right_panel = tk.Frame(mid_container, bg="#08080C", bd=1, relief="flat")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        
        self.out_text = tk.Text(right_panel, wrap="word", bg="#08080C", fg="#EFEFEF", font=("Microsoft YaHei", 13), 
                                padx=30, pady=30, bd=0, spacing2=10)
        self.scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.out_text.yview)
        self.out_text.configure(yscrollcommand=self.scrollbar.set)
        # 用户提问：金黄色，靠右 (rmargin 留一点边距，lmargin1/2 留出左侧大片空白)
        # 用户提问：金黄色，靠右对齐
        self.out_text.tag_configure("user_msg", 
                                    justify='right', 
                                    rmargin=50,       
                                    lmargin1=400,     # 强制左侧留白
                                    lmargin2=400, 
                                    spacing1=40,      
                                    foreground=self.C_GOLD, 
                                    font=("Microsoft YaHei", 12, "bold"))
        
        # 祭司回复：纯白色，靠左对齐
        self.out_text.tag_configure("boss_msg", 
                                    justify='left', 
                                    lmargin1=50, 
                                    lmargin2=50, 
                                    rmargin=150,      
                                    spacing1=15, 
                                    foreground="#FFFFFF", 
                                    font=("Microsoft YaHei", 13))
        
        # 金色强调：用于展示排盘数据
        self.out_text.tag_configure("gold_tag", 
                                    justify='left',
                                    lmargin1=50,
                                    lmargin2=50,
                                    foreground=self.C_GOLD, 
                                    font=("Microsoft YaHei", 13, "bold"))
        self.out_text.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        bottom_bar = tk.Frame(self.master, bg="#101025", height=130)
        bottom_bar.grid(row=2, column=0, sticky="ew")
        bottom_bar.grid_propagate(False)
        
        input_inner = tk.Frame(bottom_bar, bg="#101025", pady=30, padx=40)
        input_inner.pack(fill="both")

        tk.Label(input_inner, text="祈愿追问:", fg=self.C_GOLD, bg="#101025", font=("Microsoft YaHei", 12, "bold")).pack(side="left")
        
        self.quest_ent = tk.Entry(input_inner, bg="#050510", fg="white", font=("Microsoft YaHei", 15), 
                                  insertbackground=self.C_GOLD, bd=1, relief="solid", highlightthickness=2, 
                                  highlightbackground="#333", highlightcolor=self.C_GOLD)
        self.quest_ent.pack(side="left", fill="x", expand=True, padx=20, ipady=10)
        self.quest_ent.insert(0, "测算近期的事业财运发展")
        self.quest_ent.bind("<Return>", lambda e: self.start_workflow())
        
        self.run_btn = tk.Button(input_inner, text="✦ 开启推演 ✦", command=self.start_workflow, 
                                 bg=self.C_GOLD, fg="black", font=("Microsoft YaHei", 12, "bold"), 
                                 padx=40, relief="flat", cursor="hand2")
        self.run_btn.pack(side="right")
        
    def _lock_input(self):
        """锁定：清空输入框并禁用，防止用户乱点"""
        self.quest_ent.config(state="disabled", background="#121212") 
        self.run_btn.config(state="disabled", text="✦ 正在洞察天机...")

    def _unlock_input(self):
        """解锁：恢复输入功能"""
        self.quest_ent.config(state="normal", background=self.C_INPUT_BG)
        self.quest_ent.delete(0, tk.END) # 确保清空
        self.run_btn.config(state="normal", text="✦ 继续追问 ✦")
        self.quest_ent.focus_set() # 自动聚焦，方便直接打字

    def _create_input_pair(self, parent, label, default):
        tk.Label(parent, text=label, fg="#999", bg="#0D0D1A", font=("Microsoft YaHei", 11)).pack(anchor="w", pady=(20, 0))
        ent = tk.Entry(parent, bg=self.C_INPUT_BG, fg="white", bd=0, font=("Microsoft YaHei", 14), 
                       insertbackground="white", highlightthickness=1, highlightbackground="#333")
        ent.pack(fill="x", pady=10, ipady=6)
        ent.insert(0, default)
        return ent
    
    # --- 4. 核心逻辑恢复 (完全保留你的 safe_generate_with_fallback) ---
    def safe_generate_with_fallback(self, prompt, delay=0):
        if delay > 0: time.sleep(delay)
        for model_name in self.model_pool:
            try:
                res = client.models.generate_content(model=model_name, contents=prompt)
                if res and res.text: return res.text, model_name
            except Exception as e:
                if "429" in str(e): time.sleep(1.5)
                continue 
        return "【维度坍缩】: 算力节点暂无响应。", "None"

    def start_workflow(self):
        question = self.quest_ent.get().strip()
        if not question: return
        self.run_btn.config(state="disabled", text="正在读取天机...")
        
        # 封装当前用户信息 (含出生地)
        info = {
            "name": self.name_ent.get(), "gender": self.gender_cb.get(), "calendar": self.calendar_cb.get(),
            "place": self.place_ent.get(), "birth": f"{self.year_cb.get()}-{self.month_cb.get()}-{self.day_cb.get()}",
            "hour": self.hour_cb.get(), "is_true_sun": self.use_true_sun.get(), "question": question
        }

        # 判断是初次推演还是追问
        if self.master_data is None:
            self.out_text.delete("1.0", tk.END)
            threading.Thread(target=self._run_first_round, args=(info,), daemon=True).start()
        else:
            self._write(f"\n\n◈ 追问: {question}\n", "user_tag")
            threading.Thread(target=self._run_chat_round, args=(info,), daemon=True).start()

    def _run_first_round(self, info):
        """第一阶段：专家组演算并建立骨架 (完整整合：气数校验 + 名号中和 + 结论先行)"""
        # A. 暂存当前问题（供显示使用）
        self.current_q = self.quest_ent.get().strip()
        
        # B. 立即执行清空和禁用
        self.quest_ent.delete(0, tk.END)
        self.quest_ent.config(state="disabled", background="#121212") # 变灰
        self.run_btn.config(state="disabled", text="✦ 正在洞察天机...")
        try:
            # 1. 动态变量准备
            lunar = get_dynamic_lunar_params()
            sample_cards = random.sample(FULL_DECK, 9)
            card_names = [f"{c}({random.choice(['正位', '逆位'])})" for c in sample_cards]
            
            sun_active = info.get("is_true_sun", False)
            sun_logic = (
                f"【时空校准指示】：用户出生地[{info['place']}]，校准状态:{sun_active}。 "
                "若开启，请先计算真太阳时，作为干支定性的物理基准。"
            )

            self._write(">> 正在点燃星火，召集先哲建立命理数据矩阵...\n", "sys_tag")

            # 3. 专家组 JSON 逻辑 (核心：干支校验 + 名号中和)
            expert_p = (
                f"你是一个拥有严谨逻辑的命理演算矩阵。当前核心任务：回答用户提问【{info['question']}】。\n"
                f"{sun_logic}\n"
                f"命主数据：{info['name']}, {info['gender']}, 生辰{info['birth']} {info['hour']}。\n"
                f"环境背景：流年{lunar['lunar_year']}, 塔罗意向{card_names}。\n\n"
                "【执行协议 - 必须强制执行验证】：\n"
                "1. **底层排盘验证 (data_foundation)**：必须先列出日元干支及月令属性（如：戊土生于午月，身旺燥烈）。这是结论的化验单。\n"
                "2. **姓名中和分析 (name_logic)**：分析姓名【{info['name']}】对上述命局是‘调侯润局’还是‘加剧偏枯’。名字不改，只求中和。\n"
                "3. **权重博弈**：按[定数 > 姓名中和 > 流年 > 塔罗]权重定性。若塔罗与八字冲突，以八字原局定性。\n"
                "4. **直接定性 (oracle_spark)**：15字以内硬结论，针对提问直接给结果，严禁绕圈子。\n\n"
                "输出严格 JSON：{\"data_foundation\":\"核心排盘及月令状态\", \"name_logic\":\"名字对原局的中和特效说明\", "
                "\"oracle_spark\":\"对问题的硬核一句话结论\", \"metrics\":\"核心评分/指标\", "
                "\"path_a\":\"针对该问题的优化路径\", \"path_b\":\"针对该问题的风险对策\"}"
            )
            raw_json, m1 = self.safe_generate_with_fallback(expert_p)
            
            if not raw_json or "Error" in raw_json:
                raise Exception("API 未响应或 Token 耗尽，请检查网络或额度。")

            try:
                clean_j = raw_json.replace("```json", "").replace("```", "").strip()
                self.master_data = json.loads(clean_j)
            except:
                self.master_data = {"error": "解析失败", "oracle_spark": "抱歉，演算数据解析出错，请重试。"}

            # 4. 主祭司拟人化合成报告 (深度中和版)
            synthesis_p = (
                f"你是主祭司，一个洞悉时空、极具共情能力的命运提灯人。你的任务是针对【{info['question']}】与命主进行深度谈话。\n"
                f"已知数据底座（运算结果）：{json.dumps(self.master_data, ensure_ascii=False)}。\n\n"
                f"【谈话艺术准则】：\n"
                f"1. **破题结论**：开篇第一句话就要直接回应对方的祈愿 '{self.master_data.get('oracle_spark')}'。不寒暄，直接给对方一个笃定的支点。\n"
                f"2. **嵌入式验证（不生硬）**：在对话中自然地提到对方的气数底座 '{self.master_data.get('data_foundation')}'。你要通过描述五行强弱来解释他当下的心境或处境。例如：‘我看你命格中戊土生于夏日，这种燥烈感是你这段时间感到焦虑的底层原因...’。\n"
                f"3. **名号的能量场引导**：将名字 '{self.master_data.get('name_logic')}' 视为他已拥有的特殊能量。告诉他这股能量如何与他的命局（定数）产生共振，重点在于‘如何调动这股力量去解决他问的问题’，而非评价好坏。\n"
                f"4. **双向路径决策**：基于上述运算逻辑，给出 A 方案的进取和 B 方案的守成。分析这两种路径在他的气数背景下会产生怎样的后续回响，引导他做出最契合自身的选择。\n"
                f"5. **文学性与共鸣**：语调要睿智、通透且带有哲思。像老朋友在深夜指着星图谈心：‘你看，星星是这样运行的，而你的路可以这样走。’\n"
                f"6. **绝对扣题**：所有的推演（八字、姓名、塔罗）必须最终收束在【{info['question']}】的解答上，严禁答非所问。"
            )
            final_report, m2 = self.safe_generate_with_fallback(synthesis_p)
            
            self.chat_history.append({"role": "user", "content": info["question"]})
            self.chat_history.append({"role": "model", "content": final_report})
            self._final_display(final_report, m2)

        except Exception as e:
            # 拒绝玄学文案，直接报错
            self._write(f"\n[系统错误]: {str(e)}\n", "sys_tag")
            self.run_btn.config(state="normal", text="✦ 重新推演 ✦")

    def _run_chat_round(self, info):
        """第二阶段：追问模式 (基于记忆和权重逻辑对话)"""
        self.current_q = info["question"] # 确保 final_display 能拿到追问的内容
        self.master.after(0, self._lock_input)
        try:
            history_str = "\n".join([f"{h['role']}: {h['content']}" for h in self.chat_history[-2:]])
            prompt = (
                f"你是主祭司，命主的提灯人。已知背景：{json.dumps(self.master_data)}\n"
                f"上下文：{history_str}\n"
                f"用户追问：【{info['question']}】\n"
                f"【对话逻辑】：\n"
                f"1. 坚持‘定数为主，名字为辅，塔罗为象’的原则回答。如果用户不解，再次解释名字是如何在定数中起到‘中和’作用的。\n"
                f"2. 保持温暖且专业的语调，引导用户看清选择权在自己手中。"
            )
            response, m = self.safe_generate_with_fallback(prompt)
            if not response:
                raise Exception("没 Token 了，无法生成回复。")
            self.chat_history.append({"role": "user", "content": info["question"]})
            self.chat_history.append({"role": "model", "content": response})
            self._final_display(response, m, is_chat=True)
        except Exception as e:
            self._write(f"\n[追问失败]: {str(e)}", "sys_tag")
            self.master.after(0, self._unlock_input) # 失败也要解锁，不然输入框就废了

    def _final_display(self, text, model_name, is_chat=False):
        """剧场式交互：金黄提问右置，自动锁定与解锁输入"""
        
        # 1. 物理清场
        self.out_text.insert(tk.END, "\n" * 25) 

        # 2. 获取用户原话 
        # 注意：这里我们使用 self.current_q，因为它在输入框被禁用前就已经暂存了
        user_q = getattr(self, 'current_q', "请求指引")
        
        # 3. 在右侧显示金黄色的用户原话
        self.out_text.insert(tk.END, f"{user_q}\n", "user_msg")
        self.out_text.insert(tk.END, "\n", "boss_msg") 

        # 4. 演算底座展示
        if not is_chat:
            bazi = self.master_data.get('data_foundation', '')
            name = self.master_data.get('name_logic', '')
            spark = self.master_data.get("oracle_spark", "")
            evidence = (f"◈ 演算底座：{bazi}\n"
                        f"◈ 名号能量：{name}\n"
                        f"◈ 核心判定：{spark}\n\n")
            self.out_text.insert(tk.END, evidence, "boss_msg")

        # 5. 主祭司文字流生成
        def _anim():
            self.master.after(0, lambda: self.out_text.see(tk.END))
            
            for char in text:
                current_scroll = self.out_text.yview()
                is_at_bottom = current_scroll[1] >= 0.95
                self.master.after(0, lambda c=char: self.out_text.insert(tk.END, c, "boss_msg"))
                
                if is_at_bottom:
                    self.master.after(0, lambda: self.out_text.see(tk.END))
                time.sleep(0.01)
            
            # --- 关键修改：生成结束，调用解锁逻辑 ---
            self.master.after(0, self._unlock_input)

        threading.Thread(target=_anim, daemon=True).start()

    def _write(self, msg, tag=None):
        self.master.after(0, lambda: (self.out_text.insert(tk.END, msg, tag), self.out_text.see(tk.END)))

    # --- 动画逻辑 (自适应宽度修复) ---
    def animate_stars(self):
        self.canvas.delete("star")
        w = self.canvas.winfo_width()
        if w < 10: w = 1100  # 初始保护宽度
        h = 100
        t = time.time()
        
        # 增加一点深蓝色调的星星，配合金色，显得有层次感
        star_colors = [self.C_GOLD, "#ADD8E6", "#FFFACD", "#708090"] 
        
        for i in range(40):  # 数量稍微减少，强调质量
            # 这里的逻辑改为：每颗星都有自己的固定轨道半径和旋转速度
            # 使用 i 作为偏移量，让它们分布在不同的“星轨”上
            speed = 0.05 + (i % 5) * 0.02
            radius_x = (i * 20) % (w // 2) + 50
            radius_y = (i * 5) % 40 + 10
            
            # 计算平滑的星轨坐标
            center_x = w / 2
            center_y = h / 2
            
            angle = t * speed + i  # 随时间匀速转动
            x = center_x + math.sin(angle) * radius_x
            y = center_y + math.cos(angle * 0.5) * radius_y # Y轴慢一点，形成椭圆轨道
            
            # 星星的大小随位置微弱变化，产生呼吸感
            size = 1.0 + math.sin(t + i) * 0.5
            color = star_colors[i % len(star_colors)]
            
            # 绘制星星
            self.canvas.create_oval(
                x, y, x + size, y + size, 
                fill=color, 
                outline="", 
                tags="star"
            )
            
        # 保持 50ms 一次的刷新率，保证平滑度
        self.master.after(50, self.animate_stars)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call('tk', 'scaling', 1.25)
    except Exception:
        pass
    app = OracleSystem(root)
    root.mainloop()