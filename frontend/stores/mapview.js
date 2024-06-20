/**
 * This to store the mapview data of an Answer in a Response
 * 
 */

import { defineStore, } from 'pinia'
import setRequestConfig from './utils/setRequestConfig';
import { useGlobalStore } from './global'
import { da, el, th } from 'vuetify/locale';

function GeoToEWKT(srid, feature) {
    if (feature.geometry.type === "Point") {
        return `SRID=${srid};POINT(${feature.geometry.coordinates[0]} ${feature.geometry.coordinates[1]})`;
    } else if (feature.geometry.type === "LineString") {
        const coordinates = feature.geometry.coordinates.map(coord => coord.join(" ")).join(",");
        return `SRID=${srid};LINESTRING(${coordinates})`;
    } else if (feature.geometry.type === "Polygon") {
        const coordinates = feature.geometry.coordinates.map(ring => ring.map(coord => coord.join(" ")).join(",")).join(",");
        return `SRID=${srid};POLYGON((${coordinates}))`;
    } else {
        throw new Error("Unsupported geometry type");
    }
};


export const useMapViewStore = defineStore('mapView', {
    state: () => ({
        id: null,
        url: null,
        name: null,
        mapServiceUrl: null,
        zoomLevel: null,
        center: null,
        geometries: {} // a GeoJSON featurecollection for all geometries
    }),
    getters: {
        // getCurrentQuestions: (state) => state.currentQuestions
        getGeometries: (state) => state.geometries,
        getZoomLevel: (state) => state.zoomLevel,
        getCenter: (state) => state.center,
        getMapServiceUrl: (state) => state.mapServiceUrl,
        getFormattedBody: (state) => {
            return {
                name: state.name,
                map_service_url: state.mapServiceUrl,
                options: {
                    zoom: state.zoomLevel,
                    center: state.center
                },
                geometries: state.geometries
            }
        }

    },
    actions: {
        updateGeometries(geometries) {
            this.geometries = geometries
        },
        updateZoomLevel(zoomLevel) {
            this.zoomLevel = zoomLevel
        },
        updateCenter(center) {
            this.center = center
        },
        updateMapServiceUrl(mapServiceUrl) {
            this.mapServiceUrl = mapServiceUrl
        },
        updateName(name) {
            this.name = name
        },
        async createMapview() {
            /**
             * Create a new mapview in the backend with the current state of the store
             */

            // TODO: create geometries and location collection
            var location_url;
            const config = setRequestConfig({ method: 'POST', headers:{
                'Content-Type': 'application/json'
             }, body: this.getFormattedBody })

            // create the location collection, if there are geometries
            if (Object.keys(this.geometries).length !== 0) {
                const {data, error, pending } = await useAsyncData( () => $cmsApi(`/locations/`, 
                    { method: 'POST', 
                      headers: {'Content-Type': 'application/json'}, 
                      body: {
                        name: this.name, 
                        description: 'created from mapview store' 
                    } 
                    }
                ));

                if (data.value) {
                    location_url =  data.value.url
                    console.log('location_url //> ', data)
                } else {
                    throw new Error('Error creating location collection //>', data)
                }

                if (error.value) {
                    throw new Error('Error creating location collection //> ', error.value)
                }
                
                // Create the geometries and add them to the location collection
                this.geometries.features.forEach( async (feature) => {

                    var feature_endpoint;
                    var feature_ewkt;
                    if (feature.geometry.type === "Point"){
                        feature_endpoint = `/pointfeatures/`;
                        feature_ewkt = GeoToEWKT(4326, feature);
                    } else if (feature.geometry.type === "LineString") {
                        feature_endpoint = `/linefeatures/`;
                        feature_ewkt = GeoToEWKT(4326, feature);
                    } else if (feature.geometry.type === "Polygon") {
                        feature_endpoint = `/polygonfeatures/`
                        feature_ewkt = GeoToEWKT(4326, feature);
                    }

                    console.log('feature object //> ', feature_ewkt) 
                    

                    const {data, error, pending } = await useAsyncData( () => $cmsApi(feature_endpoint, 
                        { method: 'POST', 
                          headers: {'Content-Type': 'application/json'}, 
                          body: {
                            geom: feature,
                            description: 'created from mapview store',
                            location: location_url
                        } 
                        }
                    ));

                    if (error.value) {
                        throw new Error('Error creating feature //> ', error.value)
                    }
                })


            } else {
                location_url = null
            };

            const global = useGlobalStore()
            // const config = setRequestConfig({ method: 'POST', body: this.getFormattedBody })
            const { data, error, refresh } = await useAsyncData(() => $cmsApi(`/map-views/`, config));

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error.value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                return null
            }

            if (data.value) {
                this.id = data.value.id
                this.url = data.value.url               
            }

            // Notification
            global.succes('Map saved')
            return { data: data?.value, refresh }
        },
        async updateMapview(mapview_url) {
            const global = useGlobalStore()
            console.log('mapview url at store //> ', mapview_url)
            const config = setRequestConfig({ method: 'PATCH', body: this.getFormattedBody })
            const { data, error, refresh } = await useAsyncData( () => $cmsApi(`${mapview_url}`, config));

            if (error.value) {
                let warnMessage = null
                for (const [key, value] of Object.entries(error.value.data)) {
                    warnMessage = warnMessage ? `${warnMessage} \n\n ${key}: ${value}` : `${key}: ${value}`
                }
                // Notification
                global.warning(warnMessage)
                return null

            }
            // Notification
            global.succes('Map has been updated')
            return { data: data?.value, refresh }
        },
        async fetchMapView(url) {
            console.log('Map_view id //> ', url)
            const config = setRequestConfig({ method: 'GET' })
            const {data: res, error } = await useAsyncData( () => $cmsApi(`${url}`, config));

             console.log('Map_view res //> ', res)
            if (res?.value) {
                this.id = res.value.id;
                this.url= res.value.url;
                this.name = res.value.name;
                this.mapServiceUrl = res.value.map_service_url;
                console.log('res.value.options.zoom //> ', res.value.options.zoom)
                this.zoomLevel = res.value.options.zoom;
                this.center = res.value.options.center;
                this.geometries = res.value.geometries
            };
            if (error.value) {
                throw new Error('Error fetching map view //> ', error.value)
            };
            return res
        }
    },

})