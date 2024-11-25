document.addEventListener("DOMContentLoaded", function () {
    try {
        // Helper function: Calculate distance using the Haversine formula
        function calculateDistance(lat1, lon1, lat2, lon2) {
            const toRadians = (degree) => (degree * Math.PI) / 180;
            const R = 6371; // Earth's radius in kilometers
            const dLat = toRadians(lat2 - lat1);
            const dLon = toRadians(lon2 - lon1);
            const a =
                Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(toRadians(lat1)) *
                    Math.cos(toRadians(lat2)) *
                    Math.sin(dLon / 2) *
                    Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c; // Distance in kilometers
        }

        // Get user coordinates
        const userCoordinatesElement = document.getElementById("user-coordinates");
        if (!userCoordinatesElement) throw new Error("user-coordinates element not found");

        const rawUserCoordinates = userCoordinatesElement.textContent.trim();
        const userCoordinates = JSON.parse(rawUserCoordinates);
        console.log("User Coordinates:", userCoordinates);

        const userLat = Array.isArray(userCoordinates) ? userCoordinates[1] : userCoordinates.latitude;
        const userLng = Array.isArray(userCoordinates) ? userCoordinates[0] : userCoordinates.longitude;

        // Get store locations
        const storeLocationsElement = document.getElementById("store-locations");
        if (!storeLocationsElement) throw new Error("store-locations element not found");

        const rawStoreLocations = storeLocationsElement.textContent.trim();
        const fixedStoreLocations = rawStoreLocations
            .replace(/'/g, '"') // Replace single quotes with double quotes
            .replace(/\bTrue\b/g, 'true') // Replace True with true
            .replace(/\bFalse\b/g, 'false'); // Replace False with false

        const storeLocations = JSON.parse(fixedStoreLocations);
        console.log("Parsed Store Locations:", storeLocations);

        // Calculate distances from user and rank stores
        const rankedLocations = storeLocations.map((store) => {
            const distance = calculateDistance(userLat, userLng, store.latitude, store.longitude);
            return { ...store, distance }; // Add distance to each store object
        });

        // Sort locations by distance
        rankedLocations.sort((a, b) => a.distance - b.distance);

        console.log("Ranked Store Locations:", rankedLocations);

        // Initialize the map centered on the user's location
        const map = L.map("map").setView([userLat, userLng], 13);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '© OpenStreetMap contributors',
        }).addTo(map);

        // Add a marker for the user's location
        L.marker([userLat, userLng])
            .addTo(map)
            .bindPopup("Your Location")
            .openPopup();

        // Custom icon for ranked markers
        const createCustomIcon = (rank) => {
            return L.divIcon({
                className: 'custom-marker',
                html: `<div class="rank-icon">${rank}</div>`,
                iconSize: [30, 42],
                iconAnchor: [15, 42],
            });
        };

        // Add markers for each ranked store location
        rankedLocations.forEach((store, index) => {
            const rank = index + 1;
            L.marker([store.latitude, store.longitude], {
                icon: createCustomIcon(rank),
            })
                .addTo(map)
                .bindPopup(`
                    <strong>${store.name}</strong><br>
                    ${store.address}<br>
                    Phone: ${store.phone || 'N/A'}<br>
                    Rating: ${store.rating || 'N/A'} (${store.review_count || '0'} reviews)<br>
                    Distance: ${store.distance ? store.distance.toFixed(2) : 'N/A'} miles<br>
                    <a href="${store.business_url}" target="_blank">Visit Store</a><br>
                    <a href="${store.google_maps_link}" target="_blank">Get Map Directions</a>
                `);
        });

        console.log("All ranked markers added to the map.");
    } catch (error) {
        console.error("Error in map rendering:", error);
    }
});
