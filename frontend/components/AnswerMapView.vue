<template>
    <v-sheet v-model="dialog" width="auto">
        <!-- <template v-slot:activator="{ props }">
            <v-btn class="mt-4" variant="tonal" append-icon="mdi-pencil" border v-bind="props">Edit Map</v-btn>
        </template> -->

        <v-card>
            <v-card-text>
                <!-- <v-text-field v-model="title" label="Name of map view" variant="outlined"></v-text-field> -->
                <p>Map name: {{ mapViewStore.name }}</p>
                <p>Map url: {{ mapViewStore.mapServiceUrl }}</p>
                <p>Map zoom: {{ mapViewStore.zoomLevel }}</p>
                <p>Map  store center: {{ mapViewStore.center }}</p>

                <!-- TODO: fix issue with passing values for center. check issue: https://stackoverflow.com/questions/42879725/leaflet-will-not-display-my-marker-typeerror-t-is-null -->

                <div style="height:600px; width:auto">
                    <l-map ref="mapRefPopUp" 
                        :zoom="mapViewStore.zoomLevel" 
                        :center="mapViewStore.center"
                        @ready=""  @update:zoom="updateZoom"
                        @update:center="" :noBlockingAnimations="true">
                        <l-tile-layer 
                            :url="mapViewStore.mapServiceUrl"
                            layer-type="base"
                            >
                        </l-tile-layer>
                        <l-feature-group ref="featureGroupRefWControl"></l-feature-group>
                    </l-map>
                </div>
            </v-card-text>
            <v-card-actions>
                <v-btn variant="tonal" block @click="submitMap">Save map</v-btn>
                <!-- <v-btn color="primary" block @click="dialog = false">Save</v-btn> -->
            </v-card-actions>
        </v-card>
    </v-sheet>
</template>
  
<script setup>
import "leaflet/dist/leaflet.css";
import "leaflet-draw/dist/leaflet.draw.css";
import "leaflet-toolbar/dist/leaflet.toolbar.css";
import { LMap, LTileLayer, LFeatureGroup, LGeoJson, LCircle, LCircleMarker } from "@vue-leaflet/vue-leaflet";
import "leaflet-draw/dist/leaflet.draw-src.js";
import "leaflet-toolbar";
import "leaflet-draw-toolbar/dist/leaflet.draw-toolbar.js";
import { ref, reactive, onMounted } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { forEach } from 'ramda'
// Store
import { useMapViewStore } from "~/stores/mapview"
import { useQuestionDesignStore } from "~/stores/questionDesign"
import { useGlobalStore } from '~/stores/global'


const questionStore = useQuestionDesignStore()

const props = defineProps({
    questionIndex: Number,
    mapViewId: Number | undefined
    // name: String,
    // mapServiceUrl: String,
    // options: Object, // e.g. {zoom: 7, center: [52.04573404034129, 5.108642578125001]}
})

// Map without controls
const mapRefPopUp = ref(null)
const storedMapWithoutControls = ref(null)
// Map with controls (the pop up one)
const mapRef = ref(null)
const featureGroupRef = ref(null)
const featureGroupRefWControl = ref(null)
// const dialog = ref(props.dialogOpen)
const drawnItemsRef = ref(null)
const optionsTempStoreZoom = ref(null)
const optionsTempStoreCenter = ref(null)
const updateKeyMapWithoutControls = ref(0)
const updateKeyGeoJson = ref(0)

const mapViewData = reactive({
    id: props.mapViewId || null,
    name: "", 
    geometries: {}
})


const mapViewStore = useMapViewStore()
mapViewStore.$reset()

/**
 * Fetch the geojson data from the DB and add it to the mapViewData
 */
if (props.mapViewId) {        
        let mapView = await mapViewStore.fetchMapView(props.mapViewId)
    }


//  onMounted(async () => {
//     if (props.mapViewId) {
//         mapViewStore.$reset() // Reset the store to avoid old data
//         const geoData = await mapViewStore.fetchMapView(props.mapViewId)

//         if (geoData?.value?.geometries) { // 
//             console.log('geoData.value.geometries //> ', geoData.value.geometries)
//             mapViewData.geometries = mapViewStore.geometries
//         }
//         if (geoData.value?.name) {
//             mapViewData.name = mapViewStore.name
            
//         }
//         if (geoData.value?.map_service_url) {
//             mapViewData.map_service_url = mapViewStore.mapServiceUrl
//         }
//         if (geoData.value?.options?.zoom) {
//             mapViewData.options.zoom = mapViewStore.zoomLevel
//         }
//         if (geoData.value?.options?.center) {
//             let center = mapViewStore.center
//             mapViewData.options.center = center.map(Number)
//         }
        
//         console.log('map STORE CENTER //> ', mapViewStore.center)
//     }
// })


/**
 * Utils
 */

const setGeoJsonMarkers = () => {
    const drawnItems = featureGroupRef.value.leafletObject
    const initialGeojson = mapViewData.geometries;

    initialGeojson.features.forEach((feature) => {
        const layer = L.geoJSON(feature, {
            pointToLayer: function (feature, latlng) {
                if (feature.properties.radius) {
                    return L.circle(latlng, { radius: feature.properties.radius });
                } else {
                    return L.marker(latlng);
                }
            },
        }).addTo(drawnItems);
        drawnItems.addLayer(layer);
    });
}

/**
 * Listeners
 */

const geoJsonReady = () => {
    setGeoJsonMarkers()
}






/**
 * Watch mapViewData.geojson to update the map after changes or else the new values won't be visible
 */

