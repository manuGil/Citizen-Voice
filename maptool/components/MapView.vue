
<template>
    <v-sheet width="auto">
        <!-- <template v-slot:activator="{ props }">
            <v-btn class="mt-4" variant="tonal" append-icon="mdi-pencil" border v-bind="props">Edit Map</v-btn>
        </template> -->
        <v-card>
            <v-card-text>
                <!-- <v-text-field v-model="title" label="Name of map view" variant="outlined"></v-text-field> -->
                <!-- <p>Map name: {{ questionMapView.name }}</p> -->
                <div style="height:600px; width:auto">
                    <l-map ref="mapGeometriesRef" 
                        :zoom="questionMapView.options.zoom" 
                        :center="questionMapView.options.center"
                        @ready="onMapWWControlReady"  @update:zoom="handleUpdateMapViewZoom"
                        @update:center="handleUpdateMapViewCenter" :noBlockingAnimations="true">
                        <l-tile-layer 
                            :url="questionMapView.map_service_url"
                            layer-type="base"
                            >
                        </l-tile-layer>
                        <l-geo-json 
                        @ready="geoJsonReady" :key="updateKeyGeoJson">
                        </l-geo-json>
                        <l-feature-group ref="featureGroupRef">

                        </l-feature-group>
                    </l-map>
                </div>
            </v-card-text>
            <v-card-actions class="d-flex align-center justify-space-between">
                <div class="geometry-status d-flex align-center">
                    <v-icon 
                        v-if="hasGeometries" 
                        color="blue" 
                        size="small" 
                        class="mr-2"
                    >
                        mdi-map-marker-multiple
                    </v-icon>
                    <span class="text-caption">
                        {{ getGeometryStatusText() }}
                    </span>
                </div>
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
import { ref, reactive, onMounted, onBeforeMount, nextTick, computed } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { forEach } from 'ramda'
// Store

import { useAnswerMapViewStore } from "~/stores/answerMapview";
import { useQuestionMapViewStore } from "~/stores/questionMapview";
import { useResponseStore } from "~/stores/response";
import { useQuestionDesignStore } from "~/stores/questionDesign";
import { useGlobalStore } from '~/stores/global';
import { parse } from "postcss";
import { th } from "vuetify/locale";

// API endpoints
const map_views_endpoint = '/map-views/'
const answerMapViewStore = useAnswerMapViewStore() // User's answer geometries
const questionMapViewStore = useQuestionMapViewStore() // Question's base geometries  
const responseStore = useResponseStore()
answerMapViewStore.$reset()

const props = defineProps({
    mapViewUrl: String | undefined
})


function extractMapviewId(mapUrl) {
    /*
    * Extracts the mapview id from the url
    * @param {String} mapViewUrl 
    * @returns {Number} id
    */
    const match = mapUrl.match(/\d+\/?$/);
    if (match) {
        const id = parseInt(match[0], 10);
        return id;
    } else {
        throw new Error('Could not extract mapview id from url', mapUrl)
    }
}

const route = useRoute();
var question_id = route.params.question; // use url questions id as an index to load each question 
let answer_index = question_id -1;  // gets the id for the questions

var questionMapView;
// console.log('props.mapViewUrl //> ', props.mapViewUrl)
// Fetch the map view for corresponding Question
if (props.mapViewUrl) {
    const mapViewId = extractMapviewId(props.mapViewUrl)
    // console.log('mapViewId //> ', mapViewId)
    const {data, error, pending} = await useCmsApiData(`${map_views_endpoint}${mapViewId}`)
    
    // console.log('mapview data', data.value)

    questionMapView = data.value
    // store the question mapview values to questionMapViewStore (designer's base data)
    questionMapViewStore.updateMapServiceUrl(questionMapView.map_service_url)
    questionMapViewStore.updateZoomLevel(questionMapView.options.zoom)
    questionMapViewStore.updateCenter(questionMapView.options.center)
    if (questionMapView.geometries) {
        questionMapViewStore.updateGeometries(questionMapView.geometries)
    }
    
    // ALSO store basic settings to answerMapViewStore as starting point for user modifications
    answerMapViewStore.updateMapServiceUrl(questionMapView.map_service_url)
    answerMapViewStore.updateZoomLevel(questionMapView.options.zoom)
    answerMapViewStore.updateCenter(questionMapView.options.center)
    if (error?.value) {
        throw new Error('error in questionMapView //> ', error)
    }
}


const mapGeometriesRef = ref() 
// Map without controls
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

// Geometry collection state
const hasGeometries = computed(() => {
    return answerMapViewStore.geometries && 
           answerMapViewStore.geometries.features && 
           answerMapViewStore.geometries.features.length > 0
})


