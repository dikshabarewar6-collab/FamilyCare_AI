"""
Interactive 3D Three.js Component for FamilyCare AI Landing Page.
Embeds a genuine Three.js WebGL scene with floating 3D care objects,
interactive orbit controls, and an accessible SVG fallback if WebGL is unavailable.
"""
import streamlit.components.v1 as components

def render_3d_care_scene(height: int = 420):
    """
    Renders an interactive 3D WebGL scene using Three.js with:
    - Orbiting family care connection rings (connecting Chicago, New York, Seattle)
    - 3D Floating Capsule Pill (Lavender / Teal)
    - 3D Beating Heart Mesh with faceted geometry
    - 3D Shield / Home Mesh
    - Particle constellation
    - Mouse movement parallax & drag-to-rotate
    - Accessible SVG/Canvas fallback if WebGL is unsupported
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <style>
        body, html {{
          margin: 0;
          padding: 0;
          width: 100%;
          height: 100%;
          overflow: hidden;
          background: transparent;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        #canvas-container {{
          width: 100%;
          height: {height}px;
          position: relative;
          background: radial-gradient(circle at 50% 50%, rgba(243, 240, 253, 0.7) 0%, rgba(230, 255, 250, 0.4) 60%, transparent 100%);
          border-radius: 20px;
          overflow: hidden;
          box-shadow: inset 0 0 40px rgba(112, 82, 230, 0.05);
        }}
        #three-canvas {{
          width: 100%;
          height: 100%;
          display: block;
          cursor: grab;
        }}
        #three-canvas:active {{
          cursor: grabbing;
        }}
        .hud-badge {{
          position: absolute;
          bottom: 12px;
          left: 16px;
          background: rgba(255, 255, 255, 0.85);
          backdrop-filter: blur(8px);
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 11px;
          color: #7052E6;
          font-weight: 600;
          border: 1px solid rgba(155, 134, 238, 0.3);
          pointer-events: none;
          display: flex;
          align-items: center;
          gap: 6px;
        }}
        .hud-city {{
          position: absolute;
          font-size: 11px;
          font-weight: 700;
          color: #0F172A;
          background: rgba(255, 255, 255, 0.9);
          border: 1px solid rgba(13, 148, 136, 0.3);
          padding: 2px 8px;
          border-radius: 8px;
          pointer-events: none;
          box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        }}
        #fallback-scene {{
          display: none;
          width: 100%;
          height: 100%;
          align-items: center;
          justify-content: center;
          text-align: center;
        }}
      </style>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    </head>
    <body>
      <div id="canvas-container">
        <canvas id="three-canvas"></canvas>
        <div class="hud-badge">
          <span>🌐</span> Real-Time 3D Care Orbit • Drag to Rotate
        </div>
        <div id="fallback-scene">
          <svg width="100%" height="{height}" viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#9B86EE;stop-opacity:0.8" />
                <stop offset="100%" style="stop-color:#2DD4BF;stop-opacity:0.8" />
              </linearGradient>
            </defs>
            <circle cx="300" cy="200" r="140" fill="none" stroke="rgba(155,134,238,0.3)" stroke-width="2" stroke-dasharray="6,6"/>
            <circle cx="300" cy="200" r="80" fill="none" stroke="rgba(45,212,191,0.4)" stroke-width="2"/>
            <circle cx="300" cy="200" r="32" fill="url(#grad1)"/>
            <text x="300" y="206" text-anchor="middle" fill="#fff" font-size="20">❤️</text>
            <circle cx="180" cy="150" r="18" fill="#7052E6"/>
            <text x="180" y="155" text-anchor="middle" fill="#fff" font-size="12">NYC</text>
            <circle cx="420" cy="160" r="18" fill="#0D9488"/>
            <text x="420" y="165" text-anchor="middle" fill="#fff" font-size="12">SEA</text>
            <circle cx="300" cy="330" r="22" fill="#0284C7"/>
            <text x="300" y="336" text-anchor="middle" fill="#fff" font-size="13">CHI</text>
          </svg>
        </div>
      </div>

      <script>
        (function() {
          const container = document.getElementById('canvas-container');
          const canvas = document.getElementById('three-canvas');
          const fallback = document.getElementById('fallback-scene');

          // Check WebGL availability
          function isWebGLAvailable() {
            try {
              const testCanvas = document.createElement('canvas');
              return !!(window.WebGLRenderingContext && 
                (testCanvas.getContext('webgl') || testCanvas.getContext('experimental-webgl')));
            } catch (e) {
              return false;
            }
          }

          if (!window.THREE || !isWebGLAvailable()) {
            canvas.style.display = 'none';
            fallback.style.display = 'flex';
            return;
          }

          const width = container.clientWidth || 600;
          const height = container.clientHeight || {height};

          // 1. Scene, Camera, Renderer
          const scene = new THREE.Scene();
          const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
          camera.position.set(0, 5, 24);

          const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
          renderer.setSize(width, height);
          renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

          // 2. Lights
          const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
          scene.add(ambientLight);

          const dirLight1 = new THREE.DirectionalLight(0x9B86EE, 1.2);
          dirLight1.position.set(10, 20, 15);
          scene.add(dirLight1);

          const dirLight2 = new THREE.DirectionalLight(0x2DD4BF, 0.9);
          dirLight2.position.set(-15, -10, -10);
          scene.add(dirLight2);

          const pointLight = new THREE.PointLight(0x38BDF8, 1.5, 30);
          pointLight.position.set(0, 0, 8);
          scene.add(pointLight);

          // 3. Central Anchor: Faceted Care Shield / Heart Orb
          const coreGroup = new THREE.Group();
          scene.add(coreGroup);

          const heartGeo = new THREE.IcosahedronGeometry(2.5, 2);
          const heartMat = new THREE.MeshPhongMaterial({
            color: 0x7052E6,
            emissive: 0x2A1054,
            shininess: 90,
            wireframe: false,
            flatShading: true,
            transparent: true,
            opacity: 0.92
          });
          const heartMesh = new THREE.Mesh(heartGeo, heartMat);
          coreGroup.add(heartMesh);

          // Glowing Wireframe Outer Halo
          const haloGeo = new THREE.IcosahedronGeometry(3.2, 1);
          const haloMat = new THREE.MeshBasicMaterial({
            color: 0x2DD4BF,
            wireframe: true,
            transparent: true,
            opacity: 0.35
          });
          const haloMesh = new THREE.Mesh(haloGeo, haloMat);
          coreGroup.add(haloMesh);

          // 4. Orbital Rings (Family Connection Rings)
          const ringGroup = new THREE.Group();
          scene.add(ringGroup);

          const ringGeo1 = new THREE.TorusGeometry(8.5, 0.08, 16, 100);
          const ringMat1 = new THREE.MeshBasicMaterial({ color: 0x9B86EE, transparent: true, opacity: 0.65 });
          const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
          ring1.rotation.x = Math.PI / 3;
          ringGroup.add(ring1);

          const ringGeo2 = new THREE.TorusGeometry(11.5, 0.08, 16, 100);
          const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x2DD4BF, transparent: true, opacity: 0.5 });
          const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
          ring2.rotation.y = Math.PI / 4;
          ring2.rotation.x = -Math.PI / 5;
          ringGroup.add(ring2);

          // 5. Floating 3D Care Objects
          // Object A: 3D Capsule Pill (Half Purple, Half Teal)
          const pillGroup = new THREE.Group();
          const pillBodyGeo = new THREE.CylinderGeometry(0.7, 0.7, 1.6, 24);
          const pillBodyMat1 = new THREE.MeshPhongMaterial({ color: 0x7052E6, shininess: 80 });
          const pillCyl = new THREE.Mesh(pillBodyGeo, pillBodyMat1);

          const pillCapGeo1 = new THREE.SphereGeometry(0.7, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2);
          const pillCapMat1 = new THREE.MeshPhongMaterial({ color: 0x7052E6, shininess: 80 });
          const cap1 = new THREE.Mesh(pillCapGeo1, pillCapMat1);
          cap1.position.y = 0.8;

          const pillCapGeo2 = new THREE.SphereGeometry(0.7, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2);
          const pillCapMat2 = new THREE.MeshPhongMaterial({ color: 0x2DD4BF, shininess: 80 });
          const cap2 = new THREE.Mesh(pillCapGeo2, pillCapMat2);
          cap2.position.y = -0.8;
          cap2.rotation.x = Math.PI;

          pillGroup.add(pillCyl);
          pillGroup.add(cap1);
          pillGroup.add(cap2);
          pillGroup.position.set(-7, 3, 2);
          pillGroup.rotation.z = 0.5;
          scene.add(pillGroup);

          // Object B: Family Nodes (Chicago, New York, Seattle)
          const nodeGeo = new THREE.SphereGeometry(0.9, 20, 20);
          
          // Chicago (Grandparent Home Node)
          const matChi = new THREE.MeshPhongMaterial({ color: 0xF59E0B, shininess: 100 });
          const nodeChi = new THREE.Mesh(nodeGeo, matChi);
          nodeChi.position.set(0, -6.5, 3.5);
          scene.add(nodeChi);

          // New York (Caregiver Daughter Node)
          const matNYC = new THREE.MeshPhongMaterial({ color: 0x0284C7, shininess: 100 });
          const nodeNYC = new THREE.Mesh(nodeGeo, matNYC);
          nodeNYC.position.set(6.8, 4.2, -2);
          scene.add(nodeNYC);

          // Seattle (Caregiver Son Node)
          const matSEA = new THREE.MeshPhongMaterial({ color: 0x10B981, shininess: 100 });
          const nodeSEA = new THREE.Mesh(nodeGeo, matSEA);
          nodeSEA.position.set(-8.2, -2.5, -3);
          scene.add(nodeSEA);

          // 6. Floating Ambient Particle Field
          const particleCount = 120;
          const particleGeo = new THREE.BufferGeometry();
          const particlePositions = new Float32Array(particleCount * 3);
          for (let i = 0; i < particleCount * 3; i += 3) {
            particlePositions[i] = (Math.random() - 0.5) * 45;
            particlePositions[i + 1] = (Math.random() - 0.5) * 35;
            particlePositions[i + 2] = (Math.random() - 0.5) * 30;
          }
          particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
          const particleMat = new THREE.PointsMaterial({
            color: 0x9B86EE,
            size: 0.35,
            transparent: true,
            opacity: 0.65
          });
          const particles = new THREE.Points(particleGeo, particleMat);
          scene.add(particles);

          // 7. Interactive Mouse / Drag Controls
          let isDragging = false;
          let prevMouseX = 0;
          let prevMouseY = 0;
          let targetRotX = 0;
          let targetRotY = 0;

          canvas.addEventListener('mousedown', (e) => {
            isDragging = true;
            prevMouseX = e.clientX;
            prevMouseY = e.clientY;
          });

          window.addEventListener('mouseup', () => {
            isDragging = false;
          });

          window.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            if (isDragging) {
              const deltaX = e.clientX - prevMouseX;
              const deltaY = e.clientY - prevMouseY;
              targetRotY += deltaX * 0.008;
              targetRotX += deltaY * 0.008;
              prevMouseX = e.clientX;
              prevMouseY = e.clientY;
            } else if (mouseX >= 0 && mouseX <= width && mouseY >= 0 && mouseY <= height) {
              // Subtle parallax tilt
              const normX = (mouseX / width - 0.5) * 2;
              const normY = (mouseY / height - 0.5) * 2;
              camera.position.x += (normX * 3 - camera.position.x) * 0.05;
              camera.position.y += (-normY * 2 + 5 - camera.position.y) * 0.05;
              camera.lookAt(0, 0, 0);
            }
          });

          // Resize handler
          window.addEventListener('resize', () => {
            const newW = container.clientWidth || 600;
            camera.aspect = newW / height;
            camera.updateProjectionMatrix();
            renderer.setSize(newW, height);
          });

          // 8. Animation Loop
          let clock = new THREE.Clock();

          function animate() {
            requestAnimationFrame(animate);
            const t = clock.getElapsedTime();

            // Smooth rotation damping
            coreGroup.rotation.y += (targetRotY - coreGroup.rotation.y) * 0.06;
            coreGroup.rotation.x += (targetRotX - coreGroup.rotation.x) * 0.06;
            ringGroup.rotation.y += 0.004;
            ringGroup.rotation.z += 0.002;

            // Heart gentle pulse
            const pulse = 1 + 0.06 * Math.sin(t * 3.2);
            heartMesh.scale.set(pulse, pulse, pulse);
            haloMesh.rotation.y -= 0.008;
            haloMesh.rotation.x += 0.005;

            // Pill floating & tumbling
            pillGroup.position.y = 3 + Math.sin(t * 1.8) * 0.6;
            pillGroup.rotation.x += 0.012;
            pillGroup.rotation.y += 0.018;

            // Orbiting nodes bobbing
            nodeChi.position.y = -6.5 + Math.sin(t * 1.5) * 0.4;
            nodeNYC.position.y = 4.2 + Math.cos(t * 1.6) * 0.4;
            nodeSEA.position.y = -2.5 + Math.sin(t * 1.4 + 1) * 0.4;

            // Ambient particles gentle drift
            particles.rotation.y = t * 0.02;

            renderer.render(scene, camera);
          }

          animate();
        })();
      </script>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=False)
