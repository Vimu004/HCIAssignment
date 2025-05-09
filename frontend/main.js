import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

let scene, camera, renderer, controls;
let light, ambient;
let models = [], selectedModel = null, selectionOutline = null;
let floorMesh, ceilingMesh, gridHelper, walls = [];

const raycaster = new THREE.Raycaster();
raycaster.far = 50000;
const pointer = new THREE.Vector2();
let snapToGrid = false;
let isDragging = false;
let roomInitialized = false;

document.addEventListener("DOMContentLoaded", () => {
  init();
  buildRoom(); 
  animate();

  const newModelPath = localStorage.getItem("newFurnitureModel");
  if (newModelPath) {
    loadFurnitureModel(newModelPath); 
    localStorage.removeItem("newFurnitureModel");
  }
});

function init() {
  const canvas = document.getElementById("studioCanvas");
  scene = new THREE.Scene();

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);

  camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 2000);
  camera.position.set(5, 12, 20);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 0, 0);
  controls.update();

  light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(10, 20, 10);
  ambient = new THREE.AmbientLight(0x404040);
  scene.add(light, ambient);

  gridHelper = new THREE.GridHelper(50, 50);
  gridHelper.material.opacity = 0.4;
  gridHelper.material.transparent = true;
  scene.add(gridHelper);

  document.getElementById("resetRoomBtn")?.addEventListener("click", resetRoom);
  document.getElementById("deleteModelBtn")?.addEventListener("click", () => removeSelected());
  document.getElementById("snapToggleBtn")?.addEventListener("click", () => {
    snapToGrid = !snapToGrid;
    alert("Snap-to-grid: " + (snapToGrid ? "ON" : "OFF"));
  });

  document.getElementById("saveDesignBtn")?.addEventListener("click", async () => {
    const name = prompt("Enter design name:");
    if (!name) return;
    const state = getCurrentRoomState();
    state.design_name = name;
    const res = await fetch('/designs/save', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state)
    });
    const result = await res.json();
    alert(result.status === "ok" ? "Design saved!" : "Error saving design.");
  });

  document.getElementById("exportScreenshotBtn")?.addEventListener("click", () => {
    renderer.render(scene, camera);
    const link = document.createElement("a");
    link.download = "furni-studio-screenshot.png";
    link.href = renderer.domElement.toDataURL();
    link.click();
  });

  ["wallColor", "floorColor", "ceilingColor", "roomWidth", "roomLength", "lightIntensity"].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    if (id.includes("Color")) el.oninput = updateColors;
    else el.oninput = () => {
      if (roomInitialized) buildRoom();
    };
  });

  window.addEventListener("resize", () => {
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Delete") removeSelected();
  });

  renderer.domElement.addEventListener("pointerdown", onPointerDown);
  renderer.domElement.addEventListener("contextmenu", onRightClick);

  window.loadFurnitureModel = loadFurnitureModel;
}

function updateColors() {
  const wc = new THREE.Color(document.getElementById("wallColor").value);
  const fc = new THREE.Color(document.getElementById("floorColor").value);
  const cc = new THREE.Color(document.getElementById("ceilingColor").value);
  walls.forEach(w => w.material.color.set(wc));
  if (floorMesh) floorMesh.material.color.set(fc);
  if (ceilingMesh) ceilingMesh.material.color.set(cc);
}

function resetRoom() {
  document.getElementById("wallColor").value = '#dddddd';
  document.getElementById("floorColor").value = '#eeeeee';
  document.getElementById("ceilingColor").value = '#ffffff';
  document.getElementById("roomWidth").value = 10;
  document.getElementById("roomLength").value = 10;
  document.getElementById("lightIntensity").value = 1;
  buildRoom();
}

