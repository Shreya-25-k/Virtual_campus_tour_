const SCENE_IDS = {
  MAINENTRANCE: "mainentrance",
  PANORAMA2: "panorama2",
  PANORAMA3: "panorama3",
  PANORAMA4: "panorama4",
  PANORAMA5: "panorama5",
  PANORAMA6: "panorama6",
  PANORAMA6_1: "panorama6_1",
  PANORAMA7: "panorama7"
};

const scenes = {
  [SCENE_IDS.MAINENTRANCE]: {
    panorama: "images/panoramas/mainentrance.jpg",
    hotspots: [
      createHotspot(0, -10, SCENE_IDS.PANORAMA2),
    ],
  },
  [SCENE_IDS.PANORAMA2]: {
    panorama: "images/panoramas/panorama2.jpg",
    hotspots: [
      createHotspot(-5, -15, SCENE_IDS.PANORAMA4),
      createHotspot(-10, 170, SCENE_IDS.MAINENTRANCE),
      createHotspot(-12, 50, SCENE_IDS.PANORAMA6_1),
    ],
  },
  [SCENE_IDS.PANORAMA4]: {
    panorama: "images/panoramas/panorama4.jpg",
    hotspots: [
      createHotspot(-5, -170, SCENE_IDS.PANORAMA2),
      createHotspot(-10, 7, SCENE_IDS.PANORAMA5),
    ],
  },
  [SCENE_IDS.PANORAMA5]: {
    panorama: "images/panoramas/panorama5.jpg",
    hotspots: [
      createHotspot(0, -30, SCENE_IDS.PANORAMA4),
      createHotspot(0, 30, SCENE_IDS.PANORAMA),
    ],
  },
  [SCENE_IDS.PANORAMA6_1]: {
    panorama: "images/panoramas/panorama6_1.jpg",
    hotspots: [
      createHotspot(-15, -110, SCENE_IDS.PANORAMA7),
      createHotspot(0, 30, SCENE_IDS.PANORAMA2),
    ],
  },
  [SCENE_IDS.PANORAMA7]: {
    panorama: "images/panoramas/panorama7.jpg",
    hotspots: [
      createHotspot(-5, 160, SCENE_IDS.PANORAMA6_1),
    ],
  },
};

// Function to create a hotspot
function createHotspot(pitch, yaw, sceneId) {
  return {
    pitch,
    yaw,
    type: "scene",
    text: `<span class='dot dot-${sceneId === SCENE_IDS.MAINENTRANCE ? 'left' : 'right'}'></span>`,
    sceneId,
    clickHandlerFunc: () => loadScene(sceneId),
  };
}

// Initialize the Pannellum viewer
const viewer = pannellum.viewer("panorama", {
  default: {
    firstScene: SCENE_IDS.MAINENTRANCE,
    autoLoad: true,
    sceneFadeDuration:1000,
    hfov: 150,
  },
  scenes: Object.keys(scenes).reduce((acc, sceneId) => {
    const scene = scenes[sceneId];
    acc[sceneId] = {
      panorama: scene.panorama,
      hotSpots: scene.hotspots,
    };
    return acc;
  }, {}),
});

// Function to load a new scene with error handling
function loadScene(sceneId) {
  const loadingSpinner = document.getElementById('loading');
  loadingSpinner.style.display = 'block'; // Show loading spinner
  try {
    viewer.loadScene(sceneId);
    viewer.setHfov(120); // Reset zoom after scene change
  } catch (error) {
    console.error(`Error loading scene ${sceneId}:`, error);
    alert("Failed to load the scene. Please try again.");
  } finally {
    loadingSpinner.style.display = 'none'; // Hide loading spinner
  }
}

// Update compass direction based on the current yaw of the viewer
viewer.on ;javascript ('scenechange', () => {const yaw = viewer.getYaw();
  const compass = document.getElementById('compass');
  requestAnimationFrame(() => {
    compass.style.transform = `rotate(${yaw}deg)`; // Rotate compass based on viewer yaw
  });
});