import streamlit as st
import random
from typing import List

class WordItem:
    """单词数据类"""
    def __init__(self, text: str):
        self.text = text
        self.total_count = 0  # 总共出现次数
        self.last_seen_round = 0  # 上次出现的轮次
        self.visible = True  # 当前是否可见
        
    def to_dict(self):
        return {
            "text": self.text,
            "total_count": self.total_count,
            "last_seen": self.last_seen_round,
            "visible": self.visible
        }

class WordDisplay:
    def __init__(self, word: WordItem):
        self.word = word
        self.size = random.randint(30, 60)
        self.color = self._random_color()
        self.rotation = random.uniform(-15, 15)
        
    def _random_color(self):
        colors = [
            "#1e88e5", "#2e7d32", "#d32f2f",
            "#7b1fa2", "#f57c00", "#00897b",
            "#c2185b", "#3949ab", "#5d4037"
        ]
        return random.choice(colors)

class VocabularyApp:
    def __init__(self):
        self.words: List[WordItem] = []
        self.current_round = 0
        self.max_display = 15
        
        # 初始化session_state（仅初始化非小部件绑定状态）
        if "words" not in st.session_state:
            st.session_state.words = []
        if "current_round" not in st.session_state:
            st.session_state.current_round = 0
        if "need_clear_input" not in st.session_state:
            st.session_state.need_clear_input = False  # 标记是否需要清空输入框
        self.words = st.session_state.words
        self.current_round = st.session_state.current_round

    def add_word(self, text: str):
        if not text.strip():
            return
        new_word = WordItem(text.strip())
        self.words.append(new_word)
        self.current_round += 1
        self._update_visibility()
        st.session_state.words = self.words
        st.session_state.current_round = self.current_round

    def refresh_layout(self):
        self.current_round += 1
        self._update_visibility()
        st.session_state.current_round = self.current_round

    def clear_all_words(self):
        self.words = []
        self.current_round = 0
        st.session_state.words = []
        st.session_state.current_round = 0

    def _update_visibility(self):
        if len(self.words) <= self.max_display:
            for word in self.words:
                word.visible = True
                word.total_count += 1
                word.last_seen_round = self.current_round
            return
        
        sorted_words = sorted(self.words, key=lambda x: x.total_count)
        for i, word in enumerate(sorted_words):
            if i < self.max_display:
                word.visible = True
                word.total_count += 1
                word.last_seen_round = self.current_round
            else:
                rounds_since_last = self.current_round - word.last_seen_round
                if word.total_count <= 5 and rounds_since_last >= 2:
                    word.visible = True
                elif word.total_count <= 10 and rounds_since_last >= 3:
                    word.visible = True
                elif word.total_count > 10 and rounds_since_last >= 5:
                    word.visible = True
                else:
                    word.visible = False
                if word.visible:
                    word.total_count += 1
                    word.last_seen_round = self.current_round

    def get_visible_word_displays(self):
        visible_words = [w for w in self.words if w.visible]
        # 修复：打乱可见单词顺序，使显示位置随机变化
        random.shuffle(visible_words)
        # 额外：每个WordDisplay重新生成随机样式（确保位置/样式都变化）
        return [WordDisplay(word) for word in visible_words]

def main():
    st.set_page_config(page_title="A4纸背单词", layout="wide")
    app = VocabularyApp()

    # 顶部输入区域
    st.title("A4纸背单词")
    col1, col2, col3 = st.columns([4, 1, 1])
    
    # 修复：输入框逻辑（避免直接修改小部件绑定状态）
    with col1:
        # 方案：根据标记决定输入框初始值（实现清空效果）
        input_placeholder = "输入英文单词后按回车"
        initial_input_value = "" if st.session_state.need_clear_input else ""
        word_input = st.text_input(
            "输入新单词", 
            value=initial_input_value,
            placeholder=input_placeholder,
            label_visibility="collapsed",
            key="unique_word_input"  # 唯一key，不直接修改其值
        )
    
    with col2:
        add_btn = st.button("添加并刷新", type="primary")
    with col3:
        clear_btn_clicked = st.button("一键清除所有单词", type="secondary")
        # 自定义红色按钮样式
        st.markdown("""
            <style>
            div[data-testid="stButton"] > button:last-child {
                background-color: #d32f2f;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 0.5rem 1rem;
                width: 100%;
            }
            div[data-testid="stButton"] > button:last-child:hover {
                background-color: #b71c1c;
            }
            </style>
        """, unsafe_allow_html=True)

    # 1. 添加单词逻辑（修复输入框清空，无状态报错）
    if add_btn and word_input.strip():
        app.add_word(word_input.strip())
        # 标记需要清空输入框（下一次页面运行时生效，符合Streamlit规则）
        st.session_state.need_clear_input = True
        # 重置标记（避免后续输入框一直为空）
        st.experimental_rerun()  # 兼容新旧版本，替代st.rerun()
    
    # 重置清空标记（输入框已渲染后，取消下一次清空标记）
    if st.session_state.need_clear_input:
        st.session_state.need_clear_input = False

    # 2. 清除所有单词逻辑
    if clear_btn_clicked:
        app.clear_all_words()
        st.session_state.need_clear_input = True
        st.experimental_rerun()

    # 3. 手动刷新布局逻辑
    if st.button("手动刷新布局"):
        app.refresh_layout()
        st.experimental_rerun()

    # 统计信息
    total = len(app.words)
    visible = len([w for w in app.words if w.visible])
    hidden = total - visible
    st.caption(f"总单词数: {total} | 显示: {visible} | 隐藏: {hidden}")

    # 4. 单词显示区域（确保位置/样式随机变化）
    word_displays = app.get_visible_word_displays()
    if word_displays:
        cols = st.columns(5)
        for i, display in enumerate(word_displays):
            with cols[i % 5]:
                st.markdown(
                    f"""
                    <div style="
                        font-size: {display.size}px;
                        color: {display.color};
                        transform: rotate({display.rotation}deg);
                        margin: 20px;
                        text-align: center;
                        font-weight: bold;
                    ">
                        {display.word.text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    main()