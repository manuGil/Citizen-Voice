
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
                    <l-map ref="mapRefAnswer" 
                        :zoom="questionMapView.options.zoom" 
                        :center="questionMapView.options.center"
                        @ready="onMapWWControlReady"  @update:zoom="updateZoom"
                        @update:center="" :noBlockingAnimations="true">
                        <l-tile-layer 
                            :url="questionMapView.map_service_url"
                            layer-type="base"
                            >
                        </l-tile-layer>
                        <l-geo-json 
                        @ready="geoJsonReady" :key="updateKeyGeoJson"
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
import { useQuestionDesignStore } from "~/stores/questionDesign"
import { useGlobalStore } from '~/stores/global'
import { parse } from "postcss";

// API endpoints
const map_views_endpoint = '/map-views/'

const questionStore = useQuestionDesignStore()

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

var questionMapView;
console.log('props.mapViewUrl //> ', props.mapViewUrl)
// Fetch the map view for corresponding Question
if (props.mapViewUrl) {
    const mapViewId = extractMapviewId(props.mapViewUrl)
    const {data, error, pending} = await useCmsApiData(`${map_views_endpoint}${mapViewId}`)
    
    console.log('mapview data', data.value)

    questionMapView = data.value
    if (error.value) {
        throw new Error('error in questionMapView //> ', error)
    }
}

const mapRefAnswer = ref(null) 

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


const mapViewStore = useMapViewStore()
mapViewStore.$reset()

/**
 * Fetch the geojson data from the DB and add it to the mapViewData

// see: https://github.com/CUSP-Urban-Science-and-Policy/Citizen-Voice/blob/164b0e0f4c89126582cb1e49c5caeab05bfee947/frontend/components/MapView.vue#L122



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
        console.log('drawnItems //> ', drawnItems)
        drawnItems.addLayer(layer);
    });
}

/**
 * Listeners
 */

const geoJsonReady = () => {
    setGeoJsonMarkers()
};



//     console.log('mapView  in onMonted //> ', mapView)
//     if (mapView?.geometries?.features) {
//         mapViewData.geometries = mapView.geometries
//     }
//     if (mapView?.name) {
//         mapViewData.name = mapView.name
//     }
//     if (mapView?.options?.center) {
//         mapViewData.options.center = mapView.options.center
//     }
//     if (mapView?.options?.zoom) {
//         mapViewData.options.zoom = mapView.options.zoom
//     }
// };


/**
 * Watch mapViewData.geojson to update the map after changes or else the new values won't be visible
 */

watch(
    () => mapViewAnswerData.geometries,
    (newvalue) => {
        updateKeyGeoJson.value++
    },
    { deep: true }
)

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
    const map = mapRefAnswer.value.leafletObject;
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
        });

        map.on(L.Draw.Event.DELETED, (event) => {
            const layers = event.layers;
            layers.eachLayer((layer) => {
                drawnItemsRef.value.removeLayer(layer);
            });
        });

        map.on(L.Draw.Event.EDITED, (event) => {
            const layers = event.layers;
            layers.eachLayer((layer) => {
                // Remove the old version of the edited layer
                drawnItemsRef.value.removeLayer(layer);

                // Add the updated version of the edited layer
                drawnItemsRef.value.addLayer(layer);
            });
        });
    }
};

/**
 * Init the map with out controls
 */

// const onLeafletReadyMapWithoutControls = () => {
//     const map = mapRef.value.leafletObject;

//     if (map !== null) {
//         // storedMapWithoutControls.value = map
//         // set options
//         map.setView(mapViewData.options.center, mapViewData.options.zoom);

//         map.dragging.disable();
//         map.touchZoom.disable();
//         map.doubleClickZoom.disable();
//         map.scrollWheelZoom.disable();
//         map.boxZoom.disable();
//         map.keyboard.disable();
//         if (map.tap) map.tap.disable();
//         // document.getElementById('map').style.cursor = 'default';
//     }

// };

/**
 * Handlers
 */

const updateZoom = (value) => {
    // console.log('value //> ', value)
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
    mapViewAnswerData.geometries = drawnItemsRef.value.toGeoJSON()
    // Save new zoom value if not falsely
    // console.log('optionsTempStoreZoom.value submit //> ', optionsTempStoreZoom.value)
    // if (optionsTempStoreZoom?.value) {
    //     mapViewData.options.zoom = optionsTempStoreZoom.value
    // }
    // console.log('optionsTempStoreZoom.valu submit //> ', optionsTempStoreCenter.value)
    // Save new center value if not falsely
    // if (optionsTempStoreCenter?.value) {
    //     mapViewData.options.center = optionsTempStoreCenter.value
    // }
    /**
     * Check if the mapView already exists, if it exist then update, if not then create a new one
     */
    
    console.log('mapViewData on submit map //> ', mapViewAnswerData)

        // TODO: CONTINUE HERE: to save a map and its geometries,
        // do craete a location object, then save each geometry as a separate feature and reference the location object,
        // then create a mapview object and reference the location object

    if (mapViewAnswerData.url) {
        const mapview_slug = mapViewAnswerData.url.match(/map-views\/.*/);
        response = await mapViewStore.updateMapview(mapview_slug, mapViewAnswerData)
    } else {
        mapViewAnswerData.name = mapViewAnswerData?.name || uuidv4()
        response = await mapViewStore.createMapview(mapViewAnswerData)
    }

   
    // if (response.data) {
    //     mapViewData.name = response.data.name
    //     await questionStore.editCurrentQuestionKeyValue(props.questionIndex, { map_view: response.data.id })
    //     await questionStore.saveCurrentQuestions()
    // }
    updateKeyMapWithoutControls.value++
    setGeoJsonMarkers()
    // response.refresh()
    global.succes('Map view saved')
    
}


</script>
  
<style></style>