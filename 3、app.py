import streamlit as st
import streamlit.components.v1 as components

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

# 已经为你填好了专属云端直链
MODEL_URL = "https://github.com/Pluto-lyz/blessing-bomber/releases/download/v1.0/rose.glb"

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
    <div id="loading">正在通过云端加载 3D 玫瑰模型...</div>

    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
        import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';

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
        let sparkleParticles;

        const loader = new GLTFLoader();
        const modelUrl = "{MODEL_URL}";

        loader.load(modelUrl, function (gltf) {{
            document.getElementById('loading').style.display = 'none';

            let pointsGeometry = new THREE.BufferGeometry();
            let positions = [];
            let colors = [];

            gltf.scene.traverse(function (child) {{
                if (child.isMesh) {{
                    const posAttr = child.geometry.attributes.position;
                    for(let i = 0; i < posAttr.count; i++) {{
                        positions.push(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i));
                    }}
                }}
            }});

            let minY = Infinity, maxY = -Infinity;
            for(let i = 1; i < positions.length; i+=3) {{
                if(positions[i] < minY) minY = positions[i];
                if(positions[i] > maxY) maxY = positions[i];
            }}

            for(let i = 0; i < positions.length; i+=3) {{
                const y_n = Math.max(0, Math.min(1, (positions[i+1] - minY) / (maxY - minY)));
                const r = (1.0 - y_n) * 0.3 + y_n * 1.0;
                const g = (1.0 - y_n) * 1.0 + y_n * 0.3;
                const b = 1.0;
                colors.push(r, g, b);
            }}

            pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            pointsGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

            const bodyMaterial = new THREE.PointsMaterial({{
                size: 0.015, vertexColors: true, transparent: true, opacity: 0.8,
                blending: THREE.AdditiveBlending, depthWrite: false
            }});
            const roseBody = new THREE.Points(pointsGeometry, bodyMaterial);

            roseBody.geometry.center();
            roseBody.rotation.x = -Math.PI / 2;
            scene.add(roseBody);

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

            animate();
        }}, undefined, function(error) {{
            document.getElementById('loading').innerText = "模型加载失败，请检查外链是否正确";
            console.error(error);
        }});

        function animate() {{
            requestAnimationFrame(animate);
            time_t += 0.03;

            if (sparkleParticles) {{
                const positions = sparkleParticles.geometry.attributes.position.array;
                for(let i=0; i<positions.length; i+=3) {{
                    positions[i+1] += 0.002 * Math.sin(time_t + i);
                }}
                sparkleParticles.geometry.attributes.position.needsUpdate = true;
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