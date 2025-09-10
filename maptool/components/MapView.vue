
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
    mapViewUrl: String | undefined,
    savedGeometries: Object | undefined, // Previously saved geometries for this question
    savedMapOptions: Object | undefined  // Previously saved map options (zoom, center)
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
    console.log('Map zoom updated:', updatedZoom);
};

const handleUpdateMapViewCenter = (updatedCenter) => {
    // Update the center of the map. Converts object {lat:value, lng:value} to array [lat, lng]
    const newCenter = [updatedCenter.lat, updatedCenter.lng];
    currentMapView.options.center = newCenter;
    answerMapViewStore.updateCenter(newCenter);
    console.log('Map center updated:', newCenter);
};

const getCurrentMapOptions = () => {
    // Get current map state for storing in the answer
    return {
        zoom: answerMapViewStore.zoomLevel || currentMapView.options.zoom,
        center: answerMapViewStore.center || currentMapView.options.center,
        mapServiceUrl: answerMapViewStore.mapServiceUrl || questionMapView?.map_service_url
    };
};

// Function to get current map state for external access
const getMapState = () => {
    return {
        geometries: answerMapViewStore.geometries,
        mapOptions: getCurrentMapOptions()
    };
};

// Function to ensure geometry has a unique ID
const ensureGeometryId = (feature) => {
    if (!feature.properties) {
        feature.properties = {};
    }
    if (!feature.properties.id) {
        feature.properties.id = uuidv4();
    }
    return feature;
};

// Function to update store with current map geometries
const updateGeometriesInStore = () => {
    if (drawnItemsRef.value) {
        const currentGeoJSON = drawnItemsRef.value.toGeoJSON();
        
        // Ensure all geometries have unique IDs
        if (currentGeoJSON.features) {
            currentGeoJSON.features.forEach(ensureGeometryId);
        }
        
        answerMapViewStore.updateGeometries(currentGeoJSON);
    }
};

// Expose the functions to parent components
defineExpose({
    getMapState,
    getCurrentMapOptions
});


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
    const map = mapGeometriesRef.value.leafletObject
    
    // Clear the map before adding geometries (prevent accumulation)
    drawnItems.clearLayers();
    
    // Function to add geometries to the map
    const addGeometriesToMap = (geometries, layerType, isEditable = true) => {
        if (geometries?.features && geometries.features.length > 0) {
            console.log(`setGeoJsonMarkers: Loading ${layerType} geometries`);
            geometries.features.forEach((feature) => {
                // Ensure feature has unique ID for editable geometries
                if (isEditable) {
                    ensureGeometryId(feature);
                }
                
                const layer = L.geoJSON(feature, {
                    pointToLayer: function (feature, latlng) {
                        if (feature.properties.radius) {
                            return L.circle(latlng, { radius: feature.properties.radius });
                        } else {
                            return L.marker(latlng);
                        }
                    },
                });
                
                // Ensure layer has feature reference
                layer.feature = feature;
                
                if (isEditable) {
                    // For editable geometries, add each sublayer individually
                    // to ensure proper Leaflet Draw integration
                    layer.eachLayer(function(sublayer) {
                        sublayer.feature = feature; // Ensure feature reference is maintained
                        drawnItems.addLayer(sublayer);
                    });
                } else {
                    // Add directly to map for non-editable geometries (question base geometries)
                    layer.addTo(map);
                }
            });
        }
    };

    // 1. First load question's base geometries (non-editable)
    addGeometriesToMap(questionMapViewStore.geometries, "question base", false);
    
    // 2. Then load user's answer geometries (editable)
    addGeometriesToMap(answerMapViewStore.geometries, "user answer", true);
    
    // 3. Fallback to local mapViewAnswerData for backward compatibility (editable)
    if ((!questionMapViewStore.geometries || !questionMapViewStore.geometries.features || questionMapViewStore.geometries.features.length === 0) &&
        (!answerMapViewStore.geometries || !answerMapViewStore.geometries.features || answerMapViewStore.geometries.features.length === 0)) {
        addGeometriesToMap(mapViewAnswerData.geometries, "local fallback", true);
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
    }


