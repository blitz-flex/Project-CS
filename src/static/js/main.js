import { initCounters } from './ui.js';
import { initSmoothScroll } from './navigation.js';
import { initCyberMap } from './cyber-map.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI Components
    initCounters();
    
    // Initialize Navigation Logic
    initSmoothScroll();
    
    // Initialize Cyber Effects
    initCyberMap();
});