function buildRoom() {
  const width = parseFloat(document.getElementById("roomWidth").value);
  const length = parseFloat(document.getElementById("roomLength").value);

  if (floorMesh) scene.remove(floorMesh);
  if (ceilingMesh) scene.remove(ceilingMesh);
  walls.forEach(w => scene.remove(w));
  walls = [];

  const floorMat = new THREE.MeshStandardMaterial({ color: document.getElementById("floorColor").value });
  const floorGeo = new THREE.PlaneGeometry(width, length);
  floorMesh = new THREE.Mesh(floorGeo, floorMat);
  floorMesh.rotation.x = -Math.PI / 2;
  scene.add(floorMesh);

  const ceilingMat = new THREE.MeshStandardMaterial({ color: document.getElementById("ceilingColor").value });
  ceilingMesh = new THREE.Mesh(floorGeo, ceilingMat);
  ceilingMesh.rotation.x = Math.PI / 2;
  ceilingMesh.position.y = 3;
  scene.add(ceilingMesh);

  const wallMat = new THREE.MeshStandardMaterial({ color: document.getElementById("wallColor").value });
  const wallZ = new THREE.BoxGeometry(width, 3, 0.1);
  const wallX = new THREE.BoxGeometry(0.1, 3, length);

  const wallFront = new THREE.Mesh(wallZ, wallMat.clone());
  wallFront.position.set(0, 1.5, -length / 2);
  scene.add(wallFront);

  const wallBack = new THREE.Mesh(wallZ, wallMat.clone());
  wallBack.position.set(0, 1.5, length / 2);
  scene.add(wallBack);

  const wallLeft = new THREE.Mesh(wallX, wallMat.clone());
  wallLeft.position.set(-width / 2, 1.5, 0);
  scene.add(wallLeft);

  const wallRight = new THREE.Mesh(wallX, wallMat.clone());
  wallRight.position.set(width / 2, 1.5, 0);
  scene.add(wallRight);

  walls.push(wallFront, wallBack, wallLeft, wallRight);

  light.intensity = parseFloat(document.getElementById("lightIntensity").value);
  ambient.intensity = light.intensity * 0.4;

  animateCameraTo(new THREE.Vector3(0, 0, 0), Math.max(width, length));
  roomInitialized = true;
}

function animateCameraTo(targetVec, offset = 10) {
  const target = targetVec.clone();
  const newPos = new THREE.Vector3(0, offset, offset);
  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();
  let t = 0;

  function animateStep() {
    if (t >= 1) return;
    t += 0.03;
    camera.position.lerpVectors(startPos, newPos, t);
    controls.target.lerpVectors(startTarget, target, t);
    controls.update();
    requestAnimationFrame(animateStep);
  }

  animateStep();
}

function onRightClick(e) {
  e.preventDefault();
  if (selectedModel) selectedModel.rotation.y += Math.PI / 2;
}

function onPointerDown(e) {
  e.preventDefault();
  e.stopPropagation();

  pointer.x = (e.clientX / renderer.domElement.clientWidth) * 2 - 1;
  pointer.y = -(e.clientY / renderer.domElement.clientHeight) * 2 + 1;

  raycaster.setFromCamera(pointer, camera);
  const intersects = raycaster.intersectObjects(models, true);

  if (intersects.length > 0) {
    selectedModel = intersects[0].object;
    while (selectedModel.parent && !models.includes(selectedModel)) {
      selectedModel = selectedModel.parent;
    }

    updateSelectionOutline();

    const offset = intersects[0].point.clone().sub(selectedModel.position);
    controls.enabled = false;
    isDragging = true;

    const moveHandler = moveEvent => {
      moveEvent.preventDefault();
      moveEvent.stopPropagation();
      pointer.x = (moveEvent.clientX / renderer.domElement.clientWidth) * 2 - 1;
      pointer.y = -(moveEvent.clientY / renderer.domElement.clientHeight) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hits = raycaster.intersectObject(floorMesh);
      if (hits.length > 0) {
        let pos = hits[0].point.clone().sub(offset);
        if (snapToGrid) {
          pos.x = Math.round(pos.x);
          pos.z = Math.round(pos.z);
        }
        pos.y = selectedModel.position.y;
        selectedModel.position.set(pos.x, pos.y, pos.z);
        updateSelectionOutline();
      }
    };

    const upHandler = () => {
      renderer.domElement.removeEventListener("pointermove", moveHandler);
      renderer.domElement.removeEventListener("pointerup", upHandler);
      controls.enabled = true;
      isDragging = false;
    };

    renderer.domElement.addEventListener("pointermove", moveHandler);
    renderer.domElement.addEventListener("pointerup", upHandler);
  }
}

