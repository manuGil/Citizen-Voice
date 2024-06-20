
<template>
    <v-sheet v-model="dialog" width="auto">
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
                        <l-feature-group ref="featureGroupRef"></l-feature-group>
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
import { ref, reactive, onMounted, onBeforeMount } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import { forEach } from 'ramda'
// Store
import { useMapViewStore } from "~/stores/mapview"
import { useStoreResponse } from "~/stores/response";
import { useQuestionDesignStore } from "~/stores/questionDesign"
import { useGlobalStore } from '~/stores/global'
import { parse } from "postcss";
import { th } from "vuetify/locale";

// API endpoints
const map_views_endpoint = '/map-views/'

const questionStore = useQuestionDesignStore()
const mapViewStore = useMapViewStore()
const responseStore = useStoreResponse()
mapViewStore.$reset()


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
var question_id = route.params._question; // use url questions id as an index to load each question 
let answer_index = question_id -1;  // gets the id for the questions

var questionMapView;
// console.log('props.mapViewUrl //> ', props.mapViewUrl)
// Fetch the map view for corresponding Question
if (props.mapViewUrl) {
    const mapViewId = extractMapviewId(props.mapViewUrl)
    const {data, error, pending} = await useCmsApiData(`${map_views_endpoint}${mapViewId}`)
    
    // console.log('mapview data', data.value)

    questionMapView = data.value
    mapViewStore.updateMapServiceUrl(questionMapView.map_service_url)
    mapViewStore.updateZoomLevel(questionMapView.options.zoom)
    mapViewStore.updateCenter(questionMapView.options.center)
    if (error.value) {
        throw new Error('error in questionMapView //> ', error)
    }
}

// console.log('questionMapView //> ', questionMapView)

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
    mapViewStore.updateZoomLevel(updatedZoom);
};

const handleUpdateMapViewCenter = (updatedCenter) => {
    // Update the center of the map. Converts object {lat:value, lng:value} to array [lat, lng]
    // console.log('current mapview \\>', currentMapView);
    const newCenter = [updatedCenter.lat, updatedCenter.lng];
    currentMapView.options.center = newCenter;
    mapViewStore.updateCenter(newCenter);
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
    // const drawnItems = featureGroupRef.value.features // this schould be a leafleft object?
    const drawnItems = featureGroupRef.value.leafletObject
    const initialGeojson = mapViewAnswerData.geometries;

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
        // console.log('drawnItems //> ', drawnItems)
        drawnItems.addLayer(layer);
    });
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
 * Add the props.geojson to the drawnItemsRef value
 */
const onMapWWControlReady = () => {
    const map = mapGeometriesRef.value.leafletObject;
    if (map !== null) {
        drawnItemsRef.value = featureGroupRef.value.leafletObject;

        if (mapViewStore.geometries?.features) {
            const drawnItems = drawnItemsRef.value;
            const initialGeojson = mapViewStore.geometries;

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
                    properties: { radius: radius },
                    geometry: { type: 'Point', coordinates: [latlng.lng, latlng.lat] },
                };
                const circleLayer = L.geoJSON(geojsonFeature, {
                    pointToLayer: function (feature, latlng) {
                        return L.circle(latlng, { radius: feature.properties.radius });
                    },
                });
                drawnItemsRef.value.addLayer(circleLayer);
            } else {
                drawnItemsRef.value.addLayer(layer);
            }
            console.log('drawnItemsRef.value  add //> ', drawnItemsRef.value.toGeoJSON())
            mapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });

        map.on(L.Draw.Event.DELETED, (event) => {
            const layers = event.layers;
    
            layers.eachLayer((layer) => {
                // console.log('layer to remove //> ', layer)
                    drawnItemsRef.value.removeLayer(layer);
            });
            // console.log('drawnItemsRef.value  delete //> ', drawnItemsRef.value.toGeoJSON())
            mapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });

        map.on(L.Draw.Event.EDITED, (event) => {
            const layers = event.layers;
            layers.eachLayer((layer) => {
                // Remove the old version of the edited layer
                drawnItemsRef.value.removeLayer(layer);
                // Add the updated version of the edited layer
                drawnItemsRef.value.addLayer(layer);
            });
            mapViewStore.updateGeometries(drawnItemsRef.value.toGeoJSON());
        });
    }
};


const submitMap = async () => {
    // const global = useGlobalStore()
    let response
    // mapViewAnswerData.geometries = drawnItemsRef.value.toGeoJSON()

    /**
     * Check if the mapView already exists, if it exist then update, if not then create a new one
     */
    
    if (mapViewStore.name === null) {
        mapViewStore.updateName(uuidv4())
    };

    if (mapViewStore.url) {
        const mapview_slug = mapViewStore.url.match(/map-views\/.*/);
        response = await mapViewStore.updateMapview(mapview_slug)
    } else {
        // mapViewAnswerData.name = mapViewAnswerData?.name || uuidv4()
        response = await mapViewStore.createMapview()
    }
    
    responseStore.updateAnswerMapView(answer_index, mapViewStore.url)
   
    // if (response.data) {
    //     mapViewData.name = response.data.name
    //     await questionStore.editCurrentQuestionKeyValue(props.questionIndex, { map_view: response.data.id })
    //     await questionStore.saveCurrentQuestions()
    // }
    updateKeyMapWithoutControls.value++
    setGeoJsonMarkers()
    // response.refresh()
    // global.succes('Map view saved')
    
}


</script>
  
<style></style>