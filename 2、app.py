import streamlit as st
import streamlit.components.v1 as components

# 设置页面为全屏沉浸模式
st.set_page_config(page_title="吃货烟花模拟器 🍔", layout="wide")

# 注入 CSS 隐藏 Streamlit 自带的边距、页眉和页脚，实现真正的全屏
st.markdown("""
    <style>
        .block-container { padding: 0 !important; max-width: 100% !important; }
        header { display: none !important; }
        footer { display: none !important; }
        iframe { width: 100vw; height: 100vh; border: none; display: block; }
        body { margin: 0; overflow: hidden; background-color: black; }
    </style>
""", unsafe_allow_html=True)

# 核心代码：将 Pygame 的图形和物理逻辑转化为 HTML5 Canvas + JavaScript
html_code = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: black; overflow: hidden; }
        canvas { display: block; width: 100%; height: 100%; }
        #hint { position: absolute; top: 50%; width: 100%; text-align: center; color: rgba(255,255,255,0.7); font-family: sans-serif; font-size: 20px; pointer-events: none; transition: opacity 1s; }
    </style>
</head>
<body>
    <div id="hint">👆 点击或触摸屏幕发射烟花！</div>
    <canvas id="gameCanvas"></canvas>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        let width, height;

        function resize() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resize);
        resize();

        // 1. 纯代码“画”出食物和小动物 (对应原始 Pygame 代码)
        function createOffscreen(drawFn) {
            const c = document.createElement('canvas');
            c.width = 30; c.height = 30;
            const cx = c.getContext('2d');
            drawFn(cx);
            return c;
        }

        const burgerImg = createOffscreen(cx => {
            // 顶层面包
            cx.fillStyle = 'rgb(230,150,50)';
            cx.beginPath(); cx.ellipse(14, 8, 12, 5, 0, 0, Math.PI * 2); cx.fill();
            // 绿色生菜
            cx.fillStyle = 'rgb(50,200,50)'; cx.fillRect(0, 12, 30, 4);
            // 烤肉饼
            cx.fillStyle = 'rgb(100,50,20)'; cx.fillRect(2, 16, 26, 6);
            // 底层面包
            cx.fillStyle = 'rgb(230,150,50)';
            cx.beginPath(); cx.ellipse(13, 24, 11, 4, 0, 0, Math.PI * 2); cx.fill();
        });

        const watermelonImg = createOffscreen(cx => {
            // 绿皮 (只画下半圆)
            cx.fillStyle = 'rgb(30,200,50)';
            cx.beginPath(); cx.arc(15, 15, 15, 0, Math.PI, false); cx.fill();
            // 红瓤
            cx.fillStyle = 'rgb(255,50,50)';
            cx.beginPath(); cx.arc(15, 15, 12, 0, Math.PI, false); cx.fill();
            // 西瓜子
            cx.fillStyle = 'black';
            [ [10,20], [20,20], [15,24] ].forEach(pos => {
                cx.beginPath(); cx.arc(pos[0], pos[1], 2, 0, Math.PI * 2); cx.fill();
            });
        });

        const pigImg = createOffscreen(cx => {
            // 左耳 & 右耳
            cx.fillStyle = 'rgb(255,150,180)';
            cx.beginPath(); cx.moveTo(4,8); cx.lineTo(10,2); cx.lineTo(14,8); cx.fill();
            cx.beginPath(); cx.moveTo(26,8); cx.lineTo(20,2); cx.lineTo(16,8); cx.fill();
            // 粉色脑袋
            cx.fillStyle = 'rgb(255,180,200)';
            cx.beginPath(); cx.arc(15, 15, 12, 0, Math.PI * 2); cx.fill();
            // 猪鼻子
            cx.fillStyle = 'rgb(255,100,150)';
            cx.beginPath(); cx.ellipse(15, 19, 5, 3, 0, 0, Math.PI * 2); cx.fill();
            // 鼻孔 & 眼睛
            cx.fillStyle = 'rgb(50,0,0)';
            cx.beginPath(); cx.arc(13, 19, 1, 0, Math.PI * 2); cx.fill();
            cx.beginPath(); cx.arc(17, 19, 1, 0, Math.PI * 2); cx.fill();
            cx.fillStyle = 'black';
            cx.beginPath(); cx.arc(10, 12, 2, 0, Math.PI * 2); cx.fill();
            cx.beginPath(); cx.arc(20, 12, 2, 0, Math.PI * 2); cx.fill();
        });

        const eggImg = createOffscreen(cx => {
            cx.fillStyle = 'white';
            cx.beginPath(); cx.ellipse(15, 17, 12, 9, 0, 0, Math.PI * 2); cx.fill();
            cx.beginPath(); cx.ellipse(15, 14, 6, 11, 0, 0, Math.PI * 2); cx.fill();
            cx.fillStyle = 'rgb(255,200,0)';
            cx.beginPath(); cx.arc(15, 15, 7, 0, Math.PI * 2); cx.fill();
        });

        const SPRITES = [burgerImg, watermelonImg, pigImg, eggImg];

        // 状态数组
        let rockets = [];
        let normalSparks = [];
        let foodSprites = [];

        // 交互逻辑：发射导弹
        function launchRocket(tx, ty) {
            document.getElementById('hint').style.opacity = '0';
            rockets.push({
                x: tx + (Math.random() * 40 - 20),
                y: height,
                vx: 0,
                vy: (ty - height) * 0.04,
                targetY: ty
            });
        }

        // 核心大爆炸
        function explode(x, y) {
            const colors = ['rgb(255,100,100)', 'rgb(100,255,100)', 'rgb(100,150,255)', 'rgb(255,255,100)'];
            const color = colors[Math.floor(Math.random() * colors.length)];

            // 80个光点火花
            for (let i = 0; i < 80; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 10 + 2;
                normalSparks.push({
                    x: x, y: y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    color: color,
                    life: Math.floor(Math.random() * 30 + 30)
                });
            }

            // 25个四处飞散的食物/小动物
            for (let i = 0; i < 25; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = Math.random() * 12 + 3;
                foodSprites.push({
                    x: x, y: y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    img: SPRITES[Math.floor(Math.random() * SPRITES.length)],
                    angle: 0,
                    spin: Math.random() * 30 - 15,
                    life: 80
                });
            }
        }

        // 主循环
        function loop() {
            // 透明黑色图层，产生运动残影 (对应 Pygame 的 overlay)
            ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
            ctx.fillRect(0, 0, width, height);

            // 处理火箭
            for (let i = rockets.length - 1; i >= 0; i--) {
                let r = rockets[i];
                r.x += r.vx;
                r.y += r.vy;

                ctx.strokeStyle = 'rgb(255, 200, 50)';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.moveTo(r.x, r.y);
                ctx.lineTo(r.x, r.y + 20);
                ctx.stroke();

                if (r.y <= r.targetY) {
                    explode(r.x, r.y);
                    rockets.splice(i, 1);
                }
            }

            // 处理普通火花
            for (let i = normalSparks.length - 1; i >= 0; i--) {
                let p = normalSparks[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vx *= 0.95;
                p.vy *= 0.95;
                p.vy += 0.2; // 重力
                p.life -= 1;

                if (p.life <= 0) {
                    normalSparks.splice(i, 1);
                } else {
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, Math.floor(p.life / 10) + 1, 0, Math.PI * 2);
                    ctx.fill();
                }
            }

            // 处理食物和动物
            for (let i = foodSprites.length - 1; i >= 0; i--) {
                let f = foodSprites[i];
                f.x += f.vx;
                f.y += f.vy;
                f.vx *= 0.98; // 空气阻力
                f.vy *= 0.98;
                f.vy += 0.4; // 重力掉落更快
                f.angle += f.spin;
                f.life -= 1;

                if (f.life <= 0 || f.y > height + 50) {
                    foodSprites.splice(i, 1);
                } else {
                    // 根据生命值逐渐变小
                    let scale = Math.max(0.1, f.life / 80);

                    ctx.save();
                    ctx.translate(f.x, f.y);
                    ctx.rotate(f.angle * Math.PI / 180);
                    ctx.scale(scale, scale);
                    // 将图像居中绘制 (-15, -15 是因为画布大小是30x30)
                    ctx.drawImage(f.img, -15, -15);
                    ctx.restore();
                }
            }

            requestAnimationFrame(loop);
        }

        // 监听鼠标和触摸事件
        function handleInteraction(e) {
            let tx, ty;
            if (e.type === 'touchstart') {
                tx = e.touches[0].clientX;
                ty = e.touches[0].clientY;
            } else {
                tx = e.clientX;
                ty = e.clientY;
            }
            launchRocket(tx, ty);
        }

        window.addEventListener('mousedown', handleInteraction);
        window.addEventListener('touchstart', handleInteraction, {passive: true});

        loop();
    </script>
</body>
</html>
"""

# 使用 components 嵌入 HTML，并设置高度填满整个屏幕
components.html(html_code, height=1000, scrolling=False)