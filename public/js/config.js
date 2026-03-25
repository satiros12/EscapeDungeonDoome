const CONFIG = {
    FOV: Math.PI / 3,
    HALF_FOV: Math.PI / 6,
    NUM_RAYS: 320,
    MAX_DEPTH: 16,
    FOV_CULL: 0.2,
    RAY_STEP: 0.02,
    MIN_BRIGHTNESS: 0.3,
    WALL_COLOR_BASE: [255, 200, 180],
    WALL_COLOR_SIDE: [180, 160, 140],
    PLAYER_MAX_HEALTH: 100
};

const WS_URL = `ws://${window.location.hostname}:8001`;

const mapData = [
    "################",
    "#              #",
    "#   E    #     #",
    "#        #     #",
    "#      ###     #",
    "#      # P     #",
    "#          E   #",
    "#    ###      #",
    "#    #        #",
    "#    #    #   #",
    "#        #    #",
    "#   ###       #",
    "#          E  #",
    "#              #",
    "#              #",
    "################"
];

const MAP_WIDTH = mapData[0].length;
const MAP_HEIGHT = mapData.length;