function updateSelectionOutline() {
  if (selectionOutline) scene.remove(selectionOutline);
  if (selectedModel) {
    selectionOutline = new THREE.BoxHelper(selectedModel, 0xffff00);
    scene.add(selectionOutline);
  }
}

export function loadFurnitureModel(glbPath) {
  const loader = new GLTFLoader();
  loader.load(glbPath, (gltf) => {
    const model = gltf.scene;
    const width = parseFloat(document.getElementById("roomWidth").value);
    const length = parseFloat(document.getElementById("roomLength").value);
    const scaleFactor = Math.min(width, length) / 10 * 2.0;

    model.scale.setScalar(scaleFactor);
    model.userData.glbPath = glbPath;

    const bbox = new THREE.Box3().setFromObject(model);
    const size = new THREE.Vector3();
    bbox.getSize(size);
    model.position.y = size.y / 2;

    model.traverse(o => {
      o.castShadow = true;
      o.receiveShadow = true;
    });

    scene.add(model);
    models.push(model);
  });
}

function removeSelected() {
  if (!selectedModel) return;
  scene.remove(selectedModel);
  models = models.filter(m => m !== selectedModel);
  if (selectionOutline) {
    scene.remove(selectionOutline);
    selectionOutline = null;
  }
  selectedModel = null;
}

function getCurrentRoomState() {
  return {
    room_config: {
      width: parseFloat(document.getElementById("roomWidth").value),
      length: parseFloat(document.getElementById("roomLength").value),
      wall_color: document.getElementById("wallColor").value,
      floor_color: document.getElementById("floorColor").value,
      ceiling_color: document.getElementById("ceilingColor").value,
      lighting: { intensity: parseFloat(document.getElementById("lightIntensity").value) }
    },
    furniture: models.map(m => ({
      model: m.userData.glbPath,
      position: [m.position.x, m.position.y, m.position.z],
      rotation: [m.rotation.x, m.rotation.y, m.rotation.z],
      scale: m.scale.x
    }))
  };
}

window.loadDesign = function (data) {
  const cfg = data.room_config;
  document.getElementById("roomWidth").value = cfg.width;
  document.getElementById("roomLength").value = cfg.length;
  document.getElementById("wallColor").value = cfg.wall_color;
  document.getElementById("floorColor").value = cfg.floor_color;
  document.getElementById("ceilingColor").value = cfg.ceiling_color;
  document.getElementById("lightIntensity").value = cfg.lighting.intensity;
  buildRoom();

  models.forEach(m => scene.remove(m));
  models = [];

  const loader = new GLTFLoader();
  data.furniture.forEach(f => {
    loader.load(f.model, gltf => {
      const m = gltf.scene;
      m.position.set(...f.position);
      m.rotation.set(...f.rotation);
      m.scale.setScalar(f.scale);
      m.userData.glbPath = f.model;
      scene.add(m);
      models.push(m);
    });
  });
};

function animate() {
  requestAnimationFrame(animate);
  if (!isDragging) {
    controls.update();
  }
  if (selectionOutline) selectionOutline.update();
  renderer.render(scene, camera);
}

window.modelController = {
  moveForward() {
    if (selectedModel) {
      selectedModel.position.z -= 1;
      updateSelectionOutline();
    }
  },
  moveBackward() {
    if (selectedModel) {
      selectedModel.position.z += 1;
      updateSelectionOutline();
    }
  },
  moveLeft() {
    if (selectedModel) {
      selectedModel.position.x -= 1;
      updateSelectionOutline();
    }
  },
  moveRight() {
    if (selectedModel) {
      selectedModel.position.x += 1;
      updateSelectionOutline();
    }
  },
  moveUp() {
    if (selectedModel) {
      selectedModel.position.y += 1;
      updateSelectionOutline();
    }
  },
  moveDown() {
    if (selectedModel) {
      selectedModel.position.y -= 1;
      updateSelectionOutline();
    }
  },
  rotateLeft() {
    if (selectedModel) {
      selectedModel.rotation.y += Math.PI / 8;
      updateSelectionOutline();
    }
  },
  rotateRight() {
    if (selectedModel) {
      selectedModel.rotation.y -= Math.PI / 8;
      updateSelectionOutline();
    }
  }
};