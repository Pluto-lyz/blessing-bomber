import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# 开启全屏沉浸模式
st.set_page_config(page_title="全息微光玫瑰", layout="wide")

st.markdown("""
    <style>
        .block-container { padding: 0 !important; max-width: 100% !important; }
        header { display: none !important; }
        footer { display: none !important; }
        iframe { width: 100vw; height: 100vh; border: none; display: block; }
        body { margin: 0; overflow: hidden; background-color: transparent; }
    </style>
""", unsafe_allow_html=True)

MODEL_PATH = "rose.glb"

if not os.path.exists(MODEL_PATH):
    st.error(f"❌ 启动失败：找不到模型文件 '{MODEL_PATH}'。请确保该文件已上传并与 app.py 放在同一目录下！")
else:
    # 核心魔法：将本地 GLB 模型转化为 Base64 字符串，突破网页端本地文件读取限制
    with open(MODEL_PATH, "rb") as f:
        glb_base64 = base64.b64encode(f.read()).decode("utf-8")

    # 注入 Three.js (WebGL) 前端 3D 引擎代码
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {{ margin: 0; overflow: hidden; background-color: #050505; }}
            canvas {{ display: block; width: 100vw; height: 100vh; }}
            #loading {{ position: absolute; top: 50%; width: 100%; text-align: center; color: rgba(255,255,255,0.8); font-family: sans-serif; pointer-events: none; }}
        </style>
        <!-- 引入 Three.js 核心库 -->
        <script async src="https://unpkg.com/es-module-shims@1.8.0/dist/es-module-shims.js"></script>
        <script type="importmap">
          {{
            "imports": {{
              "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
              "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
            }}
          }}
        </script>
    </head>
    <body>
        <div id="loading">正在解算高密度粒子模型...</div>

        <script type="module">
            import * as THREE from 'three';
            import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
            import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';

            // 1. 初始化场景与全息画布 (对应 vispy 的 SceneCanvas)
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(0, 0, 3.5);

            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            document.body.appendChild(renderer.domElement);

            const controls = new OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.autoRotate = true;
            controls.autoRotateSpeed = 2.0;

            let time_t = 0;
            let smokeParticles, sparkleParticles;

            // 2. 解析由 Python 传来的 Base64 模型数据
            const glbDataUrl = "data:model/gltf-binary;base64,{glb_base64}";
            const loader = new GLTFLoader();

            loader.load(glbDataUrl, function (gltf) {{
                document.getElementById('loading').style.display = 'none';

                let pointsGeometry = new THREE.BufferGeometry();
                let positions = [];
                let colors = [];

                // 提取模型顶点并应用基于高度的 Y 轴颜色渐变引擎
                gltf.scene.traverse(function (child) {{
                    if (child.isMesh) {{
                        const posAttr = child.geometry.attributes.position;
                        for(let i = 0; i < posAttr.count; i++) {{
                            positions.push(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i));
                        }}
                    }}
                }});

                // 计算边界用于颜色归一化
                let minY = Infinity, maxY = -Infinity;
                for(let i = 1; i < positions.length; i+=3) {{
                    if(positions[i] < minY) minY = positions[i];
                    if(positions[i] > maxY) maxY = positions[i];
                }}

                // 核心高度映射函数：重现 Python 的 get_color_from_y
                for(let i = 0; i < positions.length; i+=3) {{
                    const y_n = Math.max(0, Math.min(1, (positions[i+1] - minY) / (maxY - minY)));
                    const r = (1.0 - y_n) * 0.3 + y_n * 1.0;
                    const g = (1.0 - y_n) * 1.0 + y_n * 0.3;
                    const b = 1.0;
                    colors.push(r, g, b);
                }}

                pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                pointsGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

                // 创建玫瑰主体层
                const bodyMaterial = new THREE.PointsMaterial({{
                    size: 0.015, vertexColors: true, transparent: true, opacity: 0.8,
                    blending: THREE.AdditiveBlending, depthWrite: false
                }});
                const roseBody = new THREE.Points(pointsGeometry, bodyMaterial);

                // 调整姿态：中心化与侧放 (对应 Python 的 MatrixTransform)
                roseBody.geometry.center();
                roseBody.rotation.x = -Math.PI / 2;
                scene.add(roseBody);

                // 3. 初始化灵动微光星火层 (1500 个粒子)
                const sparkleGeom = new THREE.BufferGeometry();
                const sparklePos = [];
                for(let i=0; i<1500; i++) {{
                    sparklePos.push((Math.random()-0.5)*3.6, (Math.random()-0.5)*3.6, (Math.random()-0.5)*3.6);
                }}
                sparkleGeom.setAttribute('position', new THREE.Float32BufferAttribute(sparklePos, 3));
                const sparkleMat = new THREE.PointsMaterial({{
                    size: 0.02, color: 0xcceeff, transparent: true, opacity: 0.6,
                    blending: THREE.AdditiveBlending, depthWrite: false
                }});
                sparkleParticles = new THREE.Points(sparkleGeom, sparkleMat);
                scene.add(sparkleParticles);

                // 开始动画循环
                animate();
            }});

            // 4. 动画循环 (对应 Python 的 update 函数)
            function animate() {{
                requestAnimationFrame(animate);
                time_t += 0.03;

                // 星火闪烁与缓慢漂浮逻辑
                if (sparkleParticles) {{
                    const positions = sparkleParticles.geometry.attributes.position.array;
                    for(let i=0; i<positions.length; i+=3) {{
                        positions[i+1] += 0.002 * Math.sin(time_t + i); // Y轴漂浮
                    }}
                    sparkleParticles.geometry.attributes.position.needsUpdate = true;
                    // 正弦波透明度闪烁
                    sparkleParticles.material.opacity = 0.2 + 0.4 * Math.sin(time_t * 3.0);
                }}

                controls.update();
                renderer.render(scene, camera);
            }}

            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=1000, scrolling=False)