const onMapWWControlReady = () => {
    const map = mapGeometriesRef.value.leafletObject;
    if (map !== null) {
        drawnItemsRef.value = featureGroupRef.value.leafletObject;

        const drawnItems = drawnItemsRef.value;

        // Function to add geometries to the map
        const addGeometriesToMap = (geometries, layerType, isEditable = true) => {
            if (geometries?.features && geometries.features.length > 0) {
                console.log(`Loading ${layerType} geometries:`, geometries);
                geometries.features.forEach((feature) => {
                    // Ensure feature has unique ID for editable geometries
                    if (isEditable) {
                        ensureGeometryId(feature);
                    }
                    
                    const layer = L.geoJSON(feature, {
                        pointToLayer: function (feature, latlng) {
                            if (feature.properties.radius) {
                                return L.circle(latlng, { radius: feature.properties.radius });
                            } else {
                                return L.marker(latlng);
                            }
                        },
                    });
                    
                    // Ensure layer has feature reference
                    layer.feature = feature;
                    
                    if (isEditable) {
                        // For editable geometries, we need to add each sublayer individually
                        // to ensure proper Leaflet Draw integration
                        layer.eachLayer(function(sublayer) {
                            sublayer.feature = feature; // Ensure feature reference is maintained
                            drawnItems.addLayer(sublayer);
                        });
                    } else {
                        // Add directly to map for non-editable geometries (question base geometries)
                        layer.addTo(map);
                    }
                });
            }
        };

        // 1. First load question's base geometries (non-editable, directly to map)
        addGeometriesToMap(questionMapViewStore.geometries, "question base", false);
        
        // 2. Clear the map before loading geometries (prevent accumulation)
        drawnItems.clearLayers();
        
        // 3. Load previously saved user geometries if available
        if (props.savedGeometries && props.savedGeometries.features && props.savedGeometries.features.length > 0) {
            // Ensure all saved geometries have unique IDs
            props.savedGeometries.features.forEach(ensureGeometryId);
            
            // Set answerMapViewStore with geometries from responseStore
            answerMapViewStore.updateGeometries(props.savedGeometries);
            
            // Add to map for editing
            addGeometriesToMap(props.savedGeometries, "restored user geometries", true);
        } else {
            // No saved geometries - start with empty store
            answerMapViewStore.updateGeometries({ type: "FeatureCollection", features: [] });
        }
        
        // 4. Fallback to local currentMapView for backward compatibility (editable)
        if ((!questionMapViewStore.geometries || !questionMapViewStore.geometries.features || questionMapViewStore.geometries.features.length === 0) &&
            (!answerMapViewStore.geometries || !answerMapViewStore.geometries.features || answerMapViewStore.geometries.features.length === 0) &&
            (!props.savedGeometries || !props.savedGeometries.features || props.savedGeometries.features.length === 0)) {
            addGeometriesToMap(currentMapView.geometries, "local fallback", true);
        }

        // Restore map state if provided
        if (props.savedMapOptions) {
            console.log('Restoring map state:', props.savedMapOptions);
            if (props.savedMapOptions.zoom) {
                map.setZoom(props.savedMapOptions.zoom);
                answerMapViewStore.updateZoomLevel(props.savedMapOptions.zoom);
            }
            if (props.savedMapOptions.center) {
                map.setView(props.savedMapOptions.center, map.getZoom());
                answerMapViewStore.updateCenter(props.savedMapOptions.center);
            }
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
                        id: uuidv4(), // Add unique ID
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
                // For other geometries, ensure they have a feature property
                if (!layer.feature) {
                    layer.feature = {
                        type: 'Feature',
                        properties: {
                            id: uuidv4(), // Add unique ID
                            annotation: '' // Initialize empty annotation
                        },
                        geometry: layer.toGeoJSON().geometry
                    };
                } else {
                    // Ensure existing feature has an ID
                    ensureGeometryId(layer.feature);
                }              
                drawnItemsRef.value.addLayer(layer); 
            }
            
            // Update geometries in store after creating geometry
            updateGeometriesInStore();
            
            // Create annotation popup
            const popupContent = document.createElement('div');
            popupContent.style.width = '200px';
            const input = document.createElement('input');
            input.type = 'text';
            input.id = 'feature-description';
            input.placeholder = 'Type a description (optional)';
            input.style.width = '100%';
            input.style.padding = '5px 5px'; 
            input.style.borderRadius = '3px'; 
            input.style.overflowWrap = 'break-word';
            
            const saveButton = document.createElement('button');
            saveButton.textContent = 'Save Description';
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
                        // Ensure the feature still has its unique ID after annotation update
                    }
                } else {
                    // For other geometries, update the layer feature
                    if (layer.feature) {
                        layer.feature.properties.annotation = description;
                        // Ensure the feature still has its unique ID after annotation update
                    }
                }
                
                // Update the popup to show the saved description
                layer.closePopup();
                if (description.trim()) {
                    layer.bindPopup(description);
                }
                
                // Update geometries in store after annotation
                updateGeometriesInStore();
                
                handleSaveDescription(description);
            };

            popupContent.appendChild(input);
            popupContent.appendChild(saveButton);

            layer.bindPopup(popupContent);
            
        });

        map.on(L.Draw.Event.DELETED, (event) => {
            const layers = event.layers;
    
            layers.eachLayer((layer) => {
                    drawnItemsRef.value.removeLayer(layer);
            });
            
            // Update geometries in store after deleting geometry
            updateGeometriesInStore();
        });

        map.on(L.Draw.Event.EDITED, (event) => {
            const layers = event.layers;
            layers.eachLayer((layer) => {
                // The layer is already updated by Leaflet, just need to sync the store
            });
            
            // Update geometries in store after editing geometry
            updateGeometriesInStore();
            console.log('Geometries updated in store after editing');
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