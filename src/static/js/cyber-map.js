export function initCyberMap() {
    const mapRoot = document.getElementById('cyber-map-root');
    const attackLayer = document.getElementById('attack-layers');
    const logElement = document.getElementById('latest-attack-log');
    const nodes = document.querySelectorAll('.map-node');
    
    if (!mapRoot || !attackLayer) return;

    const ips = ['45.12.33.1', '192.168.12.4', '10.0.4.122', '88.21.4.9', '172.16.0.44'];
    const threats = ['Brute-force', 'DDoS Vector', 'SQL Injection', 'Payload Delivery', 'Lateral Movement'];

    function createAttack() {
        const startNode = nodes[Math.floor(Math.random() * nodes.length)];
        const endNode = nodes[Math.floor(Math.random() * nodes.length)];
        
        if (startNode === endNode) return;

        const x1 = startNode.getAttribute('cx');
        const y1 = startNode.getAttribute('cy');
        const x2 = endNode.getAttribute('cx');
        const y2 = endNode.getAttribute('cy');

        const midX = (parseInt(x1) + parseInt(x2)) / 2;
        const midY = (parseInt(y1) + parseInt(y2)) / 2 - 50; 
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const d = `M${x1},${y1} Q${midX},${midY} ${x2},${y2}`;
        
        path.setAttribute('d', d);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', 'var(--primary-gold)');
        path.setAttribute('stroke-width', '1');
        path.setAttribute('stroke-dasharray', '1000');
        path.setAttribute('stroke-dashoffset', '1000');
        path.setAttribute('opacity', '0.6');
        
        path.style.transition = 'stroke-dashoffset 2s ease-in-out, opacity 1s 2s';
        attackLayer.appendChild(path);

        setTimeout(() => {
            path.style.strokeDashoffset = '0';
        }, 50);

        const randomIP = ips[Math.floor(Math.random() * ips.length)];
        const randomThreat = threats[Math.floor(Math.random() * threats.length)];
        logElement.innerHTML = `<span class="text-danger">[${randomThreat}]</span> from ${randomIP} to ${endNode.dataset.name}`;

        setTimeout(() => {
            path.style.opacity = '0';
            setTimeout(() => path.remove(), 1000);
        }, 3000);
    }

    setInterval(createAttack, 3000);
    createAttack();
}