// collects map parameters for the user's answer
const currentMapView = reactive({
    map_service_url: null,
    options: { 
        zoom:  null,
        center:  [] },
    name: "", 
    geometries: {
        type: "FeatureCollection",
        features: []
    }
});

const handleUpdateMapViewZoom = (updatedZoom) => {
    // Handle the updated answer here
    currentMapView.options.zoom = updatedZoom;
    answerMapViewStore.updateZoomLevel(updatedZoom);
};

const handleUpdateMapViewCenter = (updatedCenter) => {
    // Update the center of the map. Converts object {lat:value, lng:value} to array [lat, lng]
    // console.log('current mapview \\>', currentMapView);
    const newCenter = [updatedCenter.lat, updatedCenter.lng];
    currentMapView.options.center = newCenter;
    answerMapViewStore.updateCenter(newCenter);
};


const mapViewAnswerData = reactive({
    id: props.mapViewId || null,
    url: props.mapViewUrl || null,
    options: { zoom: 8, center: [52.045, 5.10] },
    name: "", 
    geometries: {
        type: "FeatureCollection",
        features: []
    }
})


/**
 * Utils
 */
const setGeoJsonMarkers = () => {
    const drawnItems = featureGroupRef.value.leafletObject
    
    // Function to add geometries to the map
    const addGeometriesToMap = (geometries, layerType) => {
        if (geometries?.features && geometries.features.length > 0) {
            console.log(`setGeoJsonMarkers: Loading ${layerType} geometries`);
            geometries.features.forEach((feature) => {
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
    };

    // 1. First load question's base geometries (from questionMapViewStore)
    addGeometriesToMap(questionMapViewStore.geometries, "question base");
    
    // 2. Then load user's answer geometries (from answerMapViewStore) - these will layer on top
    addGeometriesToMap(answerMapViewStore.geometries, "user answer");
    
    // 3. Fallback to local mapViewAnswerData for backward compatibility
    if ((!questionMapViewStore.geometries || !questionMapViewStore.geometries.features || questionMapViewStore.geometries.features.length === 0) &&
        (!answerMapViewStore.geometries || !answerMapViewStore.geometries.features || answerMapViewStore.geometries.features.length === 0)) {
        addGeometriesToMap(mapViewAnswerData.geometries, "local fallback");
    }
}

/**
 * Listeners
 */

const geoJsonReady = () => {
    setGeoJsonMarkers()
};


/**
 * Computed functions
 */

const title = computed({
    get: () => props.title || mapViewAnswerData.name,
    set: (value) => {
        mapViewAnswerData.name = value
    }
})

/**
 * Methods
 */

 const emit = defineEmits(['saveDescription']);

 const handleSaveDescription = (description) => {
      // Emit the saveDescription event with the description text
      emit('saveDescription', description);
    //   console.log('Description saved:', description);
      // You can also perform other actions here, like sending the description to a server
      // TODO: Fix. save the description to the layer
    }


/**
 * Add the props.geojson to the drawnItemsRef value
 */


const onMapWWControlReady = () => {
    const map = mapGeometriesRef.value.leafletObject;
    if (map !== null) {
        drawnItemsRef.value = featureGroupRef.value.leafletObject;

        const drawnItems = drawnItemsRef.value;

        // Function to add geometries to the map
        const addGeometriesToMap = (geometries, layerType) => {
            if (geometries?.features && geometries.features.length > 0) {
                console.log(`Loading ${layerType} geometries:`, geometries);
                geometries.features.forEach((feature) => {
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
        };

        // 1. First load question's base geometries (from questionMapViewStore)
        addGeometriesToMap(questionMapViewStore.geometries, "question base");
        
        // 2. Then load user's answer geometries (from answerMapViewStore) - these will layer on top
        addGeometriesToMap(answerMapViewStore.geometries, "user answer");
        
        // 3. Fallback to local currentMapView for backward compatibility
        if ((!questionMapViewStore.geometries || !questionMapViewStore.geometries.features || questionMapViewStore.geometries.features.length === 0) &&
            (!answerMapViewStore.geometries || !answerMapViewStore.geometries.features || answerMapViewStore.geometries.features.length === 0)) {
            addGeometriesToMap(currentMapView.geometries, "local fallback");
        }

        // Initialize the draw control and pass it the FeatureGroup of editable layers
        const drawControl = new L.Control.Draw({
            edit: {
                featureGroup: drawnItemsRef.value,
            },
            draw: {
                circle: true, // Add circle shape
                marker: true,
                polyline: true,
                polygon: true,
                rectangle: false,
                circleMarker: false,
            }
        });

        map.addControl(drawControl);
        // set options
        // map.setView(mapViewData.options.center, mapViewData.options.zoom);

        map.on(L.Draw.Event.CREATED, (event) => {
            const layer = event.layer;
            const layerType = event.layerType;

            if (layerType === 'circle') {
                const radius = layer.getRadius();
                const latlng = layer.getLatLng();
                const geojsonFeature = {
                    type: 'Feature',
                    properties: { 
                        radius: radius,
                        annotation: '' // Add annotation property
                    },
                    geometry: { type: 'Point', coordinates: [latlng.lng, latlng.lat] },
                };
                const circleLayer = L.geoJSON(geojsonFeature, {
                    pointToLayer: function (feature, latlng) {
                        return L.circle(latlng, { radius: feature.properties.radius });
                    },
                });
                circleLayer.feature = geojsonFeature; // Ensure feature is accessible
                drawnItemsRef.value.addLayer(circleLayer);
            } else {                
                drawnItemsRef.value.addLayer(layer); 
            }
            // popup
            const popupContent = document.createElement('div');
            popupContent.style.width = '200px'; // Set the width of the popup
            const input = document.createElement('input');
            input.type = 'text';
            input.id = 'feature-description';
            input.placeholder = 'Type a description';
            input.style.width = '100%'; // Make input take the full width of its parent
            input.style.padding = '5px 5px'; 
            input.style.borderRadius = '3px'; 
            input.style.overflowWrap = 'break-word'; // Break long words to prevent overflow
            
            const saveButton = document.createElement('button');
            saveButton.textContent = 'Save';
            saveButton.style.backgroundColor = '#FF4C50';
            saveButton.style.color = 'white'; 
            saveButton.style.padding = '4px 8px'; 
            saveButton.style.borderRadius = '5px'; 
            saveButton.style.marginTop = '10px'; 
            saveButton.onclick = () => {
                const description = input.value;
                
                // Save description to layer properties as annotation
                if (layerType === 'circle') {
                    // For circles, update the geojsonFeature that was created
                    const circleLayers = drawnItemsRef.value.getLayers();
                    const circleLayer = circleLayers[circleLayers.length - 1]; // Get the last added layer (current circle)
                    if (circleLayer && circleLayer.feature) {
                        circleLayer.feature.properties.annotation = description;
                    }
                } else {
                    // For other geometries, add properties to the layer
                    if (!layer.feature) {
                        layer.feature = {
                            type: 'Feature',
                            properties: {},
                            geometry: layer.toGeoJSON().geometry
                        };
                    }
                    layer.feature.properties.annotation = description;
                }
                
                // Update the popup to show the saved description
                layer.closePopup();
                layer.bindPopup(description);
                
                // Update geometries in store AFTER description is saved
                answerMapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
                
                handleSaveDescription(description);
            };

            popupContent.appendChild(input);
            popupContent.appendChild(saveButton);

            layer.bindPopup(popupContent);
            
            // Note: geometries will be updated when description is saved, not immediately
        });

        map.on(L.Draw.Event.DELETED, (event) => {
            const layers = event.layers;
    
            layers.eachLayer((layer) => {
                // console.log('layer to remove //> ', layer)
                    drawnItemsRef.value.removeLayer(layer);
            });
            // console.log('drawnItemsRef.value  delete //> ', drawnItemsRef.value.toGeoJSON())
            answerMapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });

        map.on(L.Draw.Event.EDITED, (event) => {
            const layers = event.layers;
            layers.eachLayer((layer) => {
                // Remove the old version of the edited layer
                drawnItemsRef.value.removeLayer(layer);
                // Add the updated version of the edited layer
                drawnItemsRef.value.addLayer(layer);
            });
            answerMapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });
    }
};


const current_question_id = route.params.question
const suveryStore = useSurveyStore()

// Ensure we have the questions loaded and current_question_id is valid
let current_question_url = null;
if (suveryStore.questions && suveryStore.questions.length > 0) {
    const questionIndex = parseInt(current_question_id) - 1;
    if (questionIndex >= 0 && questionIndex < suveryStore.questions.length) {
        current_question_url = suveryStore.questions[questionIndex].url;
    } else {
        console.error('Invalid question index:', questionIndex, 'Available questions:', suveryStore.questions.length);
    }
} else {
    console.error('Survey questions not loaded or empty:', suveryStore.questions);
}

const getGeometryStatusText = () => {
    if (!hasGeometries.value) {
        return 'No geometries drawn';
    }
    const count = answerMapViewStore.geometries.features.length;
    return `${count} geometry${count !== 1 ? 'ies' : ''} drawn`;
}


</script>
  
<style scoped>
.geometry-status {
  min-width: 120px;
}
</style>