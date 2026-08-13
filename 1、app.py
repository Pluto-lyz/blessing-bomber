import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="专属祝福轰炸机", page_icon="🎁", layout="centered")

# 66 条绝不重复的祝福语词库
unique_blessings = [
    "天天开心！😄", "暴富暴美！💰", "心想事成！✨", "好运连连！🍀", "永远十八岁！🎂",
    "平安喜乐！🍎", "万事胜意！🌟", "升职加薪！🚀", "无忧无虑！🎈", "发量惊人！💇‍♀️",
    "睡觉睡到自然醒！🛌", "数钱数到手抽筋！💵", "水逆退散！🛑", "锦鲤附体！🐟", "干饭不长胖！🍚",
    "每天都有好心情！🌻", "事业步步高升！📈", "出门必捡钱！💴", "抽卡必出金！🃏", "逢考必过！💯",
    "烦恼全消！💨", "桃花朵朵开！🌸", "百病不侵！🛡️", "一帆风顺！⛵", "二龙腾飞！🐉",
    "三羊开泰！🐐", "四季平安！🌈", "五福临门！🚪", "六六大顺！🎲", "七星高照！⭐",
    "八方来财！💎", "九九同心！💞", "十全十美！🏆", "生活甜如蜜！🍯", "前程似锦！🌅",
    "万事如意！🎊", "笑口常开！😁", "福如东海！🌊", "寿比南山！⛰️", "岁岁平安！🎆",
    "吉星高照！✨", "招财进宝！🪙", "金玉满堂！🕍", "喜上眉梢！😊", "大吉大利！🍊",
    "排位十连胜！🎮", "不脱发不失眠！🌙", "永远不缺钱！💳", "遇见的都是好人！🤝", "想吃的店都不排队！🍜",
    "快递永远提前到！📦", "手机永远有电！🔋", "WIFI永远满格！📶", "买瓜必甜！🍉", "吃泡面必有调料包！🍜",
    "永远不会踩到水坑！🌂", "挤地铁永远有座！💺", "上班摸鱼不被发现！🐟", "每天都能看到晚霞！🌇", "不用定闹钟！⏰",
    "所有期待都能如愿！🌠", "所有梦想都能成真！🎠", "好运正在派件！📮", "你就是最棒的！👍", "人间值得！🌍", "未来可期！🔭"
]

colors = ["#FFB6C1", "#87CEFA", "#98FB98", "#FFD700", "#FFA07A", "#E6E6FA", "#F08080", "#E0FFFF", "#FFC0CB", "#DDA0DD"]

st.title("💌 专属祝福轰炸机 (原味复刻版)")
st.write("请准备好，点击下方按钮体验网页版的**满屏弹窗轰炸**！支持手机和电脑。")

# 当点击按钮时
if st.button("🚀 点击接受轰炸！", use_container_width=True):
    # 将 Python 列表转为 JSON 字符串，方便传给 JavaScript
    blessings_js = json.dumps(unique_blessings)
    colors_js = json.dumps(colors)

    # 用前端魔法在 Streamlit 的整个网页上层动态生成弹窗
    html_code = f"""
    <script>
        // 获取最外层网页的 Document，突破 iframe 限制
        const parentDoc = window.parent.document;
        const parentWin = window.parent;

        const blessings = {blessings_js};
        const colors = {colors_js};

        // 随机打乱祝福语
        blessings.sort(() => Math.random() - 0.5);

        let count = 0;

        function spawnWindow() {{
            if (count >= blessings.length) return;

            // 1. 创建类似电脑窗口的 div 容器
            const win = parentDoc.createElement('div');
            win.className = 'blessing-popup-window'; // 标记一下，方便后面一键删除

            // 2. 模拟原生窗口的 CSS 样式
            win.style.position = 'fixed';
            win.style.width = '240px';
            win.style.height = '100px';

            // 随机分布在屏幕范围内
            const maxX = parentWin.innerWidth - 240;
            const maxY = parentWin.innerHeight - 100;
            const x = Math.max(0, Math.floor(Math.random() * maxX));
            const y = Math.max(0, Math.floor(Math.random() * maxY));
            win.style.left = x + 'px';
            win.style.top = y + 'px';

            // 外观装饰
            win.style.border = '1px solid #a0a0a0';
            win.style.borderRadius = '6px';
            win.style.boxShadow = '2px 4px 12px rgba(0,0,0,0.3)';
            win.style.zIndex = 99999 + count; // 保证新弹出的在最上面
            win.style.display = 'flex';
            win.style.flexDirection = 'column';
            win.style.overflow = 'hidden';
            win.style.transform = 'scale(0.8)';
            win.style.opacity = '0';
            win.style.transition = 'all 0.1s ease-out';

            // 3. 模拟窗口标题栏
            const header = parentDoc.createElement('div');
            header.style.backgroundColor = '#f0f0f0';
            header.style.padding = '4px 8px';
            header.style.fontSize = '12px';
            header.style.color = '#333';
            header.style.borderBottom = '1px solid #ccc';
            header.innerHTML = '💌 收到一条祝福';

            // 4. 模拟窗口内容区
            const body = parentDoc.createElement('div');
            body.style.flex = '1';
            body.style.display = 'flex';
            body.style.alignItems = 'center';
            body.style.justifyContent = 'center';
            body.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            body.style.fontWeight = 'bold';
            body.style.fontSize = '14px';
            body.style.color = '#333';
            body.innerHTML = blessings[count];

            // 拼装并添加到网页主体
            win.appendChild(header);
            win.appendChild(body);
            parentDoc.body.appendChild(win);

            // 弹簧动画效果
            setTimeout(() => {{
                win.style.transform = 'scale(1)';
                win.style.opacity = '1';
            }}, 10);

            count++;

            // 40毫秒后生成下一个，和原来的 root.after(40) 一模一样
            setTimeout(spawnWindow, 40);
        }}

        // 开始轰炸
        spawnWindow();

        // 6秒后（6000毫秒），瞬间关闭所有窗口，和 root.after(6000, root.destroy) 逻辑一致
        setTimeout(() => {{
            const elements = parentDoc.querySelectorAll('.blessing-popup-window');
            elements.forEach(el => el.remove());
        }}, 6000 + (blessings.length * 40)); 
        // 加上生成所需的时间，确保是全屏弹完之后再等 6 秒

    </script>
    """

    # 渲染这段隐藏的 HTML 代码来执行 JavaScript
    components.html(html_code, height=0)

    st.success("准备接受轰炸！请看屏幕四周...")