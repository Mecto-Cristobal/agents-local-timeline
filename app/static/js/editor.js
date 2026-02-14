import * as THREE from "https://unpkg.com/three@0.159.0/build/three.module.js";
import { OrbitControls } from "https://unpkg.com/three@0.159.0/examples/jsm/controls/OrbitControls.js";
import { TransformControls } from "https://unpkg.com/three@0.159.0/examples/jsm/controls/TransformControls.js";

const container = document.getElementById("editor-canvas");
const statusEl = document.getElementById("editor-status");
const nameInput = document.getElementById("scene-name");
const saveBtn = document.getElementById("scene-save");
const loadBtn = document.getElementById("scene-load");
const sceneList = document.getElementById("scene-list");
const deleteBtn = document.getElementById("delete-object");

if (!container) {
  throw new Error("Missing editor container");
}

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b0f16);

const camera = new THREE.PerspectiveCamera(
  60,
  container.clientWidth / container.clientHeight,
  0.1,
  1000
);
camera.position.set(6, 6, 8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

const orbit = new OrbitControls(camera, renderer.domElement);
orbit.enableDamping = true;

const transform = new TransformControls(camera, renderer.domElement);
transform.setSpace("world");
scene.add(transform);

const grid = new THREE.GridHelper(20, 20, 0x444c5c, 0x222832);
scene.add(grid);

const hemi = new THREE.HemisphereLight(0xffffff, 0x222833, 1.0);
scene.add(hemi);

const dir = new THREE.DirectionalLight(0xffffff, 0.6);
dir.position.set(5, 10, 7);
scene.add(dir);

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let selected = null;
let currentSceneId = null;

const animate = () => {
  requestAnimationFrame(animate);
  orbit.update();
  renderer.render(scene, camera);
};

const resize = () => {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
};
window.addEventListener("resize", resize);

const selectObject = (obj) => {
  selected = obj;
  transform.detach();
  if (obj) {
    transform.attach(obj);
  }
};

const createPrimitive = (type) => {
  let geometry;
  switch (type) {
    case "sphere":
      geometry = new THREE.SphereGeometry(0.7, 32, 24);
      break;
    case "cone":
      geometry = new THREE.ConeGeometry(0.6, 1.2, 24);
      break;
    default:
      geometry = new THREE.BoxGeometry(1, 1, 1);
  }
  const material = new THREE.MeshStandardMaterial({ color: 0x5bbcff });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(Math.random() * 2, 0.5, Math.random() * 2);
  scene.add(mesh);
  selectObject(mesh);
};

const serializeScene = () => {
  const objects = [];
  scene.traverse((obj) => {
    if (obj.isMesh && obj !== grid) {
      objects.push({
        type: obj.geometry.type,
        position: obj.position.toArray(),
        rotation: obj.rotation.toArray(),
        scale: obj.scale.toArray(),
        color: obj.material.color.getHex(),
      });
    }
  });
  return JSON.stringify({ objects }, null, 2);
};

const loadSceneFromJson = (json) => {
  let parsed = {};
  try {
    parsed = JSON.parse(json);
  } catch {
    parsed = {};
  }
  const keep = new Set([grid, transform, hemi, dir]);
  scene.children
    .filter((child) => child.isMesh && !keep.has(child))
    .forEach((child) => scene.remove(child));
  (parsed.objects || []).forEach((obj) => {
    let geometry;
    if (obj.type === "SphereGeometry") {
      geometry = new THREE.SphereGeometry(0.7, 32, 24);
    } else if (obj.type === "ConeGeometry") {
      geometry = new THREE.ConeGeometry(0.6, 1.2, 24);
    } else {
      geometry = new THREE.BoxGeometry(1, 1, 1);
    }
    const material = new THREE.MeshStandardMaterial({ color: obj.color || 0x5bbcff });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.fromArray(obj.position || [0, 0, 0]);
    mesh.rotation.fromArray(obj.rotation || [0, 0, 0]);
    mesh.scale.fromArray(obj.scale || [1, 1, 1]);
    scene.add(mesh);
  });
  selectObject(null);
};

const refreshSceneList = async () => {
  const res = await fetch("/api/agents/scenes");
  if (!res.ok) return;
  const scenes = await res.json();
  sceneList.innerHTML = scenes
    .map((scene) => `<option value="${scene.id}">${scene.name}</option>`)
    .join("");
};

container.addEventListener("pointerdown", (event) => {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const meshes = [];
  scene.traverse((obj) => {
    if (obj.isMesh && obj !== grid) meshes.push(obj);
  });
  const intersects = raycaster.intersectObjects(meshes);
  selectObject(intersects.length ? intersects[0].object : null);
});

transform.addEventListener("dragging-changed", (event) => {
  orbit.enabled = !event.value;
});

Array.from(document.querySelectorAll("[data-primitive]")).forEach((btn) => {
  btn.addEventListener("click", () => createPrimitive(btn.dataset.primitive));
});

saveBtn?.addEventListener("click", async () => {
  const name = nameInput.value.trim() || "Untitled";
  const payload = { name, scene_json: serializeScene() };
  const url = currentSceneId
    ? `/api/agents/scenes/${currentSceneId}`
    : "/api/agents/scenes";
  const method = currentSceneId ? "PUT" : "POST";
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (res.ok) {
    const data = await res.json();
    currentSceneId = data.id;
    statusEl.textContent = `Saved ${data.name}`;
    await refreshSceneList();
  } else {
    statusEl.textContent = "Save failed";
  }
});

loadBtn?.addEventListener("click", async () => {
  const id = sceneList.value;
  if (!id) return;
  const res = await fetch(`/api/agents/scenes?account_id=`);
  if (!res.ok) return;
  const scenes = await res.json();
  const sceneData = scenes.find((s) => String(s.id) === String(id));
  if (sceneData) {
    currentSceneId = sceneData.id;
    nameInput.value = sceneData.name;
    loadSceneFromJson(sceneData.scene_json || "{}");
    statusEl.textContent = `Loaded ${sceneData.name}`;
  }
});

deleteBtn?.addEventListener("click", () => {
  if (selected) {
    scene.remove(selected);
    selectObject(null);
  }
});

await refreshSceneList();
animate();