watch(
    () => mapViewData.geometries,
    (newvalue) => {
        updateKeyGeoJson.value++
    },
    { deep: true }
)

/**
 * Computed functions
 */

const title = computed({
    get: () => props.title || mapViewData.name,
    set: (value) => {
        mapViewData.name = value
    }
})

/**
 * Add the props.geojson to the drawnItemsRef value
 */
// const onMapWWControlReady = () => {
//     const map = mapRefPopUp.value.leafletObject;
//     if (map !== null) {
//         drawnItemsRef.value = featureGroupRefWControl.value.leafletObject;

//         if (mapViewData.geometries.features) {
//             const drawnItems = drawnItemsRef.value;
//             const initialGeojson = mapViewData.geometries;

//             initialGeojson.features.forEach((feature) => {
//                 const layer = L.geoJSON(feature, {
//                     pointToLayer: function (feature, latlng) {
//                         if (feature.properties.radius) {
//                             return L.circle(latlng, { radius: feature.properties.radius });
//                         } else {
//                             return L.marker(latlng);
//                         }
//                     },
//                 }).addTo(drawnItems);
//                 drawnItems.addLayer(layer);
//             });
//         }

//         // Initialize the draw control and pass it the FeatureGroup of editable layers
//         const drawControl = new L.Control.Draw({
//             edit: {
//                 featureGroup: drawnItemsRef.value,
//             },
//             draw: {
//                 circle: true, // Add circle shape
//                 marker: true,
//                 polyline: true,
//                 polygon: true,
//                 rectangle: false,
//                 circleMarker: false
//             }
//         });

//         map.addControl(drawControl);
//         // set options
//         map.setView(mapViewData.options.center, mapViewData.options.zoom);


//         map.on(L.Draw.Event.CREATED, (event) => {
//             const layer = event.layer;
//             const layerType = event.layerType;

//             if (layerType === 'circle') {
//                 const radius = layer.getRadius();
//                 const latlng = layer.getLatLng();
//                 const geojsonFeature = {
//                     type: 'Feature',
//                     properties: { radius: radius },
//                     geometry: { type: 'Point', coordinates: [latlng.lng, latlng.lat] },
//                 };
//                 const circleLayer = L.geoJSON(geojsonFeature, {
//                     pointToLayer: function (feature, latlng) {
//                         return L.circle(latlng, { radius: feature.properties.radius });
//                     },
//                 });
//                 drawnItemsRef.value.addLayer(circleLayer);
//             } else {
//                 drawnItemsRef.value.addLayer(layer);
//             }
//         });


//         map.on(L.Draw.Event.DELETED, (event) => {
//             const layers = event.layers;
//             layers.eachLayer((layer) => {
//                 drawnItemsRef.value.removeLayer(layer);
//             });
//         });

//         map.on(L.Draw.Event.EDITED, (event) => {
//             const layers = event.layers;
//             layers.eachLayer((layer) => {
//                 // Remove the old version of the edited layer
//                 drawnItemsRef.value.removeLayer(layer);

//                 // Add the updated version of the edited layer
//                 drawnItemsRef.value.addLayer(layer);
//             });
//         });
//     }
// };

/**
 * Init the map with out controls
 */

const onLeafletReadyMapWithoutControls = () => {
    const map = mapRef.value.leafletObject;

    if (map !== null) {
        // storedMapWithoutControls.value = map
        // set options
        map.setView(mapViewData.options.center, mapViewData.options.zoom);

        map.dragging.disable();
        map.touchZoom.disable();
        map.doubleClickZoom.disable();
        map.scrollWheelZoom.disable();
        map.boxZoom.disable();
        map.keyboard.disable();
        if (map.tap) map.tap.disable();
        // document.getElementById('map').style.cursor = 'default';
    }

};

/**
 * Handlers
 */

const updateZoom = (value) => {
    console.log('value //> ', value)
    optionsTempStoreZoom.value = value
    console.log('optionsTempStoreZoom.valu //> ', optionsTempStoreZoom.value)
}

// const updateCenter = (value) => {
//     console.log('value //> ', value)
//     optionsTempStoreCenter.value = [value.lat, value.lng]
//     console.log('optionsTempStoreCenter.valu //> ', optionsTempStoreCenter.value)
// }

const submitMap = async () => {
    const global = useGlobalStore()
    let response
    mapViewData.geometries = drawnItemsRef.value.toGeoJSON()
    // Save new zoom value if not falsely
    console.log('optionsTempStoreZoom.value submit //> ', optionsTempStoreZoom.value)
    if (optionsTempStoreZoom?.value) {
        mapViewData.options.zoom = optionsTempStoreZoom.value
    }
    console.log('optionsTempStoreZoom.valu submit //> ', optionsTempStoreCenter.value)
    // Save new center value if not falsely
    if (optionsTempStoreCenter?.value) {
        mapViewData.options.center = optionsTempStoreCenter.value
    }
    /**
     * Check if the mapView already exists, if it exist then update, if not then create a new one
     */

    if (props.mapViewId) {
        response = await mapViewStore.updateMapview(props.mapViewId, mapViewData)
    } else {
        mapViewData.name = mapViewData?.name || uuidv4()
        response = await mapViewStore.createMapview(mapViewData)
    }

    if (response.data) {
        mapViewData.name = response.data.name
        await questionStore.editCurrentQuestionKeyValue(props.questionIndex, { map_view: response.data.id })
        await questionStore.saveCurrentQuestions()
    }
    updateKeyMapWithoutControls.value++
    setGeoJsonMarkers()
    // response.refresh()
    global.succes('Map view saved')
    
}
</script>
  
<style></style>