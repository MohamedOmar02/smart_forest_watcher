/**
 * camera-alerts.js
 * Listen for real-time camera fire detections via WebSocket.
 */
document.addEventListener('DOMContentLoaded', function() {
    const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = protocol + window.location.host + '/ws/cameras/';
    
    console.log("Connecting to Camera WebSocket:", wsUrl);
    
    function connect() {
        const cameraSocket = new WebSocket(wsUrl);

        cameraSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            console.log("Camera Alert Received:", data);

            if (data.type === 'camera_alert') {
                const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/995/995-preview.mp3');
                audio.play().catch(e => console.warn("Audio play blocked by browser"));

                Swal.fire({
                    title: '🔥 FIRE DETECTED!',
                    html: `
                        <div class="text-start">
                            <p><b>Camera:</b> ${data.camera_name} (${data.camera_id})</p>
                            <p><b>Location:</b> ${data.parcelle} — ${data.project}</p>
                            <p><b>Confidence:</b> ${(data.confidence * 100).toFixed(1)}%</p>
                            <img src="${data.image_url}" class="img-fluid rounded shadow-sm mt-2" style="max-height: 300px; width: 100%; object-fit: cover;">
                        </div>
                    `,
                    icon: 'warning',
                    confirmButtonText: 'View on Map',
                    confirmButtonColor: '#ef4444',
                    showCancelButton: true,
                    cancelButtonText: 'Dismiss',
                    background: '#fff',
                    customClass: {
                        popup: 'premium-swal-alert'
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        if (window.map) {
                            location.reload(); 
                        }
                    }
                });
            }
        };

        cameraSocket.onclose = function(e) {
            console.error('Camera socket closed unexpectedly. Reconnecting in 5s...');
            setTimeout(() => {
                connect(); // Reconnect the websocket instead of reloading the page
            }, 5000);
        };
    }

    connect();
});
